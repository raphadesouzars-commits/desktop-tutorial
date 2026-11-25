# Análise de Riscos e Controles do AICI

**Versão 0.3 - novembro/2026.** Análise de riscos **do projeto** feita pela equipe de concepção. Ela **não substitui** a Análise de Riscos específica do Copilot Chat conduzida pela área de tecnologia, cujo cumprimento integral é condição da autorização do CTSI (comunicado de 24/06/2026). Quando a TI entregar essa análise, este documento deve ser reconciliado com ela (item 5).

Escalas: probabilidade (B baixa, M média, A alta) e impacto (B, M, A). Exposição = combinação das duas.

## 1. Registro de riscos

| # | Risco | Causa | P | I | Controles existentes | Controles a implantar | Dono |
|---|---|---|---|---|---|---|---|
| 1 | Vazamento de dados pessoais ou sigilosos do servidor | Texto da consulta enviado a serviço não autorizado ou exposto em arquivo | M | A | Mascaramento de CPF, matrícula, telefone, e-mail e nome; modo sem IA; dados fora do git; escuta local; token | Controles da Análise de Riscos; criptografia em repouso; retenção e descarte; autenticação por usuário; ambiente institucional | Cotec / Concepção |
| 2 | Uso de IA não homologada (cola em outro serviço ou conta pessoal) | Fluxo manual de copiar e colar | M | A | Aviso na tela; link ao Copilot Chat corporativo; provedor `openai` bloqueado | Orientação e treinamento; controles de TI (bloqueio de outras IAs, DLP) | Cotec / COGER |
| 3 | Alucinação: fundamento ou precedente inexistente | Limitação dos modelos generativos | M | A | Contexto restrito ao acervo; fontes obrigatórias e validadas; descarte de parágrafo sem fonte; só vale citar o que foi enviado; revisão humana | Medição de acurácia no piloto; amostragem pelo curador | Curador |
| 4 | Conclusão errada aceita sem crítica (excesso de confiança) | Viés de automação | M | A | Validação humana obrigatória (tela e API); avisos de baixa confiança; aviso quando a conclusão difere do modelo; revisão de consistência | Treinamento; auditoria por amostragem | COGER / Curador |
| 5 | Precedente desatualizado ou revogado orientar a análise | Acervo sem controle de vigência | M | A | Normativos com vigência verificada na carga (ex.: Portaria CGU 57/2019 revogada pela 234/2025); regras de negócio RN026 e RN027 | Status de validação por documento; rotina de revisão da base; prioridade aos entendimentos recentes | Coordenação |
| 6 | Entendimentos divergentes ou conflitantes na base | Pareceres de épocas diferentes | M | M | Peso maior para a COGER; origem sempre exibida | Seção "A consolidar" de `regras_coger.md`; validação pela Coordenação | Coordenação |
| 7 | Viés ou tratamento desigual entre casos semelhantes | Base e modelos refletirem práticas passadas | B | A | Resultado ancorado em precedentes visíveis; revisão humana | Avaliação de vieses pelo curador | Curador |
| 8 | Classificação errada da atividade | Busca por palavras limitada | M | M | Confiança e candidatas exibidas; usuário confirma ou escolhe; categoria fora da lista descartada | Busca semântica; medição da acurácia (meta ≥ 85%) | Concepção |
| 9 | Prompt maior que o limite do Copilot Chat | Limite do chat desconhecido | A | M | Limite configurável; contexto repartido; prompt curto + arquivo; aviso do que ficou de fora | Confirmar o limite real com a TI | Cotec |
| 10 | Acesso indevido ao serviço ou aos dados | Exposição em rede sem autenticação | B | A | Escuta local por padrão; token; CORS restrito; validação de upload | HTTPS e autenticação institucional; perfis; teste de segurança | Cotec |
| 11 | Perda ou alteração de registros de auditoria | Arquivos locais sem proteção | M | M | Registros em `.jsonl`, separados por tipo | Armazenamento institucional com proteção contra alteração; cópia de segurança | Cotec |
| 12 | Indisponibilidade do serviço | Falha do servidor ou do Copilot | M | B | Gerador HTML funciona sem o motor; motor funciona sem IA; fallback automático | Supervisão e reinício automático; rotina de cópia | Cotec |
| 13 | Dependência de uma pessoa | Concepção e manutenção concentradas | M | M | Documentação, testes automatizados, conhecimento em arquivos | Ponto focal da TI; transferência de conhecimento | Patrocinador |
| 14 | Dependências de software vulneráveis | Bibliotecas de terceiros | M | M | Dependências mínimas e conhecidas | Varredura de vulnerabilidades; política de atualização | Cotec |
| 15 | Texto livre do servidor conter dados que o mascaramento não alcança | Mascaramento por padrões | M | M | Aviso nas limitações; auditoria | Decisão da TI sobre o mascaramento; orientação ao parecerista | Cotec / COGER |
| 17 | No modo local, o parecer sair sem revisão suficiente (sem bloqueio técnico) e sem consulta à biblioteca de pareceres | Modo sem motor | M | M | Conferência de coerência com aviso de texto do Copilot; fontes validadas; precedentes da CGU; Manual do Usuário | Avaliar com a Cotec bloqueio equivalente; levar a biblioteca ao modo local (arquivo exportado) | Concepção / Cotec |
| 18 | Índice da biblioteca (trechos de pareceres, com dados pessoais) guardado no navegador do usuário e a pasta sincronizada no computador | Conexão da biblioteca no modo local | M | A | Dados ficam na estação institucional; botão "Esquecer biblioteca"; nomes de servidores mascarados no prompt | Confirmar com a TI se a sincronização e o armazenamento no navegador são permitidos; criptografia de disco; política de retenção | Cotec |
| 19 | Etapa 1 do Copilot sugerir atividade, incisos ou termos errados e o usuário aceitar sem crítica; caso exposto em duas rodadas | Fluxo em duas etapas | M | M | Validação da resposta (lista fechada, incisos válidos, termos saneados); sugestões só por ação do usuário; termos editáveis; etapa opcional; mascaramento nas duas etapas | Medir o ganho no piloto; incluir as duas rodadas na avaliação da TI | Concepção / Cotec |
| 16 | Parecer emitido em desacordo com o modelo institucional | Alteração indevida de templates | B | M | Templates e textos institucionais em arquivos controlados | Controle de acesso a `templates/` e `institucional.json` | Coordenação |

## 2. Matriz de exposição

| | Impacto B | Impacto M | Impacto A |
|---|---|---|---|
| **P alta** | | 9 | |
| **P média** | 12 | 6, 8, 11, 13, 14, 15, 17, 19 | 1, 2, 3, 4, 5, 18 |

| **P baixa** | | 16 | 7, 10 |

Prioridade de tratamento: 1 a 5 (impacto alto e probabilidade média), seguidos de 9.

## 3. Mapeamento dos controles técnicos já implementados

| Controle | Onde | Riscos mitigados |
|---|---|---|
| Modo sem IA e fallback | `OfflineProvider`; `report_generator` | 1, 12 |
| Mascaramento de identificadores | `utilities/text.anonimizar` | 1, 15 |
| Contexto restrito ao acervo | `montar_contexto`; `prompts/reasoning.txt` | 3, 5 |
| Fontes obrigatórias e validadas | `interpretar_fundamentacao` | 3 |
| Só citar o que foi enviado | Filtro do mapa de marcadores | 3 |
| Categorias fechadas | `classifier` | 3, 8 |
| Validação humana obrigatória | API e interface | 3, 4 |
| Avisos de confiança e de divergência | Classificação, minuta, conferência | 4, 8 |
| Trilha de auditoria | `ia_auditoria.jsonl`, `metricas.jsonl` | 3, 4, 7 |
| Token, CORS, validação de upload, escuta local | `main.py`, `routes.py`, `analysis_service.py` | 10 |
| Dados fora do controle de versão | `.gitignore` | 1 |

## 4. Indicadores de risco a acompanhar no piloto

| Indicador | Meta | Fonte |
|---|---|---|
| Parágrafos de IA descartados por fonte inválida (% do total) | Acompanhar; alta taxa indica problema no prompt ou no modelo | Avisos da minuta; auditoria |
| Respostas coladas recusadas por formato inválido | Acompanhar | Auditoria |
| Pareceres com conclusão alterada em relação à sugestão | Acompanhar (mostra o juízo crítico do parecerista) | Indicadores |
| Ocorrências de alucinação ou viés comunicadas | Zero ocorrências graves sem tratamento | Canal da Cotec |
| Incidentes de segurança | Zero | Segurança da informação |

## 5. Reconciliação com a Análise de Riscos da Cotec

| Passo | Responsável |
|---|---|
| Receber a Análise de Riscos específica do Copilot Chat e a lista de controles e tratamentos | Cotec |
| Para cada controle, registrar neste documento: atendido / parcialmente / não atendido, a evidência e o plano | Concepção |
| Incluir os controles novos como requisitos não funcionais (RNF037) | Concepção |
| Submeter o resultado ao curador e à Cotec | Concepção |
| Atualizar o Documento 05 (art. 16) | Concepção |

| Controle da Análise de Riscos | Situação no AICI | Evidência | Plano |
|---|---|---|---|
| [a preencher quando recebida] | | | |
