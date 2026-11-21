# Gerador de parecer – conflito de interesses

O arquivo `gerador-parecer-conflito.html` (na raiz) é montado a partir desta pasta:

- `app.src.html` – tela, prévia e geração do Word
- `modelos/*.json` – um arquivo por atividade, com uma variante por conclusão/situação
- `cabecalho.jpg` – imagem padrão do cabeçalho
- `build.py` – junta tudo em um arquivo único

Para incluir ou corrigir um modelo, edite ou crie um JSON em `modelos/` (copie um existente) e rode:

    python3 parecer/build.py

Marcadores aceitos no texto: `{{nome}}`, `{{cargo}}`, `{{cargo_sigla}}`, `{{unidade}}`, `{{matricula}}`,
`{{portaria_curta}}`, `{{orgao_corregedoria}}`, `{{g:masculino|feminino}}` e os campos declarados em `campos`.
`**negrito**` e `*itálico*` também são aceitos.

Os modelos não contêm dados pessoais: nomes, matrículas, processos e entidades dos casos concretos foram
substituídos por campos.
