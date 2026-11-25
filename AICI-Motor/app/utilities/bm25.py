"""BM25 em Python puro: busca lexical sem dependências, adequada para um acervo de milhares de trechos."""
from __future__ import annotations

import math
from collections import Counter


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.4, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.len = [len(d) for d in docs]
        self.avg = (sum(self.len) / len(docs)) if docs else 0.0
        df: Counter = Counter()
        for t in self.tf:
            df.update(t.keys())
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.inv: dict[str, list[int]] = {}
        for i, t in enumerate(self.tf):
            for term in t:
                self.inv.setdefault(term, []).append(i)

    def pontuar(self, consulta: list[str]) -> dict[int, float]:
        """Devolve {indice_do_documento: score} apenas para documentos com algum termo da consulta."""
        out: dict[int, float] = {}
        for term in set(consulta):
            idf = self.idf.get(term)
            if idf is None:
                continue
            for i in self.inv[term]:
                f = self.tf[i][term]
                denom = f + self.k1 * (1 - self.b + self.b * self.len[i] / (self.avg or 1))
                out[i] = out.get(i, 0.0) + idf * f * (self.k1 + 1) / denom
        return out
