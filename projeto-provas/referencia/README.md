# referencia/

Coloque aqui os PDFs escaneados das provas antigas (Bahiana/PROSEF) que servem
de referência visual. Estes arquivos são **somente leitura** — nunca editar
ou apagar o conteúdo original.

Assim que o primeiro PDF real for adicionado, execute o Passo 0 do
`CLAUDE.md` (extração da especificação visual):

```
pdftoppm -png -r 150 -f <pagina_inicial> -l <pagina_final> referencia/<arquivo>.pdf referencia/pagina
```

Depois visualize as imagens geradas e atualize `template/especificacao_visual.md`
com o que for observado de fato (fonte, margens, colunas, cabeçalho, etc.),
substituindo a versão provisória atual.

Nenhum PDF de referência foi fornecido ainda — esta pasta está vazia por enquanto.
