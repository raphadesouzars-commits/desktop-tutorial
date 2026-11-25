# Requisitos Funcionais

**Versão 0.2 - novembro/2026**

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

### 2.3 Conhecimento, IA e gestão

| ID | Requisito | Prior. | Critério de aceite | Situação | Evidência / observação |
|---|---|---|---|---|---|
| RF020 | Indexar a biblioteca de forma incremental | M | Reprocessa só arquivos novos ou alterados e remove os excluídos; um arquivo corrompido não interrompe a indexação | Implementado | `indexer`; teste `test_indexacao_incremental` |
| RF021 | Enviar à IA sempre o caso **junto** com normativos, precedentes/pareceres/modelos e as regras da COGER | M | Sem normativos e sem precedentes/pareceres/modelos, a IA não é chamada | Implementado | `ai_provider.montar_contexto`; testes `test_ia_nunca_recebe_so_o_caso`, `test_regras_coger_sempre_no_contexto` |
| RF022 | Validar a resposta da IA contra o acervo | M | Categoria fora da lista é descartada; parágrafo sem fonte válida é descartado; falha da IA volta ao modo extrativo | Implementado | Testes `test_classificador_usa_so_categorias_do_html`, `test_ia_fundamentacao_com_fontes_validadas`, `test_ia_indisponivel_cai_no_extrativo` |
| RF023 | Permitir trocar de provedor de IA por configuração | M | `ia.provider`: offline, mock, copilot, azure, openai | Implementado (sem endpoint real) | `ai_provider`; teste `test_provedores_configuracao`. **Nenhum provedor real foi exercitado** |
| RF024 | Busca semântica por embeddings locais, combinada à busca por palavras | S | BM25 top 20 + vetores top 20, fusão (RRF) e reclassificação | Parcial | Mecanismo testado com embedder de teste (`test_busca_hibrida_acha_o_que_o_bm25_nao_acha`). **Nenhum modelo real (bge-m3 / e5) foi avaliado** |
| RF025 | Registrar indicadores | S | Cada parecer gerado grava atividade, resultado, precedente utilizado e data; `GET /indicadores` consolida | Implementado | `metrics_service`; teste `test_fluxo_completo_offline`. Sem painel gráfico |
| RF026 | Registrar cada chamada à IA (trilha para o curador) | M | Grava data, provedor, tamanho e, se configurado, o prompt e a resposta (já mascarados) | Implementado | `AuditedProvider`; teste `test_auditoria_das_chamadas_de_ia` |
| RF027 | Mascarar dados pessoais antes do envio à IA | M | CPF, matrícula, telefone, e-mail e nome do servidor substituídos por marcadores | Implementado | `utilities/text.anonimizar`; teste `test_ia_fundamentacao_com_fontes_validadas` |
| RF028 | Consultar a memória institucional em linguagem natural (resposta fundamentada com os documentos citados) | S | O usuário pergunta; o sistema pesquisa e responde com as fontes | Planejado | UC004 |
| RF029 | Sincronizar a biblioteca com o SharePoint | S | Sincronização automática e agendada | Planejado | Hoje, importação manual por script (`scripts/importar_biblioteca.py`) |
| RF030 | Catalogação assistida do acervo (status de cada documento: não processado, classificado, validado, utilizado) | C | Metadados e status por documento, com validação humana | Parcial | Planilha de metadados no Drive (coluna `Status_IA`); sem integração com o motor |
| RF031 | Atualizar os precedentes da CGU sobre a RFB | C | Rotina de atualização das ementas | Implementado | `parecer/atualizar_precedentes.py` (32 ementas embutidas no gerador) |
| RF032 | Painel de indicadores gerenciais | C | Visualização gráfica por atividade, resultado, precedente e período | Planejado | Hoje, tabelas simples na aba |

## 3. Resumo da situação

| Situação | Quantidade | Requisitos |
|---|---|---|
| Implementado | 25 | RF001, RF003, RF005 a RF023 (exceto os parciais), RF025 a RF027, RF031 |
| Parcial | 4 | RF002, RF004, RF024, RF030 |
| Planejado | 3 | RF028, RF029, RF032 |
| **Total** | **32** | |

"Implementado" significa que existe e foi testado em ambiente de desenvolvimento; não significa homologado nem validado com casos reais. O OCR (RF011) e os provedores reais de IA (RF023) estão implementados mas **não foram exercitados** contra serviços reais.

## 4. Matriz de rastreabilidade (RF -> componente)

| Componente | Requisitos atendidos |
|---|---|
| `app/services/pdf_reader.py`, `ocr_service.py` | RF011 |
| `app/services/fact_extractor.py` | RF004, RF012 |
| `app/services/indexer.py`, `embeddings.py` | RF001 a RF003, RF020, RF024 |
| `app/services/retriever.py` | RF001 a RF003, RF006, RF024 |
| `app/services/classifier.py` | RF005, RF022 |
| `app/services/ai_provider.py`, `prompts/*.txt` | RF021 a RF023, RF026, RF027 |
| `app/services/report_generator.py` | RF007, RF009, RF015 |
| `app/services/docx_generator.py`, `templates/*.docx` | RF010, RF018, RF019 |
| `app/services/analysis_service.py`, `app/api/routes.py` | RF013, RF017 |
| `app/services/metrics_service.py` | RF025 |
| `gerador-parecer-conflito.html` | RF008, RF010, RF014 a RF016, RF031 |
