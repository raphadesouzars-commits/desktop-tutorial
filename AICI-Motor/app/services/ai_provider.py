"""Módulo 8 - Camada de IA. O motor só conhece a interface AIProvider; quem está por trás (nenhuma IA, Copilot Studio, Azure OpenAI,
outro modelo homologado) é configuração em config/settings.yaml (ia.provider).

REGRA MAIS IMPORTANTE: a IA nunca recebe apenas o PDF. montar_contexto() só monta o contexto com normativos + precedentes/pareceres/modelos;
sem isso levanta ContextoInsuficiente e nenhuma chamada é feita."""
from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod

import httpx

from ..models.schemas import Trecho
from ..utilities.text import anonimizar


class ContextoInsuficiente(Exception):
    """O acervo não devolveu base suficiente para chamar a IA."""


class ErroIA(Exception):
    pass


# ------------------------------------------------------------------ interface
class AIProvider(ABC):
    nome = "base"
    usa_ia = False

    @abstractmethod
    def completar(self, sistema: str, usuario: str, json_mode: bool = False) -> str:
        """Primitiva: instrução de sistema + mensagem do usuário -> texto."""

    def analyze(self, prompt: str, context: dict) -> str:
        """Forma de alto nível: um prompt e um contexto estruturado (dict) -> texto."""
        corpo = "\n\n".join(f"=== {k} ===\n{v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}" for k, v in context.items())
        return self.completar(prompt, corpo)


Provider = AIProvider   # nome antigo, mantido por compatibilidade


class RespostaProvider(AIProvider):
    """Devolve uma resposta já obtida (ex.: colada pelo parecerista a partir do Copilot Chat), para passar pela mesma validação de fontes."""
    nome = "copilot_chat_assistido"
    usa_ia = True

    def __init__(self, resposta: str, limite_contexto: int = 200000):
        self.resposta, self.limite_contexto = resposta, limite_contexto   # limite_contexto: o que o chat realmente recebeu

    def completar(self, sistema, usuario, json_mode=False):
        return self.resposta


class OfflineProvider(AIProvider):
    """Sem IA: o motor funciona só com a base (parecer extrativo a partir dos modelos institucionais)."""
    nome = "offline"
    usa_ia = False

    def completar(self, sistema, usuario, json_mode=False):
        raise ErroIA("provider offline não gera texto")


class MockProvider(AIProvider):
    """Respostas programadas, para testes e demonstrações sem IA real. `respostas` mapeia um trecho do prompt de sistema à resposta."""
    nome = "mock"
    usa_ia = True

    def __init__(self, respostas: dict[str, str] | None = None):
        self.respostas, self.chamadas = respostas or {}, []

    def completar(self, sistema, usuario, json_mode=False):
        self.chamadas.append((sistema, usuario))
        for chave, resp in self.respostas.items():
            if chave in sistema:
                return resp
        raise ErroIA("MockProvider: sem resposta programada para este prompt")


# ------------------------------------------------------------------ provedores HTTP
def _caminho(dado, caminho: str):
    for parte in str(caminho).split("."):
        try:
            dado = dado[int(parte)] if isinstance(dado, list) else dado[parte]
        except Exception as e:
            raise ErroIA(f"resposta inesperada da IA (caminho '{caminho}')") from e
    return dado


class HTTPProvider(AIProvider):
    usa_ia = True

    def __init__(self, cfg: dict, temperatura: float = 0.1):
        self.cfg, self.temp = cfg, temperatura

    def _url(self) -> str:
        if not self.cfg.get("endpoint"):
            raise ErroIA(f"ia.{self.nome}.endpoint não configurado em config/settings.yaml")
        return self.cfg["endpoint"]

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        tok = os.environ.get(self.cfg.get("token_env", ""), "")
        if tok:
            h[self.cfg.get("cabecalho_auth", "Authorization")] = self.cfg.get("prefixo_auth", "Bearer ") + tok
        return h

    def _corpo(self, sistema: str, usuario: str, json_mode: bool) -> dict:
        corpo = {"messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}], "temperature": self.temp}
        if self.cfg.get("modelo"):
            corpo["model"] = self.cfg["modelo"]
        if json_mode:
            corpo["response_format"] = {"type": "json_object"}
        return corpo

    caminho_resposta = "choices.0.message.content"

    def completar(self, sistema, usuario, json_mode=False):
        try:
            r = httpx.post(self._url(), json=self._corpo(sistema, usuario, json_mode), headers=self._headers(),
                           timeout=float(self.cfg.get("timeout_s", 120)), verify=bool(self.cfg.get("verificar_tls", True)))
            r.raise_for_status()
            dado = r.json()
        except ErroIA:
            raise
        except Exception as e:
            raise ErroIA(f"falha ao chamar {self.nome}: {e}") from e
        return str(_caminho(dado, self.cfg.get("caminho_resposta", self.caminho_resposta)))


class CopilotProvider(HTTPProvider):
    """Copilot Studio publicado por HTTPS, ou gateway interno homologado. formato "openai" (messages -> choices) ou "custom"
    (corpo_template com {{system}}/{{user}} e caminho_resposta). Só use se a TI informar endpoint, autenticação e formato."""
    nome = "copilot"

    def _corpo(self, sistema, usuario, json_mode):
        if self.cfg.get("formato", "openai") == "openai":
            return super()._corpo(sistema, usuario, json_mode)

        def sub(x):
            if isinstance(x, str):
                return {"{{system}}": sistema, "{{user}}": usuario}.get(x, x)
            if isinstance(x, list):
                return [sub(i) for i in x]
            if isinstance(x, dict):
                return {k: sub(v) for k, v in x.items()}
            return x
        return sub(json.loads(self.cfg["corpo_template"]))


class AzureOpenAIProvider(HTTPProvider):
    """Azure OpenAI corporativo: endpoint (https://<recurso>.openai.azure.com), deployment e api_version fornecidos pela TI."""
    nome = "azure"

    def _url(self):
        c = self.cfg
        if not (c.get("endpoint") and c.get("deployment") and c.get("api_version")):
            raise ErroIA("ia.azure exige endpoint, deployment e api_version")
        return f"{c['endpoint'].rstrip('/')}/openai/deployments/{c['deployment']}/chat/completions?api-version={c['api_version']}"

    def _headers(self):
        h = {"Content-Type": "application/json"}
        tok = os.environ.get(self.cfg.get("token_env", "AICI_AZURE_KEY"), "")
        if tok:
            h["api-key"] = tok
        return h

    def _corpo(self, sistema, usuario, json_mode):
        c = super()._corpo(sistema, usuario, json_mode)
        c.pop("model", None)   # no Azure o modelo é o deployment
        return c


class OpenAIProvider(HTTPProvider):
    """API compatível com OpenAI. Atenção: a API pública NÃO é IA homologada pela RFB; por segurança só funciona com
    ia.openai.confirmo_homologado: true (use com gateways/modelos que a instituição tenha aprovado)."""
    nome = "openai"

    def _url(self):
        if not self.cfg.get("confirmo_homologado"):
            raise ErroIA("ia.openai.confirmo_homologado não está ativado: dados de consulta não serão enviados a provedor não homologado")
        return self.cfg.get("endpoint") or "https://api.openai.com/v1/chat/completions"

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if tok := os.environ.get(self.cfg.get("token_env", "AICI_OPENAI_KEY"), ""):
            h["Authorization"] = "Bearer " + tok
        return h


class AuditedProvider(AIProvider):
    """Registra cada chamada à IA em metrics/ia_auditoria.jsonl (RNF003/RNF004; Port. RFB 647/2026, art. 12, parágrafo único e art. 19):
    quando, qual provedor, tamanho e, se `registrar_conteudo`, o prompt e a resposta (já com identificadores mascarados), para o curador."""

    def __init__(self, interno: AIProvider, arquivo, registrar_conteudo: bool = True):
        self.interno, self.arquivo, self.conteudo = interno, arquivo, registrar_conteudo
        self.nome, self.usa_ia = interno.nome, interno.usa_ia

    def completar(self, sistema, usuario, json_mode=False):
        from datetime import datetime
        import pathlib
        reg = {"quando": datetime.now().isoformat(timespec="seconds"), "provider": self.nome, "chars_entrada": len(sistema) + len(usuario)}
        try:
            r = self.interno.completar(sistema, usuario, json_mode)
            reg.update(ok=True, chars_saida=len(r))
            if self.conteudo:
                reg.update(sistema=sistema, entrada=usuario, saida=r)
            return r
        except Exception as e:
            reg.update(ok=False, erro=str(e)[:300])
            raise
        finally:
            arq = pathlib.Path(self.arquivo); arq.parent.mkdir(parents=True, exist_ok=True)
            with arq.open("a", encoding="utf8") as f:
                f.write(json.dumps(reg, ensure_ascii=False) + "\n")


def criar_provider(settings) -> AIProvider:
    nome = settings.get("ia.provider", "offline")
    t = float(settings.get("ia.temperatura", 0.1))
    if nome == "offline":
        return OfflineProvider()
    if nome == "mock":
        return MockProvider()
    classes = {"copilot": CopilotProvider, "azure": AzureOpenAIProvider, "openai": OpenAIProvider}
    if nome not in classes:
        raise ErroIA(f"ia.provider desconhecido: {nome} (use offline, mock, copilot, azure ou openai)")
    prov = classes[nome](settings.get(f"ia.{nome}", {}) or {}, t)
    if settings.get("ia.auditoria.habilitada", True):
        return AuditedProvider(prov, settings.caminho("metrics") / "ia_auditoria.jsonl", bool(settings.get("ia.auditoria.registrar_conteudo", True)))
    return prov


# ------------------------------------------------------------------ contexto
def montar_contexto(fatos_txt: str, normativos: list[Trecho], precedentes: list[Trecho], pareceres: list[Trecho],
                    modelos: list[Trecho], anonimizar_texto: bool = True, limite: int = 28000,
                    regras: Trecho | None = None) -> tuple[str, dict[str, Trecho]]:
    """Monta o contexto enviado à IA e o mapa marcador -> trecho (para validar as fontes citadas na resposta).
    `regras` (knowledge/regras_coger.md) acompanha sempre o contexto, como marcador R1.
    Com limite pequeno (ex.: prompt do Copilot Chat), o espaço é repartido entre os trechos (prioridade N, P, A, M) e os que não
    cabem ficam de fora - e deixam de poder ser citados."""
    if not normativos:
        raise ContextoInsuficiente("nenhum normativo recuperado: a IA não será chamada só com o caso")
    if not (precedentes or pareceres or modelos):
        raise ContextoInsuficiente("nenhum precedente, parecer ou modelo recuperado: a IA não será chamada só com o caso")
    cabeca = "=== CASO CONCRETO ===\n" + fatos_txt + "\n\n"
    tit = {"R": "REGRAS INSTITUCIONAIS DA COGER", "N": "NORMATIVOS", "P": "PRECEDENTES", "A": "PARECERES DA COGER", "M": "MODELOS INSTITUCIONAIS"}
    regras_txt = ""
    if regras:
        regras_txt = regras.texto if limite >= 20000 else _regras_resumidas(regras.texto)[: int(limite * 0.2)]
    itens = [(l, t) for l, lista in (("N", normativos), ("P", precedentes), ("A", pareceres), ("M", modelos)) for t in lista]
    base = len(cabeca) + len(regras_txt) + 120 + 90 * 5
    cap = min(1800, (limite - base) // max(len(itens), 1))
    while cap < 300 and len(itens) > 2:
        itens.pop(); cap = min(1800, (limite - base) // len(itens))
    cap = max(cap, 150)
    mapa: dict[str, Trecho] = {}
    blocos: list[str] = []
    if regras:
        mapa["R1"] = regras
        blocos.append(f"=== {tit['R']} ===\n[R1] {regras.titulo} ({regras.fonte})\n{regras_txt}")
    cont: dict[str, int] = {}
    ultimo = ""
    for letra, t in itens:
        cont[letra] = cont.get(letra, 0) + 1
        mid = f"{letra}{cont[letra]}"
        corpo = anonimizar(t.texto) if anonimizar_texto else t.texto
        corpo = corpo if len(corpo) <= cap else corpo[:cap].rsplit(" ", 1)[0] + " [...]"
        if letra != ultimo:
            blocos.append(f"=== {tit[letra]} ==="); ultimo = letra
        mapa[mid] = t
        blocos.append(f"[{mid}] {t.titulo} ({t.fonte})\n{corpo}")
    ctx = (cabeca + "\n\n".join(blocos))[:limite]
    return ctx, {k: v for k, v in mapa.items() if f"[{k}]" in ctx}   # só vale citar o que a IA efetivamente recebeu


def _regras_resumidas(texto: str) -> str:
    """Versão curta de regras_coger.md para prompts pequenos: sem a lista de categorias (seção 3) nem a seção de pendências (7)."""
    import re
    partes = re.split(r"(?m)^(?=## )", texto)
    return "".join(p for p in partes if not re.match(r"## (3|7)\.", p))
