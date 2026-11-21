#!/usr/bin/env python3
"""Baixa da Busca de Precedentes do SeCI/CGU (https://seci.cgu.gov.br/busca/) as ementas de casos
da RFB respondidos nos últimos 3 anos e grava parecer/precedentes_cgu.json.
Uso:  python3 parecer/atualizar_precedentes.py && python3 parecer/build.py
"""
import datetime, json, pathlib, re, urllib.request

API = "https://seci.cgu.gov.br/api/BuscaSeci/Avancada"
ORGAO_RFB = 77
AQUI = pathlib.Path(__file__).resolve().parent


def buscar(inicio):
    itens, pagina = [], 0
    while True:
        corpo = {"termoBusca": None, "nup": None, "orgaoId": ORGAO_RFB, "dataSubmissaoInicio": None,
                 "dataSubmissaoFim": None, "dataEnvioInicio": None, "dataEnvioFim": None,
                 "dataRespostaInicio": inicio, "dataRespostaFim": None, "resultadoRevisao": None,
                 "situacaoConflitoInteresse": None, "tipologiaConflitoInteresse": None,
                 "tipoDecisaoRecurso": None, "numPagina": pagina, "itensPorPagina": 100}
        req = urllib.request.Request(API, data=json.dumps(corpo).encode(),
                                     headers={"Content-Type": "application/json", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            lote = json.load(r).get("solicitacoes") or []
        itens += lote
        if len(lote) < 100:
            return itens
        pagina += 1


def main():
    hoje = datetime.date.today()
    inicio = hoje.replace(year=hoje.year - 3).isoformat() + "T00:00:00"
    saida = []
    for s in sorted(buscar(inicio), key=lambda s: s["dataResposta"], reverse=True):
        n = s["nup"]
        m = re.fullmatch(r"(\d{5})(\d{6})(\d{4})(\d{2})", n or "")
        saida.append({
            "n": f"{m[1]}.{m[2]}/{m[3]}-{m[4]}" if m else n,
            "d": s["dataResposta"][:10],
            "r": s["descTipoRespostaAutorizacao"] or "",
            "rec": s["descTipoDecisaoRecurso"] or "",
            "t": s["descTipologiaConflitoInteresse"] or "",
            "x": re.sub(r"\s+", " ", (s["resumo"] or "").replace("-\n", "")).strip(),
        })
    dados = {"orgao": "RFB", "desde": inicio[:10], "baixadoEm": hoje.isoformat(), "itens": saida}
    (AQUI / "precedentes_cgu.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf8")
    print(len(saida), "precedentes gravados")


if __name__ == "__main__":
    main()
