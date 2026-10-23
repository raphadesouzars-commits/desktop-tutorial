# Log de migração do catálogo — Rodada 5 (unificação com o Nexo Coger)

Data: 2026-07-10
Fonte: `nexus_1.html` (Nexo Coger), `NORMAS_BASE`/`RELACOES_DECL`/`buildCatalogo()`, `CATALOGO_VERSION = "1.0"`.

## Observação sobre a contagem

O documento da Rodada 5 fala em "45 normas". Conferido o código-fonte real do Nexo: `NORMAS_BASE` tem **52 entradas** — 45 da Lei nº 8.112/90 (arts. 116, 117, 130 §1º e 132) + 7 do art. 32 da Lei nº 12.527/2011 (LAI). O "45" do documento contava só o bloco da Lei 8.112/90, sem a LAI. A migração aplicada usa os 52 reais.

## Correspondência aplicada (id antigo → normaId novo)

Todas as 11 infrações originais do Oitiva bateram exatamente com a proposta da seção 2.2 do documento da rodada — nenhum ajuste de correspondência foi necessário.

| Id antigo (Oitiva) | normaId novo (Nexo) | Rótulo no Nexo | Dispositivo | Perguntas migradas |
|---|---|---|---|---|
| `inf_desidia` | `N-117-XV` | Proceder de forma desidiosa | art. 117, XV, Lei nº 8.112/90 | 5 |
| `inf_abandono` | `N-132-II` | Abandono de cargo | art. 132, II, Lei nº 8.112/90 | 5 |
| `inf_inassiduidade` | `N-132-III` | Inassiduidade habitual | art. 132, III, Lei nº 8.112/90 | 5 |
| `inf_proveito` | `N-117-IX` | Valimento do cargo | art. 117, IX, Lei nº 8.112/90 | 5 |
| `inf_vantagem` | `N-117-XII` | Receber propina, comissão, presente ou vantagem de qualquer espécie | art. 117, XII, Lei nº 8.112/90 | 5 |
| `inf_gerencia` | `N-117-X` | Participar de gerência/administração de sociedade privada; exercer o comércio | art. 117, X, Lei nº 8.112/90 | 5 |
| `inf_sigilo` | `N-132-IX` | Revelação de segredo apropriado em razão do cargo | art. 132, IX, Lei nº 8.112/90 | 5 |
| `inf_incompativel` | `N-117-XVIII` | Exercer atividades incompatíveis com o cargo/função ou com o horário de trabalho | art. 117, XVIII, Lei nº 8.112/90 | 5 |
| `inf_urbanidade` | `N-116-XI` | Falta de urbanidade | art. 116, XI, Lei nº 8.112/90 | 5 |
| `inf_normas` | `N-116-III` | Inobservância de normas legais e regulamentares | art. 116, III, Lei nº 8.112/90 | 5 |
| `inf_enriquecimento_ilicito` | `N-132-IV` | Improbidade administrativa | art. 132, IV, Lei nº 8.112/90 | 13 (tratamento especial, seção 5 — inalterado) |

**Total de perguntas migradas: 63** (50 + 13). Nenhuma pergunta órfã — todas as 63 perguntas específicas que existiam antes da migração continuam existindo depois, só com o campo `infracoes` apontando para o `normaId` novo.

### Nota sobre `inf_sigilo`

O documento da rodada pedia verificar se o banco atual tratava sigilo como "leve" (`N-116-VIII`) ou "grave" (`N-132-IX`). O dispositivo já registrado no Oitiva (`Art. 132, IX c/c art. 116, VIII, Lei 8.112/90`) e a pena (`demissão`) e o texto das perguntas já existentes (acesso indevido a sistemas fiscais, revelação a terceiro, correlação com recebimento de vantagem) descrevem inequivocamente a versão **grave** (demissão). Migrado para `N-132-IX` sem necessidade de dividir o banco entre duas entradas.

## `inf_outras` — fora da unificação

Por decisão do usuário (2026-07-10), a categoria residual `inf_outras` **não** foi migrada para nenhum `normaId` do Nexo — não faz parte do catálogo de 52 normas, e continua existindo no Oitiva como fallback próprio, com as mesmas 12 perguntas genéricas de antes. Só teve os nomes de campo do objeto convertidos para o padrão do Nexo (`rotulo`/`dispositivo`/`descricaoTipo`/`gravidade`/`penaPrevista`/`elementoSubjetivoExigido`/`notasEnquadramento`/`relacoes`), por uniformidade de renderização — sem id `N-*`, sem dispositivo real.

## Referências funcionais fora do banco de perguntas, também migradas

Além do campo `infracoes` de cada pergunta, 4 comparações diretas no código (não em perguntas) usavam o id antigo `inf_enriquecimento_ilicito` e foram atualizadas para `N-132-IV`:

- 3 itens de `CATALOGO.checklistItens` com `condicao: "infracao == inf_enriquecimento_ilicito"` (documentação patrimonial, oportunidade de justificação, terceiros interpostos).
- `atualizarPainelDicasEtapa2()` — dica contextual da 11ª infração.
- `atualizarVisibilidadeTerceiroInterposto()` — exibição do card de terceiro interposto.
- `itensChecklistAplicaveis()` — mesma condição do primeiro item, no filtro de checklist aplicável.

## Campos de schema trocados (sem reinterpretação de conteúdo)

| Campo antigo (Oitiva, só nas 11 infrações isoladas) | Campo novo (Nexo, todas as 52 normas) |
|---|---|
| `nome` | `rotulo` |
| `elementosTipicos` (array) | `descricaoTipo` (string) — sem correspondência 1:1; adotado o campo do Nexo tal como está |
| `penaAbstrata` | `penaPrevista` |
| `observacoes` | `notasEnquadramento` |
| `grupo`, `modulo` | removidos (não lidos em nenhum lugar do código — confirmado antes de remover) |
| — | `gravidade`, `elementoSubjetivoExigido`, `relacoes[]` (novos, não existiam no Oitiva) |

`observacaoControversia` e `notaTerceiroInterposto` (campos extras, exclusivos de `N-132-IV`) foram preservados integralmente — não fazem parte do schema do Nexo, mas a seção 5 do documento da rodada pede que o tratamento especial do art. 132, IV fique "exatamente como está", então continuam ali.

## Código UI atualizado para os novos nomes de campo

- `<option>` do seletor de infração: `i.nome` → `i.rotulo`.
- `renderInfracaoDetalhe()`: mostrava `elementosTipicos`/`penaAbstrata`; agora mostra `descricaoTipo`/`gravidade`/`penaPrevista`/`elementoSubjetivoExigido`/`notasEnquadramento`.
- Impressão do roteiro (`montarAreaImpressaoRoteiro`): `infracaoObj.nome` → `infracaoObj.rotulo` + `infracaoObj.dispositivo`.

## Seletor de infração agrupado (seção 6)

Select reagrupado em `<optgroup>` na ordem definida no Nexo, ordenado por inciso (numeração romana) dentro de cada grupo:

1. Lei 8.112/90 — Deveres (art. 116) — 12 normas
2. Lei 8.112/90 — Proibições (art. 117) — 19 normas
3. Lei 8.112/90 — Demissão (art. 132) — 13 normas
4. Lei 8.112/90 — Outras (art. 130) — 1 norma
5. LAI (Lei nº 12.527/2011) — 7 normas
6. Outras categorias — `inf_outras` (fora da unificação)

Campo de busca por rótulo/dispositivo/id adicionado (não existia antes — o Oitiva nunca teve mais de 12 infrações num só select).

## Função de preparação para a Rodada 6

`resolverNormaPorId(normaId)` implementada conforme a seção 7 do documento, com teste unitário simples em `validarCatalogo()` (console, ao carregar a ferramenta): confirma que um id existente resolve `encontrada: true` e um id inexistente resolve `encontrada: false, norma: null`. Sem UI de importação nesta rodada (Rodada 6).

## Regressão

Suíte de 21 checagens automatizadas (Playwright) cobrindo: seletor agrupado + busca, ordenação por inciso, detalhe da norma, roteiro gerado a partir de infração migrada, impressão (roteiro/termo/cartão de mesa), tratamento especial do art. 132, IV (painel de controvérsia + checklist patrimonial), `inf_outras` inalterada, exportação/importação de `.json` — todas passando, zero erros de console.
