"""Módulo 8 - Conector Copilot (IA homologada). O motor só fala com a IA por esta interface.
REGRA MAIS IMPORTANTE: a IA nunca recebe apenas o PDF. O contexto sempre leva normativos + precedentes/pareceres/modelos;
sem isso, montar_contexto() levanta ContextoInsuficiente e nenhuma chamada é feita."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod

import httpx

from ..models.schemas import Trecho
from ..utilities.text import anonimizar


class ContextoInsuficiente(Exception):
    """O acervo não devolveu base suficiente para chamar a IA."""


class ErroIA(Exception):
    pass


class Provider(ABC):
    nome = "base"
    usa_ia = False

    @abstractmethod
    def completar(self, sistema: str, usuario: str, json_mode: bool = False) -> str: ...


class OfflineProvider(Provider):
    """Sem IA: o motor funciona só com a base (parecer extrativo a partir dos modelos institucionais)."""
    nome = "offline"
    usa_ia = False

    def completar(self, sistema, usuario, json_mode=False):
        raise ErroIA("provider offline não gera texto")


class CopilotProvider(Provider):
    """Gateway HTTP do Copilot/IA homologada. O formato "openai" (messages -> choices) cobre a maioria dos gateways;
    "custom" usa um corpo_template próprio. Endpoint e token são configuração local - nada fica no código."""
    nome = "copilot"
    usa_ia = True

    def __init__(self, cfg: dict, temperatura: float = 0.1):
        self.cfg, self.temp = cfg, temperatura
        if not cfg.get("endpoint"):
            raise ErroIA("ia.copilot.endpoint não configurado em config/settings.yaml")

    def _corpo(self, sistema: str, usuario: str, json_mode: bool):
        if self.cfg.get("formato", "openai") == "openai":
            corpo = {"messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
                     "temperature": self.temp}
            if self.cfg.get("modelo"):
                corpo["model"] = self.cfg["modelo"]
            if json_mode:
                corpo["response_format"] = {"type": "json_object"}
            return corpo
        import json
        modelo = json.loads(self.cfg["corpo_template"])

        def sub(x):
            if isinstance(x, str):
                return {"{{system}}": sistema, "{{user}}": usuario}.get(x, x)
            if isinstance(x, list):
                return [sub(i) for i in x]
            if isinstance(x, dict):
                return {k: sub(v) for k, v in x.items()}
            return x
        return sub(modelo)

    def completar(self, sistema, usuario, json_mode=False):
        headers = {"Content-Type": "application/json"}
        tok = os.environ.get(self.cfg.get("token_env", "AICI_COPILOT_TOKEN"), "")
        if tok:
            headers[self.cfg.get("cabecalho_auth", "Authorization")] = self.cfg.get("prefixo_auth", "Bearer ") + tok
        try:
            r = httpx.post(self.cfg["endpoint"], json=self._corpo(sistema, usuario, json_mode), headers=headers,
                           timeout=float(self.cfg.get("timeout_s", 120)), verify=bool(self.cfg.get("verificar_tls", True)))
            r.raise_for_status()
            dado = r.json()
        except Exception as e:
            raise ErroIA(f"falha ao chamar o Copilot: {e}") from e
        for parte in str(self.cfg.get("caminho_resposta", "choices.0.message.content")).split("."):
            try:
                dado = dado[int(parte)] if isinstance(dado, list) else dado[parte]
            except Exception as e:
                raise ErroIA(f"resposta inesperada do Copilot (caminho {self.cfg.get('caminho_resposta')})") from e
        return str(dado)


def criar_provider(settings) -> Provider:
    nome = settings.get("ia.provider", "offline")
    if nome == "copilot":
        return CopilotProvider(settings.get("ia.copilot", {}), float(settings.get("ia.temperatura", 0.1)))
    return OfflineProvider()


def montar_contexto(fatos_txt: str, normativos: list[Trecho], precedentes: list[Trecho], pareceres: list[Trecho],
                    modelos: list[Trecho], anonimizar_texto: bool = True, limite: int = 28000) -> tuple[str, dict[str, Trecho]]:
    """Monta o contexto enviado à IA e o mapa marcador -> trecho (para validar as fontes citadas na resposta)."""
    if not normativos:
        raise ContextoInsuficiente("nenhum normativo recuperado: a IA não será chamada só com o caso")
    if not (precedentes or pareceres or modelos):
        raise ContextoInsuficiente("nenhum precedente, parecer ou modelo recuperado: a IA não será chamada só com o caso")
    mapa: dict[str, Trecho] = {}
    blocos: list[str] = []
    grupos = (("N", "NORMATIVOS", normativos), ("P", "PRECEDENTES", precedentes), ("A", "PARECERES DA COGER", pareceres),
              ("M", "MODELOS INSTITUCIONAIS", modelos))
    for letra, titulo, itens in grupos:
        if not itens:
            continue
        blocos.append(f"=== {titulo} ===")
        for i, t in enumerate(itens, 1):
            mid = f"{letra}{i}"
            mapa[mid] = t
            corpo = anonimizar(t.texto) if anonimizar_texto else t.texto
            blocos.append(f"[{mid}] {t.titulo} ({t.fonte})\n{corpo}")
    ctx = "=== CASO CONCRETO ===\n" + fatos_txt + "\n\n" + "\n\n".join(blocos)
    return ctx[:limite], mapa
