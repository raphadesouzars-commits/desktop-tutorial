"""Módulo 1 - Leitor de PDF: abrir_pdf, extrair_texto, corrigir_quebras, normalizar. Saída: ConsultaText."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf as fitz  # PyMuPDF

from . import ocr_service


@dataclass
class ConsultaText:
    texto: str
    paginas: int
    usou_ocr: bool = False
    avisos: list[str] = field(default_factory=list)


def abrir_pdf(caminho: str | Path | bytes) -> "fitz.Document":
    if isinstance(caminho, (bytes, bytearray)):
        return fitz.open(stream=bytes(caminho), filetype="pdf")
    return fitz.open(str(caminho))


def extrair_texto(doc: "fitz.Document") -> list[str]:
    """Texto de cada página, na ordem de leitura."""
    return [p.get_text("text", sort=True) for p in doc]


_LIG = str.maketrans({"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", " ": " ", "​": "", "­": ""})


def corrigir_quebras(texto: str) -> str:
    """Conserta hifenização no fim da linha e remove espaços/linhas em branco excessivos.
    Mantém uma linha por linha do PDF: o extrator de fatos depende do alinhamento "rótulo: valor"."""
    t = texto.replace("\r", "")
    t = re.sub(r"(\w)-\n(?=[a-zà-ÿ])", r"\1", t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFC", texto).translate(_LIG)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t.strip()


def ler_consulta(origem: str | Path | bytes, ocr: bool = True, idiomas=("pt", "en"), min_chars: int = 40) -> ConsultaText:
    doc = abrir_pdf(origem)
    try:
        paginas = extrair_texto(doc)
        avisos: list[str] = []
        usou = False
        for i, tx in enumerate(paginas):
            if len(tx.strip()) >= min_chars:
                continue
            if not ocr:
                avisos.append(f"Página {i + 1} sem texto e OCR desabilitado.")
            elif not ocr_service.ocr_disponivel():
                avisos.append(f"Página {i + 1} parece digitalizada, mas o OCR (EasyOCR) não está instalado.")
            else:
                paginas[i] = ocr_service.ocr_pagina(doc, i, idiomas); usou = True
        texto = normalizar(corrigir_quebras("\n\n".join(paginas)))
        if not texto:
            avisos.append("Nenhum texto foi extraído do PDF.")
        return ConsultaText(texto=texto, paginas=len(paginas), usou_ocr=usou, avisos=avisos)
    finally:
        doc.close()
