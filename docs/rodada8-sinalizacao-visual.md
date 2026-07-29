# Rodada 8 — Sinalização Visual de Pendências

## Pré-requisito

Depende das Rodadas 1–7 concluídas. Escopo restrito, conforme decidido: sinalização **local a cada ferramenta**, sem detecção automática entre sistemas — cada indicador reflete apenas o que já foi importado manualmente e ainda não foi processado dentro da própria ferramenta.

## Restrição de arquitetura

Como não há servidor nem verificação automática entre arquivos, "pendente" não significa "existe algo em outro sistema esperando para ser importado" — significa "algo já foi importado aqui e ainda não recebeu a próxima ação do usuário dentro desta mesma ferramenta". A detecção é sempre local, e recalculada a partir do estado atualmente carregado (o JSON de trabalho que o usuário salva/carrega em cada ferramenta, seguindo o padrão já usado no restante da suíte).

## Escopo

### 8.1 — Diagnóstico do mecanismo de persistência

Confirmar, em cada uma das três ferramentas, como o estado de trabalho é salvo/carregado hoje (exportação/importação de JSON local, já usada no restante da suíte). A sinalização desta rodada usa esse mesmo mecanismo — nenhum armazenamento novo (como `localStorage`) é introduzido, para manter a ferramenta previsível e portátil entre computadores.

### 8.2 — Campo de status por item importado

Cada entidade que chega por importação (Rodadas 3–6) ganha um campo de status simples:

| Ferramenta | Entidade | Estados |
|---|---|---|
| Nexo Coger | Prova importada do Veritas | `pendente` → `vinculada` (usuário associou a um fato) |
| Oitiva 360 | Pauta importada do Nexo Coger | `pendente` → `em_andamento` → `concluida` |
| Nexo Coger | Retorno de prova de oitiva | `pendente_revisao` → `revisado` |

A transição de estado acontece pela ação natural que o usuário já realizaria (vincular a prova a um fato, iniciar/concluir a rodada de oitiva, abrir e confirmar o retorno) — não é um botão novo e isolado só para "marcar como visto".

### 8.3 — Indicador visual

Um contador (badge) no cabeçalho de cada ferramenta, próximo ao logotipo/hero band do design system COGER, mostrando a quantidade de itens em estado pendente daquela ferramenta. Uso da paleta navy/gold: fundo navy do cabeçalho, badge em dourado com o número, para contraste sem introduzir cor nova ao sistema visual.

Clicar no badge filtra ou rola a visualização até os itens pendentes correspondentes — evita que o indicador seja só decorativo.

### 8.4 — Sem polling, sem verificação automática

Nenhuma das três ferramentas verifica arquivos de outra automaticamente, nem ao abrir nem em intervalo. O indicador só muda quando o usuário importa algo novo ou processa um item existente, dentro da própria sessão de uso.

## Entregáveis da Rodada 8

1. Diagnóstico do mecanismo de persistência atual de cada ferramenta.
2. Campo de status adicionado às três entidades da tabela acima, persistido no JSON de estado de cada ferramenta.
3. Badge de pendências no cabeçalho das três ferramentas, com contagem correta e navegação ao clicar.
4. Registro no `CHANGELOG-catalogo.md`.

## Critérios de aceite

- Importar uma prova no Nexo Coger e não vinculá-la a nenhum fato mantém o badge com a contagem correspondente.
- Vincular a prova a um fato reduz a contagem em um, sem recarregar a página.
- Salvar o estado, fechar e recarregar o JSON preserva os status corretamente — nenhum item pendente "some" nem vira "vinculado" sozinho.
- Nenhuma das três ferramentas tenta acessar ou verificar arquivo de outra ferramenta automaticamente.
