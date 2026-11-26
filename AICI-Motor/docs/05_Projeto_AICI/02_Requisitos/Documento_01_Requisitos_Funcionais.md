# Requisitos Funcionais

**Versão 0.3 - novembro/2026**

Legenda de **prioridade** (MoSCoW): **M** deve, **S** deveria, **C** poderia, **W** não nesta fase.
Legenda de **situação**: **Implementado** (existe e tem teste automatizado ou foi verificado no navegador), **Parcial** (existe com limitação descrita), **Planejado** (não existe).
**UC** = caso de uso (Documento 03 da pasta Casos de Uso). A coluna "Evidência" aponta o módulo e o teste em `AICI-Motor/tests/test_pipeline.py`.

## 1. Requisitos originais (RF001 a RF010)

| ID | Requisito | Prior. | Critério de aceite | UC | Situação | Evidência / observação |
|---|---|---|---|---|---|---|
| RF001 | Pesquisar precedentes semelhantes | M | Dada a descrição da atividade, retorna até 4 precedentes, cada um com título, origem (arquivo), ano e **motivo da similaridade**; precedentes da COGER pesam mais que os demais | UC001 | Implementado | `retriever`, `indexer`; teste `test_recuperacao_traz_origem_e_tipos`. Busca por palavras (BM25); a busca por sentido é opcional (RF024) |
| RF002 | Pesquisar pareceres emitidos por tema | M | Retorna pareceres da COGER relacionados à atividade, com número, ano e tema extraídos do nome do arquivo (`PA_<num>_<ano>_<Tema>`) | UC001 | Parcial | Recuperação por similaridade implementada. **Falta** filtro explícito por tema/ano/resultado na API |
| RF003 | Localizar normativos relacionados ao caso | M | Retorna normativos (Lei nº 12.813/2013, Portaria nº 333/2013 etc.) relevantes ao caso, com a origem | UC001 | Implementado | Teste `test_recuperacao_traz_origem_e_tipos` (a Lei é recuperada). Depende de a pasta `normativos` estar populada |
| RF004 | Interpretar descrições em linguagem natural | M | Extrai atividade, entidade, remuneração, vínculo, descrição e atribuições do texto livre da consulta | UC001, UC002 | Parcial | Extração por regras e leitura do formulário SeCI (`fact_extractor`, teste `test_extrator_formulario_seci`); resumo por IA opcional. Interpretação semântica depende de embeddings/IA |
| RF005 | Sugerir atividade enquadrável | M | Sugere uma das categorias existentes, com grau de confiança (alta/média/baixa) e motivos; nunca cria categoria nova | UC002 | Implementado | `classifier`; testes `test_classificador_usa_so_categorias_do_html`, `test_sem_correspondencia_cai_no_generico`. A acurácia ainda não foi medida com casos reais |
| RF006 | Indicar precedentes correlatos | M | Lista precedentes e pareceres correlatos com justificativa | UC001 | Implementado | Justificativa lexical (termos em comum); frase de similaridade pela IA, se habilitada (`test_ia_fundamentacao_com_fontes_validadas`) |
| RF007 | Sugerir compromissos mitigadores | S | Apresenta as ressalvas e os deveres aplicáveis ao caso | UC003 | Implementado | Deveres padrão (item 13 do Parecer Coger/GNP nº 522/2023) e ressalvas do modelo; ressalvas da IA, se habilitada. Fonte: `templates/institucional.json` |
| RF008 | Revisar consistência do parecer | S | Aponta campos pendentes, parágrafo sem fonte, conclusão incoerente com o resultado e ausência de menção ao Termo | UC003 | Implementado | `POST /revisar`; no gerador HTML, o painel de coerência. Revisão adicional pela IA, se habilitada |
| RF009 | Gerar minuta preliminar | M | Gera relatório, fundamentos e conclusão, cada parágrafo com a origem | UC001 a UC003 | Implementado | `report_generator`; teste `test_fluxo_completo_offline` |
| RF010 | Permitir geração de documento Word no modelo institucional | M | Gera .docx editável no padrão dos pareceres da COGER (cabeçalho, ementa, parágrafos numerados, assinaturas); campos pendentes destacados em amarelo | UC001 | Implementado | `docx_generator` (modelos em `templates/*.docx`); gerador HTML; teste `test_fluxo_completo_offline` |

## 2. Requisitos adicionais identificados no desenvolvimento

### 2.1 Entrada e análise

| ID | Requisito | Prior. | Critério de aceite | Situação | Evidência / observação |
|---|---|---|---|---|---|
| RF011 | Receber o PDF da consulta e extrair o texto, com OCR quando for digitalizado | M | Aceita somente PDF (verifica a assinatura do arquivo), até 25 MB; PDF sem camada de texto aciona o OCR; se o OCR não estiver instalado, avisa | Implementado (OCR não testado) | `pdf_reader`, `ocr_service`; testes `test_pdf_texto_e_limpeza`, `test_pdf_sem_texto_avisa_ocr_ausente`, `test_api_validacoes_e_token`. O OCR depende de instalação opcional (EasyOCR) |
| RF012 | Extrair do formulário SeCI os dados do servidor e as respostas 1 a 10 | M | Extrai nome, cargo, matrícula, protocolo, tipo (consulta ou pedido) e as respostas, ignorando os cabeçalhos repetidos a cada página | Implementado | Teste `test_extrator_formulario_seci`; verificado com um formulário real do SeCI |
| RF013 | Registrar a consulta, a análise e o resultado | M | Cada upload gera um identificador; a análise fica gravada (JSON) e o status é atualizado | Implementado | Banco SQLite (`consultas`, `pareceres`, `metricas`) e `output/consulta_<id>/analise.json` |
| RF014 | Manter, no gerador offline, o preenchimento a partir do PDF e a identificação do tema | S | O gerador HTML lê o PDF no navegador, sem internet, e preenche os campos | Implementado | `gerador-parecer-conflito.html` (pdf.js embutido) |

### 2.2 Decisão do parecerista

| ID | Requisito | Prior. | Critério de aceite | Situação | Evidência / observação |
|---|---|---|---|---|---|
| RF015 | Permitir ao parecerista escolher a atividade e a **conclusão do caso concreto**, independentemente do modelo sugerido | M | Quatro resultados selecionáveis; ementa e conclusão mudam; aviso de revisão dos fundamentos quando a conclusão diverge do modelo | Implementado | Gerador HTML e `POST /minuta`; teste `test_fluxo_completo_offline` |
| RF016 | Permitir várias atividades no mesmo parecer, com conclusão única agrupada | S | Atividades com o mesmo resultado compartilham uma frase; resultados diferentes geram uma frase por grupo | Implementado | Gerador HTML (verificado no navegador) |
| RF017 | **Exigir a validação humana** antes de gerar qualquer documento | M | Na tela, os botões ficam bloqueados até a confirmação; na API, `/gerar-parecer` recusa (HTTP 422) sem `validado=true` | Implementado | Teste `test_geracao_exige_validacao_humana` |
| RF018 | Gerar o Termo de Compromisso nas autorizações com ressalvas | M | Disponível somente para o resultado "sem conflito, com ressalvas"; reúne os compromissos aplicáveis, com campos para assinatura do servidor, da chefia e da Comissão de Ética | Implementado | `docx_generator.gerar_termo`; teste `test_fluxo_completo_offline` |
| RF019 | Gerar o despacho de encaminhamento | C | Gera .docx do despacho a partir do modelo | Implementado | `docx_generator.gerar_despacho` |

### 2.3 Copilot Chat da RFB (modo assistido)

O Copilot Chat (conta corporativa, Microsoft 365) é a IA homologada e autorizada pelo CTSI, mas não oferece API ao AICI. O modo assistido leva o contexto ao chat pelas mãos do parecerista.

| ID | Requisito | Prior. | Critério de aceite | Situação | Evidência / observação |
|---|---|---|---|---|---|
| RF033 | Gerar o prompt para o Copilot Chat com o caso, as regras da COGER, os normativos, os precedentes, os pareceres e os modelos | M | `POST /ia/pacote` devolve o prompt com as seções e os marcadores [R1], [N1], [P1], [A1], [M1]; dados pessoais mascarados | Implementado | `analysis_service.pacote_copilot`; teste `test_copilot_chat_assistido`; verificado no navegador. **Não testado com o Copilot Chat real** |
| RF034 | Oferecer prompt curto + arquivo de contexto para anexar ao chat | S | `prompt_curto` e `contexto_md` (todo o acervo recuperado) | Implementado | Botão "Baixar contexto_AICI.md" na aba |
| RF035 | Respeitar o limite de caracteres do prompt do chat | M | O prompt completo não excede `ia.copilot_chat.limite_caracteres`; o espaço é repartido entre os trechos (prioridade normativos, precedentes, pareceres, modelos) e o aviso informa o que ficou de fora | Implementado | Teste `test_pacote_respeita_limite_e_so_vale_citar_o_que_foi_enviado`. O limite padrão (7.500) é uma suposição: **confirmar com a TI** |
| RF036 | Validar a resposta colada do Copilot Chat antes de usá-la | M | Aceita só JSON no formato pedido; fonte que não existe (ou que não coube no prompt) invalida o parágrafo; resultado fora da lista é ignorado; resposta inválida é recusada com mensagem | Implementado | `POST /ia/resposta`; testes `test_copilot_chat_assistido`, `test_pacote_respeita_limite_e_so_vale_citar_o_que_foi_enviado` |
| RF037 | Registrar na trilha de auditoria cada prompt gerado e cada resposta aplicada | M | `metrics/ia_auditoria.jsonl` com data, tipo (pacote ou resposta), consulta e conteúdo | Implementado | Teste `test_copilot_chat_assistido` |
| RF038 | Orientar o usuário a usar somente o Copilot Chat da conta corporativa | M | Aviso na tela e link para o Copilot Chat corporativo | Implementado (orientação) | O AICI **não controla** onde o usuário cola o prompt |
| RF039 | O documento Word usa a minuta validada com a resposta do Copilot | M | O gerador envia a minuta aprovada a `/gerar-parecer`; mudar atividade ou conclusão pede confirmação e descarta a resposta | Implementado | Teste `test_copilot_chat_assistido`; verificado no navegador |

### 2.3a Modo local (sem motor, dentro do HTML)

Adicionado porque o computador de uso pode não ter Python. Reutiliza a leitura do PDF e a identificação do gerador e leva o Copilot Chat ao mesmo fluxo assistido, sem instalar nada.

| ID | Requisito | Prior. | Critério de aceite | Situação | Evidência / observação |
|---|---|---|---|---|---|
| RF040 | Analisar a consulta (PDF, DOCX, ODT ou TXT) no próprio navegador, sem motor e sem internet | M | Preenche servidor, cargo, matrícula, protocolo, respostas do SeCI; mostra fatos, atividade sugerida (trocável), situação e precedentes da CGU parecidos | Implementado | Aba "Análise Inteligente", modo Local; verificado no navegador. Não consulta a biblioteca de pareceres |
| RF041 | Gerar, no navegador, o prompt para o Copilot Chat (caso mascarado, regras da COGER, normativos, precedentes da CGU, modelo da atividade) dentro do limite de caracteres | M | Prompt com marcadores [R1], [N1], [P1], [M1]; sem CPF, matrícula, telefone, e-mail e nome; limite configurável | Implementado | Verificado no navegador (7.500 caracteres, sem vazamento de identificadores). O acervo embutido: `parecer/kb_local.json` |
| RF042 | Validar a resposta colada | M | JSON obrigatório; fonte que não foi enviada invalida o parágrafo; resposta inválida recusada com orientação | Implementado | Verificado no navegador |
| RF043 | Aplicar a fundamentação validada ao parecer do gerador | M | A fundamentação do Copilot substitui a do modelo no Word; a conferência avisa para revisar; é possível remover | Implementado | Verificado no navegador, inclusive o Word gerado |
| RF045 | Conectar a biblioteca da COGER (pasta sincronizada do SharePoint) e indexá-la no navegador | S | Lê PDF, DOCX, TXT e MD de `01_`, `02_` e `03_`; ignora `_Duplicados_Revisar` e demais pastas; mostra progresso e permite cancelar; reaproveita o que não mudou; guarda o índice no navegador | Implementado (testado com biblioteca sintética) | Verificado no navegador com PDF, DOCX e TXT. **Desempenho com as centenas de PDFs reais não medido** |
| RF046 | Pesquisar pareceres, precedentes e normativos da biblioteca conectada e mostrá-los com origem e termos em comum | S | Lista com título, ano, arquivo e trecho | Implementado | Idem |
| RF047 | Levar ao prompt do Copilot os trechos da biblioteca (marcador [A]), com nomes de servidores mascarados no cabeçalho | S | Trechos entram no prompt, citáveis; "Servidor: ..." vira [SERVIDOR] | Implementado | Nomes no corpo do texto podem permanecer |
| RF048 | Etapa 1 com o Copilot: gerar o prompt para entender o caso (caso mascarado + lista fechada de categorias) dentro do limite de caracteres | S | Prompt com instruções, caso e a lista "id: atividade"; o texto das respostas é encurtado se necessário para caber | Implementado | `prompts/understand.txt`; verificado no navegador (≈ 6.000 caracteres, sem nome, CPF ou matrícula) |
| RF049 | Validar a resposta da etapa 1 | S | JSON obrigatório; atividade e atividades adicionais só da lista (fora da lista: descartada com aviso); incisos só algarismos romanos I a XI; termos saneados (máx. 20, 60 caracteres) | Implementado | Verificado no navegador |
| RF050 | Usar os termos da etapa 1 para refazer a busca nos precedentes da CGU e na biblioteca, com termos editáveis | S | Documento com vocabulário do termo sobe na lista (ex.: de 6,3 para 22,2 de pontuação e da 3ª para a 1ª posição em teste) | Implementado | Verificado em biblioteca sintética. **Ganho com casos reais não medido** |
| RF051 | Levar o entendimento da etapa 1 (incisos, fatos, pontos de atenção, informações que faltam) ao prompt da etapa 2 | S | Aparece no caso concreto do prompt, como sugestão a confirmar | Implementado | Verificado no navegador |
| RF052 | Aplicar as sugestões da etapa 1 somente por ação do usuário | M | "Usar esta atividade", "＋ atividade adicional" e "Marcar incisos" são botões; nada é aplicado sozinho | Implementado | Verificado no navegador |
| RF053 | Base ampliada de precedentes da CGU (SeCI): todos os 123 casos da RFB (2014 a 2026) embutidos no gerador e os 2.576 casos de todos os órgãos como arquivos de biblioteca | S | Um trecho por caso, começando por "Protocolo SeCI nº ..."; título com protocolo, órgão e resultado; peso COGER > CGU/RFB > CGU outros órgãos; vários casos do mesmo arquivo podem aparecer | Implementado | Testes `test_precedentes_cgu_um_trecho_por_caso`; verificado no navegador (2.576 casos indexados em menos de 1 s; busca em cerca de 5 ms). Dados públicos baixados da API de busca do SeCI em 25/11/2026 |
| RF054 | Atualizar a base da CGU por rotina | C | `parecer/atualizar_precedentes.py [--md pasta]` baixa os casos (com pausa entre páginas) e regenera o JSON da RFB e os arquivos Markdown | Implementado | Execução manual; agendamento periódico planejado |
| RF055 | Preenchimento guiado no gerador: só os campos essenciais visíveis; "Mais opções" e "Respostas do formulário SeCI" recolhidas (com contagem de respostas preenchidas); campos pendentes clicáveis (na prévia e na lista "Falta preencher") que levam ao campo; local de assinatura lembrado; sugestão do próximo nº do parecer | S | O formulário vazio cai de cerca de 2.770 para cerca de 1.070 px de altura; clicar em `[PROCESSO]` na prévia leva ao campo; ao reabrir, a cidade é lembrada e o nº mostra "próximo: N+1" | Implementado | Verificado no navegador. Unidade, equipe, cargo e tratamento **não** são lembrados (mudam a cada consulente) |
| RF056 | Conclusão por atividade do pedido: ler a lista de atividades da pergunta 2 (a, b, c ...), sugerir a conclusão de cada uma (a partir dos "componentes" do modelo) e redigir uma conclusão para cada atividade | M | Pedido com 3 atividades gera a frase "a) a atividade de “...” não configura conflito...; b) ...; c) ... não pode ser autorizada ..., em razão de ..."; o Termo de Compromisso e o parágrafo de autorização citam só as atividades autorizadas; a conferência avisa se a conclusão trata o conjunto | Implementado | Verificado no navegador com um formulário real do SeCI de 3 atividades e no Word gerado. Só no gerador HTML; o motor Python ainda tem a conclusão única |
| RF057 | Ler por OCR, no navegador e sem internet, PDF sem texto selecionável (texto desenhado como imagem ou vetor), como a impressão da solicitação emitida pelo SeCI/SERPRO | M | Se o PDF não tem texto, o gerador faz OCR em português (tesseract.js embutido), preenche os dados e as 9 respostas e avisa que o texto veio de OCR e deve ser conferido | Implementado | Verificado com um PDF real de 2 páginas que o gerador antes não lia: nome, matrícula, protocolo, tipo, cargo e as respostas 1 a 10 corretos; cerca de 10 s no total. O arquivo do gerador passa de 1,9 para 5,6 MB. O OCR do motor Python (EasyOCR) continua não testado |
| RF058 | Recomendar a atividade e a situação a partir do caso e da base: separar a atividade ("proferir palestras e dar aulas") do assunto ("sobre IRPF"), pesar os termos pela raridade, casar o caso com as situações de cada modelo e somar a evidência de precedentes parecidos (CGU embutidos e biblioteca conectada, inclusive o tema dos pareceres) | M | A atividade sugerida e a situação "parecida com o caso" refletem o que o servidor vai fazer, não o assunto; os chips mostram quantos precedentes parecidos sustentam a sugestão | Implementado | Caso real que motivou a mudança: "palestras e aulas sobre IRPF" saía como "declaração de IRPF" e agora sai como Palestras (com 3 precedentes parecidos), Magistério e Cursos entre as opções. Auto-avaliação com as 160 situações dos modelos: acerto na 1ª posição de 88% para 97% e nas 3 primeiras de 94% para 100% (avaliação circular, otimista; falta medir com consultas reais) |
| RF059 | Situação em branco: "Nenhuma destas situações - redigir com base no caso concreto" | M | Quando nenhuma situação do modelo descreve o caso (ou a pontuação é baixa), o parecer usa a estrutura padrão com a atividade, a ementa e os campos de fundamentos para escrever (um parágrafo por linha), usar os precedentes ou aplicar a resposta do Copilot | Implementado | Verificado no navegador |
| RF060 | Ementa editável | M | Caixa "Ementa do parecer (editar)": o texto editado vale no parecer e no Word; "Restaurar a ementa do modelo" volta ao padrão; trocar a situação recarrega a ementa | Implementado | Verificado no navegador |
| RF061 | Vocabulário aprendido dos pareceres reais da COGER e avaliação com dados reais | S | Termos que a COGER usa para cada atividade (119 temas e descritores de 476 pareceres) entram como um sinal da recomendação; só termos já presentes nos modelos ou nas ementas públicas da CGU (sem nomes de pessoas); rotina `parecer/avaliacao/treinar_vocabulario.js` com validação cruzada | Implementado | Medição com descritores reais (nomes de arquivo, texto curto e ruidoso): atividade certa na 1ª sugestão em 73,7% sem o vocabulário e **76,3%** com ele, em casos não vistos no treino; entre as 3 primeiras, 84,9% e **86,8%**. Com os nomes dos temas: 92,9% e 97,3% (vistos no treino). Abaixo da meta de 85% na 1ª sugestão: o usuário deve conferir a atividade |
| RF062 | Situação escolhida pelo que a distingue: termos próprios de uma situação (ex.: "teletrabalho", "público específico") precisam aparecer no pedido | S | Situações cujo traço distintivo não está no caso perdem pontuação; as próximas ficam marcadas "parecida com o caso" | Implementado | Verificado com 8 casos sintéticos; sem medição com casos reais |
| RF063 | Identidade visual alinhada à Wiki Coger (azul-marinho e dourado, cabeçalho com abas, cartões) e tratamento "a servidora" detectado pelas respostas | C | - | Implementado | Verificado no navegador |
| RF044 | Funcionar sem instalação | M | Nenhum programa além do navegador | Implementado | Modo local é o padrão da aba |

### 2.4 Conhecimento, IA e gestão

| ID | Requisito | Prior. | Critério de aceite | Situação | Evidência / observação |
|---|---|---|---|---|---|
| RF020 | Indexar a biblioteca de forma incremental | M | Reprocessa só arquivos novos ou alterados e remove os excluídos; um arquivo corrompido não interrompe a indexação | Implementado | `indexer`; teste `test_indexacao_incremental` |
| RF021 | Enviar à IA sempre o caso **junto** com normativos, precedentes/pareceres/modelos e as regras da COGER | M | Sem normativos e sem precedentes/pareceres/modelos, a IA não é chamada | Implementado | `ai_provider.montar_contexto`; testes `test_ia_nunca_recebe_so_o_caso`, `test_regras_coger_sempre_no_contexto` |
| RF022 | Validar a resposta da IA contra o acervo | M | Categoria fora da lista é descartada; parágrafo sem fonte válida é descartado; falha da IA volta ao modo extrativo | Implementado | Testes `test_classificador_usa_so_categorias_do_html`, `test_ia_fundamentacao_com_fontes_validadas`, `test_ia_indisponivel_cai_no_extrativo` |
| RF023 | Permitir trocar de provedor de IA por configuração | S | `ia.provider`: offline, mock, copilot, azure, openai | Implementado (sem endpoint real) | `ai_provider`; teste `test_provedores_configuracao`. **Nenhum provedor real foi exercitado.** Como o Copilot Chat não tem API, os provedores automáticos só serão usados se a TI disponibilizar acesso programático; o caminho principal é o modo assistido (RF033 a RF039) |
| RF024 | Busca semântica por embeddings locais, combinada à busca por palavras | S | BM25 top 20 + vetores top 20, fusão (RRF) e reclassificação | Parcial | Mecanismo testado com embedder de teste (`test_busca_hibrida_acha_o_que_o_bm25_nao_acha`). **Nenhum modelo real (bge-m3 / e5) foi avaliado** |
| RF025 | Registrar indicadores | S | Cada parecer gerado grava atividade, resultado, precedente utilizado e data; `GET /indicadores` consolida | Implementado | `metrics_service`; teste `test_fluxo_completo_offline`. Sem painel gráfico |
| RF026 | Registrar cada chamada à IA (trilha para o curador) | M | Grava data, provedor, tamanho e, se configurado, o prompt e a resposta (já mascarados) | Implementado | `AuditedProvider`; teste `test_auditoria_das_chamadas_de_ia` |
| RF027 | Mascarar dados pessoais antes do envio à IA | M | CPF, matrícula, telefone, e-mail e nome do servidor substituídos por marcadores | Implementado | `utilities/text.anonimizar`; teste `test_ia_fundamentacao_com_fontes_validadas` |
| RF028 | Consultar a memória institucional em linguagem natural (resposta fundamentada com os documentos citados) | S | O usuário pergunta; o sistema pesquisa e responde com as fontes | Planejado | UC004 |
| RF029 | Sincronizar a biblioteca com o SharePoint | S | Sincronização automática e agendada | Planejado | Hoje, importação manual por script (`scripts/importar_biblioteca.py`) |
| RF030 | Catalogação assistida do acervo (status de cada documento: não processado, classificado, validado, utilizado) | C | Metadados e status por documento, com validação humana | Parcial | Planilha de metadados no Drive (coluna `Status_IA`); sem integração com o motor |
| RF031 | Atualizar os precedentes da CGU sobre a RFB | C | Rotina de atualização das ementas | Implementado | `parecer/atualizar_precedentes.py` (123 casos da RFB embutidos no gerador; ver RF053) |
| RF032 | Painel de indicadores gerenciais | C | Visualização gráfica por atividade, resultado, precedente e período | Planejado | Hoje, tabelas simples na aba |

## 3. Resumo da situação

| Situação | Quantidade | Requisitos |
|---|---|---|
| Implementado | 56 | RF001, RF003, RF005 a RF023, RF025 a RF027, RF031, RF033 a RF063 |
| Parcial | 4 | RF002, RF004, RF024, RF030 |
| Planejado | 3 | RF028, RF029, RF032 |
| **Total** | **63** | |

"Implementado" significa que existe e foi testado em ambiente de desenvolvimento; não significa homologado nem validado com casos reais. O OCR (RF011), os provedores automáticos de IA (RF023) e o modo assistido com o Copilot Chat (RF033 a RF044, no motor e no modo local) estão implementados mas **não foram exercitados** contra serviços reais (o modo assistido foi testado com respostas simuladas). O modo local só busca na biblioteca de pareceres da COGER se o usuário conectar a pasta sincronizada.

## 4. Matriz de rastreabilidade (RF -> componente)

| Componente | Requisitos atendidos |
|---|---|
| `app/services/pdf_reader.py`, `ocr_service.py` | RF011 |
| `app/services/fact_extractor.py` | RF004, RF012 |
| `app/services/indexer.py`, `embeddings.py` | RF001 a RF003, RF020, RF024 |
| `app/services/retriever.py` | RF001 a RF003, RF006, RF024 |
| `app/services/classifier.py` | RF005, RF022 |
| `app/services/ai_provider.py`, `prompts/*.txt` | RF021 a RF023, RF026, RF027, RF035 |
| `analysis_service.pacote_copilot` / `aplicar_resposta_copilot` | RF033 a RF037, RF039 |
| `app/services/report_generator.py` | RF007, RF009, RF015 |
| `app/services/docx_generator.py`, `templates/*.docx` | RF010, RF018, RF019 |
| `app/services/analysis_service.py`, `app/api/routes.py` | RF013, RF017 |
| `app/services/metrics_service.py` | RF025 |
| `gerador-parecer-conflito.html` | RF008, RF010, RF014 a RF016, RF031 |
