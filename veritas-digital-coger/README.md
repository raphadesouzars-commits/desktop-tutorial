# Veritas Digital - Coger

Ferramenta de apoio à decisão para comissões de PAD/sindicância da Corregedoria da RFB — documenta a cadeia de custódia dos elementos de prova digitais e documentais juntados ao processo. Ver especificação completa em `Desenho Estrutural v0.2`.

## Uso

Abra **`veritas_digital_coger.html`** diretamente no navegador (duplo clique ou `Arquivo > Abrir`). É um arquivo único, 100% offline — nenhum dado sai do computador. Hashes são calculados localmente via `crypto.subtle` (SHA-256).

O dossiê do processo é salvo automaticamente no `localStorage` do navegador. Use **Exportar .json** para gerar o arquivo de trabalho recalculável (o que carrega o valor probatório de continuidade) e **Imprimir / Salvar PDF** na tela de Relatório para gerar a peça para os autos.

## Estrutura

```
veritas-digital-coger/
├── veritas_digital_coger.html   ← arquivo único a distribuir/abrir (gerado)
├── coger-ui.css                  ← design system institucional (embutido no HTML)
├── build.sh                      ← remonta o HTML a partir dos fontes abaixo
└── src/
    ├── template.html             ← esqueleto HTML
    ├── app.css                   ← estilos próprios da ferramenta
    └── app.js                    ← lógica da aplicação
```

Para alterar a ferramenta: edite os arquivos em `src/` (ou `coger-ui.css`) e rode `./build.sh` para regerar `veritas_digital_coger.html`.

## Escopo implementado (Fase 1 — MVP)

Tela do processo (dados, lista de itens, export/import `.json`); cadastro de item em 4 etapas (identificação, proveniência, arquivos múltiplos com hash e verificação individuais, linha do tempo); cálculo de hash local (SHA-256) e comparação conforme proveniência; custodiante atual e status (Ativo/Substituído/Contestado/Descartado); Conferência Geral por arquivo com agregação por item; relatório de impressão (resumo + apêndice com linha do tempo detalhada); export/import do dossiê com `hashDoDossie`; dicas contextuais.

Fases 2 e 3 (refinamento e integração com o ecossistema Coger) permanecem como próximos passos, conforme o desenho estrutural.
