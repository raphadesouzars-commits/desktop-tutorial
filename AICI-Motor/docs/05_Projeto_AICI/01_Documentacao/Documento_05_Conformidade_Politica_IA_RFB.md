# Matriz de Conformidade com a Política de IA da RFB

**Referência:** Portaria RFB nº 647, de 5 de fevereiro de 2026 (DOU de 12/02/2026) - Política de Inteligência Artificial da Secretaria Especial da Receita Federal do Brasil.
**Versão 0.2 - novembro/2026.** Análise feita pelo responsável pela concepção sobre o texto da Portaria disponível na biblioteca (`03_Normativos/Portarias`). Não substitui a análise da Cotec e do CTSI.

**Situação:** **Atendido** (há controle implementado e verificado), **Parcial**, **Pendente** (depende de ato da RFB/TI/área de negócio).

## 1. Matriz artigo a artigo

| Art. | Exigência (resumo) | Como o AICI atende | Situação | Falta |
|---|---|---|---|---|
| 4º, I | Autonomia e supervisão humana: a IA apoia, não substitui, a decisão | Minuta é sugestão; geração de documento bloqueada sem validação humana (tela e API); resultado e atividade são escolhidos pelo parecerista | Atendido | - |
| 4º, IV | Privacidade e proteção de dados, respeito ao sigilo legal | Mascaramento de identificadores antes do envio à IA; dados fora do controle de versão; modo sem IA | Parcial | Autorização do art. 16; parecer da segurança/proteção de dados; criptografia em repouso e retenção |
| 4º, V | Transparência, explicabilidade e auditabilidade | Origem de cada parágrafo; justificativa da similaridade; indicação de quando a minuta foi redigida com IA; trilha de auditoria | Atendido | Texto de transparência ao usuário final, se a Cotec exigir |
| 4º, VI | Segurança, resiliência e não maleficência | Falha da IA não impede o parecer (modo extrativo); validação de arquivos; token e CORS | Parcial | Parecer de segurança; ambiente de produção com HTTPS e autenticação institucional |
| 4º, III | Prevenção de vieses | Resultado sugerido ancorado em precedentes da COGER, com origem visível; revisão humana | Parcial | Avaliação de vieses pelo curador durante o piloto |
| 5º e parágrafo único | A decisão final e o ato administrativo competem exclusivamente ao agente público | O parecerista decide e assina; o AICI não assina nem emite ato | Atendido | - |
| 10 | Casos de uso de IA submetidos previamente à Cotec (análise técnica) e ao CTSI (deliberação); a área de negócio faz a análise de impacto e de riscos | Este conjunto de documentos descreve o caso de uso, os objetivos e os riscos iniciais | **Pendente** | **Submeter formalmente o caso de uso à Cotec**; concluir a análise de impacto e de riscos de negócio (parte do TAP) |
| 11 | IA generativa: controles adicionais, com **curador**, **nível de acurácia aceitável** e monitoramento contínuo | Metas propostas (≥ 80% precisão dos precedentes, ≥ 85% classificação); trilha de auditoria | **Pendente** | Designar o curador; a COGER definir e aprovar a acurácia aceitável; rotina de monitoramento |
| 12 | Atribuições do curador (monitorar respostas, alucinações, vieses, qualidade dos dados, evidências) e acesso a logs, prompts e saídas | `metrics/ia_auditoria.jsonl` registra cada chamada com prompt e resposta (mascarados); fontes obrigatórias reduzem alucinações | Parcial | Designação e treinamento do curador; ferramenta de consulta à trilha; definição de retenção |
| 13 | Requisitos no desenvolvimento e treinamento (inclui robustez e resiliência) | Não há treinamento de modelo; o acervo é usado apenas como contexto (RAG). Testes automatizados | Parcial | Avaliação da Cotec; o item exato do art. 13 deve ser confrontado pela equipe técnica |
| 14 | Priorizar soberania e controle institucional; modelos externos ou não soberanos exigem avaliação técnica da Cotec | Suporta embeddings e busca locais; provedor de IA configurável, sem dependência de um fornecedor | Pendente | A Cotec avaliar o provedor escolhido (especialmente Azure OpenAI/serviços externos) |
| 15 | Uso de IA restrito às soluções desenvolvidas, contratadas ou homologadas pela RFB, em ambiente seguro | O padrão é `offline`; provedor externo só com configuração explícita; `openai` bloqueado por padrão | Parcial | Indicar a IA homologada e o ambiente seguro de execução |
| 16 | **Inserção de dados pessoais e sigilosos em IA é vedada, salvo se expressamente autorizada**; solução experimental só em estação ou ambiente experimental institucional (§ 2º) | O mascaramento reduz a exposição; o modo sem IA não envia dados a nenhum serviço | **Pendente - crítico** | **Autorização expressa** da Cotec/RFB para uso de dados de consultas e de pareceres; ou piloto como solução experimental em estação institucional; inclusão no repositório de soluções autorizadas (§ 1º) |
| 17 | O usuário é responsável pelas informações fornecidas, por revisar e validar o conteúdo e por responder pelo uso | Validação humana obrigatória; avisos de baixa confiança e de conclusão divergente do modelo | Atendido | Orientação aos pareceristas (art. 22) |
| 18 | Comunicar alucinação, viés, desvio ou resultado incompatível ao canal oficial | Campo de revisão e avisos na tela | Parcial | A Cotec divulgar o canal oficial; incluir o link ou instrução na aba |
| 19 | Manter registros: autorização, descrição do problema, objetivos, avaliação de impacto, decisões técnicas, dados utilizados, incidentes | Este conjunto documenta problema, objetivos, decisões técnicas e riscos; código e testes versionados | Parcial | Registro no ambiente institucional da Cotec; avaliação de impacto; autorizações de dados (item VI); registro de incidentes |
| 20 | Monitoramento contínuo, avaliação periódica de desempenho/acurácia/vieses e sujeição a auditorias | Indicadores e trilha de auditoria | Parcial | Periodicidade e procedimentos serão definidos em normas complementares da Cotec |
| 21 | Incidentes implicam medidas corretivas ou suspensão, determinadas pela Cotec com a área de negócio | A IA é desligável por configuração (`provider: offline`) sem interromper o processo | Atendido | Procedimento formal de suspensão |
| 22 | Capacitação, orientação e conscientização | O fluxo em três etapas e os avisos orientam o uso | Pendente | Plano de capacitação dos pareceristas e do curador |

## 2. Conclusão da análise

1. **O AICI pode operar hoje sem IA** (provedor `offline`), sem enviar dados a nenhum serviço de IA; nesse modo as exigências específicas de IA generativa (arts. 10 a 12 e 16) não se aplicam ao uso do motor como busca e montagem de minuta a partir de modelos, o que deve ser confirmado pela Cotec.
2. **O uso de IA generativa depende de três atos externos ao projeto:** submissão do caso de uso à Cotec/CTSI (art. 10), designação do curador e definição da acurácia (arts. 11 e 12) e **autorização expressa para o tratamento de dados pessoais e sigilosos** (art. 16).
3. As salvaguardas técnicas implementadas (contexto restrito ao acervo, fontes obrigatórias, mascaramento, validação humana, trilha de auditoria, fallback) atendem aos princípios da Portaria, mas **não substituem** as aprovações acima.

## 3. Itens para a TI/Cotec deliberar

1. O enquadramento do AICI: o motor sem IA exige submissão à Cotec? E o piloto como solução experimental (art. 16, § 2º)?
2. Quais IAs estão autorizadas a receber dados pessoais ou sigilosos, e em que condições (repositório do art. 16, § 1º)?
3. A classificação de sigilo das consultas do SeCI e dos pareceres da COGER.
4. O canal oficial de comunicação de ocorrências (art. 18, parágrafo único).
5. Os procedimentos de monitoramento e auditoria (art. 20, parágrafo único).
