"""Carrega config/settings.yaml. A base do projeto pode ser trocada com AICI_HOME (útil em testes)."""
from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import yaml

RAIZ = Path(os.environ.get("AICI_HOME") or Path(__file__).resolve().parent.parent)


def _mescla(base: dict, extra: dict) -> dict:
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _mescla(base[k], v)
        else:
            base[k] = v
    return base


class Settings:
    def __init__(self, dados: dict, raiz: Path):
        self.dados = dados
        self.raiz = raiz

    def __getitem__(self, k: str) -> Any:
        return self.dados[k]

    def get(self, caminho: str, padrao: Any = None) -> Any:
        """get("ia.copilot.endpoint")"""
        atual: Any = self.dados
        for parte in caminho.split("."):
            if not isinstance(atual, dict) or parte not in atual:
                return padrao
            atual = atual[parte]
        return atual

    def caminho(self, chave: str) -> Path:
        p = Path(self.dados["caminhos"][chave])
        return p if p.is_absolute() else self.raiz / p


def carregar(arquivo: str | Path | None = None, sobrescrever: dict | None = None) -> Settings:
    arq = Path(arquivo or os.environ.get("AICI_CONFIG") or RAIZ / "config" / "settings.yaml")
    dados = yaml.safe_load(arq.read_text(encoding="utf8")) or {}
    if sobrescrever:
        dados = _mescla(copy.deepcopy(dados), sobrescrever)
    return Settings(dados, RAIZ)
