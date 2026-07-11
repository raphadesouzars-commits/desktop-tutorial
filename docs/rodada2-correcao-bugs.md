# Rodada 2 — Correção dos Bugs Conhecidos (contra o catálogo canônico)

## Pré-requisito

Depende da Rodada 1 concluída: `catalogo-canonico.json` existente e populado, com `PAPEL.VITIMA` e `PAPEL.PESSOA_SITUACAO_INDEFINIDA` já definidos como entradas únicas e sem ambiguidade. Esta rodada não cria vocabulário novo — só corrige onde os sistemas usam (ou deixam de usar) o vocabulário já definido.

## Escopo

Dois problemas conhecidos, ambos de causa ainda não diagnosticada — o diagnóstico faz parte do trabalho desta rodada, feito lendo o código real dos arquivos:

### Bug 1 — Classificação incorreta do papel de vítima (Oitiva 360, Rodada 6)

**Sintoma relatado:** na Rodada 6 do fluxo de oitiva, o papel de vítima é atribuído/exibido de forma incorreta.

**Trabalho de diagnóstico (Claude Code):**
1. Localizar no `oitiva-360.html` toda a lógica que lê, atribui ou exibe o papel de pessoa na Rodada 6 — campo de formulário, função de mapeamento, e trecho de exportação/renderização.
2. Determinar em qual dessas três camadas está a falha: entrada de dado (formulário permite valor errado), lógica interna (mapeamento troca papéis), ou saída (exibição/exportação usa rótulo errado mesmo com dado correto).
3. Confirmar se o mesmo campo/lógica é usado em outras rodadas do Oitiva 360 — se sim, verificar se o bug se repete lá também, mesmo sem ter sido relatado.

**Correção:** ajustar a camada identificada para usar `PAPEL.VITIMA` do catálogo canônico (por ID, não por string), eliminando a possibilidade de divergência de rótulo entre telas.

**Critério de aceite:** em um caso de teste manual (uma oitiva fictícia com um depoente marcado como vítima), o papel exibido e exportado na Rodada 6 corresponde exatamente ao papel atribuído na entrada, em todas as telas subsequentes do fluxo.

### Bug 2 — Ausência de "pessoa em situação indefinida" no vocabulário de prova do Nexo Coger

**Sintoma relatado:** o papel não aparece em algum ponto do vocabulário de prova do `nexo-coger.html` — local exato não mapeado.

**Trabalho de diagnóstico (Claude Code):**
1. Levantar todos os pontos do `nexo-coger.html` onde papéis de pessoa são selecionáveis ou exibidos: formulário de cadastro de pessoa envolvida, seletor de papel ao vincular fato-prova, filtros de visualização do mapa fático-probatório, e qualquer tela de exportação/relatório que liste papéis.
2. Para cada ponto, verificar se a lista de opções é estática (hardcoded no HTML/JS) ou dinâmica (lida de alguma estrutura de dados interna). Isso determina se a correção é só de conteúdo (adicionar a opção) ou também estrutural (a fonte da lista precisa mudar para ler do catálogo).
3. Mapear todos os pontos onde o papel está ausente — pode ser mais de um.

**Correção:** cada ponto identificado passa a ler a lista de papéis do `CATALOGO_COGER` (ver Rodada 1), garantindo que `PAPEL.PESSOA_SITUACAO_INDEFINIDA` apareça em todos os lugares onde os demais papéis aparecem — não apenas no ponto onde a ausência foi originalmente notada.

**Critério de aceite:** uma busca por `PAPEL.PESSOA_SITUACAO_INDEFINIDA` (ou pelo rótulo "pessoa em situação indefinida") no código do `nexo-coger.html` retorna presença em todos os seletores/formulários de papel, não em um subconjunto.

## Efeito colateral esperado (e desejável)

Ao migrar essas duas correções para consumir o catálogo por ID, os dois sistemas já deixam de usar string livre nesses dois pontos específicos — isso é a primeira fatia real de migração das Rodadas 3–6 (contratos JSON), então o trabalho desta rodada não é só correção pontual, é o primeiro teste de que o catálogo canônico funciona na prática antes de virar contrato entre sistemas.

## Entregáveis da Rodada 2

1. Relato de diagnóstico dos dois bugs (causa raiz identificada, camada afetada).
2. Correção aplicada em `oitiva-360.html` e `nexo-coger.html`, usando IDs do catálogo canônico nos dois pontos corrigidos.
3. Registro no `CHANGELOG-catalogo.md` (iniciado na Rodada 1) indicando que essas duas correções foram fechadas nesta rodada.

## Critérios de aceite gerais

- Nenhuma string livre ("vítima", "pessoa em situação indefinida" como texto solto) permanece nos dois pontos corrigidos — ambos referenciam o ID do catálogo.
- Teste manual dos dois cenários (oitiva com vítima; cadastro de pessoa em situação indefinida no Nexo Coger) confirma comportamento correto de ponta a ponta.
- Nenhuma regressão nos demais papéis/fluxos que usavam os mesmos formulários ou seletores tocados na correção.
