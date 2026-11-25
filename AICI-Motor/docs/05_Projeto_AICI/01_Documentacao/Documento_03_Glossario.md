# Glossário

**Versão 0.3 - novembro/2026**

## 1. Negócio

| Termo | Definição |
|---|---|
| AICI | Assistente Inteligente para Conflitos de Interesse |
| AICI-Motor | Componente em Python que lê o PDF, pesquisa a base e monta a minuta; o gerador HTML é a interface |
| Coger / GNP | Corregedoria da Receita Federal / Grupo Nacional dos Pareceristas, sigla usada na numeração dos pareceres ("Parecer Coger/GNP nº 522/2023") |
| Conflito de interesses | Situação gerada pelo confronto entre interesses públicos e privados que possa comprometer o interesse coletivo ou influenciar, de maneira imprópria, o desempenho da função pública (Lei nº 12.813/2013, art. 3º, I) |
| Consulta | Pergunta do servidor sobre risco de conflito de interesses |
| Pedido de autorização | Solicitação para exercer atividade privada de natureza continuada (Portaria Interministerial nº 333/2013) |
| SeCI | Sistema Eletrônico de Prevenção de Conflito de Interesses, da CGU, por onde o servidor formula consultas e pedidos |
| CGU | Controladoria-Geral da União |
| Parecer | Documento conclusivo da análise |
| Minuta | Rascunho de parecer gerado pelo AICI, sujeito à revisão do parecerista |
| Precedente | Parecer anteriormente utilizado como referência (da COGER ou da CGU) |
| PA / PAR | Prefixo do número do parecer nos nomes de arquivo e nos modelos (ex.: PA_211_2026, PAR 265/2020) |
| Conhecimento institucional | Conjunto de decisões, fundamentos e entendimentos acumulados |
| Modelo institucional | Texto-base de uma atividade (fundamentos e conclusão) extraído de pareceres reais; há 68 atividades e 163 situações |
| Atividade / categoria | Tipo de atividade privada (docência, advocacia, síndico etc.); lista fechada, usada pelo classificador |
| Situação (variante) | Cada conclusão modelada para uma atividade (ex.: docência com compatibilidade de horários) |
| Resultado | Conclusão do parecer: `sem_conflito`, `sem_conflito_ressalvas`, `conflito` ou `outro` |
| Ressalva | Condição imposta à autorização (ex.: não usar informação privilegiada, respeitar a compatibilidade de horários) |
| Termo de Compromisso | Documento pelo qual o servidor se obriga a cumprir as ressalvas perante a Comissão de Ética e a chefia; gerado nas autorizações com ressalvas |
| Despacho | Documento de encaminhamento do processo |
| Comissão de Ética da RFB | Destinatária dos pareceres e dos Termos de Compromisso |
| Siape | Sistema de cadastro de pessoal; a matrícula Siape identifica o servidor |
| Regras da COGER | Documento `knowledge/regras_coger.md` com princípios, categorias, estrutura e compromissos, sempre enviado à IA |

## 2. Governança de IA (Portaria RFB nº 647/2026)

| Termo | Definição |
|---|---|
| Política de IA | Portaria RFB nº 647/2026: diretrizes, limites e salvaguardas para o uso de IA na RFB |
| Cotec | Coordenação-Geral de Tecnologia da Informação; faz a governança tecnológica de IA |
| CTSI | Comitê de Tecnologia e Segurança da Informação; delibera sobre casos de uso de IA (autorizou o Copilot Chat na 3ª Reunião Ordinária de 2026, em 18/06) |
| Curador | Responsável por monitorar continuamente as respostas de uma solução de IA generativa (art. 12) |
| IA homologada | IA desenvolvida, contratada ou homologada pela RFB, usada em ambiente seguro e sob sua governança (art. 15) |
| Soberania | Maior grau de controle institucional sobre os modelos, com preferência por ambientes sob governança da RFB (art. 14) |
| Acurácia aceitável | Nível de qualidade que a área de negócio define para o caso de uso (art. 11) |
| Alucinação | Resposta plausível, mas sem base real (ex.: citar parecer ou artigo inexistente) |

## 3. Inteligência artificial e busca

| Termo | Definição |
|---|---|
| IA | Inteligência Artificial |
| IA generativa | Modelo que produz texto a partir de instruções (prompts) |
| Copilot Chat | Assistente de IA generativa conversacional integrado ao Microsoft 365, acessível pela conta corporativa da RFB, disponível aos usuários da licença E5 e homologado pela Cotec; uso aprovado pelo CTSI em 18/06/2026, inclusive com dados protegidos por sigilo legal, condicionado aos controles da Análise de Riscos |
| Copilot (genérico) | Nome comercial de ferramentas de IA da Microsoft; neste projeto, "Copilot" significa o Copilot Chat da RFB |
| Modo assistido | Forma de usar o Copilot Chat sem API: o AICI gera o prompt e o contexto, o parecerista os leva ao chat e cola a resposta de volta, que o AICI valida contra o acervo |
| Prompt curto / arquivo de contexto | Alternativa ao prompt completo: o prompt traz só as instruções e o contexto vai em um arquivo (`contexto_AICI.md`) anexado ao chat |
| Análise de Riscos específica | Estudo da área de tecnologia que identifica os controles e tratamentos de segurança exigidos para usar o Copilot Chat; condição da autorização do CTSI |
| NT Cotec | Nota Técnica da Coordenação-Geral de Tecnologia da Informação; uma delas homologa o Copilot Chat |
| Licença E5 | Licença Microsoft 365 em que o Copilot Chat está disponível aos usuários da RFB |
| Copilot Studio | Plataforma Microsoft para construir agentes, que podem ser publicados por HTTPS |
| Azure OpenAI | Serviço corporativo de modelos de linguagem na nuvem Microsoft, acessado por endpoint, deployment e chave |
| Provedor de IA (provider) | Classe do AICI que fala com um serviço de IA específico; o restante do sistema não sabe qual é |
| Provedor offline | Modo sem IA: a minuta sai dos modelos institucionais |
| Prompt | Instrução enviada à IA; ficam em `prompts/*.txt` |
| RAG | Geração aumentada por recuperação: a IA responde com base em trechos recuperados do acervo |
| BM25 | Algoritmo de busca por palavras, com peso maior para termos raros |
| Embedding | Representação numérica do sentido de um texto; permite achar "docência" a partir de "professor universitário" |
| Busca híbrida | BM25 + embeddings, com fusão e reclassificação |
| RRF | Reciprocal Rank Fusion: método de fusão de duas listas ordenadas |
| bge-m3, multilingual-e5-large | Modelos de embeddings multilíngues, executáveis localmente |
| Chunk | Trecho de um documento indexado (cerca de 1.200 caracteres) |
| Índice / vectorstore | Estrutura onde ficam os trechos e os vetores para busca |
| ChromaDB | Banco vetorial local opcional |
| Mascaramento | Substituição de CPF, matrícula, telefone, e-mail e nome por marcadores antes do envio à IA |
| Base de conhecimento | Repositório estruturado de documentos e metadados (`knowledge/`) |

## 4. Técnico

| Termo | Definição |
|---|---|
| API | Interface HTTP do motor (`/upload`, `/analisar`, `/minuta`, `/gerar-parecer`, `/revisar`, `/indicadores`, `/indexar`, `/saude`, `/categorias`) |
| FastAPI | Framework Python da API |
| OCR | Reconhecimento óptico de caracteres, usado em PDF digitalizado (EasyOCR, opcional) |
| DOCX | Formato Word; gerado a partir dos modelos em `templates/` |
| SQLite | Banco operacional inicial (consultas, pareceres, métricas); migrável para PostgreSQL |
| CORS | Regra do navegador que permite ao HTML falar com o motor; restrita às origens configuradas |
| Trilha de auditoria | Registros de análises, métricas e chamadas à IA (`metrics/`) |
| SharePoint | Repositório documental da biblioteca da COGER |
| M365 | Microsoft 365 |
| MoSCoW | Prioridade: Must (deve), Should (deveria), Could (poderia), Won't (não nesta fase) |
