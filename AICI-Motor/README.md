# AICI-Motor

Motor do **Assistente Inteligente para Conflitos de Interesse** (COGER/RFB). Transforma o PDF da consulta do SeCI em

```
Análise estruturada  +  Pesquisa de conhecimento  +  Minuta de parecer  +  Indicadores
```

usando a **biblioteca da COGER** (pareceres, precedentes, normativos, modelos), uma **IA homologada** (Copilot) e os **modelos institucionais**.
A decisão final é sempre do parecerista.

## Princípio: o conhecimento não fica no código

```
knowledge/ (pareceres, precedentes, normativos, modelos)  ->  índice  ->  recuperação  ->  IA  ->  minuta
```

O código só orquestra. Atividades, categorias, textos de conclusão, deveres e prompts são **dados** editáveis:

| O quê | Onde |
|---|---|
| Pareceres, precedentes, normativos | `knowledge/<tipo>/` (sincronizados do SharePoint/Drive) |
| Modelos por atividade (68 atividades / 163 situações) | `knowledge/modelos/atividades/*.json` (exportados do gerador HTML) |
| Categorias do classificador | `config/categorias.json` (exportado do HTML) |
| Linguagem institucional (abertura, conclusões, deveres, termo) | `templates/institucional.json` |
| Aparência do Word | `templates/parecer.docx`, `termo.docx`, `despacho.docx` (estilos "AICI ...") |
| Instruções para a IA | `prompts/*.txt` |
| Regras institucionais que a IA sempre lê | `knowledge/regras_coger.md` |
| Endereço da IA, limites, caminhos | `config/settings.yaml` |

## Dois modos de uso

- **Modo local (sem instalar nada):** abra `gerador-parecer-conflito.html` -> aba "Análise Inteligente" (modo Local). Lê o PDF no navegador, mostra fatos, atividade e precedentes da CGU e, opcionalmente, prepara o prompt do Copilot Chat e valida a resposta colada. Usa a biblioteca de pareceres da COGER se você conectar a pasta sincronizada do SharePoint (índice BM25 em JavaScript guardado no navegador); não tem bloqueio técnico de revisão. O acervo embutido vem de `parecer/kb_local.json` (`python parecer/gerar_kb_local.py` + `python parecer/build.py`).
- **Motor AICI (este projeto Python):** o restante deste README. Consulta a biblioteca de pareceres, precedentes e normativos da COGER, tem API, auditoria e indicadores.

## Instalação e execução

**Atalho:** no Windows, dê dois cliques em `iniciar_AICI.bat` (primeira vez instala as dependências; exige Python 3.12+ e acesso ao repositório de pacotes; **não testado em Windows**). No Linux/macOS: `./iniciar_AICI.sh`. Mantenha a janela aberta enquanto usa a aba "Análise Inteligente".

```bash
cd AICI-Motor
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py                                         # http://127.0.0.1:8765  (documentação automática em /docs)
```

Na primeira execução o motor indexa `knowledge/` (incremental nas seguintes). Abra `gerador-parecer-conflito.html`, aba **Análise Inteligente**, informe o endereço do motor e siga as 3 etapas:
**1 Análise** (envia o PDF; mostra fatos, enquadramento, normativos, precedentes e compromissos) -> **2 Validação humana** (você confere e marca a revisão) -> **3 Geração** (só então liberada).

Testes: `python -m pytest -q`. Documentação completa do projeto: `docs/05_Projeto_AICI/00_Indice.md`.

## Alimentando a base de conhecimento

```bash
python scripts/importar_biblioteca.py /caminho/da/biblioteca [--sincronizar]
```

Lê a estrutura `01_Pareceres_Emitidos`, `02_Precedentes`, `03_Normativos`, `04_Modelos_Institucionais` (a pasta `_Duplicados_Revisar` fica de fora)
e copia para `knowledge/`. Nomes no padrão `PA_<num>_<ano>_<Tema>` geram os metadados número/ano/tema. Depois: `POST /indexar` (ou reiniciar).
Se um modelo do HTML mudar: `python scripts/exportar_categorias.py`.

`knowledge/pareceres` e `knowledge/precedentes` **não são versionados** (git ignora): contêm dados pessoais. Já vêm incluídos a Lei 12.813/2013 e a Portaria Interministerial 333/2013.

## API

| Método | Rota | Função |
|---|---|---|
| POST | `/upload` | PDF da consulta -> texto (OCR se digitalizado); devolve `consulta_id` |
| POST | `/analisar` | fatos + enquadramento + precedentes + pareceres + normativos + minuta |
| POST | `/minuta` | refaz a minuta com a atividade/resultado escolhidos |
| POST | `/ia/pacote`, `/ia/resposta` | modo assistido com o Copilot Chat: prompt e contexto; validação da resposta colada |
| POST | `/gerar-parecer` | DOCX (`documento`: `parecer`, `termo` ou `despacho`); exige `validado=true` (revisão humana) |
| POST | `/revisar` | confere a consistência da minuta |
| GET | `/indicadores` | totais por atividade, resultado, precedente, mês |
| POST | `/indexar` | (re)indexa `knowledge/` (`?completo=true` refaz tudo) |
| GET | `/categorias`, `/saude` | categorias do HTML; estado do motor |

## Módulos (`app/services`)

`pdf_reader` (1) · `ocr_service` (2) · `fact_extractor` (3) · base em `knowledge/` (4) · `indexer` (5) · `retriever` (6) · `classifier` (7) ·
`ai_provider` (8) · `embeddings` · `prompts` + `prompts/*.txt` (9) · `report_generator` (10) · `docx_generator` (11) · `metrics_service` (12) · `analysis_service` (orquestrador).

## Copilot Chat da RFB (modo assistido)

O Copilot Chat (conta corporativa, Microsoft 365) é a IA homologada e autorizada pelo CTSI (3ª Reunião Ordinária de 2026, 18/06), **condicionada aos controles da Análise de Riscos**, mas não tem API para o AICI. Por isso o AICI trabalha em **modo assistido**:
`/ia/pacote` monta o prompt (caso mascarado + regras da COGER + normativos + precedentes + pareceres + modelos, com marcadores citáveis) dentro de `ia.copilot_chat.limite_caracteres`; o parecerista o cola no Copilot Chat
(ou anexa `contexto_AICI.md` e usa o prompt curto), copia a resposta em JSON e a cola na aba; `/ia/resposta` valida as fontes (só valem as que foram enviadas), descarta parágrafo sem fonte, e refaz a minuta. Tudo entra na trilha `metrics/ia_auditoria.jsonl`.
O limite de caracteres padrão (7.500) é suposição: confirme com a TI. **Testado só com respostas simuladas.**

## IA: camada de provedores (`app/services/ai_provider.py`)

O motor só conhece a interface `AIProvider` (`completar(sistema, usuario)` e `analyze(prompt, contexto)`); o restante do sistema nunca sabe qual provedor está por trás.
Escolha em `config/settings.yaml` -> `ia.provider`:

| Provedor | Quando usar |
|---|---|
| `offline` (padrão) | Sem IA. O parecer sai dos modelos institucionais, cada parágrafo com a origem. **O projeto é utilizável integralmente assim.** |
| `mock` | Testes/demonstrações. |
| `copilot` | Copilot Studio publicado por HTTPS, ou gateway interno (`formato: openai` ou `custom`). |
| `azure` | Azure OpenAI corporativo: a TI informa `endpoint`, `deployment` e `api_version`; a chave vai em `AICI_AZURE_KEY`. |
| `openai` | API compatível com OpenAI; só funciona com `confirmo_homologado: true` (a API pública não é homologada pela RFB). |

O que a TI da RFB precisa informar (um dos cenários): **(A)** Copilot só pelo chat (m365.cloud.microsoft/chat): não há como automatizar, o servidor usa à mão e o motor segue em `offline`;
**(B)** Copilot Studio com API HTTPS; **(C)** Azure OpenAI corporativo (melhor caso). Só `offline`, `mock` e chamadas HTTP simuladas foram testados; nenhum endpoint real.

Garantias aplicadas no código:
- a IA **nunca recebe só o PDF**: `montar_contexto` exige normativos + (precedentes, pareceres ou modelos), senão não chama a IA; `knowledge/regras_coger.md` acompanha sempre o contexto (marcador R1);
- CPF, matrícula, telefone, e-mail e o nome do servidor são **mascarados** antes do envio (`ia.anonimizar`);
- a IA só pode escolher **categorias existentes**; resposta fora da lista é descartada;
- parágrafo da IA **sem fonte válida do contexto é descartado**; as fontes citadas viram a origem do parágrafo;
- falha da IA -> o motor cai no modo extrativo e avisa.

## Regras da COGER (`knowledge/regras_coger.md`)

Documento curto (categorias válidas, resultados possíveis, estrutura do parecer, deveres padrão, Termo, encaminhamento) que a IA recebe em toda chamada.
É gerado dos dados do projeto: `python scripts/gerar_regras_coger.py`. A seção **"A consolidar pela COGER"** é preenchida à mão e preservada nas próximas gerações:
os princípios consolidados da COGER que ainda não estão em norma nem em parecer precisam ser escritos pela equipe, o motor não os inventa.

## Busca (RAG)

- **BM25** (padrão): Python puro, sem download, funciona em rede fechada. A consulta é expandida com as palavras-chave da atividade reconhecida.
- **Busca híbrida (BM25 + embeddings)**: `recuperacao.embeddings.habilitado: true` (+ `pip install sentence-transformers`). Fluxo: BM25 top 20 + vetores top 20 -> fusão por Reciprocal Rank Fusion ->
  reclassificação com o peso COGER -> top finais. Modelos sugeridos, rodando **localmente**: `BAAI/bge-m3` ou `intfloat/multilingual-e5-large` (e5 pede os prefixos `query: ` e `passage: `).
  Em rede fechada, baixe o modelo uma vez numa máquina com internet e aponte `modelo` para a pasta. Os vetores ficam em `vectorstore/dense.npy` e são atualizados só para trechos novos ou alterados.
  A fusão foi testada com um embedder de teste (mostra um parecer de "docência" achado por "professor universitário", que o BM25 sozinho não acha); **nenhum modelo real foi executado aqui**, então a qualidade com bge-m3 precisa ser medida com casos reais.
- **Chroma** (`indexador.backend: chroma`, `pip install chromadb`): alternativa vetorial pura; integração testada com embedding de teste.

## OCR

PDF digitalizado exige `pip install easyocr` (puxa PyTorch, ~2 GB; os modelos de idioma são baixados na 1ª execução). Sem ele, o `/upload` avisa e o status fica `sem_texto`. **OCR não foi testado aqui.**

## Segurança

- Escuta só em `127.0.0.1`. Para uso em rede, coloque atrás do proxy reverso institucional e defina `AICI_TOKEN` (cabeçalho `X-AICI-Token`).
- CORS restrito às origens de `config/settings.yaml` (`null` = HTML aberto como arquivo).
- Uploads: só PDF (assinatura `%PDF`), máx. 25 MB, salvos com nome aleatório.
- `uploads/`, `output/`, `metrics/`, `vectorstore/` contêm dados pessoais e ficam fora do git.

## Evolução (5-10 anos)

Trocar PostgreSQL por SQLite = só `app/models/db.py`. Trocar de IA = outra classe `AIProvider`. Trocar o índice = outra classe de armazenamento em `indexer.py`.
Novas atividades/entendimentos = novos arquivos em `knowledge/`, sem mexer no código.
