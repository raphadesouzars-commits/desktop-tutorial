"""Módulo 6 - Recuperação de conhecimento (RAG). Devolve, por tipo, os trechos mais relevantes COM a origem de cada um."""
from __future__ import annotations

from ..models.schemas import Fatos, Trecho
from ..utilities.text import norm


def texto_da_consulta(f: Fatos) -> str:
    """O que descreve o caso (e só isso): atividade, entidade e descrição. Atribuições do cargo ficam de fora de propósito."""
    partes = [f.atividade, f.entidade, f.descricao, f.respostas.get(3, "")]
    return " ".join(p for p in partes if p)


class Retriever:
    """HybridRetriever: BM25 (palavras) + embeddings (sentido), fundidos por Reciprocal Rank Fusion e reclassificados pelo peso COGER.
    Sem embedder configurado, funciona só com BM25."""

    def __init__(self, settings, store, embedder=None, dense=None):
        self.s, self.store, self.emb, self.dense = settings, store, embedder, dense

    def _por_chave(self, tipo: str) -> dict:
        from .embeddings import _chave
        return {_chave(c): c for c in getattr(self.store, "chunks", []) if c.tipo == tipo}

    def _candidatos(self, consulta: str, tipo: str, n: int) -> list[tuple]:
        """[(chunk, rrf, termos_em_comum, similaridade|None)] da fusão BM25 + vetores."""
        lex = self.store.buscar(consulta, tipo, n)
        fund: dict[str, list] = {}
        for r, (c, sc, comuns) in enumerate(lex):
            fund[c.id] = [c, 1.0 / (60 + r + 1), comuns, None]
        if self.emb is not None and self.dense is not None:
            perm = self._por_chave(tipo)
            for r, (k, sim) in enumerate(self.dense.buscar(self.emb.embed_consulta(consulta), perm, n)):
                c = perm[k]
                if c.id in fund:
                    fund[c.id][1] += 1.0 / (60 + r + 1); fund[c.id][3] = sim
                else:
                    fund[c.id] = [c, 1.0 / (60 + r + 1), [], sim]
        return [tuple(v) for v in fund.values()]

    def _buscar_tipo(self, consulta: str, tipo: str, k: int) -> list[Trecho]:
        n = int(self.s.get("recuperacao.embeddings.candidatos", 20)) if self.emb is not None else k * 12
        peso = float(self.s.get("recuperacao.peso_coger", 1.25))
        melhor: dict[str, tuple] = {}
        for c, sc, comuns, sim in self._candidatos(consulta, tipo, max(n, k * 3)):
            if self.emb is None:
                sc = sc * 1.0                       # BM25 puro: a pontuação já vem do índice lexical
            sc = sc * (peso if c.origem == "COGER" and tipo != "normativo" else 1.0)   # RN005
            chave = c.fonte if tipo != "modelo" else c.id                                # um trecho por documento (modelo: por variante)
            if chave not in melhor or sc > melhor[chave][1]:
                melhor[chave] = (c, sc, comuns, sim)
        top = sorted(melhor.values(), key=lambda x: -x[1])[:k]
        out = []
        for c, sc, comuns, sim in top:
            partes = []
            if comuns:
                partes.append("termos em comum: " + ", ".join(comuns[:8]))
            if sim is not None:
                partes.append(f"similaridade semântica ({sim:.2f})")
            out.append(Trecho(id=c.id, tipo=c.tipo, titulo=c.titulo, fonte=c.fonte, texto=c.texto[:1800], tema=c.tema, ano=c.ano,
                              numero=c.numero, score=round(sc * (100 if self.emb is not None else 1), 3), origem=c.origem,
                              extra=c.extra, motivo="; ".join(partes) or "similaridade semântica"))
        return out

    def recuperar(self, f: Fatos, palavras_extra: list[str] | None = None) -> dict[str, list[Trecho]]:
        consulta = texto_da_consulta(f) + " " + " ".join(palavras_extra or [])
        k = lambda n: int(self.s.get(f"recuperacao.top_k_{n}", 4))
        return {
            "pareceres": self._buscar_tipo(consulta, "parecer", k("pareceres")),
            "precedentes": self._buscar_tipo(consulta, "precedente", k("precedentes")),
            # normativos: a consulta ganha as expressões-chave da lei para não depender só do vocabulário do servidor
            "normativos": self._buscar_tipo(consulta + " conflito de interesses atividade privada autorização", "normativo", k("normativos")),
            "modelos": self._buscar_tipo(consulta, "modelo", max(k("modelos"), 6)),
        }
