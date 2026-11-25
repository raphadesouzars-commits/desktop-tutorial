# Regras de Negócio - v02

**Versão 0.3 - novembro/2026.** Substitui a v01. "Aplicada em" indica onde a regra é imposta (código, configuração ou orientação).

## 1. Princípios (RN001 a RN006, mantidas)

| ID | Regra | Aplicada em | Situação |
|---|---|---|---|
| RN001 | A decisão final pertence ao parecerista | Geração bloqueada sem `validado=true` (tela e API); resultado e atividade escolhidos pelo usuário | Implementada |
| RN002 | A IA possui caráter consultivo | A resposta da IA só entra na minuta após validação e revisão humana | Implementada |
| RN003 | Toda sugestão deve ser validada | Validação de fontes e de formato; revisão de consistência; confirmação humana | Implementada |
| RN004 | Os documentos institucionais têm prioridade sobre conhecimento externo | A IA recebe só o acervo; instrução em `prompts/reasoning.txt`; `regras_coger.md` sempre no contexto | Implementada |
| RN005 | Os precedentes da COGER possuem maior peso interpretativo | `recuperacao.peso_coger` (1,25) para pareceres, precedentes e modelos de origem COGER | Implementada |
| RN006 | Nenhum documento será alterado automaticamente pela IA | O motor só lê `knowledge/`; saídas vão para `output/` | Implementada |

## 2. Regras adicionais

### 2.1 Uso da IA

| ID | Regra | Aplicada em | Situação |
|---|---|---|---|
| RN007 | A IA nunca recebe apenas o caso: o contexto leva sempre normativos e, ao menos, precedentes, pareceres ou modelos | `montar_contexto` (levanta `ContextoInsuficiente`) | Implementada |
| RN008 | Todo parágrafo de IA precisa citar ao menos uma fonte válida do contexto; sem isso, é descartado | `interpretar_fundamentacao` | Implementada |
| RN009 | Só vale citar o que a IA efetivamente recebeu (no modo assistido, o que coube no prompt) | Mapa de marcadores filtrado pelo contexto enviado | Implementada |
| RN010 | A IA não cria categorias de atividade: só escolhe entre as existentes | `classifier` | Implementada |
| RN011 | Dados de identificação (CPF, matrícula, telefone, e-mail, nome) são mascarados antes de ir à IA, salvo decisão da TI em contrário | `ia.anonimizar` (padrão ligado) | Implementada |
| RN012 | Usar somente a IA homologada: o Copilot Chat da conta corporativa da RFB | Aviso na tela; provedor `openai` bloqueado; padrão `offline` | Parcial (orientação) |
| RN013 | Toda interação com a IA (prompt gerado, resposta aplicada, chamada automática) é registrada para o curador | `metrics/ia_auditoria.jsonl` | Implementada |
| RN014 | Falha ou indisponibilidade da IA nunca impede a elaboração do parecer | Fallback para a minuta extrativa | Implementada |

### 2.2 Conteúdo do parecer

| ID | Regra | Aplicada em | Situação |
|---|---|---|---|
| RN015 | A estrutura do parecer é fixa: I - Relatório, II - Fundamentos, III - Conclusão | `report_generator` | Implementada |
| RN016 | O relatório reproduz as respostas 1 a 10 do formulário do SeCI | `report_generator._relatorio` | Implementada |
| RN017 | Em autorização com ressalvas (risco mitigável) a conclusão registra o Termo de Compromisso e o sistema habilita a geração do Termo | `institucional.json` (`termo_registro`); `/gerar-parecer` (`documento=termo`) | Implementada |
| RN018 | O Termo de Compromisso só é gerado para o resultado "sem conflito, com ressalvas" | `analysis_service.gerar_documento` | Implementada |
| RN019 | Em autorização, o parecer traz a lista de deveres (item 13 do Parecer Coger/GNP nº 522/2023) e o fecho de nova consulta em caso de alteração dos fatos | `institucional.json` | Implementada |
| RN020 | Resultado "conflito": encaminhar à Comissão de Ética para prosseguimento e remessa à CGU pelo SeCI (Portaria Interministerial nº 333/2013) | `institucional.json` (`encaminha_conflito`) | Implementada |
| RN021 | Se a conclusão escolhida difere da do modelo, o sistema avisa para revisar os fundamentos | `report_generator`; conferência no gerador | Implementada |
| RN022 | Consulta sobre atividade de natureza continuada é tratada como pedido de autorização (Portaria Interministerial nº 333/2013, art. 2º, II) | Gerador HTML (opção "converter") | Implementada (HTML) |
| RN023 | Campos que o sistema não consegue preencher aparecem entre colchetes e em amarelo no Word, nunca inventados | `report_generator.preencher`, `docx_generator` | Implementada |

### 2.3 Dados e acervo

| ID | Regra | Aplicada em | Situação |
|---|---|---|---|
| RN024 | Só PDF é aceito como consulta (assinatura `%PDF`), até 25 MB; o arquivo é salvo com nome aleatório | `analysis_service.receber_pdf` | Implementada |
| RN025 | Pareceres duplicados ou em revisão (`_Duplicados_Revisar`) ficam fora da base | `scripts/importar_biblioteca.py` | Implementada |
| RN026 | Normativo revogado não deve fundamentar parecer (ex.: a Portaria CGU nº 57/2019 foi revogada pela Portaria Normativa CGU nº 234/2025) | Governança da biblioteca; marcar vigência na planilha de metadados | Orientação |
| RN027 | Documento da biblioteca só recebe `UtilizarIA = Sim` após confirmação da vigência e do conteúdo | Planilha de metadados | Orientação |
| RN028 | `knowledge/pareceres` e `knowledge/precedentes` (dados pessoais) não vão para o controle de versão | `.gitignore` | Implementada |
| RN029 | Os princípios consolidados da COGER sem fonte em norma ou parecer devem ser registrados pela Coordenação em `regras_coger.md`, seção "A consolidar" | Governança | Orientação |
| RN030 | O índice é atualizado de forma incremental; arquivo corrompido não interrompe a indexação | `indexer` | Implementada |

### 2.4 Governança

| ID | Regra | Situação |
|---|---|---|
| RN031 | O uso de IA generativa exige curador, nível de acurácia aceitável e monitoramento contínuo (art. 11 da Portaria RFB nº 647/2026) | Pendente (designar curador e aprovar acurácia) |
| RN032 | O uso do Copilot Chat com dados protegidos exige a adoção integral dos controles da Análise de Riscos (condição da autorização do CTSI) | Pendente (obter a Análise de Riscos) |
| RN033 | Ocorrências de alucinação, viés ou desvio devem ser comunicadas ao canal oficial da Cotec | Pendente (canal a divulgar) |
| RN034 | O parecerista responde pelas informações que fornece à IA, por revisar o conteúdo e por justificar o uso (art. 17 da Portaria RFB nº 647/2026) | Orientação (Manual do Usuário) |
