# Plano de Implantação e Piloto

**Versão 0.3 - novembro/2026.** Prazos serão definidos com a Cotec e a COGER.

## 1. Estratégia

Implantação incremental e reversível. **O piloto pode começar sem Python**: o modo local da aba "Análise Inteligente" roda só no navegador; o motor entra quando a TI disponibilizar o ambiente. O gerador de pareceres continua sendo a ferramenta de produção; o motor entra como apoio, primeiro em **piloto restrito**, com os pareceristas decidindo e assinando como hoje. A IA (Copilot Chat) é opcional, em modo assistido.

| Fase | Escopo | Saída esperada |
|---|---|---|
| 0 - Pré-requisitos | Respostas da TI aos itens do Documento 04; Análise de Riscos recebida; curador designado; acurácia aprovada; ambiente definido | Marco M2 e M3 |
| 1 - Preparação | Carregar o acervo real; validar vigência dos normativos; preencher `regras_coger.md`; configurar o limite do prompt; treinar os usuários | Ambiente e base prontos |
| 2 - Piloto | Grupo restrito de pareceristas; casos reais; medição de métricas | Relatório do piloto |
| 3 - Decisão | Cotec e COGER decidem: expandir, ajustar ou encerrar | Marco M6 |
| 4 - Expansão | Demais pareceristas; operação contínua | Operação |

## 2. Pré-requisitos de entrada no piloto

| # | Pré-requisito | Responsável |
|---|---|---|
| 1 | Enquadramento do AICI confirmado pela Cotec (art. 10 da Portaria RFB nº 647/2026) | Cotec |
| 2 | Análise de Riscos do Copilot Chat recebida e controles aplicáveis ao AICI adotados | Cotec / Concepção |
| 3 | Curador designado e rotina de monitoramento definida | COGER / Cotec |
| 4 | Nível de acurácia aceitável aprovado | COGER |
| 5 | Ambiente de execução disponível e seguro (estação institucional ou servidor) | Cotec |
| 6 | Acervo carregado e indexado; normativos com vigência verificada | Coordenação / Concepção |
| 7 | Parecer de segurança e de proteção de dados | Cotec |
| 8 | Pareceristas do piloto treinados; Manual do Usuário entregue | Concepção |
| 9 | Limite de prompt do Copilot Chat confirmado e configurado | Cotec |

## 3. Composição e duração do piloto

- **Grupo:** pareceristas voluntários da Coger/GNP (número a definir) + coordenação + curador.
- **Casos:** consultas reais recebidas durante o piloto, processadas **em paralelo** ao fluxo atual (o parecerista elabora o parecer como de costume e usa o AICI como apoio, registrando o resultado da comparação).
- **Duração:** a definir; o critério é obter uma amostra suficiente para medir as metas (sugestão: pelo menos 30 consultas, cobrindo as atividades mais frequentes; o tamanho final deve ser definido com a Coordenação).

## 4. Medição das metas

| Métrica | Como medir | Meta |
|---|---|---|
| Classificação da atividade | % de casos em que a atividade sugerida (primeira candidata) coincide com a escolhida/confirmada pelo parecerista | ≥ 85% |
| Precisão dos precedentes | O parecerista marca, entre os 4 primeiros pareceres/precedentes, os que realmente aplicaria; precisão = marcados / apresentados | ≥ 80% |
| Tempo de localização | Tempo cronometrado para localizar os precedentes aplicáveis, com o AICI e sem (pesquisa manual) em amostra pareada | Redução > 50% |
| Satisfação | Questionário de 1 a 5 ao fim do piloto | ≥ 4 |
| Aproveitamento da minuta | % da minuta mantida sem alteração relevante (avaliação do parecerista) | Registrar |
| Qualidade da fundamentação do Copilot | % de parágrafos aproveitados; % descartados por fonte inválida; ocorrências de alucinação | Registrar (art. 11 e 12) |
| Segurança | Incidentes de segurança ou de vazamento | Zero |

**Registro:** formulário simples por caso (planilha) preenchido pelo parecerista, com: consulta (identificador), atividade sugerida/escolhida, precedentes marcados, tempo, observações, ocorrências. Os indicadores do motor (`/indicadores`) complementam.

## 5. Capacitação

Ver Plano do Projeto, item 7. Sessão de treinamento antes do piloto, com o Manual do Usuário, o fluxo de três etapas, o uso seguro do Copilot Chat e como comunicar ocorrências.

## 6. Operação durante o piloto

| Item | Prática |
|---|---|
| Suporte | Ponto focal da TI e da concepção; canal definido na abertura do piloto |
| Ocorrências de IA | Canal oficial da Cotec (a divulgar); registro no formulário do piloto |
| Revisões | Reunião quinzenal (modelo `ATA_PADRAO`) para analisar resultados, ocorrências e ajustes na base e nas regras |
| Mudanças | Ajustes de base, prompts e modelos feitos pela concepção com aval da Coordenação; testes automatizados antes de cada atualização |

## 7. Critérios de sucesso e de encerramento

**Sucesso:** metas atingidas em amostra representativa; nenhum incidente de segurança; curador e Cotec aprovam a continuidade.

**Ajuste:** metas de acurácia não atingidas, mas com causa identificada (base, prompts, busca): novo ciclo.

**Suspensão imediata** (por decisão da Cotec, art. 21 da Portaria RFB nº 647/2026): incidente de segurança, desvio relevante de desempenho ou uso indevido de dados.

## 8. Reversão (rollback)

O AICI é aditivo: para voltar ao estado anterior, basta usar o gerador de pareceres (aba 1, offline), que independe do motor. A IA pode ser desligada por configuração (`ia.provider: offline`; o modo assistido só existe se o usuário o acionar). Os documentos já gerados permanecem como arquivos Word comuns.

## 9. Evolução após o piloto

Busca semântica validada com casos reais; consulta à memória em linguagem natural; sincronização automática com o SharePoint; painel de indicadores; autenticação institucional e perfis; avaliação com a TI de agente publicado (por exemplo, Copilot Studio) ou API, para reduzir o copiar e colar.
