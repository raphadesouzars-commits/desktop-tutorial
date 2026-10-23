#!/usr/bin/env python3
"""Fase C, item 4.4 — extensão do generateMinuta com as justificativas do
operador, opção A (in loco, mesmo com 0%), confirmada pelo usuário."""

SCRATCH = '/tmp/claude-0/-home-user-desktop-tutorial/3517a069-00ce-5e7e-8ba1-0624996120fa/scratchpad'
with open(f'{SCRATCH}/decoded.html', 'r', encoding='utf-8') as f:
    doc = f.read()

def rep(old, new, n=1, label=''):
    global doc
    c = doc.count(old)
    assert c == n, f'[{label}] esperado {n} ocorrência(s), achou {c}: {old[:90]!r}'
    doc = doc.replace(old, new, n)

# ── 1) função utilitária pushJust — inserida junto ao início de generateMinuta ──
rep(
    "    function generateMinuta() {\n        const fat = num('in-fat');",
    "    function justText(n) {\n"
    "        const el = document.getElementById('just-step' + n);\n"
    "        return el ? el.value.trim() : '';\n"
    "    }\n"
    "    function pushJust(linhas, n) {\n"
    "        const txt = justText(n);\n"
    "        if (!txt) return;\n"
    "        linhas.push('');\n"
    "        linhas.push(`Justificativa do operador (Etapa ${n} — ${STEP_LABELS[n]}): ${txt}.`);\n"
    "    }\n\n"
    "    function generateMinuta() {\n        const fat = num('in-fat');",
    label='pushJust helper')

# ── 2) Etapa 0 (Base de Cálculo) — após o parágrafo condicional, antes do blank+Seção II
rep(
    "        } else {\n            linhas.push(`A base de cálculo da multa corresponde ao faturamento bruto da pessoa jurídica no exercício imediatamente anterior ao da instauração do PAR (exercício ${parseInt(anoPAR) - 1}), excluídos os tributos incidentes sobre vendas, na forma do art. 20 do Decreto nº 11.129/2022, no valor de ${fmt(fat)}.`);\n        }\n        linhas.push('');\n        linhas.push('II — VANTAGEM AUFERIDA E PRETENDIDA (Art. 26)');",
    "        } else {\n            linhas.push(`A base de cálculo da multa corresponde ao faturamento bruto da pessoa jurídica no exercício imediatamente anterior ao da instauração do PAR (exercício ${parseInt(anoPAR) - 1}), excluídos os tributos incidentes sobre vendas, na forma do art. 20 do Decreto nº 11.129/2022, no valor de ${fmt(fat)}.`);\n        }\n        pushJust(linhas, 0);\n        linhas.push('');\n        linhas.push('II — VANTAGEM AUFERIDA E PRETENDIDA (Art. 26)');",
    label='pushJust etapa 0')

# ── 3) Etapa 1 (Vantagens) — após o bloco condicional da vantagem pretendida, antes do blank+Seção III
rep(
    "        if (vanPretendida > 0 && vanPretendida !== vanAuferida) {\n            linhas.push(`A vantagem pretendida, correspondente ao ganho planejado com o ilícito, foi estimada em ${fmt(vanPretendida)}. Por ser superior à vantagem auferida, será utilizada como referência para o cálculo do teto máximo da sanção, nos termos do art. 25, II, do Decreto nº 11.129/2022.`);\n        }\n        linhas.push('');\n        linhas.push('III — AGRAVANTES (Art. 22)');",
    "        if (vanPretendida > 0 && vanPretendida !== vanAuferida) {\n            linhas.push(`A vantagem pretendida, correspondente ao ganho planejado com o ilícito, foi estimada em ${fmt(vanPretendida)}. Por ser superior à vantagem auferida, será utilizada como referência para o cálculo do teto máximo da sanção, nos termos do art. 25, II, do Decreto nº 11.129/2022.`);\n        }\n        pushJust(linhas, 1);\n        linhas.push('');\n        linhas.push('III — AGRAVANTES (Art. 22)');",
    label='pushJust etapa 1')

# ── 4) Seção III — Agravantes: desacoplar bullets de pushJust; imprimir mesmo com pct=0 ──
OLD_III = """        if (totalAgrav === 0) {
            linhas.push('Não foram identificados fatores agravantes aplicáveis ao caso concreto.');
        } else {
            if (gConcurso > 0) linhas.push(`• Concurso de atos lesivos (art. 22, I): ${pct(gConcurso)}.`);
            if (gCiencia > 0) linhas.push(`• Ciência/tolerância hierárquica (art. 22, II): ${pct(gCiencia)}.`);
            if (gIII > 0) linhas.push(`• Interrupção/descumprimento — maior entre os subitens (art. 22, III): ${pct(gIII)}.`);
            if (gEcon > 0) linhas.push(`• Situação econômica do infrator (art. 22, IV): ${pct(gEcon)}.`);
            if (gReinc > 0) linhas.push(`• Reincidência (art. 22, V): ${pct(gReinc)}.`);
            if (gContr > 0) linhas.push(`• Valor dos contratos com o ente lesado (art. 22, VI): ${pct(gContr)}.`);
            linhas.push(`O somatório dos fatores agravantes totalizou ${pct(totalAgrav)}.`);
        }"""
NEW_III = """        if (totalAgrav === 0) {
            linhas.push('Não foram identificados fatores agravantes aplicáveis ao caso concreto.');
        }
        if (gConcurso > 0) linhas.push(`• Concurso de atos lesivos (art. 22, I): ${pct(gConcurso)}.`);
        pushJust(linhas, 2);
        if (gCiencia > 0) linhas.push(`• Ciência/tolerância hierárquica (art. 22, II): ${pct(gCiencia)}.`);
        pushJust(linhas, 3);
        if (gIII > 0) linhas.push(`• Interrupção/descumprimento — maior entre os subitens (art. 22, III): ${pct(gIII)}.`);
        pushJust(linhas, 4);
        if (gEcon > 0) linhas.push(`• Situação econômica do infrator (art. 22, IV): ${pct(gEcon)}.`);
        pushJust(linhas, 5);
        if (gReinc > 0) linhas.push(`• Reincidência (art. 22, V): ${pct(gReinc)}.`);
        pushJust(linhas, 6);
        if (gContr > 0) linhas.push(`• Valor dos contratos com o ente lesado (art. 22, VI): ${pct(gContr)}.`);
        pushJust(linhas, 7);
        if (totalAgrav > 0) linhas.push(`O somatório dos fatores agravantes totalizou ${pct(totalAgrav)}.`);"""
rep(OLD_III, NEW_III, label='Seção III restruturada')

# ── 5) Seção IV — Atenuantes: mesma lógica ──
OLD_IV = """        if (totalAten === 0) {
            linhas.push('Não foram identificados fatores atenuantes aplicáveis ao caso concreto.');
        } else {
            if (tConsum > 0) linhas.push(`• Não consumação da infração (art. 23, I): ${pct(tConsum)}.`);
            if (tRessar > 0) linhas.push(`• Ressarcimento/devolução espontânea (art. 23, II): ${pct(tRessar)}.`);
            if (tColab > 0) linhas.push(`• Colaboração durante a apuração (art. 23, III): ${pct(tColab)}.`);
            if (tAdmis > 0) linhas.push(`• Admissão voluntária da responsabilidade (art. 23, IV): ${pct(tAdmis)}.`);
            if (tPI > 0) linhas.push(`• Programa de integridade (art. 23, V): ${pct(tPI)}${piState.multiplied ? ' (resultado da planilha majorado pelo fator de 1,25, conforme Portaria Conjunta CGU nº 6/2022)' : ''}.`);
            linhas.push(`O somatório dos fatores atenuantes totalizou ${pct(totalAten)}.`);
        }"""
NEW_IV = """        if (totalAten === 0) {
            linhas.push('Não foram identificados fatores atenuantes aplicáveis ao caso concreto.');
        }
        if (tConsum > 0) linhas.push(`• Não consumação da infração (art. 23, I): ${pct(tConsum)}.`);
        pushJust(linhas, 8);
        if (tRessar > 0) linhas.push(`• Ressarcimento/devolução espontânea (art. 23, II): ${pct(tRessar)}.`);
        pushJust(linhas, 9);
        if (tColab > 0) linhas.push(`• Colaboração durante a apuração (art. 23, III): ${pct(tColab)}.`);
        pushJust(linhas, 10);
        if (tAdmis > 0) linhas.push(`• Admissão voluntária da responsabilidade (art. 23, IV): ${pct(tAdmis)}.`);
        pushJust(linhas, 11);
        if (tPI > 0) linhas.push(`• Programa de integridade (art. 23, V): ${pct(tPI)}${piState.multiplied ? ' (resultado da planilha majorado pelo fator de 1,25, conforme Portaria Conjunta CGU nº 6/2022)' : ''}.`);
        pushJust(linhas, 12);
        if (totalAten > 0) linhas.push(`O somatório dos fatores atenuantes totalizou ${pct(totalAten)}.`);"""
rep(OLD_IV, NEW_IV, label='Seção IV restruturada')

# ── 6) Etapa 13 (Publicação) — após NOTA_PUBLICACAO, ainda dentro do if(publicacaoResult) ──
rep(
    "            linhas.push('');\n            linhas.push(NOTA_PUBLICACAO);\n            linhas.push('');\n        }",
    "            linhas.push('');\n            linhas.push(NOTA_PUBLICACAO);\n            pushJust(linhas, 13);\n            linhas.push('');\n        }",
    label='pushJust etapa 13')

with open(f'{SCRATCH}/decoded.html', 'w', encoding='utf-8') as f:
    f.write(doc)
print('OK — item 4.4 (minuta) aplicado com a Opção A (in loco, mesmo com 0%).')
