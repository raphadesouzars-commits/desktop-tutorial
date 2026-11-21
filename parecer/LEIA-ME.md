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

## Precedentes da CGU

`precedentes_cgu.json` guarda as ementas públicas da Busca de Precedentes do SeCI (https://seci.cgu.gov.br/busca/)
para a RFB, respondidas nos últimos 3 anos. Para atualizar:

    python3 parecer/atualizar_precedentes.py && python3 parecer/build.py

## Formulário SeCI

A tela separa o texto colado nas 10 perguntas do formulário SeCI. A pergunta 10 define se a demanda é consulta ou
pedido de autorização; as respostas 7, 8 e 4 geram alertas sobre os incisos I, II e VII do art. 5º da Lei 12.813/2013.

## Envio do formulário preenchido

No passo 1 é possível enviar o formulário do servidor em PDF, DOCX, ODT ou TXT. A leitura é feita no navegador,
sem internet. O PDF é lido com a biblioteca pdf.js 3.11.174 (licença Apache-2.0, em `vendor/`), embutida no HTML.
PDF digitalizado (imagem) e arquivos `.doc` antigos não são lidos.

## Estrutura do parecer

Segue o padrão dos pareceres Coger/GNP de 2023: I. Relatório (parágrafos iniciais e formulário, com as respostas
entre aspas), II. Fundamentos (modelo da atividade, lista "Em resumo, o servidor deve" e registro de nova consulta)
e III. Conclusão (conclusão e encaminhamento). A lista de deveres está em `DEVERES`, em `app.src.html`.

## Várias atividades e conferência

No passo 2, "Adicionar outra atividade ao mesmo parecer" junta os fundamentos de mais de um modelo: a ementa é
composta, cada atividade ganha um parágrafo de abertura, fundamentos idênticos entram uma vez só e as conclusões
ficam em sequência na seção III. O painel "Conferência", acima da prévia, aponta incoerências entre as respostas
do formulário, o modelo escolhido, os precedentes da CGU e as opções marcadas (função `conferir` em `app.src.html`).

## Termo de Compromisso

Em conclusões que autorizam com ressalvas, o parecer condiciona a autorização à assinatura de Termo de Compromisso
e o botão "Gerar Termo de Compromisso" produz o documento (.docx) pronto para assinatura: identificação do servidor,
deveres gerais marcados, compromissos específicos digitados no passo 3, ciência da chefia e recebimento pela
Comissão de Ética. A redação do Termo está na função `blocosTermo`, em `app.src.html`.
