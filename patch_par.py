import re

with open('/home/user/desktop-tutorial/Multa_PAR.html', 'r', encoding='utf-8') as f:
    raw = f.read()

# ── 1. CSS para o campo de justificativa ─────────────────────────────────────
css_justif = """
        .justif-block {
            margin: 18px 0 10px 0;
            border-top: 1px dashed #c5cfe0;
            padding-top: 12px;
        }
        .justif-block label.justif-lbl {
            display: block;
            font-size: 9pt;
            font-weight: 600;
            color: #1D3A78;
            margin-bottom: 4px;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }
        .justif-block textarea {
            width: 100%;
            min-height: 66px;
            border: 1px solid #b0bec5;
            border-radius: 6px;
            padding: 8px 10px;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
            color: #333;
            resize: vertical;
            box-sizing: border-box;
            background: #f7f9ff;
            transition: border-color 0.2s;
        }
        .justif-block textarea:focus {
            border-color: #1D3A78;
            outline: none;
            background: #fff;
        }
        .justif-block .char-hint {
            font-size: 8pt;
            color: #aaa;
            text-align: right;
            margin-top: 2px;
        }"""

# The CSS lives inside a JS template string, so it's escaped.
# We insert before the closing </style> tag (which is escaped as /style)
css_target = '@media print { body { margin: 10px; } }\\n        <\\u002Fstyle>'

# Escape the CSS for insertion into the JS template string context
css_escaped = css_justif.replace('\\', '\\\\').replace("'", "\\'")
# Convert newlines to \n literal
css_escaped_inline = css_escaped.replace('\n', '\\n').replace('\r', '')

css_replacement = '@media print { body { margin: 10px; } }' + css_escaped_inline + '\\n        <\\u002Fstyle>'
assert css_target in raw, "CSS target not found!"
raw = raw.replace(css_target, css_replacement, 1)
print("OK: CSS inserted")

# ── 2. Justificativa HTML block ───────────────────────────────────────────────
step_labels = {
    0:  'Justificativa — Base de Cálculo (Faturamento)',
    1:  'Justificativa — Vantagens Auferida e Pretendida',
    2:  'Justificativa — Agravante: Concurso de Atos Lesivos (Art. 22, I)',
    3:  'Justificativa — Agravante: Ciência/Tolerância Hierárquica (Art. 22, II)',
    4:  'Justificativa — Agravante: Interrupção/Descumprimento (Art. 22, III)',
    5:  'Justificativa — Agravante: Situação Econômica (Art. 22, IV)',
    6:  'Justificativa — Agravante: Reincidência (Art. 22, V)',
    7:  'Justificativa — Agravante: Contratos com o Ente Lesado (Art. 22, VI)',
    8:  'Justificativa — Atenuante: Não Consumação (Art. 23, I)',
    9:  'Justificativa — Atenuante: Ressarcimento/Devolução (Art. 23, II)',
    10: 'Justificativa — Atenuante: Colaboração (Art. 23, III)',
    11: 'Justificativa — Atenuante: Admissão Voluntária (Art. 23, IV)',
    12: 'Justificativa — Atenuante: Programa de Integridade (Art. 23, V)',
    13: 'Justificativa — Publicação Extraordinária',
}

def justif_block(step_num):
    label = step_labels[step_num]
    s = str(step_num)
    return (
        '<div class=\\"justif-block\\">\\n'
        '                <label class=\\"justif-lbl\\" for=\\"justif-step' + s + '\\">' + label + '</label>\\n'
        '                <textarea id=\\"justif-step' + s + '\\" placeholder=\\"Registre aqui a fundamentação da escolha realizada nesta etapa (facultativo). O texto será incorporado à minuta do relatório.\\"></textarea>\\n'
        '                <div class=\\"char-hint\\">Campo facultativo — incorporado à minuta.</div>\\n'
        '            <\\u002Fdiv>\\n\\n            '
    )

nav_target = '<div class=\\"nav-buttons\\">'
all_nav_pos = [m.start() for m in re.finditer(re.escape(nav_target), raw)]
print(f"Found {len(all_nav_pos)} nav-buttons positions")
assert len(all_nav_pos) == 14, f"Expected 14, got {len(all_nav_pos)}"

# Insert from last to first to preserve offsets
for step_num in reversed(range(14)):
    pos = all_nav_pos[step_num]
    block = justif_block(step_num)
    raw = raw[:pos] + block + raw[pos:]

print("OK: Justificativa fields inserted in all 14 steps")

# ── 3. Rewrite generateMinuta ─────────────────────────────────────────────────
old_fn_start = 'function generateMinuta() {'
old_fn_end_marker = "document.getElementById('minuta-text').textContent = linhas.join('\\\\n');\\n    }\\n\\n    function copyMinuta"

old_fn_start_idx = raw.find(old_fn_start)
old_fn_end_idx   = raw.find(old_fn_end_marker, old_fn_start_idx)
assert old_fn_start_idx > 0, "generateMinuta not found"
assert old_fn_end_idx   > 0, "generateMinuta end not found"

# The new function — written as a raw string (no Python escaping issues)
# Internal JS quotes use \" because the whole thing is inside a JS template literal
# that uses escaped quotes \\" in the HTML source
new_fn = r"""function generateMinuta() {
        const fat = num('in-fat');
        const vanAuferida = num('in-van');
        const vanPretendida = parseFloat(document.getElementById('in-van-pretendida-stored').value) || 0;
        const vanParaTeto = Math.max(vanAuferida, vanPretendida);
        const anoPAR = document.getElementById('in-ano-par').value || '____';
        const usaArt21 = document.querySelector('input[name=\"fat-tem-fatur\"]:checked').value === 'nao';

        const gConcurso = num('g-concurso');
        const gCiencia  = parseFloat(document.querySelector('input[name=\"g-ciencia\"]:checked').value)  || 0;
        const gServ     = parseFloat(document.querySelector('input[name=\"g-serv\"]:checked').value)      || 0;
        const gObra     = num('g-obra');
        const gReg      = parseFloat(document.querySelector('input[name=\"g-reg\"]:checked').value)       || 0;
        const gIII      = Math.max(gServ, gObra, gReg);
        const gEcon     = parseFloat(document.querySelector('input[name=\"g-econ\"]:checked').value)      || 0;
        const gReinc    = parseFloat(document.querySelector('input[name=\"g-reinc\"]:checked').value)     || 0;
        const gContr    = parseFloat(document.querySelector('input[name=\"g-contr\"]:checked').value)     || 0;
        const totalAgrav = gConcurso + gCiencia + gIII + gEcon + gReinc + gContr;

        const tConsum = parseFloat(document.querySelector('input[name=\"t-consum\"]:checked').value) || 0;
        const tRessar = getRessarEffective();
        const tColab  = parseFloat(document.getElementById('t-colab').value)                         || 0;
        const tAdmis  = parseFloat(document.querySelector('input[name=\"t-admis\"]:checked').value)  || 0;
        const tPI     = parseFloat(document.getElementById('t-pi-value').value)                      || 0;
        const totalAten = tConsum + tRessar + tColab + tAdmis + tPI;
        const idx = totalAgrav - totalAten;
        const idxEhZeroOuNegativo = (idx <= 0) || (totalAgrav === 0 && totalAten === 0);

        const finalValFmt = document.getElementById('out-fine').textContent;

        // Lê o campo de justificativa de cada etapa
        function justif(step) {
            const el = document.getElementById('justif-step' + step);
            return el ? el.value.trim() : '';
        }

        // Labels das opções selecionadas
        const fatCenario = (() => {
            const el = document.querySelector('input[name=\"fat-cenario\"]:checked');
            if (!el) return '';
            const map = { dre: 'regime geral (DRE — Receita Bruta excluídos os tributos sobre vendas, art. 20, caput)', simples: 'Simples Nacional (ME ou EPP, conforme LC nº 123/2006, art. 3º, §1º)', 'sem-fins': 'entidade sem fins lucrativos (art. 20, §1º, IV)', hipotese: 'hipótese residual — faturamento estimado pela autoridade (art. 20, §1º, III)' };
            return map[el.value] || el.value;
        })();

        const cienciaLabel = (() => {
            const el = document.querySelector('input[name=\"g-ciencia\"]:checked');
            if (!el) return '';
            const map = { '0': 'ausência de conhecimento do ilícito pelo corpo diretivo e gerencial', '0.010': 'tolerância ou ciência do 5º nível hierárquico abaixo dos administradores', '0.015': 'tolerância ou ciência do 4º nível hierárquico abaixo dos administradores', '0.020': 'tolerância ou ciência do 3º nível hierárquico abaixo dos administradores', '0.025': 'tolerância ou ciência do 2º nível hierárquico (imediatamente abaixo dos administradores)', '0.030': 'tolerância ou ciência dos próprios sócios, acionistas ou administradores' };
            return map[el.value] || el.value;
        })();

        const ressarLabel = (() => {
            const el = document.querySelector('input[name=\"t-ressar\"]:checked');
            if (!el) return 'ausência de devolução espontânea';
            const map = { '0': 'ausência de devolução espontânea da vantagem auferida e do ressarcimento dos danos', '0.005': 'devolução parcial (vantagem sem ressarcimento de danos, ou ressarcimento sem devolução da vantagem)', '0.010': 'devolução espontânea da vantagem auferida e ressarcimento integral dos danos identificados', '0.010b': 'devolução integral da vantagem, sem danos identificados', '0.010c': 'inexistência ou falta de comprovação de vantagem e de danos' };
            return map[el.value] || el.value;
        })();

        const admisLabel = (() => {
            const el = document.querySelector('input[name=\"t-admis\"]:checked');
            if (!el) return 'ausência de admissão voluntária';
            const map = { '0': 'ausência de admissão voluntária da responsabilidade', '0.0025': 'admissão parcial após as alegações finais', '0.005': 'admissão total após as alegações finais, ou admissão parcial no prazo das alegações finais', '0.010': 'admissão total no prazo das alegações finais, ou admissão parcial no prazo de defesa', '0.015': 'admissão total no prazo de defesa, ou admissão parcial antes da instauração do PAR', '0.020': 'admissão total da responsabilidade antes da instauração do PAR' };
            return map[el.value] || el.value;
        })();

        const contrLabel = (() => {
            const el = document.querySelector('input[name=\"g-contr\"]:checked');
            if (!el) return 'somatório dos instrumentos celebrados com o ente lesado';
            const map = { '0': 'somatório dos instrumentos com o ente lesado de até R$ 500.000,00', '0.010': 'somatório dos instrumentos entre R$ 500.000,01 e R$ 1.500.000,00', '0.020': 'somatório dos instrumentos entre R$ 1.500.000,01 e R$ 10.000.000,00', '0.030': 'somatório dos instrumentos entre R$ 10.000.000,01 e R$ 50.000.000,00', '0.040': 'somatório dos instrumentos entre R$ 50.000.000,01 e R$ 250.000.000,00', '0.050': 'somatório dos instrumentos superior a R$ 250.000.000,00' };
            return map[el.value] || el.value;
        })();

        const consumLabel = tConsum > 0
            ? 'o ato lesivo não chegou a produzir seus efeitos plenos (tentativa)'
            : 'o ato lesivo foi consumado em sua integralidade';

        const reincLabel = gReinc > 0
            ? 'nova infração praticada em menos de cinco anos contados da publicação do julgamento da infração anterior'
            : 'inexistência de reincidência nos termos do art. 22, V, do Decreto nº 11.129/2022';

        const colabItens = [];
        if (document.getElementById('colab-admitiu')   && document.getElementById('colab-admitiu').checked)   colabItens.push('admissão da prática do ato');
        if (document.getElementById('colab-elementos') && document.getElementById('colab-elementos').checked) colabItens.push('fornecimento de elementos probatórios para a apuração');
        if (document.getElementById('colab-prazos')    && document.getElementById('colab-prazos').checked)    colabItens.push('renúncia aos prazos processuais');

        let linhas = [];

        // I — BASE DE CÁLCULO
        linhas.push('DO CÁLCULO DA MULTA');
        linhas.push('(Art. 6º, I, da Lei nº 12.846/2013 c/c arts. 20 e seguintes do Decreto nº 11.129/2022)');
        linhas.push('');
        linhas.push('I — DA BASE DE CÁLCULO');
        linhas.push('');
        if (usaArt21) {
            linhas.push('Conforme apurado nos autos, a pessoa jurídica investigada não apresentou faturamento no exercício imediatamente anterior ao da instauração do presente PAR (ano-base ' + (parseInt(anoPAR)-1) + '). Em razão dessa circunstância, aplica-se o disposto no art. 21 do Decreto nº 11.129/2022, que determina a adoção, como base de cálculo, do último faturamento bruto apurado pela pessoa jurídica, devidamente atualizado pelo Índice Nacional de Preços ao Consumidor Amplo (IPCA) até o último dia do exercício anterior à instauração do PAR. O valor assim apurado, excluídos os tributos incidentes sobre vendas, corresponde a ' + fmt(fat) + '.');
        } else {
            linhas.push('A base de cálculo da sanção pecuniária corresponde ao faturamento bruto da pessoa jurídica no exercício imediatamente anterior ao da instauração do presente PAR (exercício ' + (parseInt(anoPAR)-1) + '), excluídos os tributos incidentes sobre vendas, na forma do art. 20, caput, do Decreto nº 11.129/2022' + (fatCenario ? ', apurado pelo critério do ' + fatCenario : '') + '. O valor do faturamento bruto ajustado, adotado como base de cálculo, é de ' + fmt(fat) + '.');
        }
        const j0 = justif(0); if (j0) linhas.push('A escolha da metodologia de apuração do faturamento decorre do seguinte: ' + j0);
        linhas.push('');

        // II — VANTAGENS
        linhas.push('II — DAS VANTAGENS AUFERIDA E PRETENDIDA');
        linhas.push('(Art. 25 c/c Art. 26 do Decreto nº 11.129/2022)');
        linhas.push('');
        if (vanAuferida > 0) {
            linhas.push('A vantagem auferida, compreendida como o ganho real e efetivamente obtido pela pessoa jurídica em decorrência do ato lesivo praticado, foi quantificada em ' + fmt(vanAuferida) + (metodoLabel ? ', pela metodologia do ' + metodoLabel : '') + ', nos termos do art. 26 do Decreto nº 11.129/2022. Referido valor constitui o piso mínimo inafastável da sanção, nos termos do art. 25, I, do mesmo diploma, uma vez que a multa não poderá ser fixada em montante inferior ao benefício ilicitamente obtido.');
        } else {
            linhas.push('A vantagem auferida não foi estimável no caso concreto — seja pela impossibilidade de quantificação, seja pela ausência de ganho patrimonial verificável —, situação que, nos termos do art. 26 c/c art. 25, I, do Decreto nº 11.129/2022, não afasta a aplicação da multa, recaindo o piso mínimo sobre o percentual mínimo legal incidente sobre o faturamento bruto.');
        }
        if (vanPretendida > 0 && vanPretendida !== vanAuferida) {
            linhas.push('Ademais, a vantagem pretendida — correspondente ao ganho que a pessoa jurídica visava auferir com a prática do ilícito, independentemente de sua efetiva concretização — foi estimada em ' + fmt(vanPretendida) + '. Por superar a vantagem auferida, este valor será adotado como referência para o cálculo do teto máximo da sanção, conforme determinação expressa do art. 25, II, do Decreto nº 11.129/2022.');
        }
        const j1 = justif(1); if (j1) linhas.push('Acerca da metodologia de apuração das vantagens, registra-se: ' + j1);
        linhas.push('');

        // III — AGRAVANTES
        linhas.push('III — DOS FATORES AGRAVANTES');
        linhas.push('(Art. 22 do Decreto nº 11.129/2022)');
        linhas.push('');
        if (totalAgrav === 0) {
            linhas.push('Da análise do conjunto probatório dos autos, não foram identificados fatores agravantes aplicáveis ao caso concreto dentre aqueles elencados no art. 22 do Decreto nº 11.129/2022, razão pela qual nenhum acréscimo percentual incide sobre a base de cálculo a título de agravante.');
        } else {
            linhas.push('Da análise das circunstâncias do caso concreto, foram identificados os seguintes fatores agravantes, nos termos do art. 22 do Decreto nº 11.129/2022:');
            linhas.push('');
            const letras = ['a)','b)','c)','d)','e)','f)']; let li = 0;
            if (gConcurso > 0) { linhas.push(letras[li++] + ' Concurso de atos lesivos (art. 22, I): verificou-se a prática de múltiplos atos lesivos em concurso, resultando, pelo cruzamento entre a quantidade de condutas ilícitas e o número de espécies distintas de atos lesivos elencados no art. 5º da Lei nº 12.846/2013, na incidência do percentual agravante de ' + pct(gConcurso) + '.'); const j2 = justif(2); if (j2) linhas.push('   Fundamentação: ' + j2); }
            if (gCiencia > 0) { linhas.push(letras[li++] + ' Tolerância ou ciência do corpo diretivo/gerencial (art. 22, II): constatou-se ' + cienciaLabel + ', circunstância que, por refletir o grau de comprometimento dos níveis hierárquicos superiores com a conduta ilícita, determina a incidência do percentual agravante de ' + pct(gCiencia) + '.'); const j3 = justif(3); if (j3) linhas.push('   Fundamentação: ' + j3); }
            if (gIII > 0) { linhas.push(letras[li++] + ' Interrupção na prestação de serviços públicos, execução de obras ou descumprimento de requisitos regulatórios (art. 22, III): verificou-se hipótese enquadrada no referido dispositivo, prevalecendo o maior percentual entre as três alíneas avaliadas, correspondente a ' + pct(gIII) + '.'); const j4 = justif(4); if (j4) linhas.push('   Fundamentação: ' + j4); }
            if (gEcon > 0) { linhas.push(letras[li++] + ' Situação econômica do infrator (art. 22, IV): verificado que a pessoa jurídica apresenta, cumulativamente, índice de solvência geral superior a 1 (um), índice de liquidez geral superior a 1 (um) e lucro líquido positivo no exercício de referência, incide o percentual agravante fixo de ' + pct(gEcon) + ', conforme parâmetros do art. 22, IV, do Decreto nº 11.129/2022.'); const j5 = justif(5); if (j5) linhas.push('   Fundamentação: ' + j5); }
            if (gReinc > 0) { linhas.push(letras[li++] + ' Reincidência (art. 22, V): configurada a hipótese de reincidência, em razão de ' + reincLabel + ', o que determina a incidência do percentual agravante de ' + pct(gReinc) + '.'); const j6 = justif(6); if (j6) linhas.push('   Fundamentação: ' + j6); }
            if (gContr > 0) { linhas.push(letras[li++] + ' Valor dos contratos com o ente lesado (art. 22, VI): o ' + contrLabel + ', o que, na forma da tabela prevista no art. 22, VI, do Decreto nº 11.129/2022, determina a incidência do percentual agravante de ' + pct(gContr) + '.'); const j7 = justif(7); if (j7) linhas.push('   Fundamentação: ' + j7); }
            linhas.push('');
            linhas.push('O somatório dos fatores agravantes apurados totaliza ' + pct(totalAgrav) + '.');
        }
        linhas.push('');

        // IV — ATENUANTES
        linhas.push('IV — DOS FATORES ATENUANTES');
        linhas.push('(Art. 23 do Decreto nº 11.129/2022)');
        linhas.push('');
        if (totalAten === 0) {
            linhas.push('Da análise das circunstâncias do caso concreto, não foram identificados fatores atenuantes aplicáveis dentre os previstos no art. 23 do Decreto nº 11.129/2022, razão pela qual nenhum desconto percentual incide sobre a base de cálculo a esse título.');
        } else {
            linhas.push('Foram reconhecidos os seguintes fatores atenuantes, nos termos do art. 23 do Decreto nº 11.129/2022:');
            linhas.push('');
            const letrasAten = ['a)','b)','c)','d)','e)']; let la = 0;
            if (tConsum > 0) { linhas.push(letrasAten[la++] + ' Não consumação da infração (art. 23, I): ficou demonstrado que ' + consumLabel + ', circunstância que configura a hipótese do art. 23, I, do Decreto nº 11.129/2022, importando na atenuante de ' + pct(tConsum) + '.'); const j8 = justif(8); if (j8) linhas.push('   Fundamentação: ' + j8); }
            if (tRessar > 0) { linhas.push(letrasAten[la++] + ' Devolução espontânea da vantagem auferida e ressarcimento dos danos (art. 23, II): verificou-se ' + ressarLabel + ', situação que, nos termos do art. 23, II, do Decreto nº 11.129/2022 e da Tabela 5 do Guia CGU, determina a atenuante de ' + pct(tRessar) + '.'); const j9 = justif(9); if (j9) linhas.push('   Fundamentação: ' + j9); }
            if (tColab > 0) { const colabDesc = colabItens.length > 0 ? colabItens.join('; ') : 'formas de colaboração identificadas nos autos'; linhas.push(letrasAten[la++] + ' Colaboração durante a investigação e o PAR (art. 23, III): a pessoa jurídica colaborou com a apuração mediante: ' + colabDesc + '. Referidas condutas, reconhecidas independentemente de admissão de responsabilidade, totalizam a atenuante de ' + pct(tColab) + '.'); const j10 = justif(10); if (j10) linhas.push('   Fundamentação: ' + j10); }
            if (tAdmis > 0) { linhas.push(letrasAten[la++] + ' Admissão voluntária da responsabilidade (art. 23, IV): configurou-se hipótese de ' + admisLabel + ', o que, pela conjugação do conteúdo (parcial ou total) e da tempestividade da admissão, determina a atenuante de ' + pct(tAdmis) + '.'); const j11 = justif(11); if (j11) linhas.push('   Fundamentação: ' + j11); }
            if (tPI > 0) { linhas.push(letrasAten[la++] + ' Programa de integridade (art. 23, V): a pessoa jurídica apresentou programa de integridade, devidamente avaliado conforme a metodologia do Capítulo V do Decreto nº 11.129/2022 e da IN CGU nº 1/2015, por meio da aplicação da fórmula [COI × MPI] + APJ, cujo resultado, observado o teto de 5% (cinco por cento) previsto no art. 23, V, corresponde à atenuante de ' + pct(tPI) + '.'); const j12 = justif(12); if (j12) linhas.push('   Fundamentação: ' + j12); }
            linhas.push('');
            linhas.push('O somatório dos fatores atenuantes apurados totaliza ' + pct(totalAten) + '.');
        }
        linhas.push('');

        // V — DOSIMETRIA E LIMITES
        linhas.push('V — DA DOSIMETRIA E DOS LIMITES LEGAIS');
        linhas.push('(Art. 25 do Decreto nº 11.129/2022)');
        linhas.push('');
        if (idxEhZeroOuNegativo) {
            linhas.push('O resultado da dosimetria, correspondente à diferença entre o somatório das agravantes e das atenuantes (' + pct(idx) + '), é igual ou inferior a zero. Nos termos do § 2º do art. 25 do Decreto nº 11.129/2022, tal circunstância não afasta a aplicação da multa, mas determina a fixação da sanção no valor correspondente ao limite mínimo legalmente estabelecido, conforme apurado a seguir.');
        } else {
            linhas.push('O índice final da dosimetria, correspondente à diferença entre o somatório das agravantes (' + pct(totalAgrav) + ') e o somatório das atenuantes (' + pct(totalAten) + '), resulta em ' + pct(idx) + '. Aplicado esse índice sobre a base de cálculo de ' + fmt(fat) + ', apura-se a multa bruta de ' + fmt(fat * Math.max(idx,0)) + '.');
        }
        linhas.push('');
        const pisoCalc = usaArt21 ? Math.max(6000, vanAuferida) : Math.max(fat * 0.001, vanAuferida);
        const pisoDesc = usaArt21 ? 'R$ 6.000,00 (seis mil reais) ou o valor da vantagem auferida (art. 25, I, alínea "b")' : '0,1% (um décimo por cento) do faturamento bruto ou o valor da vantagem auferida (art. 25, I, alínea "a")';
        const tetoCalc = vanParaTeto > 0 ? Math.min(3 * vanParaTeto, usaArt21 ? 60000000 : fat * 0.20) : (usaArt21 ? 60000000 : fat * 0.20);
        linhas.push('O limite mínimo (piso) da sanção equivale ao maior entre ' + pisoDesc + ', fixando-se, no caso concreto, em ' + fmt(pisoCalc) + '.');
        linhas.push('');
        linhas.push('O limite máximo (teto) da sanção corresponde ao menor valor entre três vezes a maior vantagem apurada (' + fmt(vanParaTeto > 0 ? vanParaTeto : 0) + ' × 3 = ' + fmt(vanParaTeto * 3) + ') e ' + (usaArt21 ? 'R$ 60.000.000,00 (sessenta milhões de reais) ou 20% do faturamento alternativo' : '20% (vinte por cento) do faturamento bruto') + ', fixando-se, no caso concreto, em ' + fmt(tetoCalc) + '.');
        if (pisoCalc > tetoCalc) {
            linhas.push('');
            linhas.push('Registra-se que o limite mínimo apurado (' + fmt(pisoCalc) + ') supera o limite máximo (' + fmt(tetoCalc) + '). Nessa hipótese, aplica-se o § 1º do art. 25 do Decreto nº 11.129/2022, segundo o qual o teto máximo não é observado quando inferior ao resultado calculado para o piso mínimo.');
        }
        linhas.push('');

        // VI — VALOR FINAL
        linhas.push('VI — DO VALOR DA SANÇÃO PROPOSTA');
        linhas.push('');
        linhas.push('Diante de todo o exposto — base de cálculo apurada, vantagens quantificadas, fatores agravantes e atenuantes devidamente ponderados e limites legais verificados, nos termos do art. 25 do Decreto nº 11.129/2022 —, propõe-se a aplicação de multa no valor de ' + finalValFmt + ', a título de sanção pecuniária prevista no art. 6º, I, da Lei nº 12.846/2013.');
        linhas.push('');

        // VII — PUBLICAÇÃO EXTRAORDINÁRIA
        if (publicacaoResult) {
            const p = publicacaoResult;
            linhas.push('VII — DA PUBLICAÇÃO EXTRAORDINÁRIA DA DECISÃO CONDENATÓRIA');
            linhas.push('(Art. 6º, II, da Lei nº 12.846/2013 c/c Art. 24 do Decreto nº 11.129/2022)');
            linhas.push('');
            if (p.semBase) {
                linhas.push('Inexistindo base de faturamento apta a viabilizar o cálculo da Alíquota de Referência pela razão entre o valor final da multa e o faturamento bruto, adota-se, em caráter subsidiário, o índice da dosimetria preliminar como Alíquota de Referência, equivalente a ' + pctBR(p.aliquota) + '.');
            } else if (p.cenario === 'A') {
                linhas.push('Para fins de dosimetria do prazo da publicação extraordinária, constata-se que o valor final da multa (' + fmt(p.finalVal) + ') resultou da aplicação direta da alíquota preliminar apurada na dosimetria dos arts. 22 e 23 do Decreto nº 11.129/2022, sem que houvesse incidência dos limites mínimo ou máximo previstos no art. 25 do mesmo Decreto. Adota-se, assim, a regra geral (Cenário A): a Alíquota de Referência corresponde à própria alíquota preliminar da dosimetria, equivalente a ' + pctBR(p.aliquota) + '.');
            } else {
                linhas.push('Para fins de dosimetria do prazo da publicação extraordinária, verifica-se que o valor final da multa (' + fmt(p.finalVal) + ') não decorreu da aplicação direta da alíquota preliminar, tendo sido alterado pela incidência dos limites legais ou pela vantagem auferida, nos termos do art. 25 do Decreto nº 11.129/2022 (Cenário B — Regra de Exceção). A Alíquota de Referência foi, portanto, recalculada pela razão entre o valor final da multa e o faturamento bruto, na seguinte forma: (' + fmt(p.finalVal) + ' ÷ ' + fmt(p.fat) + ') × 100 = ' + pctBR(p.aliquota) + '.');
            }
            linhas.push('');
            linhas.push('Aplicada a tabela de escalonamento prevista no art. 24 do Decreto nº 11.129/2022, à Alíquota de Referência de ' + pctBR(p.aliquota) + ' corresponde o prazo de ' + p.prazo + ' (' + PRAZO_EXTENSO[p.prazo] + ') dias corridos para a publicação extraordinária da decisão condenatória.');
            linhas.push('');
            linhas.push(NOTA_PUBLICACAO);
            const j13 = justif(13); if (j13) { linhas.push(''); linhas.push('Considerações adicionais sobre a publicação extraordinária: ' + j13); }
            linhas.push('');
        }

        linhas.push('');
        linhas.push('[Local e data] ___________________________________________');
        linhas.push('[Assinatura — Comissão Processante do PAR nº ____/' + anoPAR + ']');

        document.getElementById('minuta-text').textContent = linhas.join('\n');
    }

    '"""

raw = raw[:old_fn_start_idx] + new_fn + "    function copyMinuta" + raw[old_fn_end_idx + len(old_fn_end_marker):]
print("OK: generateMinuta rewritten with legal language")

# ── 4. Save ───────────────────────────────────────────────────────────────────
with open('/home/user/desktop-tutorial/Multa_PAR.html', 'w', encoding='utf-8') as f:
    f.write(raw)
print(f"OK: File saved ({len(raw):,} bytes)")
