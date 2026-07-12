# Auditoria de código-fonte — Nexo Coger (nexo-coger.html)

Fonte: `/home/user/desktop-tutorial/ferramentas/nexo-coger.html` (SPA vanilla JS single-file, ~4140 linhas, sem framework, tudo em escopo de topo dentro de um único `<script>`). Todas as citações abaixo são texto literal lido do arquivo, com o número de linha entre colchetes.

---

## 1. Cadastro de um fato apurado — campo a campo

Função: `abrirFormFato(id)` — linhas 2719–2909.

O objeto `f` de um fato novo é inicializado assim (linha 2721–2724):
```
{id, titulo:'', descricao:'', periodo:{inicio:'',fim:''}, local:'', dataCiencia:'',
 ordem, status:'ativo', justificativaArquivamento:'', pautaEnviada:{em:null},
 condutas:[], provaIds:[], estadoProbatorio:{calculado:'ausente',override:null,justificativaOverride:''},
 enquadramentos:[], multiplicidade:{...}, elementosBuscados:''}
```

Ordem real dos campos no corpo do modal (array `body`, linhas 2871–2888):

1. **"Título"** — `fieldText`, texto livre. [linha 2872]
2. **"Descrição pormenorizada"** — `fieldArea`, com hint "delineamento fático claro e individualizado — STJ, MS 13.110/DF". O último argumento `true` ativa apenas o contador de caracteres (`fieldArea(label,val,oninput,hint,max)` — `max` não é flag de obrigatoriedade, é o gatilho do contador). [linhas 2491–2496, 2873]
3. **"Início do período"** — `fieldText`, tipo `date`. [linha 2875]
4. **"Fim do período"** — `fieldText`, tipo `date`. [linha 2876]
5. **"Local"** — `fieldText`, texto livre. [linha 2877]
6. **"Data de ciência da autoridade (art. 142, §1º)"** — `fieldText`, tipo `date`, com hint: "Marco inicial da prescrição — NÃO é a data do fato, mas quando a autoridade competente teve ciência dele. Se vazio, o cálculo usa o fim do período como estimativa." [linhas 2878–2879]
7. Aviso condicional "📤 Pauta enviada em …" com link "limpar marca de pauta enviada" (só aparece se `f.pautaEnviada.em` estiver setado). [linhas 2880–2886]
8. Bloco **"Condutas individualizadas (uma por acusado)"** (`condBox`) — não é `fieldX`, é um bloco de sub-linhas repetíveis: select de acusado, textarea "conduta individualizada" (placeholder), select Comissiva/Omissiva, botão "✕" para remover, botão "+ conduta" para adicionar. Se não há acusados cadastrados, mostra hint "Cadastre acusados primeiro (+ acusado)." [linhas 2728–2746]
9. Bloco **"Provas vinculadas"** (`provBox`) — ver seção 2 abaixo.
10. `wizardBanner` — banner de multiplicidade (só aparece com 2+ enquadramentos ativos).
11. Bloco **"Enquadramentos legais"** (`enqBox`) — ver detalhamento abaixo.
12. Bloco **"Estado probatório"** (`estBox`).
13. Bloco **"Situação do fato"** (`sitBox`).

### Enquadramento legal — como o usuário busca/seleciona a norma

Não é busca por texto: é um **`<select>` agrupado por `<optgroup>`**, populado a partir de `doc.catalogoNormas` filtrado por grupo (`grupoDaNorma`). [linhas 2774–2782]

Os grupos (`GRUPOS`, linha 1487) são, na ordem:
1. `'Lei 8.112/90 — Deveres (art. 116)'`
2. `'Lei 8.112/90 — Proibições (art. 117)'`
3. `'Lei 8.112/90 — Demissão (art. 132)'`
4. `'Outras (art. 130)'`
5. `'LAI (Lei 12.527/2011)'`
6. `''` (vazio, propositalmente sem optgroup)
7. `'Criadas pelo usuário'`

Cada `<option>` mostra `dispositivo — rótulo` (ex.: "art. 116, I, Lei nº 8.112/90 — Inassiduidade ao dever de exercer com zelo e dedicação").

**Contagem real do catálogo**: `NORMAS_BASE` (linha 1335) tem **65 normas** cadastradas de fábrica (confirmado por contagem de entradas `['N-116-...`, etc., no bloco 1335–1486). `buildCatalogo()` (linha 1416) as converte para objetos com campos `id, dispositivo, rotulo, descricaoTipo, gravidade, penaPrevista, elementoSubjetivoExigido, notasEnquadramento, relacoes`. O usuário pode adicionar normas residuais via "+ enquadramento" → mas normas totalmente novas (fora do catálogo de 65) só entram pelo formulário separado `abrirFormNorma()` (seção "13. FORMULÁRIO NOVA NORMA (residual)", linha 2993), que grava com prefixo `NU-` e cai no grupo "Criadas pelo usuário".

Ao lado do select aparece um `pill` colorido com gravidade e pena prevista (ex.: "leve · advertência"). [linha 2783]

Para cada enquadramento adicionado ("+ enquadramento", cria `{normaId:doc.catalogoNormas[0].id, elementoSubjetivo:'', fundamentacao:''}`), o formulário mostra:

- **"Norma"** (rótulo dinâmico: se afastado, vira "Norma (AFASTADA — <princípio>)") — o select agrupado acima.
- **"Elemento subjetivo \*"** — grupo de rádios com as opções exatas, nesta ordem [linha 2789]:
  - `Dolo direto` (valor `dolo_direto`)
  - `Dolo eventual` (valor `dolo_eventual`)
  - `Negligência` (valor `negligencia`)
  - `Imprudência` (valor `imprudencia`)
  - `Imperícia` (valor `impericia`)
  
  Há um aviso inline (`⚠`) se o elemento subjetivo escolhido conflitar com o `elementoSubjetivoExigido` da norma (ex.: "⚠ art. X exige DOLO. <nota>" ou "⚠ art. X é de natureza CULPOSA. <nota>"). [linhas 2793–2799]
- **"Fundamentação"** — `fieldArea` livre. [linha 2801]
- Nota de enquadramento da norma (hint, se `notasEnquadramento` preenchido no catálogo).
- Botão "✕ remover enquadramento".

**Multiplicidade de enquadramentos**: se 2+ enquadramentos ativos (não afastados), aparece banner "⚖ Multiplicidade de enquadramentos: este fato tem 2+ enquadramentos ativos. Classifique: concurso formal ou conflito aparente?" com botão "Abrir wizard de multiplicidade" (`abrirWizard`, linha 2914). O wizard tem 2 passos:
- Passo 1: "Uma única conduta violou mais de uma hipótese legal?" → botão "Sim, e as infrações coexistem → concurso formal" ou "Não — só uma hipótese deve prevalecer → conflito aparente".
- Passo 2 (só se conflito aparente): escolher **princípio aplicado** (`alternatividade`, `consuncao`, `subsidiariedade`, `especialidade` — com descrições fixas no objeto `PRINC`, linha 2931), **norma prevalente** (select) e **justificativa (obrigatória)** — bloqueia com "Escolha o princípio." / "Escolha a norma prevalente." / "Justificativa é obrigatória." se faltar algo. [linhas 2949–2978]

### Estado probatório

Calculado automaticamente (`calcEstadoProbatorio(f)`) e exibido como hint "Calculado automaticamente: <valor>". A comissão pode fazer **override** via select "(usar calculado: X)" / "Sobrescrever: suficiente" / "Sobrescrever: indícios" / "Sobrescrever: ausente". Se houver override, exige **"Justificativa do override (obrigatória)"** (`fieldArea`). Se o estado exibido (calculado ou override) não for "suficiente", aparece **"Elementos buscados (alimenta a pauta do Oitiva 360)"** com hint "O que falta provar? Vira \"elementos buscados\" da próxima oitiva." [linhas 2832–2851]

### Situação do fato

Rádio "Disposição da comissão": **"Ativo — será indiciado"** ou **"Arquivado — apurado, não indiciado"**. Se arquivado: banner informativo ("Fato arquivado não gera pendências e não entra na minuta; permanece no mapa como memória da decisão…") e **"Justificativa do arquivamento (obrigatória)"** com hint "Motivação jurídica: por que a comissão decidiu não indiciar este fato." [linhas 2854–2869]

### Validações no salvamento (`foot`, linhas 2893–2906)

- Título vazio → `$('#fatoErr').textContent='Informe o título do fato.'`
- Se `status==='arquivado'`: exige `justificativaArquivamento` não vazia → "O arquivamento exige justificativa." (fato arquivado **não** precisa estar completo em mais nada).
- Senão (fato ativo):
  - Se há override de estado probatório sem justificativa → "O override do estado probatório exige justificativa."
  - Para cada enquadramento sem `elementoSubjetivo` → "Todo enquadramento exige o elemento subjetivo."

Botão "Excluir" (só em edição, não em fato novo) pede `confirm('Excluir este fato?')`.

---

## 2. Vinculação de prova a fato

Localização: bloco `provBox` dentro de `abrirFormFato`, função `renderProv()`, linhas 2749–2763.

Mecanismo: **checkboxes multiseleção** (`class:'multiselect'`), uma por prova cadastrada em `doc.provas`. Cada linha mostra `${p.id} · ${p.titulo||'(sem título)'} — ${p.tipo}`.

```js
const cb=el('input',{type:'checkbox'}); cb.checked=f.provaIds.includes(p.id);
cb.addEventListener('change',()=>{ if(cb.checked){if(!f.provaIds.includes(p.id))f.provaIds.push(p.id);} else f.provaIds=f.provaIds.filter(x=>x!==p.id); });
```

- Marcar a checkbox → adiciona `p.id` a `f.provaIds`.
- Desmarcar → remove `p.id` de `f.provaIds`.
- Se não há nenhuma prova cadastrada: hint "Nenhuma prova cadastrada ainda."
- Botão **"+ criar prova daqui"** abre `abrirFormProva(null, callback)` que, ao salvar, empurra o novo id em `f.provaIds` (comentário no código reconhece que reabrir o fato preservando edições "exige regravar; simplificação: salva fato atual e reabre").

### Como aparece depois no mapa (`drawFatoCard`, linhas 2145–2208, e desenho de arestas linhas 2044–2058)

- É desenhada uma **linha (aresta bezier)** entre o cartão do fato e cada cartão de prova vinculada (`fato → prova`).
  - Se a prova é "direta" (`provaEhDireta(p)` e sem pendências P6a/P6b): traço **contínuo**, cor `var(--ink-2)`, espessura 2.5.
  - Caso contrário: traço **tracejado** (`stroke-dasharray:'6 5'`), cor cinza `#9AA3AD`, espessura 1.5.
- Se o fato não tem nenhuma prova vinculada (pendência **P1**), é desenhada uma aresta tracejada vermelha (`var(--estado-critico)`) terminando em seta (`marker-end:'url(#xend)'`) até o meio do vão fato→prova, sinalizando a lacuna.
- No cartão do fato (`drawFatoCard`), não há badge textual específica de "tem prova"/"sem prova" — o sinal visual principal é o **semáforo de estado probatório** (círculo colorido à esquerda do título: verde=`suficiente`, amarelo=`indícios`, vermelho=`ausente`, cinza=arquivado), e a badge de severidade no canto superior direito (`⛔` pendência crítica — inclui P1 sem prova; `⚠` pendência frágil).
- Provas que não sustentam nenhum fato ("órfãs", pendência P3) recebem um **desalinhamento visual deliberado** no eixo X (`x+=24`) no desenho do cartão de prova (linha 2096, comentário "desalinhamento deliberado (P3)").

Ao excluir uma prova (`excluirProvaFlow`, linha 2705), se ela sustenta fatos, o confirm mostra:
> `Esta prova sustenta ${N} fato(s): ${lista de ids}. Excluí-la pode disparar a pendência P1 (fato sem prova). Confirmar exclusão?`

Caso contrário:
> `Excluir esta prova órfã?`

---

## 3. Papel de pessoa (acusado, vítima, testemunha, pessoa em situação indefinida)

### Catálogo-fonte: `CATALOGO_COGER.papeis_pessoa` (linhas 622–681)

5 papéis, todos com `"status": "ativo"`:

| id | label (exato) | compromisso | direito_silencio | origem_permitida |
|---|---|---|---|---|
| `PAPEL.ACUSADO` | **Investigado/Acusado** | `false` | `true` | `["nexo-coger","oitiva-360"]` |
| `PAPEL.VITIMA` | **Vítima** | `false` | (não definido) | `["oitiva-360"]` |
| `PAPEL.TESTEMUNHA` | **Testemunha** | `true` | (não definido) | `["oitiva-360"]` |
| `PAPEL.DECLARANTE_INFORMANTE` | **Declarante/Informante** | `false` | (não definido) | `["oitiva-360"]` |
| `PAPEL.PESSOA_SITUACAO_INDEFINIDA` | **Pessoa em Situação Indefinida** | `false` | `true` | `["oitiva-360"]` |

Descrições literais relevantes (para o manual):
- **Investigado/Acusado**: "Servidor submetido a apuração disciplinar; objeto do processo. Não presta compromisso. Tem direito constitucional ao silêncio, com advertência da Lei 13.869/2019 (art. 15, parágrafo único, I): se exercido o silêncio, a comissão não formula questionamentos. Defensor facultativo (Súmula Vinculante nº 5/STF). O interrogatório deve ser o último ato da instrução (art. 159), com antecedência mínima de 3 dias úteis na intimação."
- **Vítima**: "Não é testemunha e não presta compromisso legal de dizer a verdade, não respondendo por falso testemunho — mas sujeita-se à denunciação caluniosa. Documentação própria: Termo de Depoimento, Termo de Declarações ou Alegações do Ofendido, conforme o caso." (com nota interna: "Definição única do catálogo; corrige bug do Oitiva 360 em que tipoSugeridoParaItem() marcava prova de vítima como compromissada:true… Nexo Coger não tinha nenhum papel de vítima antes desta rodada.")
- **Testemunha**: "Presta compromisso legal de dizer a verdade (art. 342, CP). Responde a perguntas de praxe sobre parentesco, amizade/inimizade, interesse e impedimento. Tem o dever de depor, ressalvado o direito de não produzir prova contra si mesma."
- **Declarante/Informante**: "Não presta compromisso legal de dizer a verdade. Ouvido em razão de vínculo com o investigado ou de participação anterior no contexto apurado. Não responde por falso testemunho, mas apela-se à sua colaboração voluntária com a apuração."
- **Pessoa em Situação Indefinida**: "Autos indicam possível envolvimento da pessoa no contexto fático, sem elementos ainda para tratá-la como investigada. Não presta compromisso de testemunha e tem facultado o direito ao silêncio, por cautela e analogia à vedação à autoincriminação. Exige consulta prévia à defesa sobre o enquadramento adotado." (nota: "Ausente no Nexo Coger antes desta rodada; item novo criado a partir da definição do Oitiva 360 (Orientações de Implementação, 2026-07-09).")

**Achado importante**: o campo `origem_permitida` do catálogo diz que 4 dos 5 papéis (todos exceto `PAPEL.ACUSADO`) são destinados apenas ao `oitiva-360`. Mas **o código do Nexo Coger não filtra por `origem_permitida`** — o select usa apenas `.filter(x=>x.status==='ativo')` (linhas 2610 e 3227). Ou seja, **os 5 papéis aparecem igualmente nos dois seletores do Nexo Coger**, independentemente do que `origem_permitida` declara. Vale documentar isso no manual como comportamento real, não como o que o catálogo "pretendia".

### Onde o seletor "Papel do depoente"/"Papel" aparece na interface

Há **dois** pontos, ambos lendo `CATALOGO_COGER.papeis_pessoa` dinamicamente (não hardcoded):

**(a) Formulário de prova, `abrirFormProva` → bloco "Detalhes do tipo" (`renderDetalhe`), linhas 2596–2651.**
Só aparece quando o **"Tipo de prova"** selecionado é **"Testemunhal"** (`testemunhal`) ou **"Declaração de informante"** (`declaracao_informante`). Campos, na ordem:
1. **"Deponente"** (`fieldText`) — nome livre.
2. **"Papel do depoente"** (`fieldSelect`) — opções = os 5 papéis ativos do catálogo, rotulados com o `label` exato de cada um. Valor padrão: `PAPEL.DECLARANTE_INFORMANTE` se o tipo de prova for "declaração de informante", senão `PAPEL.TESTEMUNHA`.
3. **"Compromissada?"** — rádio Sim/Não.
4. **"Houve contradita?" / "Acolhida?" / "Ref. autos"** — trio de campos sobre contradita.

**(b) Tela "Revisão de pauta" (para exportar oitiva), `abrirRevisaoPauta`, linhas 3190–3252.**
No bloco "Depoente" ao final do formulário: **"Nome"** (`fieldText`) e **"Papel (catálogo canônico)"** (`fieldSelect`, mesma fonte `CATALOGO_COGER.papeis_pessoa.filter(x=>x.status==='ativo')`). Valor padrão do objeto local `depoente = {nome:'', papelId:'PAPEL.TESTEMUNHA'}`.

Não há nenhum outro ponto no arquivo (`abrirFormAcusado` não tem seletor de papel — o "acusado" é um modelo de dados totalmente separado, sem `papelId`).

### O que muda ao escolher cada papel

No formulário de prova, ao trocar o **"Papel do depoente"**:
```js
v=>{ d.papelId=v; const pc=CATALOGO_COGER.papeis_pessoa.find(x=>x.id===v); if(pc) d.compromissada=!!pc.compromisso; renderDetalhe(); }
```
O campo **"Compromissada?"** é **automaticamente re-preenchido** conforme `compromisso` do papel escolhido: `true` só para `PAPEL.TESTEMUNHA` (o único com `"compromisso": true` no catálogo); os outros 4 papéis colocam `compromissada = false`. O usuário ainda pode sobrescrever manualmente via o rádio Sim/Não depois — a mudança de papel apenas define o valor inicial, não trava o campo.

Na tela "Revisão de pauta" (b), trocar o papel só atualiza `depoente.papelId` — não há efeito colateral em outro campo (não existe campo "compromissada" nessa tela).

**Inconsistência de inicialização observada**: quando o bloco de detalhe de depoente é criado pela primeira vez (`d.deponente===undefined`), o código faz:
```js
Object.assign(d,{deponente:'',papelId:(p.tipo==='declaracao_informante'?'PAPEL.DECLARANTE_INFORMANTE':'PAPEL.TESTEMUNHA'),compromissada:true,contradita:{...}});
```
`compromissada` é fixado em `true` **sempre**, mesmo quando o papel padrão é `PAPEL.DECLARANTE_INFORMANTE` (cujo `compromisso` no catálogo é `false`). Ou seja, ao abrir uma prova nova do tipo "Declaração de informante" pela primeira vez, o rádio "Compromissada?" nasce marcado em "Sim", contradizendo o catálogo — só se corrige se o usuário reselecionar o papel no dropdown (o que dispara o `renderDetalhe()` e recalcula `compromissada` a partir de `pc.compromisso`). Vale um alerta no manual: **conferir manualmente o campo "Compromissada?" ao abrir uma prova nova de declaração de informante**.

### Obrigatoriedade / opção vazia

Não existe opção em branco/"—" no select de papel em nenhum dos dois pontos: as opções são geradas só a partir da lista filtrada (`.map(x=>[x.id,x.label])`), sem inserir um `['','—']` inicial (diferente, por exemplo, do select de acusado em condutas, que tem `el('option',{value:''},'—')`, linha 2735). Portanto, sempre que o seletor de papel está visível, ele **sempre tem um valor selecionado** (o padrão automático de novo registro, ou o valor salvo anteriormente) — não há estado "papel não informado".

Não há nenhum texto de orientação no código sobre quando usar "Pessoa em Situação Indefinida" — a única explicação textual do papel está na `descricao` do catálogo (reproduzida acima) e não é exibida em nenhum tooltip/hint no formulário — o select mostra apenas o `label` curto ("Pessoa em Situação Indefinida") como texto da opção, sem a descrição jurídica completa aparecendo na interface.

---

## 4. Geração de indiciação (minuta do termo de indiciação)

Fluxo: `gerarMinutaFlow()` (linhas 3626–3656) → `validaMinuta()` (3671–3687) → `renderIndiciacao(id,dataDoc)` (3725–3813) ou `abrirListaIndiciacoes` (3658–3670) se mais de um indiciado.

### Pré-requisito bloqueante antes mesmo de abrir a tela

```js
const criticas=PENDENCIAS.filter(p=>p.nivel==='critico');
if(criticas.length){ alert('Há pendências críticas que impedem a indiciação. Veja o painel.'); return; }
```
Isso é checado **globalmente** (todo `doc.fatos`/`doc.provas`/`doc.acusados`, não só do indiciado que se quer gerar) via `computePendencias()` (linhas 1739–1802). Pendências críticas possíveis (todas fecham a geração se presentes):
- **P1** — "Fato sem prova vinculada — alegação sem evidência" (a menos que haja override de estado probatório com justificativa preenchida).
- **P2** — "Fato sem enquadramento legal" — crítico **apenas** a partir da fase `indiciacao_em_elaboracao` em diante (`FASES_INDICIACAO_ADIANTE`); nas fases anteriores é apenas frágil.
- **P5** — "Conduta não individualizada — risco de indiciação genérica (nulidade)" (fato sem conduta descrita, ou conduta sem `acusadoId`).
- **P8** — "Alternatividade violada: enquadramentos doloso e culposo simultâneos no mesmo fato" (2+ enquadramentos ativos não resolvidos como conflito aparente, com um exigindo dolo e outro culpa).

Pendências **frágeis** (P3, P6a, P6b, P6c, P7) **não bloqueiam**, mas aparecem como aviso dentro da própria tela de geração:
> banner "⚠ Pendências frágeis ainda abertas: <códigos>. A minuta pode ser gerada, mas revise-as."

### Tela que abre (corpo do modal "Gerar minuta do termo de indiciação")

1. Hint: "Selecione os indiciados (um documento por indiciado):"
2. Uma checkbox por acusado cadastrado (`${a.id} — ${a.nome||'(sem nome)'}`), **todas marcadas por padrão** (`cb.checked=true`).
3. **"Data do documento"** (`fieldText`, tipo `date`), pré-preenchida com a data de hoje (`new Date().toISOString().slice(0,10)`), hint: "Usada no fecho e nas assinaturas. Sugestão inicial: hoje."
4. (condicional) banner de pendências frágeis, se houver.

### Validação ao clicar "Gerar minuta" (`validaMinuta(ids)`, linhas 3671–3687)

- Se nenhum acusado selecionado: `alert('Selecione ao menos um indiciado.')`.
- Senão, roda `validaMinuta`, que acumula mensagens de campos essenciais faltantes:
  - `• Número do processo (dados do processo).`
  - `• Nome do presidente da comissão.`
  - por indiciado: `• Nome do indiciado <id>.` / `• Cargo do indiciado <nome ou id>.`
  - `• <nome ou id> não possui fato ativo imputado (todos arquivados?).` (se não há fato ativo com conduta dele)
  - por fato ativo do indiciado: `• Descrição do fato <id>.` / `• Enquadramento do fato <id>.`
- Se `faltas.length`: `alert('Campos essenciais em branco impedem a geração:\n\n'+faltas.join('\n'))` e a geração é interrompida.

### O que é gerado ao final

Se 1 indiciado selecionado: abre direto `renderIndiciacao(id,dataDoc)` (visualização/impressão). Se mais de um: abre lista intermediária "Termos gerados — Indiciação" com hint "Um Termo de Indiciação por indiciado. Abra cada um individualmente para visualizar ou imprimir." e um botão "Visualizar / Imprimir" por indiciado.

Estrutura do documento (`renderIndiciacao`, HTML impresso via `openPrint`), em ordem:
1. Cabeçalho institucional fixo: "MINISTÉRIO DA FAZENDA — RECEITA FEDERAL DO BRASIL" / "CORREGEDORIA DA RECEITA FEDERAL DO BRASIL (Coger/RFB) — <unidade>"; título "Indiciação"; linha "Processo Administrativo Disciplinar nº <número> — Rito <rito>"; linha da portaria de instauração; linha "Servidor: <nome>, <cargo>, matrícula <matrícula>".
2. Tabela de qualificação (Nome, Matrícula, Cargo, Lotação, Qualificação complementar se houver).
3. **"Dos fatos e das condutas"** — um parágrafo por fato ativo imputado ao indiciado (na ordem narrativa definida no painel, fatos arquivados são ignorados), com descrição, período e local; e um segundo parágrafo com a conduta individualizada (comissiva/omissiva) daquele indiciado especificamente.
4. **"Das provas"** — por fato, lista as provas vinculadas com referência aos autos, e trechos significativos citados entre aspas (bloco `.quote`).
5. **"Do enquadramento legal"** — por fato, cada enquadramento ativo ("a conduta amolda-se ao <dispositivo> (<rótulo>), a título de <elemento subjetivo>. <fundamentação>"), mais nota de concurso formal ou de qual norma prevalece em conflito aparente, quando aplicável.
6. **"Síntese dos fatos, provas e enquadramentos"** — tabela `tabelaFatoProvaEnquadramento` com colunas "Fatos de que se acusa" / "Provas acerca dos fatos" / "Fls. dos autos" / "Enquadramentos".
7. **"Das alegações da defesa não acatadas"** — bloco editável (`contenteditable`) com o texto de `a.alegacoesDefesaNaoAcatadas`, ou placeholder "[Inserir alegações da defesa não acatadas durante a instrução, se houver, e a motivação de sua rejeição]" se vazio.
8. **"Do encerramento"** — texto padrão citando art. 161, §1º da Lei 8.112/90 (citação para defesa escrita) e ressalva de que o enquadramento pode ser adequado no Relatório Final; data e cidade; bloco de assinatura em 3 colunas (Vogal | Presidente | Vogal, cada um rotulado "Assinatura digital").

Efeito colateral: na primeira geração bem-sucedida, `doc._minutaGerada=true` e `prazosSecOpen=true` são setados (abre a seção de prazos no painel).

---

## 5. Outras observações úteis — textos de aviso/confirmação visíveis ao usuário

### Cadastro de fato (`abrirFormFato`)
- Excluir fato: `confirm('Excluir este fato?')`
- Erros inline (não são `alert`, aparecem em `<span id="fatoErr">`):
  - `'Informe o título do fato.'`
  - `'O arquivamento exige justificativa.'`
  - `'O override do estado probatório exige justificativa.'`
  - `'Todo enquadramento exige o elemento subjetivo.'`

### Wizard de multiplicidade (`abrirWizard`)
- Erros inline: `'Escolha o princípio.'` / `'Escolha a norma prevalente.'` / `'Justificativa é obrigatória.'`

### Cadastro de prova (`abrirFormProva` / `excluirProvaFlow`)
- Erro inline: `'Informe o título da prova.'`
- Exclusão com fatos afetados: `` `Esta prova sustenta ${N} fato(s): ${ids}. Excluí-la pode disparar a pendência P1 (fato sem prova). Confirmar exclusão?` `` (via `confirm`)
- Exclusão sem fatos afetados: `'Excluir esta prova órfã?'` (via `confirm`)

### Cadastro de acusado (`abrirFormAcusado`)
- Excluir acusado: `confirm('Excluir este acusado? As condutas vinculadas a ele nos fatos serão removidas.')`
- Erro inline: `'Informe o nome do acusado.'`

### Geração de minuta / indiciação (`gerarMinutaFlow`)
- `alert('Há pendências críticas que impedem a indiciação. Veja o painel.')` — bloqueia antes de abrir a tela.
- `alert('Selecione ao menos um indiciado.')`
- `alert('Campos essenciais em branco impedem a geração:\n\n'+faltas.join('\n'))`

### Revisão de pauta / papel do depoente (`abrirRevisaoPauta`)
- `alert('Informe o nome do depoente.')`
- `alert('Nenhum ponto de instrução confirmado — nada a exportar.')`

### Notas de arquitetura relevantes para o manual
- O modelo de "acusado" (`doc.acusados[]`) é **totalmente separado** do sistema de papéis do catálogo (`papeis_pessoa`) — um acusado nunca tem `papelId`; o papel só existe no contexto de "depoente" (prova testemunhal/declaração de informante) e na tela de revisão de pauta.
- O catálogo de papéis (`CATALOGO_COGER.papeis_pessoa`) é lido dinamicamente pelo Nexo Coger (comentário explícito no código, linhas 2602–2605: "Lista lida de CATALOGO_COGER.papeis_pessoa, não hardcoded, para que qualquer papel novo do catálogo apareça aqui automaticamente"), mas o filtro aplicado é só `status==='ativo'`; o campo `origem_permitida` (que sugere que 4 dos 5 papéis seriam exclusivos do Oitiva 360) **não é respeitado** na prática — todos os 5 aparecem nos dois seletores do próprio Nexo Coger.
- Bug potencial identificado: inicialização de `compromissada:true` fixa ao criar o bloco de detalhe de depoente pela primeira vez, mesmo quando o papel padrão correspondente (`PAPEL.DECLARANTE_INFORMANTE`) tem `compromisso:false` no catálogo — só se autocorrige se o usuário reselecionar o papel no dropdown.

---

## 6. Adendo (rodada de implementação 2026-07-12) — Tela "Dados do Processo" (gate) e selo de origem oitiva

### 6.1 Tela "Dados do Processo" — primeira etapa, bloqueante

Novo bloco HTML `<div class="gate" id="gate">` (linhas ~510–516), fixo em tela cheia, `z-index:9999` — acima de `#overlay`/`#modal`. Conteúdo montado dinamicamente por `renderGateProcesso()` (função `13-bis`, logo antes de `abrirFormProcesso()`). Escreve **diretamente** em `doc.processo` (não é uma cópia como `abrirFormProcesso`), com `scheduleSave()` a cada alteração — autosave por campo, sem "Cancelar/Salvar".

Campos, na ordem exibida (rótulos exatos):
1. **"Número do processo"** (`fieldText`, id do input gerado por `fieldText`, sem `id` fixo — localizável por `.field:has-text("Número do processo") input`) — único campo obrigatório para liberar o gate.
2. **"Tipo (PN CGU 27)"** (`<select>` agrupado, mesmo catálogo `TIPOS_PROCESSO` já usado em `abrirFormProcesso` — IP/SINVE/SINPA/SINAC/PAD, agrupados "— Investigativos —"/"— Acusatórios —"). *Desvio da especificação*: o pedido original citava um select simples "PAD, PAR, Sindicância"; optei por reaproveitar o catálogo `TIPOS_PROCESSO` já existente (mais preciso, 5 tipos reais da PN CGU 27/2022) em vez de introduzir uma segunda lista de tipos divergente da já usada em `abrirFormProcesso`/`renderIndiciacao` (`doc.processo.tipo==='PAD'?'CI':'CS'`, linha ~3863).
3. **"Portaria de instauração — nº"** (`fieldText`) — grava em `doc.processo.comissao.portariaInstauracao.numero`.
4. **"Data de instauração"** (`fieldText` tipo `date`, hint "Marco de interrupção da prescrição (art. 142, §3º, Lei 8.112/90).") — grava em `doc.processo.comissao.portariaInstauracao.data`. Não é um campo novo: é o mesmo `portariaInstauracao.data` que já existia (reaproveitado, só renomeado na UI da nova tela).
5. **"Presidente da comissão"** — trio Nome/Cargo/Matrícula → `doc.processo.comissao.presidente`.
6. **"Secretário(a)"** — trio Nome/Cargo/Matrícula → `doc.processo.comissao.secretario` (**campo novo** no modelo de dados; não existia antes desta rodada). Adicionado a `docVazio()` e retrocompatibilizado em `migra()`.
7. **"Vogal(is)"** — lista repetível de trios Nome/Cargo/Matrícula, botão **"+ Adicionar vogal"**, botão "✕" por linha para remover. Grava em `doc.processo.comissao.membros` — **o nome interno do array continua `membros`** (não renomeado para `vogais`, para não tocar identificador interno já usado em `blocoAssinatura3`/`renderIndiciacao`/`migra`); só o rótulo visível virou "Vogal N" (era "Membro N") e o botão "+ Adicionar vogal" (era "+ membro"). O mesmo rótulo foi aplicado ao modal de edição já existente `abrirFormProcesso()` (bloco "Comissão"), para manter os dois pontos de edição consistentes entre si.

Rótulos e agrupamento (Presidente → Secretário(a) → Vogais, com "+ Adicionar vogal") replicam literalmente o vocabulário da Etapa 1 do Oitiva 360 e da própria "Tela do Processo" do Oitiva 360 (`oitiva-360.html`, linhas ~1562–1615 e ~1650–1702).

### 6.2 Lógica do gate

- `processoGateCompleto()` → `!!(doc.processo.numero && doc.processo.numero.trim())`.
- `atualizarGateProcesso()` → mesmo padrão de `atualizarAvisoMatriz()`/`atualizarAvisoNumeroProcesso()` do Oitiva 360: desabilita o botão `#gateBtnContinuar` e mostra `<div class="gate-aviso">` com o texto "Preencha ao menos o \"Número do processo\" para liberar o acesso ao cadastro de fatos, provas e ao mapa — o número também nomeia os arquivos exportados." enquanto incompleto.
- `abrirGateProcesso()` → renderiza e exibe (`display:flex`); `fecharGateProcesso()` → esconde e chama `render()`.
- Disparado em `init()`, logo após o primeiro `render()`: `if(!processoGateCompleto()) abrirGateProcesso();`. Também disparado por `limparTudo()` (que zera `doc.processo.numero`), reabrindo o gate após "Limpar tudo".
- O gate é um elemento fixo cobrindo 100% da viewport com `z-index` acima de tudo — o app por trás (`#btnAddFato`, `#btnMenu`, etc.) continua no DOM mas fica inacessível a clique/tab enquanto o gate está visível (confirmado via teste automatizado: `page.click('#btnAddFato')` sob o gate estoura timeout de "elemento não clicável").
- **Rascunhos antigos do localStorage**: se já existir um dossiê salvo com `doc.processo.numero` preenchido, o gate não aparece (mesma UX do Oitiva 360 — o gate é first-run, não uma tela obrigatória a cada carregamento).

### 6.3 Nomeação de arquivos exportados pelo número do processo

Levantamento de **todas** as funções de export (`baixar(...)`, 2 ocorrências no arquivo):
- `exportJson()` (linha ~3122) — já usava `doc.processo.numero` antes desta rodada: `nexo-coger-<numero>-<data>.json`. Sem alteração necessária.
- `gerarPautaPorDepoente()` (linha ~3291, dispara a partir de "Pauta de instrução por depoente") — **alterado nesta rodada**: antes só usava o nome do depoente (`nexo-coger-pauta-<depoente>-<data>.json`); passou a incluir também o número do processo: `nexo-coger-pauta-<numero>-<depoente>-<data>.json`.
- `gerarMinutaFlow`/`gerarIntimacaoFlow`/`printMap` não geram download de arquivo — usam `openPrint()` (impressão do navegador), fora do escopo de "nome de arquivo exportado".
- `manual/screenshot.js` foi ajustado (`runNexo`) para preencher o gate antes de dirigir o resto do fluxo, já que ele passou a bloquear `#btnMenu` no primeiro carregamento.

### 6.4 Selo "🎙 Oitiva" no cartão de prova (`drawProvaCard`)

**Achado importante antes de implementar** (confirmado por grep, não presumido): o contrato de retorno de oitiva "Rodada 6" (`origem:"oitiva-360"`, `pauta_id`, `rodada_id`, `id_ponto`) documentado no comentário de `oitiva-360.html` ("RODADA 6 do contrato entre ferramentas — Retorno da prova (contexto do acusado no Nexo Coger)", função `construirEnvelopeRetorno`) **não cria uma prova em `doc.provas`** — ele popula `acusado.provasContexto[]` (consumido por `importarRetornoOitiva()` → `mapearRetornoContexto()`, nexo-coger.html linha ~3600), que já tinha seu próprio selo dourado `🎙` no **cartão de FATO** (`contextoOitivaFato`, linha ~2193, pré-existente, fora do escopo desta rodada).

O contrato que efetivamente cria itens em `doc.provas` a partir do Oitiva 360 é o botão "Exportar prova(s) para o Nexo" (`oitiva-360.html`, handler de `#btn-confirmar-exportar-prova`, ~linha 5984), que gera `{origem:"oitiva-360", processo, provas:[{fatoIds, tipo, titulo, ...}]}` — **sem** `pauta_id`/`rodada_id`/`id_ponto` por item na versão atual do Oitiva 360. Esse arquivo é consumido no Nexo Coger por `importarProva()` → `revisarImportacaoProva(d)` → `aplicarImportacaoProva(aprovadas, d)`.

Implementação adotada (fiel ao contrato real, e preparada para quando/se o Oitiva 360 passar a emitir `pauta_id`/`rodada_id`/`id_ponto` por item de prova, já que a task pedia exatamente esses 3 campos no tooltip):
- `revisarImportacaoProva(d)` agora passa `d` para `aplicarImportacaoProva(aprovadas, d)` (antes só recebia `aprovadas`).
- `aplicarImportacaoProva` marca `nova.origemOitiva = {pautaId, rodadaId, idPonto}` quando `d.origem==='oitiva-360'` (lendo `it.pauta_id||it.pautaId`, etc. — hoje resultam em `''` porque o Oitiva 360 ainda não exporta esses 3 campos nesse contrato específico, mas o campo `origemOitiva` já fica presente e não-nulo, então o selo aparece mesmo assim, só com "—" nos 3 IDs). Provas importadas do Veritas (`revisarImportacaoVeritas`/`aplicarImportacaoVeritas`, que já gravam `origemVeritas`) **não** passam por este caminho, logo nunca recebem `origemOitiva`.
- `migra()` faz backfill de `pr.origemOitiva=null` em provas de rascunhos antigos que não tinham o campo.
- `docVazio()` não precisou de alteração (o campo só existe em provas concretas, nunca no array vazio inicial).
- `drawProvaCard()` (linha ~2210): novo badge, inserido logo após o badge `🌐` (Veritas) e antes do `§` (trechos): `if(p.origemOitiva){ badge(node,bx,20,'🎙','var(--rfb-gold-600)', 'Origem: retorno de oitiva (Oitiva 360) · pauta_id: '+... ); bx-=20; }`. Usa a mesma variável `--rfb-gold-600` já usada no selo homônimo do cartão de fato (`contextoOitivaFato`), para manter a mesma paleta "dourado = Oitiva 360" em toda a ferramenta. Tooltip nativo (`<title>` dentro do `<text>` SVG, mesmo padrão de todos os outros badges de `drawProvaCard`/`drawFatoCard`) mostra `pauta_id`/`rodada_id`/`id_ponto`.
- Testado via Playwright headless (`doc`/`aplicarImportacaoProva` chamados diretamente por `page.evaluate`, sem passar por upload de arquivo real): confirmado que o selo aparece com o tooltip correto quando `origemOitiva` está presente, e que uma prova com apenas `origemVeritas` (sem `origemOitiva`) não recebe o selo.
