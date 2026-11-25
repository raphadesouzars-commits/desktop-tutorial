"""Funções de texto compartilhadas (sem dependências externas)."""
from __future__ import annotations

import re
import unicodedata

STOP = set("""a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sob sobre ao aos à às e ou
que se como mais menos muito já não sim ser estar ter foi são era sua seu suas seus este esta isto esse essa isso
àquele pelo pela pelos pelas entre até também quando onde qual quais cujo cuja art inciso lei""".split())


def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", sem_acento(s or "").lower()).strip()


def tokens(s: str) -> list[str]:
    """Tokens minúsculos sem acento; remove stopwords e aplica um radical simples (plural)."""
    out = []
    for t in re.findall(r"[a-z0-9]+", norm(s)):
        if t in STOP or len(t) < 2:
            continue
        if len(t) > 4 and t.endswith("s"):
            t = t[:-1]
        out.append(t)
    return out


def titulo_nome(n: str) -> str:
    n = re.sub(r"\s+", " ", n or "").strip().lower()
    n = re.sub(r"(^|[\s'’-])([a-zà-ÿ])", lambda m: m.group(1) + m.group(2).upper(), n)
    return re.sub(r"\b(De|Da|Do|Das|Dos|E)\b", lambda m: m.group(1).lower(), n)


def anonimizar(texto: str, nome: str | None = None) -> str:
    """Mascara identificadores diretos antes de enviar o texto a uma IA (CPF, matrícula, telefone, e-mail, nome)."""
    t = texto
    t = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "[CPF]", t)
    t = re.sub(r"(?i)(matr[íi]cula(?:\s+siape)?\s*(?:n[ºo°.]*)?\s*[:\-–]?\s*)\d[\d.\-]{3,11}\d", r"\1[MATRÍCULA]", t)
    t = re.sub(r"\(?\b\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b", "[TELEFONE]", t)
    t = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[E-MAIL]", t)
    if nome and len(nome.strip()) > 4:
        t = re.sub(re.escape(nome.strip()), "[SERVIDOR]", t, flags=re.I)
        for parte in nome.split():
            if len(parte) > 5:  # sobrenomes/prenomes longos isolados
                t = re.sub(rf"\b{re.escape(parte)}\b", "[SERVIDOR]", t, flags=re.I)
    return t


def dividir_chunks(texto: str, tamanho: int = 1200, sobreposicao: int = 150) -> list[str]:
    """Quebra em blocos por parágrafo (~tamanho caracteres), com sobreposição entre blocos vizinhos."""
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\s*(?:Art\.|§|\d+[.)]\s))", texto) if p.strip()]
    out, atual = [], ""
    for p in paras:
        while len(p) > tamanho * 1.5:  # parágrafo gigante: corta em frase
            corte = p.rfind(". ", 0, tamanho)
            corte = corte if corte > tamanho // 2 else tamanho
            out.append((atual + " " + p[:corte + 1]).strip()); atual = ""
            p = p[corte + 1:].strip()
        if len(atual) + len(p) + 1 > tamanho and atual:
            out.append(atual)
            atual = (atual[-sobreposicao:] + " " + p) if sobreposicao else p
        else:
            atual = (atual + "\n" + p).strip()
    if atual.strip():
        out.append(atual.strip())
    return out
