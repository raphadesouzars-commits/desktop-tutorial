# Resultados dos Testes Automatizados

**Execução:** `python -m pytest -q` na pasta `AICI-Motor` - **22 testes, 22 aprovados, 0 falhas** (ambiente de desenvolvimento: Linux, Python 3.13; novembro/2026).
Os testes usam arquivos temporários e dados **sintéticos** (formulário SeCI fabricado, pareceres de exemplo, embedder e provedor de IA simulados). Não usam o acervo real, nem o Copilot, nem modelos de embeddings reais, nem OCR.

| Teste | O que verifica | Requisitos |
|---|---|---|
| `test_pdf_texto_e_limpeza` | Leitor de PDF | RF011 |
| `test_pdf_sem_texto_avisa_ocr_ausente` | PDF sem texto e OCR ausente | RF011 |
| `test_extrator_formulario_seci` | Extração de fatos do formulário SeCI | RF004, RF012 |
| `test_indexacao_incremental` | Indexação incremental | RF020, RNF023 |
| `test_recuperacao_traz_origem_e_tipos` | Recuperação com origem e motivo | RF001, RF003, RF006 |
| `test_classificador_usa_so_categorias_do_html` | Classificador só usa categorias existentes | RF005, RF022, RNF017 |
| `test_sem_correspondencia_cai_no_generico` | Sem correspondência: modelo genérico | RF005 |
| `test_ia_nunca_recebe_so_o_caso` | A IA nunca recebe só o caso (contexto com marcadores, mascaramento) | RF021, RF027, RNF015 |
| `test_copilot_formatos_e_erros` | Provedor HTTP genérico: formatos e erros | RF023 |
| `test_fluxo_completo_offline` | Fluxo completo sem IA: upload, análise, Word, termo, despacho, indicadores | RF009, RF010, RF013, RF015, RF018, RF019, RF025 |
| `test_api_validacoes_e_token` | Validações da API e token | RNF008, RNF010 |
| `test_cors_do_html_aberto_como_arquivo` | CORS do HTML aberto como arquivo | RNF009 |
| `test_ia_fundamentacao_com_fontes_validadas` | IA automática: fontes validadas, descarte de parágrafo sem fonte, lacunas | RF022, RF027, RNF016 |
| `test_ia_indisponivel_cai_no_extrativo` | Falha da IA volta ao modo extrativo | RNF022 |
| `test_backend_chroma` | Backend vetorial Chroma | RF024 |
| `test_busca_hibrida_acha_o_que_o_bm25_nao_acha` | Busca híbrida BM25 + embeddings | RF024 |
| `test_provedores_configuracao` | Provedores Azure/OpenAI/Mock e fábrica | RF023, RNF002 |
| `test_regras_coger_sempre_no_contexto` | Regras da COGER sempre no contexto | RF021 |
| `test_geracao_exige_validacao_humana` | Geração exige validação humana | RF017, RNF006 |
| `test_auditoria_das_chamadas_de_ia` | Auditoria das chamadas à IA | RF026, RNF003 |
| `test_copilot_chat_assistido` | Modo assistido: prompt, resposta, validação, Word, auditoria | RF033 a RF039 |
| `test_pacote_respeita_limite_e_so_vale_citar_o_que_foi_enviado` | Limite do prompt e fontes que não couberam | RF035, RF036 |

## Verificações complementares (fora do pytest)

| Verificação | Resultado |
|---|---|
| Aba "Análise Inteligente" ponta a ponta no Chromium contra o motor real: teste de conexão, upload, análise, escolha de conclusão, Word, revisão, aplicar no gerador, indicadores, Copilot assistido (prompt, contexto, resposta válida, resposta inválida) | Sem erros |
| **Modo local** (sem motor) no Chromium: análise do PDF, fatos, atividade, prompt (7.500 caracteres, sem vazamento de nome, CPF ou matrícula), resposta com fonte válida e fonte inventada (a inventada descartada), nome do servidor reposto no texto, aviso na conferência, Word gerado, remoção e nova análise | Sem erros |
| Formulário real do SeCI (um exemplar): extração de servidor, cargo, matrícula, protocolo, respostas 1 a 10; classificação "conteúdo digital" | Correta |
| Word do motor convertido em PDF e conferido visualmente (cabeçalho, ementa, parágrafos numerados, deveres, conclusão, assinaturas, campos pendentes em amarelo) | Aderente ao padrão |
| Medições de tempo (base de 189 trechos, sem IA): leitura 0,02-0,03 s; análise 0,01-0,25 s; Word cerca de 0,1 s | Registradas (não representam o acervo real) |

## Lacunas de teste

Copilot Chat real (motor e modo local); modo local sem teste automatizado (só verificação no navegador); modelos de embeddings reais; OCR; carga com o acervo completo; Windows e Edge; segurança (varredura e intrusão); acurácia com casos reais (piloto).
