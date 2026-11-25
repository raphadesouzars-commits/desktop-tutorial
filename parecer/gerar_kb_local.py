#!/usr/bin/env python3
"""Gera parecer/kb_local.json: o pequeno acervo que o gerador HTML leva embutido para montar o prompt do Copilot Chat
sem precisar do motor Python (instruções à IA, regras da COGER e trechos de normativos). Fonte única: AICI-Motor/.
Rode sempre que prompts/, regras_coger.md ou os normativos mudarem; depois, python3 parecer/build.py."""
import json, pathlib, re
import pymupdf

AQUI = pathlib.Path(__file__).resolve().parent
MOTOR = AQUI.parent / "AICI-Motor"


def pdf_texto(p):
    with pymupdf.open(str(p)) as d:
        return "\n".join(x.get_text() for x in d)


def limpa(t):
    return re.sub(r"[ \t]+", " ", re.sub(r"\n{2,}", "\n", t)).strip()


def main():
    lei = pdf_texto(MOTOR / "knowledge/normativos/Lei_12813_2013/Lei_12813_2013.pdf")
    i, j = lei.index("Art. 3º"), lei.index("Art. 6º")
    port = limpa(pdf_texto(MOTOR / "knowledge/normativos/Portarias/Portaria_Interministerial_333_2013.pdf"))
    k = port.find("Art. 1")
    kb = {
        "prompts": {n: (MOTOR / "prompts" / f"{n}.txt").read_text(encoding="utf8") for n in ("reasoning", "draft", "understand")},
        "regras": (MOTOR / "knowledge/regras_coger.md").read_text(encoding="utf8"),
        "normativos": [
            {"titulo": "Lei nº 12.813/2013 (arts. 3º a 5º)", "fonte": "normativos/Lei_12813_2013/Lei_12813_2013.pdf", "texto": limpa(lei[i:j])},
            {"titulo": "Portaria Interministerial MP/CGU nº 333/2013", "fonte": "normativos/Portarias/Portaria_Interministerial_333_2013.pdf",
             "texto": port[k if k >= 0 else 0:][:4500]},
        ],
    }
    (AQUI / "kb_local.json").write_text(json.dumps(kb, ensure_ascii=False, indent=1), encoding="utf8")
    print("kb_local.json:", {k: (len(v) if not isinstance(v, (dict, list)) else len(json.dumps(v))) for k, v in kb.items()})


if __name__ == "__main__":
    main()
