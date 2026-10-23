# Rodada 7 — Teste de Fluxo Integrado Ponta a Ponta

## Pré-requisito

Depende das Rodadas 1–6 concluídas: catálogo canônico, bugs corrigidos, e os três contratos (Veritas→Nexo Coger, Nexo Coger→Oitiva 360, Oitiva 360→Veritas, Oitiva 360→Nexo Coger) implementados.

## Escopo

### 7.1 — Diagnóstico: separabilidade da lógica

Como os três sistemas são HTML single-file sem build/test runner, o primeiro passo é verificar, em cada um, se as funções centrais de cada contrato (exportar, importar, calcular hash, validar schema) já estão separadas da manipulação de DOM, ou se estão misturadas (ex.: uma função que lê um campo do formulário, calcula e já escreve o resultado na tela, tudo junto).

Onde estiverem misturadas, extrair essa lógica para funções puras (recebem dados, devolvem dados, sem tocar em `document`), mantendo o comportamento da interface idêntico — é refatoração de organização interna, não mudança de funcionalidade. Isso é o que torna possível rodar os testes via Node, sem precisar simular um navegador inteiro.

Se as três suítes já expõem essas funções de forma isolada (ex.: dentro de um objeto ou módulo interno do `<script>`), esse passo é só de confirmação.

### 7.2 — Caso de teste fictício reutilizável

Criar `fixtures/pad-ficticio-001.json`: um PAD simulado completo, cobrindo o fluxo inteiro —

- Um acusado.
- Dois ou três fatos apurados, com normas do catálogo canônico vinculadas.
- Uma prova inicial cadastrada no Veritas (documento fictício, com hash).
- Ao menos uma lacuna que gera pauta de instrução.
- Um depoente (testemunha), com respostas fictícias às perguntas da pauta — incluindo pelo menos uma resposta que, na Rodada 6, resulta em vínculo automático com o acusado padrão.

Esse fixture fica salvo no projeto para reuso em testes futuros — qualquer mudança nas Rodadas 1–6 pode ser validada rodando o mesmo caso de novo.

### 7.3 — Script de teste automatizado

`test-fluxo-integrado.js`, executável via `node test-fluxo-integrado.js` (sem interação manual, sem abrir navegador), usando as funções extraídas em 7.1 e o fixture de 7.2. Sequência simulada:

1. Veritas exporta a prova inicial do fixture → valida estrutura do contrato (Rodada 3).
2. Nexo Coger importa essa prova → confirma que os campos de tipo de prova/norma foram resolvidos para os rótulos corretos via ID do catálogo.
3. Nexo Coger gera pauta a partir da lacuna do fixture → valida `pauta_id` único e estrutura (Rodada 4).
4. Oitiva 360 importa a pauta → popula rodada de oitiva com as perguntas do fixture.
5. Oitiva 360 gera o termo com as respostas do fixture → calcula hash → exporta para Veritas (Rodada 5).
6. Veritas importa o termo → confere hash → gera novo `id_prova`.
7. Oitiva 360 exporta o retorno da prova para o Nexo Coger, usando o `id_prova` gerado no passo 6 → Nexo Coger importa e vincula ao acusado padrão, sem disparar indiciação (Rodada 6).

### 7.4 — Testes de idempotência

Repetir cada passo de importação (2, 4, 6, 7) uma segunda vez com o mesmo payload, e afirmar que:
- Nenhum registro duplicado é criado.
- O sistema sinaliza a tentativa de reimportação de forma explícita (não falha silenciosa, não duplica silenciosamente).

### 7.5 — Testes de falha controlada

- Alterar um caractere do texto do termo antes do passo 6 e confirmar que a importação no Veritas é rejeitada por divergência de hash (valida o critério de aceite da Rodada 5).
- Importar um payload com `catalogo_schema_version` diferente da versão atual e confirmar que o sistema gera aviso (valida critério da Rodada 3).

### 7.6 — Relatório de saída

O script imprime um relatório claro no console: cada etapa (1 a 7), se passou ou falhou, e para os testes de idempotência/falha controlada, se o comportamento esperado (rejeição, aviso, não duplicação) ocorreu. Sem necessidade de framework de teste (Jest, Mocha etc.) — asserts simples com `console.assert` ou equivalente são suficientes dado o porte do projeto.

## Entregáveis da Rodada 7

1. Funções centrais extraídas e testáveis via Node, nos três HTMLs (só onde ainda não estavam separadas).
2. `fixtures/pad-ficticio-001.json`.
3. `test-fluxo-integrado.js`, executável de ponta a ponta sem interação manual.
4. Relatório de execução (saída do script) demonstrando todas as 7 etapas passando, mais os testes de idempotência e falha controlada.

## Critérios de aceite

- `node test-fluxo-integrado.js` roda do início ao fim sem erros não tratados, imprimindo o relatório de todas as etapas.
- As quatro reimportações testadas (passos 2, 4, 6, 7) não geram duplicidade.
- A alteração de hash é corretamente rejeitada; a divergência de `catalogo_schema_version` corretamente sinalizada.
- O fixture `pad-ficticio-001.json` permanece no projeto, documentado o suficiente para ser reexecutado após qualquer mudança futura nas Rodadas 1–6.
