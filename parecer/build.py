#!/usr/bin/env python3
"""Monta o arquivo único gerador-parecer-conflito.html a partir de:
   parecer/app.src.html  (interface e lógica)
   parecer/modelos/*.json (um arquivo por atividade)
   parecer/cabecalho.jpg  (imagem do cabeçalho do parecer)
   parecer/vendor/pdf*.js (pdf.js 3.11.174, para ler o formulário em PDF sem internet)
   parecer/vendor/ocr/* (tesseract.js 7 + dados do português, para PDF sem camada de texto)
   parecer/precedentes_cgu.json (ementas da CGU; atualize com atualizar_precedentes.py)
   parecer/kb_local.json (instruções, regras e normativos para o prompt do Copilot Chat; gerar_kb_local.py)
Uso:  python3 parecer/build.py
"""
import base64, gzip, json, pathlib, struct, sys

AQUI = pathlib.Path(__file__).resolve().parent
SAIDA = AQUI.parent / "gerador-parecer-conflito.html"


def dim_jpeg(b):
    i = 2
    while i < len(b):
        if b[i] != 0xFF:
            i += 1
            continue
        m = b[i + 1]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack(">HH", b[i + 5:i + 9])
            return [w, h]
        i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    raise ValueError("dimensões do JPEG não encontradas")


def main():
    modelos = []
    for f in sorted((AQUI / "modelos").glob("*.json")):
        modelos.append(json.loads(f.read_text(encoding="utf8")))
    ids = [m["id"] for m in modelos]
    if len(ids) != len(set(ids)):
        sys.exit("ids de atividade repetidos")
    logo = (AQUI / "cabecalho.jpg").read_bytes()
    html = (AQUI / "app.src.html").read_text(encoding="utf8")
    dados = json.dumps(modelos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = html.replace("/*__MODELOS__*/[]", dados)
    prec = json.loads((AQUI / "precedentes_cgu.json").read_text(encoding="utf8"))
    html = html.replace('/*__PRECEDENTES__*/{"itens":[]}',
                        json.dumps(prec, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    kb = (AQUI / "kb_local.json")
    html = html.replace('/*__KB__*/{}', json.dumps(json.loads(kb.read_text(encoding="utf8")), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") if kb.exists() else "{}")
    ocr = AQUI / "vendor" / "ocr"
    if (ocr / "por.traineddata.gz").exists():     # OCR offline (tesseract.js, Apache-2.0): lê PDF cujo texto é imagem ou desenho
        for marca, arq in (("/*__OCR_JS__*/", "tesseract.min.js"), ("/*__OCR_WORKER__*/", "worker.min.js"), ("/*__OCR_CORE__*/", "tesseract-core-simd-lstm.wasm.js")):
            html = html.replace(marca, base64.b64encode(gzip.compress((ocr / arq).read_bytes(), 9, mtime=0)).decode())
        html = html.replace("/*__OCR_POR__*/", base64.b64encode((ocr / "por.traineddata.gz").read_bytes()).decode())
    for marca, arq in (("/*__PDFJS__*/", "pdf.min.js"), ("/*__PDFW__*/", "pdf.worker.min.js")):
        gz = gzip.compress((AQUI / "vendor" / arq).read_bytes(), 9, mtime=0)
        html = html.replace(marca, base64.b64encode(gz).decode())
    html = html.replace("/*__LOGO__*/", base64.b64encode(logo).decode())
    html = html.replace("/*__LOGO_DIM__*/[1300,137]", json.dumps(dim_jpeg(logo)))
    SAIDA.write_text(html, encoding="utf8")
    print(f"{SAIDA.name}: {len(modelos)} atividades, "
          f"{sum(len(m['variantes']) for m in modelos)} variantes, {len(html) // 1024} KB")


if __name__ == "__main__":
    main()
