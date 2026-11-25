# Especificação Técnica e Solicitações à TI

**Projeto AICI - Assistente Inteligente para Conflitos de Interesse**
**Versão 0.3 - novembro/2026 - documento para análise da Cotec/TI**

---

## Parte A - Especificação técnica do protótipo

### A.1 Visão geral

O AICI tem dois componentes independentes:

| Componente | O que é | Onde roda |
|---|---|---|
| **Gerador de pareceres** (`gerador-parecer-conflito.html`) | Página HTML única (1,6 MB), sem dependências externas, com 68 atividades/163 situações embutidas, leitor de PDF e gerador de Word. Funciona offline | No navegador do parecerista |
| **AICI-Motor** (`AICI-Motor/`) | Serviço Python (FastAPI) que lê o PDF, extrai os fatos, pesquisa a base, classifica, monta a minuta e gera o Word. Consulta uma IA somente se configurada | Máquina local, servidor ou contêiner (a decidir) |

O gerador funciona sem o motor (e, no **modo local** da aba "Análise Inteligente", já analisa a consulta e prepara o prompt do Copilot Chat no navegador, sem instalar nada). O motor funciona sem IA. A IA é uma camada opcional e substituível.

**IA de referência: Copilot Chat da RFB.** Conforme o comunicado de 24/06/2026, o CTSI autorizou (18/06/2026) o uso do Copilot Chat, acessível pela conta corporativa e integrado ao Microsoft 365, inclusive com dados sob sigilo legal, condicionado aos controles da Análise de Riscos. Como o Copilot Chat é uma interface conversacional, sem API disponível ao AICI até onde se sabe, o AICI opera em **modo assistido**: gera o prompt e o contexto, o parecerista os leva ao chat e cola a resposta de volta, e o AICI a valida contra o acervo. A integração automática (API) fica como alternativa a avaliar com a TI.

### A.2 Arquitetura lógica

```
 Navegador (gerador HTML, aba "Análise Inteligente")
        |  HTTPS/HTTP (JSON, upload de PDF)           [token X-AICI-Token]
        v
 +------------------------ AICI-Motor (FastAPI) -------------------------+
 |  /upload -> pdf_reader (+ocr_service) -> texto                         |
 |  /analisar -> fact_extractor -> classifier -> retriever -> report      |
 |  /minuta, /gerar-parecer -> report_generator -> docx_generator         |
 |  /revisar, /indicadores, /indexar, /saude, /categorias                 |
 |                                                                        |
 |  Base de conhecimento (knowledge/)  <-  indexer  ->  índice            |
 |   pareceres | precedentes | normativos | modelos | regras_coger.md    |
 |                                                                        |
 |  Modo assistido: /ia/pacote (prompt + contexto) e /ia/resposta         |
 |   (validação de fontes) <-> parecerista <-> Copilot Chat (conta RFB)   |
 |  AIProvider  --(opcional, só se houver API)--> IA homologada           |
 |  SQLite (consultas, pareceres, metricas) | metrics/*.jsonl (auditoria) |
 +------------------------------------------------------------------------+
```

Fluxo de uma consulta: PDF -> texto (OCR se preciso) -> fatos -> classificação e recuperação (BM25 e, opcionalmente, embeddings) -> minuta extrativa a partir dos modelos -> (opcional) prompt para o Copilot Chat -> resposta colada e **validada contra o acervo** -> **validação humana** -> Word.

Contexto enviado ao Copilot Chat: caso (mascarado) + regras da COGER + normativos + precedentes + pareceres + modelos, cada trecho com um marcador citável ([R1], [N1], [P1], [A1], [M1]). O espaço é repartido entre os trechos para caber no limite de caracteres do chat; o que não coube não pode ser citado na resposta.

### A.3 Módulos

| Módulo | Arquivo | Função |
|---|---|---|
| Leitor de PDF | `pdf_reader.py` | Abrir, extrair texto, corrigir quebras, normalizar |
| OCR | `ocr_service.py` | OCR de páginas sem texto (EasyOCR, opcional) |
| Extrator de fatos | `fact_extractor.py` | Servidor, cargo, matrícula, protocolo, respostas 1 a 10; resumo por IA opcional |
| Indexador | `indexer.py`, `embeddings.py` | Lê, divide em trechos (~1.200 caracteres), indexa de forma incremental |
| Recuperação | `retriever.py` | BM25, opcionalmente fundido com embeddings (RRF), com peso maior para a COGER |
| Classificador | `classifier.py` | Escolhe entre as 68 categorias existentes, com confiança |
| IA | `ai_provider.py` | Contexto com marcadores e limite; provedores opcionais (`offline`, `mock`, `copilot`, `azure`, `openai`); resposta pré-obtida (modo assistido); auditoria |
| Prompts | `prompts/*.txt` | Instruções à IA (fatos, classificação, precedentes, raciocínio, minuta, revisão) |
| Minuta | `report_generator.py` | I - Relatório, II - Fundamentos, III - Conclusão |
| Word | `docx_generator.py`, `templates/*.docx` | Parecer, Termo de Compromisso, despacho |
| Indicadores | `metrics_service.py` | Registro e consolidação |
| Orquestrador | `analysis_service.py` | Coordena os módulos |

### A.4 API (principais rotas)

| Método | Rota | Função |
|---|---|---|
| POST | `/upload` | Recebe o PDF; devolve `consulta_id` |
| POST | `/analisar` | Fatos, enquadramento, normativos, precedentes, pareceres, minuta |
| POST | `/minuta` | Refaz a minuta com atividade e resultado escolhidos |
| POST | `/ia/pacote` | Modo assistido: prompt, prompt curto e arquivo de contexto para o Copilot Chat |
| POST | `/ia/resposta` | Modo assistido: valida a resposta colada e refaz a minuta |
| POST | `/gerar-parecer` | .docx (`documento`: parecer, termo ou despacho); exige `validado=true` |
| POST | `/revisar` | Revisão de consistência |
| GET | `/indicadores` | Consolidação por atividade, resultado, precedente e mês |
| POST | `/indexar` | (Re)indexa a base |
| GET | `/categorias`, `/saude` | Categorias; estado do serviço (provedor, índice, OCR, busca) |

Documentação interativa em `/docs` quando o serviço está em execução.

### A.5 Tecnologias e dependências

| Componente | Tecnologia | Uso | Obrigatória |
|---|---|---|---|
| Linguagem | Python 3.12+ (desenvolvido com 3.13) | Motor | Sim |
| API | FastAPI, Uvicorn, python-multipart, Pydantic | Serviço HTTP | Sim |
| PDF | PyMuPDF | Leitura de PDF | Sim |
| Word | python-docx | Geração de .docx | Sim |
| Configuração | PyYAML | `config/settings.yaml` | Sim |
| HTTP cliente | httpx | Chamadas ao provedor de IA | Sim |
| Banco | SQLite (nativo) | Operação; PostgreSQL como evolução | Sim |
| Testes | pytest | 22 testes automatizados | Desenvolvimento |
| Busca semântica | sentence-transformers, numpy (modelos `BAAI/bge-m3` ou `intfloat/multilingual-e5-large`) | Embeddings locais | Opcional |
| Vetores | ChromaDB | Backend vetorial alternativo | Opcional |
| OCR | EasyOCR (PyTorch, cerca de 2 GB) | PDF digitalizado | Opcional |

O gerador HTML embute o leitor de PDF (pdf.js, licença Apache-2.0).

### A.6 Dados tratados

| Dado | Onde fica | Contém dado pessoal | Observação |
|---|---|---|---|
| PDF e texto da consulta | `uploads/` | **Sim** (nome, CPF, matrícula, contatos, descrição da atividade) | Nome de arquivo aleatório |
| Análise e documentos gerados | `output/consulta_<id>/` | **Sim** | |
| Banco operacional | `metrics/aici.db` | Parcial (identificador da consulta, atividade, resultado) | |
| Métricas | `metrics/metricas.jsonl` | Não (atividade, resultado, precedente, data) | |
| Auditoria da IA | `metrics/ia_auditoria.jsonl` | Possível (prompts e respostas **já mascarados**, mas texto livre pode conter dados) | |
| Pareceres e precedentes | `knowledge/pareceres`, `knowledge/precedentes` | **Sim** | Fora do controle de versão |
| Normativos, modelos, regras da COGER | `knowledge/normativos`, `modelos`, `regras_coger.md` | Não | |
| Índice e vetores | `vectorstore/` | **Sim** (trechos dos pareceres) | |

Pendências de proteção de dados: criptografia em repouso, política de retenção e descarte, controle de acesso por perfil.

### A.7 Segurança implementada

- Escuta em `127.0.0.1` por padrão; exposição em rede só com proxy reverso institucional, HTTPS e token (`AICI_TOKEN`, cabeçalho `X-AICI-Token`, comparação em tempo constante).
- CORS restrito às origens configuradas (inclui `null` para o HTML aberto como arquivo).
- Upload: somente PDF (assinatura `%PDF`), máximo de 25 MB, salvo com nome aleatório (o nome enviado nunca vira caminho).
- Segredos (token da IA) apenas em variáveis de ambiente, nunca no arquivo de configuração.
- IA: contexto restrito ao acervo; mascaramento de CPF, matrícula, telefone, e-mail e nome; resposta validada; fontes obrigatórias; categoria fora da lista descartada; `openai` bloqueado sem confirmação de homologação.
- Revisão humana obrigatória para gerar documento (tela e API).
- Modo assistido: o AICI nunca envia dados a serviço algum; a resposta colada passa pela mesma validação de fontes da IA automática; pacote e resposta ficam na trilha de auditoria.
- Trilha de auditoria de cada chamada à IA (data, provedor, tamanho, prompt e resposta mascarados).

Não foi realizado teste de intrusão nem revisão de segurança por terceiros.

### A.8 Medições (ambiente de desenvolvimento)

Base de 189 trechos (163 modelos e 26 trechos normativos), sem IA, sem embeddings:

| Etapa | Tempo |
|---|---|
| Indexação completa | menos de 0,1 s |
| Leitura do PDF de 2 páginas | 0,02 a 0,03 s |
| Análise (fatos, classificação, recuperação, minuta) | 0,01 a 0,25 s |
| Geração do Word | cerca de 0,1 s |

Não representam o acervo completo nem o uso de IA/embeddings; o dimensionamento deve ser medido com o acervo real.

### A.9 Estimativa de infraestrutura (a confirmar)

| Cenário | Estimativa | Observação |
|---|---|---|
| Motor sem IA e sem embeddings | CPU e memória modestas (uma VM pequena) | Estimativa, não medida com o acervo |
| Com embeddings locais (bge-m3 ou e5-large) | Memória de 8 a 16 GB; CPU suficiente (GPU opcional); alguns GB de disco para o modelo | Estimativa; o tempo de indexação inicial depende do acervo |
| Com OCR (EasyOCR) | Disco de cerca de 2 GB, mais memória; processamento mais lento em CPU | Só para PDFs digitalizados |

### A.10 Opções de implantação

| Opção | Descrição | Prós | Contras |
|---|---|---|---|
| 0. Somente o HTML (modo local) | O parecerista abre o gerador no navegador; análise, prompt e validação da resposta ocorrem no navegador | Nada a instalar; dados não saem da estação | Sem biblioteca de pareceres da COGER e sem bloqueio técnico de revisão; acervo embutido limitado |
| 1. Estação institucional (piloto) | Cada parecerista roda o motor na própria estação | Dados não saem da estação; atende a solução experimental (art. 16, § 2º, a confirmar) | Instalação e manutenção por usuário |
| 2. Servidor/VM interno | Um serviço na rede interna, com proxy HTTPS e autenticação institucional | Centralizado; acervo e logs em um só lugar | Exige ambiente, segurança e operação da TI |
| 3. Contêiner (Docker/Kubernetes) | Imagem do motor, volumes para `knowledge/` e `metrics/` | Reprodutível e escalável | Depende da plataforma da RFB |
| 4. Azure (App Service/Functions) | Hospedagem em nuvem corporativa | Aderente ao M365 | Depende de avaliação de soberania (art. 14) |

### A.11 Limitações conhecidas

1. O modo assistido foi testado só com respostas simuladas; o Copilot Chat real não foi exercitado (formato JSON seguido, tamanho do prompt, comportamento com arquivo anexo). Nenhum provedor automático de IA foi exercitado.
1a. O AICI não controla onde o usuário cola o prompt (risco de uso de serviço não homologado).
1b. O modo local (sem motor) tem só o acervo embutido (instruções, regras, trechos de normativos, precedentes da CGU): não consulta a biblioteca de pareceres e não tem bloqueio técnico de revisão.
2. Nenhum modelo real de embeddings foi avaliado; a qualidade da busca semântica precisa ser medida.
3. O OCR não foi testado.
4. A acurácia da classificação e a precisão dos precedentes não foram medidas com casos reais.
5. Sem autenticação por usuário nem perfis; sem criptografia em repouso.
6. O acervo real (centenas de pareceres) ainda não foi carregado; a sincronização com o SharePoint é manual.
7. Validado em Linux/Chromium; Windows e Edge a validar.

### A.12 Qualidade

22 testes automatizados (pytest) cobrem: leitura de PDF, extração de fatos (formulário sintético e verificação com formulário real), indexação incremental, recuperação, classificação, contexto da IA, provedores (Copilot/Azure/OpenAI/Mock), busca híbrida, backend Chroma, fluxo completo da API, validações de upload, token, CORS, geração de Word, revisão humana obrigatória e auditoria.

---

## Parte B - Solicitações à TI

Peço o apoio da Cotec/TI para responder aos itens abaixo (31 itens). A coluna "Resposta da TI" pode ser preenchida diretamente neste documento.

### B.1 Governança e enquadramento

| # | Solicitação | Referência | Resposta da TI |
|---|---|---|---|
| 1 | Indicar a modalidade em que este desenvolvimento deve ser formalizado (sistema institucional, Modelo de Desenvolvimento Interno, solução experimental) e os documentos/aprovações exigidos | Portaria RFB/Sucor/Cotec nº 41/2017 | |
| 2 | Orientar a submissão do caso de uso à Cotec e ao CTSI | Port. RFB nº 647/2026, art. 10 | |
| 3 | Informar se o piloto sem IA exige submissão ou pode ocorrer como solução experimental em estação institucional | Art. 16, § 2º | |
| 4 | Indicar o procedimento para designação do curador e os requisitos do cargo | Arts. 11 e 12 | |
| 5 | Informar o canal oficial para comunicação de ocorrências de IA | Art. 18, parágrafo único | |
| 6 | Indicar o repositório de soluções de IA autorizadas a usar dados pessoais ou sigilosos e o procedimento para inclusão | Art. 16, § 1º | |
| 7 | Designar um ponto focal da TI | - | |

### B.2 Copilot Chat e IA

Contexto: o comunicado da RFB de 24/06/2026 informa que o CTSI autorizou o Copilot Chat (conta corporativa, licença E5), inclusive para dados sob sigilo legal, condicionado à adoção integral dos controles da Análise de Riscos.

| # | Solicitação | Resposta da TI |
|---|---|---|
| 8 | Enviar a **Análise de Riscos específica** do Copilot Chat (ou os controles e tratamentos de segurança dela decorrentes) para que o AICI os adote integralmente | |
| 9 | Informar o número e enviar a **NT Cotec** que homologa o Copilot Chat (o número não estava legível no comunicado) | |
| 10 | Confirmar se o uso do Copilot Chat **pelo AICI** (prompt gerado pelo sistema, resposta colada de volta) está coberto pela autorização do CTSI ou se exige submissão própria (art. 10 da Portaria RFB nº 647/2026) | |
| 11 | Informar o **limite de tamanho do prompt** do Copilot Chat e se aceita **arquivos anexos** (tipos, tamanho) e se o conteúdo anexado fica sob as mesmas garantias contratuais | |
| 12 | O mascaramento de CPF, matrícula, telefone, e-mail e nome continua exigido, ou os controles da Análise de Riscos o dispensam? | |
| 13 | Existe **acesso programático** ao Copilot (API, agente publicado no Copilot Studio, Power Automate/Graph) que a RFB possa autorizar? Se sim: endpoint, autenticação, formato, limites, registro de chamadas | |
| 14 | A RFB pode disponibilizar um **agente** (por exemplo, no Copilot Studio) com a biblioteca da COGER no SharePoint como fonte de conhecimento? Em caso afirmativo, quais as condições e quem o mantém | |
| 15 | Existe **curador** do Copilot Chat? Ele cobre o caso de uso do AICI (arts. 11 e 12)? Como ele acessa os registros de uso (prompts e respostas)? | |
| 16 | Como a TI controla que os dados de consultas sejam colados **somente** no Copilot Chat corporativo (bloqueio de outras IAs, DLP, orientação)? | |
| 17 | Há registro (log) do uso do Copilot Chat e política de retenção das conversas? As conversas podem conter dados sob sigilo e como devem ser descartadas? | |
| 18 | Canal oficial para comunicar ocorrências de IA (art. 18, parágrafo único) | |

### B.3 Ambiente

| # | Solicitação | Resposta da TI |
|---|---|---|
| 19 | Ambiente para executar o motor (estação, VM ou contêiner), Python 3.12 ou superior, com acesso pelos usuários da COGER via rede interna | |
| 20 | HTTPS e autenticação institucional na frente do serviço (proxy reverso); integração com a identidade da RFB e perfis (parecerista, coordenador, curador, administrador) | |
| 21 | Liberação de rede do servidor ao endpoint da IA | |
| 22 | Mecanismo para sincronizar a biblioteca do SharePoint (pasta sincronizada, Graph API ou rotina agendada), com leitura de `01_Pareceres_Emitidos`, `02_Precedentes`, `03_Normativos` e `04_Modelos_Institucionais` | |
| 23 | Autorização para instalar as dependências open source (item A.5) ou repositório interno de pacotes | |
| 24 | Cópia de segurança, retenção, criptografia em repouso e descarte de `uploads/`, `output/`, `metrics/` e `vectorstore/` | |
| 25 | Como a solução deve operar "no ambiente Microsoft 365" (RNF001): autenticação, hospedagem e interface | |

### B.4 Busca semântica e OCR (opcionais)

| # | Solicitação | Resposta da TI |
|---|---|---|
| 26 | Autorização para executar localmente um modelo de embeddings (`BAAI/bge-m3` ou `intfloat/multilingual-e5-large`), com download em máquina com internet e cópia para o servidor | |
| 27 | Disponibilidade de memória (8 a 16 GB) e, se houver, GPU | |
| 28 | Instalação do EasyOCR (PyTorch, cerca de 2 GB) para PDFs digitalizados | |

### B.5 Segurança e proteção de dados

| # | Solicitação | Resposta da TI |
|---|---|---|
| 29 | Parecer da segurança da informação sobre o desenho (Parte A) e o tratamento de dados pessoais e sigilosos | |
| 30 | Parecer de proteção de dados (LGPD) sobre uso do acervo de pareceres e das consultas | |
| 31 | Teste de segurança/varredura de vulnerabilidades do código e das dependências | |

## Parte C - Próximos passos propostos

1. Reunião de 30 a 45 minutos com a Cotec para apresentar a ferramenta e esclarecer os itens da Parte B.
2. Piloto restrito sem IA, em estação ou ambiente institucional, com casos reais, para medir as metas (precisão dos precedentes, acerto da classificação, tempo de pesquisa).
3. Em paralelo, tramitação do caso de uso (art. 10), designação do curador e definição da IA homologada.
4. Uso do Copilot Chat em modo assistido já no piloto; se a TI disponibilizar API ou agente, a integração automática entra pela camada `AIProvider`, sem alterar o restante do sistema.

## Anexos disponíveis

- `AICI-Motor.zip`: código, configuração, prompts, templates, testes e README.
- `gerador-parecer-conflito.html`: gerador de pareceres com a aba "Análise Inteligente".
- Documentos 01 a 03 do projeto e Documento 05 (conformidade).
- **Não** devem ser anexados pareceres reais nem PDFs de consultas (dados pessoais).
