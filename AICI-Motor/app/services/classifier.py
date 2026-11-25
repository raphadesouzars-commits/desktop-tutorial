"""Módulo 7 - Classificador. As categorias vêm de config/categorias.json (exportado do gerador HTML).
Regra: a IA nunca inventa categoria - qualquer resposta fora da lista é descartada."""
from __future__ import annotations

import json
import re

from ..models.schemas import Candidata, Classificacao, Fatos, Trecho
from ..utilities.bm25 import BM25
from ..utilities.text import tokens
from . import prompts as P
from .retriever import texto_da_consulta

GENERICA = "generico"


class Classificador:
    def __init__(self, settings):
        self.s = settings
        dados = json.loads(settings.caminho("categorias").read_text(encoding="utf8"))["categorias"]
        self.cats = {c["id"]: c for c in dados}
        self.ids = list(self.cats)
        docs = []
        for c in dados:
            kw = " ".join(c.get("palavrasChave", []))
            texto = f"{c['nome']} {c['nome']} {kw} {kw} {c.get('descricao','')} " + " ".join(v["rotulo"] for v in c["variantes"])
            docs.append(tokens(texto))
        self.bm = BM25(docs)

    def palavras_chave(self, id_: str) -> list[str]:
        return self.cats.get(id_, {}).get("palavrasChave", [])

    def _confianca(self, s1: float, s2: float, tem_voto: bool) -> str:
        margem = s1 - s2
        if s1 >= 0.75 and margem >= 0.25 and tem_voto:
            return "alta"
        return "media" if margem >= 0.12 and s1 >= 0.5 else "baixa"

    def classificar(self, f: Fatos, modelos: list[Trecho] | None = None, provider=None, n: int = 5) -> Classificacao:
        q = tokens(texto_da_consulta(f))
        base = {self.ids[i]: s for i, s in self.bm.pontuar(q).items() if self.ids[i] != GENERICA}
        votos: dict[str, float] = {}
        for t in modelos or []:
            aid = t.extra.get("atividade_id")
            if aid and aid != GENERICA:
                votos[aid] = votos.get(aid, 0.0) + t.score
        mb, mv = max(base.values(), default=0.0), max(votos.values(), default=0.0)
        final = {}
        for aid in set(base) | set(votos):
            final[aid] = 0.6 * (base.get(aid, 0) / mb if mb else 0) + 0.4 * (votos.get(aid, 0) / mv if mv else 0)
        ordem = sorted(final.items(), key=lambda x: -x[1])[:n]
        res = Classificacao(metodo="lexical" + ("+modelos" if votos else ""))
        if not ordem:
            res.avisos.append("Nenhuma categoria reconhecida: use o modelo genérico ou escolha a atividade manualmente.")
            g = self.cats.get(GENERICA)
            if g:
                res.escolhida = Candidata(id=GENERICA, nome=g["nome"], score=0.0, confianca="baixa", motivos=["sem correspondência"])
                res.candidatas = [res.escolhida]
            return res
        for i, (aid, sc) in enumerate(ordem):
            seg = ordem[i + 1][1] if i + 1 < len(ordem) else 0.0
            motivos = [f"palavra-chave: {k}" for k in self.palavras_chave(aid) if set(tokens(k)) <= set(q)][:4]
            if aid in votos:
                motivos.append("modelos institucionais semelhantes")
            res.candidatas.append(Candidata(id=aid, nome=self.cats[aid]["nome"], score=round(sc, 3),
                                            confianca=self._confianca(sc, seg, aid in votos) if i == 0 else "baixa", motivos=motivos))
        res.escolhida = res.candidatas[0]
        if provider is not None and getattr(provider, "usa_ia", False):
            self._refinar_com_ia(res, f, provider)
        if res.escolhida.confianca == "baixa":
            res.avisos.append("Enquadramento com baixa confiança: confirme a atividade antes de gerar o parecer.")
        return res

    def _refinar_com_ia(self, res: Classificacao, f: Fatos, provider) -> None:
        """A IA só pode escolher entre as candidatas já recuperadas; qualquer outra resposta é ignorada."""
        try:
            lista = "\n".join(f"- {c.id}: {c.nome}" for c in res.candidatas)
            sistema = P.carregar("classify", self.s)
            bruto = provider.completar(P.preencher(sistema, categorias=lista), texto_da_consulta(f), json_mode=True)
            esc = json.loads(re.search(r"\{.*\}", bruto, re.S).group(0)).get("id", "")
            alvo = next((c for c in res.candidatas if c.id == esc), None)
            if alvo is None:
                res.avisos.append("A IA sugeriu uma categoria fora da lista e a sugestão foi descartada.")
                return
            if alvo is not res.escolhida:
                res.candidatas.remove(alvo); res.candidatas.insert(0, alvo); res.escolhida = alvo
            res.metodo += "+ia"
            alvo.motivos.append("confirmada pela IA entre as candidatas")
        except Exception:
            res.avisos.append("A IA não respondeu à classificação; mantido o resultado lexical.")
