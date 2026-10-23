# Especificação Visual — Padrão Bahiana/PROSEF

> Extraída por inspeção visual real das provas em `referencia/`:
> - `BAHIANA_MED_2021.1_TIPO1.pdf` (Medicina, PROSEF 2021.1)
> - `BAHIANA_MED_2021.2.pdf` (Medicina, PROSEF 2021.2)
> - `BAHIANA_AREA_DE_SAUDE_PROVA_2021_2.pdf` (Área de Saúde, PROSEF 2021.2)
>
> Páginas inspecionadas: capa, folha de instruções e páginas de conteúdo
> (questões 1 a 11) das três provas, via
> `pdftoppm -png -r 150 ...` + leitura visual das imagens.
>
> Este documento substitui a versão provisória anterior. Qualquer item aqui
> descrito tem prioridade sobre suposições genéricas de "prova de
> vestibular" — é o que foi de fato observado nos PDFs de referência.

---

## Página

- A4, retrato.
- Margens laterais e inferior generosas (~1,8 cm). Margem superior menor
  (~1,2 cm) até o filete duplo que marca o topo da área útil.
- **Escala de cinza**: as três provas não usam nenhuma cor de destaque
  (nada de vermelho/bordô) — tudo em preto, branco e tons de cinza. Isso é
  consistente nas três referências e muda a suposição provisória anterior
  (que usava um tom bordô como `--cor-destaque`).

## Cabeçalho — só na primeira página de cada prova/seção

Diferente da suposição provisória, o cabeçalho institucional **não se
repete em todas as páginas**. Ele aparece apenas uma vez, no topo da
primeira página de conteúdo da seção de questões, como conteúdo normal do
fluxo (não como running header):

1. Marca/nome da instituição (brasão + "BAHIANA" + "ESCOLA DE MEDICINA E
   SAÚDE PÚBLICA" em caixa alta, menor, logo abaixo). *Não temos o arquivo
   de imagem do brasão — reproduzimos apenas o texto da marca; se o brasão
   for fornecido como imagem, incluir no cabeçalho.*
2. Barra cinza-médio com texto em negrito e um "➔" antes do texto, ex.:
   "➔ Prova Objetiva – Questões de 1 a 35".
3. Barra cinza-claro logo abaixo, com um ícone "↺" e o subtítulo/tema da
   prova, ex.: "↺ Questões Objetivas de Conhecimentos Gerais Contemporâneos".
4. Barra de instrução: uma etiqeta preta arredondada "Instrução" (com uma
   pequena seta apontando para a direita) seguida de uma caixa com borda
   contendo o texto da instrução.

Nas páginas seguintes da mesma seção **não há nada disso** — a página
começa direto com o conteúdo (grupo de questões, texto-suporte, etc.).

## Running header (todas as páginas)

O único elemento que de fato se repete em todas as páginas é um **filete
duplo** (duas linhas horizontais finas, ~1 mm de distância entre si) no
topo da área útil da página, sem nenhum texto.

## Rodapé (todas as páginas)

Uma linha só, com três zonas:
- Esquerda: marca da editora/gráfica que imprimiu a prova (nas referências,
  "Strix educação") — **não reproduzir**, é marca de terceiro sem relação
  com o nosso material.
- Centro: identificação da prova, ex.: "▶ BAHIANA – MEDICINA – PROSEF
  2021.1 – PROVA DE CONHECIMENTOS GERAIS CONTEMPORÂNEOS".
- Direita: número da página.

Nas referências essa disposição alterna de lado em páginas pares/ímpares
(espelhamento típico de miolo de livro). Para o nosso uso (PDF avulso, não
encadernado) não replicamos o espelhamento — mantemos sempre a mesma
posição em todas as páginas.

## Colunas

- **Resumo: 1 coluna, largura cheia da página.** As provas oficiais não têm
  seção de resumo (é uma adição nossa, fora do padrão da banca), e o resumo
  costuma trazer tabelas largas (ex.: comparando vários nutrientes lado a
  lado) que não cabem numa coluna estreita sem quebrar/transbordar texto.
  Decisão de projeto: o bloco de **resumo inteiro roda em 1 coluna só**,
  ocupando toda a largura útil da página; só **questões e gabarito** entram
  no layout de 2 colunas abaixo.
  (Nota técnica: `column-span: all` do CSS, que permitiria uma tabela larga
  "furar" um layout de 2 colunas, não funciona corretamente no WeasyPrint
  nesta versão — a tabela some ou fica cortada entre as colunas. Por isso a
  solução foi manter o resumo inteiro fora do container de colunas, e não
  tentar fazer só a tabela "furar" as colunas.)
- **Questões e gabarito: 2 colunas**, separadas por um **filete vertical
  único** (linha fina) no meio, não apenas espaço em branco.
- Gutter (espaço entre coluna e o filete) pequeno, ~0,4–0,6 cm de cada lado.
- Quando um texto-suporte é compartilhado por duas ou mais questões (ex.:
  "Questões 6 e 7", "Questões 9 e 10"), ele é diagramado **acima das
  colunas**, ocupando a largura cheia da página, com um rótulo em negrito
  antes ("Questões 6 e 7"); só depois o conteúdo entra em 2 colunas com uma
  questão por coluna.
- Quando o texto-suporte pertence a uma única questão, ele fica dentro da
  própria coluna, na mesma largura da coluna.

## Fontes

- **Texto-suporte (estímulo)**: fonte serifada, justificada, recuo de
  parágrafo na primeira linha (~1,2 cm). É serifada tanto quando ocupa a
  largura cheia da página quanto quando está dentro de uma coluna.
- **Comando da questão e alternativas**: fonte **sem serifa**, justificada
  no comando; alternativas com recuo suspenso (texto que quebra linha
  alinha com o início do texto da alternativa, não com a letra).
- **Referência da fonte do texto-suporte**: sem serifa, tamanho reduzido,
  **texto normal (não itálico)**, alinhada à esquerda, logo abaixo do
  texto-suporte — ex.: "ALVES, Rubem. A Escutatória. Disponível em:
  <...>. Acesso em: jan. 2021.".
- **Rótulo de grupo de questões** ("Questões 6 e 7"): sem serifa, negrito,
  um pouco maior que o corpo.

## Número da questão

Não é uma caixa simples — é um selo composto:
- Um retângulo de cantos arredondados à esquerda, fundo cinza-escuro/preto
  em gradiente, com o texto "QUESTÃO" em branco, maiúsculas, negrito.
- Um círculo mais escuro sobreposto à direita do retângulo, com o número
  da questão em branco, negrito, tamanho maior.

## Caixa de texto-suporte em verso (poema/letra de música)

Quando o texto-suporte é um poema ou letra de música (em vez de prosa),
ele ganha um tratamento visual diferente do texto corrido:
- Fundo em gradiente cinza claro-a-médio, cantos arredondados.
- Elementos gráficos decorativos discretos ao fundo (tema-relacionados —
  ex.: fogos de artifício para uma música sobre "Firework"). Não
  reproduzimos esse elemento decorativo (é específico de cada conteúdo);
  mantemos só o fundo em gradiente e a caixa arredondada.
- Fonte sem serifa para os versos, alinhados à esquerda (não justificado),
  um verso por linha, sem recuo de parágrafo.
- Se a peça tem título, ele aparece em negrito no topo da caixa.

## Figuras dentro do texto-suporte

- Centralizadas na largura da coluna (ou da página cheia, se o
  texto-suporte for compartilhado).
- Legenda/fonte da imagem logo abaixo, mesma formatação da referência de
  fonte (sem serifa, tamanho reduzido, não itálico).

## Alternativas

- Lista vertical, uma por linha.
- Letra em negrito seguida de ")", ex. "A)", depois o texto da alternativa.
- Texto da alternativa com recuo suspenso (linha 2+ alinhada ao texto, não
  à letra).

---

## Observações fora do escopo do template atual

- Em alguns casos uma única página de instruções lista formatos de questão
  adicionais (verdadeiro/falso com "( )", por exemplo). O `.md` de entrada
  (Passo 2 do `CLAUDE.md`) descreve apenas questões de alternativa única
  A–E; esse outro formato não é coberto por este template — sinalizar se
  aparecer um `.md` desse tipo, em vez de adaptar o template sem avisar.
- O brasão institucional (imagem) não foi extraído/incluído — o cabeçalho
  usa apenas o texto da marca. Se um arquivo de imagem do brasão for
  fornecido, atualizar o template para incluí-lo.
