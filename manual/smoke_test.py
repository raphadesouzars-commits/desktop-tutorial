# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/desktop-tutorial/manual")
from helpers import *

doc = new_document()
add_cover(
    doc,
    "/home/user/desktop-tutorial/manual/assets/logo_coger.png",
    "Manual da Suíte COGER",
    "Veritas · Nexo Coger · Oitiva 360",
    ["Lei nº 8.112, de 11 de dezembro de 1990", "Versão de teste — smoke test", "Corregedoria da Receita Federal do Brasil"],
    alerta_lines=["Este é um documento de teste de componentes, não o manual final."],
)
add_sumario(doc)

page_break(doc)
add_chapter(doc, "Capítulo 1", "Título do Capítulo de Teste")
add_h2(doc, "Uma seção H2")
add_body(doc, "Parágrafo corrido com **negrito** e *itálico* misturados, para testar add_runs. " * 3)
add_h3(doc, "Um subtítulo H3")
add_bullet(doc, "Item de lista com em-dash como marcador.")
add_bullet(doc, "Segundo item de lista.")
add_numbered(doc, 1, "Primeiro passo numerado.")
add_numbered(doc, 2, "Segundo passo numerado, com **destaque**.")

add_alert(doc, ["Texto do aviso de atenção."], kind="warn", label="ATENÇÃO")
add_alert(doc, ["Resultado esperado do teste."], kind="green", label="RESULTADO ESPERADO")
add_alert(doc, ["Processo: 10768.204512/2026-31", "Unidade: Alfândega — Porto de Suape/PE"], kind="mono")
add_alert(doc, ["Erro grave de exemplo."], kind="danger")
add_alert(doc, ["Informação de contexto."], kind="info", label="fundamento")

add_separator(doc)

make_table(
    doc,
    headers=["Nó", "Pergunta", "Resposta esperada"],
    rows=[("moral-isolado", "Foi ato isolado?", "NÃO"), ("moral-cargo", "Uso do cargo?", "SIM")],
    col_widths=[3.5, 8.0, 4.5],
)

add_muted(doc, "Nota editorial de rodapé de teste.")

doc.save("/home/user/desktop-tutorial/manual/smoke_test.docx")
print("saved smoke_test.docx")
