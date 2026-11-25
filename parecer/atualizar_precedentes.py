#!/usr/bin/env python3
"""Baixa da Busca de Precedentes do SeCI/CGU (https://seci.cgu.gov.br/busca/, API pública) as ementas de casos já respondidos.

Gera:
  1. parecer/precedentes_cgu.json  - TODOS os casos da RFB (de 2014 até hoje), embutidos no gerador HTML (python3 parecer/build.py);
  2. (opcional) --md PASTA - arquivos Markdown com os casos de TODOS os órgãos, para a biblioteca da COGER:
       CGU_Precedentes_RFB.md e CGU_Precedentes_Outros_Orgaos_<ano>-<ano>.md
     (o gerador e o motor os indexam como precedentes; cada caso começa por "Protocolo SeCI nº ...").
Uso:  python3 parecer/atualizar_precedentes.py [--md /caminho/saida] && python3 parecer/build.py
"""
import argparse, collections, datetime, json, pathlib, re, time, urllib.request

API = "https://seci.cgu.gov.br/api/BuscaSeci/Avancada"
ORGAO_RFB = 77
AQUI = pathlib.Path(__file__).resolve().parent


def pagina(orgao, n):
    corpo = {"termoBusca": None, "nup": None, "orgaoId": orgao, "dataSubmissaoInicio": None, "dataSubmissaoFim": None,
             "dataEnvioInicio": None, "dataEnvioFim": None, "dataRespostaInicio": None, "dataRespostaFim": None,
             "resultadoRevisao": None, "situacaoConflitoInteresse": None, "tipologiaConflitoInteresse": None,
             "tipoDecisaoRecurso": None, "numPagina": n, "itensPorPagina": 100}
    req = urllib.request.Request(API, data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json", "Accept": "application/json"})
    for t in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r).get("solicitacoes") or []
        except Exception:
            if t == 2:
                raise
            time.sleep(2 * (t + 1))


def buscar(orgao=None):
    itens, n = [], 0
    while True:
        lote = pagina(orgao, n)
        itens += lote
        if len(lote) < 100:
            return itens
        n += 1
        time.sleep(0.4)          # sem sobrecarregar o serviço


def nup_fmt(n):
    m = re.fullmatch(r"(\d{5})(\d{6})(\d{4})(\d{2})", n or "")
    return f"{m[1]}.{m[2]}/{m[3]}-{m[4]}" if m else (n or "")


def limpa(t):
    return re.sub(r"\s+", " ", (t or "").replace("-\n", "")).strip()


def item(s):
    return {"n": nup_fmt(s["nup"]), "d": s["dataResposta"][:10], "r": s["descTipoRespostaAutorizacao"] or "",
            "rec": s["descTipoDecisaoRecurso"] or "", "t": s["descTipologiaConflitoInteresse"] or "",
            "o": s.get("nomeOrgao") or "", "x": limpa(s["resumo"])}


def md(itens):
    blocos = []
    for i in itens:
        cab = f"Protocolo SeCI nº {i['n']} · {i['d']} · {i['o']} · {i['r'] or 'resultado não informado'}" + (f" · {i['t']}" if i["t"] else "") + (f" · recurso: {i['rec']}" if i["rec"] and i["rec"] != "Não se aplica" else "")
        blocos.append(cab + "\n" + i["x"])
    return "\n\n".join(blocos) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", help="pasta onde gravar os arquivos Markdown de todos os órgãos")
    a = ap.parse_args()
    hoje = datetime.date.today()
    todos = sorted((item(s) for s in buscar(None)), key=lambda i: (i["d"], i["n"]), reverse=True)
    rfb = [i for i in todos if "Receita Federal" in i["o"]]
    dados = {"orgao": "RFB", "desde": min(i["d"] for i in rfb), "baixadoEm": hoje.isoformat(), "total_cgu": len(todos),
             "itens": [{k: v for k, v in i.items() if k != "o"} for i in rfb]}
    (AQUI / "precedentes_cgu.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"RFB: {len(rfb)} casos ({dados['desde']} a {rfb[0]['d']}) em precedentes_cgu.json; base total da CGU: {len(todos)}")
    if a.md:
        saida = pathlib.Path(a.md); saida.mkdir(parents=True, exist_ok=True)
        cab = f"<!-- Precedentes do SeCI/CGU (https://seci.cgu.gov.br/busca/), baixados em {hoje.isoformat()}. Texto público e anonimizado. -->\n\n"
        (saida / "CGU_Precedentes_RFB.md").write_text(cab + md(rfb), encoding="utf8")
        outros = [i for i in todos if i not in rfb]
        grupos = [(2014, 2017), (2018, 2019), (2020, 2021), (2022, 2023), (2024, 2026)]
        for ini, fim in grupos:
            sel = [i for i in outros if ini <= int(i["d"][:4]) <= fim]
            (saida / f"CGU_Precedentes_Outros_Orgaos_{ini}-{fim}.md").write_text(cab + md(sel), encoding="utf8")
            print(f"  {ini}-{fim}: {len(sel)} casos")
        res = collections.Counter(i["r"] or "(sem resultado)" for i in todos)
        print("Resultados:", dict(res.most_common()))


if __name__ == "__main__":
    main()
