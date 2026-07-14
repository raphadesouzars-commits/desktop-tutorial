# Auditoria de código-fonte — Oitiva 360 (fluxo manual, sem pauta importada)

Fonte: `/home/user/desktop-tutorial/ferramentas/oitiva-360.html` (6252 linhas, SPA vanilla JS em IIFE).
Tudo abaixo foi extraído por leitura direta do HTML/JS (Grep + Read), citando texto exato de labels, placeholders e mensagens onde indicado entre aspas.

---

## 1. Criação manual de um depoente/rodada de oitiva (SEM pauta importada)

### 1.0 Pré-requisito ANTES do diálogo "Adicionar depoente" ficar habilitado

Na Tela do Processo existe o cartão **"Matriz de Apuração (nível processo — obrigatória)"** (`id="cartao-matriz"`), com 4 campos, todos `textarea`, todos com `class="obrigatorio"` no label:

1. `campo-conduta` (`data-campo-matriz="conduta"`) — label **"Conduta investigada"**, texto de apoio: "Qual ação ou omissão está sendo apurada?"
2. `campo-investigado` (`data-campo-matriz="investigado"`) — label **"Investigado"**, texto de apoio: "Quem está, em tese, vinculado à conduta?"
3. `campo-elementos-disponiveis` (`data-campo-matriz="elementosDisponiveis"`) — label **"Elementos disponíveis"**, texto de apoio: "Que provas/informações já constam dos autos?"
4. `campo-hipotese` (`data-campo-matriz="hipotese"`) — label **"Hipótese investigativa"**, texto de apoio: "Qual a linha de raciocínio que conecta os fatos?"

Função `matrizCompleta(m)` (linha 3577): retorna `true` somente se os 4 campos (`conduta`, `investigado`, `elementosDisponiveis`, `hipotese`) estiverem preenchidos (`.trim()` não vazio) — os 4 são obrigatórios, sem exceção.

`atualizarAvisoMatriz()` (linha 3737): enquanto a matriz não estiver completa, o botão `btn-add-depoente` fica `disabled = true` e é exibido o aviso pedagógico:
> "Preencha os quatro campos da Matriz de Apuração acima para habilitar a adição de depoentes — \"roteiro sem matriz é roteiro cego\"."

O handler de clique de `btn-add-depoente` (linha 3810) ainda faz dupla checagem: `if (!matrizCompleta()) return;` (comentário no código: "botão já fica desabilitado, dupla checagem").

### 1.1 Diálogo "Adicionar depoente" (`dialogo-add-depoente`, linha 1906)

Título: **"Adicionar depoente"**.

Campos, na ordem em que aparecem no DOM:

1. **Identificação** (`campo-identificacao-depoente`, `<input type="text">`, obrigatório — `label class="obrigatorio"`)
   - Placeholder: `Ex.: T-01 ou "Depoente A"`
   - Texto de apoio: "Use iniciais ou nome fictício — evite dados pessoais reais (LGPD)."
2. **Elementos buscados com este depoente** (`campo-elementos-buscados-depoente`, `<textarea>`, obrigatório — `label class="obrigatorio"`)
   - Texto de apoio: "Por que ouvir ESTA pessoa? O que ela pode trazer?"

Botões no rodapé: "Cancelar" (`btn-cancelar-add-depoente`) e "Adicionar" (`btn-confirmar-add-depoente`).

Validação no handler de `btn-confirmar-add-depoente` (linha 3842): se `identificacao` ou `elementosBuscados` estiverem vazios (após `.trim()`), exibe em `erro-add-depoente`:
> "Identificação e \"elementos buscados\" são obrigatórios para adicionar o depoente."
e não prossegue. Se ambos preenchidos, cria o depoente via `novoDepoente()` (linha 3824) com valores default: `papel: null`, `infracao: null`, `status: "rascunho"`, `ato.modalidade: "presencial"`, `roteiro: []`, `checklist: {}`, `pautaSelecionada: []`, `pautaConclusao: {}`, `referenciaAcusadoNexo: null` — e fecha o diálogo, voltando à lista de depoentes.

### 1.2 Etapa 1 do wizard — "Dados do Ato"

Ao clicar em "Abrir depoente" o wizard abre com stepper: "1. Dados do Ato" / "2. Depoente" / "3. Montagem do Roteiro" / "4. Revisão e Checklist".

`renderEtapa1()` popula os seguintes campos (todos opcionais — não há chamada de validação para a Etapa 1 em `irParaEtapa`):

**Cartão "Dados herdados do processo (editáveis pontualmente para este ato)":**
- Nº do processo (`ato-numero`)
- Portaria (`ato-portaria`)
- Presidente da comissão: Nome / Cargo / Matrícula (`ato-presidente-nome/cargo/matricula`)
- Secretário(a): Nome / Cargo / Matrícula (`ato-secretario-nome/cargo/matricula`)
- Vogais: lista repetível (Nome/Cargo/Matrícula por linha) com botão "+ Adicionar vogal" (`btn-add-vogal-ato`)

**Cartão "Data, hora e local do ato":**
- Data (`ato-data`, `type="date"`)
- Hora (`ato-hora`, `type="time"`)
- Local (`ato-local`, texto)
- Modalidade: rádio `name="ato-modalidade"` com opções **"Presencial"** (`value="presencial"`) e **"Videoconferência"** (`value="videoconferencia"`)
- Checkbox "Há defensor constituído presente?" (`ato-defensor-presente`) — texto de apoio: "Define se o bloco \"Palavra à defesa / reperguntas\" entra no roteiro." Se marcado, revela o bloco "Nome do defensor" (`ato-defensor-nome`) e "Nº de inscrição na OAB" (`ato-defensor-oab`).

**Cartão "Estratégia da equipe (opcional)":**
- Quem pergunta (`ato-quem-pergunta`)
- Quem revisa ("guardião da pergunta de ouro") (`ato-quem-revisa`)
- Formato de abertura (`ato-formato-abertura`, select): opções "Não definido", "Explanação livre inicial" (`explanacao_livre`), "Apenas respostas pontuais" (`respostas_pontuais`)
- Momento de exibição de documentos (`ato-momento-documentos`, textarea)

### 1.3 Etapa 2 do wizard — "Depoente"

**Cartão "Identificação":**
- Aviso LGPD fixo: "Recomendamos usar iniciais ou nome fictício. Esta ferramenta não deve armazenar dados pessoais reais dos envolvidos (aviso LGPD)."
- **Identificação** (`dep-identificacao`, obrigatório)
- Bloco "Vincular a acusado do Nexo (opcional)" (`campo-vinculo-manual-nexo`) — `hidden` por padrão; só aparece quando há sugestão de vínculo com pauta importada do Nexo (não faz parte do fluxo manual sem pauta).
- **Elementos buscados com este depoente** (`dep-elementos-buscados`, textarea, obrigatório) — mesmo texto de apoio da etapa anterior.

**Cartão "Papel do depoente"** (`papel-opcoes`): renderizado dinamicamente a partir de `CATALOGO.papeis`, como rádios `name="papel-depoente"`. As 5 opções de papel, na ordem definida no catálogo (linhas 2684-2745):

1. **Testemunha** (`id: "testemunha"`) — descrição exibida: "Presta compromisso legal de dizer a verdade (art. 342, CP). Responde a perguntas de praxe sobre parentesco, amizade/inimizade, interesse e impedimento. Tem o dever de depor, ressalvado o direito de não produzir prova contra si mesma."
2. **Declarante/Informante** (`id: "declarante_informante"`) — "Não presta compromisso legal de dizer a verdade. Ouvido em razão de vínculo com o investigado ou de participação anterior no contexto apurado. Não responde por falso testemunho, mas apela-se à sua colaboração voluntária com a apuração."
3. **Pessoa em Situação Indefinida** (`id: "situacao_indefinida"`) — "Autos indicam possível envolvimento da pessoa no contexto fático, sem elementos ainda para tratá-la como investigada. Não presta compromisso de testemunha e tem facultado o direito ao silêncio, por cautela e analogia à vedação à autoincriminação. Exige consulta prévia à defesa sobre o enquadramento adotado."
4. **Vítima** (`id: "vitima"`) — "Não é testemunha e não presta compromisso legal de dizer a verdade, não respondendo por falso testemunho — mas sujeita-se à denunciação caluniosa. Documentação própria: Termo de Depoimento, Termo de Declarações ou Alegações do Ofendido, conforme o caso."
5. **Investigado/Acusado** (`id: "acusado"`) — "Não presta compromisso. Tem direito constitucional ao silêncio, com advertência da Lei 13.869/2019 (art. 15, parágrafo único, I): se exercido o silêncio, a comissão não formula questionamentos. Defensor facultativo (Súmula Vinculante nº 5/STF). O interrogatório deve ser o último ato da instrução (art. 159), com antecedência mínima de 3 dias úteis na intimação."

Selecionar "Testemunha" com infração `N-132-IV` (enriquecimento ilícito) revela um cartão extra oculto por padrão, **"Terceiro interposto"** (`cartao-terceiro-interposto`), com checkbox: "Este depoente é possível terceiro interposto (familiar/pessoa em cujo nome está bem sob suspeita)".

**Cartão "Pauta do Nexo"** (`cartao-pauta-nexo`) — `hidden` por padrão; só aparece "se o processo tiver recebido uma pauta importada" (comentário explícito na linha 1808-1809). **Não faz parte do fluxo manual sem pauta.**

**Cartão "Categoria de infração":**
- Buscar infração (`dep-infracao-busca`, texto) — placeholder: `Buscar por rótulo ou dispositivo (ex.: "sigilo", "art. 117, IX")…`
- **Infração apurada** (`dep-infracao`, `<select>`, obrigatório) — populado dinamicamente por `popularSelectInfracao()` a partir de `CATALOGO.infracoes` (52 normas). Estrutura: um `<option value="">Selecione…</option>` inicial, seguido de `<optgroup>` agrupados por origem normativa, na ordem fixa definida em `GRUPOS_INFRACAO_ORDEM`:
  - "Lei 8.112/90 — Deveres (art. 116)" (prefixo `N-116-`)
  - "Lei 8.112/90 — Proibições (art. 117)" (prefixo `N-117-`)
  - "Lei 8.112/90 — Demissão (art. 132)" (prefixo `N-132-`)
  - "Lei 8.112/90 — Outras (art. 130)" (prefixo `N-130-`)
  - "LAI (Lei nº 12.527/2011)" (prefixo `N-LAI-`)
  - "Outras categorias" (fallback)
  Dentro de cada grupo, as opções são ordenadas por algarismo romano do inciso (função `incisoOrdemDaInfracao`/`romanoParaInt`). O rótulo de cada `<option>` é `rótulo — dispositivo`. O campo de busca refiltra o `<select>` por rótulo, dispositivo ou id a cada tecla digitada.

**Cartão "Perfil do depoente (opcional)"** — não obrigatório:
- Nível de conhecimento dos fatos (`dep-nivel-conhecimento`, select): "Não definido", "Presenciou diretamente (viu)" (`viu`), "Ouviu de participante direto" (`ouviu_participante`), "Teve acesso a documentos/registros" (`documentos`), "Ouviu dizer (relato de terceiros)" (`ouviu_dizer`)
- Vínculos com investigado/vítima/administração (`dep-vinculos`, textarea)

**Validação para avançar (`validarEtapa2`, linha 4408):** obrigatórios são exatamente 4 — identificação, elementos buscados, papel do depoente, categoria de infração (infração/select). Se algum faltar, ao tentar avançar (`irParaEtapa` com destino > 2) o usuário é mantido na Etapa 2 e vê o erro:
> "Para avançar, preencha: " + lista dos itens faltantes (ex.: "identificação, elementos buscados, papel do depoente, categoria de infração") + "."

---

## 2. Registro de perguntas e respostas

### 2.1 Etapa 3 — Montagem do Roteiro (geração automática)

`renderEtapa3()` chama `garantirRoteiroGerado(d)`, que monta o roteiro a partir da combinação papel + infração (e, se aplicável, marcação de terceiro interposto), organizando as perguntas em blocos fixos definidos em `CATALOGO.blocos` (13 blocos, ex.: "Preparação e cenário", "Acolhimento e identificação dos presentes", "Abertura formal", "Avisos legais e LGPD", "Qualificação, praxe e compromisso/advertências", "Abertura para objeções da defesa", "Contexto funcional", "Materialidade", "Autoria e participação", "Elemento subjetivo (dolo/culpa)", "Circunstâncias do art. 128", "Palavra à defesa / reperguntas", "Fechamento"). Se papel/infração/terceiro-interposto mudarem depois de gerado, a tela mostra aviso pedagógico com botão "Regenerar roteiro" (confirmação via `confirm()`: "Isso substituirá as perguntas atuais do roteiro (inclusive as adicionadas manualmente) pelas sugestões do banco para o papel e infração atuais. Deseja continuar?"). Nessa etapa o usuário pode adicionar/editar/remover perguntas (perguntas de praxe da testemunha são `removivel: false`, ou seja, fixas). Não há registro de resposta nesta etapa — apenas montagem do roteiro de perguntas.

### 2.2 Etapa 4 — seção "Respostas registradas"

Localizada em `renderEtapa4()` (linha 5617 em diante). Estrutura, confirmada pelo código:

- Para cada pergunta do roteiro (obtidas via `perguntasRespostasOrdenadas(d)`, na ordem do roteiro), é renderizado um bloco:
  - Título com o texto da pergunta (`item.texto`)
  - **Uma única `<textarea>` por pergunta**, atributo `data-resposta-roteiro="<chave da pergunta>"`, placeholder **"Resposta dada pelo(a) depoente"**, valor inicial = resposta já salva (`item.resposta`).
- **Não existe** nenhum campo auxiliar por pergunta (sem campo de observação e sem marcação de relevância) — o único controle por pergunta é a textarea de resposta. Confirmado por leitura do bloco HTML: apenas `titulo-item-pauta` (texto da pergunta) + a `textarea[data-resposta-roteiro]`, nenhum outro input.
- Cada textarea tem listener de `input` que grava em `d.respostasRoteiro[chave]` e persiste via `salvarLocalStorage()` (linha 5762-5768).
- Caso o papel tenha direito ao silêncio e o depoente tenha exercido esse direito (`acusadoSilencio === true`), a seção inteira exibe apenas o texto: "Direito ao silêncio exercido — nenhuma pergunta foi dirigida ao(à) depoente nesta sessão." (sem textareas).
- Se o roteiro ainda não tiver perguntas: "Roteiro ainda não gerado ou sem perguntas. Volte à Etapa 3."

### 2.3 "Resumo da resposta" e "Acusado alternativo" — confirmação de escopo

Esses dois campos (`data-pauta-conclusao-resumo` / `data-pauta-conclusao-acusado-alt`, placeholders **"Resumo da resposta (para o contexto do acusado no Nexo Coger)"** e **"Acusado alternativo (opcional — deixe em branco para o padrão do processo)"**) pertencem ao bloco **"Pauta do Nexo — itens abordados nesta sessão"** (`cartao-pauta-conclusao`), que só é renderizado dentro do `if`:
```
if (estado.pautaImportada && d.pautaSelecionada && d.pautaSelecionada.length){ ... }
```
Ou seja: **NÃO fazem parte do fluxo manual sem pauta importada.** Confirmado por leitura direta — sem `estado.pautaImportada` preenchido (o que só acontece ao importar um arquivo de pauta do Nexo Coger), esse cartão inteiro não é gerado, e a seção "Respostas registradas" (item 2.2 acima) é o único local de registro de resposta no fluxo manual.

---

## 3. Geração do termo

Função `gerarTermoTexto(d)` (linha 5358). Não há requisito formal de bloqueio: o termo é gerado automaticamente ao entrar na Etapa 4, via:
```js
if (!d.termoTexto){
  d.termoTexto = gerarTermoTexto(d);
  salvarLocalStorage();
}
```
(linha 5555-5558) — isto é, roda incondicionalmente sempre que a Etapa 4 é renderizada e ainda não existe termo salvo; usa "____" como placeholder para campos vazios (hora, local, portaria, presidente, vogais, secretário, nome) em vez de bloquear a geração.

**Estrutura do texto final** (concatenação de trechos):
1. Cabeçalho: `"TERMO DE " + tipo` — tipo é "INTERROGATÓRIO" (se papel = acusado), "OITIVA DE TESTEMUNHA" (se papel = testemunha) ou "OITIVA" (demais papéis).
2. Parágrafo de abertura/qualificação: data por extenso, hora, local, Portaria, composição da comissão (presidente/vogais/secretário), nome do depoente, forma de intimação/notificação e papel. Se acusado com defensor presente e identificado, acrescenta menção ao defensor (nome/OAB); se acusado sem defensor preenchido, usa texto com lacunas "___".
3. Parágrafo de qualificação civil/funcional (texto fixo).
4. Parágrafo de compromisso/advertências — varia por papel: compromisso legal + perguntas de praxe (testemunha); silêncio constitucional com fundamentação da Lei 13.869/2019 e SV 5 (acusado); silêncio por cautela/analogia com registro de consulta prévia à defesa (situação indefinida); isenção de compromisso com advertência de denunciação caluniosa (vítima); colaboração voluntária sem compromisso nem falso testemunho (declarante/informante).
5. Placeholder fixo: "[Registro de incidentes, se houver: contradita, arguição de parcialidade, questões de ordem, protestos — com a deliberação da comissão.]"
6. Corpo de perguntas e respostas — "Passou-se à inquirição pela comissão:" seguido da transcrição real, pergunta a pergunta, na ordem do roteiro: `N. P: <texto>\n   R: <resposta ou "[sem resposta registrada]">`. Se silêncio exercido: "[Direito ao silêncio exercido — nenhuma pergunta foi dirigida ao(à) depoente.]". Se não há perguntas: "[Nenhuma pergunta do roteiro foi registrada.]".
7. Placeholder fixo: "Dada a palavra à defesa, [formulou as seguintes reperguntas | nada requereu]."
8. Fecho fixo: "Nada mais havendo, encerrou-se o presente termo, que, lido e achado conforme, vai assinado por todos os presentes."
9. **Tabela/colunas de membros da comissão** (`formatarColunasMembrosTermo`, linha 5291): 3 colunas — Presidente, Vogal(is), Secretário(a) — cada uma com nome/cargo/matrícula; vogais múltiplos são concatenados com "; "; texto truncado a 22 caracteres por célula (com reticências) para não desalinhar a tabela impressa em fonte monoespaçada.

**Fluxo de exibição/ações** (cartão "Termo de redução"):
- `<textarea id="termo-texto">` editável (edições manuais são salvas em `d.termoTexto` a cada `input`).
- Botão **"Copiar termo"** (`btn-copiar-termo`) — usa `navigator.clipboard.writeText`; em caso de falha, seleciona o texto e muda o rótulo do botão para "Selecionado — use Ctrl+C".
- Botão **"Regenerar termo"** (`btn-regenerar-termo`) — pede confirmação: "Isso substituirá o texto atual do termo (inclusive edições manuais) pelo modelo gerado a partir dos dados do ato. Deseja continuar?" e, se confirmado, roda `gerarTermoTexto(d)` novamente.
- Botão **"Imprimir termo"** (`btn-imprimir-termo`).

---

## 4. Checklist e alertas de nulidade

Ambos aparecem na Etapa 4, dependentes do papel escolhido (e de infração/modalidade em alguns itens):

- **"Checklist pré-oitiva"**: lista de itens de `CATALOGO.checklistItens` filtrados por `itensChecklistAplicaveis(d)` — inclui itens sempre aplicáveis (revisão da matriz, intimação regular, roteiro revisado, documentos separados, ambiente adequado, trajes adequados) mais itens condicionais por papel (ex.: "papel == acusado" → notificação com 3 dias úteis, interrogatório como último ato, advertências obrigatórias), por modalidade ("modalidade == videoconferencia" → teste de conexão, avisos de gravação/LGPD, regra de conversa reservada, foco sem distrações) e por infração ("infracao == N-132-IV" → documentação patrimonial, oportunidade de justificação do acréscimo, identificação de terceiros interpostos). Cada item é um checkbox simples.
- **"Alertas de nulidade"**: compara os itens de checklist condicionados especificamente ao papel selecionado (`condicao === "papel == " + d.papel`) contra os já marcados em `d.checklist`; se houver pendentes, exibe alerta listando-os ("Itens obrigatórios do checklist para o papel selecionado ainda não confirmados: ..."); se todos confirmados, exibe aviso positivo ("Todos os itens obrigatórios do checklist para o papel selecionado estão confirmados."); se o papel não tiver exigências específicas, mostra texto neutro ("Sem exigências específicas de nulidade para o papel selecionado além do checklist comum acima.").

---

## 5. Outras observações úteis (mensagens que o usuário vê no fluxo manual)

- Ao remover um depoente: `confirm("Remover o depoente \"" + d.identificacao + "\"? Esta ação não pode ser desfeita.")`.
- Ao clicar "Novo processo" com dados não exportados: `confirm("Isso vai descartar os dados do processo atual (não exportado). Deseja continuar?")`.
- Exportação do processo (`btn-exportar-processo`) fica desabilitada até o campo "Nº do processo" estar preenchido, com aviso: "Preencha o \"Nº do processo\" para habilitar a exportação — o número é usado no nome do arquivo .json exportado." (função `atualizarAvisoNumeroProcesso`).
- Ao regenerar o roteiro (Etapa 3): `confirm("Isso substituirá as perguntas atuais do roteiro (inclusive as adicionadas manualmente) pelas sugestões do banco para o papel e infração atuais. Deseja continuar?")`.
- Ao regenerar o termo (Etapa 4): `confirm("Isso substituirá o texto atual do termo (inclusive edições manuais) pelo modelo gerado a partir dos dados do ato. Deseja continuar?")`.
- Mensagens de `alert()` relacionadas a importação de arquivo (.json do processo / pauta do Nexo) só se aplicam a fluxos de importação, fora do escopo "sem pauta importada" pedido — citadas aqui apenas por completude: "Arquivo inválido: não foi possível interpretar o JSON.", "Arquivo inválido: estrutura de processo do Oitiva 360 não reconhecida.", "Arquivo inválido: este arquivo não é uma pauta exportada pelo Nexo Coger (...)", "Arquivo inválido: a pauta não traz \"pauta_id\".", "A pauta " + pauta_id + " já havia sido importada antes — itens existentes foram atualizados, nenhum item duplicado foi criado.".
- Botão de exportação para o Nexo Coger ("Exportar prova(s) para o Nexo" / "Exportar retorno (contexto do acusado)") só aparece quando há itens de pauta abordados na sessão (`itensPautaAbordadosNestaSessao(d).length`) — não aparece no fluxo manual sem pauta.
- O botão "Exportar termo para o Veritas" (`btn-exportar-termo-veritas`) está sempre visível na Etapa 4, independente de pauta importada.

---

## 6. Gerenciar múltiplos depoentes do mesmo processo

### 6.1 Lista de depoentes (Tela do Processo)

Antes de entrar no wizard de qualquer depoente específico, a Tela do Processo mostra uma tabela de depoentes já cadastrados — `renderListaDepoentes()` (linha 3693), alvo do `<div id="tabela-depoentes-wrap">`. É a partir dela que o diálogo `dialogo-add-depoente` é aberto: o botão `btn-add-depoente` (linha 3810, na mesma tela) dispara `dialogoAddDepoente.showModal()`, mas só depois de a Matriz de Apuração estar completa (ver seção 1.0 acima).

Se não houver nenhum depoente ainda: `<p class="vazio">Nenhum depoente adicionado ainda.</p>`.

Com depoentes cadastrados, a tabela tem colunas **Identificação / Papel / Infração / Status / (ações)**:
- Papel exibido é o nome de `CATALOGO.papeis` (ou "não definido" em `<span class="vazio">`, se ainda não escolhido na Etapa 2).
- Infração exibida é o nome/rótulo de `CATALOGO.infracoes` (ou "não definida").
- Status é um badge (`badge-status <status>`) com rótulo de `statusLabel(s)` (linha 3689): `rascunho` → "Rascunho", `roteiro_pronto` → "Roteiro pronto", `oitiva_realizada` → "Oitiva realizada". Esse status é o do **depoente** (progresso do wizard), não o de item de pauta (seção 9 abaixo trata do status de item de pauta, que é outro conceito).
- Cada linha tem dois botões: **"Abrir depoente"** (`data-abrir-wizard="<id>"`) e **"Remover"** (`data-remover-depoente="<id>"`, classe `perigo pequeno`).

### 6.2 Alternar entre depoentes já cadastrados

Não há "próximo/anterior" — a navegação entre depoentes é sempre: fechar o wizard atual (`fecharWizard()`, que zera `depoenteAtivoId`, esconde `tela-wizard-depoente` e reexibe `tela-processo` com a lista) e clicar em "Abrir depoente" na linha correspondente ao próximo depoente desejado.

### 6.3 Editar um depoente existente — sempre reabre na Etapa 1

`abrirWizard(depoenteId)` (linha 4387) é o handler de "Abrir depoente": define `depoenteAtivoId`, garante a estrutura de `d.ato` (`garantirEstruturaAto`) e chama `irParaEtapa(1, { forcar: true })`. Ou seja: **qualquer reabertura de um depoente já cadastrado (mesmo com wizard já concluído/"Oitiva realizada") sempre volta para a Etapa 1 ("Dados do Ato")** — não há memória de "última etapa visitada". O usuário precisa navegar manualmente pelo stepper (1 → 2 → 3 → 4) até a etapa que deseja editar; os dados de cada etapa já preenchida permanecem salvos e são apenas re-renderizados.

### 6.4 Remoção de um depoente

Confirmado: o botão **"Remover"** de cada linha da lista (`data-remover-depoente`, seção 6.1 acima) é o único ponto de remoção de depoente na ferramenta — não há atalho de remoção de dentro do wizard. O handler (linha 3716-3726) exibe `confirm("Remover o depoente \"" + d.identificacao + "\"? Esta ação não pode ser desfeita.")`; se confirmado, filtra o depoente de `estado.depoentes`, persiste via `salvarLocalStorage()` e re-renderiza a lista. Não há "lixeira"/desfazer — a remoção é definitiva a partir da confirmação.

---

## 7. "Kit de Incidentes" (equivalente ao "kit de situações" pedido — não existe funcionalidade com esse nome exato)

Busca por "situaç"/"kit" no código não encontrou nada chamado "kit de situações" ou "kit-situacoes". O que existe, e que cumpre exatamente esse papel, é o **"Kit de Incidentes"** (`CATALOGO.formulasIncidentes`, linha 3218 em diante) — um banco de 17 fórmulas verbais prontas para o condutor usar em situações específicas durante a oitiva/interrogatório (contradita, intimidação, pergunta ofensiva, pergunta indutiva, imprecisão do depoente, contradição/possível falso testemunho, questão de ordem, elucubrações/juízo de valor, consulta a anotações, conversa reservada advogado-cliente, abalo emocional, pedido-surpresa de diligência, táticas de desestabilização, pedido de perícia, perguntas impertinentes/protelatórias, pedido de esclarecimento/impugnação de pergunta da comissão, advogado da testemunha).

Cada item tem: `id`, `grupo` (categoria, ex.: "Postura da defesa", "Depoimento do depoente", "Condução do ato", "Cuidado com o depoente", "Táticas de desestabilização"), `situacao` (rótulo curto do gatilho), `formulaVerbal` (o texto pronto, em geral entre aspas, para o presidente falar), opcionalmente `sequencia` (passos numerados antes da fala) e `baseLegal`. Comentários no código confirmam a origem: fórmulas extraídas/adaptadas do documento-fonte "Roteiros das Simulações de Oitiva e Interrogatório" (Marcos Salles Teixeira/CGU-CRG), com pronomes neutralizados.

**Onde aparece na interface:** é conteúdo de apoio textual, sempre visível (não é preciso buscar), num painel lateral fixo nas **Etapas 3 e 4** do wizard (comentário na linha 5200: "Kit de Incidentes (aside — visível nas etapas 3 e 4)"). No DOM, fica ao lado do painel "💡 Dicas desta tela" (linha 1883-1888), sob o título "Kit de Incidentes" e o container `<div id="kit-incidentes-conteudo">`. `renderKitIncidentes()` (linha 5202) agrupa os 17 itens por `grupo` em blocos `<details>` (um `<summary>` por categoria, expansível), cada item mostrando situação, sequência de passos (se houver), a fórmula verbal e a base legal (se houver).

**Como apoia a condução:** é puramente textual/de apoio — não há nenhuma ação/registro associado (não é um botão que grava algo no processo); o presidente consulta o painel durante a sessão e usa a fórmula sugerida na hora. O próprio banco de conteúdo (`abertura_objecoes_defesa`, `palavra_defesa_reperguntas`, linhas 3212-3213) referencia explicitamente o Kit de Incidentes como remissão cruzada (ex.: "seguir o procedimento de contradita descrito no Kit de Incidentes (inc_contradita)"), confirmando que ele é pensado como script de contingência a ser usado ao vivo, não como documento gerado.

Ver também seção 8 abaixo — o "Cartão de Mesa" é a versão impressa de 17 dos itens deste mesmo Kit de Incidentes (todos, já que todos têm `cartaoMesa: true` no catálogo atual).

---

## 8. Impressão do "Cartão de Mesa"

Botão **"Imprimir Cartão de Mesa"** (`btn-imprimir-cartao-mesa`, classe `secundario`), no cartão "Impressão" da **Etapa 4** ("Revisão e Checklist"), ao lado de "Imprimir roteiro" (linha 5662-5668). Handler (linha 5824-5829): chama `montarAreaImpressaoCartaoMesa()`, depois `prepararAreaImpressaoParaImpressao()` e `window.print()` — é uma impressão isolada (comentário no código: "só o Cartão de Mesa, sem o roteiro antes").

**Conteúdo** (`montarAreaImpressaoCartaoMesa()`, linha 6137-6147): cabeçalho "Cartão de Mesa" com subtítulo "Kit de Incidentes — Ferramentas Coger · Oitiva 360"; em seguida uma grade de duas colunas (`cartao-mesa-grid`, `column-count:2`, fonte 8.5pt para impressão compacta) com um bloco por item do Kit de Incidentes filtrado por `inc.cartaoMesa` (todos os 17 itens atuais têm essa flag `true`) — cada bloco mostra a `situacao` em negrito e a `formulaVerbal` completa. Ou seja: o Cartão de Mesa **não é um resumo do ato/depoente** (não traz dados do processo, do depoente ou do roteiro) — é o Kit de Incidentes inteiro, compactado em duas colunas para caber numa folha de consulta rápida.

**Indicação de uso, no próprio código:** o rodapé de impressão (`htmlRodapeImpressao`) recebe o texto **"Uso interno · Consulta rápida durante o ato"** (linha 6145) — confirma que o cartão se destina a ser impresso antes e consultado **durante** a sessão (na mesa da comissão), não como registro/anexo do processo.

---

## 9. Transição de status de item de pauta importada (pendente → em_andamento → concluída)

Aplica-se apenas quando há uma pauta do Nexo Coger importada (`estado.pautaImportada`) — fora do escopo do fluxo manual sem pauta, mas documentado aqui à parte. O status de cada item de pauta **não é um campo armazenado com essas 3 palavras** — é computado ao vivo por `statusPautaItemRodada8(item, depoentes)` (linha 4106, comentário explícito nas linhas 4103-4105):

```js
function statusPautaItemRodada8(item, depoentes){
  if (item.statusChecklist === "abordado" || item.statusChecklist === "sem_resposta") return "concluida";
  const selecionadoPorAlguem = (depoentes || []).some(d => (d.pautaSelecionada || []).includes(item.fatoId));
  return selecionadoPorAlguem ? "em_andamento" : "pendente";
}
```

Ou seja, apenas `item.statusChecklist` é persistido (valores `"pendente"` | `"abordado"` | `"sem_resposta"`); os rótulos "pendente"/"em_andamento"/"concluida" usados na UI (badge de contagem no cabeçalho, `badgePautaPendente`) são derivados na hora da renderização, não gravados como tal.

**Gatilhos exatos de cada transição:**

1. **`pendente`** — estado inicial de todo item ao importar a pauta (`mesclarPautaImportada`, linha 4061-4063: `statusChecklist` novo começa como `"pendente"`) **e** enquanto nenhum depoente tiver esse item em `d.pautaSelecionada`. Ou seja, importar a pauta por si só não muda nada além de criar os itens com `statusChecklist: "pendente"` — a mudança de rótulo para "em_andamento" não depende de reimportação.
2. **`em_andamento`** — assim que **qualquer** depoente cadastrado passa a ter o `fatoId` do item dentro de `d.pautaSelecionada` (isto é: o usuário, na Etapa 2 do wizard daquele depoente, marca o item da "Pauta do Nexo" como algo a abordar nesta oitiva — ação de seleção, fora do escopo do fluxo manual sem pauta e não detalhada nesta auditoria porque o cartão `cartao-pauta-nexo` só existe com pauta importada). Continua "em_andamento" enquanto `statusChecklist` permanecer `"pendente"`.
3. **`concluida`** — só é atingido quando `item.statusChecklist` vira `"abordado"` ou `"sem_resposta"`, o que só acontece em `atualizarChecklistPautaAoConcluir(d)` (linha 4243), chamada **exclusivamente** pelo handler do checkbox **"Marcar oitiva como realizada"** (`chk-oitiva-realizada`, Etapa 4, linha 5702-5712) — nunca antes, nunca automaticamente. Ao marcar esse checkbox: `d.status` do depoente vira `"oitiva_realizada"` e, para cada item em `d.pautaSelecionada`, verifica `d.pautaConclusao[fatoId].respondida`: se `false`, `item.statusChecklist = "sem_resposta"` (com `notaSemResposta` opcional); caso contrário (padrão `respondida: true`), `item.statusChecklist = "abordado"`. Desmarcar o checkbox reverte apenas `d.status` do depoente para `"roteiro_pronto"` — **não** reverte `statusChecklist` do item de pauta (comentário no código confirma: só ao concluir a oitiva o statusChecklist é atualizado, "nunca antes, nunca calculado sozinho" — mas o código não mostra reversão automática ao desmarcar).

Resumo direto: **importar pauta = pendente**; **algum depoente selecionar o item para abordar nesta sessão = em_andamento**; **marcar a checkbox "Marcar oitiva como realizada" na Etapa 4 daquele depoente = concluída** (como "abordado" ou "sem_resposta", conforme a resposta ter sido de fato registrada).

---

## 10. Correção — pauta_id/rodada_id/id_ponto ausentes em "Exportar prova(s) para o Nexo" (rodada 2026-07-12)

Fecha o gap descrito no Adendo §6.4 de `audit-nexo-coger.md`: o handler de `#btn-confirmar-exportar-prova` (linha ~5986, dentro do listener `click`) agora inclui, por item de prova, os mesmos três campos que `construirEnvelopeRetorno()` já emitia desde a Rodada 6 (linha 5488-5512) — lidos exatamente da mesma fonte.

**Vínculo prova → ponto de pauta**: cada chave de `_exportProvaDraft` é um `fatoId` que só existe porque veio de `itensPautaAbordadosNestaSessao(d)` (linha 4270), que por sua vez filtra `estado.pautaImportada.itens` pelos `fatoId` em `d.pautaSelecionada` com `statusChecklist==='abordado'` (linha 4262-4267, `itensPautaAbordadosPuro`). Ou seja: todo item que chega ao diálogo "Exportar prova(s) para o Nexo" já tem, por construção, um item correspondente em `estado.pautaImportada.itens` — o mesmo array de onde `construirEnvelopeRetorno` lê `item.pautaIdOrigem`/`item.idPontoOrigem` (linhas 5495 e 5497).

No handler corrigido, cada prova agora faz esse mesmo lookup por `fatoId` antes de montar o objeto exportado:

```js
if (!d.rodadaId) d.rodadaId = gerarId();
salvarLocalStorage();
...
const itemPauta = estado.pautaImportada && estado.pautaImportada.itens.find(i => i.fatoId === fatoId);
return {
  fatoIds: [fatoId],
  ...
  pauta_id: (itemPauta && itemPauta.pautaIdOrigem) || null,
  rodada_id: itemPauta ? (d.rodadaId || null) : null,
  id_ponto: (itemPauta && itemPauta.idPontoOrigem) || null,
  ...
};
```

`d.rodadaId` é o mesmo id de rodada reaproveitado por `exportarTermoParaVeritas`/`exportarRetornoContextoAcusado` (gerado uma vez por depoente, com `gerarId()`, se ainda não existir) — os dois contratos (retorno de contexto e prova nova) agora apontam para a mesma sessão de oitiva quando emitidos pelo mesmo depoente.

**Caso sem origem de pauta**: como este diálogo só é populado a partir de itens de pauta (não existe, no Oitiva 360, um fluxo de "prova avulsa sem pauta" alimentando `_exportProvaDraft`), o `itemPauta` só fica `null`/`undefined` num cenário defensivo — item de pauta removido/inacessível entre abrir o diálogo e confirmar a exportação. Nesse caso os três campos saem `null` explicitamente (`(itemPauta && itemPauta.pautaIdOrigem) || null` — nunca um valor inventado), confirmado por teste automatizado (ver seção de teste abaixo): ao simular um `fatoId` inexistente em `estado.pautaImportada.itens`, a mesma expressão de lookup devolveu `pauta_id === null`, `rodada_id === null`, `id_ponto === null`.

**Teste end-to-end** (Playwright, Chromium headless): gerado um contrato de pauta real no Nexo Coger (`construirContratoPauta`, a partir de um fato com lacuna de prova via `analisarLacunasPauta`), importado no Oitiva 360 via `mesclarPautaImportada`, depoente marcado com o item "abordado", e o botão real `#btn-confirmar-exportar-prova` clicado (handler de produção, não uma cópia da lógica) — o download capturado trouxe `pauta_id`/`id_ponto` idênticos aos gerados pelo Nexo e um `rodada_id` não vazio. O arquivo foi então importado de volta no Nexo Coger via `revisarImportacaoProva`/clique real em "Importar selecionadas", e `doc.provas[].origemOitiva` resultou com os três campos preenchidos e batendo com os valores originais.

Dois hooks de teste mínimos foram adicionados perto de `window.getEstado`/`window.setEstadoPautaImportada` (mesmo padrão já existente desde a Rodada 7, seção 7.1) para tornar esse fluxo testável de fora do IIFE de topo do arquivo: `window.setDepoenteAtivoIdParaTeste` e `window.abrirDialogoExportarProvaParaTeste`. Nenhum dos dois altera comportamento em produção — são só portas de entrada para o script de teste.
