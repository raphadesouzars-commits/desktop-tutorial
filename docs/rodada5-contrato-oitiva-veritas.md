# Rodada 5 — Contrato Oitiva 360 → Veritas (Cadeia de Custódia do Termo)

## Pré-requisito

Depende das Rodadas 1–4 concluídas. O termo gerado nesta rodada carrega `pauta_id` (Rodada 4) para permitir rastreabilidade completa desde a lacuna que originou a pergunta até a prova final.

## Escopo

Como o termo é só texto (transcrição/ata, sem áudio/vídeo), o contrato pode ser inteiramente textual — sem necessidade de anexar binário em base64, o que simplifica o arquivo único offline.

### 5.1 — Geração do termo no Oitiva 360 (do zero)

Ao final de uma rodada de oitiva, o Oitiva 360 deve compor um termo estruturado, não apenas as respostas soltas:

- Identificação do depoente (nome, papel — ID do catálogo).
- Data/hora da oitiva.
- Responsável pela condução (se o sistema já capturar esse dado; se não, campo pode ficar vazio nesta rodada).
- Cada pergunta da pauta (Rodada 4) e a resposta correspondente registrada, na ordem em que foram feitas.
- Observações gerais, se o Oitiva 360 já tiver esse campo.

O termo final é serializado como texto simples (o conteúdo que apareceria num documento impresso), e é sobre essa string de texto que o hash de integridade é calculado — não sobre o JSON inteiro, para que o hash sobreviva a mudanças de metadado no envelope.

### 5.2 — Cálculo de hash pelo próprio Oitiva 360

O Oitiva 360 calcula um hash (SHA-256, mesmo algoritmo já usado no Veritas para consistência) sobre o texto final do termo, **antes** de exportar. Esse hash vai junto no envelope JSON como `hash_origem` — permite ao Veritas, ao importar, recalcular o hash sobre o texto recebido e confirmar que não houve alteração no trajeto (mesmo sendo importação manual de arquivo local, essa checagem já vale como prática de integridade e prepara o sistema para qualquer transporte menos confiável no futuro).

### 5.3 — Importação no Veritas

O Veritas recebe o envelope e cria uma nova prova com:

- **Tipo de prova:** `PROVA.TERMO_OITIVA` — se esse ID ainda não existir no catálogo canônico, deve ser adicionado nesta rodada (pequena extensão do catálogo, justificada porque é um tipo de prova novo surgindo do próprio fluxo de integração).
- **Proveniência:** marcada como interna — o termo nasce dentro da própria suíte COGER, ao contrário de um documento externo anexado manualmente. Usar a lógica de proveniência interna já existente no Veritas para essa distinção.
- **Hash:** recalculado pelo Veritas sobre o texto recebido e comparado ao `hash_origem`. Divergência bloqueia a importação com mensagem clara — não falha silenciosa.
- **Novo `id_prova`** gerado pelo Veritas no momento da importação — esse é o identificador que a Rodada 6 vai usar para vincular a prova ao Nexo Coger.

**Estrutura de referência:**

```json
{
  "schema_version": "1.0.0",
  "catalogo_schema_version": "1.0.0",
  "origem": "oitiva-360",
  "pauta_id": "PAUTA.2026-07-11.001",
  "rodada_id": "...",
  "deponente": {
    "nome": "...",
    "papel": "PAPEL.TESTEMUNHA"
  },
  "termo": {
    "conteudo": "texto completo do termo, formatado como documento",
    "gerado_em": "2026-07-11T00:00:00Z",
    "responsavel": "..."
  },
  "hash_origem": "sha256:..."
}
```

## Entregáveis da Rodada 5

1. Função de geração do termo estruturado no Oitiva 360, ao final de uma rodada de oitiva.
2. Cálculo de hash sobre o texto do termo, antes da exportação.
3. `PROVA.TERMO_OITIVA` adicionado ao catálogo canônico, se ainda não existir.
4. Rotina de importação no Veritas: criação de prova com proveniência interna, verificação de hash, geração de `id_prova`.
5. Registro no `CHANGELOG-catalogo.md`.

## Critérios de aceite

- Um termo exportado do Oitiva 360 é importado no Veritas sem erro, com hash conferido e proveniência marcada como interna.
- Alterar manualmente um caractere do texto do termo antes da importação faz o Veritas rejeitar o arquivo por divergência de hash.
- A prova criada no Veritas recebe `id_prova` único, disponível para uso na Rodada 6.
- O termo importado preserva a ordem original de perguntas e respostas, sem reordenação ou perda de conteúdo.
