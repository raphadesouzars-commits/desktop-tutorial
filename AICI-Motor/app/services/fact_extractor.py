"""Módulo 3 - Extrator de Fatos.
1) Leitura determinística do formulário SeCI (cabeçalho e perguntas 1 a 10), no mesmo critério do gerador HTML.
2) Opcional: a IA organiza os fatos (prompts/facts.txt). O resultado da IA só preenche o que a leitura direta não achou
   e é validado - nunca substitui dados de identificação do servidor."""
from __future__ import annotations

import json
import re

from ..models.schemas import Fatos, Servidor
from ..utilities.text import anonimizar, norm, titulo_nome
from . import prompts as P

# Trechos que identificam cada pergunta (redação atual do SeCI e a do manual)
CHAVES = [
    ["sua duvida tem relacao"],
    ["descreva a atividade que voce pretende"],
    ["voce estaria vinculado"],
    ["essa pessoa fisica ou juridica", "mantem algum vinculo", "mantenha algum vinculo"],
    ["quais sao as atribuicoes", "atribuicoes de seu cargo"],
    ["quais atividades", "atividades voce exerce efetivamente", "atividades que exerce especificamente"],
    ["voce lida", "informacoes sigilosas"],
    ["no desempenho de sua funcao publica", "seu poder decisorio", "poder decisorio"],
    ["descreva como a situacao", "poderia gerar um conflito", "qual o possivel conflito"],
    ["a partir das informacoes prestadas", "a partir dessas informacoes", "voce gostaria de receber", "seu interesse e receber"],
]

# Cabeçalhos/rodapés que o SeCI repete em toda página do PDF (às vezes colados na mesma linha pela extração)
_RUIDO_TXT = re.compile(r"(?i)controladoria geral da uni[ãa]o|sistema eletr[ôo]nico de conflito de interesses|emitido em:?|p[áa]gina \d+ de \d+")


def limpar_ruido(texto: str) -> str:
    out = []
    for l in texto.split("\n"):
        if _RUIDO_TXT.search(l):
            l = re.sub(r"\s{2,}", " ", _RUIDO_TXT.sub("", l)).strip()
            if re.fullmatch(r"(\d{2}/\d{2}/\d{4})?", l):
                continue
        out.append(l)
    return "\n".join(out)


def separar_perguntas(texto: str) -> dict[int, str]:
    linhas = limpar_ruido(texto).replace("\r", "").split("\n")
    resp: dict[int, list[str]] = {}
    atual, na_pergunta = 0, False
    for ln in linhas:
        mn = re.match(r"^\s*(\d{1,2})\s*[-–—.)]", ln)
        num = int(mn.group(1)) if mn else 0
        sem_num = re.sub(r"^\s*\d{1,2}\s*[-–—.)]*\s*", "", norm(ln))
        q = 0
        for i in range(atual, 10):
            if any((num == i + 1 and k in sem_num) if num else (0 <= sem_num.find(k) <= 4) for k in CHAVES[i]):
                q = i + 1
                break
        if q:
            atual = q; resp[q] = []
            na_pergunta = not re.search(r"[?:.]\s*$", ln)
            r = re.match(r"^.{40,}[?:]\s+(\S.*)$", ln)
            if r and not na_pergunta and not re.search(r"[?:]\s*$", ln) and not re.match(r"(?i)se sim", r.group(1)):
                resp[q].append(r.group(1))
        elif na_pergunta:
            if re.search(r"[?:.]\s*$", ln):
                na_pergunta = False
        elif atual:
            resp[atual].append(ln)
    out = {k: re.sub(r"\n{3,}", "\n\n", "\n".join(v)).strip() for k, v in resp.items()}
    if len(out) >= 2:
        return {k: v.lstrip("±").strip() for k, v in out.items()}
    # sem as frases das perguntas: só pela numeração
    r2: dict[int, list[str]] = {}; atual = 0
    for ln in linhas:
        m = re.match(r"^\s*(\d{1,2})\s*[-–—.)]\s*\S", ln)
        if m and 1 <= int(m.group(1)) <= 10 and int(m.group(1)) > atual:
            atual = int(m.group(1)); r2[atual] = []
        elif atual:
            r2[atual].append(ln)
    return {k: "\n".join(v).strip() for k, v in r2.items()} if len(r2) >= 2 else {}


def extrair_servidor(texto: str) -> Servidor:
    s = Servidor()
    if m := re.search(r"Nome\s+Completo\s*:\s*([^\n]+?)(?:\s{3,}|\n|$)", texto, re.I):
        s.nome = titulo_nome(m.group(1))
    if m := re.search(r"(?:matr[íi]cula(?:\s+(?:siape|funcional))?|siape)\s*(?:n[ºo°.]*)?\s*[:\-–]?\s*(\d[\d.\-]{3,11}\d)", texto, re.I):
        s.matricula = m.group(1)
    if m := re.search(r"Cargo\s*\/?\s*emprego\s*:\s*([^\n]+(?:\n[^\n:]{2,40}(?=\n))?)", texto, re.I):
        s.cargo = re.sub(r"\s+", " ", m.group(1)).strip()
        if re.search(r"(?i)auditor", texto[m.start():m.start() + 200]):
            s.cargo = "Auditora-Fiscal da Receita Federal do Brasil" if re.search(r"(?i)auditora", texto[m.start():m.start() + 200]) else "Auditor-Fiscal da Receita Federal do Brasil"
        elif re.search(r"(?is)analista.{0,40}tribut", texto[m.start():m.start() + 200]):
            s.cargo = "Analista-Tributário da Receita Federal do Brasil"
    if m := re.search(r"Protocolo\s*:\s*(\d{5}\.\d{6}/\d{4}-\d{2})", texto, re.I):
        s.protocolo = m.group(1)
    if m := re.search(r"Tipo de Solicita[çc][ãa]o\s*:\s*(Pedido|Consulta)", texto, re.I):
        s.tipo = "pedido" if m.group(1).lower() == "pedido" else "consulta"
    procs = [n for n in re.findall(r"\b\d{5}\.\d{6}/\d{4}-\d{2}\b", texto) if not n.startswith("00096")]
    if procs:
        s.processo = procs[0]
    if m := re.search(r"(?im)^\s*(?:unidade(?: de (?:exerc[íi]cio|lota[çc][ãa]o))?|lota[çc][ãa]o)\s*[:\-–]\s*(.+)$", texto):
        s.unidade = m.group(1).strip()
    return s


def _heuristica(resp: dict[int, str]) -> dict:
    q2, q3, q5 = resp.get(2, ""), resp.get(3, ""), resp.get(5, "") or resp.get(6, "")
    rem = ""
    if m := re.search(r"(?i)(R\$\s*[\d.]+(?:,\d{2})?(?:\s*(?:por|\/)\s*(?:m[êe]s|hora|aula|palestra|evento))?)", q2 + " " + q3):
        rem = m.group(1)
    elif re.search(r"(?i)sem\s+(?:qualquer\s+)?remunera|gratuit|volunt[áa]ri", q2 + " " + q3):
        rem = "sem remuneração"
    elif re.search(r"(?i)remunera|comiss[ãa]o|honor[áa]rio|pro[- ]labore|monetiz|lucro", q2 + " " + q3):
        rem = "remunerada (valor não informado)"
    entidade = ""
    if m := re.search(r"(?i)\b((?:universidade|faculdade|instituto|col[ée]gio|escola|associa[çc][ãa]o|condom[ií]nio|empresa|sociedade|funda[çc][ãa]o|sindicato|cooperativa)\s+[A-ZÀ-Ý][^\n,.;]{2,70})", q2 + "\n" + q3):
        entidade = m.group(1).strip()
    elif q3 and not re.match(r"(?i)^\s*n[ãa]o\b", q3):
        entidade = q3.split("\n")[0][:120]
    vinculo = "" if re.match(r"(?i)^\s*n[ãa]o\b", q3) or not q3 else re.sub(r"\s+", " ", q3)[:400]
    atrib = [a.strip(" -•;") for a in re.split(r"\n|;|(?<=\.)\s+(?=[A-ZÀ-Ý])", q5) if len(a.strip(" -•;")) > 3]
    return {"descricao": re.sub(r"\s+", " ", q2).strip(), "remuneracao": rem, "entidade": entidade,
            "vinculo": vinculo, "atribuicoes": atrib[:12], "atividade": re.sub(r"\s+", " ", q2).strip()[:200]}


def extrair_fatos(texto: str, provider=None, settings=None) -> Fatos:
    texto = limpar_ruido(texto)
    resp = separar_perguntas(texto)
    f = Fatos(servidor=extrair_servidor(texto), respostas=resp)
    if not resp:
        f.respostas = {2: texto.strip()[:3000]}
    for k, v in _heuristica(f.respostas).items():
        setattr(f, k, v)
    if provider is not None and getattr(provider, "usa_ia", False):
        try:
            ctx = "\n".join(f"{i}. {t}" for i, t in sorted(f.respostas.items()))
            if settings is not None and settings.get("ia.anonimizar", True):
                ctx = anonimizar(ctx, f.servidor.nome)
            bruto = provider.completar(P.carregar("facts", settings), ctx, json_mode=True)
            dados = json.loads(re.search(r"\{.*\}", bruto, re.S).group(0))
            # a IA resume atividade/entidade/remuneração/vínculo; descrição e identificação do servidor vêm só do formulário
            for chave in ("atividade", "entidade", "remuneracao", "vinculo"):
                if isinstance(dados.get(chave), str) and dados[chave].strip():
                    setattr(f, chave, dados[chave].strip()[:400])
            if isinstance(dados.get("atribuicoes"), list) and not f.atribuicoes:
                f.atribuicoes = [str(a) for a in dados["atribuicoes"] if str(a).strip()][:12]
            f.origem = "heuristica+ia"
        except Exception:
            pass  # a leitura direta já é suficiente; a falha da IA vira apenas um aviso no orquestrador
    return f
