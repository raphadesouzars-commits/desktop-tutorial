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
| Endereço da IA, limites, caminhos | `config/settings.yaml` |

## Instalação e execução

```bash
cd AICI-Motor
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py                                         # http://127.0.0.1:8765  (documentação automática em /docs)
```

Na primeira execução o motor indexa `knowledge/` (incremental nas seguintes). Abra `gerador-parecer-conflito.html`, aba **Análise Inteligente**,
informe o endereço do motor e envie o PDF.

Testes: `python -m pytest -q`.

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
| POST | `/gerar-parecer` | DOCX (`documento`: `parecer`, `termo` ou `despacho`) |
| POST | `/revisar` | confere a consistência da minuta |
| GET | `/indicadores` | totais por atividade, resultado, precedente, mês |
| POST | `/indexar` | (re)indexa `knowledge/` (`?completo=true` refaz tudo) |
| GET | `/categorias`, `/saude` | categorias do HTML; estado do motor |

## Módulos (`app/services`)

`pdf_reader` (1) · `ocr_service` (2) · `fact_extractor` (3) · base em `knowledge/` (4) · `indexer` (5) · `retriever` (6) · `classifier` (7) ·
`copilot_service` (8) · `prompts` + `prompts/*.txt` (9) · `report_generator` (10) · `docx_generator` (11) · `metrics_service` (12) · `analysis_service` (orquestrador).

## IA (Copilot)

`ia.provider: offline` (padrão) funciona **sem IA**: a fundamentação sai dos modelos institucionais, cada parágrafo com a origem (PAR/ano).
Para usar a IA homologada, em `config/settings.yaml`:

```yaml
ia:
  provider: copilot
  copilot:
    endpoint: "https://<gateway-homologado>/..."   # o endereço que a RFB disponibiliza
    token_env: AICI_COPILOT_TOKEN                    # export AICI_COPILOT_TOKEN=...  (nunca no arquivo)
    formato: openai                                   # ou custom, com corpo_template e caminho_resposta
```

**Atenção:** o motor foi escrito para um gateway HTTP genérico. Eu não conheço o endpoint/contrato real do Copilot na rede da RFB - ele precisa ser configurado
(ou o formato `custom` ajustado) com a equipe de TI; só `offline` e um provedor simulado foram testados.

Garantias aplicadas no código:
- a IA **nunca recebe só o PDF**: `montar_contexto` exige normativos + (precedentes, pareceres ou modelos), senão não chama a IA;
- CPF, matrícula, telefone, e-mail e o nome do servidor são **mascarados** antes do envio (`ia.anonimizar`);
- a IA só pode escolher **categorias existentes**; resposta fora da lista é descartada;
- parágrafo da IA **sem fonte válida do contexto é descartado**; as fontes citadas viram a origem do parágrafo;
- falha da IA -> o motor cai no modo extrativo e avisa.

## Índice (RAG)

- `indexador.backend: lexical` (padrão): BM25 em Python puro, sem dependências nem download, funciona em rede fechada. A consulta é expandida com as palavras-chave da atividade reconhecida.
- `indexador.backend: chroma`: busca vetorial (`pip install chromadb`). Por padrão o Chroma baixa um modelo de embeddings da internet; em rede fechada, passe um
  modelo local em `criar_store(settings, embedding_function=...)`. Integração testada com um embedding de teste, **não** com um modelo semântico real.
- A busca semântica real ("professor universitário" ~ "docência" sem palavras em comum) depende de embeddings; no modo lexical isso é coberto só pelas palavras-chave dos modelos.

## OCR

PDF digitalizado exige `pip install easyocr` (puxa PyTorch, ~2 GB; os modelos de idioma são baixados na 1ª execução). Sem ele, o `/upload` avisa e o status fica `sem_texto`. **OCR não foi testado aqui.**

## Segurança

- Escuta só em `127.0.0.1`. Para uso em rede, coloque atrás do proxy reverso institucional e defina `AICI_TOKEN` (cabeçalho `X-AICI-Token`).
- CORS restrito às origens de `config/settings.yaml` (`null` = HTML aberto como arquivo).
- Uploads: só PDF (assinatura `%PDF`), máx. 25 MB, salvos com nome aleatório.
- `uploads/`, `output/`, `metrics/`, `vectorstore/` contêm dados pessoais e ficam fora do git.

## Evolução (5-10 anos)

Trocar PostgreSQL por SQLite = só `app/models/db.py`. Trocar de IA = outra classe `Provider`. Trocar o índice = outra classe de armazenamento em `indexer.py`.
Novas atividades/entendimentos = novos arquivos em `knowledge/`, sem mexer no código.
