# Rodada 3 — Revisão do Contrato Veritas → Nexo Coger

## Pré-requisito

Depende da Rodada 1 concluída (`catalogo-canonico.json` e `CATALOGO_COGER` embutido nos três HTMLs) e idealmente da Rodada 2 (primeira validação prática do catálogo em uso). Como o formato de exportação pode mudar livremente — não há arquivos em produção a preservar — esta rodada tem liberdade para redesenhar o contrato do zero, sem camada de compatibilidade retroativa.

## Escopo

Dois ajustes independentes, mas entregues juntos por tocarem o mesmo par de arquivos:

### 3.1 — Padronização do nome da constante de exportação

**Decisão:** o nome definitivo é `nexo-coger` em todos os pontos — variável, chave de identificação no JSON exportado, nome de arquivo sugerido no download, e qualquer string de log ou comentário que hoje use `nexus-coger`.

**Trabalho do Claude Code:**
1. Buscar todas as ocorrências de `nexus-coger` (e variações de capitalização/hífen, ex. `nexusCoger`, `NEXUS_COGER`) em `veritas.html` e `nexo-coger.html`.
2. Substituir por `nexo-coger` (ou a variação de capitalização equivalente no mesmo padrão já usado no restante do arquivo).
3. Conferir se a mudança quebra algum nome de arquivo esperado por rotina de importação já existente no Nexo Coger — ajustar ambos os lados juntos.

### 3.2 — Extração e redesenho do contrato JSON

**Trabalho de diagnóstico (Claude Code):**
1. Ler o `veritas.html` real e localizar a função de exportação: o que ela gera hoje — estrutura de campos, nomes, tipos, aninhamento.
2. Ler o `nexo-coger.html` real e localizar a função de importação correspondente (se já existir) — o que ela espera ler.
3. Documentar as duas estruturas encontradas (mesmo que hoje estejam desalinhadas) antes de redesenhar, para que a mudança fique rastreável.

**Redesenho do contrato**, considerando o catálogo canônico da Rodada 1:

- Todo campo que hoje carrega papel de pessoa, tipo de prova ou norma como texto livre passa a carregar o `id` do catálogo (ex.: `"tipo_prova": "PROVA.DIGITAL"` em vez de `"tipo_prova": "Prova Digital"`).
- Cada prova exportada mantém os campos de cadeia de custódia já existentes no Veritas (proveniência, hash, lógica interna/externa) — a Rodada 3 não altera essa parte, só ajusta o restante do contrato para usar IDs canônicos onde aplicável.
- Incluir `schema_version` no JSON exportado, alinhado ao `schema_version` do `catalogo-canonico.json` usado no momento da exportação — permite ao Nexo Coger detectar se está importando um arquivo gerado com uma versão de catálogo diferente da que ele mesmo usa.
- Incluir referência de origem: identificador do arquivo/instância do Veritas que gerou a exportação (útil futuramente para rastreabilidade, mesmo sem uso imediato).

**Estrutura de referência (a validar contra o código real):**

```json
{
  "schema_version": "1.0.0",
  "catalogo_schema_version": "1.0.0",
  "exportado_em": "2026-07-11T00:00:00Z",
  "origem": "veritas",
  "provas": [
    {
      "id_prova": "...",
      "tipo_prova": "PROVA.DIGITAL",
      "descricao": "...",
      "hash": "...",
      "proveniencia": "...",
      "cadeia_custodia": [ ]
    }
  ]
}
```

O nome exato dos campos de cadeia de custódia deve seguir o que já existe no Veritas real — a estrutura acima é ilustrativa apenas para os campos novos (`schema_version`, `catalogo_schema_version`, `tipo_prova` por ID).

## Entregáveis da Rodada 3

1. Constante `nexo-coger` padronizada em ambos os arquivos, sem ocorrências remanescentes de `nexus-coger`.
2. Relato da estrutura JSON original encontrada em cada lado (export do Veritas, import do Nexo Coger), antes da mudança.
3. Contrato JSON redesenhado e implementado nos dois lados (exportação no Veritas, importação no Nexo Coger), usando IDs do catálogo canônico.
4. Registro no `CHANGELOG-catalogo.md` descrevendo a mudança de contrato.

## Critérios de aceite

- Um arquivo exportado do Veritas é importado sem erro pelo Nexo Coger, com todos os campos de papel/tipo de prova/norma resolvidos corretamente para os rótulos do catálogo na interface do Nexo Coger (o usuário vê o rótulo em português, não o ID cru).
- Nenhuma ocorrência de `nexus-coger` remanescente em nenhum dos dois arquivos.
- Importar um JSON com `catalogo_schema_version` diferente da versão atual do catálogo no Nexo Coger gera um aviso visível (não falha silenciosa).
