"""Módulo 10 - Gerador de minuta. Estrutura fixa e institucional: I - RELATÓRIO, II - FUNDAMENTAÇÃO, III - CONCLUSÃO.
A IA (quando habilitada) escreve apenas a FUNDAMENTAÇÃO e sugere resultado/ressalvas; o restante vem de templates/institucional.json.
Sem IA, a fundamentação é extraída dos modelos institucionais (knowledge/modelos), com a origem de cada parágrafo."""
from __future__ import annotations

import json
import re
from pathlib import Path

from ..models.schemas import Fatos, Classificacao, Minuta, Paragrafo, Secao, Trecho
from ..utilities.text import norm
from . import ai_provider as C
from . import prompts as P

RESULTADOS = ("sem_conflito", "sem_conflito_ressalvas", "conflito", "outro")
# campos dos modelos que partem de uma pergunta do formulário (igual ao gerador HTML)
CAMPO_DE_PERGUNTA = {"descricao_atividade": 2, "descricao_pretensao": 2, "descricao_pedido": 2, "atividades": 2, "atividade_exercida": 6}


def institucional(settings) -> dict:
    return json.loads((settings.caminho("templates") / "institucional.json").read_text(encoding="utf8"))


def rot_padrao(nome: str) -> str:
    t = re.sub(r"\s*\(.*?\)", "", nome)
    t = re.sub(r"\s+–.*$", "", t).strip()
    return t if re.match(r"^[A-ZÀ-Ý]{2}", t) else t[:1].lower() + t[1:]


def preencher(txt: str, ctx: dict, campos: dict | None = None) -> str:
    """{{g:masc|fem}} concorda o gênero; {{campo}} vem do contexto; o que faltar vira [CAMPO] (destacado em amarelo no Word)."""
    def rep(m):
        k = m.group(1)
        if k.startswith("g:"):
            a, _, b = k[2:].partition("|")
            return b if ctx.get("fem") else a
        if ctx.get(k):
            return str(ctx[k])
        c = (campos or {}).get(k)
        return f"[{(c or k).upper()}]"
    t = re.sub(r"\{\{(.*?)\}\}", rep, txt)
    return re.sub(r" +([,.;:])", r"\1", re.sub(r"  +", " ", t))


def _ctx(settings, fatos: Fatos, atividade: str, variante: dict | None) -> tuple[dict, dict]:
    inst = institucional(settings)
    s = fatos.servidor
    fem = bool(re.search(r"(?i)auditora|servidora|tribut[áa]ria", s.cargo))
    cargo, sigla = s.cargo, ""
    if re.search(r"(?i)auditor", s.cargo):
        cargo, sigla = ("Auditora-Fiscal" if fem else "Auditor-Fiscal") + " da Receita Federal do Brasil", "AFRFB"
    elif re.search(r"(?i)analista", s.cargo) and re.search(r"(?i)tribut", s.cargo):
        cargo, sigla = ("Analista-Tributária" if fem else "Analista-Tributário") + " da Receita Federal do Brasil", "ATRFB"
    ctx = {"nome": s.nome, "cargo": cargo, "matricula": s.matricula, "unidade": s.unidade, "processo": s.processo,
           "orgao": inst["orgao"], "orgao_corregedoria": inst["orgao"], "portaria_longa": inst["portaria_longa"],
           "portaria_curta": inst["portaria_curta"], "atividade": atividade, "cargo_sigla": sigla, "fem": fem}
    campos = {}
    for c in (variante or {}).get("campos", []):
        campos[c["id"]] = c.get("rotulo", c["id"])
        q = CAMPO_DE_PERGUNTA.get(c["id"])
        if q and (t := re.sub(r"\s+", " ", fatos.respostas.get(q, "")).strip().rstrip(".;")) and len(t) <= 160:
            ctx[c["id"]] = t if re.match(r"^[A-ZÀ-Ý]{2}", t) else t[:1].lower() + t[1:]
    return ctx, campos


def carregar_regras(settings) -> Trecho | None:
    """knowledge/regras_coger.md: segue sempre no contexto da IA (marcador R1), em vez de depender da recuperação por similaridade."""
    arq = settings.caminho("knowledge") / "regras_coger.md"
    if not arq.exists():
        return None
    return Trecho(id="regras_coger", tipo="regra", titulo="Regras institucionais da COGER", fonte="regras_coger.md",
                  texto=arq.read_text(encoding="utf8")[:9000], origem="COGER")


def _carregar_modelo(settings, atividade_id: str) -> dict | None:
    arq = settings.caminho("knowledge") / "modelos" / "atividades" / f"{atividade_id}.json"
    return json.loads(arq.read_text(encoding="utf8")) if arq.exists() else None


def _escolher_variante(modelo: dict, resultado: str | None, hits: list[Trecho]) -> dict:
    pontos = {t.extra.get("variante_id"): t.score for t in hits if t.extra.get("atividade_id") == modelo["id"]}
    cand = [v for v in modelo["variantes"] if not resultado or v["resultado"] == resultado] or modelo["variantes"]
    return max(cand, key=lambda v: pontos.get(v["id"], 0.0))


def _relatorio(settings, fatos: Fatos, ctx: dict, inst: dict) -> Secao:
    tipo = fatos.servidor.tipo or "consulta"
    ctx = {**ctx, "demanda": "o pedido" if tipo == "pedido" else "a consulta"}
    paras = [Paragrafo(texto=preencher(inst["abertura"][tipo], ctx), fontes=["modelo institucional"]),
             Paragrafo(texto=preencher(inst["identificacao"], ctx), fontes=["formulário SeCI"])]
    for i in range(1, 10):
        r = (fatos.respostas.get(i) or "").strip()
        if not r:
            continue
        paras.append(Paragrafo(texto=f"{i} – {inst['perguntas_seci'][i - 1]}", tipo="cit", fontes=["formulário SeCI"]))
        paras.append(Paragrafo(texto="“" + r.replace("\n", " ") + ("”" if re.search(r"[.!?…]$", r) else ".”"), tipo="cit", fontes=["formulário SeCI"]))
    paras.append(Paragrafo(texto=f"10 – {inst['perguntas_seci'][9]}", tipo="cit", fontes=["formulário SeCI"]))
    paras.append(Paragrafo(texto="“Autorização.”" if tipo == "pedido" else "“Consulta.”", tipo="cit", fontes=["formulário SeCI"]))
    return Secao(titulo="I. RELATÓRIO", paragrafos=paras)


def _fund_offline(modelo: dict | None, variante: dict | None, ctx: dict, campos: dict, minuta: Minuta) -> list[Paragrafo]:
    if not modelo or not variante:
        minuta.avisos.append("Sem modelo institucional para a atividade: a fundamentação precisa ser redigida manualmente.")
        return [Paragrafo(texto="[FUNDAMENTAÇÃO]")]
    base = f"{variante.get('fonte', '')} · modelo {modelo['id']}/{variante['id']}"
    corpo = [b for b in variante["corpo"] if not b.get("opc") or b["opc"].get("padrao")]
    ic = max((i for i, b in enumerate(corpo) if b["t"] == "p"), default=-1)  # o último parágrafo é a conclusão do modelo
    out = []
    for i, b in enumerate(corpo):
        if i == ic:
            continue
        if b["t"] == "p":
            out.append(Paragrafo(texto=preencher(b["x"], ctx, campos), fontes=[base]))
        else:
            for ln in b["x"]:
                out.append(Paragrafo(texto=preencher(ln, ctx, campos), tipo="cit", fontes=[base]))
    return out


def _fund_ia(provider, settings, fatos: Fatos, recup: dict, minuta: Minuta, resultado: str | None) -> list[Paragrafo] | None:
    s = settings
    resumo = (f"Atividade: {fatos.atividade}\nEntidade: {fatos.entidade}\nRemuneração: {fatos.remuneracao}\n"
              f"Vínculo: {fatos.vinculo}\nDescrição: {fatos.descricao}\nAtribuições do cargo: {'; '.join(fatos.atribuicoes)}")
    if s.get("ia.anonimizar", True):
        from ..utilities.text import anonimizar
        resumo = anonimizar(resumo, fatos.servidor.nome)
    try:
        ctx, mapa = C.montar_contexto(resumo, recup["normativos"], recup["precedentes"], recup["pareceres"], recup["modelos"],
                                      bool(s.get("ia.anonimizar", True)), regras=carregar_regras(s))
    except C.ContextoInsuficiente as e:
        minuta.avisos.append(f"IA não utilizada: {e}.")
        return None
    sistema = P.carregar("reasoning", s) + "\n\n" + P.carregar("draft", s)
    if resultado:
        sistema += f"\nO parecerista já definiu o resultado: {resultado}. Fundamente nessa direção, apontando eventuais riscos."
    try:
        bruto = provider.completar(sistema, ctx, json_mode=True)
        dado = json.loads(re.search(r"\{.*\}", bruto, re.S).group(0))
    except Exception as e:
        minuta.avisos.append(f"IA indisponível ou resposta inválida ({e}); usada a fundamentação extrativa.")
        return None
    out = []
    for p in dado.get("fundamentacao", []):
        fontes = [f"{mapa[m].titulo} ({mapa[m].fonte})" for m in p.get("fontes", []) if m in mapa]
        if not fontes:
            minuta.avisos.append("Um parágrafo da IA foi descartado por não citar fonte válida do acervo.")
            continue
        out.append(Paragrafo(texto=str(p.get("texto", "")).strip(), fontes=fontes))
    if dado.get("resultado_sugerido") in RESULTADOS:
        minuta.resultado_sugerido = dado["resultado_sugerido"]
    minuta.ressalvas = [str(r) for r in dado.get("ressalvas", [])][:12]
    for lac in dado.get("lacunas", []):
        minuta.avisos.append(f"Lacuna apontada pela IA: {lac}")
    minuta.modo = "copilot"
    return out or None


def gerar_minuta(settings, fatos: Fatos, classif: Classificacao, recup: dict, provider, resultado: str | None = None,
                 atividade_id: str | None = None) -> Minuta:
    inst = institucional(settings)
    minuta = Minuta()
    aid = atividade_id or (classif.escolhida.id if classif.escolhida else "generico")
    modelo = _carregar_modelo(settings, aid)
    variante = _escolher_variante(modelo, resultado, recup.get("modelos", [])) if modelo else None
    atividade = rot_padrao(modelo["nome"]) if modelo else (fatos.atividade or "[ATIVIDADE]")
    ctx, campos = _ctx(settings, fatos, atividade, variante)

    minuta.resultado_sugerido = (variante or {}).get("resultado", "sem_conflito_ressalvas")
    minuta.atividade_id, minuta.variante_id = aid, (variante or {}).get("id", "")
    secoes = [_relatorio(settings, fatos, ctx, inst)]

    fund = _fund_ia(provider, settings, fatos, recup, minuta, resultado) if provider.usa_ia else None
    if fund is None:
        fund = _fund_offline(modelo, variante, ctx, campos, minuta)
        minuta.modo = "offline"
    final = resultado or minuta.resultado_sugerido
    autoriza = final.startswith("sem_")
    if autoriza:
        itens = list(inst["deveres"])
        fund.append(Paragrafo(texto=preencher("Em resumo, em qualquer caso, {{g:o servidor|a servidora}} deve:", ctx), fontes=["Parecer Coger/GNP nº 522/2023, item 13"]))
        for j, t in enumerate(itens):
            fund.append(Paragrafo(texto=f"**{chr(97 + j)})** {t}", tipo="it", fontes=["Parecer Coger/GNP nº 522/2023, item 13"]))
        minuta.ressalvas = minuta.ressalvas or itens
    fund.append(Paragrafo(texto=preencher(inst["nova_consulta"], {**ctx}), fontes=["modelo institucional"]))
    secoes.append(Secao(titulo="II. FUNDAMENTAÇÃO", paragrafos=fund))

    # conclusão: a do próprio modelo quando coincide com o resultado; do contrário, o modelo-padrão do resultado escolhido
    if variante and variante["resultado"] == final:
        corpo = [b for b in variante["corpo"] if not b.get("opc") or b["opc"].get("padrao")]
        ps = [b for b in corpo if b["t"] == "p"]
        conc = preencher(ps[-1]["x"], ctx, campos) if ps else preencher(inst["conclusao_por_resultado"][final], ctx)
    else:
        conc = preencher(inst["conclusao_por_resultado"][final], ctx)
        if variante and variante["resultado"] != final:
            minuta.avisos.append("O resultado escolhido difere do modelo: revise os fundamentos para que sustentem a conclusão.")
    conclusao = [Paragrafo(texto=conc, fontes=[f"modelo institucional ({final})"])]
    if final == "sem_conflito_ressalvas":
        conclusao.append(Paragrafo(texto=preencher(inst["termo_registro"], ctx), fontes=["modelo institucional"]))
    conclusao.append(Paragrafo(texto=inst["encaminha_conflito"].replace("{{enquadramento}}", "") if final == "conflito" else inst["encaminha"],
                               fontes=["modelo institucional"]))
    secoes.append(Secao(titulo="III. CONCLUSÃO", paragrafos=conclusao))
    minuta.secoes = secoes
    minuta.resultado_sugerido = final if resultado else minuta.resultado_sugerido
    if resultado is None:
        minuta.avisos.append("Resultado sugerido: confirme ou altere antes de gerar o documento (decisão do parecerista).")
    return minuta


def ementa(settings, atividade: str, resultado: str, tipo: str, modelo: dict | None, variante: dict | None,
           ctx: dict | None = None, campos: dict | None = None) -> list[str]:
    inst = institucional(settings)
    if variante and variante["resultado"] == resultado and variante.get("ementa"):
        linhas = [variante.get("ementaTitulo", "")] + list(variante["ementa"])
    else:
        pre = "Pedido de autorização" if tipo == "pedido" else "Consulta"
        linhas = [f"{pre} para exercício da atividade de {atividade}. {inst['ementa_por_resultado'][resultado]}"]
    return [preencher(x, ctx or {}, campos) for x in linhas]
