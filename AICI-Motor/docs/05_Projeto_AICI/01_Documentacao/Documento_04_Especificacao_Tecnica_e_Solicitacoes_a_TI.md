# Especificação Técnica e Solicitações à TI

**Projeto AICI - Assistente Inteligente para Conflitos de Interesse**
**Versão 0.2 - novembro/2026 - documento para análise da Cotec/TI**

---

## Parte A - Especificação técnica do protótipo

### A.1 Visão geral

O AICI tem dois componentes independentes:

| Componente | O que é | Onde roda |
|---|---|---|
| **Gerador de pareceres** (`gerador-parecer-conflito.html`) | Página HTML única (1,6 MB), sem dependências externas, com 68 atividades/163 situações embutidas, leitor de PDF e gerador de Word. Funciona offline | No navegador do parecerista |
| **AICI-Motor** (`AICI-Motor/`) | Serviço Python (FastAPI) que lê o PDF, extrai os fatos, pesquisa a base, classifica, monta a minuta e gera o Word. Consulta uma IA somente se configurada | Máquina local, servidor ou contêiner (a decidir) |

O gerador funciona sem o motor. O motor funciona sem IA. A IA é uma camada opcional e substituível.

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
 |  AIProvider  --(opcional)-->  IA homologada (Copilot/Azure/outro)      |
 |  SQLite (consultas, pareceres, metricas) | metrics/*.jsonl (auditoria) |
 +------------------------------------------------------------------------+
```

Fluxo de uma consulta: PDF -> texto (OCR se preciso) -> fatos -> classificação e recuperação (BM25 e, opcionalmente, embeddings) -> montagem do contexto (caso + normativos + precedentes + pareceres + modelos + regras) -> minuta (extrativa ou com IA) -> **validação humana** -> Word.

### A.3 Módulos

| Módulo | Arquivo | Função |
|---|---|---|
| Leitor de PDF | `pdf_reader.py` | Abrir, extrair texto, corrigir quebras, normalizar |
| OCR | `ocr_service.py` | OCR de páginas sem texto (EasyOCR, opcional) |
| Extrator de fatos | `fact_extractor.py` | Servidor, cargo, matrícula, protocolo, respostas 1 a 10; resumo por IA opcional |
| Indexador | `indexer.py`, `embeddings.py` | Lê, divide em trechos (~1.200 caracteres), indexa de forma incremental |
| Recuperação | `retriever.py` | BM25, opcionalmente fundido com embeddings (RRF), com peso maior para a COGER |
| Classificador | `classifier.py` | Escolhe entre as 68 categorias existentes, com confiança |
| Provedores de IA | `ai_provider.py` | `offline`, `mock`, `copilot`, `azure`, `openai`; contexto; auditoria |
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
| Testes | pytest | 20 testes automatizados | Desenvolvimento |
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
| 1. Estação institucional (piloto) | Cada parecerista roda o motor na própria estação | Dados não saem da estação; atende a solução experimental (art. 16, § 2º, a confirmar) | Instalação e manutenção por usuário |
| 2. Servidor/VM interno | Um serviço na rede interna, com proxy HTTPS e autenticação institucional | Centralizado; acervo e logs em um só lugar | Exige ambiente, segurança e operação da TI |
| 3. Contêiner (Docker/Kubernetes) | Imagem do motor, volumes para `knowledge/` e `metrics/` | Reprodutível e escalável | Depende da plataforma da RFB |
| 4. Azure (App Service/Functions) | Hospedagem em nuvem corporativa | Aderente ao M365 | Depende de avaliação de soberania (art. 14) |

### A.11 Limitações conhecidas

1. Nenhum provedor real de IA foi exercitado; só `offline` e simulações.
2. Nenhum modelo real de embeddings foi avaliado; a qualidade da busca semântica precisa ser medida.
3. O OCR não foi testado.
4. A acurácia da classificação e a precisão dos precedentes não foram medidas com casos reais.
5. Sem autenticação por usuário nem perfis; sem criptografia em repouso.
6. O acervo real (centenas de pareceres) ainda não foi carregado; a sincronização com o SharePoint é manual.
7. Validado em Linux/Chromium; Windows e Edge a validar.

### A.12 Qualidade

20 testes automatizados (pytest) cobrem: leitura de PDF, extração de fatos (formulário sintético e verificação com formulário real), indexação incremental, recuperação, classificação, contexto da IA, provedores (Copilot/Azure/OpenAI/Mock), busca híbrida, backend Chroma, fluxo completo da API, validações de upload, token, CORS, geração de Word, revisão humana obrigatória e auditoria.

---

## Parte B - Solicitações à TI

Peço o apoio da Cotec/TI para responder aos itens abaixo. A coluna "Resposta da TI" pode ser preenchida diretamente neste documento.

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

### B.2 IA homologada

| # | Solicitação | Resposta da TI |
|---|---|---|
| 8 | Qual é a forma homologada de acesso a IA generativa por sistema (API) na RFB? **A**: Copilot apenas pelo chat (sem API) / **B**: Copilot Studio com publicação HTTPS / **C**: Azure OpenAI corporativo / **D**: outro modelo ou gateway interno | |
| 9 | Se houver API: endpoint (URL), modelo ou deployment, `api_version` (Azure), método de autenticação (chave, OAuth/Entra ID, certificado) e como obter as credenciais | |
| 10 | Formato de requisição e resposta (ou documentação técnica) | |
| 11 | Limites: tamanho de contexto, requisições por minuto, quotas e custos | |
| 12 | Registro (log) das chamadas e política de retenção; se os dados enviados são usados para treinamento | |
| 13 | Região/localização do processamento dos dados e avaliação de soberania | Art. 14 |
| 14 | Quais dados podem ser enviados (consulta do servidor, trechos de pareceres) e qual a classificação de sigilo permitida | Art. 16 |
| 15 | Se a resposta for "A" (somente chat): confirmação formal, pois o AICI seguirá em modo sem IA | |

### B.3 Ambiente

| # | Solicitação | Resposta da TI |
|---|---|---|
| 16 | Ambiente para executar o motor (estação, VM ou contêiner), Python 3.12 ou superior, com acesso pelos usuários da COGER via rede interna | |
| 17 | HTTPS e autenticação institucional na frente do serviço (proxy reverso); integração com a identidade da RFB e perfis (parecerista, coordenador, curador, administrador) | |
| 18 | Liberação de rede do servidor ao endpoint da IA | |
| 19 | Mecanismo para sincronizar a biblioteca do SharePoint (pasta sincronizada, Graph API ou rotina agendada), com leitura de `01_Pareceres_Emitidos`, `02_Precedentes`, `03_Normativos` e `04_Modelos_Institucionais` | |
| 20 | Autorização para instalar as dependências open source (item A.5) ou repositório interno de pacotes | |
| 21 | Cópia de segurança, retenção, criptografia em repouso e descarte de `uploads/`, `output/`, `metrics/` e `vectorstore/` | |
| 22 | Como a solução deve operar "no ambiente Microsoft 365" (RNF001): autenticação, hospedagem e interface | |

### B.4 Busca semântica e OCR (opcionais)

| # | Solicitação | Resposta da TI |
|---|---|---|
| 23 | Autorização para executar localmente um modelo de embeddings (`BAAI/bge-m3` ou `intfloat/multilingual-e5-large`), com download em máquina com internet e cópia para o servidor | |
| 24 | Disponibilidade de memória (8 a 16 GB) e, se houver, GPU | |
| 25 | Instalação do EasyOCR (PyTorch, cerca de 2 GB) para PDFs digitalizados | |

### B.5 Segurança e proteção de dados

| # | Solicitação | Resposta da TI |
|---|---|---|
| 26 | Parecer da segurança da informação sobre o desenho (Parte A) e o tratamento de dados pessoais e sigilosos | |
| 27 | Parecer de proteção de dados (LGPD) sobre uso do acervo de pareceres e das consultas | |
| 28 | Teste de segurança/varredura de vulnerabilidades do código e das dependências | |

## Parte C - Próximos passos propostos

1. Reunião de 30 a 45 minutos com a Cotec para apresentar a ferramenta e esclarecer os itens da Parte B.
2. Piloto restrito sem IA, em estação ou ambiente institucional, com casos reais, para medir as metas (precisão dos precedentes, acerto da classificação, tempo de pesquisa).
3. Em paralelo, tramitação do caso de uso (art. 10), designação do curador e definição da IA homologada.
4. Integração da IA homologada: basta preencher `ia.provider` e as credenciais em `config/settings.yaml`; o restante do sistema não muda.

## Anexos disponíveis

- `AICI-Motor.zip`: código, configuração, prompts, templates, testes e README.
- `gerador-parecer-conflito.html`: gerador de pareceres com a aba "Análise Inteligente".
- Documentos 01 a 03 do projeto e Documento 05 (conformidade).
- **Não** devem ser anexados pareceres reais nem PDFs de consultas (dados pessoais).
