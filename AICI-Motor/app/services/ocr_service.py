"""Módulo 2 - OCR. Só é acionado quando o PDF não tem camada de texto. EasyOCR é opcional (requirements-opcional.txt)."""
from __future__ import annotations

_reader = None


def ocr_disponivel() -> bool:
    try:
        import easyocr  # noqa: F401
        return True
    except Exception:
        return False


def _leitor(idiomas):
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(list(idiomas), gpu=False, verbose=False)
    return _reader


def ocr_pagina(doc, indice: int, idiomas=("pt", "en"), dpi: int = 200) -> str:
    """Renderiza a página como imagem e devolve o texto reconhecido ("" se o OCR não estiver instalado)."""
    if not ocr_disponivel():
        return ""
    png = doc[indice].get_pixmap(dpi=dpi).tobytes("png")
    linhas = _leitor(idiomas).readtext(png, detail=0, paragraph=True)
    return "\n".join(linhas)
