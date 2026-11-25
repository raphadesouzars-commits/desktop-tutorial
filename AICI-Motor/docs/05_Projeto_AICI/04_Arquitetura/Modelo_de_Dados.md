# Modelo de Dados e Dicionário

**Versão 0.3 - novembro/2026.**

## 1. Banco operacional (SQLite - `metrics/aici.db`)

### consultas
| Coluna | Tipo | Descrição |
|---|---|---|
| id | INTEGER PK | Identificador da consulta |
| data | TEXT | Data e hora do recebimento |
| arquivo | TEXT | Nome aleatório do PDF em `uploads/` |
| usuario | TEXT | Usuário informado (campo livre; autenticação institucional é planejada) |
| atividade | TEXT | `id` da atividade classificada ou escolhida |
| resultado | TEXT | Resultado do parecer gerado |
| status | TEXT | `recebida`, `sem_texto`, `analisada`, `parecer_gerado` |

### pareceres
| Coluna | Tipo | Descrição |
|---|---|---|
| id | INTEGER PK | |
| consulta_id | INTEGER FK | Consulta de origem |
| resultado | TEXT | `sem_conflito`, `sem_conflito_ressalvas`, `conflito`, `outro` |
| modelo | TEXT | `id` da atividade usada como modelo |
| arquivo_saida | TEXT | Nome do .docx em `output/consulta_<id>/` |
| data | TEXT | |

### metricas
| Coluna | Tipo | Descrição |
|---|---|---|
| id | INTEGER PK | |
| data | TEXT | Data (AAAA-MM-DD) |
| atividade | TEXT | Atividade, por extenso |
| resultado | TEXT | Resultado |
| precedente_utilizado | TEXT | `PA-<número>-<ano>` do precedente mais próximo, ou o título |

## 2. Arquivos de operação

| Arquivo | Conteúdo | Dados pessoais |
|---|---|---|
| `uploads/<uuid>.pdf` | PDF original da consulta | Sim |
| `uploads/<id>.txt` | Texto extraído | Sim |
| `output/consulta_<id>/analise.json` | Análise completa (fatos, classificação, trechos recuperados, minuta) | Sim |
| `output/consulta_<id>/<documento>_<número>_<ano>.docx` | Parecer, termo ou despacho | Sim |
| `metrics/metricas.jsonl` | Uma linha por parecer: `{"atividade","resultado","precedente","data"}` | Não |
| `metrics/ia_auditoria.jsonl` | Uma linha por interação com a IA: data, provedor, tipo (`pacote`, `resposta` ou chamada automática), tamanho e, se configurado, prompt e resposta mascarados | Possível |
| `vectorstore/lexical.json` | Trechos e manifesto do índice | Sim (trechos dos pareceres) |
| `vectorstore/dense.npy`, `dense_chaves.json` | Vetores dos trechos (busca por sentido) | Derivado |

## 3. Estruturas principais (JSON da API)

### Fatos
`atividade`, `entidade`, `remuneracao`, `vinculo`, `descricao`, `atribuicoes[]`, `servidor{nome, cargo, matricula, unidade, processo, protocolo, tipo}`, `respostas{1..10}`, `origem` (`heuristica` ou `heuristica+ia`).

### Trecho (item recuperado)
`id`, `tipo` (`parecer`, `precedente`, `normativo`, `modelo`, `regra`), `titulo`, `fonte` (caminho em `knowledge/`), `texto`, `tema`, `ano`, `numero`, `score`, `motivo`, `origem` (`COGER` ou `CGU`), `extra`.

### Classificação
`escolhida` e `candidatas[]` com `id`, `nome`, `score`, `confianca` (`alta`, `media`, `baixa`), `motivos[]`; `metodo`; `avisos[]`.

### Minuta
`secoes[]` (`titulo`, `paragrafos[]` com `texto`, `tipo` = `p`, `cit` ou `it`, `fontes[]`), `resultado_sugerido`, `ressalvas[]`, `modo` (`offline`, `copilot`, `copilot_chat`), `atividade_id`, `variante_id`, `avisos[]`.

### Pacote (modo assistido)
`prompt`, `prompt_curto`, `contexto_md`, `limite_caracteres`, `caracteres`, `truncado`, `ids[]`, `url_chat`, `avisos[]`.

Esquemas completos: `openapi.json` (esta pasta).

## 4. Base de conhecimento (`knowledge/`)

| Pasta/arquivo | Conteúdo | Nome do arquivo | Origem |
|---|---|---|---|
| `pareceres/` | Pareceres emitidos | `PA_<número>_<ano>_<Tema>.<ext>` | `01_Pareceres_Emitidos` |
| `precedentes/<Tema>/` | Pareceres reutilizáveis por tema | idem | `02_Precedentes` |
| `normativos/<Grupo>/` | Lei nº 12.813/2013, portarias, notas técnicas, orientações da CGU | livre | `03_Normativos` |
| `modelos/` | Modelos institucionais | livre | `04_Modelos_Institucionais` |
| `modelos/atividades/<id>.json` | 68 modelos de atividade (exportados do gerador HTML) | `<id>.json` | `parecer/modelos` |
| `regras_coger.md` | Regras institucionais, sempre enviadas à IA | - | `scripts/gerar_regras_coger.py` + seção manual |

Extensões lidas: `.pdf`, `.docx`, `.txt`, `.md` e `.json` (só os modelos de atividade). Metadados (número, ano, tema, origem) são extraídos do nome e da pasta.

### Modelo de atividade (`modelos/atividades/<id>.json`)
`id`, `nome`, `descricao`, `grupo`, `palavrasChave[]`, `variantes[]`. Cada variante: `id`, `rotulo`, `resultado`, `quandoUsar`, `fonte` (parecer de origem), `assunto`, `ementaTitulo`, `ementa[]`, `campos[]` (campos a preencher), `corpo[]` (blocos: `t` = `p` parágrafo ou `cit` citação; `x` texto com `{{campo}}` e `{{g:masculino|feminino}}`; `opc` = bloco opcional). O último parágrafo é a conclusão.

### Categorias (`config/categorias.json`)
Lista de `{id, nome, grupo, descricao, palavrasChave[], variantes[{id, rotulo, resultado, fonte, quandoUsar}]}`, exportada dos modelos.

## 5. Planilha de metadados da biblioteca (Drive)

Colunas: TipoDocumento, Ano, Tema, Subtema, Resultado, PossuiCompromisso, UtilizarIA, NivelConfianca, **Status_IA** (`Nao_Processado`, `Classificado_IA`, `Validado_Humano`, `Utilizado_Base_Conhecimento`), Observações. Ainda não integrada ao motor.

## 6. Retenção (a definir com a TI)

Não há rotina de retenção ou descarte. Proposta: definir prazo para `uploads/`, `output/` e `ia_auditoria.jsonl`, criptografia em repouso e cópia de segurança (Documento 04, solicitação 24).
