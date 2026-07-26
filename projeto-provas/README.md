# Geração de PDFs de Simulados — Bahiana/PROSEF

Ver `CLAUDE.md` para o escopo completo do projeto.

## Status atual

- ✅ Estrutura de pastas criada (`referencia/`, `template/`, `questoes-md/`, `scripts/`, `output/`).
- ⚠️ **Passo 0 pendente**: nenhum PDF de referência real foi fornecido ainda.
  `template/especificacao_visual.md` está marcado como **provisório**,
  baseado em convenções genéricas de prova de vestibular — precisa ser
  substituído pela inspeção real de PDFs escaneados assim que estiverem
  em `referencia/`.
- ✅ Template (`template/prova.html` + `template/estilo.css`) implementado
  seguindo a especificação provisória: A4, 2 colunas, cabeçalho/rodapé
  repetidos em todas as páginas, numeração de página, caixa de número de
  questão, alternativas A-E, tabela de gabarito + justificativas.
- ✅ `scripts/gerar_pdf.py` implementado e testado de ponta a ponta com
  `questoes-md/_exemplo_teste.md` (arquivo sintético, sem valor pedagógico,
  só para validar o parser e a geração de PDF).

## Próximos passos (dependem de você)

1. Adicionar pelo menos um PDF real de prova antiga em `referencia/`.
2. Rodar o Passo 0 (`pdftoppm` + inspeção visual) e atualizar
   `template/especificacao_visual.md` com o padrão real.
3. Ajustar as variáveis CSS em `template/estilo.css` para bater com a
   especificação real (Passo 4 — validação visual lado a lado).
4. Adicionar os `.md` reais gerados pelo projeto Claude "Bahiana" em
   `questoes-md/` e gerar os PDFs finais.

## Uso

```bash
pip install -r scripts/requirements.txt
python scripts/gerar_pdf.py questoes-md/<arquivo>.md
python scripts/gerar_pdf.py questoes-md/<arquivo>.md --sem-gabarito
```

O PDF é salvo em `output/[tema-em-slug]_[AAAA-MM-DD].pdf`.

A flag `--sem-gabarito` (versão só com resumo + questões, sem gabarito) foi
implementada como opção — o `CLAUDE.md` pede para perguntar antes de
implementar a separação em duas versões; fique à vontade para não usá-la
se preferir só a versão completa por padrão.
