#!/usr/bin/env python3
"""Cria templates/parecer.docx, termo.docx e despacho.docx. Os estilos "AICI ..." definem a aparência (Calibri 12, justificado);
a instituição pode abrir os .docx no Word e ajustar estilos, cabeçalho e rodapé - o gerador só preenche os marcadores {{...}}."""
import pathlib

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
T = RAIZ / "templates"


def estilos(doc):
    st = doc.styles
    n = st["Normal"]; n.font.name = "Calibri"; n.font.size = Pt(12)
    def novo(nome, alinh=WD_ALIGN_PARAGRAPH.JUSTIFY, esq=0.0, depois=12, neg=False, ital=False, tam=12):
        s = st.add_style(nome, WD_STYLE_TYPE.PARAGRAPH); s.base_style = n
        f = s.paragraph_format; f.alignment = alinh; f.left_indent = Cm(esq); f.space_after = Pt(depois); f.space_before = Pt(0)
        s.font.bold = neg; s.font.italic = ital; s.font.size = Pt(tam); s.font.name = "Calibri"
        return s
    novo("AICI Cabecalho", WD_ALIGN_PARAGRAPH.LEFT, depois=0, neg=True)
    novo("AICI Ementa", esq=8.5, depois=6)
    novo("AICI Titulo", WD_ALIGN_PARAGRAPH.LEFT, depois=12, neg=True)
    novo("AICI Titulo Centro", WD_ALIGN_PARAGRAPH.CENTER, depois=14, neg=True, tam=13)
    p = novo("AICI Paragrafo", depois=12); p.paragraph_format.tab_stops.add_tab_stop(Cm(1.9))
    novo("AICI Pergunta", esq=4.0, depois=2, neg=True, tam=11)
    novo("AICI Citacao", esq=2.8, depois=8, ital=True, tam=11)
    novo("AICI Item", esq=4.2, depois=8)
    novo("AICI Assinatura", WD_ALIGN_PARAGRAPH.CENTER, depois=0)
    novo("AICI Assinatura Italico", WD_ALIGN_PARAGRAPH.CENTER, depois=0, ital=True, tam=11)
    d = novo("AICI Despacho", esq=0, depois=10); d.paragraph_format.first_line_indent = Cm(1.9)


def base():
    d = Document(); estilos(d)
    sec = d.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.5); sec.top_margin = Cm(1.8); sec.bottom_margin = Cm(2.0)
    for p in list(d.paragraphs):
        p._element.getparent().remove(p._element)
    return d


def cabecalho_img(d):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run().add_picture(str(T / "cabecalho.jpg"), width=Cm(16.0))


def parecer():
    d = base(); cabecalho_img(d)
    for t in ("Parecer {{SIGLA}} nº {{NUMERO}}/{{ANO}}", "Data: {{DATA}}", "Processo nº {{PROCESSO}}", "{{ROTULO_SERVIDOR}}: {{SERVIDOR}}"):
        d.add_paragraph(t, style="AICI Cabecalho")
    d.add_paragraph("")
    d.add_paragraph("{{EMENTA}}", style="AICI Ementa")
    d.add_paragraph("")
    d.add_paragraph("{{CORPO}}", style="AICI Paragrafo")
    d.add_paragraph("{{ASSINATURAS}}", style="AICI Assinatura")
    d.save(T / "parecer.docx")


def termo():
    d = base(); cabecalho_img(d)
    d.add_paragraph("TERMO DE COMPROMISSO", style="AICI Titulo Centro")
    for t in ("Processo nº {{PROCESSO}}", "Referência: {{REFERENCIA}}"):
        d.add_paragraph(t, style="AICI Cabecalho")
    d.add_paragraph("")
    d.add_paragraph("{{CORPO}}", style="AICI Paragrafo")
    d.add_paragraph("{{ASSINATURAS}}", style="AICI Assinatura")
    d.save(T / "termo.docx")


def despacho():
    d = base(); cabecalho_img(d)
    d.add_paragraph("DESPACHO", style="AICI Titulo Centro")
    d.add_paragraph("Processo nº {{PROCESSO}}", style="AICI Cabecalho")
    d.add_paragraph("")
    d.add_paragraph("{{CORPO}}", style="AICI Despacho")
    d.add_paragraph("{{ASSINATURAS}}", style="AICI Assinatura")
    d.save(T / "despacho.docx")


if __name__ == "__main__":
    parecer(); termo(); despacho(); print("templates criados em", T)
