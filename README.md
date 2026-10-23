# Suíte Nexo — Verificação de Nexo Fático-Probatório (Coger/RFB)

Duas ferramentas irmãs de apoio à decisão, mesma arquitetura e mesmo motor,
para domínios de responsabilização diferentes:

Arquivo | Ferramenta | Domínio
---|---|---
`nexo-coger.html` | **Nexo Coger** | PAD e sindicância acusatória de **servidores** (Lei nº 8.112/90)
`nexo-par.html` | **Nexo PAR** | Processo Administrativo de Responsabilização de **entes privados** (Lei nº 12.846/2013 — LAC)

Ambas constroem o **mapa visual Fato → Prova → Norma**, revelam lacunas de
instrução em tempo real e geram os documentos de indiciação/notificação do
respectivo rito. Fazem parte do ecossistema digital da Corregedoria
(Suíte Coger), com integrações opcionais com o **Oitiva 360** e o **Veritas**.

## Uso

Abra **`nexo-coger.html`** ou **`nexo-par.html`** por duplo clique em qualquer
navegador (Chrome/Edge). Não requer instalação, servidor ou conexão de rede.
Cada arquivo é 100% independente e mantém seu próprio rascunho no navegador —
abrir um não interfere no outro.

Ao abrir, aparece a **tela inicial** (processo salvo neste navegador, ou
"novo processo" / "importar processo .json"); em seguida o **gate de dados do
processo**, que bloqueia o restante do app até nº do processo, tipo, comissão
etc. estarem preenchidos. Esse fluxo é padronizado com o Veritas.

Para conhecer a ferramenta, use **exportar ▾ → 🧪 Carregar exemplo** em cada
arquivo: cada um carrega um cenário completo (acusado/ente, fatos, provas e
enquadramentos) já pronto para demonstrar o mapa e o motor de pendências.

## Características compartilhadas

- **Arquivo único, 100% offline.** CSS, JS, catálogo de normas e ícones estão
  todos embutidos em cada arquivo. Nenhuma requisição de rede é feita —
  nenhum dado sai do navegador.
- **Identidade visual do ecossistema (coger-ui.css oficial).** Design system
  Cogerui v1.0 — fontes Barlow Condensed / Inter / JetBrains Mono (base64) e
  tokens `--rfb-*` — embutido; os componentes consomem esses tokens via
  aliases, preservando apenas os matizes de categoria (Fato/Prova/Norma).
- **Mapa em SVG** de três colunas (Fatos, Provas, Normas) com estados visuais
  em dois canais (matiz = categoria; forma/cor = criticidade), acessível e
  imprimível.
- **Motor de pendências** recalculado a cada mutação, com painel clicável e
  checklist de encerramento — o conjunto de códigos (P1–P8 no Nexo Coger)
  é adaptado por domínio; ver diferenças do Nexo PAR abaixo.
- **Wizard de multiplicidade** (concurso formal × conflito aparente:
  consunção, subsidiariedade, especialidade, alternatividade).
- **Fato ativo × arquivado**: a comissão pode arquivar um fato apurado que
  decidiu não indiciar, com justificativa obrigatória. O fato arquivado não
  gera pendência, não entra no documento final nem na pauta, e permanece no
  mapa esmaecido como memória da decisão.
- **Ordem narrativa dos fatos**: campo `ordem` editável por arrasto no
  painel, usado apenas na sequência do documento final (não afeta o mapa).
- **Caixa de prescrição** e **trilha de prazos** processuais, com pendência de
  antecedência mínima de intimação (art. 41, Lei nº 9.784/99). Seções
  colapsadas no painel; informativas, não bloqueiam a geração do documento.
- **Documento de indiciação/notificação em modelo oficial** — um documento
  **completo e independente por acusado/ente** (Nexo Coger: "Indiciação";
  Nexo PAR: "Nota de Indiciação"), com qualificação, fatos/condutas, provas,
  enquadramento, tabela-síntese "Fatos × Provas × Enquadramentos" (agrupada
  por fato), seção "Das alegações da defesa não acatadas" (editável) e bloco
  de assinatura em 3 colunas — Vogal / Presidente / Vogal, rótulo "Assinatura
  digital". Data de assinatura editável no momento da geração. Com 2+
  indiciados/entes selecionados, uma tela intermediária "Termos gerados"
  permite abrir cada documento individualmente.
- **Termos de intimação/notificação**: esclarecimento de fato, manifestação
  sobre prova (contraditório) ou interrogatório, um documento por
  destinatário. Fundamentação legal e blocos de texto variam conforme a
  situação do destinatário e, no interrogatório, o momento (prévio/final).
  Numeração manual e prazo de resposta editáveis. Mesmo bloco de assinatura
  em 3 colunas do documento de indiciação.
- **Persistência**: rascunho automático em `localStorage` (chaves
  `nexo-coger:draft` e `nexo-par:draft`, independentes) e export/import de
  `.json` como guarda oficial.

> O rascunho no navegador é volátil. Exporte o `.json` para guarda oficial.

## Nexo Coger — específico

Fundamentação: Manual de PAD CGU 2025 (cap. 10), Lei nº 8.112/90 (arts. 155 e
161) e Portaria Normativa CGU nº 27/2022 (arts. 119–121 e 127).

- **Catálogo de fábrica com 52 normas**: arts. 116, 117, 130 §1º e 132 da Lei
  nº 8.112/90 e art. 32 da LAI, com relações de conflito aparente espelhadas
  nos dois sentidos. Normas residuais podem ser criadas (prefixo `NU-`).
- **Dados complementares do acusado** (situação funcional, telefone(s),
  e-mail(s)) e **cidade do processo**, usados no cabeçalho dos documentos.
- **Motor de pendências P1–P8**, incluindo P6c (intimação do interrogatório
  com menos de 3 dias úteis).

## Nexo PAR — específico

Fundamentação: Lei nº 12.846/2013 (Lei Anticorrupção — LAC) e IN CGU nº
13/2019. Adapta o mesmo motor à **responsabilidade objetiva** de entes
privados — sem dolo/culpa, sem gravidade/pena da Lei nº 8.112/90.

- **"Acusado" = ente privado**: razão social, nome fantasia, CNPJ, endereço,
  faturamento bruto, representante(s) legal(is) (com CPF e vínculo), além dos
  campos de **solidariedade**, **sucessão empresarial** e **desconsideração
  da personalidade jurídica** (art. 4º e 14 da LAC).
- **Catálogo dedicado** com as normas do art. 5º da Lei nº 12.846/2013,
  agrupadas em "Atos de corrupção em geral" e "Licitações e contratos".
  Gravidade/pena/elemento subjetivo não existem na LAC e ficam neutros.
- **Pendência P-ENTE**: processo sem ente cadastrado, ou ente sem
  representante legal — crítica, bloqueia a geração da Nota de Indiciação.
- **Pendência P8-PAR** (substitui o P8 do Nexo Coger, que pressupõe
  dolo/culpa): fato com enquadramento LAC sem descrição do
  interesse/benefício da pessoa jurídica ou do nexo causal.
- **Nota de Indiciação**: mesmo modelo de documento por acusado, nomeado
  conforme o rito PAR. Defesa escrita em 30 dias a contar da intimação
  (art. 17, IN CGU nº 13/2019).

## Exportações

- **Documento `.json`** completo (guarda e troca no ecossistema Coger).
- **Indiciação / Nota de Indiciação** — um documento por acusado/ente, em
  vista de impressão/PDF.
- **Termos de intimação/notificação** — um documento por destinatário.
- **Pauta de instrução por depoente** para o Oitiva 360 (fatos carentes de
  prova) — enriquecida com contexto dos acusados/entes e enquadramentos
  ativos por fato.
- **Impressão do mapa** em paisagem, com legenda dos estados.

## Integração com o ecossistema Coger (aditiva e opcional)

Preparação do lado do Nexo; nenhuma dependência de Oitiva 360 ou Veritas
existirem. Tudo é opcional — cada ferramenta funciona de forma idêntica para
quem não usa.

- **Importar prova(s) de retorno**: aceita um `.json` de qualquer origem que
  siga o contrato genérico (formato interno de `provas[]` + `fatoIds`).
  Validação antes de aplicar e **tela de revisão obrigatória** com preview e
  seleção por item — nada entra silenciosamente.
- **Importar provas do Veritas**: contrato por catálogo canônico (tipo de
  prova como id do catálogo, ex. `PROVA.PRINT_SISTEMA`), resolvido para o
  tipo interno correspondente e exibido com o rótulo em português do
  catálogo.
- **Importar retorno do Oitiva 360 — contexto do acusado**: populariza
  `provasContexto[]` do acusado/ente com material informativo do depoimento.
  Deliberadamente isolado — não afeta pendências, força probatória ou a
  indiciação.
- **Badge "pauta enviada"**: rastro neutro no card do fato após exportar a
  pauta; some sozinho quando o fato recebe prova e deixa de carecer de
  evidência.

## Manutenção

O JavaScript de cada ferramenta está embutido no próprio arquivo (um bloco
`<script>` ao final), conforme o requisito de arquivo único. `nexo-coger.html`
e `nexo-par.html` são independentes — não compartilham módulo — então uma
mudança no motor comum (mapa, pendências, catálogo, exportações) precisa ser
replicada manualmente nos dois arquivos quando aplicável a ambos.
