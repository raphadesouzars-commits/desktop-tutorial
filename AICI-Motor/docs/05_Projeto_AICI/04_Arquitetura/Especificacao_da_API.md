# Especificação da API do AICI-Motor

**Versão 0.3 - novembro/2026.** Contrato completo e interativo: `openapi.json` (esta pasta) e `http://<servidor>:8765/docs` com o serviço em execução.

## 1. Convenções

- Base: `http://127.0.0.1:8765` (padrão). Corpo em JSON (`Content-Type: application/json`), exceto `/upload` (multipart).
- **Autenticação:** se a variável de ambiente `AICI_TOKEN` existir, toda rota exige o cabeçalho `X-AICI-Token`. Sem token válido: HTTP 401.
- **CORS:** só as origens de `servidor.cors_origens` (inclui `null`, usada pelo HTML aberto como arquivo).
- **Erros:** `{"detail": "mensagem"}` com o código HTTP indicado.
- **Resultado** (enumeração): `sem_conflito`, `sem_conflito_ressalvas`, `conflito`, `outro`.

## 2. Rotas

### GET /saude
Estado do serviço. Resposta: `{"status":"ok","provider":"offline","indice":{"normativo":26,"modelo":163},"backend":"lexical","arquivos_indexados":70,"embeddings":null,"ocr":false}`.

### POST /upload
Recebe o PDF da consulta. Multipart: `arquivo` (PDF), `usuario` (opcional).

Resposta 200: `{"consulta_id":1,"arquivo_original":"consulta.pdf","paginas":2,"usou_ocr":false,"caracteres":4642,"avisos":[],"status":"recebida"}`

| Código | Situação |
|---|---|
| 400 | Não é PDF (assinatura) ou PDF ilegível |
| 413 | Acima de 25 MB |
| 200 + `status: "sem_texto"` | PDF sem texto e sem OCR disponível (ver `avisos`) |

### POST /analisar
Corpo: `{"consulta_id":1,"gerar_minuta":true}`.

Resposta 200 (`Analise`): `consulta_id`, `fatos`, `classificacao` (`escolhida`, `candidatas[]`, `metodo`, `avisos[]`), `precedentes[]`, `pareceres[]`, `normativos[]`, `modelos[]` (todos `Trecho`), `minuta`, `avisos[]`.

| Código | Situação |
|---|---|
| 404 | Consulta inexistente |
| 422 | Consulta sem texto extraído |

### POST /minuta
Refaz a minuta com a escolha do parecerista. Corpo: `{"consulta_id":1,"atividade_id":"magisterio","resultado":"conflito"}` (os dois últimos opcionais). Resposta: `Minuta`. Erros: 409 (consulta ainda não analisada), 422 (`atividade_id` fora da lista de categorias).

### POST /ia/pacote  (modo assistido)
Prepara o material para o Copilot Chat. Corpo: `{"consulta_id":1,"atividade_id":"...","resultado":"..."}` (opcionais).

Resposta 200 (`Pacote`): `prompt` (instrução + contexto, dentro de `limite_caracteres`), `prompt_curto` (instrução; usar com o arquivo), `contexto_md` (contexto completo), `limite_caracteres`, `caracteres`, `truncado`, `ids[]` (marcadores citáveis no prompt completo), `url_chat`, `avisos[]`.

Erros: 409 (não analisada); 422 (base insuficiente: sem normativo ou sem precedente/parecer/modelo). Registra na trilha de auditoria (tipo `pacote`).

### POST /ia/resposta  (modo assistido)
Valida a resposta colada do Copilot Chat e refaz a minuta. Corpo: `{"consulta_id":1,"texto":"<resposta do chat>","modo":"texto|arquivo","atividade_id":"...","resultado":"..."}`.

- `modo: "texto"`: só valem fontes que couberam no prompt completo; `"arquivo"`: valem todas as do contexto.
- Formato esperado da resposta: JSON com `fundamentacao[{texto, fontes[]}]`, `resultado_sugerido`, `ressalvas[]`, `lacunas[]` (instruído em `prompts/draft.txt`). O JSON pode vir cercado de texto ou de cercas de código.

Resposta 200: `Minuta` com `modo: "copilot_chat"`. Parágrafo sem fonte válida é descartado (aviso na minuta).

| Código | Situação |
|---|---|
| 422 | Sem JSON na resposta, JSON incompleto/inválido ou `atividade_id` inválido |
| 409 | Consulta não analisada |

Registra na trilha de auditoria (tipo `resposta`).

### POST /gerar-parecer
Gera o documento Word e o devolve (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`, com `Content-Disposition`).

Corpo (`PedidoParecer`): `consulta_id`, `documento` (`parecer`, `termo` ou `despacho`), `validado` (**obrigatório `true`**), `resultado`, `atividade_id`, `minuta` (a minuta aprovada, por exemplo a do modo assistido; se ausente, é refeita), `numero`, `ano`, `destino` (despacho).

| Código | Situação |
|---|---|
| 422 | `validado` ausente/falso (revisão humana obrigatória); `atividade_id` inválido; Termo para resultado diferente de `sem_conflito_ressalvas` |
| 409 | Consulta não analisada |

Para `parecer`: registra o parecer, atualiza o status da consulta e grava o indicador.

### POST /revisar
Query `consulta_id`; corpo: `Minuta`. Resposta: `{"pontos":[{"gravidade":"alta|media|baixa","descricao":"...","trecho":"..."}]}`. Verifica campos pendentes, parágrafos sem origem, conclusão incoerente com o resultado e ausência do Termo na conclusão (e, se houver API de IA, revisão adicional).

### GET /indicadores
`{"total_consultas","total_pareceres","por_atividade":[{atividade,n}],"por_resultado":[{resultado,n}],"precedentes_mais_utilizados":[{precedente,n}],"por_mes":[{mes,n}]}`.

### POST /indexar
Query `completo=true|false`. (Re)indexa `knowledge/`. Resposta: `{"backend","novos","alterados","removidos","erros":[],"chunks":{...},"vetores":null}`.

### GET /categorias
Lista das 68 atividades com suas variantes: `[{"id","nome","grupo","variantes":[{"id","rotulo","resultado"}]}]`.

## 3. Exemplo de uso (curl)

```bash
curl -s -F "arquivo=@consulta.pdf" http://127.0.0.1:8765/upload
curl -s -H "Content-Type: application/json" -d '{"consulta_id":1}' http://127.0.0.1:8765/analisar
curl -s -H "Content-Type: application/json" -d '{"consulta_id":1,"validado":true,"numero":"300","ano":"2026"}' \
     -o parecer.docx http://127.0.0.1:8765/gerar-parecer
```

## 4. Versionamento

A API está na versão 0.1.0 (protótipo). Mudanças incompatíveis devem ser registradas no Backlog e comunicadas ao gerador HTML, que é o único cliente.
