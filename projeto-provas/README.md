# Geração de PDFs de Simulados — Bahiana/PROSEF

Ver `CLAUDE.md` para o escopo completo do projeto.

## Status atual

- ✅ Estrutura de pastas criada (`referencia/`, `template/`, `questoes-md/`, `scripts/`, `output/`).
- ✅ **Passo 0 concluído**: `template/especificacao_visual.md` foi extraída
  por inspeção visual real de 3 provas em `referencia/` (Medicina 2021.1,
  Medicina 2021.2, Área de Saúde 2021.2) — página de capa, instruções e
  conteúdo (questões 1 a 11) convertidas em PNG a 150 DPI e comparadas
  visualmente.
- ✅ Template (`template/prova.html` + `template/estilo.css`) reescrito para
  bater com o padrão real: escala de cinza (sem cor de destaque), cabeçalho
  institucional só na 1ª página (não repete por página — só um filete duplo
  se repete), 2 colunas com filete vertical, selo de questão composto (pílula
  "QUESTÃO" + círculo com o número), texto-suporte serifado vs.
  comando/alternativas sem serifa, rodapé com instituição + prova + página.
- ✅ Comparação lado a lado (Passo 4) feita entre a página gerada e a
  página 3 de `BAHIANA_MED_2021.1_TIPO1.pdf` — proporções de coluna, caixas
  de cabeçalho, selo de questão e tipografia condizentes.
- ✅ `scripts/gerar_pdf.py` implementado e testado de ponta a ponta, incluindo
  com um `.md` **real**: `questoes-md/Revisao_Fisiologia_Digestiva_Absorcao_Intestinal.md`
  (10 questões, PDF de 9 páginas gerado e inspecionado visualmente).
- ✅ **Resumo roda em 1 coluna de largura cheia** (decisão de projeto — ver
  `especificacao_visual.md` → seção "Colunas"), enquanto questões e gabarito
  continuam em 2 colunas. Isso resolveu um bug real encontrado com o .md de
  fisiologia digestiva: uma tabela de 4 colunas no resumo não cabia numa
  coluna estreita e transbordava por cima do texto vizinho
  (`column-span: all` não funciona no WeasyPrint para contornar isso).
- ✅ Parser ajustado para convenções reais observadas no .md de fisiologia
  digestiva: cabeçalhos de seção no formato "BLOCO N — ...", questões em
  **negrito** (não só `###`), referência de fonte totalmente em itálico sem
  prefixo "Fonte:", e cabeçalhos de justificativa do gabarito com texto
  extra após o número ("### Questão 1 — Correta: C").
- ✅ Blocos de cálculo linha a linha (crase tripla ` ``` ` no .md, comuns em
  questões de exatas) agora viram bloco monoespaçado com quebra de linha
  preservada (extensão `fenced_code` do markdown + estilo `pre`/`code`).
- ✅ **Texto-suporte compartilhado por 2+ questões** ("Questões N e M
  (estímulo comum)") suportado de verdade: rótulo + texto-suporte + fonte
  aparecem uma vez, em largura cheia, acima das colunas — igual ao padrão
  das provas oficiais de referência — e as questões do grupo entram depois
  em 2 colunas só com comando + alternativas. Descoberto e implementado a
  partir do .md de Sociologia (Marx/Durkheim/Weber), que tinha 3 grupos
  desse tipo.

## Próximos passos (dependem de você)

1. Adicionar novos `.md` reais gerados pelo projeto Claude "Bahiana" em
   `questoes-md/` e gerar os PDFs.
2. Se um `.md` novo tiver texto-suporte em verso/poema (ver
   `especificacao_visual.md` → caixa de verso), avisar antes — isso ainda
   não é reconhecido automaticamente (precisa da classe CSS `.verso`
   aplicada manualmente).
3. Se você tiver o arquivo de imagem do brasão da Bahiana, podemos incluí-lo
   no cabeçalho (hoje ele usa só o nome em texto).

## Uso

```bash
pip install -r scripts/requirements.txt
python scripts/gerar_pdf.py questoes-md/<arquivo>.md
python scripts/gerar_pdf.py questoes-md/<arquivo>.md --sem-gabarito
```

Outras opções: `--instituicao`, `--subtitulo-instituicao`,
`--processo-seletivo`, `--nome-prova`, `--instrucao`, `--saida`
(`python scripts/gerar_pdf.py --help` para a lista completa).

O PDF é salvo em `output/[tema-em-slug]_[AAAA-MM-DD].pdf`.

A flag `--sem-gabarito` (versão só com resumo + questões, sem gabarito) foi
implementada como opção — o `CLAUDE.md` pede para perguntar antes de
implementar a separação em duas versões; fique à vontade para não usá-la
se preferir só a versão completa por padrão.
