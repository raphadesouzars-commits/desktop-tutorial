# Especificação Visual — PROVISÓRIA

> ⚠️ **Este documento é um rascunho provisório**, baseado em convenções comuns
> de provas de vestibular brasileiras (ENEM/PROSEF/Bahiana em geral) — **não**
> foi extraído da inspeção de PDFs de referência reais, porque nenhum PDF
> escaneado foi fornecido ainda em `referencia/`.
>
> Segundo o `CLAUDE.md`, este passo **nunca deveria ser pulado**. Assim que
> houver pelo menos um PDF real em `referencia/`, siga o Passo 0:
>
> ```
> pdftoppm -png -r 150 -f <pagina_inicial> -l <pagina_final> referencia/<arquivo>.pdf referencia/pagina
> ```
>
> Visualize as páginas geradas e **substitua cada item abaixo** pelo que for
> observado de fato. Até lá, o template em `template/` implementa exatamente
> o que está descrito aqui — e só aqui — e deve ser tratado como um "melhor
> palpite" temporário, não como padrão definitivo.

---

## Página

- Tamanho: A4 (21 x 29,7 cm), retrato.
- Margens: 2,0 cm superior/inferior, 1,8 cm laterais.

## Colunas

- 2 colunas por página, largura igual, com 0,8 cm de espaçamento (gutter) entre elas.
- Quebra de **coluna**, não de página, sempre que uma questão couber inteira na coluna seguinte sem cortar o texto-suporte no meio.

## Fonte

- Serifada (ex.: Georgia / Times New Roman) para corpo de texto e enunciados — leitura de prova impressa tradicionalmente usa serifada.
- Corpo de texto (resumo, texto-suporte): 10pt, entrelinha 1.3.
- Comando da questão: 10pt, negrito.
- Alternativas: 10pt, regular.

## Cabeçalho institucional

- Repete em todas as páginas.
- Caixa no topo com nome do processo seletivo/instituição centralizado, borda inferior simples separando do corpo.
- Logo (se houver) alinhado à esquerda da caixa de cabeçalho.

## Número da questão

- Caixa arredondada com fundo sólido (cor de destaque) contendo "QUESTÃO" + número, alinhada ao início do bloco da questão.

## Alternativas

- Lista vertical, uma por linha, com recuo de 0,4 cm em relação à margem do texto do comando.
- Espaçamento de 0,15 cm entre alternativas.
- Prefixo "A)" a "E)" em negrito, seguido do texto da alternativa.

## Referência da fonte do texto-suporte

- Fonte em itálico, tamanho reduzido (8pt), alinhada à direita logo abaixo do texto-suporte.

## Rodapé

- Numeração de página centralizada.
- Nome da instituição/prova à esquerda ou direita do número de página, fonte reduzida (8pt).

## Figuras/imagens no texto-suporte

- Centralizadas na largura da coluna, com legenda em itálico abaixo (8pt), sem sangrar para a outra coluna.

---

## Gabarito e justificativas

- Tabela simples "Questão | Alternativa Correta" no início da seção.
- Justificativa por alternativa (A a E) para cada questão, em corpo de texto normal, mesma largura de coluna do restante do documento.
