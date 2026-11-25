"""Módulo 9 - Engenharia de prompt. Os textos ficam em prompts/*.txt (editáveis pela equipe, fora do código)."""
from __future__ import annotations

import re

NOMES = ("facts", "precedents", "reasoning", "draft", "review")


def carregar(nome: str, settings) -> str:
    arq = settings.caminho("prompts") / f"{nome}.txt"
    return arq.read_text(encoding="utf8")


def preencher(modelo: str, **vars) -> str:
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(vars.get(m.group(1), m.group(0))), modelo)
