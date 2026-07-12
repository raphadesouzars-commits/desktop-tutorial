# Auditoria de código-fonte — Veritas Digital - Coger

Arquivo auditado: `/home/user/desktop-tutorial/ferramentas/veritas.html` (SPA vanilla JS, IIFE única, ~3081 linhas / ~1,2 MB). Todas as citações abaixo são texto literal extraído por leitura direta do arquivo (linhas indicadas entre colchetes).

---

## 1. Cadastro de prova nova (wizard) — campo a campo

O wizard (`viewItemWizard`, L2154) tem 4 etapas controladas por `UI.wizardStep`, com barra de progresso (`stepBarHtml`, L2146) rotulada `WIZARD_STEPS = ["Identificação", "Proveniência", "Arquivos", "Linha do tempo"]` (L2145). Navegação: botão "Avançar →" chama `App.avancarStep()`, que só avança se `App._validarStep(UI.wizardStep)` retornar true; botão "Voltar ←" (a partir do step 2) não valida. No último step o botão muda para "Salvar item" (`App.salvarItem()`), que revalida os steps 1, 2 e 3 antes de gravar (L2949-2950).

### Etapa 1 — Identificação (`stepIdentificacao`, L2177)

Antes dos campos, exibe a dica `dica_fishing` (ver seção 6).

| Ordem | Label exato | Tipo | Obrigatório? | Opções / observações |
|---|---|---|---|---|
| 1 | `Título/descrição` | input texto (`oninput`, salvamento silencioso via `setDraftQuiet`) | **Obrigatório** — `_validarStep(1)`: `if (!d.titulo.trim()) { toast("Informe o título/descrição.", "danger"); return false; }` (L2892) | placeholder: `Ex.: Extrato bancário — conta XXXX, período 01/2023 a 12/2023` |
| 2 | `Categoria` | select (`onchange`) | **Obrigatório** — `if (!d.categoria) { toast("Selecione a categoria.", "danger"); return false; }` (L2893) | Primeira opção `Selecione…` (value vazio); demais opções vêm de `CATEGORIAS` (L1792-1799): `print_sistema`→"Print de sistema", `documento_financeiro`→"Documento financeiro", `comunicacao`→"Comunicação (e-mail/mensagem)", `foto_video`→"Foto/vídeo", `laudo_pericia`→"Laudo/perícia", `oficio`→"Ofício", `decisao_judicial`→"Decisão judicial", `documento_fisico`→"Documento físico", `dispositivo_fisico`→"Dispositivo/mídia física (HD, celular, pendrive etc.)", `termo_oitiva`→"Termo de oitiva" (comentário no código: "categoria criada só pela importação do Oitiva 360" — não é selecionável manualmente no wizard porque não é oferecida como fluxo de criação normal, mas aparece como option no select mesmo assim), `outro`→"Outro" |
| 3 | `Nº/folha nos autos` (com hint `opcional`, `<span class="rfb-label__hint">opcional</span>`) | input texto | Opcional | — |
| 4 | `Vinculado à matriz de apuração` | input texto | Opcional (não checado em `_validarStep`) | placeholder: `Fato/hipótese que este elemento sustenta` |
| 5 | `Sigilo/classificação` | select | Opcional (default `acesso_restrito`, não validado) | `SIGILO` (L1805): `publico`→"Público nos autos", `acesso_restrito`→"Acesso restrito", `sigiloso`→"Sigiloso" |

Dependência condicional: se `categoria === 'comunicacao'`, exibe a dica `dica_privacidade_consentimento` logo após a grade de campos (L2193).

Campo seguinte, sempre visível:

| Label exato | Tipo | Obrigatório? | Opções |
|---|---|---|---|
| `Extrato ou conteúdo integral?` | radio (name="integral") | Implícito — sempre tem valor default `true` | Opção "sim": rótulo visível `Sim — conteúdo integral`; opção "nao": rótulo visível `Não — extrato/trecho parcial` (L2178-2181) |

Dependência: se o radio estiver em "Não" (`d.conteudoIntegral === false`), aparece:

| Label exato | Tipo | Obrigatório? | Observações |
|---|---|---|---|
| `Justificativa` (hint `obrigatória`) | textarea (2 linhas) | **Obrigatório apenas quando conteudoIntegral=false** — `if (!d.conteudoIntegral && !d.justificativaExtrato.trim()) { toast("Justificativa obrigatória para extrato parcial.", "danger"); return false; }` (L2894) | Logo abaixo exibe a dica `dica_integralidade` |

### Etapa 2 — Proveniência (`stepProveniencia`, L2201)

Campo raiz, sempre presente:

| Label exato | Tipo | Obrigatório? | Opções (value / label visível / subtexto) |
|---|---|---|---|
| (sem label de campo — é um grupo de radio) | radio (name="proveniencia") | **Obrigatório** — `if (!d.proveniencia.tipo) { toast("Selecione o tipo de proveniência.", "danger"); return false; }` (L2897) | `gerado_internamente` — "A) Gerado internamente" — subtexto: "Print, PDF exportado, foto de diligência — a ferramenta gera o hash no momento da coleta."; `recebido_hash_oficial` — "B) Recebido com hash oficial" — subtexto: "PJe, ofício de compartilhamento, operação conjunta — a comissão declara o hash da origem."; `extraido_sistema_trilha` — "C) Extraído de sistema com trilha própria" — subtexto: "Extração ativa pela própria Coger, com acesso institucional." |

Os campos abaixo só aparecem depois de escolhido o tipo (nenhum é validado obrigatoriamente em `_validarStep(2)` — a única checagem de fato é a seleção do `tipo`). Ver seção 2 para detalhamento completo por ramo.

Ao final da etapa 2, independentemente do tipo escolhido (mas só se `d.proveniencia.tipo` já tiver algum valor), aparece o bloco de elemento físico (`elementoFisicoBlocoHtml`, L2249):

| Label exato | Tipo | Obrigatório? |
|---|---|---|
| `Este item inclui um elemento físico (documento físico, HD, celular, mídia removível etc.), além do(s) arquivo(s) digital(is)?` | checkbox | Opcional |

Se marcado, exibe a dica `dica_lacre_fisico` e mais estes campos:

| Label exato | Tipo | Opções |
|---|---|---|
| `Tipo de elemento físico` | select | `ELEMENTO_FISICO_TIPOS` (L1800-1803): `documento_fisico`→"Documento físico (papel)", `hd_armazenamento`→"HD/dispositivo de armazenamento", `celular_smartphone`→"Celular/smartphone", `midia_removivel`→"Mídia removível (pendrive, CD/DVD)", `outro`→"Outro" |
| `Nº do lacre` | input texto | — |
| `Condição do lacre` | select | `CONDICAO_LACRE` (L1804): `intacto`→"Íntegro", `rompido`→"Rompido", `nao_lacrado`→"Não lacrado" |
| `Descrição do lacre (cor/característica)` | input texto | — |
| `Local de guarda física` | input texto | — |
| `Responsável pela guarda física` | input texto | — |

Nenhum destes campos de elemento físico é obrigatório em `_validarStep` — a única consequência de marcar `presente=true` é que a etapa 3 (Arquivos) deixa de exigir arquivo anexado (ver etapa 3).

### Etapa 3 — Arquivos (`stepArquivos`, L2274)

Se `d.proveniencia.tipo === ""` (proveniência não definida ainda), mostra alerta: `Defina a proveniência (etapa anterior) antes de adicionar arquivos.`

Formulário de anexação de arquivo (repete-se por arquivo adicionado, via cards):

| Label exato | Tipo | Obrigatório? | Dependência |
|---|---|---|---|
| `Descrição do arquivo no pacote` | input texto (`id="novoArquivoDescricao"`) | Opcional (default `""` se vazio) | placeholder: `Ex.: extrato bancário, print de conversa…` |
| `Hash declarado pela origem (deste arquivo)` | input texto (`id="novoArquivoHashDeclarado"`) | Opcional, mas só aparece se `proveniencia.tipo === "recebido_hash_oficial"` **e** `proveniencia.modoHashDeclarado === "por_arquivo"` (variável `porArquivo`) | placeholder: `sha256…` |
| `Arquivo` | input file (`id="novoArquivoInput"`) | **Obrigatório ao clicar em "Calcular hash e adicionar"** — `if (!file) { toast("Selecione um arquivo.", "danger"); return; }` (L2908) | — |

Botão: `Calcular hash e adicionar` (`App.adicionarArquivoDraft()`). Logo abaixo, se a proveniência já foi definida, aparece a dica `dica_carimbo_local`.

Validação de step (`_validarStep(3)`, L2899-2901): `if (d.arquivos.length === 0 && !d.proveniencia.elementoFisico.presente) { toast("Adicione ao menos um arquivo (ou marque o elemento físico na Proveniência).", "danger"); return false; }` — ou seja, é obrigatório ter ao menos 1 arquivo **a menos que** o elemento físico esteja marcado como presente na etapa 2.

Mensagens auxiliares condicionais (sem input associado):
- Se `d.arquivos.length === 0` e elemento físico presente: `Elemento físico marcado na Proveniência — arquivo digital é opcional aqui (ex.: foto do objeto lacrado).`
- Se `d.arquivos.length === 0` e elemento físico ausente: `É necessário ao menos um arquivo para salvar o item.`

### Etapa 4 — Linha do tempo (`stepLinhaDoTempoResumo`, L2313)

| Label exato | Tipo | Obrigatório? |
|---|---|---|
| `Responsável pelo registro na ferramenta` | input texto | Opcional (não validado) |
| `Custodiante atual` | input texto (placeholder `Quem responde pelo item agora`) | Opcional |
| `Observações livres` | textarea (2 linhas) | Opcional |

Não há `_validarStep(4)` — a validação final ao clicar em "Salvar item" reexecuta apenas os steps 1, 2 e 3. Abaixo dos campos, título fixo `Prévia da linha do tempo (gerada ao salvar)`, com lista de eventos (se houver) ou texto `Os eventos automáticos (identificação, cálculo de hash) serão gerados ao salvar o item.`

---

## 2. Proveniência interna vs. externa

`PROVENIENCIA_TIPOS` (L1806-1810):
```
gerado_internamente: "A) Gerado internamente"
recebido_hash_oficial: "B) Recebido com hash oficial"
extraido_sistema_trilha: "C) Extraído de sistema com trilha própria"
```

Lógica de troca de formulário: `stepProveniencia` (L2201-2248) monta a variável `extra` conforme `d.proveniencia.tipo`.

**A) `gerado_internamente`** — campos exibidos (via `campoDraft`, todos input texto):
- `Quem coletou` (`proveniencia.quemColetou`)
- `Contexto da coleta` (`proveniencia.contextoColeta`) — placeholder: `Diligência, atendimento, consulta a sistema…`
- `Local/situação` (`proveniencia.localSituacao`)

**B) `recebido_hash_oficial`** — primeiro exibe a dica `dica_custodia_externa`, depois:
- `Processo judicial de origem` (`proveniencia.processoJudicialOrigem`), input texto
- `Órgão expedidor` (`proveniencia.orgaoExpedidor`), input texto
- `Natureza do compartilhamento` (`proveniencia.naturezaCompartilhamento`), select com `NATUREZA_COMPARTILHAMENTO` (L1811-1814): `mandado`→"Mandado", `oficio`→"Ofício", `decisao_compartilhamento`→"Decisão de compartilhamento de prova", `operacao_conjunta`→"Operação conjunta"
- `Nome/codinome da operação` (`proveniencia.nomeOperacao`), input texto
- `Data do ofício/decisão` (`proveniencia.dataOficio`), input type="date"
- `Data de recebimento pela Coger` (`proveniencia.dataRecebimento`), input type="date"
- `Nº do ofício/expediente` (`proveniencia.numeroOficio`), input texto

Depois, campo de grupo: `Modo do hash declarado pela origem` — radio (name="modoHash"):
- value `por_arquivo` → rótulo: `Hash declarado individualmente por arquivo`
- value `pacote` → rótulo: `Hash único do pacote compactado`

Só quando `modoHashDeclarado === "pacote"`, aparecem mais estes campos exclusivos:
- `Hash declarado do pacote` (`proveniencia.hashDeclaradoPacote`), input texto
- `Algoritmo declarado` (`proveniencia.algoritmoDeclarado`), input texto (default `"SHA-256"`)

...e um alerta de aviso fixo: `Modo pacote: a comparação por arquivo individual não é aplicável — cada arquivo é conferido, na Conferência Geral, contra o hash local originalmente registrado (consistência interna), não contra o hash do pacote.`

Quando `modoHashDeclarado === "por_arquivo"` (o default), o campo exclusivo é, na etapa 3 (Arquivos), o `Hash declarado pela origem (deste arquivo)` por arquivo anexado (ver seção 1, etapa 3) — este é o único caso em que aparece o campo de hash declarado por arquivo individual.

**C) `extraido_sistema_trilha`** — campos exibidos:
- `Sistema de origem` (`proveniencia.sistemaOrigem`), input texto — placeholder: `PJe, e-CAC, outro`
- `ID do documento no sistema de origem` (`proveniencia.idDocumentoOrigem`), input texto
- `Nº do processo de origem` (`proveniencia.processoOrigem`), input texto
- `Usuário que extraiu` (`proveniencia.usuarioExtraiu`), input texto
- `Data/hora da extração` (`proveniencia.dataHoraExtracao`), input type="datetime-local"

O bloco de elemento físico (checkbox "Este item inclui um elemento físico...") aparece em todos os três casos, sempre depois dos campos específicos, desde que `d.proveniencia.tipo` já tenha algum valor (L2247: `(d.proveniencia.tipo ? elementoFisicoBlocoHtml(d) : "")`).

---

## 3. Cálculo de hash

Funções relevantes:
- `sha256Hex(arrayBufferOrString)` (L1755-1761): calcula SHA-256 via `crypto.subtle.digest`, retorna hex.
- `hashFile(file)` (L1762-1765): lê o arquivo bruto com `file.arrayBuffer()` e passa para `sha256Hex` — hash é sobre **o conteúdo binário bruto do arquivo anexado**, não sobre metadados.
- `hashDossieMetadata(dossie)` (L1766-1770): hash separado, sobre uma cópia JSON do dossiê inteiro (com `hashDoDossie` zerado antes) via `stableStringify` — usado só para o campo `hashDoDossie` do dossiê (integridade do arquivo exportado/importado), não é o mesmo hash mostrado por arquivo de prova.

**Momento exato do cálculo do hash do arquivo de prova**: ocorre ao clicar no botão `Calcular hash e adicionar` (`App.adicionarArquivoDraft()` no wizard, L2905, ou `App.adicionarArquivoExistente()` na tela de detalhe, L2917) — ou seja, **no momento em que o usuário anexa o arquivo**, não ao salvar o item inteiro e não automaticamente ao selecionar o arquivo no input. Ambas chamam `App._construirArquivo(file, descricao, hashDeclarado, proveniencia)` (L2932), que executa `var hashLocal = await hashFile(file);` como primeiro passo.

**Comparação com hash declarado**: dentro de `_construirArquivo` (L2932-2947):
```
var isB = proveniencia.tipo === "recebido_hash_oficial";
var porArquivo = isB && proveniencia.modoHashDeclarado === "por_arquivo";
var resultado = "nao_aplicavel";
if (porArquivo && hashDeclarado) resultado = (hashLocal.toLowerCase() === hashDeclarado.toLowerCase()) ? "confere" : "diverge";
```
Ou seja: a comparação automática só ocorre quando proveniência = B (recebido com hash oficial) **e** modo = "por_arquivo" **e** o campo de hash declarado foi preenchido para aquele arquivo específico. Nos demais casos (A, C, ou B em modo "pacote", ou campo de hash declarado vazio) o resultado fica `"nao_aplicavel"` (rótulo visível: `Não aplicável`, de `RESULTADO` L1816: `confere`→"Confere", `diverge`→"Diverge", `nao_aplicavel`→"Não aplicável").

Eventos de linha do tempo automáticos gerados no momento do anexo (via `registrarEventoArquivo`): `arquivo_adicionado` (label "Arquivo adicionado ao item ao pacote" — na verdade label é "Arquivo adicionado ao item", `EVENTO_TIPOS.arquivo_adicionado`, L1822), `hash_local_calculado` ("Hash local calculado", L1820), e — só se houver hash declarado por arquivo — `hash_declarado_recebido` ("Hash declarado recebido", L1819).

Depois de salvo, há uma segunda função de comparação — **Conferência de integridade** — em `App.conferirArquivo(itemId, arquivoId)` (L3033-3047): o usuário anexa um novo arquivo (input `id="conf_" + arquivoId"`) para reconferência; calcula `hashRecalculado = await hashFile(file)` e compara contra `referenciaHash(it, a)` (não lida integralmente neste levantamento, mas usada como "referência" de comparação — presumivelmente o `hashLocal` originalmente gravado ou o hash declarado, dependendo do caso). Resultado gera evento `conferencia_arquivo`, com observação fixa em caso de divergência: `Divergência encontrada na conferência — ver princípio do prejuízo.`

**Dica/tooltip literal sobre o carimbo de data/hora** (`CATALOGO.dicas.dica_carimbo_local`, L1783, exibida logo abaixo do botão "Calcular hash e adicionar" na etapa 3 do wizard):
> "O carimbo de data/hora é o relógio deste computador, não um selo de tempo com autoridade certificadora. Tem valor para mostrar consistência interna do arquivo, não para provar o instante exato de forma inatacável."

O campo `carimboLocal` de cada arquivo é preenchido com `nowIso()` no momento da construção do objeto arquivo (`_construirArquivo`, L2941) — ou seja, também no momento do anexo, mesmo instante do cálculo do hash.

---

## 4. Consulta/edição de prova já cadastrada

Tela: `viewItemDetalhe(itemId)` (L2348-2415).

**Como o usuário chega até ela**: na tabela de itens da tela de Processo (`viewProcesso`, L2063), cada linha `<tr class="vdc-item-row">` tem `onclick="App.abrirItem('<id>')" title="Abrir e editar item"` (L2069), e a última coluna tem um ícone de lápis (`&#9998;`) com o mesmo título. `App.abrirItem` (L2866): `UI.view = "itemDetalhe"; UI.editingField = id; render();`.

**Campos editáveis depois de salvo** (via `campo()` L2420 ou `selectCampoDetalhe()` L2416, ambos chamando `App.salvarCampoItem(field, value)` no `onchange`, que persiste imediatamente — `set(it, field, value); persistir().then(render);`, L2962-2967):
- `Título/descrição` (campo `titulo`) — input texto
- `Categoria` (campo `categoria`) — select, opções = `CATEGORIAS`. Obs.: `salvarCampoItem` tem proteção — `if (field === "categoria" && value === "") return;` — não permite limpar a categoria para vazio.
- `Nº/folha nos autos` (campo `folhaAutos`) — input texto
- `Vinculado à matriz de apuração` (campo `vinculoMatriz`) — input texto
- `Sigilo/classificação` (campo `sigilo`) — select, opções = `SIGILO`
- `Custodiante atual` (campo `custodianteAtual`) — input texto

**Campos travados/read-only depois de criado o item**: todo o bloco de Proveniência (`provenienciaResumoHtml`, L2423-2439) é exibido só como texto (`<div><strong>Label:</strong> valor</div>`), sem inputs — ou seja, tipo de proveniência e todos os subcampos (quem coletou, processo judicial de origem, hash declarado do pacote, sistema de origem etc.) **não podem mais ser editados** depois que o item é salvo. O mesmo vale para o resumo de elemento físico (`elementoFisicoResumoHtml`, L2440-2452) — exceto a condição do lacre, que só pode ser alterada através do fluxo de evento "Conferência do lacre" (modal, `evCondicaoLacre`), não diretamente no formulário.
Também não editável diretamente: `conteudoIntegral`/`justificativaExtrato` (mostrado como badge "Extrato parcial" com o texto da justificativa, sem input), `status` (só via modal "Registrar evento" → "Status alterado"), `fundamentacaoContestacao` (só via evento).

Arquivos podem ser **adicionados** (não removidos/editados) na tela de detalhe pelo mesmo padrão de formulário do wizard (`Descrição do arquivo no pacote`, opcionalmente `Hash declarado pela origem` se aplicável, `Arquivo`), botão `Calcular hash e adicionar` → `App.adicionarArquivoExistente(itemId)`.

Eventos de linha do tempo só podem ser adicionados via modal "Registrar evento" (botão `+ Registrar evento`, `App.abrirModal('evento', {itemId:...})`), nunca editados/removidos.

---

## 5. Exportação isolada (sem contrato com Nexo Coger)

Função: `App.exportarDossie` (L2785-2794):
```js
exportarDossie: function () {
  persistir().then(function () {
    var blob = new Blob([JSON.stringify(DB.dossie, null, 2)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "dossie-" + (DB.dossie.processo.numero || "veritas-digital-coger").replace(/[^\w.-]+/g, "_") + ".json";
    document.body.appendChild(a); a.click(); a.remove();
    toast("Dossiê exportado.", "success");
  });
}
```

- **O que é exportado**: `DB.dossie` inteiro (o objeto completo do dossiê — dados do processo, comissão, todos os itens, arquivos, provemiência, linhas do tempo) serializado como JSON com indentação de 2 espaços. É o dossiê inteiro, não uma seleção de campos.
- **Nome do arquivo gerado**: padrão `"dossie-" + (Nº do processo, ou "veritas-digital-coger" se vazio) + ".json"`, com o número do processo passado por `.replace(/[^\w.-]+/g, "_")` (qualquer caractere que não seja letra/número/underscore/ponto/hífen vira `_`). Exemplo: processo "123.456/2024" → `dossie-123.456_2024.json` (a barra vira `_`, os pontos são preservados pois `.` está na whitelist).
- **Como o usuário aciona**: botão de texto exato `Exportar .json` — aparece em pelo menos dois lugares: (1) na tela de Processo, no cabeçalho "Dados do processo" (L2088); (2) dentro do modal "Reiniciar dossiê", como `Exportar .json antes` (L2538), oferecido como salvaguarda antes da ação destrutiva de reiniciar.

Distinto disso, existe uma exportação separada e específica para integração — `App.exportarProvasParaNexo()` (L2799-2810) — que gera `nexo-coger-provas-<numero>.json` com botão de texto `Exportar provas → Nexo Coger`, contendo **apenas as provas** com `tipo_prova` mapeado para o catálogo canônico (`CATEGORIA_VERITAS_PARA_PROVA_ID`, L1836-1848) — este é o "contrato com Nexo Coger" que a pergunta pede para excluir; não deve ser confundido com `exportarDossie`.

---

## 6. Outras observações úteis para o manual

**Disclaimers** (`CATALOGO`, L1775-1790):
- `disclaimerCurto`: "Ferramenta de apoio à decisão. Não realiza perícia técnica, não valida assinatura digital ICP-Brasil e não substitui laudo pericial formal."
- `disclaimerLongo`: "Veritas Digital - Coger é uma ferramenta de apoio à decisão para as unidades da Corregedoria da RFB — investigação, parecer técnico e comissões de PAD/sindicância. Documenta a consistência interna e a continuidade de elementos de prova digitais e documentais, mas não realiza perícia técnica formal, não valida assinatura digital ICP-Brasil e não substitui laudo pericial quando a autenticidade de um elemento for seriamente contestada. O carimbo de data/hora registrado é o relógio do sistema local do usuário — não é um selo de tempo com autoridade certificadora. A avaliação do caso concreto é sempre da unidade responsável." — exibido na tela inicial (`viewInicio`) e no relatório final.
- `fundamentacao`: "A cadeia de custódia tem disciplina legal expressa apenas no processo penal (art. 158-A a 158-F do CPP, Lei 13.964/2019). No PAD, sua aplicação decorre por analogia e principiologia — verdade real, devido processo, ampla defesa — reforçada pela intercambialidade doutrinária de provas entre PAD e processo penal (compartilhamento de interceptações e dados de operações conjuntas). Esta ferramenta não sugere vinculação normativa direta ao CPP." — exibido em alerta "Fundamentação doutrinária" na tela inicial e no relatório.
- Epígrafe (`CATALOGO.epigrafe`): texto "Toda prova, antes de provar, deve ser provada.", autor "Iacoviello" — aparece no topo da tela inicial e da tela de Processo.

**Dicas contextuais** (`CATALOGO.dicas`, L1780-1789), todas exibidas com ícone 💡 (`&#128161;`) via função `dica(id)`:
- `dica_integralidade`: "Cuidado: decisões não devem se fundamentar em prints de tela, áudios isolados ou trechos sem contexto. Se este é um extrato parcial, registre por que o conteúdo integral não foi anexado e avalie a necessidade de complementação." — aparece na etapa 1 do wizard quando "conteúdo integral" = Não.
- `dica_custodia_externa`: "A partir daqui você documenta a <strong>cadeia externa</strong>: o que aconteceu antes do recebimento pela Coger não está sob seu controle direto. Registre com precisão a origem e o hash declarado — é essa comparação que sustenta a continuidade da prova." — etapa 2, proveniência B.
- `dica_carimbo_local`: ver seção 3. — etapa 3 (Arquivos), sempre que a proveniência já estiver definida.
- `dica_fishing`: "Mantenha o objeto da apuração determinado: fato, pessoa e meios de prova. Evite incorporar elementos coletados sem relação direta com a hipótese investigativa em curso." — topo da etapa 1 do wizard.
- `dica_privacidade_consentimento`: "Ao registrar mensagens ou gravações, observe as normas de privacidade aplicáveis e, quando pertinente, documente se houve consentimento na colaboração de quem forneceu o material." — etapa 1, só quando categoria = "Comunicação (e-mail/mensagem)".
- `dica_prejuizo`: "Uma divergência ou lacuna formal na cadeia de custódia não gera nulidade automática. Registre o ocorrido com precisão e avalie se há prejuízo concreto e demonstrável para a acusação ou para a defesa — esse é o critério que prevalece, não a falha formal isolada em si." (usado em contexto de conferência/relatório — não localizado o ponto exato de exibição neste levantamento, mas presente no catálogo).
- `dica_pericia`: "Se a autenticidade deste elemento for seriamente contestada, esta ferramenta não substitui perícia formal. Ela documenta a cadeia até este ponto; a partir daqui, avalie a necessidade de exame pericial." — exibida na tela de detalhe do item quando `status === "contestado"`.
- `dica_lacre_fisico`: "Documentos físicos e dispositivos (HD, celular, mídia removível) não têm hash — a integridade deles se sustenta pelo lacre. Registre o nº do lacre, sua condição no recebimento/coleta e o local de guarda física; use "Registrar evento → Conferência do lacre" sempre que o objeto for reaberto ou transferido." — etapa 2 do wizard, quando checkbox de elemento físico marcado.

**Mensagens de alerta/erro (toasts) relevantes para o usuário final**, todas em `App._validarStep` e nas ações de formulário:
- "Informe o título/descrição." (etapa 1)
- "Selecione a categoria." (etapa 1)
- "Justificativa obrigatória para extrato parcial." (etapa 1)
- "Selecione o tipo de proveniência." (etapa 2)
- "Adicione ao menos um arquivo (ou marque o elemento físico na Proveniência)." (etapa 3)
- "Selecione um arquivo." (ao tentar adicionar arquivo sem escolher)
- "Selecione um arquivo para conferir." (na Conferência Geral)
- "Informe o novo custodiante." / "Fundamentação da contestação é obrigatória." / "Justificativa é obrigatória para descarte." (modal Registrar evento)

**Reinício do dossiê** (modal `renderModalReiniciar`, L2527-2542): texto de aviso — "Este dossiê (<número>) tem N item(ns) e está salvo neste navegador — reabrir o navegador continuaria carregando-o automaticamente." / "Reiniciar apaga o dossiê deste navegador (localStorage) e volta à tela inicial, para começar um novo ou importar outro. **Exporte o .json antes, se ainda precisar destes dados.**" / alerta: "Esta ação não pode ser desfeita — o dossiê só será recuperável se você tiver exportado o .json antes." Botões: `Cancelar`, `Exportar .json antes`, `Reiniciar mesmo assim` (danger).

**Importação de dossiê**: ao importar um `.json` com dossiê já aberto, modal avisa "Você tem um dossiê aberto com N item(ns). A importação nunca mescla dossiês — o dossiê atual será substituído nesta sessão." Se o `hashDoDossie` do arquivo importado não confere com o conteúdo, alerta adicional: "O hashDoDossie do arquivo importado não confere com o conteúdo — possível indício de alteração externa do arquivo."

**Importação de termo de oitiva (Oitiva 360)** — fluxo de integração à parte (`App.importarTermoOitiva`), com bloqueios via `alert()` nativo do browser (não toast) em três cenários:
1. Formato inválido: "Arquivo inválido: este arquivo não é um termo exportado pelo Oitiva 360 (esperado "origem":"oitiva-360", "termo.conteudo" e "hash_origem")."
2. Hash divergente (bloqueia import): "Importação bloqueada: o hash do termo não confere.\n\nEsperado (hash_origem): <hash>\nCalculado sobre o texto recebido: <hash>\n\nO conteúdo do termo pode ter sido alterado após a exportação do Oitiva 360. Nada foi importado."
3. Duplicado: "Importação recusada: já existe uma prova neste dossiê com o mesmo hash_origem (<hash>). Este termo já foi importado antes — reimportação não cria uma segunda prova."
4. Divergência de versão de catálogo (não bloqueia, pede confirmação via `confirm()`): "Este termo foi exportado com catalogo_schema_version <X>, diferente da versão do catálogo em uso neste Veritas (<Y>). O hash já foi conferido e confere — o aviso é só sobre o vocabulário do catálogo. Deseja continuar?"

Itens importados de termo de oitiva ganham categoria automática `termo_oitiva` e aparecem na tela de detalhe com um card extra "Termo de oitiva (Oitiva 360)" com badge "Revisado"/"Pendente de revisão" e botão `Marcar como revisado`.

**Modal "Registrar evento"** (`renderModalEvento`, L2471): tipos de evento selecionáveis, rótulo exato de cada opção (`EVENTO_TIPO_OPTIONS`, L2464-2470): "Transferência de custódia", "Enviado para perícia formal", "Status alterado", "Item descartado", "Descrição/contexto registrado" — mais "Conferência do lacre" (só se o item tiver elemento físico presente). Cada tipo tem campos extras dinâmicos (ver `buildEventoExtraFieldsHtml`, L2489-2517), com um campo `Responsável` e `Observação` sempre presentes ao final.

**Badge "Pendências de termo"**: ícone `⏳` no topbar (`badgeTermoPendente`) mostra contagem de termos de oitiva importados pendentes de revisão; clicar leva ao primeiro item pendente.

**Contagem aproximada de campos de formulário documentados no wizard (etapas 1-4, todas as variações condicionais incluídas)**: cerca de 40 campos de input/select/radio/checkbox distintos, mais 6 campos editáveis na tela de detalhe (seção 4) e ~10 campos adicionais nos modais de evento.
