# Projeto: Geração de PDFs de Simulados — Padrão Visual Bahiana/PROSEF

## Objetivo

Converter arquivos Markdown de questões objetivas (resumo didático + questões + gabarito explicativo, gerados no projeto Claude "Bahiana") em documentos **PDF com o mesmo padrão visual das provas oficiais** Bahiana/PROSEF, para envio aos filhos como material de estudo.

Este não é um projeto de geração de conteúdo — o conteúdo já vem pronto do `.md`. O trabalho aqui é **diagramação fiel**.

---

## Estrutura do projeto

```
projeto-provas/
├── CLAUDE.md                        ← este arquivo
├── referencia/                      ← PDFs escaneados das provas antigas (Bahiana/PROSEF), usados só como referência visual
├── template/
│   ├── especificacao_visual.md      ← especificação extraída das provas antigas (fonte, margens, cores, layout)
│   ├── prova.html                   ← template HTML da prova
│   └── estilo.css                   ← estilos (fonte, colunas, cabeçalho, alternativas, rodapé)
├── questoes-md/                     ← arquivos .md de entrada (colados do projeto Claude "Bahiana")
├── scripts/
│   └── gerar_pdf.py                 ← script de conversão .md → PDF
└── output/                          ← PDFs finais gerados
```

---

## Passo 0 — Especificação visual (executar uma vez, no início do projeto)

Os arquivos em `referencia/` são PDFs cujas páginas são imagens escaneadas (não têm texto selecionável). Para extrair o padrão visual real:

1. Converter 3-4 páginas de exemplo em PNG de alta resolução:
   ```
   pdftoppm -png -r 150 -f <pagina_inicial> -l <pagina_final> referencia/<arquivo>.pdf referencia/pagina
   ```
2. Visualizar as imagens geradas e documentar em `template/especificacao_visual.md`:
   - Tamanho de página e margens (A4, margens aproximadas em cm).
   - Layout: quantas colunas por página, largura de cada coluna, espaçamento entre elas.
   - Fonte: serifada ou não serifada, tamanho aproximado do corpo de texto, do comando da questão e das alternativas.
   - Cabeçalho institucional: posição do logo, caixa com nome do processo seletivo, se repete em todas as páginas.
   - Formatação do número da questão (ex.: caixa arredondada com "QUESTÃO" + número).
   - Formatação das alternativas (A) a E), em lista vertical, recuo, espaçamento entre elas).
   - Formatação da referência de fonte do texto-suporte (tamanho menor, itálico ou não).
   - Rodapé: numeração de página, nome da instituição/prova.
   - Uso de imagens/figuras dentro do texto-suporte (como ficam posicionadas na coluna).

3. Esta especificação deve ser tratada como **fonte de verdade** para o template — não usar suposições genéricas de "prova de vestibular", usar exatamente o que está documentado aqui, extraído da inspeção real das imagens.

**Nunca pular este passo ao iniciar o projeto ou ao adicionar uma nova referência visual.**

---

## Passo 1 — Template (HTML + CSS)

- `template/prova.html`: estrutura semântica da prova (cabeçalho, corpo em colunas, bloco de questão, bloco de gabarito).
- `template/estilo.css`: toda a formatação visual, com **variáveis CSS** no topo do arquivo para fonte, tamanhos, cores e margens, de modo que ajustes finos não exijam reescrever o CSS inteiro.
- O layout deve reproduzir fielmente a `especificacao_visual.md`, incluindo o comportamento de colunas (quebra de coluna, não de página, quando o conteúdo permite).
- Gerar o PDF a partir do HTML via **weasyprint** (preferencial, mais previsível para impressão) ou Playwright/Chromium headless como alternativa.

---

## Passo 2 — Formato de entrada esperado (.md)

Os arquivos em `questoes-md/` seguem sempre esta estrutura, já produzida no projeto Claude "Bahiana" segundo o `GUIA_MESTRE_QUESTOES_OBJETIVAS_EBMSP.md`:

1. **Resumo didático** do tema (texto corrido, tabelas, listas).
2. **Questões objetivas** — cada uma com: número, texto-suporte (estímulo), referência da fonte, comando, cinco alternativas `A)` a `E)`.
3. **Gabarito e justificativas** — tabela `Questão | Alternativa Correta` seguida de justificativa por alternativa.

**Regra importante:** o script de conversão nunca deve alterar, resumir ou reescrever o conteúdo do `.md` — apenas diagramar. Se o Markdown de entrada estiver com formatação inconsistente (ex.: alternativas sem `A)` `B)` etc.), sinalizar o problema em vez de tentar adivinhar a estrutura.

---

## Passo 3 — Script de conversão

`scripts/gerar_pdf.py` deve:
- Ler um arquivo `.md` de `questoes-md/`.
- Fazer o parsing das três seções (resumo, questões, gabarito) de forma robusta a pequenas variações de formatação.
- Popular o template HTML.
- Exportar o PDF para `output/` com o nome `[tema-em-slug]_[AAAA-MM-DD].pdf`.
- Opcionalmente, gerar **duas versões**: uma só com resumo + questões (para os filhos responderem primeiro) e outra completa com gabarito (para conferência depois) — perguntar ao usuário se quer essa separação antes de implementar.

Uso esperado:
```
python scripts/gerar_pdf.py questoes-md/absorcao_intestinal.md
```

---

## Passo 4 — Validação visual (rodar sempre que o template for alterado)

1. Gerar um PDF de teste com um `.md` de exemplo.
2. Converter a primeira página do PDF gerado e a primeira página de um PDF de `referencia/` em imagem PNG (mesma resolução).
3. Visualizar as duas lado a lado e comparar: proporção de colunas, tamanho de fonte, espaçamento, posição do cabeçalho.
4. Ajustar `estilo.css` até a equivalência visual ser satisfatória.
5. Só então considerar o template "fechado" para uso corrente.

Repetir esse loop de comparação sempre que houver mudança relevante no template — não confiar apenas na leitura do CSS.

---

## Convenções gerais

- Nunca modificar os arquivos em `referencia/` — são fonte de consulta, somente leitura.
- Nunca modificar o conteúdo textual/pedagógico dos arquivos em `questoes-md/` — esse conteúdo já foi validado no projeto Claude "Bahiana" contra o guia de padrão da banca.
- Cada alteração no template deve ser testada com pelo menos um `.md` real antes de ser considerada concluída.
- Se um `.md` novo tiver uma estrutura visivelmente diferente da esperada (ex.: tabelas extras, questões com imagem), avisar antes de tentar adaptar o template automaticamente.
