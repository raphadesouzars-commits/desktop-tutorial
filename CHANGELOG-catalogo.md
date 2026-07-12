# Changelog — Catálogo Canônico

`catalogo-canonico.json` — `schema_version: 1.2.0` (inalterada; estendida na Rodada PAR-1, era `1.1.0`), `atualizado_em: 2026-07-12`, hash8 (SHA-256, 8 primeiros caracteres): `0955151a` (era `958dfd97`).

### Correção pontual pós-PAR-2 — `origem_permitida` das categorias de prova PAR

A implementação da PAR-2 (2.2, abaixo) expõe `PROVA.PROGRAMA_INTEGRIDADE` e `PROVA.INFORMACOES_COAF` como categorias selecionáveis no Veritas — mas o agente que executou a PAR-2 encontrou e sinalizou (sem corrigir, por estar fora do escopo da sua tarefa) que o `origem_permitida` desses dois itens no catálogo, criado na Rodada PAR-1, listava só `["nexo-coger"]`, sem `"veritas"`. Isso contradizia o comportamento que a própria PAR-2 já implementa. Corrigido para `["nexo-coger","veritas"]` nos dois itens, `CATALOGO_COGER` reembutido nos três HTMLs (hash8 `958dfd97` → `0955151a`) e reconfirmado idêntico nos três arquivos e no JSON fonte. `test-fluxo-integrado.js`: 43/43, sem regressão. `schema_version` não muda (correção de dado, não mudança estrutural).

## Rodada PAR-2 — Ajuste do Veritas (modo dual PAD/PAR) (fechada)

Segunda rodada da trilha PAR, depende da PAR-1 concluída (catálogo com `dominio`, `TIPOS_PROCESSO` com PAR/IPS). Princípio explícito da rodada, respeitado à risca: o Veritas é quase agnóstico de domínio (cadeia de custódia, hash, proveniência, lacre e linha do tempo funcionam identicamente para PAD e PAR) — só vocabulário e propagação de domínio, **nenhuma mudança na lógica de custódia**. Nenhum arquivo além de `ferramentas/veritas.html` foi tocado.

### PAR-2.1 — Campo "Tipo de processo" nos Dados do processo

- `TIPOS_PROCESSO` (mesmo array `[valor, rótulo]`, mesmo agrupamento Investigativos/Acusatórios, com PAR e IPS já incluídos pela PAR-1) foi **copiado** de `nexo-coger.html` para `veritas.html` — não existia lá antes desta rodada. Novo select "Tipo de processo" (com hint "opcional") na seção "Dados do processo" da tela de Processo, ao lado dos campos já existentes (Nº do processo, Portaria, Seção/unidade responsável). Campo opcional: não bloqueia `_validarStep` nem qualquer outro fluxo; dossiês sem esse campo continuam funcionando exatamente como hoje.
- Novo campo `processo.tipoProcesso` (default `""`) em `novoDossie()`, migrado em `migrarDossie()` para dossiês antigos (`if (d.processo.tipoProcesso === undefined) d.processo.tipoProcesso = ""`, mesmo padrão já usado por `secaoResponsavel`).
- Nova função pura `dominioDoProcesso(tipoProcesso)`: `"PAR"` → `"par"`; `TIPOS_QUE_LEVAM_A_PAD` (`PAD`, `investigacao_preliminar`, `sindicancia_investigativa`, `sindicancia_patrimonial`, `sindicancia_acusatoria`) → `"pad"` — mesma lógica implícita de "tipos que levam a PAD" já usada no Nexo Coger (o Nexo trata IP/SINVE/SINPA como investigativos que alimentam a mesma matriz fato-prova-norma do PAD, e SINAC/PAD como os acusatórios correspondentes); qualquer outro valor (incluindo tipo não informado) devolve `undefined`.
- **Decisão sobre IPS (Investigação Preliminar Sumária):** deliberadamente **fora** de `TIPOS_QUE_LEVAM_A_PAD`, então `dominioDoProcesso('investigacao_preliminar_sumaria')` devolve `undefined` — o campo `dominio` fica **ausente**, não `"pad"`. A spec desta rodada só lista IP/SINVE/SINPA/SINAC (não IPS) como "tipos investigativos correlatos" ao PAD, e o texto da spec já reconhece que IPS é ambíguo. Presumir `"pad"` para IPS esconderia as categorias de prova PAR (2.2) e o campo `dominio` na exportação (2.3) exatamente do processo que mais precisa ficar neutro até a comissão decidir o rito — na prática, um processo de IPS que vier a virar PAR perderia sem necessidade a sinalização de domínio se o padrão fosse "pad por omissão". A alternativa descartada (`dominio: "pad"` fixo para IPS) foi considerada e rejeitada por esse motivo; a ausência do campo é o comportamento mais conservador e reversível (a comissão pode reclassificar o tipo de processo a qualquer momento, sem precisar desfazer nenhuma marcação anterior).
- Retrocompatibilidade testada explicitamente (Playwright): dossiê `.json` construído manualmente sem `tipoProcesso`/`dominio` (simulando exportação pré-PAR-2) importa sem erro, mostra o item já existente normalmente e o select "Tipo de processo" aparece vazio.

### PAR-2.2 — Categorias de prova sensíveis a domínio

- Nova função pura `categoriasDisponiveis(dominio)`: `dominio !== "par"` (ausente, `"pad"`, ou qualquer outro) → devolve o objeto `CATEGORIAS` estático, sem cópia nem alteração — comportamento de hoje, byte a byte; `dominio === "par"` → devolve `Object.assign({}, CATEGORIAS, CATEGORIAS_ADICIONAIS_PAR)`, uma cópia nova a cada chamada (o array/objeto `CATEGORIAS` original nunca é mutado). Usada nos dois selects de categoria que existiam (Etapa 1 do wizard de criação e o campo "Categoria" editável na tela de detalhe do item) — as duas passaram a montar as opções dinamicamente a partir do `dominio` do processo atual (`dominioDoProcesso(DB.dossie.processo.tipoProcesso)`), em vez de `Object.keys(CATEGORIAS)` fixo.
- `CATEGORIAS_ADICIONAIS_PAR = { programa_integridade: "Programa de integridade", informacoes_coaf: "Informações do COAF" }` — rótulos reproduzidos literalmente do `catalogo-canonico.json` (`PROVA.PROGRAMA_INTEGRIDADE`, `PROVA.INFORMACOES_COAF`). `PROVA.EMPRESTADA` **não foi adicionada**: confirmado por leitura de `CATEGORIAS` que ela não existe como categoria própria selecionável no Veritas hoje (o Veritas não tem um conceito de "prova emprestada" na Etapa 1 — isso é vocabulário do Nexo Coger), então não havia o que estender, exatamente como a spec previa ("se implementada").
- **Discrepância encontrada e não corrigida nesta rodada** (fora de escopo, documentada para rodada futura de consistência do catálogo): `catalogo-canonico.json` define `origem_permitida: ["nexo-coger"]` para os dois tipos de prova PAR (`PROVA.PROGRAMA_INTEGRIDADE`, `PROVA.INFORMACOES_COAF"`), sem incluir `"veritas"` — mas a spec desta rodada instrui explicitamente expor essas duas categorias no Veritas quando `dominio: "par"`. Segui a instrução explícita da spec (aprovada) em vez do campo `origem_permitida` do catálogo (que não previu esse uso quando foi escrito na PAR-1) — nenhuma validação automática lê `origem_permitida` hoje em nenhuma das três ferramentas, então não há quebra de comportamento, só uma inconsistência de metadado a ser resolvida quando o catálogo for revisado.
- `CATEGORIAS_TODAS = Object.assign({}, CATEGORIAS, CATEGORIAS_ADICIONAIS_PAR)`: lookup de rótulo (não de opções selecionáveis) usado na listagem de itens e no relatório, para que um item já salvo com categoria PAR continue exibindo o rótulo certo mesmo que o processo seja reaberto sem `tipoProcesso` definido.
- "Termo de oitiva" mantém seu comportamento especial (atribuída só via `App.importarTermoOitiva`, não oferecida como opção de criação manual no fluxo normal) nos dois domínios — nenhuma mudança nesse ponto; ela continua presente como `<option>` no HTML do select em ambos os casos (comportamento herdado, não alterado por esta rodada).
- Testado via Playwright: sem tipo de processo definido e com tipo `PAD`, as duas categorias PAR não aparecem no select da Etapa 1; com tipo `PAR`, ambas aparecem, junto com todas as categorias originais (incluindo "Termo de oitiva", inalterada).

### PAR-2.3 — Propagação do domínio na exportação

- `persistir()` (chamada antes de toda exportação e a cada alteração salva) agora sincroniza `DB.dossie.processo.dominio` com `dominioDoProcesso(DB.dossie.processo.tipoProcesso)` a cada chamada — `dominio` recebe `"pad"`/`"par"` quando derivável, ou é **removido do objeto** (`delete`, não `= null`) quando não derivável. Decisão de arquitetura: em vez de deixar `dominio` como um valor puramente computado só em memória (o que exigiria `exportarDossie` reconstruir o objeto exportado campo a campo, arriscando divergir do `hashDoDossie`, calculado sobre o mesmo `DB.dossie` que é serializado), o campo é escrito no próprio objeto que `persistir()` já hasheia e serializa — assim o hash cobre exatamente o que sai no arquivo, e o campo nunca fica dessincronizado do `tipoProcesso` (recalculado a cada persistência, nunca editado à mão), no mesmo espírito de "computado, não digitado" já usado pelos badges de status da Rodada 8.
- `App.exportarDossie()` não precisou de nenhuma mudança de código — como já serializa `DB.dossie` inteiro após `persistir()`, o campo `processo.dominio` passa a vir de graça quando presente, e simplesmente não existe no objeto quando ausente (confirmado inspecionando o JSON bruto exportado — a string `"dominio"` não aparece no arquivo quando o tipo de processo não foi informado).
- `construirContratoProvasNexo()` (núcleo puro do contrato Veritas → Nexo Coger, `App.exportarProvasParaNexo`) ganhou `var dominio = dossie.processo.dominio || dominioDoProcesso(dossie.processo.tipoProcesso);` e só atribui `contrato.dominio = dominio` quando o valor existe — mesma regra "ausente, não `null` inventado" do dossiê completo. Testado nos dois sentidos: `dominio: "par"` presente no envelope quando o processo é PAR; chave `dominio` completamente ausente (`Object.prototype.hasOwnProperty` retorna `false`, string `"dominio"` ausente do JSON bruto) quando o tipo de processo não foi definido.
- **Nenhuma validação de importação por domínio foi implementada** — nem no Veritas (que não faz nenhuma checagem de `dominio` ao importar dossiê ou termo de oitiva), nem em nenhum outro arquivo (`nexo-coger.html`, `oitiva-360.html` não foram tocados nesta rodada). Só a emissão do campo, exatamente como a spec pediu, reservando a validação cruzada para a Rodada PAR-5.
- `dominioDoProcesso`, `categoriasDisponiveis`, `TIPOS_PROCESSO`, `CATEGORIAS`, `CATEGORIAS_ADICIONAIS_PAR` e `migrarDossie` foram adicionados a `window.VeritasPuro` (mesmo padrão de núcleos puros estabelecido na Rodada 7), para serem exercitados diretamente via Node em testes automatizados, sem depender de browser.

### PAR-2.4 — Ajustes de texto neutro

Busca case-insensitive por "servidor" no arquivo inteiro encontrou só **3 ocorrências**, todas dentro do `CATALOGO_COGER` embutido (dados do catálogo canônico, não texto de interface do Veritas em si):
- `PAPEL.ACUSADO.descricao` ("Servidor submetido a apuração disciplinar...") — descreve literalmente o papel de acusado num PAD, `dominio: "pad"` desde a PAR-1; o PAR já tem seu próprio papel equivalente (`PAPEL.ENTE_PRIVADO`, com descrição própria, não tocado). **Mantido como está** — reescrever a descrição de um papel `dominio: "pad"` para linguagem neutra apagaria a distinção que a própria PAR-1 criou entre os dois domínios.
- Duas normas da Lei nº 8.112/1990 (`NORMA.L8112.ART117_XVII` — "Cometer a outro servidor atribuições estranhas ao cargo..." — e `NORMA.L8112.ART322` — "Ofensa física, em serviço, a servidor ou particular...") — texto legal reproduzido literalmente do dispositivo, `dominio: "pad"`. **Mantidas como estão** — são o texto de um artigo de lei que só se aplica a servidor por natureza jurídica do próprio dispositivo; "neutralizar" a redação seria parafrasear a lei incorretamente, o que a PAR-1 já havia decidido não fazer para nenhuma norma do catálogo.

Fora do catálogo embutido, duas ocorrências de texto de interface presumiam escopo só-PAD e foram ajustadas para incluir PAR:
- `CATALOGO.disclaimerLongo` (exibido na tela inicial e no rodapé do relatório impresso): "...investigação, parecer técnico e comissões de **PAD/sindicância**." → "...investigação, parecer técnico e comissões de **PAD/sindicância/PAR**."
- Parágrafo descritivo fixo da tela de Processo (`viewProcesso`, logo abaixo do cabeçalho "Dados do processo"): mesmo trecho "comissões de PAD/sindicância." → "comissões de PAD/sindicância/PAR.", mesma razão.

**Explicitamente NÃO tocado, por instrução direta da spec:** `CATALOGO.fundamentacao` (a fundamentação doutrinária da cadeia de custódia por analogia ao CPP) — vale para os dois domínios tal como já estava escrita e permanece byte a byte idêntica. Também não tocados: qualquer rótulo de campo do wizard (Título/descrição, Proveniência, Sigilo etc. já eram neutros), os textos dos 6 tipos de evento e das dicas contextuais (`CATALOGO.dicas`) — nenhuma delas menciona "servidor" nem qualquer termo PAD-específico, revisão confirmou que já eram neutras.

### Teste de regressão

`node test-fluxo-integrado.js` — **43/43 verificações passaram, exit code 0**, mesmo placar de antes da mudança (conferido antes de editar). Nenhum teste do domínio PAD foi afetado.

### Teste manual (Playwright, `ferramentas/veritas.html` real, Chromium)

20 verificações, todas ok, cobrindo os 3 critérios de aceite da spec:
1. **Retrocompatibilidade:** dossiê `.json` construído manualmente sem `tipoProcesso`/`dominio` (simulando um dossiê exportado antes desta rodada) importado sem erro — tela de Processo carrega, o único item pré-existente aparece normalmente, e o select "Tipo de processo" aparece vazio (não quebra, não força um valor).
2. **Categorias por domínio:** sem tipo de processo e com tipo `PAD`, "Programa de integridade" e "Informações do COAF" não aparecem no select "Categoria" da Etapa 1; com tipo `PAR`, ambas aparecem, junto com todas as categorias originais (incluindo "Termo de oitiva", intacta).
3. **Exportação:** com tipo `PAR`, `Exportar .json` gera `processo.dominio === "par"` e `Exportar provas → Nexo Coger` gera `dominio === "par"` no envelope (inspecionado no JSON bruto salvo em disco, não só na tela); com tipo de processo revertido para vazio na mesma sessão, os dois exports não têm a chave `dominio` (confirmado por `hasOwnProperty` e por ausência da string `"dominio"` no arquivo bruto — não veio como `null`).

## Rodada PAR-1 — Extensão do catálogo para o domínio PAR (fechada)

Primeira rodada da trilha PAR (responsabilização de entes privados, Lei nº 12.846/2013 — LAC), bloqueando as Rodadas PAR-2 a PAR-6. Escopo estritamente de dados: só o catálogo cresce; nenhuma interface das três ferramentas passou a expor os itens novos nesta rodada (exceção única e explícita: PAR/IPS em `TIPOS_PROCESSO`, ver PAR-1.3).

### PAR-1.1 — Campo `dominio` em todos os itens existentes

Todo item de `papeis_pessoa[]`, `tipos_prova[]` e `normas[]` ganhou o campo `dominio` (`"pad"` | `"par"` | `"comum"`). Nenhum item existente mudou de `id` ou de qualquer outro campo — validado programaticamente (script Python comparando, item a item por `id`, todos os campos exceto `dominio` entre o JSON original salvo antes da edição e o JSON final; zero divergências).

- **Normas:** as 45 da Lei nº 8.112/1990 e as 7 do art. 32 da LAI (Lei nº 12.527/2011) → `"pad"`. A spec já indicava explicitamente a LAI como `"pad"` (é usada apenas no contexto de apuração PAD, conforme a auditoria original da Rodada 1 — o Veritas nem chega a referenciá-la); confirmado por leitura de cada item `NORMA.LAI.*` antes da migração, nenhum sinal de uso fora do contexto disciplinar.
- **Papéis de pessoa:** `PAPEL.ACUSADO` → `"pad"` (é o servidor investigado; no PAR o polo passivo é o ente privado, um conceito à parte — `PAPEL.ENTE_PRIVADO`, novo). `PAPEL.VITIMA`, `PAPEL.TESTEMUNHA`, `PAPEL.DECLARANTE_INFORMANTE`, `PAPEL.PESSOA_SITUACAO_INDEFINIDA` → `"comum"`, exatamente como a spec instruiu.
- **Tipos de prova (decisão de bom senso — não estavam listados item a item na spec):** os 8 tipos nativos do Nexo Coger (`PROVA.DOCUMENTAL`, `PROVA.PERICIAL`, `PROVA.TESTEMUNHAL`, `PROVA.DECLARACAO_INFORMANTE`, `PROVA.INTERROGATORIO`, `PROVA.DILIGENCIA`, `PROVA.EMPRESTADA`, `PROVA.INDICIARIA`) e as 9 subcategorias de evidência do Veritas (`PROVA.PRINT_SISTEMA`, `PROVA.DOCUMENTO_FINANCEIRO`, `PROVA.COMUNICACAO`, `PROVA.FOTO_VIDEO`, `PROVA.OFICIO`, `PROVA.DECISAO_JUDICIAL`, `PROVA.DOCUMENTO_FISICO`, `PROVA.DISPOSITIVO_FISICO`, `PROVA.OUTRO`) foram classificados `"comum"`: são vocabulário de tipo de mídia/meio de prova (um documento, uma perícia, uma comunicação eletrônica, um depoimento) e nada neles é exclusivo de um rito — tanto um PAD quanto um PAR podem ter prova documental, pericial, testemunhal ou uma comunicação eletrônica como evidência. `PROVA.TERMO_OITIVA` (Rodada 5) também foi classificada `"comum"` pelo mesmo raciocínio: é o veículo estruturado de pergunta-resposta de uma oitiva, e nada na Lei nº 12.846/2013 restringe a oitiva de preposto ou sócio-administrador a um formato diferente do já usado para testemunha/acusado no PAD.

### PAR-1.2 — Itens novos

- **11 normas `NORMA.LAC.*`** (art. 5º da Lei nº 12.846/2013), com `descricao` reproduzindo o texto legal do inciso tal como fornecido pela spec (sem paráfrase) e `nota_aplicacao` com o entendimento da CGU — grupo `"Atos de corrupção em geral"` (incisos I, II, III, V) e `"Licitações e contratos"` (inciso IV, alíneas a–g), exatamente a divisão doutrinária do manual CGU indicada na spec.
- **4 papéis PAR:** `PAPEL.ENTE_PRIVADO`, `PAPEL.REPRESENTANTE_LEGAL`, `PAPEL.PREPOSTO`, `PAPEL.SOCIO_ADMINISTRADOR`, todos `dominio:"par"`.
- **2 tipos de prova PAR novos:** `PROVA.PROGRAMA_INTEGRIDADE`, `PROVA.INFORMACOES_COAF`. `PROVA.EMPRESTADA` **não foi duplicada** — já existia desde a Rodada 1 (migrada do Nexo Coger); só recebeu `dominio:"comum"`, conforme a spec ("prova produzida em outro processo, transportada com contraditório" já era exatamente a definição existente).
- **Contagem final:** 92 itens no catálogo (eram 74 na Rodada 1), 53 `"pad"`, 22 `"comum"`, 17 `"par"`.

### PAR-1.3 — `TIPOS_PROCESSO` do `nexo-coger.html`

Único ponto de UI tocado nesta rodada, por instrução explícita da spec (correção de lacuna preexistente, não feature nova do domínio PAR): adicionado `investigacao_preliminar_sumaria` ("Investigação Preliminar Sumária (IPS)") ao grupo Investigativos e `PAR` ("Processo Administrativo de Responsabilização (PAR)") ao grupo Acusatórios, em `TIPOS_PROCESSO`, `TIPO_SIGLA` e `TIPOS_INVESTIGATIVOS` (IPS somado ao `Set` de tipos investigativos, junto de IP/SINVE/SINPA, para preservar a lógica existente de `mostraRito` que já depende desse `Set`).

### PAR-1.4 — Re-sincronização de `CATALOGO_COGER`

Reembutido nos três `ferramentas/*.html` a partir do `catalogo-canonico.json` atualizado, comentário de cabeçalho atualizado (`schema_version: 1.2.0`, hash8 `958dfd97`). Script Python extraiu `CATALOGO_COGER` de cada um dos três arquivos via regex e comparou (`==` estrutural, via `json.loads`) contra o JSON fonte e entre si: **os quatro batem exatamente**. Verificação adicional: `node -c` (via `new Function()`) em cada `<script>` embutido dos três HTMLs, sem erro de sintaxe após a substituição.

### Teste de regressão

`node test-fluxo-integrado.js` — **43/43 verificações passaram, exit code 0** (mesmo placar de antes da mudança; conferido a contagem antes de editar, já era 43/43 desde a Rodada 7/8). Nenhum teste do domínio PAD foi afetado pela extensão. Teste adicional descartável (script Python, não versionado) confirmou: todo item tem `dominio` válido (`pad`/`par`/`comum`); as 11 normas LAC presentes com os IDs exatos da spec; os 4 papéis PAR e os 2 tipos de prova PAR presentes; `PROVA.EMPRESTADA` existe uma única vez com `dominio:"comum"`; os três HTMLs e o JSON fonte são estruturalmente idênticos.

## Rodada 8 — Sinalização visual de pendências (fechada)

### 8.1 — Diagnóstico

Confirmado: as três ferramentas já usam exclusivamente exportação/importação de JSON local (`exportJson`/`importJson` no Nexo, `App.exportarDossie`/`App.importarArquivo` no Veritas, botões de exportar/importar processo no Oitiva) — nenhuma usa `localStorage` como fonte de verdade entre sessões de trabalho compartilhadas (`localStorage` só existe como rascunho automático dentro do mesmo navegador). A Rodada 8 não introduziu nenhum mecanismo novo — os campos de status desta rodada viajam dentro do mesmo JSON já exportado/importado.

### Decisão de arquitetura: status computado vs. persistido

A introdução do escopo já avisa: "a detecção é sempre local, e recalculada a partir do estado atualmente carregado". Segui isso à risca — só usei um campo `status` **persistido e mutável** onde o estado realmente não é derivável de outro dado (é uma decisão humana, tipo "eu já li isso"). Onde o status já podia ser deduzido de uma relação que já existe no JSON, optei por **computar ao vivo a cada render**, para eliminar qualquer risco de desincronização entre o campo e a relação real:

| Ferramenta | Entidade | Mecanismo |
|---|---|---|
| Nexo Coger | Prova importada do Veritas (`pendente`/`vinculada`) | **Computado**: pendente se `p.origemVeritas` existe e nenhum `f.provaIds` contém `p.id`; vinculada caso contrário. Mesma lógica já usada pela pendência P3 ("prova órfã"), sem campo novo — a vinculação em si já é a ação natural (checkbox no formulário do fato, Rodada existente). |
| Oitiva 360 | Pauta importada do Nexo Coger (`pendente`/`em_andamento`/`concluida`) | **Computado**: concluída se `statusChecklist` é `abordado`/`sem_resposta`; em_andamento se algum depoente tem o `fatoId` em `pautaSelecionada`; pendente caso contrário. |
| Nexo Coger | Retorno de prova de oitiva (`pendente_revisao`/`revisado`) | **Persistido**: `provasContexto[].status`, porque "revisado" é puramente uma confirmação humana — nenhum outro dado do JSON indica isso. Transição pela ação natural de abrir o cadastro do acusado, conferir o item e salvar (não é um botão isolado). |
| Veritas (extensão além da tabela da spec) | Termo de oitiva importado (`pendente_revisao`/`revisado`) | **Persistido**: `item.termoOitiva.status`, mesmo raciocínio do retorno de oitiva. A tabela do escopo (8.2) lista só 3 entidades, mas o texto geral diz "cada entidade que chega por importação (Rodadas 3-6) ganha um campo de status" — e o Veritas recebe o termo (Rodada 5), então essa 4ª entidade foi coberta para os três badges baterem com o entregável 3 ("badge... nas três ferramentas"). Transição pela ação natural de abrir o item e clicar "Marcar como revisado" (mostrado só quando o item tem `termoOitiva`, junto com o próprio texto do termo — antes desta rodada não havia nenhuma tela mostrando esse conteúdo).

### Badges

Os três seguem a paleta navy/gold já usada pelo design system COGER: fundo navy do próprio cabeçalho de cada ferramenta (hero do Nexo/Oitiva, topbar do Veritas) com o badge em dourado sólido (`--rfb-gold-500`), texto navy escuro para contraste — nenhuma cor nova introduzida. Cada um só aparece quando a contagem é maior que zero (`display:none` em zero, evita ruído visual permanente). Clicar no badge do Nexo abre um modal listando os itens pendentes com atalho para abrir cada um; no Oitiva rola até o resumo da pauta; no Veritas abre diretamente o primeiro termo pendente.

### Teste (Playwright, os três HTMLs reais)

- Nexo: importar uma prova do Veritas sem vincular mantém o badge em 1; vincular a um fato reduz para 0 **sem recarregar a página**; simular salvar+recarregar o JSON com uma prova ainda pendente preserva o status (não some, não vira "vinculada" sozinho).
- Nexo: um retorno de oitiva pendente conta no badge; abrir o formulário do acusado, marcar "Revisado" e salvar zera o badge e persiste `status:"revisado"` no objeto.
- Confirmado que os elementos `#badgePautaPendente` (Oitiva) e `#badgeTermoPendente` (Veritas) existem no cabeçalho de cada ferramenta.
- Reexecutado o teste de ponta a ponta da Rodada 6 (Playwright) e o `test-fluxo-integrado.js` da Rodada 7 (43/43) depois de todas as mudanças — nenhuma regressão.
- Nenhuma das três ferramentas ganhou código de rede/`fetch`/leitura de arquivo de outra ferramenta — os badges só reagem a mudanças no próprio estado já carregado, conforme 8.4.

## Rodada 7 — Teste de fluxo integrado ponta a ponta (fechada)

### 7.1 — Diagnóstico de separabilidade

- **`nexo-coger.html`** não tem IIFE — tudo (funções e variáveis de topo) já é escopo de script. A maior parte da lógica de contrato já era pura (`analisarLacunasPauta`, `normaInternaParaCanonica`, `retornoJaExiste`); o que faltava era **extrair** a construção de envelopes/objetos de dentro de funções que também baixavam arquivo/re-renderizavam (`gerarPautaPorDepoente`, `aplicarImportacaoVeritas`, `aplicarImportacaoRetornoOitiva`). Como `doc`/`CATALOGO_COGER`/`PROVA_ID_PARA_TIPO_NEXO` são `let`/`const` de topo de script, não viram propriedades do objeto global mesmo fora de IIFE (só `function` declarada vira) — foram criados accessors mínimos (`getDoc`/`setDoc`/`getCatalogoCoger`/`tipoNexoParaProvaId`) só para isso.
- **`veritas.html`** e **`oitiva-360.html`** são IIFEs — só o que é explicitamente atribuído a `window` é visível de fora. Cada um ganhou um namespace novo (`window.VeritasPuro`, `window.OitivaPuro`) reunindo as funções centrais de cada contrato, todas reescritas/extraídas para receber dados e devolver dados (inclusive as assíncronas de hash), sem tocar `document`/`localStorage`. As funções de UI (`App.exportarProvasParaNexo`, `App.importarTermoOitiva`, `exportarTermoParaVeritas`, `exportarRetornoContextoAcusado`, `aplicarImportacaoPauta`) viraram wrappers finos em torno dessas — **mesmo comportamento de interface, lógica testável isolada**. Confirmado sem regressão reexecutando o teste Playwright da Rodada 6 (browser real) depois do refactor: passou integralmente.
- Duas lacunas de idempotência foram descobertas só ao planejar os testes de 7.4 e corrigidas nesta rodada (iam além do que as Rodadas 3 e 5 tinham exigido originalmente): a importação de prova do Veritas no Nexo (Rodada 3) não tinha nenhum dedup — reimportar o mesmo `id_prova` criava uma segunda prova; e a importação de termo no Veritas (Rodada 5) também não tinha dedup — reimportar o mesmo `hash_origem` gerava um novo `id_prova` a cada vez. Ambas ganharam checagem de duplicidade com mensagem clara (`provaVeritasJaImportada`/`avaliarImportacaoTermo` com `motivo:"duplicado"`), no mesmo padrão já usado pela Rodada 6 para o retorno de contexto.

### 7.2/7.3 — Fixture e script de teste

- `fixtures/pad-ficticio-001.json`: 1 acusado, 3 fatos (1 com prova inicial do Veritas, 2 gerando lacuna — o teste usa a lacuna de `F2`, tipo `sem_prova`), depoente testemunha com uma `respostaPadrao` fictícia aplicada a todo o roteiro gerado, sem acusado alternativo (exercita o vínculo automático da Rodada 6).
- `test-fluxo-integrado.js`: carrega os três `ferramentas/*.html` **reais** via `vm.createContext`/`vm.runInContext` do Node, com um stub mínimo de `document`/`localStorage`/`URL`/`Blob`/`crypto` só para os scripts terminarem de carregar sem lançar (nenhuma asserção depende do stub — toda a lógica exercitada é pura). Roda as 7 etapas do fluxo (Veritas exporta prova → Nexo importa → Nexo gera pauta → Oitiva importa pauta e monta roteiro → Oitiva responde e gera termo com hash → Veritas importa termo e gera `id_prova` → Oitiva exporta retorno e Nexo importa vinculando ao acusado padrão), depois repete os passos 2, 4, 6 e 7 com o mesmo payload (7.4) e testa hash adulterado + `catalogo_schema_version` divergente (7.5). Relatório por grupo no console, `console.assert`-style, sem framework.

### Resultado

`node test-fluxo-integrado.js` — **43/43 verificações passaram**, exit code 0: as 7 etapas, as 4 reimportações (nenhuma duplicidade, todas sinalizadas explicitamente — reimportar pauta agora dispara um aviso, reimportar prova/termo/retorno são recusados com motivo claro) e os 2 testes de falha controlada (hash divergente rejeitado; `catalogo_schema_version` divergente sinalizada sem bloquear quando o hash confere).

## Rodada 6 — Contrato Oitiva 360 → Nexo Coger: retorno da prova / contexto do acusado (fechada)

### 6.2 — Diagnóstico

Confirmado por busca: **nenhuma estrutura de "contexto do acusado" existia** no `nexo-coger.html` — criada do zero (`acusado.provasContexto[]`).

Achado mais importante da rodada: o Oitiva 360 **já tinha** um mecanismo de "prova de retorno" para o Nexo (botão "Exportar prova(s) para o Nexo" / `abrirDialogoExportarProva`, consumido por `aplicarImportacaoProva` no Nexo) — mas esse mecanismo empurra a prova para `doc.provas[]` e `f.provaIds`, que **alimentam diretamente** `computePendencias()` (P1 "sem prova", P7 "sustentação frágil") e, por consequência, a força probatória e o caminho até a indiciação. Isso conflita frontalmente com o critério 6.4 desta rodada ("nenhum caminho de código que dispare indiciação automaticamente" / "sem qualquer campo que participe do cálculo/fluxo de indiciação"). Conclusão: o mecanismo existente serve a um propósito legítimo diferente (prova evidenciária formal) e **não foi reaproveitado nem alterado** — o contrato desta rodada é novo, paralelo, e deliberadamente isolado de `doc.provas`/`doc.fatos`, para que nenhuma função de pendência ou indiciação possa lê-lo, nem por acidente.

### Contrato implementado

`oitiva-360.html`:
- O bloco já existente "Pauta do Nexo — itens abordados nesta sessão" (Etapa 4) ganhou, por item abordado, um campo "Resumo da resposta" e um campo opcional "Acusado alternativo" — vazio (o caso comum) implica `acusado_vinculo: "padrao"`, preenchido implica `"manual"` com `acusado_alternativo` no envelope. Nenhuma ação extra é exigida do usuário no caso comum (critério 6.1).
- Nova `exportarRetornoContextoAcusado()`: para cada item de pauta abordado nesta sessão (já carrega `pautaIdOrigem`/`idPontoOrigem`/`fatoId` desde a Rodada 4), monta um envelope com `id_prova` (pedido ao usuário via `prompt()` — é o identificador gerado pelo Veritas na Rodada 5 ao importar o termo; não há como o Oitiva conhecê-lo automaticamente, já que são três ferramentas offline sem integração ao vivo), `pauta_id`, `rodada_id` (reaproveita `d.rodadaId` da Rodada 5), `id_ponto`, `acusado_vinculo`/`acusado_alternativo`, `fato_referencia`, `resumo_resposta`.
- Botão novo "Exportar retorno (contexto do acusado)", ao lado do já existente "Exportar prova(s) para o Nexo" — visualmente próximos, mas contratos diferentes (comentado explicitamente no código para não confundir as duas "Rodada 6": a numeração interna do próprio Oitiva, anterior a este projeto, e a Rodada 6 deste projeto).

`nexo-coger.html`:
- `acusado.provasContexto[]` — lista nova, default `[]` em acusados novos e migrada em acusados existentes. Nenhuma função de `computePendencias()`, força probatória ou geração de minuta/indiciação lê este campo — isolamento estrutural, não apenas por convenção.
- Nova importação (`importarRetornoOitiva()`, menu "📥 Importar retorno do Oitiva (contexto do acusado)"): tela de revisão mostra, por retorno, um `<select>` do acusado-alvo — pré-selecionado automaticamente para o único acusado do processo quando há só um (regra geral, critério 6.1); quando o `acusado_alternativo` bate por nome com outro acusado cadastrado, esse é o pré-selecionado; sem correspondência, o primeiro acusado fica pré-selecionado mas o campo continua editável antes de confirmar.
- **Deduplicação:** a nota da spec fala em "recusar reimportar um `id_prova` já presente", mas um único `id_prova` pode legitimamente responder a vários pontos de pauta diferentes (um termo cobre várias lacunas). Interpretação adotada: duplicidade = **mesmo par `id_prova` + `id_ponto`** já presente no `provasContexto` daquele acusado — cobre exatamente o caso descrito ("reimportação acidental do mesmo arquivo") sem impedir o caso legítimo de um termo responder a múltiplas lacunas. Itens duplicados aparecem na tela de revisão com mensagem clara e são automaticamente excluídos do lote a importar (recomputado ao vivo se o usuário trocar o acusado selecionado).
- Selo visual: `drawFatoCard()` (mapa fato-prova-norma) ganhou um badge 🎙 (cor `--rfb-gold-600`, design system COGER) quando qualquer acusado tem `provasContexto` referenciando aquele fato — tooltip deixa explícito que não é prova evidenciária formal e não conta para a força probatória.

### Teste de ponta a ponta (Playwright, os três HTMLs reais, fluxo completo Nexo → Oitiva → Veritas → Nexo)

1. Nexo (exemplo reduzido a 1 acusado, caso comum) gera pauta para um depoente → Oitiva importa a pauta, marca o item para abordar, responde o roteiro, marca oitiva como realizada, exporta termo (Rodada 5) e, na sequência, exporta retorno de contexto (`id_prova` informado manualmente, simulando o dado vindo do Veritas) — envelope confirma `acusado_vinculo: "padrao"`, `pauta_id`/`id_ponto`/`rodada_id` presentes.
2. Nexo importa o retorno: **pendências (7) e `doc.provas` (3) permanecem idênticos antes/depois** — confirmação direta do critério 6.4. `provasContexto` do único acusado cresce exatamente pelo número de retornos, vinculado automaticamente, sem nenhuma seleção manual (critério de aceite 1).
3. Selo "Contexto de oitiva vinculado" confirmado presente no mapa via inspeção dos `<title>` dos badges SVG (critério de aceite 5).
4. Reimportar o mesmo arquivo: tela de revisão mostra "reimportação recusada" e o total de `provasContexto` não muda mesmo clicando "Importar" (critério de aceite 4).
5. Importação do termo no Veritas (Rodada 5) confirmada intacta, sem regressão.

Os critérios de aceite 2 (vínculo manual com acusado alternativo) e 3 (nenhuma indiciação alterada) foram cobertos por revisão de código e pela ausência de qualquer leitura de `provasContexto` nas funções de pendência/indiciação — o vínculo manual segue exatamente o mesmo caminho de código do padrão automático, só troca qual acusado é pré-selecionado.

## Rodada 5 — Contrato Oitiva 360 → Veritas: termo de oitiva (fechada)

### 5.1 — Diagnóstico

`gerarTermoTexto()` já existia no `oitiva-360.html` e já montava cabeçalho, qualificação civil/funcional e o parágrafo de compromisso/silêncio/colaboração por papel — mas a seção de inquirição era o texto fixo literal `"[transcrição das perguntas e respostas]"`. `d.roteiro` (o banco de perguntas selecionadas para a sessão) nunca teve campo de resposta: é um roteiro do que perguntar, não um transcript do que foi respondido. Não existiam também "responsável pela condução" nem "observações gerais" como campos do depoente — por isso, seguindo a spec, ficaram de fora desta rodada (campo `termo.responsavel` exportado vazio).

### Extensão do catálogo

`PROVA.TERMO_OITIVA` adicionada a `tipos_prova` no `catalogo-canonico.json` (`origem_permitida: ["oitiva-360", "veritas"]`), com bump de `schema_version` para `1.1.0` (adição não-quebra de vocabulário) e reembutida (mesmo hash `744bb790`) nos três HTMLs.

### Contrato implementado

`oitiva-360.html`:
- `d.respostasRoteiro` (chave estável `blocoId::refId::ordem`) guarda a resposta de cada pergunta do roteiro, editável na nova seção "Respostas registradas" da Etapa 4.
- `gerarTermoTexto()` agora monta a transcrição real, numerada, na ordem do roteiro (`perguntasRespostasOrdenadas()`), ou uma nota de "direito ao silêncio exercido" quando aplicável — nunca mais o placeholder fixo.
- `exportarTermoParaVeritas()`: regenera o termo a partir do estado corrente (garante que o texto exportado sempre reflete as respostas mais recentes), calcula SHA-256 sobre esse texto exato via Web Crypto (`sha256HexOitiva`, mesmo algoritmo do Veritas), e monta o envelope (`schema_version`, `catalogo_schema_version`, `pauta_id` — deduzido dos `pautaIdOrigem` dos itens de pauta selecionados pelo depoente, Rodada 4 —, `rodada_id` gerado e persistido em `d.rodadaId`, `deponente.papel` por ID via `PAPEL_SLUG_PARA_ID_CATALOGO`, Rodada 2 —, `termo`, `hash_origem`).

`veritas.html`:
- `App.importarTermoOitiva()`: valida `origem`/`termo.conteudo`/`hash_origem`, recalcula o hash sobre o texto recebido e **bloqueia a importação com `alert()` claro (mostrando hash esperado vs. calculado) se divergir** — nenhum item é criado nesse caso. Se o hash confere, cria um novo item com `categoria: "termo_oitiva"` (rótulo "Termo de oitiva", nova entrada em `CATEGORIAS`), `proveniencia.tipo: "gerado_internamente"` (mesma lógica de proveniência interna já usada para itens gerados dentro da suíte), `id` novo gerado por `uid()` no momento da importação, e guarda o envelope completo em `item.termoOitiva` (conteúdo, `pautaId`, `rodadaId`, `deponente`, `hashOrigem`) para rastreabilidade da Rodada 6. Aviso não bloqueante (mesmo padrão das Rodadas 3/4) se `catalogo_schema_version` divergir mas o hash conferir.
- `CATEGORIA_VERITAS_PARA_PROVA_ID.termo_oitiva = "PROVA.TERMO_OITIVA"` também adicionado, para que um termo já importado seja corretamente re-rotulado se algum dia reexportado ao Nexo (`exportarProvasParaNexo()`, Rodada 3).

### Teste de ponta a ponta (Playwright, os dois HTMLs reais)

1. Depoente criado no Oitiva 360 (papel testemunha) → roteiro gerado com 33 perguntas → todas as 33 respondidas com texto identificável pela ordem → termo exportado contém as 33 respostas na mesma ordem em que foram registradas (verificado por posição no texto, não só por presença).
2. Envelope exportado: `catalogo_schema_version: "1.1.0"`, `deponente.papel: "PAPEL.TESTEMUNHA"`, `rodada_id` presente, `hash_origem` com prefixo `sha256:`.
3. Importado no Veritas sem erro: 1 prova criada, categoria "Termo de oitiva", proveniência "Gerado internamente", `id_prova` novo e diferente do `rodada_id` de origem.
4. Mesmo arquivo com 1 caractere alterado no `termo.conteudo` → Veritas **rejeitou a importação** com alerta mostrando hash esperado e hash calculado — zero itens criados.

Todos os quatro critérios de aceite da Rodada 5 confirmados na prática.

## Rodada 4 — Contrato Nexo Coger → Oitiva 360 (pauta de instrução, fechada)

### 4.1 — Diagnóstico

Diferente da Rodada 3 (onde não existia contrato algum), aqui **já existia uma integração parcial construída na própria "Rodada 6" interna do Oitiva 360** (numeração própria do changelog de cada ferramenta, sem relação com as Rodadas 1–8 deste projeto):

- **`nexo-coger.html`** já tinha `exportPauta()`: exportava **todos** os fatos não arquivados com estado `ausente`/`indicios` — sem tela de revisão, sem confirmação item a item, sem `pauta_id`, sem referência a depoente (pauta única "geral" do processo, não por pessoa). Usava `catalogoVersion`/`CATALOGO_VERSION` (constante `"1.0"` própria, não relacionada ao `catalogo-canonico.json` da Rodada 1) e `normaId` no formato interno (`N-132-IV`), não no formato canônico do catálogo.
- **`nexo-coger.html` já tinha a estrutura de lacuna pedida em 4.2**, embutida no sistema de pendências (`computePendencias()`): `P1` ("Fato sem prova vinculada", crítico) e `P7` ("Sustentação exclusivamente indiciária/informal", frágil) já eram exatamente os dois critérios de lacuna pedidos (`sem_prova` e `prova_fragil`). Não existia nenhuma marcação de "provas em contradição" a nível de fato — por isso, seguindo a spec, **essa terceira categoria não foi criada nesta rodada**.
- **`oitiva-360.html` já tinha a rotina de importação completa** (`aplicarImportacaoPauta`, seção 2.3 da "Rodada 6" própria do Oitiva): populava `estado.pautaImportada.itens` (pool único compartilhado, chaveado por `fatoId`), do qual cada depoente seleciona os itens relevantes via `d.pautaSelecionada` — ou seja, a resolução "por depoente" já acontecia no momento do uso dentro do Oitiva, não no momento da exportação. Toda a lógica de checklist, roteiro de perguntas pré-selecionadas por norma e badge "pauta enviada" já dependia dessa estrutura.

Decisão de adaptação: como a spec exige explicitamente `pauta_id`, `depoente` e confirmação item a item na exportação — e a arquitetura existente do Oitiva (pool compartilhado + seleção por depoente no uso) é sólida e não deveria ser descartada — a Rodada 4 **manteve o pool compartilhado do Oitiva intacto** e **adicionou** `pauta_id`, `depoente` de destino (armazenado como metadado/rastro, sem restringir a seleção a só aquele depoente) e os campos de rastreabilidade (`idPontoOrigem`, `pautaIdOrigem`, `tipoLacuna`, `confirmadoPeloUsuario`) em cada item importado.

### Contrato final implementado

`nexo-coger.html`:
- Nova tela de revisão de lacunas (`abrirRevisaoPauta()`, botão "🎯 Pauta de instrução por depoente"): lista as sugestões automáticas (P1→`sem_prova`, P7→`prova_fragil`) com checkbox marcado por padrão e pergunta editável, permite adicionar pontos manuais (fato + pergunta livre, `tipo_lacuna:"manual"`) e exige nome + papel (ID do catálogo) do depoente antes de gerar. **Só os itens marcados entram no export** — nenhum ponto sai sem confirmação explícita, mesmo os sugeridos automaticamente.
- Nova `gerarPautaPorDepoente()`: gera `pauta_id` único via contador persistido `doc._seq.PAUTA` (formato `PAUTA.<data>.<seq 3 dígitos>`, testado: duas exportações no mesmo dia geram `PAUTA.2026-07-11.001` e `...002`), `schema_version`/`catalogo_schema_version` (= `CATALOGO_COGER.schema_version`), `depoente:{nome, papel}` com papel por ID do catálogo, e `pontos_instrucao[]` com `normas_relacionadas` convertidas para IDs canônicos via nova `normaInternaParaCanonica()` (conversão determinística `N-132-IV` ↔ `NORMA.L8112.ART132_IV`, validada contra o catálogo embutido antes de usar). Mantém `acusados_contexto` (fora da estrutura ilustrativa da spec, mas necessário — ver abaixo) e `acusados_vinculados` por ponto, preservando a função de sugestão de vínculo já existente no Oitiva.

`oitiva-360.html`:
- `aplicarImportacaoPauta()` adaptada para ler `pontos_instrucao`/`pauta_id`/`catalogo_schema_version` em vez do formato antigo (`pauta`/`catalogoVersion`), com aviso visível (não bloqueante) quando `catalogo_schema_version` diverge — mesmo padrão da Rodada 3.
- Nova `normaCanonicaParaInterna()` (inverso exato da função do Nexo) resolve `normas_relacionadas` de volta para o `normaId` interno usado por `resolverNormaPorId()`/pré-seleção de perguntas — testado: `NORMA.L8112.ART116_III` importado resultou em `enquadramentosAtivos[0].normaId === "N-116-III"`, preservando a pré-seleção de perguntas por norma que já existia.
- Cada item de `estado.pautaImportada.itens` ganhou `idPontoOrigem`, `pautaIdOrigem`, `tipoLacuna`, `confirmadoPeloUsuario` — presentes no dado mesmo sem estar em destaque na UI, conforme o critério de aceite ("não precisa ser visível ao usuário final, mas o dado precisa estar presente").
- `renderResumoPautaNexo()` agora mostra o `pauta_id` da última importação e o depoente de destino (nome + rótulo do papel resolvido do catálogo, nunca o ID cru) — testado: banner mostra "Última pauta importada: PAUTA.2026-07-11.001 — destinada a Maria Testemunha da Silva (Testemunha)".

**Por que `acusados_contexto` ficou fora da estrutura ilustrativa da spec:** é o que alimenta `acusadoSugeridoPorNome()`/`renderVinculoNexo()`, a sugestão (não automática) de vínculo entre o depoente e um acusado do Nexo já existente no Oitiva — sem esse campo, essa funcionalidade quebraria para pautas importadas pelo novo contrato.

### Teste de ponta a ponta (Playwright, os dois HTMLs reais)

1. Exemplo pré-carregado no Nexo (`carregarExemplo()`) → `analisarLacunasPauta()` detecta 1 lacuna real (`sem_prova`) → tela de revisão aberta, depoente preenchido ("Maria Testemunha da Silva", `PAPEL.TESTEMUNHA`) → pauta gerada com `pauta_id: "PAUTA.2026-07-11.001"`, `normas_relacionadas: ["NORMA.L8112.ART116_III"]`, `confirmado_pelo_usuario: true`.
2. Segunda exportação no mesmo teste gerou `PAUTA.2026-07-11.002` — `pauta_id` confirmado único a cada exportação.
3. Arquivo importado no Oitiva 360 sem erro → resumo mostra o `pauta_id` e "destinada a Maria Testemunha da Silva (Testemunha)" → item interno tem `enquadramentosAtivos[0].normaId === "N-116-III"` (convertido corretamente de volta do formato canônico) e carrega `pautaIdOrigem`/`tipoLacuna`/`confirmadoPeloUsuario` para rastreabilidade futura.

Um bug foi pego pelo próprio teste antes do commit: `gerarPautaPorDepoente()` chamava uma função de persistência (`salvarLocalStorage`) que não existe no Nexo Coger — o nome real é `scheduleSave()`. Corrigido antes de fechar a rodada.

## Rodada 3 — Contrato Veritas → Nexo Coger (fechada)

### 3.1 — Padronização do nome `nexo-coger`

Ocorrências de `nexus-coger` encontradas e corrigidas, todas em `nexo-coger.html` (nenhuma em `veritas.html`):
- `LS_KEY_LEGADO='nexus-coger:draft'` e `FERRAMENTA_LEGADO='nexus-coger'` — removidos por inteiro. A spec desta rodada autoriza explicitamente redesenhar sem camada de retrocompatibilidade ("não há arquivos em produção a preservar"), então a checagem de leitura/importação (`loadDraft()`, handler de `#fileInput`) passou a aceitar só `FERRAMENTA==='nexo-coger'`.
- Nome de arquivo de download em `exportJson()`: prefixo `nexus-` (não continha `-coger`, mas era a mesma raiz do nome legado) trocado para `nexo-coger-`, alinhando com a decisão "nome de arquivo sugerido no download" da spec.
- Confirmado por busca (case-insensitive) zero ocorrências remanescentes de `nexus-coger`/`nexuscoger`/`NEXUS_COGER` em ambos os arquivos.

### 3.2 — Estruturas originais encontradas (antes do redesenho)

**Exportação do Veritas (diagnóstico):** não existia nenhuma função de exportação dedicada ao Nexo Coger. `App.exportarDossie()` (a única exportação existente) baixa o `DB.dossie` inteiro — processo, comissão, todos os itens com todos os campos internos — no próprio formato de rascunho do Veritas (`versaoEsquema`, `hashDoDossie`). Não há conceito de "provas" isoladas nem de contrato com outro sistema.

**Importação no Nexo Coger (diagnóstico):** também não existia importação específica do Veritas. O único elo entre os dois sistemas era o campo `hashVeritas` no formulário de prova (`abrirFormProva`), texto livre preenchido manualmente pelo usuário, explicitamente documentado no próprio rótulo como "sem integração automática". O import existente de arquivo (`#fileInput`) só aceita o formato interno do próprio Nexo Coger (`d.ferramenta==='nexo-coger'`); e a "Importação de prova de retorno" (`importarProva`/`#fileInputProva`, Rodada 4) é um contrato à parte, do Oitiva 360, com `tipo` em slug interno do Nexo (`documental`, `testemunhal` etc.) e `fatoIds` — não tem relação com o Veritas.

Conclusão do diagnóstico: a Rodada 3 não estava ajustando um contrato desalinhado — estava criando o contrato Veritas → Nexo do zero, como a própria spec previa como possibilidade.

### Contrato redesenhado e implementado

Novo formato de exportação (`veritas.html`, `App.exportarProvasParaNexo()`, botão "Exportar provas → Nexo Coger"):
```json
{
  "schema_version": "1.0",
  "catalogo_schema_version": "1.0.0",
  "exportado_em": "2026-07-11T22:18:21.354Z",
  "origem": "veritas",
  "origem_instancia": "<processo.id do dossiê Veritas>",
  "provas": [{
    "id_prova": "...", "titulo": "...", "tipo_prova": "PROVA.PRINT_SISTEMA",
    "descricao": "...", "sigilo": "...", "status": "...",
    "proveniencia": { /* exatamente os mesmos campos já existentes no item do Veritas */ },
    "arquivos": [{ "nomeArquivo": "...", "descricao": "...", "hashLocal": "...", "hashDeclarado": "..." }],
    "cadeia_custodia": [ /* linhaDoTempoItem do Veritas, sem alteração de formato */ ]
  }]
}
```
- `tipo_prova` resolvido via novo mapa fixo `CATEGORIA_VERITAS_PARA_PROVA_ID` (uma entrada por chave de `CATEGORIAS`) — nunca texto livre.
- Campos de cadeia de custódia (`proveniencia`, `arquivos`, `cadeia_custodia`) preservados tal como já existiam no Veritas, conforme escopo da rodada.
- Nome de arquivo de download: `nexo-coger-provas-<numero-do-processo>.json`.

Nova importação (`nexo-coger.html`, `importarProvasVeritas()`, botão "Importar provas do Veritas", modal de revisão — nada é importado silenciosamente, mesmo padrão já usado na importação de retorno do Oitiva):
- `tipo_prova` (id do catálogo) resolvido para rótulo em português via `CATALOGO_COGER.tipos_prova` — a tela mostra "Print de sistema", nunca `PROVA.PRINT_SISTEMA` cru.
- `tipo_prova` também mapeado para um dos 8 `TIPOS_PROVA_VALIDOS` internos do Nexo via novo `PROVA_ID_PARA_TIPO_NEXO` (as 9 subcategorias exclusivas do Veritas caem em `documental`, a mais próxima; os 8 tipos nativos mapeiam 1:1); o rótulo de origem mais específico fica preservado em `p.origemVeritas.tipoProvaOrigemLabel` e aparece como badge 🌐 no card da prova no mapa.
- `catalogo_schema_version` do arquivo comparado com `CATALOGO_COGER.schema_version` do Nexo: se diferente, um banner de aviso visível (não bloqueante, mas impossível de não ver) é exibido no topo do modal de revisão antes de qualquer importação — nunca falha silenciosa.
- Proveniência e cadeia de custódia completas do Veritas ficam guardadas em `p.origemVeritas` para rastreabilidade, sem alterar o restante da lógica interna do Nexo Coger.

### Teste de ponta a ponta (Playwright, os dois HTMLs reais no navegador)

1. Item criado no Veritas (categoria `print_sistema`) → exportado → arquivo real gerado com `tipo_prova: "PROVA.PRINT_SISTEMA"`, `catalogo_schema_version: "1.0.0"`, proveniência e 1 evento de cadeia de custódia preservados.
2. Arquivo importado no Nexo Coger → modal mostra "Print de sistema" (não o id cru) → após confirmar, `doc.provas` recebe a prova com `tipo: "documental"` e `origemVeritas.tipoProvaOrigemLabel === "Print de sistema"`.
3. Mesmo arquivo com `catalogo_schema_version` alterada para `"0.9.0"` → modal exibe aviso visível: *"Este arquivo foi exportado com catalogo_schema_version 0.9.0, diferente da versão do catálogo em uso neste Nexo Coger (1.0.0)."*

Os três critérios de aceite da Rodada 3 foram confirmados nesse teste real (não apenas leitura de código).

## Rodada 2 — Correção dos bugs conhecidos (fechada)

Os dois bugs registrados na Rodada 1 foram diagnosticados e corrigidos, consumindo o catálogo canônico por ID nos dois pontos afetados.

### Bug 1 — Classificação incorreta do papel de vítima (Oitiva 360, Rodada 6)

**Diagnóstico:** três camadas foram inspecionadas. A entrada (radio de papel, Etapa 1) e a saída de termo (`gerarTermoTexto()`) já liam `compromisso` dinamicamente de `CATALOGO.papeis` e estavam corretas. A falha estava isolada na lógica de sugestão de exportação de prova para o Nexo — `tipoSugeridoParaItem()` (Rodada 6, seção 6.3), chamada só em `abrirDialogoExportarProva()` (nenhuma outra rodada reutiliza essa função, então o bug não se repetia em outro lugar): retornava `{ tipo: "testemunhal", compromissada: true }` para o papel `vitima`, hardcoded, contradizendo `PAPEL.VITIMA.compromisso === false` já fixado no catálogo canônico desde a Rodada 1.

**Correção:** `oitiva-360.html` — `tipoSugeridoParaItem()` agora resolve o slug interno (`d.papel`) para o ID do catálogo via novo mapa `PAPEL_SLUG_PARA_ID_CATALOGO` e lê `compromisso` de `CATALOGO_COGER.papeis_pessoa` em vez de um booleano fixo. Teste manual (Node, fora do DOM): `tipoSugeridoParaItem({papel:'vitima'})` agora retorna `compromissada:false`; os demais papéis (`acusado`, `declarante_informante`, `testemunha`, `situacao_indefinida`) mantiveram o comportamento anterior — sem regressão.

### Bug 2 — Ausência de "pessoa em situação indefinida" no vocabulário de prova do Nexo Coger

**Diagnóstico:** o Nexo Coger não tem, em lugar nenhum do arquivo, um conceito genérico de "papel de pessoa" — a única entidade de pessoa é `doc.acusados[]`. O único ponto onde um depoente é referenciado ao vincular prova a um fato é o formulário de detalhe de prova testemunhal/declaração de informante (`abrirFormProva()`), que capturava o depoente apenas como nome livre + um booleano `compromissada`, sem nenhum campo de papel — por isso `PAPEL.PESSOA_SITUACAO_INDEFINIDA` (e qualquer outro papel) não podia aparecer em lugar nenhum: não faltava uma opção em uma lista, faltava a lista em si. Não existem "seletor de papel ao vincular fato-prova" separado, "filtros do mapa fático-probatório" por papel, nem tela de exportação/relatório listando papéis — o mapa SVG e a matriz de força probatória do Nexo não segmentam por papel de pessoa.

**Correção:** `nexo-coger.html` — o formulário de detalhe de prova testemunhal/declaração de informante ganhou o campo "Papel do depoente" (`d.papelId`), populado dinamicamente a partir de `CATALOGO_COGER.papeis_pessoa.filter(status==='ativo')` (não hardcoded), com "Compromissada?" pré-preenchido a partir do `compromisso` do papel escolhido (ainda editável pela comissão, no mesmo padrão de outros campos "sugestão, nunca aplicação automática" do sistema). Teste (Node, fora do DOM): a lista de opções gerada contém os 5 papéis do catálogo, incluindo `PAPEL.PESSOA_SITUACAO_INDEFINIDA` — confirmado programaticamente. Como esse era o único ponto do arquivo relacionado a papel de pessoa, a correção cobre a totalidade dos "seletores/formulários de papel" do critério de aceite (conjunto de um único ponto).

**Nota:** o critério de aceite geral pedia ausência de string livre "vítima"/"pessoa em situação indefinida" nos dois pontos corrigidos — confirmado: ambos os pontos agora referenciam apenas os IDs `PAPEL.VITIMA`/`PAPEL.PESSOA_SITUACAO_INDEFINIDA` do catálogo, nunca a string solta.

## Rodada 1 — Itens migrados por sistema de origem

### Nexo Coger (base de partida)
- **Papéis de pessoa:** apenas `PAPEL.ACUSADO` existia (array `doc.acusados[]`). O Nexo Coger não tinha vocabulário próprio de vítima, testemunha, declarante/informante ou pessoa em situação indefinida.
- **Tipos de prova:** `PROVA.DOCUMENTAL`, `PROVA.PERICIAL`, `PROVA.TESTEMUNHAL`, `PROVA.DECLARACAO_INFORMANTE`, `PROVA.INTERROGATORIO`, `PROVA.DILIGENCIA`, `PROVA.EMPRESTADA`, `PROVA.INDICIARIA` — migrados de `TIPOS_PROVA_VALIDOS`.
- **Normas:** todas as 52 entradas de `NORMAS_BASE` migradas — 45 dispositivos da Lei nº 8.112/1990 (arts. 116, 117, 130 §1º e 132) e 7 do art. 32 da Lei nº 12.527/2011 (LAI).

### Oitiva 360
- **Papéis de pessoa:** `PAPEL.VITIMA`, `PAPEL.TESTEMUNHA`, `PAPEL.DECLARANTE_INFORMANTE` e `PAPEL.PESSOA_SITUACAO_INDEFINIDA` migrados de `CATALOGO.papeis`, com descrições literais preservadas. A definição de `PAPEL.ACUSADO` do catálogo canônico usa o texto mais completo do Oitiva 360 (direito ao silêncio, Lei 13.869/2019, Súmula Vinculante nº 5/STF, art. 159), unificando com o `PAPEL.ACUSADO` mínimo do Nexo Coger.

### Veritas Digital
- **Tipos de prova:** nenhum papel de pessoa (Veritas não lida com depoentes, só com cadeia de custódia de evidência). As categorias de evidência digital/física (`CATEGORIAS`) foram registradas como novos itens de `tipos_prova`, pois são subcategorias mais finas que não colidem 1:1 com o vocabulário do Nexo: `PROVA.PRINT_SISTEMA`, `PROVA.DOCUMENTO_FINANCEIRO`, `PROVA.COMUNICACAO`, `PROVA.FOTO_VIDEO`, `PROVA.OFICIO`, `PROVA.DECISAO_JUDICIAL`, `PROVA.DOCUMENTO_FISICO`, `PROVA.DISPOSITIVO_FISICO`, `PROVA.OUTRO`. A categoria `laudo_pericia` do Veritas foi tratada como equivalente a `PROVA.PERICIAL` (já existente), sem duplicação.
- Vocabulário interno de rastreabilidade forense do Veritas (`PROVENIENCIA_TIPOS`, `ELEMENTO_FISICO_TIPOS`, `CONDICAO_LACRE`, `SIGILO`, `STATUS_ITEM`, `RESULTADO`, `EVENTO_TIPOS`) **não** entrou no catálogo — não é papel de pessoa, tipo de prova ou norma; é metadado de cadeia de custódia, fora do escopo desta rodada.
- Normas: Veritas cita apenas art. 158-A a 158-F do CPP (Lei nº 13.964/2019), por analogia, e explicitamente declara não vincular-se ao CPP. Não há referência real a Lei 8.112/1990 ou LAI no arquivo — nenhuma norma nova migrada dessa fonte.

## Itens novos criados (sem equivalente exato em nenhuma fonte)

- Nenhum item foi criado do zero fora do que já existia em algum dos três sistemas. Todos os itens "novos" no catálogo (papéis do Oitiva, categorias de prova do Veritas) já existiam em pelo menos uma das três ferramentas — a novidade é que passam a ter ID estável compartilhado, o que antes não existia.

## Correções de bug resolvidas nesta rodada

1. **`PAPEL.PESSOA_SITUACAO_INDEFINIDA` ausente no vocabulário do Nexo Coger** — o Nexo não tinha nenhum papel equivalente a "pessoa em situação indefinida" (confirmado por busca exaustiva, zero ocorrências). O catálogo agora inclui `PAPEL.PESSOA_SITUACAO_INDEFINIDA`, usando a definição do Oitiva 360 como fonte única (não havia versão do Nexo para conciliar).
2. **Divergência/bug na classificação de `PAPEL.VITIMA`** — o Nexo Coger não tinha nenhum conceito de vítima (zero ocorrências de "vítima" no arquivo); o Oitiva 360 define `vitima` com `compromisso: false`, mas a função `tipoSugeridoParaItem()` (usada ao exportar prova de retorno para o Nexo) marcava incorretamente `{ tipo: "testemunhal", compromissada: true }` para o papel `vitima`, contradizendo a própria definição do papel no mesmo arquivo. O catálogo agora fixa `PAPEL.VITIMA` com `compromisso: false` como definição única e documenta a nota do bug. **A correção da lógica interna (`tipoSugeridoParaItem()` no Oitiva 360 e o reconhecimento do papel vítima no Nexo) fica para as Rodadas 2–6**, conforme escopo desta entrega (criar o catálogo, não ainda consumi-lo).

## Observação sobre a meta de "45 dispositivos"

A especificação da Rodada 1 menciona um "conjunto canônico de 45 dispositivos da Lei nº 8.112 e da LAI". A extração real do Nexo Coger mostra que **os 45 dispositivos correspondem exatamente à Lei nº 8.112/1990 isolada** (12 do art. 116 + 19 do art. 117 + 1 do art. 130 §1º + 13 do art. 132 = 45); a LAI contribui mais 7 dispositivos próprios (art. 32, I a VII), totalizando **52 normas** no catálogo. Nenhum dispositivo foi omitido — os 52 refletem o universo completo já mapeado no Nexo Coger.

## Critérios de aceite — status

- [x] Todo papel de pessoa, tipo de prova e norma hoje usado em qualquer um dos três sistemas tem um ID correspondente no catálogo.
- [x] Nenhum ID duplicado ou ambíguo entre categorias (validado programaticamente — 74 IDs, 74 únicos).
- [x] Os três HTMLs carregam exatamente o mesmo `CATALOGO_COGER` (mesmo hash8 `5906e98f`).
- [x] `PAPEL.PESSOA_SITUACAO_INDEFINIDA` presente e `PAPEL.VITIMA` com definição única, sem divergência entre Nexo Coger e Oitiva 360.
