# Requisitos Não Funcionais

**Versão 0.3 - novembro/2026**

Situação: **Atendido** (existe e foi verificado), **Parcial**, **Em aberto** (depende de decisão ou ação da TI), **Planejado**.

## 1. Requisitos originais (RNF001 a RNF007)

| ID | Requisito | Verificação | Situação | Observação |
|---|---|---|---|---|
| RNF001 | A solução deverá operar no ambiente Microsoft 365 | Operação a partir do M365 (autenticação, repositório, interface) | **Parcial / em aberto** | A biblioteca já está no SharePoint e a IA é o Copilot Chat, integrado ao M365. O motor, porém, é um serviço Python que roda em servidor/VM/contêiner e a interface é um HTML. Opções a decidir com a TI: (a) serviço interno acessado por navegador com login institucional; (b) hospedagem em Azure (App Service/Functions); (c) outra integração M365 sugerida pela TI. Hoje a interface HTML funciona em qualquer navegador |
| RNF002 | Utilizar exclusivamente IA homologada pela Receita Federal | Nenhum dado enviado a provedor não homologado | **Atendido (com orientação)** | A IA de referência é o Copilot Chat da conta corporativa, homologado pela Cotec e autorizado pelo CTSI. O padrão do motor é `offline`; o AICI não envia nada sozinho a serviço de IA; o provedor `openai` é bloqueado por padrão. Como o uso do Copilot Chat é manual, a garantia de que o prompt vai ao chat corporativo depende de orientação do usuário (RNF038) |
| RNF003 | Permitir rastreabilidade das sugestões geradas | Cada parágrafo tem a origem; cada análise e cada chamada à IA ficam registradas | **Atendido** | Origem por parágrafo na minuta; `output/consulta_<id>/analise.json`; `metrics/metricas.jsonl`; `metrics/ia_auditoria.jsonl` (prompt e resposta mascarados). Teste `test_auditoria_das_chamadas_de_ia` |
| RNF004 | Permitir auditoria posterior | Registros imutáveis o suficiente, com data, atividade, resultado, precedente | **Parcial** | Os registros existem, mas o usuário é informado em campo livre, não por login institucional, e os arquivos não têm proteção contra alteração. Requer integração com a identidade da RFB e política de guarda |
| RNF005 | Preservar os modelos institucionais existentes | O Word gerado segue o padrão atual; os 68 modelos permanecem íntegros | **Atendido** | Modelos em `knowledge/modelos` e `templates/*.docx` editáveis pela instituição |
| RNF006 | Garantir revisão humana obrigatória | Geração bloqueada sem validação | **Atendido** | Bloqueio na tela e na API (HTTP 422). Teste `test_geracao_exige_validacao_humana` |
| RNF007 | Permitir evolução incremental sem interrupção do processo atual | O gerador atual continua funcionando sem o motor | **Atendido** | O HTML é independente do motor; a aba de análise é opcional; o motor funciona sem IA |

## 2. Requisitos adicionais

### 2.1 Segurança e privacidade

| ID | Requisito | Verificação | Situação | Observação |
|---|---|---|---|---|
| RNF008 | O motor deve escutar apenas na máquina local por padrão, e exigir token quando exposto em rede | Configuração `servidor.host`; variável `AICI_TOKEN` | **Atendido** | Padrão `127.0.0.1`. Para uso em rede: proxy reverso institucional com HTTPS e autenticação (item para a TI) |
| RNF009 | Restringir as origens que podem chamar a API (CORS) | Origens listadas em `settings.yaml` | **Atendido** | Teste `test_cors_do_html_aberto_como_arquivo` (origem estranha não recebe cabeçalho CORS) |
| RNF010 | Validar os arquivos enviados | Aceita só PDF (assinatura `%PDF`), até 25 MB, salvo com nome aleatório | **Atendido** | Teste `test_api_validacoes_e_token` |
| RNF011 | Mascarar identificadores antes de enviar dados à IA | CPF, matrícula, telefone, e-mail, nome | **Atendido (limitação)** | O mascaramento é por padrões e pelo nome do servidor; **não** garante a remoção de todo dado pessoal ou sigiloso que o servidor descreva em texto livre. Com a autorização do CTSI para o Copilot Chat (inclusive dados sob sigilo legal), ele passa a ser defesa adicional; a TI decide se continua obrigatório (Análise de Riscos) |
| RNF012 | Manter dados pessoais fora do controle de versão e em ambiente controlado | `uploads/`, `output/`, `metrics/`, `vectorstore/`, `knowledge/pareceres` e `knowledge/precedentes` ignorados pelo git | **Atendido** | Falta definir criptografia em repouso, retenção e descarte com a segurança da informação |
| RNF013 | Controle de acesso por perfil (parecerista, coordenador, curador, administrador) | Autenticação institucional e papéis | **Planejado** | Hoje, um único token compartilhado |
| RNF014 | Não depender de serviço externo para funcionar | Modo `offline` e busca por palavras sem download de modelos | **Atendido** | Rede fechada suportada; modelos de embeddings, se usados, devem ser copiados para o servidor |

### 2.2 Qualidade das respostas (IA)

| ID | Requisito | Verificação | Situação | Observação |
|---|---|---|---|---|
| RNF015 | A IA só usa o acervo fornecido | Contexto restrito a normativos, precedentes, pareceres, modelos e regras da COGER | **Atendido** | Instrução em `prompts/reasoning.txt`; teste `test_ia_nunca_recebe_so_o_caso` |
| RNF016 | Resposta sem fonte válida é descartada | Verificação de cada fonte citada | **Atendido** | Teste `test_ia_fundamentacao_com_fontes_validadas` |
| RNF017 | A IA não cria categorias | Lista fechada de categorias | **Atendido** | Teste `test_classificador_usa_so_categorias_do_html` |
| RNF018 | Níveis de acurácia aceitáveis definidos e monitorados | Metas: precisão dos precedentes ≥ 80%; classificação ≥ 85% | **Em aberto** | Metas propostas, ainda não medidas com casos reais; a medição é parte do piloto (art. 11 da Portaria RFB nº 647/2026) |
| RNF019 | Monitoramento contínuo por curador | Curador designado, acesso à trilha de auditoria | **Em aberto** | Trilha existe (RNF003, inclusive pacotes e respostas do Copilot Chat); falta designar o curador (ou verificar se o do Copilot Chat cobre o AICI) e definir a rotina |

### 2.3 Desempenho, disponibilidade e capacidade

| ID | Requisito | Verificação | Situação | Observação |
|---|---|---|---|---|
| RNF020 | Análise de uma consulta, sem IA, em poucos segundos | Medida em ambiente de desenvolvimento | **Atendido (medido em escala reduzida)** | Em base de 189 trechos (modelos e normativos): leitura do PDF 0,02 a 0,03 s; análise 0,01 a 0,25 s; geração do Word cerca de 0,1 s. **Não representa o acervo completo**: precisa ser remedido com o acervo real (centenas de pareceres) |
| RNF021 | Com IA, o tempo depende do provedor | Latência do provedor, limite de requisições | **Em aberto** | Depende do serviço; o motor tem tempo limite configurável (padrão 120 s) |
| RNF022 | Degradação graciosa: falha da IA não impede o parecer | Fallback para o modo extrativo | **Atendido** | Teste `test_ia_indisponivel_cai_no_extrativo` |
| RNF023 | Indexação incremental | Reprocessar só o que mudou | **Atendido** | Teste `test_indexacao_incremental` |
| RNF024 | Capacidade para o acervo da COGER | Indexar e consultar o acervo completo em tempo aceitável | **Em aberto** | A medir com o acervo real; o índice lexical é simples e adequado para milhares de trechos, a validar |
| RNF025 | Disponibilidade compatível com o uso diário | Serviço supervisionado, com reinício automático e cópia de segurança | **Planejado** | Depende do ambiente de produção (TI) |

### 2.4 Usabilidade, manutenção e portabilidade

| ID | Requisito | Verificação | Situação | Observação |
|---|---|---|---|---|
| RNF026 | Fluxo em três etapas: análise, validação humana, geração | Interface | **Atendido** | Aba "Análise Inteligente" |
| RNF027 | O documento gerado deve ser editável e destacar campos pendentes | Word com campos pendentes em amarelo | **Atendido** | |
| RNF028 | O conhecimento não fica no código | Atividades, textos, regras, prompts e modelos Word em arquivos | **Atendido** | `knowledge/`, `templates/`, `prompts/`, `config/` |
| RNF029 | Código testado e documentado | Testes automatizados; README; API documentada | **Atendido** | 20 testes automatizados; documentação automática da API em `/docs` |
| RNF030 | Trocar componentes sem reescrever o sistema | Provedor de IA, índice, banco | **Atendido** | Interface `AIProvider`; backends de índice (lexical/Chroma); camada de banco isolada (migração para PostgreSQL) |
| RNF031 | Portabilidade | Python 3.12 ou superior, Windows e Linux | **Parcial** | Desenvolvido e testado em Linux com Python 3.13; Windows a validar |
| RNF032 | Navegadores | Chrome/Edge atuais | **Parcial** | Verificado com Chromium; Edge a validar |

### 2.5 Conformidade

| ID | Requisito | Situação | Observação |
|---|---|---|---|
| RNF033 | Aderência à Política de IA da RFB (Portaria RFB nº 647/2026) | **Parcial** | Ver o Documento 05 (matriz de conformidade) |
| RNF036 | O limite de tamanho do prompt do Copilot Chat deve ser configurável e respeitado | **Atendido (valor a confirmar)** | `ia.copilot_chat.limite_caracteres`; o padrão de 7.500 caracteres é suposição e precisa ser confirmado com a TI |
| RNF037 | Adotar integralmente os controles e tratamentos de segurança da Análise de Riscos do Copilot Chat (condição da autorização do CTSI) | **Em aberto** | A Análise de Riscos ainda não foi recebida; este requisito será detalhado quando ela for obtida |
| RNF038 | O usuário deve usar apenas o Copilot Chat da conta corporativa | **Parcial** | Aviso na tela, link direto e orientação no Manual do Usuário; o AICI não tem como impedir que o texto seja colado em outro serviço, o que depende de controles da TI (bloqueio de acesso a outras IAs, DLP) |
| RNF034 | Proteção de dados pessoais (LGPD) e sigilo funcional | **Em aberto** | Parecer da segurança da informação e da proteção de dados |
| RNF035 | Aderência ao processo de desenvolvimento de sistemas institucionais (Portaria RFB/Sucor/Cotec nº 41/2017) | **Em aberto** | A Cotec deve indicar o enquadramento e os documentos exigidos |

## 3. Pontos que dependem da TI

RNF001, RNF004, RNF013, RNF021, RNF024, RNF025, RNF031/032 (validação em ambiente real), RNF034, RNF035, RNF036 (confirmação do limite), RNF037 e RNF038. Ver a lista de solicitações no Documento 04.
