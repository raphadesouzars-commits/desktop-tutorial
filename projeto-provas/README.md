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
- ✅ `scripts/gerar_pdf.py` implementado e testado de ponta a ponta com
  `questoes-md/_exemplo_teste.md` (arquivo sintético, sem valor pedagógico,
  só para validar o parser e a geração de PDF).

## Próximos passos (dependem de você)

1. Adicionar os `.md` reais gerados pelo projeto Claude "Bahiana" em
   `questoes-md/` e gerar os PDFs finais.
2. Se um `.md` real tiver texto-suporte em verso/poema (ver
   `especificacao_visual.md` → caixa de verso) ou texto-suporte
   compartilhado por várias questões, avisar antes — o parser atual
   assume uma questão = um texto-suporte de prosa.
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
