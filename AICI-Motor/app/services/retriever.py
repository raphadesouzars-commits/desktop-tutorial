"""Módulo 6 - Recuperação de conhecimento (RAG). Devolve, por tipo, os trechos mais relevantes COM a origem de cada um."""
from __future__ import annotations

from ..models.schemas import Fatos, Trecho
from ..utilities.text import norm


def texto_da_consulta(f: Fatos) -> str:
    """O que descreve o caso (e só isso): atividade, entidade e descrição. Atribuições do cargo ficam de fora de propósito."""
    partes = [f.atividade, f.entidade, f.descricao, f.respostas.get(3, "")]
    return " ".join(p for p in partes if p)


class Retriever:
    def __init__(self, settings, store):
        self.s, self.store = settings, store

    def _buscar_tipo(self, consulta: str, tipo: str, k: int) -> list[Trecho]:
        bruto = self.store.buscar(consulta, tipo, k * 12)
        peso = float(self.s.get("recuperacao.peso_coger", 1.25))
        melhor: dict[str, tuple] = {}
        for c, sc, comuns in bruto:
            sc = sc * (peso if c.origem == "COGER" and tipo != "normativo" else 1.0)   # RN005
            chave = c.fonte if tipo != "modelo" else c.id                                # um trecho por documento (modelo: por variante)
            if chave not in melhor or sc > melhor[chave][1]:
                melhor[chave] = (c, sc, comuns)
        top = sorted(melhor.values(), key=lambda x: -x[1])[:k]
        return [Trecho(id=c.id, tipo=c.tipo, titulo=c.titulo, fonte=c.fonte, texto=c.texto[:1800], tema=c.tema, ano=c.ano,
                       numero=c.numero, score=round(sc, 3), origem=c.origem, extra=c.extra,
                       motivo=("termos em comum: " + ", ".join(comuns[:8])) if comuns else "similaridade semântica")
                for c, sc, comuns in top]

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
