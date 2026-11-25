import json
import zipfile

import docx
import pytest
from fastapi.testclient import TestClient

from app.services import ai_provider as C
from app.services import fact_extractor, indexer, pdf_reader
from app.services.classifier import Classificador
from app.services.retriever import Retriever
from app.models.schemas import Fatos, Trecho
from conftest import IAFalsa, pdf_em_branco, pdf_seci


# ---------------------------------------------------------------- leitor de PDF / OCR
def test_pdf_texto_e_limpeza(pdf_consulta):
    ct = pdf_reader.ler_consulta(pdf_consulta, ocr=False)
    assert ct.paginas == 2 and "Nome Completo" in ct.texto and not ct.usou_ocr
    assert pdf_reader.corrigir_quebras("administra-\nção pública\n\n\n\nfim") == "administração pública\n\nfim"


def test_pdf_sem_texto_avisa_ocr_ausente():
    ct = pdf_reader.ler_consulta(pdf_em_branco(), ocr=True)
    assert ct.texto == "" and any("OCR" in a or "texto" in a for a in ct.avisos)


# ---------------------------------------------------------------- extrator de fatos
def test_extrator_formulario_seci(pdf_consulta):
    f = fact_extractor.extrair_fatos(pdf_reader.ler_consulta(pdf_consulta, ocr=False).texto)
    s = f.servidor
    assert s.nome == "Maria Aparecida de Souza Lima" and s.matricula == "1234567"
    assert s.protocolo == "00096.000123/2023-45" and s.tipo == "pedido" and s.cargo == "Auditora-Fiscal da Receita Federal do Brasil"
    assert set(range(1, 11)) <= set(f.respostas)
    assert "professora universitária" in f.descricao and "3.500,00" in f.remuneracao
    assert "Universidade Particular Exemplo" in f.entidade
    assert f.respostas[10].strip() == "Autorização"


# ---------------------------------------------------------------- indexador / recuperação
def test_indexacao_incremental(settings):
    s = indexer.criar_store(settings)
    r1 = indexer.indexar(settings, s)
    assert r1["novos"] >= 4 and not r1["erros"] and r1["chunks"]["modelo"] > 100 and r1["chunks"]["normativo"] > 0
    r2 = indexer.indexar(settings, indexer.criar_store(settings))
    assert r2["novos"] == 0 and r2["alterados"] == 0            # nada mudou: nada reprocessado
    arq = settings.caminho("knowledge") / "pareceres" / "PA_211_2026_Sindico.txt"
    arq.write_text(arq.read_text(encoding="utf8") + " Acréscimo.", encoding="utf8")
    assert indexer.indexar(settings, indexer.criar_store(settings))["alterados"] == 1
    arq.unlink()
    assert indexer.indexar(settings, indexer.criar_store(settings))["removidos"] == 1


def test_recuperacao_traz_origem_e_tipos(settings):
    store = indexer.criar_store(settings); indexer.indexar(settings, store)
    f = Fatos(atividade="Professor universitário", descricao="lecionar em faculdade particular de Direito")
    rec = Retriever(settings, store).recuperar(f)
    assert rec["pareceres"][0].numero == "145" and rec["pareceres"][0].ano == "2025"
    assert rec["pareceres"][0].fonte.startswith("pareceres/") and "termos em comum" in rec["pareceres"][0].motivo
    assert rec["precedentes"] and rec["precedentes"][0].tema == "Docencia"
    assert any("12813" in t.fonte for t in rec["normativos"])          # a Lei é recuperada para o caso
    assert all(t.tipo == "modelo" for t in rec["modelos"])


# ---------------------------------------------------------------- classificador
def test_classificador_usa_so_categorias_do_html(settings):
    cl = Classificador(settings)
    f = Fatos(atividade="síndico", descricao="Pretendo ser síndico do condomínio onde resido")
    res = cl.classificar(f)
    assert res.escolhida.id == "sindico"
    # IA tenta inventar uma categoria: descartada
    ia = IAFalsa({"Escolha a categoria": json.dumps({"id": "FEITICARIA", "justificativa": "x"})})
    res2 = cl.classificar(f, provider=ia)
    assert res2.escolhida.id == "sindico" and any("fora da lista" in a for a in res2.avisos)
    # IA escolhe entre as candidatas: aceita
    outra = res.candidatas[1].id if len(res.candidatas) > 1 else None
    if outra:
        ia2 = IAFalsa({"Escolha a categoria": json.dumps({"id": outra, "justificativa": "x"})})
        assert cl.classificar(f, provider=ia2).escolhida.id == outra


def test_sem_correspondencia_cai_no_generico(settings):
    res = Classificador(settings).classificar(Fatos(descricao="xyzzy qwerty"))
    assert res.escolhida.id == "generico" and res.escolhida.confianca == "baixa" and res.avisos


# ---------------------------------------------------------------- conector Copilot
def _t(tipo, i):
    return Trecho(id=f"{tipo}{i}", tipo=tipo, titulo=f"{tipo} {i}", fonte=f"{tipo}s/{i}.txt", texto="Texto com CPF 123.456.789-09")


def test_ia_nunca_recebe_so_o_caso():
    with pytest.raises(C.ContextoInsuficiente):
        C.montar_contexto("caso", [], [_t("precedente", 1)], [], [])
    with pytest.raises(C.ContextoInsuficiente):
        C.montar_contexto("caso", [_t("normativo", 1)], [], [], [])
    ctx, mapa = C.montar_contexto("caso", [_t("normativo", 1)], [_t("precedente", 1)], [_t("parecer", 1)], [])
    assert "[N1]" in ctx and "[P1]" in ctx and "[A1]" in ctx and "[CPF]" in ctx and "123.456" not in ctx
    assert mapa["N1"].fonte == "normativos/1.txt"


def test_copilot_formatos_e_erros(monkeypatch):
    with pytest.raises(C.ErroIA):
        C.CopilotProvider({"endpoint": ""}).completar("s", "u")
    enviados = {}

    class R:
        def __init__(self, d): self.d = d
        def raise_for_status(self): pass
        def json(self): return self.d

    def post(url, json, headers, timeout, verify):
        enviados.update(url=url, json=json, headers=headers); return R({"choices": [{"message": {"content": "ok"}}]})
    monkeypatch.setattr(C.httpx, "post", post)
    monkeypatch.setenv("TOK_X", "segredo")
    p = C.CopilotProvider({"endpoint": "https://gw.interno/v1", "token_env": "TOK_X", "modelo": "m1"})
    assert p.completar("sis", "usr", json_mode=True) == "ok"
    assert enviados["headers"]["Authorization"] == "Bearer segredo" and enviados["json"]["model"] == "m1"
    assert enviados["json"]["messages"][0] == {"role": "system", "content": "sis"}
    custom = C.CopilotProvider({"endpoint": "https://gw/x", "formato": "custom", "caminho_resposta": "saida.0",
                                "corpo_template": '{"prompt": {"s": "{{system}}", "u": "{{user}}"}}'})
    monkeypatch.setattr(C.httpx, "post", lambda url, json, headers, timeout, verify: (enviados.update(json=json), R({"saida": ["texto"]}))[1])
    assert custom.completar("S", "U") == "texto" and enviados["json"] == {"prompt": {"s": "S", "u": "U"}}


# ---------------------------------------------------------------- API ponta a ponta (sem IA)
def _app(settings, provider=None):
    from main import criar_app
    return criar_app(settings, provider=provider)


def test_fluxo_completo_offline(settings, pdf_consulta, monkeypatch):
    monkeypatch.delenv("AICI_TOKEN", raising=False)
    with TestClient(_app(settings)) as c:
        assert c.get("/saude").json()["arquivos_indexados"] >= 4
        up = c.post("/upload", files={"arquivo": ("consulta.pdf", pdf_consulta, "application/pdf")}, data={"usuario": "t"}).json()
        cid = up["consulta_id"]; assert up["paginas"] == 2 and up["status"] == "recebida"
        a = c.post("/analisar", json={"consulta_id": cid}).json()
        assert a["fatos"]["servidor"]["nome"].startswith("Maria")
        assert a["classificacao"]["escolhida"]["id"] == "magisterio"
        assert a["normativos"] and a["pareceres"] and a["precedentes"]
        titulos = [s["titulo"] for s in a["minuta"]["secoes"]]
        assert titulos == ["I. RELATÓRIO", "II. FUNDAMENTAÇÃO", "III. CONCLUSÃO"]
        assert all(p["fontes"] for s in a["minuta"]["secoes"] for p in s["paragrafos"])   # toda frase com origem
        r = c.post("/gerar-parecer", json={"validado": True, "consulta_id": cid, "numero": "300", "ano": "2026"})
        assert r.status_code == 200 and r.headers["content-type"].startswith("application/vnd.openxmlformats")
        arq = settings.caminho("output") / f"consulta_{cid}" / "parecer_300_2026.docx"
        d = docx.Document(str(arq)); txt = "\n".join(p.text for p in d.paragraphs)
        for h in ("I. RELATÓRIO", "II. FUNDAMENTAÇÃO", "III. CONCLUSÃO", "Maria Aparecida de Souza Lima", "Parecer Coger/GNP nº 300/2026"):
            assert h in txt
        assert "{{" not in txt and "}}" not in txt
        # decisão humana: o parecerista troca a conclusão -> a conclusão e o aviso mudam
        r2 = c.post("/gerar-parecer", json={"validado": True, "consulta_id": cid, "resultado": "conflito", "numero": "301", "ano": "2026"})
        d2 = docx.Document(str(settings.caminho("output") / f"consulta_{cid}" / "parecer_301_2026.docx"))
        assert "configura situação de conflito de interesses" in "\n".join(p.text for p in d2.paragraphs)
        # termo só para risco mitigável; despacho sempre
        assert c.post("/gerar-parecer", json={"validado": True, "consulta_id": cid, "documento": "termo", "resultado": "conflito"}).status_code == 422
        assert c.post("/gerar-parecer", json={"validado": True, "consulta_id": cid, "documento": "termo", "resultado": "sem_conflito_ressalvas", "numero": "300", "ano": "2026"}).status_code == 200
        assert c.post("/gerar-parecer", json={"validado": True, "consulta_id": cid, "documento": "despacho", "destino": "a Comissão de Ética"}).status_code == 200
        ind = c.get("/indicadores").json()
        assert ind["total_consultas"] == 1 and ind["total_pareceres"] == 2 and ind["por_atividade"][0]["n"] == 2
        assert (settings.caminho("metrics") / "metricas.jsonl").read_text().count("\n") == 2


def test_api_validacoes_e_token(settings, pdf_consulta, monkeypatch):
    monkeypatch.setenv("AICI_TOKEN", "s3cr3t")
    with TestClient(_app(settings)) as c:
        assert c.get("/saude").status_code == 401
        h = {"X-AICI-Token": "s3cr3t"}
        assert c.get("/saude", headers=h).status_code == 200
        assert c.post("/upload", files={"arquivo": ("x.pdf", b"MZ nao eh pdf", "application/pdf")}, headers=h).status_code == 400
        assert c.post("/analisar", json={"consulta_id": 999}, headers=h).status_code == 404
        cid = c.post("/upload", files={"arquivo": ("c.pdf", pdf_consulta, "application/pdf")}, headers=h).json()["consulta_id"]
        assert c.post("/gerar-parecer", json={"validado": True, "consulta_id": cid}, headers=h).status_code == 409   # ainda não analisada
        assert c.post("/analisar", json={"consulta_id": cid}, headers=h).status_code == 200
        assert c.post("/gerar-parecer", json={"validado": True, "consulta_id": cid, "atividade_id": "inexistente"}, headers=h).status_code == 422


def test_cors_do_html_aberto_como_arquivo(settings, monkeypatch):
    monkeypatch.delenv("AICI_TOKEN", raising=False)
    with TestClient(_app(settings)) as c:
        r = c.options("/analisar", headers={"Origin": "null", "Access-Control-Request-Method": "POST",
                                            "Access-Control-Request-Headers": "content-type"})
        assert r.headers.get("access-control-allow-origin") == "null"
        assert c.get("/saude", headers={"Origin": "https://malicioso.example"}).headers.get("access-control-allow-origin") is None


# ---------------------------------------------------------------- caminho com IA
def test_ia_fundamentacao_com_fontes_validadas(settings, pdf_consulta, monkeypatch):
    monkeypatch.delenv("AICI_TOKEN", raising=False)
    resp = json.dumps({"fundamentacao": [
        {"texto": "A docência não é incompatível com o cargo.", "fontes": ["N1", "A1"]},
        {"texto": "Parágrafo inventado sem base.", "fontes": ["X9"]}],
        "resultado_sugerido": "sem_conflito_ressalvas", "ressalvas": ["observar horários"], "lacunas": ["remuneração"]})
    ia = IAFalsa({"Redija a FUNDAMENTAÇÃO": resp, "Extraia os fatos": json.dumps({"atividade": "Docência universitária", "entidade": "Universidade Particular Exemplo", "remuneracao": "R$ 3.500,00/mês", "vinculo": "horista", "descricao": "x", "atribuicoes": []}),
                  "Escolha a categoria": json.dumps({"id": "magisterio", "justificativa": "docência"}),
                  "explique em uma frase": json.dumps({"itens": [{"id": "A1", "similaridade": "também docência privada", "aplicavel": True}]})})
    with TestClient(_app(settings, ia)) as c:
        cid = c.post("/upload", files={"arquivo": ("c.pdf", pdf_consulta, "application/pdf")}).json()["consulta_id"]
        a = c.post("/analisar", json={"consulta_id": cid}).json()
    m = a["minuta"]
    assert m["modo"] == "copilot" and m["ressalvas"] == ["observar horários"]
    fund = [p for s in m["secoes"] if s["titulo"].startswith("II") for p in s["paragrafos"]]
    assert fund[0]["texto"].startswith("A docência") and any("normativos/" in f for f in fund[0]["fontes"])
    assert not any("inventado" in p["texto"] for p in fund)                 # sem fonte válida -> descartado
    assert any("fonte válida" in x for x in m["avisos"]) and any("Lacuna" in x for x in m["avisos"])
    assert a["fatos"]["origem"] == "heuristica+ia" and a["fatos"]["servidor"]["nome"].startswith("Maria")
    for sis, usr in ia.chamadas:                                              # a IA nunca viu CPF/matrícula/telefone e sempre recebeu normativos
        assert "123.456.789-09" not in usr and "1234567" not in usr
    assert any("=== NORMATIVOS ===" in usr for sis, usr in ia.chamadas if "Redija" in sis)
    assert any("também docência privada" == t["motivo"] for t in a["pareceres"] + a["precedentes"])


def test_ia_indisponivel_cai_no_extrativo(settings, pdf_consulta, monkeypatch):
    monkeypatch.delenv("AICI_TOKEN", raising=False)
    with TestClient(_app(settings, IAFalsa({}))) as c:                          # IAFalsa levanta erro em toda chamada
        cid = c.post("/upload", files={"arquivo": ("c.pdf", pdf_consulta, "application/pdf")}).json()["consulta_id"]
        a = c.post("/analisar", json={"consulta_id": cid}).json()
    assert a["minuta"]["modo"] == "offline" and any("IA indisponível" in x for x in a["minuta"]["avisos"])


# ---------------------------------------------------------------- backend vetorial opcional (Chroma)
def test_backend_chroma(settings):
    chromadb = pytest.importorskip("chromadb")
    import hashlib
    from chromadb import Documents, EmbeddingFunction, Embeddings
    from app.utilities.text import tokens

    class Hash(EmbeddingFunction):          # embedding determinístico, sem baixar modelo: serve para validar a integração
        def __init__(self): pass
        def __call__(self, input: Documents) -> Embeddings:
            out = []
            for d in input:
                v = [0.0] * 256
                for t in tokens(d):
                    v[int(hashlib.md5(t.encode()).hexdigest(), 16) % 256] += 1.0
                n = sum(x * x for x in v) ** 0.5 or 1.0
                out.append([x / n for x in v])
            return out
        @staticmethod
        def name() -> str: return "hash-teste"
        def get_config(self): return {}
        @staticmethod
        def build_from_config(c): return Hash()

    cfg = settings.dados; cfg["indexador"]["backend"] = "chroma"
    store = indexer.criar_store(settings, Hash())
    r = indexer.indexar(settings, store)
    assert r["backend"] == "chroma" and not r["erros"] and r["chunks"]["total"] > 100
    rec = Retriever(settings, store).recuperar(Fatos(atividade="Professor universitário", descricao="lecionar em faculdade particular de Direito"))
    assert rec["pareceres"] and rec["pareceres"][0].numero == "145"
    assert indexer.indexar(settings, indexer.criar_store(settings, Hash()))["novos"] == 0


# ---------------------------------------------------------------- busca híbrida (BM25 + embeddings)
class EmbSinonimos:
    """Embedder de teste: palavras do mesmo conceito caem na mesma dimensão (simula o que um modelo semântico faz)."""
    nome = "sinonimos"
    CONCEITOS = [{"professor", "docencia", "magisterio", "aula", "universitario", "lecionar", "ensino", "faculdade"},
                 {"sindico", "condominio", "assembleia", "taxa"}]

    def _v(self, t):
        from app.utilities.text import tokens
        tk = set(tokens(t))
        v = [float(len(tk & c)) for c in self.CONCEITOS] + [0.01]
        n = sum(x * x for x in v) ** 0.5
        return [x / n for x in v]

    def embed_documentos(self, textos): return [self._v(t) for t in textos]
    def embed_consulta(self, texto): return self._v(texto)


def test_busca_hibrida_acha_o_que_o_bm25_nao_acha(settings):
    pytest.importorskip("numpy")
    from app.services.embeddings import DenseStore
    k = settings.caminho("knowledge")
    for f in (k / "pareceres").glob("*"): f.unlink()
    for f in (k / "precedentes").rglob("*.txt"): f.unlink()
    (k / "pareceres" / "PA_300_2025_Ensino.txt").write_text(
        "Atividade de docência e magistério em instituição de ensino, com aulas noturnas e compatibilidade de horários.", encoding="utf8")
    (k / "pareceres" / "PA_301_2025_Condominio.txt").write_text(
        "Síndico de condomínio, assembleia e taxa condominial.", encoding="utf8")
    emb = EmbSinonimos()
    store = indexer.criar_store(settings)
    r = indexer.indexar(settings, store, embedder=emb)
    assert r["vetores"]["vetores"] == r["chunks"]["parecer"] + r["chunks"].get("normativo", 0) + r["chunks"]["modelo"]
    f = Fatos(atividade="Professor universitário", descricao="lecionar aula")    # nenhuma palavra em comum com o parecer 300... exceto 'aula'
    f2 = Fatos(atividade="Professor universitário")                              # sem nenhum termo em comum
    so_bm25 = Retriever(settings, store).recuperar(f2)["pareceres"]
    hibrido = Retriever(settings, store, emb, DenseStore(settings.caminho("vectorstore"))).recuperar(f2)["pareceres"]
    assert not so_bm25 or so_bm25[0].numero != "300"
    assert hibrido[0].numero == "300" and "similaridade semântica" in hibrido[0].motivo
    # incremental: nada mudou -> nenhum vetor novo
    assert indexer.indexar(settings, indexer.criar_store(settings), embedder=emb)["vetores"]["novos"] == 0


# ---------------------------------------------------------------- provedores de IA
def test_provedores_configuracao(monkeypatch):
    with pytest.raises(C.ErroIA):
        C.AzureOpenAIProvider({"endpoint": "https://r.openai.azure.com"}).completar("s", "u")        # faltam deployment/api_version
    with pytest.raises(C.ErroIA):
        C.OpenAIProvider({}).completar("s", "u")                                                      # não homologado: nada é enviado
    capt = {}

    class R:
        def raise_for_status(self): pass
        def json(self): return {"choices": [{"message": {"content": "azul"}}]}
    monkeypatch.setattr(C.httpx, "post", lambda url, json, headers, timeout, verify: (capt.update(url=url, json=json, headers=headers), R())[1])
    monkeypatch.setenv("CHAVE_AZ", "k1")
    az = C.AzureOpenAIProvider({"endpoint": "https://r.openai.azure.com/", "deployment": "gpt-4o", "api_version": "2024-06-01",
                                "token_env": "CHAVE_AZ", "modelo": "ignorado"})
    assert az.completar("s", "u") == "azul"
    assert capt["url"] == "https://r.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-06-01"
    assert capt["headers"]["api-key"] == "k1" and "model" not in capt["json"]
    oa = C.OpenAIProvider({"confirmo_homologado": True, "endpoint": "https://gw.interno/v1/chat", "modelo": "m", "token_env": "CHAVE_AZ"})
    assert oa.completar("s", "u") == "azul" and capt["headers"]["Authorization"] == "Bearer k1" and capt["json"]["model"] == "m"
    # interface de alto nível e fábrica
    mock = C.MockProvider({"instr": "resp"})
    assert mock.analyze("instr", {"caso": "x", "n": [1, 2]}) == "resp" and "=== caso ===" in mock.chamadas[0][1]
    from app.config import carregar
    assert isinstance(C.criar_provider(carregar()), C.OfflineProvider)
    with pytest.raises(C.ErroIA):
        C.criar_provider(carregar(sobrescrever={"ia": {"provider": "inexistente"}}))


def test_regras_coger_sempre_no_contexto(settings):
    from app.services import report_generator as R
    regras = R.carregar_regras(settings)
    assert regras and "Categorias válidas" in regras.texto
    ctx, mapa = C.montar_contexto("caso", [_t("normativo", 1)], [_t("precedente", 1)], [], [], regras=regras)
    assert "REGRAS INSTITUCIONAIS DA COGER" in ctx and mapa["R1"].fonte == "regras_coger.md"


# ---------------------------------------------------------------- revisão humana obrigatória e auditoria da IA
def test_geracao_exige_validacao_humana(settings, pdf_consulta, monkeypatch):
    monkeypatch.delenv("AICI_TOKEN", raising=False)
    with TestClient(_app(settings)) as c:
        cid = c.post("/upload", files={"arquivo": ("c.pdf", pdf_consulta, "application/pdf")}).json()["consulta_id"]
        c.post("/analisar", json={"consulta_id": cid})
        r = c.post("/gerar-parecer", json={"consulta_id": cid})
        assert r.status_code == 422 and "Revisão humana" in r.json()["detail"]
        assert c.post("/gerar-parecer", json={"consulta_id": cid, "validado": True}).status_code == 200


def test_auditoria_das_chamadas_de_ia(tmp_path):
    log = tmp_path / "aud.jsonl"
    p = C.AuditedProvider(C.MockProvider({"x": "resposta"}), log)
    assert p.usa_ia and p.completar("instrução x", "entrada mascarada [CPF]") == "resposta"
    with pytest.raises(C.ErroIA):
        p.completar("outra", "e")
    linhas = [json.loads(l) for l in log.read_text(encoding="utf8").splitlines()]
    assert linhas[0]["ok"] and linhas[0]["saida"] == "resposta" and linhas[0]["entrada"] == "entrada mascarada [CPF]"
    assert not linhas[1]["ok"] and "erro" in linhas[1]
