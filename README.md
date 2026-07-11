# NEXUS — Sistema de Verificação de Nexo Fático-Probatório

Ferramenta de apoio à decisão para comissões de PAD e sindicância acusatória da
Corregedoria da Receita Federal do Brasil (Coger/RFB). Constrói o **mapa visual
Fato → Prova → Norma**, revela lacunas de instrução em tempo real e gera a
**minuta do termo de indiciação** (um capítulo por acusado) e a **pauta de
retroalimentação** para o Oitiva 360.

Fundamentação: Manual de PAD CGU 2025 (cap. 10), Lei nº 8.112/90 (arts. 155 e
161) e Portaria Normativa CGU nº 27/2022 (arts. 119–121 e 127).

## Uso

Abra **`nexus.html`** por duplo clique em qualquer navegador (Chrome/Edge). Não
requer instalação, servidor ou conexão de rede.

Para conhecer a ferramenta, use **exportar ▾ → 🧪 Carregar exemplo**: um cenário
com 2 acusados e 4 fatos que demonstra as pendências P1, P3, P4, P5, P6a e P8.

## Características

- **Arquivo único, 100% offline.** CSS, JS, catálogo de normas e ícones estão
  todos embutidos. Nenhuma requisição de rede é feita — nenhum dado sai do
  navegador.
- **Identidade visual do ecossistema (coger-ui.css oficial).** O design system
  Cogerui v1.0 — fontes Barlow Condensed / Inter / JetBrains Mono (base64) e os
  tokens `--rfb-*` — está embutido; os componentes do Nexo consomem esses tokens
  via aliases, preservando apenas os matizes de categoria (Fato/Prova/Norma).
- **Mapa em SVG** de três colunas (Fatos, Provas, Normas) com estados visuais
  em dois canais (matiz = categoria; forma/cor = criticidade), acessível e
  imprimível.
- **Motor de pendências (P1–P8)** recalculado a cada mutação, com painel
  clicável e checklist de encerramento.
- **Catálogo de fábrica com 52 normas**: arts. 116, 117, 130 §1º e 132 da Lei
  nº 8.112/90 e art. 32 da LAI, com relações de conflito aparente espelhadas nos
  dois sentidos. Normas residuais podem ser criadas (prefixo `NU-`).
- **Wizard de multiplicidade** (concurso formal × conflito aparente: consunção,
  subsidiariedade, especialidade, alternatividade).
- **Fato ativo × arquivado**: a comissão pode arquivar um fato apurado que
  decidiu não indiciar (p. ex. princípio da insignificância, ou fato não
  confirmado contra aquele acusado), com justificativa obrigatória. O fato
  arquivado não gera pendência, não entra na minuta nem na pauta, e permanece
  no mapa esmaecido como memória da decisão.
- **Ordem narrativa dos fatos**: campo `ordem` editável por arrasto no painel,
  usado apenas na sequência da minuta (não afeta o mapa).
- **Caixa de prescrição** (art. 142): cálculo informativo por acusado
  (gravidade → prazo, termo inicial pela ciência da autoridade, interrupção
  pela portaria de instauração, hipóteses do art. 127 da PN CGU 27/2022).
  Elemento discreto ao lado do nº do processo — só ganha cor em alerta real;
  popover com o detalhamento por acusado. Nunca projeta contagem pós-instauração.
- **Trilha de prazos**: prazo de conclusão (art. 152) com prorrogações, prazo de
  citação/defesa escrita (art. 161, §§1º-2º) e pendência **P6c** (intimação do
  interrogatório com menos de 3 dias úteis — art. 41, Lei 9.784/99). Seção
  "Prazos" colapsada no painel; informativa, não bloqueia a minuta.
- **Índice de provas na minuta**: numeração automática das provas por capítulo,
  citações prefixadas no texto e tabela "Índice de Provas Citadas" (campo
  opcional `codigoAnexo` por prova).
- **Persistência**: rascunho automático em `localStorage` (chave
  `nexus-coger:draft`) e export/import de `.json` como guarda oficial.

> O rascunho no navegador é volátil. Exporte o `.json` para guarda oficial.

## Exportações

- **Documento `.json`** completo (guarda e troca no ecossistema Coger).
- **Minuta do termo de indiciação** — por acusado, em vista de impressão/PDF.
- **Pauta de instrução** para o Oitiva 360 (fatos carentes de prova) — enriquecida
  com contexto dos acusados e enquadramentos ativos por fato (`catalogoVersion`,
  `acusadosContexto`, `acusadosVinculados`, `enquadramentosAtivos`).
- **Impressão do mapa** em paisagem, com legenda dos estados.

## Integração com o Oitiva 360 (aditiva e opcional)

Preparação do lado do Nexo; nenhuma dependência do Oitiva existir. Tudo é
opcional — a ferramenta funciona de forma idêntica para quem não usa.

- **Importar prova(s) de retorno**: aceita um `.json` de qualquer origem que siga
  o contrato (cada item = formato interno de `provas[]` + `fatoIds`). Validação
  antes de aplicar (tipo válido, fatos existentes, aviso de processo divergente)
  e **tela de revisão obrigatória** com preview e seleção por item — nada entra
  silenciosamente. Sem deduplicação automática nesta versão.
- **Badge "pauta enviada"**: rastro neutro no card do fato após exportar a pauta;
  some sozinho quando o fato recebe prova e deixa de carecer de evidência.

## Manutenção

O JavaScript está embutido em `nexus.html` (um bloco `<script>` ao final do
arquivo), conforme o requisito de arquivo único. Edite-o diretamente ali.
