"""Módulo 11 - Geração DOCX a partir dos templates institucionais (templates/*.docx) com python-docx.
O Word resultante é editável: texto corrido em estilos "AICI ...", campos pendentes destacados em amarelo."""
from __future__ import annotations

import copy
import re
from datetime import date
from pathlib import Path

import docx
from docx.enum.text import WD_COLOR_INDEX

from ..models.schemas import Fatos, Minuta
from . import report_generator as R

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
PENDENTE = re.compile(r"(\[[A-ZÀ-Ý0-9ºª /.\-]{3,}\])")


def data_extenso(d: date | None = None) -> str:
    d = d or date.today()
    return f"{d.day}º de {MESES[d.month - 1]} de {d.year}" if d.day == 1 else f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def _runs(par, texto: str) -> None:
    """**negrito**, *itálico* e [CAMPO PENDENTE] em amarelo."""
    for parte in re.split(r"(\*\*.+?\*\*)", texto):
        neg = parte.startswith("**") and parte.endswith("**") and len(parte) > 4
        parte = parte[2:-2] if neg else parte
        for sub in re.split(r"(\*[^*\s][^*]*\*)", parte):
            ita = sub.startswith("*") and sub.endswith("*") and len(sub) > 2
            sub = sub[1:-1] if ita else sub
            for seg in PENDENTE.split(sub):
                if not seg:
                    continue
                r = par.add_run(seg)
                r.bold = neg or None
                r.italic = ita or None
                if PENDENTE.fullmatch(seg):
                    r.font.highlight_color = WD_COLOR_INDEX.YELLOW


def _inserir_antes(ref, texto: str, estilo: str):
    novo = copy.deepcopy(ref._element)
    for ch in list(novo):
        if ch.tag.endswith("}r"):
            novo.remove(ch)
    ref._element.addprevious(novo)
    from docx.text.paragraph import Paragraph
    p = Paragraph(novo, ref._parent)
    p.style = ref.part.document.styles[estilo]
    _runs(p, texto)
    return p


def _trocar(par, mapa: dict[str, str]):
    txt = "".join(r.text for r in par.runs)
    if "{{" not in txt:
        return
    for k, v in mapa.items():
        txt = txt.replace("{{" + k + "}}", v)
    for r in list(par.runs):
        r._element.getparent().remove(r._element)
    _runs(par, txt)


def _achar(doc, marcador: str):
    for p in doc.paragraphs:
        if marcador in p.text:
            return p
    return None


def _salvar(doc, saida: Path) -> Path:
    saida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(saida)
    return saida


def _assinaturas(doc, ref, assin: list[dict]):
    for s in assin:
        if s.get("despacho"):
            for ln in s["despacho"].split("\n"):
                _inserir_antes(ref, ln, "AICI Despacho")
        _inserir_antes(ref, "Assinado Digitalmente", "AICI Assinatura Italico")
        _inserir_antes(ref, s.get("nome") or "[NOME DO SIGNATÁRIO]", "AICI Assinatura")
        for k in ("cargo", "funcao"):
            if s.get(k):
                _inserir_antes(ref, s[k], "AICI Assinatura")
    ref._element.getparent().remove(ref._element)


ASSINATURAS_PADRAO = [
    {"despacho": "", "nome": "", "cargo": "Auditor-Fiscal da Receita Federal do Brasil", "funcao": "Membro do Grupo Nacional dos Pareceristas"},
    {"despacho": "De acordo. Encaminhe-se à autoridade competente para decisão.", "nome": "",
     "cargo": "Auditor-Fiscal da Receita Federal do Brasil", "funcao": "Coordenador do Grupo Nacional dos Pareceristas"},
]


def gerar_parecer(settings, fatos: Fatos, minuta: Minuta, ementa: list[str], saida: Path, numero: str = "", ano: str = "") -> Path:
    inst = R.institucional(settings)
    doc = docx.Document(str(settings.caminho("templates") / "parecer.docx"))
    s = fatos.servidor
    fem = bool(re.search(r"(?i)auditora|servidora", s.cargo))
    mapa = {"SIGLA": inst["sigla"], "NUMERO": numero or "[Nº]", "ANO": ano or str(date.today().year), "DATA": data_extenso(),
            "PROCESSO": s.processo or "[PROCESSO]", "ROTULO_SERVIDOR": "Servidora" if fem else "Servidor",
            "SERVIDOR": s.nome or "[NOME DO SERVIDOR]"}
    for p in doc.paragraphs:
        _trocar(p, mapa)
    ref = _achar(doc, "{{EMENTA}}")
    ass = _achar(doc, "{{ASSINATURAS}}")
    corpo = _achar(doc, "{{CORPO}}")
    tipo = s.tipo or "consulta"
    _inserir_antes(ref, "Assunto: " + ("Pedido de autorização para exercício de atividade privada formulado por meio do SeCI."
                                       if tipo == "pedido" else "Consulta SeCI."), "AICI Ementa")
    for e in ementa:
        if e.strip():
            _inserir_antes(ref, e, "AICI Ementa")
    ref._element.getparent().remove(ref._element)
    n = 0
    for sec in minuta.secoes:
        _inserir_antes(corpo, sec.titulo, "AICI Titulo")
        for p in sec.paragrafos:
            if p.tipo == "p":
                n += 1
                _inserir_antes(corpo, f"{n}.\t{p.texto}", "AICI Paragrafo")
            elif p.tipo == "it":
                _inserir_antes(corpo, p.texto, "AICI Item")
            else:  # citação / pergunta do formulário
                _inserir_antes(corpo, p.texto, "AICI Pergunta" if re.match(r"^\d{1,2} – ", p.texto) else "AICI Citacao")
    corpo._element.getparent().remove(corpo._element)
    _assinaturas(doc, ass, ASSINATURAS_PADRAO)
    return _salvar(doc, saida)


def gerar_termo(settings, fatos: Fatos, minuta: Minuta, atividade: str, saida: Path, numero: str = "", ano: str = "") -> Path:
    inst = R.institucional(settings)
    doc = docx.Document(str(settings.caminho("templates") / "termo.docx"))
    s = fatos.servidor
    ref = f"Parecer {inst['sigla']} nº {numero or '[Nº]'}/{ano or date.today().year}"
    fem = bool(re.search(r"(?i)auditora|servidora", s.cargo))
    ctx = {"nome": s.nome, "cargo": s.cargo, "matricula": s.matricula, "unidade": s.unidade, "atividade": atividade,
           "referencia": ref, "fem": fem, "demanda_ext_art": "o pedido de autorização" if s.tipo == "pedido" else "a consulta"}
    meu = lambda t: re.sub(r"\bseus\b", "meus", re.sub(r"\bsuas\b", "minhas", re.sub(r"\bseu\b", "meu", re.sub(r"\bsua\b", "minha", t))))
    for p in doc.paragraphs:
        _trocar(p, {"PROCESSO": s.processo or "[PROCESSO]", "REFERENCIA": ref})
    corpo, ass = _achar(doc, "{{CORPO}}"), _achar(doc, "{{ASSINATURAS}}")
    _inserir_antes(corpo, R.preencher(inst["termo"]["abertura"], ctx), "AICI Paragrafo")
    itens = [meu(t) for t in (minuta.ressalvas or inst["deveres"])] + [R.preencher(t, ctx) for t in inst["termo"]["itens_finais"]]
    for j, t in enumerate(itens):
        _inserir_antes(corpo, f"**{chr(97 + j)})** {t.rstrip('.;')}{'.' if j == len(itens) - 1 else ';'}", "AICI Item")
    _inserir_antes(corpo, inst["termo"]["ciencia"], "AICI Paragrafo")
    _inserir_antes(corpo, f"[CIDADE], {data_extenso()}.", "AICI Paragrafo")
    corpo._element.getparent().remove(corpo._element)
    for nome, l2, l3 in ((s.nome or "[NOME DO SERVIDOR]", s.cargo, f"Matrícula Siape nº {s.matricula}" if s.matricula else ""),
                         ("Chefia imediata", "(nome, cargo e matrícula)", ""), ("Comissão de Ética da RFB", "(nome e matrícula)", "")):
        _inserir_antes(ass, "_" * 47, "AICI Assinatura")
        for t in (nome, l2, l3):
            if t:
                _inserir_antes(ass, t, "AICI Assinatura")
        _inserir_antes(ass, "", "AICI Assinatura")
    ass._element.getparent().remove(ass._element)
    return _salvar(doc, saida)


def gerar_despacho(settings, fatos: Fatos, destino: str, saida: Path, numero: str = "", ano: str = "") -> Path:
    inst = R.institucional(settings)
    doc = docx.Document(str(settings.caminho("templates") / "despacho.docx"))
    s = fatos.servidor
    ref = f"Parecer {inst['sigla']} nº {numero or '[Nº]'}/{ano or date.today().year}"
    for p in doc.paragraphs:
        _trocar(p, {"PROCESSO": s.processo or "[PROCESSO]"})
    corpo, ass = _achar(doc, "{{CORPO}}"), _achar(doc, "{{ASSINATURAS}}")
    ctx = {"processo": s.processo or "[PROCESSO]", "nome": s.nome or "[NOME DO SERVIDOR]", "referencia": ref,
           "demanda_ext": "pedido de autorização" if s.tipo == "pedido" else "consulta", "destino": destino or "[DESTINO]"}
    _inserir_antes(corpo, R.preencher(inst["despacho"]["abertura"], ctx), "AICI Despacho")
    corpo._element.getparent().remove(corpo._element)
    _assinaturas(doc, ass, [{"nome": "", "cargo": "Auditor-Fiscal da Receita Federal do Brasil", "funcao": ""}])
    return _salvar(doc, saida)
