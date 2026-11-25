"""Orquestrador. O código só coordena: o conhecimento vem da base (knowledge/), do índice e da IA."""
from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

from ..models.db import Banco
from ..models.schemas import Analise, Fatos, Minuta, Pacote, PedidoPacote, PedidoParecer, PedidoResposta, Trecho
from ..utilities.text import anonimizar
from . import ai_provider as C
from . import docx_generator as D
from . import embeddings, fact_extractor, indexer, pdf_reader
from . import prompts as P
from . import report_generator as R
from .classifier import Classificador
from .metrics_service import Metricas
from .retriever import Retriever

LIMITE_PDF = 25 * 1024 * 1024


class ErroNegocio(Exception):
    def __init__(self, msg: str, status: int = 422):
        super().__init__(msg); self.status = status


class Motor:
    def __init__(self, settings, provider=None, store=None, embedder=None):
        self.s = settings
        for k in ("uploads", "output", "metrics", "vectorstore"):
            settings.caminho(k).mkdir(parents=True, exist_ok=True)
        self.db = Banco(settings.caminho("banco"))
        self.store = store or indexer.criar_store(settings)
        self.provider = provider or C.criar_provider(settings)
        self.embedder = embedder if embedder is not None else embeddings.criar_embedder(settings)
        self.retriever = self._novo_retriever()
        self.classificador = Classificador(settings)
        self.metricas = Metricas(self.db, settings.caminho("metrics"))

    # ------------------------------------------------------------ upload
    def receber_pdf(self, nome: str, conteudo: bytes, usuario: str = "") -> dict:
        if not conteudo.startswith(b"%PDF"):
            raise ErroNegocio("O arquivo enviado não é um PDF.", 400)
        if len(conteudo) > LIMITE_PDF:
            raise ErroNegocio("PDF acima de 25 MB.", 413)
        ocr = bool(self.s.get("ocr.habilitado", True))
        try:
            ct = pdf_reader.ler_consulta(conteudo, ocr=ocr, idiomas=tuple(self.s.get("ocr.idiomas", ["pt", "en"])),
                                         min_chars=int(self.s.get("ocr.min_caracteres_por_pagina", 40)))
        except Exception as e:
            raise ErroNegocio(f"PDF ilegível: {e}", 400)
        seguro = uuid.uuid4().hex + ".pdf"          # nunca usa o nome enviado como caminho
        cid = self.db.inserir("consultas", arquivo=seguro, usuario=usuario, status="recebida")
        up = self.s.caminho("uploads")
        (up / seguro).write_bytes(conteudo)
        (up / f"{cid}.txt").write_text(ct.texto, encoding="utf8")
        status = "recebida" if ct.texto.strip() else "sem_texto"
        self.db.atualizar("consultas", cid, status=status)
        return {"consulta_id": cid, "arquivo_original": Path(nome).name[:120], "paginas": ct.paginas, "usou_ocr": ct.usou_ocr,
                "caracteres": len(ct.texto), "avisos": ct.avisos, "status": status}

    def _texto(self, cid: int) -> str:
        if not self.db.obter("consultas", cid):
            raise ErroNegocio("Consulta não encontrada.", 404)
        arq = self.s.caminho("uploads") / f"{cid}.txt"
        return arq.read_text(encoding="utf8") if arq.exists() else ""

    # ------------------------------------------------------------ análise
    def _explicar_precedentes(self, fatos: Fatos, recup: dict, avisos: list[str]) -> None:
        """UC001 passo 4: justificativa da similaridade. Com IA, uma frase por precedente; sem IA, os termos em comum."""
        if not self.provider.usa_ia:
            return
        try:
            resumo = f"{fatos.atividade}. {fatos.descricao}"
            if self.s.get("ia.anonimizar", True):
                resumo = anonimizar(resumo, fatos.servidor.nome)
            ctx, mapa = C.montar_contexto(resumo, recup["normativos"], recup["precedentes"], recup["pareceres"], [],
                                          bool(self.s.get("ia.anonimizar", True)), regras=R.carregar_regras(self.s))
            bruto = self.provider.completar(P.carregar("precedents", self.s), ctx, json_mode=True)
            for it in json.loads(re.search(r"\{.*\}", bruto, re.S).group(0)).get("itens", []):
                t = mapa.get(it.get("id"))
                if t and it.get("similaridade"):
                    t.motivo = str(it["similaridade"])[:300]
        except Exception as e:
            avisos.append(f"Justificativa de similaridade pela IA indisponível ({e}).")

    def analisar(self, cid: int, gerar_minuta: bool = True) -> Analise:
        texto = self._texto(cid)
        if not texto.strip():
            raise ErroNegocio("A consulta não tem texto extraído (PDF digitalizado sem OCR instalado?).")
        avisos: list[str] = []
        if not self.store.manifesto:
            avisos.append("A base de conhecimento ainda não foi indexada (POST /indexar). A análise usa apenas as categorias.")
        fatos = fact_extractor.extrair_fatos(texto, self.provider, self.s)
        pre = self.classificador.classificar(fatos)
        extra = self.classificador.palavras_chave(pre.escolhida.id) if pre.escolhida else []
        recup = self.retriever.recuperar(fatos, extra)
        cls = self.classificador.classificar(fatos, recup["modelos"], self.provider)
        if fatos.origem == "heuristica" and cls.escolhida and cls.escolhida.confianca in ("alta", "media") and cls.escolhida.id != "generico":
            fatos.atividade = R.rot_padrao(cls.escolhida.nome)      # sem IA, o nome da atividade é o da categoria reconhecida
        if not recup["normativos"]:
            avisos.append("Nenhum normativo recuperado: popule knowledge/normativos (Lei 12.813/2013 etc.) e reindexe.")
        self._explicar_precedentes(fatos, recup, avisos)
        minuta = R.gerar_minuta(self.s, fatos, cls, recup, self.provider) if gerar_minuta else None
        a = Analise(consulta_id=cid, fatos=fatos, classificacao=cls, precedentes=recup["precedentes"], pareceres=recup["pareceres"],
                    normativos=recup["normativos"], modelos=recup["modelos"], minuta=minuta, avisos=avisos)
        pasta = self.s.caminho("output") / f"consulta_{cid}"
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "analise.json").write_text(a.model_dump_json(indent=1), encoding="utf8")
        self.db.atualizar("consultas", cid, atividade=cls.escolhida.id if cls.escolhida else "", status="analisada")
        return a

    def _analise(self, cid: int) -> Analise:
        arq = self.s.caminho("output") / f"consulta_{cid}" / "analise.json"
        if not arq.exists():
            raise ErroNegocio("Consulta ainda não analisada (POST /analisar).", 409)
        return Analise.model_validate_json(arq.read_text(encoding="utf8"))

    def nova_minuta(self, pedido: PedidoParecer) -> Minuta:
        """Refaz a minuta com a atividade/resultado escolhidos pelo parecerista (decisão humana, RN001)."""
        a = self._analise(pedido.consulta_id)
        aid = pedido.atividade_id or (a.classificacao.escolhida.id if a.classificacao.escolhida else "generico")
        if aid not in self.classificador.cats:
            raise ErroNegocio("atividade_id fora da lista de categorias do HTML.")
        recup = {"pareceres": a.pareceres, "precedentes": a.precedentes, "normativos": a.normativos, "modelos": a.modelos}
        return R.gerar_minuta(self.s, a.fatos, a.classificacao, recup, self.provider, pedido.resultado, aid)

    # ------------------------------------------------------------ Copilot Chat assistido (sem API)
    def _auditar_chat(self, tipo: str, **dados) -> None:
        """Mesma trilha da IA automática (metrics/ia_auditoria.jsonl), para o curador."""
        from datetime import datetime
        reg = {"quando": datetime.now().isoformat(timespec="seconds"), "provider": "copilot_chat_assistido", "tipo": tipo}
        conteudo = bool(self.s.get("ia.auditoria.registrar_conteudo", True))
        for k, v in dados.items():
            reg[k] = v if (conteudo or isinstance(v, (int, bool))) else f"[{len(str(v))} caracteres]"
        arq = self.s.caminho("metrics") / "ia_auditoria.jsonl"
        arq.parent.mkdir(parents=True, exist_ok=True)
        with arq.open("a", encoding="utf8") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")

    def _recup(self, a: Analise) -> dict:
        return {"pareceres": a.pareceres, "precedentes": a.precedentes, "normativos": a.normativos, "modelos": a.modelos}

    def pacote_copilot(self, p: PedidoPacote) -> Pacote:
        """Monta o prompt (e o arquivo de contexto) para o parecerista colar no Copilot Chat com a conta corporativa da RFB."""
        a = self._analise(p.consulta_id)
        limite = int(self.s.get("ia.copilot_chat.limite_caracteres", 7500))
        try:
            sistema, completo, mapa_total = R.preparar_fundamentacao(self.s, a.fatos, self._recup(a), p.resultado, limite=200000)
            sistema, ctx, mapa = R.preparar_fundamentacao(self.s, a.fatos, self._recup(a), p.resultado,
                                                          limite=max(limite - len(sistema) - 2, 1000))
        except C.ContextoInsuficiente as e:
            raise ErroNegocio(f"Não há base suficiente para montar o contexto: {e}.")
        avisos = []
        trunc = len(mapa) < len(mapa_total)
        if trunc:
            avisos.append(f"O contexto não coube em {limite} caracteres: {len(mapa_total) - len(mapa)} trecho(s) ficaram de fora. "
                          "Para levar tudo, anexe o arquivo de contexto ao chat e use o prompt curto.")
        pacote = Pacote(
            prompt=sistema + "\n\n" + ctx,
            prompt_curto=sistema + "\n\nO contexto completo (caso concreto, regras da COGER, normativos, precedentes, pareceres e modelos) está no arquivo "
                                   "anexo contexto_AICI.md. Use somente ele e cite os marcadores [N1], [P1], [A1], [M1], [R1].",
            contexto_md=completo, limite_caracteres=limite, caracteres=len(sistema) + 2 + len(ctx), truncado=trunc,
            ids=sorted(mapa), url_chat=str(self.s.get("ia.copilot_chat.url", "")), avisos=avisos)
        self._auditar_chat("pacote", consulta_id=p.consulta_id, chars=pacote.caracteres, truncado=trunc, prompt=pacote.prompt)
        return pacote

    def aplicar_resposta_copilot(self, p: PedidoResposta) -> Minuta:
        """Valida a resposta colada (fontes, resultado) contra o acervo e refaz a minuta com ela. A resposta nunca é aceita sem validação."""
        a = self._analise(p.consulta_id)
        aid = p.atividade_id or (a.classificacao.escolhida.id if a.classificacao.escolhida else "generico")
        if aid not in self.classificador.cats:
            raise ErroNegocio("atividade_id fora da lista de categorias do HTML.")
        self._auditar_chat("resposta", consulta_id=p.consulta_id, chars=len(p.texto), resposta=p.texto)
        if not re.search(r"\{.*\}", p.texto, re.S):
            raise ErroNegocio("A resposta não contém o JSON pedido. Peça ao Copilot para responder apenas com o JSON do formato indicado.")
        try:
            json.loads(re.search(r"\{.*\}", p.texto, re.S).group(0))
        except ValueError:
            raise ErroNegocio("O JSON da resposta está incompleto ou inválido. Copie a resposta inteira do Copilot (do primeiro { ao último }).")
        limite_ctx = 200000
        if p.modo == "texto":     # o chat recebeu o prompt completo dentro do limite: só vale citar o que coube nele
            limite = int(self.s.get("ia.copilot_chat.limite_caracteres", 7500))
            sistema, _, _ = R.preparar_fundamentacao(self.s, a.fatos, self._recup(a), p.resultado, limite=200000)
            limite_ctx = max(limite - len(sistema) - 2, 1000)
        minuta = R.gerar_minuta(self.s, a.fatos, a.classificacao, self._recup(a), C.RespostaProvider(p.texto, limite_ctx), p.resultado, aid)
        if minuta.modo != "copilot_chat":
            minuta.avisos.append("A resposta do Copilot não pôde ser aproveitada; a minuta foi montada só com os modelos.")
        return minuta

    # ------------------------------------------------------------ documentos
    def gerar_documento(self, pedido: PedidoParecer) -> tuple[Path, str]:
        if not pedido.validado:
            raise ErroNegocio("Revisão humana obrigatória: confirme (validado=true) que fatos, enquadramento, fontes e compromissos foram revisados.")
        a = self._analise(pedido.consulta_id)
        cid = pedido.consulta_id
        aid = pedido.atividade_id or (a.classificacao.escolhida.id if a.classificacao.escolhida else "generico")
        if aid not in self.classificador.cats:
            raise ErroNegocio("atividade_id fora da lista de categorias do HTML.")
        recup = {"pareceres": a.pareceres, "precedentes": a.precedentes, "normativos": a.normativos, "modelos": a.modelos}
        minuta = pedido.minuta
        if minuta is None:
            minuta = R.gerar_minuta(self.s, a.fatos, a.classificacao, recup, self.provider, pedido.resultado, aid)
        resultado = pedido.resultado or minuta.resultado_sugerido
        modelo = R._carregar_modelo(self.s, aid)
        atividade = R.rot_padrao(modelo["nome"]) if modelo else (a.fatos.atividade or "[ATIVIDADE]")
        pasta = self.s.caminho("output") / f"consulta_{cid}"
        base = re.sub(r"[^A-Za-z0-9_-]+", "_", f"{pedido.documento}_{pedido.numero or cid}_{pedido.ano or ''}").strip("_")
        saida = pasta / f"{base}.docx"
        if pedido.documento == "parecer":
            variante = R._escolher_variante(modelo, resultado, a.modelos) if modelo else None
            ctx, campos = R._ctx(self.s, a.fatos, atividade, variante)
            em = R.ementa(self.s, atividade, resultado, a.fatos.servidor.tipo, modelo, variante, ctx, campos)
            D.gerar_parecer(self.s, a.fatos, minuta, em, saida, pedido.numero, pedido.ano)
            self.db.inserir("pareceres", consulta_id=cid, resultado=resultado, modelo=aid, arquivo_saida=saida.name)
            self.db.atualizar("consultas", cid, resultado=resultado, atividade=aid, status="parecer_gerado")
            prec = (a.precedentes or a.pareceres or [None])[0]
            rotulo = (f"PA-{prec.numero}-{prec.ano}" if prec and prec.numero else (prec.titulo if prec else "")) if prec else ""
            self.metricas.registrar(atividade, resultado, rotulo)
        elif pedido.documento == "termo":
            if resultado != "sem_conflito_ressalvas":
                raise ErroNegocio("O Termo de Compromisso só é gerado para autorização com ressalvas (risco mitigável).")
            D.gerar_termo(self.s, a.fatos, minuta, atividade, saida, pedido.numero, pedido.ano)
        else:
            D.gerar_despacho(self.s, a.fatos, pedido.destino, saida, pedido.numero, pedido.ano)
        return saida, saida.name

    # ------------------------------------------------------------ revisão (UC003)
    def revisar(self, cid: int, minuta: Minuta) -> list[dict]:
        a = self._analise(cid)
        pontos: list[dict] = []
        texto = "\n".join(p.texto for s in minuta.secoes for p in s.paragrafos)
        for m in re.findall(r"\[[A-ZÀ-Ý0-9ºª /.\-]{3,}\]", texto):
            pontos.append({"gravidade": "media", "descricao": f"Campo pendente: {m}", "trecho": m})
        sem_fonte = [p.texto[:80] for s in minuta.secoes for p in s.paragrafos if not p.fontes]
        for t in sem_fonte:
            pontos.append({"gravidade": "alta", "descricao": "Parágrafo sem origem registrada (RN003: toda sugestão deve ser validada).", "trecho": t})
        conc = " ".join(p.texto for s in minuta.secoes if s.titulo.startswith("III") for p in s.paragrafos)
        neg = bool(re.search(r"configura (?:situação de )?conflito|não se recomenda", conc)) and not re.search(r"não configura", conc)
        if neg and minuta.resultado_sugerido.startswith("sem_"):
            pontos.append({"gravidade": "alta", "descricao": "A conclusão indica conflito, mas o resultado marcado autoriza a atividade.", "trecho": conc[:120]})
        if minuta.resultado_sugerido == "sem_conflito_ressalvas" and "Termo de Compromisso" not in conc:
            pontos.append({"gravidade": "media", "descricao": "Autorização com ressalvas sem menção ao Termo de Compromisso na conclusão.", "trecho": ""})
        if self.provider.usa_ia:
            try:
                recup = {"normativos": a.normativos, "precedentes": a.precedentes, "pareceres": a.pareceres, "modelos": a.modelos}
                ctx, _ = C.montar_contexto(f"{a.fatos.atividade}. {a.fatos.descricao}", recup["normativos"], recup["precedentes"],
                                           recup["pareceres"], recup["modelos"], bool(self.s.get("ia.anonimizar", True)),
                                           regras=R.carregar_regras(self.s))
                bruto = self.provider.completar(P.carregar("review", self.s), ctx + "\n\n=== MINUTA ===\n" + anonimizar(texto, a.fatos.servidor.nome), json_mode=True)
                pontos += [{"gravidade": x.get("gravidade", "media"), "descricao": x.get("descricao", ""), "trecho": x.get("trecho", "")}
                           for x in json.loads(re.search(r"\{.*\}", bruto, re.S).group(0)).get("pontos", [])]
            except Exception as e:
                pontos.append({"gravidade": "baixa", "descricao": f"Revisão pela IA indisponível: {e}", "trecho": ""})
        return pontos

    def _novo_retriever(self) -> Retriever:
        dense = embeddings.DenseStore(self.s.caminho("vectorstore")) if self.embedder is not None else None
        return Retriever(self.s, self.store, self.embedder, dense)

    def indexar(self, completo: bool = False) -> dict:
        r = indexer.indexar(self.s, self.store, completo, self.embedder)
        self.retriever = self._novo_retriever()
        return r
