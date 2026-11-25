# Arquitetura Lógica - v02

**Versão 0.3 - novembro/2026.** Substitui a v01. Detalhes de infraestrutura, dependências e solicitações à TI: Documento 04.

## 1. Princípio

**O conhecimento não fica no código.** O código orquestra; o conhecimento fica em arquivos (biblioteca, modelos, regras, prompts, templates) que a instituição edita.

```
Biblioteca (SharePoint)
        |  importação / sincronização
        v
Base de Conhecimento (knowledge/)  ->  Indexador  ->  Índice (BM25 [+ vetores])
        |                                                  |
        |                                           Recuperação (RAG)
        v                                                  v
Regras da COGER + Modelos  ------>  Montagem de contexto (marcadores citáveis)
                                                           |
                       +-----------------------------------+-----------------------------+
                       v                                                                 v
        Minuta extrativa (modelos)                              Modo assistido: prompt -> Copilot Chat (conta RFB)
                       |                                                    -> resposta colada -> validação de fontes
                       +----------------------------+----------------------------------+
                                                    v
                                     Validação humana obrigatória
                                                    v
                          Gerador de documentos (Word: parecer, termo, despacho)
```

## 2. Camadas e componentes

| Camada | Componentes | Responsabilidade |
|---|---|---|
| Apresentação | Gerador HTML (offline) + aba "Análise Inteligente" | Interface do parecerista; leitura de PDF no navegador; geração de Word editável |
| API | FastAPI (`app/api/routes.py`) | 11 rotas, autenticação por token, CORS restrito |
| Serviços | `analysis_service` (orquestra), `pdf_reader`, `ocr_service`, `fact_extractor`, `classifier`, `retriever`, `indexer`, `embeddings`, `report_generator`, `docx_generator`, `metrics_service`, `ai_provider` | Regras do processo |
| Modelos | `schemas.py` (Pydantic), `db.py` (SQLite) | Contratos e persistência |
| Conhecimento | `knowledge/`, `templates/`, `prompts/`, `config/` | Dados editáveis |
| Operação | `uploads/`, `output/`, `metrics/`, `vectorstore/` | Dados da operação, trilha de auditoria |

## 3. Fluxos

### 3.1 Análise (UC005)
`/upload` (valida, extrai texto, grava) -> `/analisar` (fatos -> pré-classificação -> recuperação -> classificação final com votos dos modelos -> minuta extrativa -> grava `analise.json`).

### 3.2 Modo assistido (UC006)
`/ia/pacote` (monta contexto com limite, grava auditoria) -> usuário no Copilot Chat -> `/ia/resposta` (extrai JSON, valida fontes contra os marcadores efetivamente enviados, refaz a minuta, grava auditoria) -> `/gerar-parecer` com a minuta aprovada.

### 3.3 Geração (UC007)
`/gerar-parecer` exige `validado=true`; gera o Word a partir de `templates/*.docx`; registra parecer e indicador.

## 4. Decisões arquiteturais (ADR)

| # | Decisão | Motivo | Consequência |
|---|---|---|---|
| ADR-01 | Conhecimento em arquivos, não em código | Evolução sem reescrever; revisão pela COGER | Mais arquivos a governar; exportação de categorias do HTML |
| ADR-02 | Motor Python + FastAPI | Ecossistema para PDF, texto e IA; documentação automática | Exige ambiente Python institucional |
| ADR-03 | Gerador HTML permanece independente e offline | RNF007: evolução sem interromper o processo | Duas implementações da geração de Word (HTML e motor) a manter alinhadas |
| ADR-04 | Busca padrão BM25 (Python puro) | Funciona em rede fechada, sem download de modelos | Não entende sinônimos; mitigado por palavras-chave e busca híbrida opcional |
| ADR-05 | Busca híbrida opcional (BM25 + embeddings locais, RRF) | Entender "professor universitário" = "docência" sem enviar dados para fora | Precisa de modelo local e memória; qualidade a medir |
| ADR-06 | Camada `AIProvider` substituível | Evitar dependência de fornecedor; trocar por configuração | Provedores automáticos sem uso enquanto não houver API |
| ADR-07 | **Modo assistido** com o Copilot Chat | Copilot Chat é a IA homologada e autorizada pelo CTSI, mas sem API | Fluxo manual (copiar e colar); validação automática da resposta; o AICI não controla onde o usuário cola |
| ADR-08 | IA só recebe o caso junto com o acervo | Evitar respostas sem base institucional | Sem base suficiente, a IA não é usada |
| ADR-09 | Fontes obrigatórias e validadas | Rastreabilidade e combate a alucinação | Parágrafo sem fonte válida é descartado |
| ADR-10 | Validação humana obrigatória na API | Art. 5º e 17 da Portaria RFB nº 647/2026 | O gerador de Word não é chamado sem `validado=true` |
| ADR-11 | Contexto repartido por trecho dentro de um limite | O prompt do chat tem tamanho máximo | Trechos de menor prioridade podem ficar de fora (e não podem ser citados) |
| ADR-12 | Mascaramento antes de qualquer envio | Minimizar exposição de dados pessoais | Não elimina dados em texto livre; decisão final da TI conforme a Análise de Riscos |
| ADR-13 | SQLite agora, PostgreSQL depois | Simplicidade do protótipo | Camada de banco isolada em `db.py` |
| ADR-14 | Trilha de auditoria em arquivos `.jsonl` | Simples e legível pelo curador | Sem proteção contra alteração; evoluir para armazenamento institucional |
| ADR-15 | **Modo local no HTML** (análise e Copilot assistido sem motor) | O ambiente de uso pode não ter Python (constatado) | Duplica no navegador a montagem do prompt e a validação; só tem o acervo embutido (`kb_local.json`: instruções, regras, trechos de normativos) e os precedentes da CGU, sem a biblioteca de pareceres; sem bloqueio técnico de revisão |

## 5. Pontos de extensão

| Para trocar... | Altere... |
|---|---|
| A IA (API, agente) | Nova classe `AIProvider` em `ai_provider.py` e `ia.provider` em `settings.yaml` |
| O índice | Nova classe de armazenamento em `indexer.py` (hoje: lexical e Chroma) |
| Os embeddings | Classe `Embedder` em `embeddings.py` (hoje: sentence-transformers) |
| O banco | `app/models/db.py` |
| O padrão do Word | `templates/*.docx` (estilos "AICI ...") e `templates/institucional.json` |
| Atividades e textos | Modelos em `knowledge/modelos/atividades/*.json` (exportados do HTML) |
| Instruções à IA | `prompts/*.txt` |

## 6. Segurança (resumo)

Escuta local por padrão; token e CORS; validação de upload; segredos em variáveis de ambiente; mascaramento; contexto restrito ao acervo; validação de fontes; validação humana; auditoria. Pendentes: autenticação por usuário e perfis, criptografia em repouso, retenção, parecer de segurança. Ver Documento 04, A.7.
