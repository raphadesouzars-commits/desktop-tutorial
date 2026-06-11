from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ── Cores institucionais ──────────────────────────────────────────────────────
AZUL_ESCURO = RGBColor(0x00, 0x20, 0x5B)   # --p281
VERDE       = RGBColor(0x64, 0xA7, 0x0B)   # --p369
CINZA_CLARO = RGBColor(0xF2, 0xF2, 0xF2)
BRANCO      = RGBColor(0xFF, 0xFF, 0xFF)
CINZA_TEXTO = RGBColor(0x44, 0x44, 0x44)
AZUL_MEDIO  = RGBColor(0x1D, 0x3A, 0x78)
VERMELHO    = RGBColor(0xC0, 0x39, 0x2B)   # agravante
VERDE_ATEN  = RGBColor(0x27, 0xAE, 0x60)   # atenuante


def set_cell_bg(cell, rgb: RGBColor):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    hex_color = '{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def set_cell_borders(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        tag = OxmlElement(f'w:{side}')
        tag.set(qn('w:val'), kwargs.get(side, 'none'))
        if kwargs.get(side, 'none') != 'none':
            tag.set(qn('w:sz'), kwargs.get('sz', '4'))
            tag.set(qn('w:space'), '0')
            tag.set(qn('w:color'), kwargs.get('color', '000000'))
        tcBorders.append(tag)
    tcPr.append(tcBorders)


def add_bottom_border_to_cell(cell, color='64A70B', sz='8'):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single')
    bot.set(qn('w:sz'), sz)
    bot.set(qn('w:space'), '0')
    bot.set(qn('w:color'), color)
    tcBorders.append(bot)
    tcPr.append(tcBorders)


def no_space_before(para):
    pPr = para._p.get_or_add_pPr()
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), '0')
    spacing.set(qn('w:after'), '60')
    pPr.append(spacing)


doc = Document()

# ── Margens ───────────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.0)

# ── Estilos base ─────────────────────────────────────────────────────────────
style_normal = doc.styles['Normal']
style_normal.font.name = 'Arial'
style_normal.font.size = Pt(11)
style_normal.font.color.rgb = CINZA_TEXTO


# ── Helpers ───────────────────────────────────────────────────────────────────
def heading1(text):
    """Título de seção numerada — fundo azul escuro."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl.style = 'Table Grid'
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, AZUL_ESCURO)
    for side in ('top','left','bottom','right'):
        try:
            set_cell_borders(cell, **{side: 'none'})
        except Exception:
            pass
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(0)
    p.paragraph_format.left_indent  = Cm(0.3)
    run = p.add_run(text)
    run.font.name  = 'Arial'
    run.font.bold  = True
    run.font.size  = Pt(13)
    run.font.color.rgb = BRANCO
    doc.add_paragraph()  # espaço após
    return tbl


def heading2(text, cor=AZUL_MEDIO):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.font.name  = 'Arial'
    run.font.bold  = True
    run.font.size  = Pt(11.5)
    run.font.color.rgb = cor
    # linha inferior verde
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single')
    bot.set(qn('w:sz'), '6')
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), '64A70B')
    pBdr.append(bot)
    pPr.append(pBdr)
    return p


def heading3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(text)
    run.font.name  = 'Arial'
    run.font.bold  = True
    run.font.size  = Pt(11)
    run.font.color.rgb = AZUL_MEDIO
    return p


def body(text, bold_parts=None, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(4)
    if bold_parts:
        remaining = text
        for bp in bold_parts:
            before, _, remaining = remaining.partition(bp)
            if before:
                r = p.add_run(before)
                r.font.name = 'Arial'; r.font.size = Pt(11)
            r2 = p.add_run(bp)
            r2.font.name = 'Arial'; r2.font.size = Pt(11); r2.bold = True
        if remaining:
            r3 = p.add_run(remaining)
            r3.font.name = 'Arial'; r3.font.size = Pt(11)
    else:
        run = p.add_run(text)
        run.font.name  = 'Arial'
        run.font.size  = Pt(11)
        run.italic     = italic
    return p


def cite(text):
    """Bloco de citação legal recuado."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent  = Cm(1.5)
    p.paragraph_format.right_indent = Cm(1.0)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.font.name   = 'Arial'
    run.font.size   = Pt(10)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x66)
    return p


def bullet(text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent   = Cm(0.5 + level * 0.5)
    p.paragraph_format.space_before  = Pt(0)
    p.paragraph_format.space_after   = Pt(2)
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(11)
    return p


def nota(text):
    """Nota de atenção com fundo cinza claro."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = 'Table Grid'
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, CINZA_CLARO)
    add_bottom_border_to_cell(cell, color='64A70B', sz='6')
    p = cell.paragraphs[0]
    run = p.add_run('⚠  ' + text)
    run.font.name = 'Arial'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x44, 0x44, 0x00)
    doc.add_paragraph()


def tabela(headers, rows, cor_header=AZUL_ESCURO, cor_texto_header=BRANCO, col_widths=None):
    n = len(headers)
    tbl = doc.add_table(rows=1 + len(rows), cols=n)
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    # cabeçalho
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_bg(hdr_cells[i], cor_header)
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = hdr_cells[i].paragraphs[0].add_run(h)
        run.font.name = 'Arial'; run.font.bold = True
        run.font.size = Pt(10); run.font.color.rgb = cor_texto_header
    # linhas
    for ri, row in enumerate(rows):
        cells = tbl.rows[ri + 1].cells
        bg = CINZA_CLARO if ri % 2 == 0 else BRANCO
        for ci, val in enumerate(row):
            set_cell_bg(cells[ci], bg)
            cells[ci].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = cells[ci].paragraphs[0].add_run(str(val))
            run.font.name = 'Arial'; run.font.size = Pt(10)
    # larguras
    if col_widths:
        for ri2, row2 in enumerate(tbl.rows):
            for ci2, cell2 in enumerate(row2.cells):
                if ci2 < len(col_widths):
                    cell2.width = Cm(col_widths[ci2])
    doc.add_paragraph()
    return tbl


def badge(text, cor=AZUL_MEDIO):
    """Rótulo colorido simulando o badge de etapa."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(f'  {text}  ')
    run.font.name  = 'Arial'
    run.font.bold  = True
    run.font.size  = Pt(10)
    run.font.color.rgb = BRANCO
    run.font.highlight_color = None
    # Usar shading via XML
    rPr = run._r.get_or_add_rPr()
    shd = OxmlElement('w:shd')
    hex_color = '{:02X}{:02X}{:02X}'.format(cor.red, cor.green, cor.blue)
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    rPr.append(shd)
    return p


def page_break():
    doc.add_page_break()


# ══════════════════════════════════════════════════════════════════════════════
#  CAPA
# ══════════════════════════════════════════════════════════════════════════════
p_capa = doc.add_paragraph()
p_capa.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_capa.paragraph_format.space_before = Pt(60)
r = p_capa.add_run('CORREGEDORIA DA RECEITA FEDERAL DO BRASIL')
r.font.name = 'Arial'; r.font.bold = True; r.font.size = Pt(13)
r.font.color.rgb = AZUL_ESCURO

p_capa2 = doc.add_paragraph()
p_capa2.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_capa2.paragraph_format.space_before = Pt(40)
r2 = p_capa2.add_run('MANUAL TEÓRICO-PRÁTICO')
r2.font.name = 'Arial'; r2.font.bold = True; r2.font.size = Pt(22)
r2.font.color.rgb = AZUL_ESCURO

p_capa3 = doc.add_paragraph()
p_capa3.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = p_capa3.add_run('Calculadora de Multa PAR')
r3.font.name = 'Arial'; r3.font.bold = True; r3.font.size = Pt(18)
r3.font.color.rgb = VERDE

# linha decorativa
tbl_linha = doc.add_table(rows=1, cols=1)
tbl_linha.alignment = WD_TABLE_ALIGNMENT.CENTER
cell_linha = tbl_linha.rows[0].cells[0]
set_cell_bg(cell_linha, VERDE)
cell_linha.paragraphs[0].add_run(' ')
cell_linha.width = Cm(12)

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_before = Pt(30)
r_sub = p_sub.add_run('Processo Administrativo de Responsabilização — PAR\nLei nº 12.846/2013 | Decreto nº 11.129/2022')
r_sub.font.name = 'Arial'; r_sub.font.size = Pt(12)
r_sub.font.color.rgb = AZUL_MEDIO

p_sub2 = doc.add_paragraph()
p_sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub2.paragraph_format.space_before = Pt(60)
r_sub2 = p_sub2.add_run('Versão 2025')
r_sub2.font.name = 'Arial'; r_sub2.font.size = Pt(11)
r_sub2.font.color.rgb = CINZA_TEXTO

page_break()

# ══════════════════════════════════════════════════════════════════════════════
#  1. INTRODUÇÃO E FINALIDADE
# ══════════════════════════════════════════════════════════════════════════════
heading1('1. INTRODUÇÃO E FINALIDADE')
body('A Calculadora de Multa PAR é uma ferramenta de apoio à decisão desenvolvida pela Corregedoria da Receita Federal do Brasil para uso nos Processos Administrativos de Responsabilização (PAR) instaurados com base na Lei Anticorrupção (Lei nº 12.846/2013) e seu decreto regulamentador (Decreto nº 11.129/2022).')
body('A ferramenta tem como objetivos:')
bullet('Padronizar a dosimetria das sanções pecuniárias aplicadas às pessoas jurídicas;')
bullet('Transparência — cada percentual aplicado está vinculado a um dispositivo legal específico;')
bullet('Rastreabilidade — o relatório final gerado documenta todos os parâmetros utilizados, servindo como instrumento de instrução processual;')
bullet('Reduzir erros de cálculo, especialmente nas interações entre os limites mínimo, máximo, vantagem auferida e alíquota preliminar.')
body('A calculadora funciona integralmente offline (sem dependência de servidores externos), sendo adequada para uso em ambientes com restrições de conectividade.')

# ══════════════════════════════════════════════════════════════════════════════
#  2. FUNDAMENTO LEGAL
# ══════════════════════════════════════════════════════════════════════════════
heading1('2. FUNDAMENTO LEGAL')
heading2('2.1 Lei nº 12.846/2013 — Lei Anticorrupção (LAC)')
tabela(
    ['Dispositivo', 'Conteúdo'],
    [
        ['Art. 5º',      'Tipificação dos atos lesivos à administração pública'],
        ['Art. 6º, I',   'Multa de 0,1% a 20% do faturamento bruto da pessoa jurídica'],
        ['Art. 6º, II',  'Publicação extraordinária da decisão condenatória'],
    ],
    col_widths=[4, 12]
)
heading2('2.2 Decreto nº 11.129/2022')
tabela(
    ['Dispositivo', 'Conteúdo'],
    [
        ['Art. 20',  'Base de cálculo: faturamento bruto do último exercício anterior ao PAR'],
        ['Art. 21',  'Hipótese subsidiária: ausência de faturamento no exercício anterior'],
        ['Art. 22',  'Fatores agravantes (I a VI)'],
        ['Art. 23',  'Fatores atenuantes (I a V)'],
        ['Art. 24',  'Publicação extraordinária e critérios de prazo'],
        ['Art. 25',  'Limites mínimo e máximo da multa'],
        ['Art. 26',  'Métodos de apuração da vantagem auferida (I a III)'],
    ],
    col_widths=[4, 12]
)
heading2('2.3 Orientações complementares')
bullet('IN CGU nº 1/2015 — metodologia de avaliação do programa de integridade;')
bullet('Guia CGU de Responsabilização de Pessoas Jurídicas — parâmetros interpretativos e tabelas de referência;')
bullet('Tabela 5 do Guia CGU — escalonamento dos percentuais de ressarcimento (Art. 23, II).')

# ══════════════════════════════════════════════════════════════════════════════
#  3. ESTRUTURA GERAL
# ══════════════════════════════════════════════════════════════════════════════
heading1('3. ESTRUTURA GERAL DA CALCULADORA')
body('A calculadora é organizada em 14 etapas sequenciais (Steps 0 a 13), agrupadas em três blocos funcionais:')
tabela(
    ['Bloco', 'Etapas', 'Conteúdo'],
    [
        ['A — Base de Cálculo',   'Etapas 0 e 1',  'Faturamento Bruto e Vantagens Auferida/Pretendida'],
        ['B — Dosimetria',        'Etapas 2 a 12', 'Agravantes (Art. 22) e Atenuantes (Art. 23)'],
        ['C — Resultado',         'Etapa 13',      'Publicação Extraordinária e Resultado Final (Art. 25)'],
    ],
    col_widths=[5, 4, 8]
)

# ══════════════════════════════════════════════════════════════════════════════
#  4. ETAPA 0 — BASE DE CÁLCULO
# ══════════════════════════════════════════════════════════════════════════════
heading1('4. ETAPA 0 — BASE DE CÁLCULO: FATURAMENTO BRUTO')
heading2('4.1 Fundamento Legal')
cite('Art. 20 do Decreto nº 11.129/2022. A multa prevista no inciso I do caput do art. 6º da Lei nº 12.846/2013 terá como base de cálculo o faturamento bruto da pessoa jurídica no último exercício anterior ao da instauração do PAR, excluídos os tributos.')
cite('Art. 21. Caso a pessoa jurídica comprovadamente não tenha tido faturamento no último exercício anterior ao da instauração do PAR, deve-se considerar como base de cálculo da multa o valor do último faturamento bruto apurado pela pessoa jurídica, excluídos os tributos incidentes sobre vendas, que terá seu valor atualizado pelo IPCA até o último dia do exercício anterior ao da instauração do PAR.')
heading2('4.2 Fluxo de Decisão')
tabela(
    ['Situação', 'Regra Aplicável', 'Fundamento'],
    [
        ['PJ teve faturamento no exercício anterior ao PAR', 'Usar faturamento do exercício de referência (Ano PAR − 1)', 'Art. 20'],
        ['PJ não teve faturamento no exercício anterior',    'Usar o último faturamento bruto apurado, atualizado pelo IPCA', 'Art. 21'],
    ],
    col_widths=[6, 7, 4]
)
heading2('4.3 Modos de Apuração')
tabela(
    ['Modo', 'Descrição', 'Fundamento'],
    [
        ['DRE (Regime Geral)',         'Receita Bruta − Tributos sobre Vendas', 'Art. 20, caput'],
        ['Simples Nacional (ME/EPP)',  'Receita bruta total apurada nas declarações do Simples', 'LC nº 123/2006, art. 3º, §1º'],
        ['Estimativa pela autoridade','Hipótese residual — outros elementos quando não há dados contábeis', 'Art. 20, §1º, III'],
    ],
    col_widths=[5, 8, 4]
)
nota('Como a calculadora funciona offline, a atualização pelo IPCA (Art. 21) deve ser realizada previamente na Calculadora do Cidadão (BCB/IPCA), disponível no site do Banco Central do Brasil. Informe o valor já corrigido no campo correspondente.')

# ══════════════════════════════════════════════════════════════════════════════
#  5. ETAPA 1 — VANTAGENS AUFERIDA E PRETENDIDA
# ══════════════════════════════════════════════════════════════════════════════
heading1('5. ETAPA 1 — VANTAGENS AUFERIDA E PRETENDIDA (Art. 26)')
heading2('5.1 Distinção Legal')
tabela(
    ['Conceito', 'Definição', 'Função na Multa', 'Fundamento'],
    [
        ['Vantagem Auferida',   'Ganho real e efetivamente obtido com o ato lesivo',     'Piso mínimo inafastável da multa',                     'Art. 25, I'],
        ['Vantagem Pretendida', 'Ganho planejado/visado, ainda que não concretizado',    'Referência para o teto máximo (maior entre as duas)',   'Art. 25, II'],
    ],
    col_widths=[4.5, 6, 5.5, 3]
)
heading2('5.2 Métodos de Apuração da Vantagem Auferida')
heading3('Modo Direto')
body('Informar o valor já apurado externamente. Utilizar zero quando a vantagem não é estimável.')
heading3('Art. 26, I — Diferença entre receita auferida e custos lícitos')
body('Aplicável quando há receita auferida indevidamente (ex.: contratos obtidos por ato ilícito).')
cite('Vantagem = Receita Auferida − CMV/CSP − Despesas Lícitas − IRPJ/CSLL')
body('Suporta múltiplos exercícios com tratamento de prejuízos acumulados.')
heading3('Art. 26, II — Custos e despesas não suportados')
body('Valor correspondente aos custos e despesas que a PJ deixou de suportar. Exemplos: tributos não recolhidos, multas regulatórias evitadas, encargos não pagos.')
heading3('Art. 26, III — Acréscimo patrimonial por ação/omissão do Poder Público')
body('Acréscimo patrimonial que não teria ocorrido sem o ato lesivo. Exemplos: juros subsidiados obtidos indevidamente, uso de informação privilegiada.')
nota('Não confundir vantagem auferida com pretendida. Inflar o piso mínimo com a vantagem pretendida é erro metodológico. A calculadora trata cada valor na função legal correta.')

# ══════════════════════════════════════════════════════════════════════════════
#  6. AGRAVANTES
# ══════════════════════════════════════════════════════════════════════════════
heading1('6. AGRAVANTES — ART. 22, I A VI')
heading2('6.1 Art. 22, I — Concurso de Atos Lesivos', cor=VERMELHO)
body('Cruzamento entre quantidade de condutas ilícitas (linhas) e número de espécies distintas de atos lesivos do art. 5º da LAC (colunas). Aplica-se o percentual da célula correspondente ao caso concreto.')
tabela(
    ['Condutas ↓ / Espécies →', '1 espécie', '2 espécies', '3 espécies', '4 ou mais'],
    [
        ['1 conduta (ato isolado)', '—',    '0,5%', '1,0%', '1,5%'],
        ['2 condutas',             '0,5%', '1,0%', '1,5%', '2,0%'],
        ['3 condutas',             '1,0%', '1,5%', '2,0%', '2,5%'],
        ['4 condutas',             '1,5%', '2,0%', '2,5%', '3,0%'],
        ['5 condutas',             '2,0%', '2,5%', '3,0%', '3,5%'],
        ['6 condutas',             '2,5%', '3,0%', '3,5%', '4,0%'],
        ['7 ou mais',              '3,0%', '3,5%', '4,0%', '4,0%'],
    ],
    cor_header=VERMELHO,
    col_widths=[5.5, 3, 3, 3, 3]
)

heading2('6.2 Art. 22, II — Ciência/Tolerância Hierárquica', cor=VERMELHO)
body('O percentual varia conforme a posição hierárquica do agente com conhecimento ou tolerância, medida a partir do topo da estrutura.')
tabela(
    ['Nível hierárquico', '%'],
    [
        ['Ausência de conhecimento pelo corpo diretivo e gerencial',          '0%'],
        ['Tolerância/ciência do 5º nível abaixo dos administradores',         '1,0%'],
        ['Tolerância/ciência do 4º nível abaixo dos administradores',         '1,5%'],
        ['Tolerância/ciência do 3º nível abaixo dos administradores',         '2,0%'],
        ['Tolerância/ciência do 2º nível (imediatamente abaixo)',             '2,5%'],
        ['Tolerância/ciência dos sócios, acionistas ou administradores',      '3,0%'],
    ],
    cor_header=VERMELHO,
    col_widths=[13, 3]
)

heading2('6.3 Art. 22, III — Interrupção/Descumprimento (três hipóteses)', cor=VERMELHO)
body('Avalie cada uma das três hipóteses abaixo. Aplica-se automaticamente o maior percentual entre elas.')
heading3('a) Interrupção no Fornecimento de Serviço Público')
tabela(
    ['Situação', '%'],
    [
        ['Ausência de interrupção',                           '0%'],
        ['Até 1 semana ou vila/povoado',                      '1,0%'],
        ['Até 2 semanas ou cidade até 500 mil hab.',          '2,0%'],
        ['Até 3 semanas ou cidade +500 mil hab./Estado',      '3,0%'],
        ['Mais de 4 semanas ou 2 ou mais Estados',            '4,0%'],
    ],
    cor_header=VERMELHO,
    col_widths=[13, 3]
)
heading3('b) Interrupção na Execução de Obra Contratada')
tabela(
    ['Período ↓ / Residual →', '< 10%', 'Até 30%', 'Até 50%', 'Até 70%', '> 70%'],
    [
        ['Até 6 meses', '0,5%', '1,0%', '1,5%', '2,0%', '2,5%'],
        ['Até 1 ano',   '1,0%', '1,5%', '2,0%', '2,5%', '3,0%'],
        ['Até 2 anos',  '1,5%', '2,0%', '2,5%', '3,0%', '3,5%'],
        ['+ 2 anos',    '2,0%', '2,5%', '3,0%', '3,5%', '4,0%'],
    ],
    cor_header=VERMELHO,
    col_widths=[4.5, 2.5, 2.5, 2.5, 2.5, 2.5]
)
heading3('c) Descumprimento de Requisitos Regulatórios')
tabela(
    ['Situação', '%'],
    [
        ['Ausência de descumprimento',          '0%'],
        ['Parcial, com prestação do serviço',   '1,0%'],
        ['Total, com prestação do serviço',     '2,0%'],
        ['Parcial, sem prestação do serviço',   '3,0%'],
        ['Total, sem prestação do serviço',     '4,0%'],
    ],
    cor_header=VERMELHO,
    col_widths=[13, 3]
)

heading2('6.4 Art. 22, IV — Situação Econômica do Infrator', cor=VERMELHO)
body('Aplica-se 1% fixo quando a PJ apresenta, cumulativamente, os três indicadores:')
tabela(
    ['Indicador', 'Fórmula'],
    [
        ['Solvência geral > 1',  '(Ativo Circulante + Ativo Não Circulante) ÷ (Passivo Circulante + Passivo Não Circulante)'],
        ['Liquidez geral > 1',   '(Ativo Circulante + Ativo Realizável a LP) ÷ (Passivo Circulante + Passivo Não Circulante)'],
        ['Lucro líquido positivo', 'Último exercício anterior ao PAR'],
    ],
    col_widths=[5, 12]
)
tabela(['Situação', '%'],
    [['Algum indicador não atendido', '0%'], ['Todos os três atendidos cumulativamente', '1,0%']],
    cor_header=VERMELHO, col_widths=[13, 3])

heading2('6.5 Art. 22, V — Reincidência', cor=VERMELHO)
body('Ocorrência de nova infração tipificada como ato lesivo (art. 5º da LAC), idêntica ou não, em menos de cinco anos contados da publicação do julgamento anterior. No caso de acordo de leniência, o prazo conta da data da celebração até cinco anos após a declaração de cumprimento.')
tabela(['Situação', '%'],
    [['Não reincidente', '0%'], ['Sim — nova infração em menos de 5 anos', '3,0%']],
    cor_header=VERMELHO, col_widths=[13, 3])

heading2('6.6 Art. 22, VI — Valor dos Contratos com o Ente Lesado', cor=VERMELHO)
body('Somatório dos contratos, convênios, acordos e demais instrumentos mantidos ou pretendidos com o órgão/entidade lesado nos anos da prática do ato lesivo.')
tabela(['Somatório dos instrumentos', '%'],
    [
        ['Até R$ 500 mil',                          '0%'],
        ['Superior a R$ 500 mil até R$ 1,5 milhão', '1,0%'],
        ['Superior a R$ 1,5 milhão até R$ 10 milhões', '2,0%'],
        ['Superior a R$ 10 milhões até R$ 50 milhões', '3,0%'],
        ['Superior a R$ 50 milhões até R$ 250 milhões','4,0%'],
        ['Superior a R$ 250 milhões',               '5,0%'],
    ],
    cor_header=VERMELHO, col_widths=[13, 3])

# ══════════════════════════════════════════════════════════════════════════════
#  7. ATENUANTES
# ══════════════════════════════════════════════════════════════════════════════
heading1('7. ATENUANTES — ART. 23, I A V')
heading2('7.1 Art. 23, I — Não Consumação', cor=VERDE_ATEN)
body('Aplica-se quando o ato lesivo não chegou a produzir seus efeitos plenos (tentativa).')
tabela(['Situação', '%'],
    [['Ato lesivo consumado', '0%'], ['Ato lesivo não consumado (tentativa)', '−0,5%']],
    cor_header=VERDE_ATEN, col_widths=[13, 3])

heading2('7.2 Art. 23, II — Ressarcimento e Devolução Espontânea', cor=VERDE_ATEN)
body('Atenuante de até 1,0% pela devolução espontânea da vantagem auferida e/ou ressarcimento dos danos, conforme Tabela 5 do Guia CGU.')
tabela(['Situação', '%'],
    [
        ['Ausência de devolução e de ressarcimento', '0%'],
        ['Devolução da vantagem sem ressarcimento dos danos; ou ressarcimento sem devolução da vantagem', '−0,5%'],
        ['Devolução da vantagem e ressarcimento dos danos', '−1,0%'],
        ['Devolução e inexistência/falta de comprovação de danos; ou ressarcimento e ausência de estimativa da vantagem', '−1,0%'],
        ['Inexistência ou falta de comprovação de vantagem e de danos', '−1,0%'],
    ],
    cor_header=VERDE_ATEN, col_widths=[13, 3])
nota('O percentual máximo de 1,0% exige confirmação expressa de devolução integral. Devolução parcial reduz o percentual para 0,5%.')

heading2('7.3 Art. 23, III — Colaboração', cor=VERDE_ATEN)
body('Reconhecida ainda que não haja admissão de responsabilidade. Cada condição acrescenta 0,5%, com teto de 1,5% (condições cumuláveis):')
tabela(['Condição (cumulável)', '%'],
    [
        ['Ausência de colaboração',           '0%'],
        ['Admitiu a prática do ato',          '+0,5%'],
        ['Forneceu elementos para a apuração','+0,5%'],
        ['Renunciou aos prazos processuais',  '+0,5%'],
    ],
    cor_header=VERDE_ATEN, col_widths=[13, 3])

heading2('7.4 Art. 23, IV — Admissão Voluntária da Responsabilidade', cor=VERDE_ATEN)
body('Avaliada em dois eixos: conteúdo (parcial/total) × tempestividade (4 momentos processuais).')
tabela(['Condição', '%'],
    [
        ['Sem admissão',                         '0%'],
        ['Parcial — após alegações finais',       '−0,25%'],
        ['Total — após alegações finais',         '−0,5%'],
        ['Parcial — no prazo das alegações finais','−0,5%'],
        ['Total — no prazo das alegações finais', '−1,0%'],
        ['Parcial — no prazo de defesa',          '−1,0%'],
        ['Total — no prazo de defesa',            '−1,5%'],
        ['Parcial — antes da instauração do PAR', '−1,5%'],
        ['Total — antes da instauração do PAR',   '−2,0%'],
    ],
    cor_header=VERDE_ATEN, col_widths=[13, 3])

heading2('7.5 Art. 23, V — Programa de Integridade', cor=VERDE_ATEN)
body('Atenuante de até 5% pela comprovada existência e efetiva aplicação de programa de integridade. O percentual máximo somente é atribuível quando o programa for anterior à prática do ato lesivo (Art. 23, parágrafo único, III).')
cite('Fórmula: [COI × MPI] + APJ   —   teto: 5%')
body('Onde: COI = Cultura Organizacional e Instâncias de Governança; MPI = Mecanismos, Políticas e Procedimentos de Integridade; APJ = Atuação da Pessoa Jurídica em relação ao ato lesivo.')
tabela(['Situação', '%'],
    [['Sem programa ou não comprovado', '0%'], ['Programa apresentado e avaliado (bloco APJ-Anterior)', 'até −5,0%'], ['Programa instituído após o ato lesivo (bloco APJ-Posterior)', 'reduzido']],
    cor_header=VERDE_ATEN, col_widths=[13, 3])

# ══════════════════════════════════════════════════════════════════════════════
#  8. CÁLCULO FINAL E LIMITES LEGAIS
# ══════════════════════════════════════════════════════════════════════════════
heading1('8. CÁLCULO FINAL E LIMITES LEGAIS (Art. 25)')
heading2('8.1 Fórmula da Multa')
cite('Índice de Dosimetria  =  Σ Agravantes (Art. 22)  −  Σ Atenuantes (Art. 23)')
cite('Multa Bruta  =  Faturamento Bruto  ×  Índice de Dosimetria')
heading2('8.2 Verificação dos Limites')
tabela(
    ['Limite', 'Regra', 'Efeito', 'Fundamento'],
    [
        ['Piso — Vantagem Auferida',    'Multa não pode ser inferior à vantagem auferida',        'Se Multa Bruta < VA → Multa = VA', 'Art. 25, I'],
        ['Teto — Maior Vantagem',       'Multa não pode exceder o maior valor entre VA e VP',      'Se Multa Bruta > max(VA,VP) → Multa = max(VA,VP)', 'Art. 25, II'],
        ['Índice ≤ 0',                  'Resultado negativo ou zero na dosimetria',                'Multa = valor mínimo (vantagem auferida)', 'Art. 25, §2º'],
    ],
    col_widths=[4, 5.5, 5, 3]
)

# ══════════════════════════════════════════════════════════════════════════════
#  9. PUBLICAÇÃO EXTRAORDINÁRIA — SEÇÃO APROFUNDADA
# ══════════════════════════════════════════════════════════════════════════════
page_break()
heading1('9. PUBLICAÇÃO EXTRAORDINÁRIA DA DECISÃO CONDENATÓRIA')

heading2('9.1 Natureza Jurídica e Fundamento')
body(
    'A publicação extraordinária da decisão condenatória é uma sanção autônoma prevista no art. 6º, inciso II, '
    'da Lei nº 12.846/2013, aplicada conjuntamente com a multa pecuniária. Não se trata de mera divulgação '
    'de ato processual — constitui penalidade independente, com caráter pedagógico e dissuasório, voltada a '
    'expor publicamente a conduta ilícita da pessoa jurídica e sua responsabilização formal pelo Estado.'
)
cite(
    'Art. 6º, II, Lei nº 12.846/2013. A publicação extraordinária da decisão condenatória ocorrerá na forma '
    'de extrato de sentença, a expensas da pessoa jurídica, em meios de comunicação de grande circulação na '
    'área da prática da infração e de atuação da pessoa jurídica ou, na sua falta, em publicação de circulação '
    'nacional, bem como por meio de afixação de edital no próprio estabelecimento ou no local de exercício da '
    'atividade, de modo visível ao público, e no sítio eletrônico na rede mundial de computadores, respeitando '
    'o prazo determinado nesta dosimetria.'
)
cite(
    'Art. 24, Decreto nº 11.129/2022. A publicação extraordinária da decisão condenatória observará o '
    'prazo fixado a partir da Alíquota de Referência apurada na dosimetria.'
)

heading2('9.2 Modalidades e Meios de Veiculação')
body('A publicação extraordinária deve ser realizada, cumulativamente, nas seguintes formas:')
tabela(
    ['Modalidade', 'Descrição'],
    [
        ['Extrato de sentença em mídia',  'Meios de comunicação de grande circulação na área da prática da infração e de atuação da PJ. Na ausência, publicação de circulação nacional'],
        ['Edital no estabelecimento',     'Afixação em local visível ao público no próprio estabelecimento ou no local de exercício da atividade'],
        ['Sítio eletrônico',              'Publicação no site da PJ na rede mundial de computadores (internet)'],
    ],
    col_widths=[5.5, 11]
)
body('Todos os custos de publicação correm por conta da pessoa jurídica condenada ("a expensas da PJ"), não gerando ônus ao erário.')

heading2('9.3 A Alíquota de Referência')
body(
    'O prazo da publicação extraordinária é dosimetrado a partir de uma grandeza denominada Alíquota de Referência, '
    'que traduz em percentual do faturamento bruto o peso efetivo da sanção aplicada. '
    'Sua apuração segue dois cenários distintos, conforme o mecanismo que determinou o valor final da multa:'
)
heading3('Cenário A — Regra Geral')
body(
    'Aplica-se quando a multa final decorreu diretamente da aplicação da alíquota preliminar resultante da '
    'dosimetria dos arts. 22 e 23, sem interferência dos limites do art. 25 (piso, teto ou vantagem auferida). '
    'Nesse caso, a Alíquota de Referência é a própria alíquota preliminar da dosimetria.'
)
cite('Alíquota de Referência  =  Índice de Dosimetria  =  Σ Agravantes − Σ Atenuantes')

heading3('Cenário B — Regra de Exceção (Limites Legais)')
body(
    'Aplica-se quando o valor final da multa foi alterado pelos limites legais — seja porque a dosimetria resultou '
    'em índice negativo ou zero (art. 25, §2º), seja porque incidiu o piso da vantagem auferida (art. 25, I) ou '
    'o teto da maior vantagem (art. 25, II). Como a alíquota preliminar não corresponde ao valor efetivamente '
    'aplicado, ela é substituída pela alíquota recalculada:'
)
cite('Alíquota de Referência  =  (Valor Final da Multa  ÷  Faturamento Bruto)  ×  100')
nota(
    'O sistema identifica automaticamente o cenário aplicável (A ou B) a partir dos dados inseridos nas etapas '
    'anteriores. A identificação e o cálculo são transparentes e constam do relatório gerado.'
)

heading2('9.4 Tabela de Escalonamento do Prazo')
body(
    'A partir da Alíquota de Referência apurada, o prazo da publicação extraordinária é determinado pela '
    'seguinte tabela de escalonamento, conforme art. 24 do Decreto nº 11.129/2022:'
)
tabela(
    ['Alíquota de Referência', 'Prazo (dias corridos)', 'Prazo por extenso'],
    [
        ['Até 2,5%',                      '30',  'trinta dias'],
        ['Maior que 2,5% até 5,0%',       '45',  'quarenta e cinco dias'],
        ['Maior que 5,0% até 7,5%',       '60',  'sessenta dias'],
        ['Maior que 7,5% até 10,0%',      '75',  'setenta e cinco dias'],
        ['Maior que 10,0% até 12,5%',     '90',  'noventa dias'],
        ['Maior que 12,5% até 15,0%',    '105',  'cento e cinco dias'],
        ['Maior que 15,0% até 17,5%',    '120',  'cento e vinte dias'],
        ['Maior que 17,5%',              '135',  'cento e trinta e cinco dias'],
    ],
    col_widths=[6, 4.5, 6]
)
body('O prazo é contado em dias corridos a partir da publicação da decisão condenatória no órgão oficial correspondente.')

heading2('9.5 Casos Especiais na Apuração da Alíquota de Referência')
heading3('Faturamento igual a zero ou não estimável')
body(
    'Quando a base de cálculo (faturamento bruto) for igual a zero ou não puder ser estimada, o Cenário B '
    'não pode ser aplicado pela impossibilidade aritmética da divisão. Nessa hipótese, adota-se como Alíquota '
    'de Referência o índice da dosimetria preliminar:'
)
cite('Alíquota de Referência  =  max(Índice de Dosimetria, 0)  ×  100')

heading3('Índice de Dosimetria negativo ou zero (art. 25, §2º)')
body(
    'Quando a dosimetria resultar em índice negativo ou zero, a multa é fixada no piso mínimo (vantagem auferida). '
    'Nessa situação, o Cenário B se aplica necessariamente, pois o valor final da multa difere da aplicação '
    'direta da alíquota preliminar. A Alíquota de Referência passa a ser calculada como o quociente entre o '
    'valor da vantagem auferida e o faturamento bruto.'
)

heading3('Vantagem auferida superior à multa bruta (piso)')
body(
    'Quando a vantagem auferida supera a multa bruta calculada pela dosimetria, a multa é elevada ao valor '
    'da vantagem auferida (piso legal, art. 25, I). O Cenário B é aplicado, e a Alíquota de Referência '
    'é recalculada pelo valor efetivamente aplicado.'
)

heading3('Teto da maior vantagem (art. 25, II)')
body(
    'Quando a multa bruta excede o maior valor entre a vantagem auferida e a pretendida, ela é reduzida a '
    'esse teto. O Cenário B é aplicado, e a Alíquota de Referência reflete o valor do teto aplicado.'
)

heading2('9.6 Redação da Decisão — Elementos Obrigatórios')
body('A seção de publicação extraordinária na peça processual deve conter, no mínimo:')
tabela(
    ['Elemento', 'Conteúdo exigido'],
    [
        ['Fundamento legal',         'Art. 6º, II, da Lei nº 12.846/2013 c/c art. 24 do Decreto nº 11.129/2022'],
        ['Cenário adotado',          'A (regra geral) ou B (regra de exceção), com memória de cálculo'],
        ['Alíquota de Referência',   'Percentual apurado, com 2 casas decimais'],
        ['Prazo',                    'Número de dias corridos, por algarismo e por extenso'],
        ['Forma de veiculação',      'Meios de comunicação, edital no estabelecimento e sítio eletrônico'],
        ['Ônus financeiro',          'Expressão de que os custos correm a expensas da pessoa jurídica'],
    ],
    col_widths=[5, 12]
)

heading2('9.7 Geração Automática pela Calculadora')
body(
    'A Etapa 13 da calculadora processa automaticamente todos os dados inseridos nas etapas anteriores e '
    'determina: (i) o cenário aplicável (A ou B); (ii) a Alíquota de Referência; (iii) o prazo correspondente '
    'na tabela de escalonamento; e (iv) o texto dissertativo da memória de cálculo para integrar a minuta '
    'processual.'
)
body('O relatório final impresso registra:')
bullet('Cenário adotado (A ou B) com fundamentação;')
bullet('Memória de cálculo da Alíquota de Referência;')
bullet('Prazo determinado em dias corridos e por extenso;')
bullet('Texto padrão para a cláusula de publicação na decisão condenatória.')
nota(
    'A dosimetria da publicação extraordinária é consequência direta do valor final da multa. Qualquer '
    'alteração nos parâmetros de dosimetria (agravantes, atenuantes, limites) afetará automaticamente o '
    'prazo da publicação. Por isso, a Etapa 13 deve sempre ser revisada após qualquer modificação nas '
    'etapas anteriores.'
)

# ══════════════════════════════════════════════════════════════════════════════
#  10. RELATÓRIO FINAL
# ══════════════════════════════════════════════════════════════════════════════
heading1('10. RELATÓRIO FINAL E IMPRESSÃO')
heading2('10.1 Impressão do Relatório Final (PDF)')
body('O botão "Imprimir Relatório Final (PDF)" aciona o modo de impressão do navegador. O documento gerado tem fundo branco, identidade visual institucional, e reúne todos os parâmetros da dosimetria.')
body('Para gerar o PDF: pressione o botão → selecione "Salvar como PDF" na janela de impressão → ajuste a escala para 80–100% → salve com nome identificador do PAR.')
heading2('10.2 Botões Adicionais')
tabela(['Botão', 'Função'],
    [
        ['Imprimir Avaliação PI',       'Imprime somente a avaliação do programa de integridade (Etapa 12)'],
        ['Gerar Minuta de Relatório',   'Gera texto dissertativo para inserção direta na peça processual'],
        ['Recomeçar',                   'Reinicia o formulário (todos os campos são zerados)'],
    ],
    col_widths=[5.5, 11]
)

# ══════════════════════════════════════════════════════════════════════════════
#  11. FLUXO RESUMIDO
# ══════════════════════════════════════════════════════════════════════════════
heading1('11. FLUXO RESUMIDO DO CÁLCULO')
tabela(
    ['Etapa', 'Conteúdo', 'Faixa de %'],
    [
        ['0',  'Faturamento Bruto (base de cálculo)',                     'Base R$'],
        ['1',  'Vantagens Auferida e Pretendida',                         'Piso e Teto'],
        ['2',  'Agrav. I — Concurso de atos lesivos',                     '0% a 4,0%'],
        ['3',  'Agrav. II — Ciência/Tolerância hierárquica',              '0% a 3,0%'],
        ['4',  'Agrav. III — Interrupção/Descumprimento (maior das 3)',   '0% a 4,0%'],
        ['5',  'Agrav. IV — Situação econômica',                          '0% ou 1,0%'],
        ['6',  'Agrav. V — Reincidência',                                 '0% ou 3,0%'],
        ['7',  'Agrav. VI — Contratos com o ente lesado',                 '0% a 5,0%'],
        ['8',  'Aten. I — Não consumação',                                '0% ou −0,5%'],
        ['9',  'Aten. II — Ressarcimento/Devolução',                      '0% a −1,0%'],
        ['10', 'Aten. III — Colaboração',                                 '0% a −1,5%'],
        ['11', 'Aten. IV — Admissão voluntária',                          '0% a −2,0%'],
        ['12', 'Aten. V — Programa de integridade',                       '0% a −5,0%'],
        ['13', 'Publicação Extraordinária + Resultado Final',             'Prazo 30–135 dias'],
    ],
    col_widths=[1.5, 10, 5]
)

# ══════════════════════════════════════════════════════════════════════════════
#  12. FAQ
# ══════════════════════════════════════════════════════════════════════════════
heading1('12. PERGUNTAS FREQUENTES E PONTOS DE ATENÇÃO')

heading2('O sistema é validado por órgão oficial?')
body('A calculadora foi desenvolvida pela Corregedoria da RFB como ferramenta de apoio. Os parâmetros refletem o Decreto nº 11.129/2022, a IN CGU nº 1/2015 e o Guia CGU. O resultado é uma proposta fundamentada, sujeita à deliberação da autoridade competente.')

heading2('Como tratar a atualização pelo IPCA?')
body('A calculadora não realiza atualização automática pelo IPCA por funcionar offline. Quando necessário (Art. 21), corrija o valor previamente na Calculadora do Cidadão (BCB/IPCA) e informe o resultado corrigido no campo correspondente.')

heading2('O que acontece se o índice de dosimetria for negativo?')
body('Nos termos do Art. 25, §2º do Decreto nº 11.129/2022, a multa é fixada no valor mínimo (vantagem auferida). Se a vantagem auferida for zero ou não estimável, aplica-se o piso legal de R$ 6 mil nas hipóteses cabíveis.')

heading2('Qual a diferença entre vantagem auferida e pretendida na prática?')
body('Auferida: valor efetivamente recebido, economizado ou patrimonializado pela PJ. Pretendida: valor planejado que seria obtido se o ato ilícito fosse plenamente executado — inferido de proposta, contrato ou estimativa.')

heading2('O programa de integridade posterior ao ato lesivo pode atenuar?')
body('Sim, mas com percentual reduzido. O bloco APJ-Posterior avalia medidas corretivas adotadas após a descoberta. O percentual máximo de 5% é exclusivo de programas preexistentes ao ato lesivo.')

heading2('Quantos dias tem a publicação extraordinária nos casos mais graves?')
body('O prazo máximo é de 135 dias corridos, aplicável quando a Alíquota de Referência superar 17,5%. Para alíquotas até 2,5%, o prazo mínimo é de 30 dias.')

# ── Rodapé ────────────────────────────────────────────────────────────────────
doc.add_paragraph()
p_rodape = doc.add_paragraph()
p_rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_rod = p_rodape.add_run(
    'Manual elaborado com base na Calculadora de Multa PAR — Corregedoria da Receita Federal do Brasil\n'
    'Fundamentos: Lei nº 12.846/2013 | Decreto nº 11.129/2022 | IN CGU nº 1/2015 | Guia CGU'
)
r_rod.font.name = 'Arial'; r_rod.font.size = Pt(9)
r_rod.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
r_rod.font.italic = True

# ── Salvar ────────────────────────────────────────────────────────────────────
output_path = '/home/user/desktop-tutorial/Manual_Calculadora_PAR.docx'
doc.save(output_path)
print(f'Salvo em: {output_path}')
