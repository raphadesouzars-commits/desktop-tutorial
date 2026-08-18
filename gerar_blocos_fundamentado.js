
    // ─── Fase D: Relatório Fundamentado — função geradora única ───
    function justWrap(n, lead) {
        const txt = justText(n);
        if (!txt) return '';
        return (lead ? lead + ' ' : '') + txt;
    }

    function gerarBlocosFundamentado() {
        const idProcesso = (document.getElementById('id-processo').value || '').trim();
        const idRazao = (document.getElementById('id-razao-social').value || '').trim();
        const idCnpj = (document.getElementById('id-cnpj').value || '').trim();
        const idComissaoRaw = (document.getElementById('id-comissao').value || '').trim();
        const dataEmissao = new Date().toLocaleDateString('pt-BR');

        const cabecalho = [];
        cabecalho.push('RELATÓRIO DE DOSIMETRIA DA MULTA E DA PUBLICAÇÃO EXTRAORDINÁRIA');
        if (idProcesso) cabecalho.push('Processo Administrativo de Responsabilização nº ' + idProcesso);
        if (idRazao || idCnpj) cabecalho.push('Pessoa jurídica processada: ' + (idRazao || '—') + (idCnpj ? ' — CNPJ ' + idCnpj : ''));
        if (idComissaoRaw) cabecalho.push('Comissão de responsabilização: ' + idComissaoRaw.split('\n').filter(l => l.trim()).join('; '));
        cabecalho.push('Data de emissão: ' + dataEmissao);

        const fat = num('in-fat');
        const vanAuferida = num('in-van');
        const vanPretendida = parseFloat(document.getElementById('in-van-pretendida-stored').value) || 0;
        const anoPARraw = document.getElementById('in-ano-par').value;
        const anoPAR = anoPARraw || '____';
        const anoBase = anoPARraw ? (parseInt(anoPARraw) - 1) : '____';
        const usaArt21 = document.querySelector('input[name="fat-tem-fatur"]:checked').value === 'nao';

        const gConcurso = num('g-concurso');
        const gCiencia = parseFloat(document.querySelector('input[name="g-ciencia"]:checked').value) || 0;
        const gServ = parseFloat(document.querySelector('input[name="g-serv"]:checked').value) || 0;
        const gObra = num('g-obra');
        const gReg = parseFloat(document.querySelector('input[name="g-reg"]:checked').value) || 0;
        const gIII = Math.max(gServ, gObra, gReg);
        const gEcon = parseFloat(document.querySelector('input[name="g-econ"]:checked').value) || 0;
        const gReinc = parseFloat(document.querySelector('input[name="g-reinc"]:checked').value) || 0;
        const gContr = parseFloat(document.querySelector('input[name="g-contr"]:checked').value) || 0;

        const tConsum = parseFloat(document.querySelector('input[name="t-consum"]:checked').value) || 0;
        const tRessar = getRessarEffective();
        const tColab = parseFloat(document.getElementById('t-colab').value) || 0;
        const tAdmis = parseFloat(document.querySelector('input[name="t-admis"]:checked').value) || 0;
        const tPI = parseFloat(document.getElementById('t-pi-value').value) || 0;

        const finalValFmt = document.getElementById('out-fine').textContent;

        const itens = [];

        const abertura = 'DA DOSIMETRIA DA MULTA (arts. 6º, I, da Lei nº 12.846/2013 e 20 a 26 do Decreto nº 11.129/2022)\n\nA multa prevista no art. 6º, I, da Lei nº 12.846/2013 constitui a sanção pecuniária central do regime de responsabilização administrativa de pessoas jurídicas por atos lesivos à administração pública, e sua quantificação não é ato discricionário livre: o Decreto nº 11.129/2022 instituiu metodologia tarifada, de aplicação vinculada, em que sobre a base de cálculo (faturamento bruto) incide índice resultante da soma dos fatores agravantes (art. 22) subtraída da soma dos fatores atenuantes (art. 23), com verificação final dos limites mínimo e máximo do art. 25. Essa arquitetura normativa concretiza, no plano regulamentar, os vetores de proporcionalidade e de individualização da sanção exigidos pelo art. 6º, § 1º, da Lei nº 12.846/2013, pelo art. 2º da Lei nº 9.784/1999 e pelos arts. 20 e 22 do Decreto-Lei nº 4.657/1942 (LINDB), que impõem ao aplicador a consideração das consequências práticas da decisão e das circunstâncias reais que envolveram a conduta. Disso decorre consequência metodológica relevante: a proporcionalidade não é aferida por juízo subjetivo sobre o resultado final, mas assegurada pela correta aplicação, individualmente motivada, de cada parâmetro do sistema — razão pela qual este relatório examina, um a um, todos os fatores de dosimetria, com registro expresso inclusive das hipóteses de não incidência, na forma do art. 50 da Lei nº 9.784/1999.';

        // ── ITEM 1 — BASE DE CÁLCULO ──
        let item1;
        if (usaArt21) {
            item1 = `**1. Da base de cálculo (art. 21 do Decreto nº 11.129/2022 — hipótese subsidiária).** Não tendo a pessoa jurídica apresentado faturamento no exercício anterior ao da instauração do PAR (${anoPAR}), incide a regra subsidiária do art. 21 do Decreto nº 11.129/2022, que determina a adoção do último faturamento bruto apurado, atualizado monetariamente pelo IPCA até o último dia do exercício anterior ao da instauração. A previsão subsidiária cumpre dupla função no sistema: impede que a interrupção das atividades — por vezes deliberadamente provocada, mediante esvaziamento patrimonial ou hibernação societária — esvazie a eficácia da sanção pecuniária, e garante que sempre exista base de cálculo aritmética apta a suportar a dosimetria, evitando o impasse da multa incalculável. A atualização pelo IPCA, por sua vez, preserva o valor real da base, neutralizando o benefício que o decurso do tempo traria ao infrator inativo. No caso, adota-se a base de ${fmt(fat)}, já atualizada na forma regulamentar.`;
        } else {
            item1 = `**1. Da base de cálculo (art. 20 do Decreto nº 11.129/2022).** A base de cálculo da multa corresponde ao faturamento bruto da pessoa jurídica no último exercício anterior ao da instauração do processo administrativo de responsabilização, excluídos os tributos incidentes sobre vendas. A eleição do faturamento bruto — e não do lucro, do patrimônio líquido ou do valor do contrato atingido — é opção deliberada do legislador e do regulamento: por refletir a dimensão econômica global da atividade empresarial, o faturamento assegura que a sanção seja sentida na proporção da capacidade econômica real do infrator, preservando a eficácia dissuasória da pena tanto para a pequena empresa quanto para o grande conglomerado. O marco temporal — exercício anterior ao da *instauração*, e não ao da prática do ato — é igualmente relevante: fixa critério objetivo, insuscetível de manipulação pela defesa e de fácil verificação documental, ainda que possa distanciar-se do porte da empresa à época dos fatos, distorção que o sistema tolera em nome da segurança jurídica. No caso, instaurado o PAR no exercício de ${anoPAR}, adota-se o faturamento bruto do exercício de ${anoBase}, apurado em ${fmt(fat)}, conforme documentação constante dos autos.`;
        }
        const just0 = justWrap(0, 'No caso concreto, a comissão consigna ainda:');
        itens.push([item1, just0].filter(Boolean).join('\n\n'));

        // ── ITEM 2 — VANTAGEM AUFERIDA E PRETENDIDA ──
        let item2;
        if (vanAuferida > 0) {
            let temPretendida = '';
            if (vanPretendida > 0 && vanPretendida !== vanAuferida) {
                temPretendida = ` A vantagem pretendida — o ganho projetado com o ilícito, ainda que não integralmente concretizado — foi estimada em ${fmt(vanPretendida)} e, por superar a auferida, servirá de referência ao teto do art. 25, II: o sistema toma por medida a ambição do infrator, e não apenas o seu êxito.`;
            }
            item2 = `**2. Da vantagem auferida e pretendida (art. 26 do Decreto nº 11.129/2022).** A vantagem auferida corresponde ao ganho real e efetivamente obtido pela pessoa jurídica com a prática do ato lesivo — conceito que não se confunde com o valor do contrato, com o dano ao erário nem com o lucro contábil do exercício, e cuja quantificação obedece a um dos métodos alternativos do art. 26 do Decreto nº 11.129/2022. Sua apuração cumpre função estrutural na dosimetria: é simultaneamente piso (a multa não pode ser inferior à vantagem auferida, art. 25, I) e componente do teto (art. 25, II), funcionando como a âncora econômica que impede tanto a sanção simbólica — que converteria o ilícito em negócio racional — quanto a sanção confiscatória. Por essa dupla função, a quantificação da vantagem é ônus probatório da administração e um dos pontos mais visados pela impugnação defensiva: a escolha do método, as premissas adotadas e as fontes documentais devem estar minuciosamente registradas nos autos, pois vício nessa quantificação contamina simultaneamente o piso e o teto da sanção. No caso, a vantagem auferida foi quantificada em ${fmt(vanAuferida)}, pela metodologia ${metodoLabel || 'não especificada'}.${temPretendida}`;
            itens.push([item2, justWrap(1, 'A quantificação apoia-se nos seguintes fundamentos:')].filter(Boolean).join('\n\n'));
        } else {
            item2 = `**2. Da vantagem auferida (art. 26 do Decreto nº 11.129/2022).** Não foi possível estimar a vantagem auferida com a prática do ato lesivo, circunstância que a comissão registra expressamente, com indicação das diligências realizadas e das razões da inestimabilidade. O registro não é formalidade: a inestimabilidade da vantagem repercute diretamente na verificação dos limites do art. 25 — altera a composição do piso e do teto aplicáveis — e a ausência de motivação nesse ponto é vulnerabilidade recorrente em sede de controle. A impossibilidade de quantificação, contudo, não paralisa a dosimetria nem beneficia o infrator com a supressão da sanção: o sistema prossegue com os parâmetros remanescentes, conforme adiante exposto.`;
            itens.push([item2, justWrap(1, 'As razões da inestimabilidade são as seguintes:')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 3 — CONCURSO DE ATOS LESIVOS ──
        let item3;
        if (gConcurso > 0) {
            const ce = concursoCondutasEspecies();
            item3 = `**3. Do concurso de atos lesivos (art. 22, I, do Decreto nº 11.129/2022).** O primeiro fator de agravamento gradua a sanção conforme a pluralidade da atividade ilícita, segundo critério bidimensional: contam-se, de um lado, as *condutas* — cada ato concreto e individualizado, ainda que da mesma espécie, de modo que três pagamentos indevidos, a destinatários ou em ocasiões distintas, são três condutas — e, de outro, as *espécies* — cada inciso do art. 5º da Lei nº 12.846/2013 efetivamente violado. O fundamento da agravante é a maior reprovabilidade de quem reitera ou diversifica a prática lesiva: a pluralidade revela não um desvio episódico, mas um padrão de atuação, e o direito sancionador responde a padrões com maior rigor do que a episódios. Registre-se que o Decreto nº 11.129/2022 abandonou deliberadamente a figura do "ato lesivo continuado" do regime anterior (Decreto nº 8.420/2015, que previa percentual máximo inferior), adotando contagem atomística de cada ato e elevando o teto do fator — opção regulatória que afasta, no plano administrativo, a unificação benéfica inspirada na continuidade delitiva do art. 71 do Código Penal, cuja importação por analogia parte da doutrina sustenta, mas que não encontra amparo no texto regulamentar vigente. Por isso mesmo, a identificação de cada conduta e de cada espécie deve estar individualizadamente demonstrada nos autos, sob pena de comprometer a legitimidade do percentual aplicado. No caso, identificaram-se ${ce.condutas} conduta(s) em ${ce.especies} espécie(s) distinta(s) do art. 5º, o que corresponde, na tabela regulamentar, ao percentual de ${pct(gConcurso)}.`;
            itens.push([item3, justWrap(2, 'A identificação das condutas e espécies funda-se nos seguintes elementos:')].filter(Boolean).join('\n\n'));
        } else {
            item3 = `**3. Do concurso de atos lesivos (art. 22, I, do Decreto nº 11.129/2022).** Tratando-se de conduta única, enquadrada em uma única espécie do art. 5º da Lei nº 12.846/2013, não incide o fator de agravamento do art. 22, I (0%). A unicidade da conduta, devidamente delimitada nos autos, afasta o juízo de maior reprovabilidade que fundamenta a agravante, reservada às hipóteses de reiteração ou diversificação da prática lesiva.`;
            itens.push([item3, justWrap(2, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 4 — CIÊNCIA/TOLERÂNCIA HIERÁRQUICA ──
        let item4;
        if (gCiencia > 0) {
            const nivel = radioLabelTexto('g-ciencia');
            item4 = `**4. Da tolerância ou ciência do corpo diretivo ou gerencial (art. 22, II, do Decreto nº 11.129/2022).** Este fator gradua a sanção conforme a posição hierárquica do agente que teve ciência do ato lesivo ou o tolerou, medida a partir do topo da estrutura societária. Seu fundamento é dos mais expressivos do sistema: embora a responsabilidade da pessoa jurídica seja objetiva (art. 2º da Lei nº 12.846/2013) — dispensando prova de dolo ou culpa para a configuração do ilícito —, o regulamento reintroduz, na fase de dosimetria, um juízo de reprovabilidade institucional: quanto mais próximo dos centros de decisão o conhecimento do ilícito, mais a infração deixa de ser desvio individual de um preposto para se tornar expressão da própria cultura organizacional, e maior a falha — ou a conivência — dos órgãos societários incumbidos de prevenir e reprimir a conduta. Para a incidência basta a ciência seguida de inércia; a norma equipara tolerância a aquiescência, dispensando prova de autorização expressa ou de proveito pessoal do dirigente. Dois cuidados metodológicos são indispensáveis: a hierarquia relevante é a vigente à época dos fatos, reconstruída por documentação contemporânea (atas societárias, contratos sociais, registros funcionais) e não pelo organograma atual; e a ciência não se presume do porte da empresa nem da gravidade do ato — exige prova concreta, tipicamente correspondências eletrônicas, aprovações formais, atas de reunião ou relatórios internos que circularam sem providência. No caso, restou demonstrada a ciência/tolerância no seguinte nível: ${nivel}, correspondente ao percentual de ${pct(gCiencia)}.`;
            itens.push([item4, justWrap(3, 'A prova da ciência hierárquica consiste em:')].filter(Boolean).join('\n\n'));
        } else {
            item4 = `**4. Da tolerância ou ciência do corpo diretivo ou gerencial (art. 22, II, do Decreto nº 11.129/2022).** Não há nos autos prova de ciência ou tolerância do ato lesivo por qualquer nível do corpo diretivo ou gerencial da pessoa jurídica, razão pela qual o fator do art. 22, II, não incide (0%). Reafirma-se que a ciência hierárquica não se presume do porte da empresa, da gravidade do ato ou da posição do executor material — exige demonstração concreta e contemporânea aos fatos, ausente no caso, e a dúvida resolve-se pela não incidência.`;
            itens.push([item4, justWrap(3, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 5 — INTERRUPÇÃO/DESCUMPRIMENTO ──
        let item5;
        if (gIII > 0) {
            const hip = hipoteseArt22III(gServ, gObra, gReg);
            item5 = `**5. Da interrupção de serviço público ou descumprimento contratual (art. 22, III, do Decreto nº 11.129/2022).** Este fator sanciona de forma majorada o ato lesivo cujos efeitos transbordam a esfera patrimonial do ente lesado e atingem a coletividade destinatária da atuação administrativa — pela interrupção no fornecimento de serviço público, pela paralisação de obra contratada ou pelo descumprimento do objeto contratual. O fundamento é a distinção entre o dano ao erário, que a reparação civil recompõe, e o dano social difuso, que não se recompõe: a população privada de um serviço essencial ou de uma obra pública não é indenizada pela devolução dos valores desviados, e é essa lesividade qualificada que o regulamento capta. A graduação opera por três hipóteses autônomas, escalonadas por critérios objetivos de duração e de alcance populacional e territorial do impacto; por expressa opção normativa, aplica-se apenas o *maior* percentual entre as hipóteses configuradas, vedada a cumulação — técnica que evita a dupla valoração de um mesmo desdobramento fático sob rubricas concorrentes. A caracterização exige nexo causal demonstrado entre o ato lesivo e a interrupção ou o descumprimento: consequências atribuíveis a causas alheias à conduta ilícita não sustentam a agravante. No caso, a hipótese de maior gravidade identificada foi: ${hip}, ao percentual de ${pct(gIII)}.`;
            itens.push([item5, justWrap(4, 'A caracterização da hipótese apoia-se em:')].filter(Boolean).join('\n\n'));
        } else {
            item5 = `**5. Da interrupção de serviço público ou descumprimento contratual (art. 22, III, do Decreto nº 11.129/2022).** Não se verificou, no caso, interrupção no fornecimento de serviço público, paralisação de obra ou descumprimento de objeto contratual em decorrência do ato lesivo, não incidindo o fator do art. 22, III (0%). A lesividade da conduta, no caso concreto, circunscreveu-se à esfera do ente lesado, sem o transbordamento social qualificado que fundamenta a agravante.`;
            itens.push([item5, justWrap(4, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 6 — SITUAÇÃO ECONÔMICA DO INFRATOR ──
        let item6;
        if (gEcon > 0) {
            item6 = `**6. Da situação econômica do infrator (art. 22, IV, do Decreto nº 11.129/2022).** Este fator ajusta a sanção à robustez patrimonial da pessoa jurídica, aferida por indicadores objetivos extraídos das demonstrações contábeis — índices de solvência geral e de liquidez e existência de lucro líquido. Sua razão de ser é a preservação da eficácia dissuasória da multa em face da heterogeneidade econômica dos infratores: percentuais que representam constrição severa para uma empresa de capital modesto podem ser absorvidos como mero custo operacional por organizações de elevada solidez — e sanção absorvível como custo não dissuade, convida. A agravante restaura a equivalência do desestímulo, em manifestação sancionatória do princípio da capacidade contributiva. Sua aplicação, contudo, é estritamente vinculada aos indicadores regulamentares: não se trata de juízo impressionista sobre o "porte" ou a notoriedade da empresa, mas de verificação aritmética sobre demonstrações contábeis identificadas nos autos, cuja origem e exercício de referência devem estar documentados. No caso, os indicadores apurados preenchem os requisitos regulamentares, conduzindo ao percentual de ${pct(gEcon)}.`;
            itens.push([item6, justWrap(5, 'Os índices e demonstrações que fundamentam a marcação são:')].filter(Boolean).join('\n\n'));
        } else {
            item6 = `**6. Da situação econômica do infrator (art. 22, IV, do Decreto nº 11.129/2022).** Os indicadores contábeis da pessoa jurídica, verificados nas demonstrações constantes dos autos, não preenchem os requisitos regulamentares do fator do art. 22, IV, que não incide (0%). A não incidência decorre de aferição objetiva, e não de juízo de benevolência: o regulamento reserva a agravante às situações de robustez patrimonial demonstrada.`;
            itens.push([item6, justWrap(5, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 7 — REINCIDÊNCIA ──
        let item7;
        if (gReinc > 0) {
            item7 = `**7. Da reincidência (art. 22, V, do Decreto nº 11.129/2022).** Configura-se a reincidência quando a pessoa jurídica pratica novo ato lesivo em menos de cinco anos contados da publicação do julgamento administrativo anterior. A agravante traduz o juízo de que a recidiva é qualitativamente mais grave que a primeira infração: quem retorna à prática ilícita após responsabilização formal demonstra que a primeira sanção falhou em sua função pedagógica, e o sistema responde elevando o custo da reiteração. Três precisões técnicas delimitam o instituto. Primeira: o termo inicial do quinquênio é a data de *publicação do julgamento* anterior — não a data da prática do ato pretérito —, e o erro nessa contagem conduz tanto à aplicação indevida quanto ao afastamento indevido da agravante. Segunda: é irrelevante que a condenação anterior provenha de outro órgão, Poder ou ente federativo — a reincidência é aferida perante o sistema de responsabilização como um todo, o que impõe pesquisa que não se limite ao órgão condutor do PAR, alcançando o Banco de Sanções da CGU (fonte mais completa, pois o CEIS e o CNEP excluem registros que cumpriram o prazo de publicidade, gerando falsos negativos). Terceira: não se exige identidade entre as infrações — qualquer ato lesivo do art. 5º da Lei nº 12.846/2013 serve de pressuposto. Anote-se, por fim, que na hipótese de acordo de leniência anterior o marco temporal é diverso: o prazo corre da celebração do acordo até cinco anos após a declaração de cumprimento integral. No caso, verificou-se condenação anterior, situando-se a nova infração dentro do quinquênio legal, incidindo o percentual de ${pct(gReinc)}.`;
            itens.push([item7, justWrap(6, 'A verificação da condenação anterior consta de:')].filter(Boolean).join('\n\n'));
        } else {
            item7 = `**7. Da reincidência (art. 22, V, do Decreto nº 11.129/2022).** Consultados os cadastros pertinentes — Banco de Sanções da CGU, CEIS e CNEP —, não se identificou condenação anterior da pessoa jurídica por ato lesivo com julgamento publicado nos cinco anos anteriores à nova infração, não incidindo o fator do art. 22, V (0%). O registro da pesquisa realizada integra a motivação: a primariedade é conclusão extraída de diligência documentada, e não presunção.`;
            itens.push([item7, justWrap(6, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 8 — VALOR DOS CONTRATOS COM O ENTE LESADO ──
        let item8;
        if (gContr > 0) {
            const somatorio = radioLabelTexto('g-contr');
            item8 = `**8. Do valor dos contratos mantidos ou pretendidos com o ente lesado (art. 22, VI, do Decreto nº 11.129/2022).** Este fator gradua a sanção pelo somatório dos contratos, convênios e demais instrumentos mantidos ou pretendidos com o órgão ou entidade lesado nos anos da prática do ato lesivo. Sua lógica é a de medir o grau de imbricação econômica entre o infrator e a vítima institucional: quanto maior o volume de negócios que a pessoa jurídica mantinha ou almejava com o ente lesado, maior a dimensão dos interesses que o ilícito visava proteger ou ampliar — e maior, portanto, o proveito potencial da corrupção do vínculo. A composição do somatório obedece a regras precisas, cuja inobservância é alvo previsível da defesa: incluem-se todos os instrumentos vigentes no(s) exercício(s) da infração, ainda que encerrados no curso do próprio ano; incluem-se os instrumentos *pretendidos* — propostas apresentadas em licitação cujo contrato veio a ser firmado posteriormente —, pois a norma alcança a expectativa negocial e não apenas o vínculo consumado; incluem-se aditivos e instrumentos derivados do contrato originário. Em contrapartida, o somatório restringe-se aos instrumentos celebrados com o ente *efetivamente lesado* — a inclusão de contratos com órgãos diversos, ou de exercícios estranhos ao período da infração, é vício aritmético que compromete o percentual e deve ser conferido pela comissão antes que o seja pela defesa. No caso, o somatório apurado foi de ${somatorio}, correspondente, na tabela regulamentar, ao percentual de ${pct(gContr)}.`;
            itens.push([item8, justWrap(7, 'O levantamento dos instrumentos considerados consta de:')].filter(Boolean).join('\n\n'));
        } else {
            item8 = `**8. Do valor dos contratos mantidos ou pretendidos com o ente lesado (art. 22, VI, do Decreto nº 11.129/2022).** O somatório dos instrumentos mantidos ou pretendidos com o ente lesado nos anos da prática do ato lesivo não ultrapassa o piso regulamentar, não incidindo o fator do art. 22, VI (0%). A verificação decorre de levantamento documentado nos autos, abrangendo os instrumentos vigentes e pretendidos no período de referência.`;
            itens.push([item8, justWrap(7, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 9 — NÃO CONSUMAÇÃO DA INFRAÇÃO ──
        let item9;
        if (tConsum > 0) {
            item9 = `**9. Da não consumação da infração (art. 23, I, do Decreto nº 11.129/2022).** Inaugurando os fatores de atenuação, o art. 23, I, beneficia a pessoa jurídica quando o ato lesivo não chegou a se consumar. O fundamento é o mesmo que, no direito penal, justifica a punição atenuada da tentativa: a reprovabilidade da conduta subsiste — o desvalor da ação é integral —, mas o desvalor do resultado é menor, pois o bem jurídico tutelado não sofreu a lesão completa que a conduta visava produzir. Transposta ao direito administrativo sancionador, a lógica preserva a coerência interna do sistema: seria desproporcional sancionar identicamente o ilícito frustrado e o ilícito exitoso. A aplicação da atenuante é essencialmente probatória — cabe demonstrar, com base nos autos, que o resultado lesivo não se produziu, seja por circunstâncias alheias à vontade do infrator, seja por interrupção do iter — e não se confunde com a ausência de vantagem auferida, que é fenômeno distinto: a infração pode ter-se consumado sem gerar ganho mensurável. No caso, restou comprovada a não consumação do ato lesivo, aplicando-se a redução de ${pct(tConsum)}.`;
            itens.push([item9, justWrap(8, 'A prova da não consumação consiste em:')].filter(Boolean).join('\n\n'));
        } else {
            item9 = `**9. Da não consumação da infração (art. 23, I, do Decreto nº 11.129/2022).** O ato lesivo consumou-se integralmente, produzindo o resultado visado, razão pela qual não incide a atenuante do art. 23, I (0%).`;
            itens.push([item9, justWrap(8, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 10 — RESSARCIMENTO ESPONTÂNEO ──
        let item10;
        if (tRessar > 0) {
            item10 = `**10. Do ressarcimento espontâneo dos danos (art. 23, II, do Decreto nº 11.129/2022).** A atenuante premia a comprovada devolução ou o ressarcimento espontâneo dos danos causados pelo ato lesivo, em fração que acompanha a integralidade da reparação demonstrada — quanto mais completa a recomposição do erário, maior a redução. Dois traços delimitam o instituto. O primeiro é a *espontaneidade*, que lhe é essencial: a reparação obtida por execução forçada, constrição judicial ou compensação imposta não configura a atenuante, pois o que se premia não é o resultado reparatório em si, mas a postura voluntária da pessoa jurídica de recompor o dano antes de compelida — manifestação, no microssistema da Lei nº 12.846/2013, da política legislativa de estímulo à autocomposição. O segundo é a *autonomia* em relação à obrigação civil: o ressarcimento valorado como atenuante não quita nem substitui a obrigação de reparação integral do dano, que subsiste por inteiro (art. 13 da Lei nº 12.846/2013) — a atenuante opera exclusivamente sobre a dosimetria da multa, sem efeito liberatório sobre a esfera cível. A comprovação exige documentação idônea do valor devolvido e de sua correspondência com o dano apurado. No caso, comprovado o ressarcimento na proporção indicada nos autos, aplica-se a redução de ${pct(tRessar)}.`;
            itens.push([item10, justWrap(9, 'A comprovação do ressarcimento consta de:')].filter(Boolean).join('\n\n'));
        } else {
            item10 = `**10. Do ressarcimento espontâneo dos danos (art. 23, II, do Decreto nº 11.129/2022).** Não há comprovação de devolução ou ressarcimento espontâneo dos danos causados pelo ato lesivo, não incidindo a atenuante do art. 23, II (0%).`;
            itens.push([item10, justWrap(9, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 11 — COLABORAÇÃO COM A APURAÇÃO ──
        let item11;
        if (tColab > 0) {
            item11 = `**11. Da colaboração com a apuração (art. 23, III, do Decreto nº 11.129/2022).** A atenuante valora a cooperação efetiva da pessoa jurídica com a apuração da infração, aferida por dois vetores: a *utilidade* e o *ineditismo* dos elementos trazidos aos autos, sempre sob o pressuposto da boa-fé processual. A linha divisória consolidada — e o ponto mais sensível da aplicação — é a que separa colaboração de cumprimento de dever legal: a entrega de documentos que a empresa estava juridicamente obrigada a fornecer mediante intimação não configura colaboração, pois não há mérito atenuante em fazer o que já se devia; a cooperação premiada é a que agrega ao acervo probatório aquilo que a administração não obteria, ou não obteria com a mesma presteza, pelos meios ordinários de instrução. Igualmente relevante é a fronteira com a atenuante seguinte: a admissão da *ocorrência do fato*, desacompanhada de assunção de responsabilidade, enquadra-se neste inciso III; o reconhecimento formal da *responsabilidade* pertence ao inciso IV — distinção que impede o duplo cômputo do mesmo comportamento sob rubricas distintas, pleito que a defesa naturalmente formula e que a comissão deve rejeitar fundamentadamente. Registre-se ainda que comportamentos cooperativos anteriores a tratativas de leniência frustradas podem ser valorados nesta sede, preservando-se o incentivo à cooperação mesmo quando o acordo não se aperfeiçoa. No caso, verificada colaboração relevante nos termos dos autos, aplica-se a redução de ${pct(tColab)}.`;
            itens.push([item11, justWrap(10, 'Os elementos de colaboração valorados foram:')].filter(Boolean).join('\n\n'));
        } else {
            item11 = `**11. Da colaboração com a apuração (art. 23, III, do Decreto nº 11.129/2022).** Não se identificou colaboração da pessoa jurídica que ultrapasse o cumprimento de deveres legais de resposta a intimações e requisições, não incidindo a atenuante do art. 23, III (0%). A conduta processual regular, embora esperada, não constitui o plus cooperativo que a norma premia.`;
            itens.push([item11, justWrap(10, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 12 — ADMISSÃO VOLUNTÁRIA DE RESPONSABILIDADE ──
        let item12;
        if (tAdmis > 0) {
            item12 = `**12. Da admissão voluntária de responsabilidade (art. 23, IV, do Decreto nº 11.129/2022).** A atenuante exige mais que a confirmação da materialidade dos fatos: pressupõe o reconhecimento formal, pela pessoa jurídica, de sua *responsabilidade* pelo ato lesivo — declaração de vontade qualificada, emitida por quem detém poderes de representação, que não se confunde com a mera não contestação nem com a admissão fática do inciso III. Sua valoração repousa em dupla justificativa: de um lado, a economia processual — a admissão abrevia a instrução, dispensa diligências e reduz o custo administrativo da persecução; de outro, o valor institucional da postura de *accountability*, indicativa de que a pessoa jurídica internaliza a reprovação da conduta em vez de resistir a ela, o que é prognóstico favorável de conformidade futura. A autonomia em relação à colaboração do inciso III é funcional: os dois incisos protegem comportamentos distintos e podem, em tese, cumular-se quando ambos estiverem autonomamente configurados — mas jamais pela dupla valoração do mesmo ato. Importa registrar que a admissão de responsabilidade não constitui confissão com efeitos civis automáticos nem dispensa a comissão do dever de fundamentar a materialidade e a autoria com base no conjunto probatório. No caso, houve admissão formal da responsabilidade, aplicando-se a redução de ${pct(tAdmis)}.`;
            itens.push([item12, justWrap(11, 'A admissão consta de:')].filter(Boolean).join('\n\n'));
        } else {
            item12 = `**12. Da admissão voluntária de responsabilidade (art. 23, IV, do Decreto nº 11.129/2022).** A pessoa jurídica não reconheceu formalmente sua responsabilidade pelo ato lesivo, não incidindo a atenuante do art. 23, IV (0%). O exercício regular do direito de defesa, registre-se, não agrava a situação do processado — a não incidência da atenuante é neutra, jamais punitiva.`;
            itens.push([item12, justWrap(11, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 13 — PROGRAMA DE INTEGRIDADE ──
        let item13;
        if (tPI > 0) {
            const pctBruto = pct(piState.rawPlanilha || 0);
            const mult125 = piState.multiplied
                ? `, sobre o qual incidiu o multiplicador de 1,25 da Portaria Conjunta CGU nº 6/2022, por superado o piso regulamentar de 1%`
                : '';
            item13 = `**13. Do programa de integridade (art. 23, V, do Decreto nº 11.129/2022).** A atenuante de maior densidade metodológica do sistema valora a existência e — sobretudo — a *efetividade* de programa de integridade, avaliado segundo os parâmetros do Decreto nº 11.129/2022 e a metodologia técnica dos relatórios de perfil e de conformidade, estruturada em blocos de avaliação (cultura organizacional de integridade, mecanismos, políticas e procedimentos de integridade, e atuação da pessoa jurídica em relação ao ato lesivo). O sistema premia o compliance real, não o cosmético: código de conduta sem evidência de treinamento, canal de denúncias sem casos processados ou comitê de ética sem atas de atuação tendem a pontuar mal, pois a avaliação exige demonstração documentada de aplicação prática. A ratio da atenuante é de política regulatória: transformar a integridade empresarial de custo em investimento, sinalizando ao mercado que a estruturação séria de mecanismos de prevenção produz efeito econômico mensurável no momento sancionador. Nessa mesma linha, sobre o percentual bruto apurado na avaliação técnica incide, quando alcançado o piso de 1%, o fator multiplicador de 1,25 instituído pela Portaria Conjunta CGU nº 6/2022 — reforço regulatório do incentivo, de aplicação obrigatória quando preenchido o pressuposto, e cuja incidência deve constar expressamente da motivação. Anote-se, por fim, a independência desta atenuante em relação à colaboração processual (art. 23, III): avaliam-se objetos distintos — ali, a conduta no processo; aqui, a estrutura preventiva da organização. No caso, a avaliação técnica resultou em percentual bruto de ${pctBruto}${mult125}, alcançando-se a redução final de ${pct(tPI)}.`;
            itens.push([item13, justWrap(12, 'A avaliação do programa apoia-se em:')].filter(Boolean).join('\n\n'));
        } else {
            item13 = `**13. Do programa de integridade (art. 23, V, do Decreto nº 11.129/2022).** Não foi demonstrada a existência de programa de integridade apto à valoração nos termos do art. 23, V — seja pela não apresentação dos relatórios de perfil e de conformidade no prazo assinalado na intimação, com a consequência preclusiva de que a pessoa jurídica foi expressamente advertida, seja pela ausência de efetividade apurada na avaliação técnica —, não incidindo a atenuante (0%).`;
            itens.push([item13, justWrap(12, '')].filter(Boolean).join('\n\n'));
        }

        // ── ITEM 14 — SÍNTESE DA DOSIMETRIA ──
        const lc = lastCalc || { fat: fat, idx: 0, bruta: 0, finalVal: 0, piso: 0, teto: 0, idxEhZeroOuNegativo: true, totalAgrav: 0, totalAten: 0 };
        let item14 = `**14. Da consolidação do índice de dosimetria.** Examinados individualmente todos os fatores, o somatório dos agravantes (art. 22) totalizou ${pct(lc.totalAgrav)}, e o dos atenuantes (art. 23), ${pct(lc.totalAten)}. O índice de dosimetria — diferença aritmética entre ambos — corresponde a ${pct(lc.idx)}.`;
        if (!lc.idxEhZeroOuNegativo) {
            item14 += `\n\nAplicado o índice sobre a base de cálculo de ${fmt(lc.fat)}, apura-se multa bruta de ${fmt(lc.bruta)}, valor preliminar sujeito à verificação dos limites legais do art. 25, a seguir procedida.`;
        } else {
            item14 += `\n\nResultando o índice em valor igual ou inferior a zero, incide o art. 25, § 2º, do Decreto nº 11.129/2022, que impõe a fixação da multa no valor do limite mínimo. A solução regulamentar tem fundamento sistemático preciso: a preponderância de atenuantes reduz a sanção, mas não a suprime — a multa é consequência legal necessária da responsabilização (art. 6º, I, da Lei nº 12.846/2013), e admitir sua eliminação pela via da dosimetria equivaleria a criar, por aritmética, hipótese de isenção que a lei não previu.`;
        }
        itens.push(item14);

        // ── ITEM 15 — VERIFICAÇÃO DOS LIMITES LEGAIS ──
        const descricaoPiso = descricaoLimite('d-piso-label', 'Piso Legal') || 'piso legal';
        const descricaoTeto = descricaoLimite('d-teto-label', 'Teto Legal') || 'teto legal';
        const valorPiso = document.getElementById('d-piso') ? document.getElementById('d-piso').textContent : fmt(lc.piso);
        const valorTeto = document.getElementById('d-teto') ? document.getElementById('d-teto').textContent : fmt(lc.teto);
        const EPS = 0.01;
        let var15 = 'A';
        if (Math.abs(lc.finalVal - lc.bruta) < EPS) var15 = 'A';
        else if (Math.abs(lc.finalVal - lc.piso) < EPS) var15 = 'B';
        else if (Math.abs(lc.finalVal - lc.teto) < EPS) var15 = 'C';

        let item15 = `**15. Dos limites mínimo e máximo (art. 25 do Decreto nº 11.129/2022).** O resultado da dosimetria submete-se a dupla contenção normativa: a multa não pode ser inferior ao piso (${descricaoPiso}, apurado em ${valorPiso}) nem superior ao teto (${descricaoTeto}, apurado em ${valorTeto}). A verificação de limites não é conferência aritmética acessória — é a cláusula de fechamento do sistema de proporcionalidade: o piso, ancorado na vantagem auferida, garante que a sanção jamais seja inferior ao proveito do ilícito, impedindo que a infração se converta em negócio economicamente racional; o teto, referenciado à maior vantagem e ao limite percentual do faturamento, impede a sanção confiscatória e assegura correlação entre a pena e a dimensão econômica do fato. Entre esses marcos, o resultado da dosimetria é soberano.`;
        if (var15 === 'A') {
            item15 += `\n\nNo caso, a multa bruta de ${fmt(lc.bruta)} situa-se dentro dos limites legais, sendo mantida como valor final da sanção pecuniária.`;
        } else if (var15 === 'B') {
            item15 += `\n\nNo caso, a multa bruta de ${fmt(lc.bruta)} resultou inferior ao piso legal, razão pela qual a multa é elevada ao valor de ${valorPiso}, nos termos do art. 25, I, do Decreto nº 11.129/2022 — prevalência do limite mínimo que assegura que a sanção não fique aquém do proveito econômico do ilícito.`;
        } else {
            item15 += `\n\nNo caso, a multa bruta de ${fmt(lc.bruta)} excedeu o teto legal, razão pela qual a multa é reduzida ao valor de ${valorTeto}, nos termos do art. 25, II, do Decreto nº 11.129/2022 — contenção que preserva a proporcionalidade da sanção em face da dimensão econômica do fato.`;
        }
        itens.push(item15);

        // ── ITEM 16 — PUBLICAÇÃO EXTRAORDINÁRIA ──
        const p = publicacaoResult || { cenario: 'A', aliquota: 0, prazo: 30, semBase: false };
        let var16 = 'A';
        if (p.semBase) var16 = 'C';
        else if (p.cenario !== 'A') var16 = 'B';

        let item16 = `**16. Da publicação extraordinária da decisão condenatória (art. 6º, II, da Lei nº 12.846/2013 e art. 24 do Decreto nº 11.129/2022).** A publicação extraordinária é sanção autônoma — não mera divulgação de ato processual —, aplicada conjuntamente com a multa pecuniária, mediante extrato da decisão condenatória, a expensas da pessoa jurídica, em meio de comunicação de grande circulação na área da infração e de atuação da empresa (ou, na falta, em publicação de circulação nacional), por afixação de edital visível ao público no próprio estabelecimento e em sítio eletrônico. Sua função é pedagógica e dissuasória por via reputacional: enquanto a multa atinge o patrimônio, a publicação atinge o ativo intangível mais sensível da pessoa jurídica — a reputação perante o mercado, os parceiros e a sociedade —, e é precisamente essa exposição que confere ao sistema anticorrupção parte relevante de seu efeito preventivo geral. O prazo da publicação não é discricionário: escalona-se, nos termos do art. 24 do Decreto nº 11.129/2022, conforme a alíquota de referência da multa efetivamente aplicada, vinculando a intensidade da sanção reputacional à gravidade econômica apurada na dosimetria.`;
        if (var16 === 'A') {
            item16 += `\n\nNo caso, o valor final da multa corresponde à aplicação direta do índice de dosimetria sobre a base de cálculo, de modo que a alíquota de referência é o próprio índice apurado: ${pctBR(p.aliquota)}.`;
        } else if (var16 === 'B') {
            item16 += `\n\nNo caso, tendo o valor final da multa sido ajustado pela verificação de limites do art. 25, a alíquota preliminar deixou de corresponder ao valor efetivamente aplicado; a alíquota de referência é então recalculada pelo quociente entre o valor final da multa e a base de cálculo, resultando em ${pctBR(p.aliquota)}.`;
        } else {
            item16 += `\n\nNo caso, sendo a base de cálculo igual a zero ou não estimável — o que inviabiliza aritmeticamente o recálculo pelo quociente —, adota-se como alíquota de referência o próprio índice da dosimetria preliminar, no valor de ${pctBR(p.aliquota)}.`;
        }
        item16 += `\n\nPela tabela de escalonamento do art. 24, a alíquota de referência de ${pctBR(p.aliquota)} corresponde ao prazo de publicação de ${p.prazo} dias corridos (${PRAZO_EXTENSO[p.prazo]}), contados da publicação da decisão condenatória no órgão oficial.`;
        const just13 = justWrap(13, 'Observações da comissão quanto à publicação:');
        itens.push([item16, just13].filter(Boolean).join('\n\n'));

        // ── ITEM 17 — CONCLUSÃO ──
        const item17 = `**17. Conclusão.** Pelo exposto, em estrita observância à metodologia dos arts. 20 a 26 do Decreto nº 11.129/2022 e com motivação individualizada de cada parâmetro — inclusive das hipóteses de não incidência —, na forma do art. 50 da Lei nº 9.784/1999, fixa-se a multa do art. 6º, I, da Lei nº 12.846/2013 em **${finalValFmt}**, cumulada com a publicação extraordinária da decisão condenatória pelo prazo de **${p.prazo} dias corridos**, nos termos do art. 6º, II, da mesma lei e do art. 24 do Decreto nº 11.129/2022. O resultado observa os limites do art. 25 e reflete, por construção metodológica, a proporcionalidade exigida pelo art. 6º, § 1º, da Lei nº 12.846/2013, pelo art. 2º da Lei nº 9.784/1999 e pelos arts. 20 e 22 da LINDB.`;
        itens.push(item17);

        return { cabecalho, abertura, itens };
    }

    function montarTextoPlano() {
        const d = gerarBlocosFundamentado();
        const linhas = [];
        d.cabecalho.forEach(l => linhas.push(mdToText(l)));
        linhas.push('');
        linhas.push(mdToText(d.abertura));
        d.itens.forEach(it => { linhas.push(''); linhas.push(mdToText(it)); });
        return linhas.join('\n');
    }

    function montarHtmlRelatorio() {
        const d = gerarBlocosFundamentado();
        let html = '';
        d.cabecalho.forEach((l, i) => {
            html += i === 0 ? `<p style="text-align:center; font-weight:800; font-size:13pt;">${mdToHtml(l)}</p>` : `<p style="text-align:center;">${mdToHtml(l)}</p>`;
        });
        html += `<div style="page-break-inside: avoid;">${mdToHtml(d.abertura).split('\n\n').map(p2 => '<p>' + p2 + '</p>').join('')}</div>`;
        d.itens.forEach(it => {
            const paras = it.split('\n\n').map(p2 => '<p style="page-break-inside: avoid;">' + mdToHtml(p2) + '</p>').join('');
            html += paras;
        });
        return html;
    }

    function imprimirRelatorioFundamentado() {
        const htmlBody = montarHtmlRelatorio();
        const anoPARval = document.getElementById('in-ano-par').value || '—';
        const win = window.open('', '_blank');
        const doc2 = `<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8">
        <title>Relatório Fundamentado — PAR</title>
        <style>
            body { font-family: Georgia, 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; color: #111; margin: 0; text-align: justify; }
            @page { margin: 2.5cm; }
            p { margin: 0 0 12px 0; }
            b { color: #000; }
        </style></head><body>${htmlBody}</body></html>`;
        win.document.write(doc2);
        win.document.close();
        win.focus();
        setTimeout(() => win.print(), 500);
    }

