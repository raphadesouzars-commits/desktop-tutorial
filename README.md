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
- **Persistência**: rascunho automático em `localStorage` (chave
  `nexus-coger:draft`) e export/import de `.json` como guarda oficial.

> O rascunho no navegador é volátil. Exporte o `.json` para guarda oficial.

## Exportações

- **Documento `.json`** completo (guarda e troca no ecossistema Coger).
- **Minuta do termo de indiciação** — por acusado, em vista de impressão/PDF.
- **Pauta de instrução** para o Oitiva 360 (fatos carentes de prova).
- **Impressão do mapa** em paisagem, com legenda dos estados.

## Manutenção

O JavaScript está embutido em `nexus.html` (um bloco `<script>` ao final do
arquivo), conforme o requisito de arquivo único. Edite-o diretamente ali.
