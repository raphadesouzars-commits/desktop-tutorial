# Casos de Uso - v02

**Versão 0.3 - novembro/2026.** Substitui a v01. Atores: **Parecerista** (principal), **Coordenador**, **Curador**, **Administrador (TI)**, **Copilot Chat** (sistema externo, operado pelo parecerista).

## Visão geral

| ID | Caso de uso | Ator | Requisitos | Situação |
|---|---|---|---|---|
| UC001 | Localizar precedentes | Parecerista | RF001 a RF003, RF006 | Implementado |
| UC002 | Classificar atividade | Parecerista | RF005, RF015 | Implementado |
| UC003 | Revisar parecer | Parecerista | RF007, RF008 | Implementado |
| UC004 | Consultar memória institucional | Parecerista | RF028 | **Planejado** |
| UC005 | Analisar consulta a partir do PDF do SeCI | Parecerista | RF011 a RF013 | Implementado |
| UC006 | Usar o Copilot Chat em modo assistido | Parecerista, Copilot Chat | RF033 a RF039 | Implementado (testado com respostas simuladas) |
| UC007 | Decidir e gerar documentos | Parecerista | RF010, RF015 a RF019 | Implementado |
| UC008 | Manter a base de conhecimento | Administrador, Coordenador | RF020, RF029 | Parcial |
| UC009 | Acompanhar indicadores | Coordenador | RF025, RF032 | Parcial |
| UC010 | Supervisionar a IA (auditoria) | Curador | RF026, RF037 | Parcial |
| UC011 | Analisar e usar o Copilot Chat no **modo local** (sem motor) | Parecerista, Copilot Chat | RF040 a RF044 | Implementado |

---

## UC005 - Analisar consulta a partir do PDF do SeCI

**Ator:** Parecerista. **Pré-condição:** motor em execução e base indexada (a análise funciona mesmo com a base vazia, mas avisa). **Pós-condição:** análise gravada com um identificador de consulta.

**Fluxo principal**
1. O parecerista abre a aba "Análise Inteligente" e informa o endereço do motor.
2. Escolhe o PDF do formulário do SeCI e aciona "Enviar Consulta (PDF)".
3. O sistema valida o arquivo (PDF, até 25 MB), extrai o texto (com OCR se a página não tiver texto) e registra a consulta.
4. O sistema extrai o servidor, o cargo, a matrícula, o protocolo, o tipo de demanda e as respostas 1 a 10.
5. O sistema classifica a atividade (lista fechada de 68 categorias), recupera pareceres, precedentes, normativos e modelos e monta a minuta extrativa.
6. O sistema apresenta: avisos, fatos extraídos, enquadramento com confiança, compromissos, pareceres/precedentes/normativos semelhantes (cada um com origem e motivo da similaridade) e a minuta com a origem de cada parágrafo.

**Fluxos alternativos**
- 3a. Arquivo que não é PDF: recusado com mensagem (HTTP 400). PDF acima de 25 MB: recusado (413).
- 3b. PDF digitalizado sem OCR instalado: a consulta fica com status "sem_texto" e o sistema orienta a instalar o OCR ou usar o gerador offline.
- 5a. Nenhuma categoria reconhecida: usa o modelo genérico, com confiança baixa e aviso.
- 5b. Base não indexada ou sem normativos: a análise segue, com aviso.
- 1a. Motor indisponível: a aba mostra o erro de conexão; o gerador offline continua funcionando.

## UC001 - Localizar precedentes

**Ator:** Parecerista. **Pré-condição:** consulta analisada (UC005).

**Fluxo principal**
1. O sistema monta a consulta de busca a partir da atividade, da entidade e da descrição (as atribuições do cargo ficam de fora de propósito).
2. Busca por palavras (BM25), acrescida das palavras-chave da atividade reconhecida e, se habilitado, da busca por sentido (embeddings), com fusão e reclassificação.
3. Os precedentes e pareceres da COGER recebem peso maior que os demais.
4. O sistema apresenta até 4 itens por tipo, com título, arquivo de origem, ano e **motivo da similaridade** (termos em comum e/ou similaridade semântica).
5. O parecerista analisa os resultados.

**Alternativa:** nada recuperado - o sistema informa e sugere popular a base.

## UC002 - Classificar atividade

**Ator:** Parecerista.

**Fluxo principal**
1. O sistema pontua as 68 categorias (palavras-chave, nome, descrição) e vota com os modelos institucionais recuperados.
2. Apresenta até 5 candidatas, com grau de confiança (alta, média ou baixa) e motivos.
3. O parecerista confirma ou escolhe outra atividade em lista com todas as categorias.
4. A minuta é refeita para a atividade escolhida.

**Regra:** o sistema nunca cria categoria; resposta de IA fora da lista é descartada.

## UC006 - Usar o Copilot Chat em modo assistido

**Atores:** Parecerista; Copilot Chat (conta corporativa da RFB). **Pré-condição:** consulta analisada. **Pós-condição:** minuta com fundamentação validada contra o acervo.

**Fluxo principal**
1. Na aba, o parecerista escolhe o modo: prompt completo (cabe na caixa do chat) ou prompt curto + arquivo de contexto.
2. Aciona "Gerar prompt". O sistema monta o contexto (caso mascarado, regras da COGER, normativos, precedentes, pareceres, modelos), respeita o limite de caracteres e informa o que ficou de fora.
3. O parecerista copia o prompt (e, no modo arquivo, baixa `contexto_AICI.md`) e abre o Copilot Chat com a **conta corporativa da RFB**.
4. Cola o prompt (e anexa o arquivo, se for o caso) e obtém a resposta em JSON.
5. Cola a resposta no AICI e aciona "Aplicar resposta à minuta".
6. O sistema extrai o JSON, valida as fontes citadas (só valem marcadores que o chat recebeu), descarta parágrafos sem fonte válida, adota o resultado sugerido e as ressalvas e registra tudo na trilha de auditoria.
7. A minuta passa a mostrar a fundamentação do Copilot, cada parágrafo com a origem.

**Fluxos alternativos**
- 6a. Resposta sem JSON ou JSON incompleto: recusada com orientação para pedir ao Copilot a resposta somente em JSON.
- 6b. Fonte inexistente: o parágrafo é descartado e o sistema avisa.
- 6c. O parecerista muda atividade ou conclusão depois de aplicar a resposta: o sistema pede confirmação e refaz a minuta sem a resposta do Copilot.
- 2a. Base insuficiente (sem normativo ou sem precedente/parecer/modelo): o prompt não é gerado.

**Regras:** o AICI não envia nada ao Copilot; o parecerista leva e traz o texto. O aviso na tela lembra de usar somente o Copilot Chat da conta corporativa.

## UC011 - Analisar e usar o Copilot Chat no modo local (sem motor)

**Ator:** Parecerista (e Copilot Chat, operado por ele). **Pré-condição:** nenhuma instalação; só o navegador e o `gerador-parecer-conflito.html`.

**Fluxo principal**
1. Na aba "Análise Inteligente" (modo Local), o parecerista escolhe o PDF e aciona "Analisar consulta".
2. O navegador lê o arquivo, extrai o servidor e as respostas 1 a 10, sugere a atividade e os precedentes da CGU e preenche o gerador.
3. O parecerista confere os fatos, ajusta a atividade/situação e marca os precedentes a citar.
4. (Opcional, etapa 1) Gera o prompt de entendimento, leva ao Copilot Chat, cola a resposta; o navegador valida (atividade da lista, incisos, termos), mostra o entendimento e **refaz a busca** com os termos do Copilot; o parecerista confirma ou ajusta a atividade e os termos.
4a. (Opcional, etapa 2) Gera o prompt da fundamentação (já com o entendimento da etapa 1 e a busca refinada), leva ao Copilot Chat, cola a resposta; o navegador valida as fontes e aplica a fundamentação ao parecer.
5. Segue ao gerador, revisa e gera o Word.

**Alternativas:** PDF digitalizado (sem texto): aviso, preencher manualmente; resposta inválida: recusada; fonte inexistente: parágrafo descartado.
**Biblioteca (opcional):** o parecerista pode conectar a pasta da biblioteca sincronizada do SharePoint (uma vez); o navegador a indexa e passa a mostrar pareceres e precedentes da COGER parecidos e a levá-los ao prompt. **Limites:** não há bloqueio técnico de revisão; a biblioteca só é consultada se conectada.

## UC007 - Decidir e gerar documentos

**Ator:** Parecerista.

**Fluxo principal**
1. O parecerista revisa fatos, enquadramento, fontes e compromissos.
2. Escolhe a atividade e a **conclusão do caso concreto** (sem conflito; sem conflito com ressalvas; risco relevante; outro). A minuta é refeita.
3. Marca a confirmação de revisão (obrigatória).
4. Gera o parecer em Word (do motor) ou aciona "Aplicar no gerador" para editar no gerador offline.
5. Nas autorizações com ressalvas, gera também o Termo de Compromisso; gera o despacho, se necessário.

**Alternativas**
- 3a. Sem a confirmação: botões bloqueados na tela e API recusa (HTTP 422).
- 4a. Termo solicitado para conclusão sem ressalvas: recusado.
- 2a. Conclusão diferente da do modelo: o sistema avisa para revisar os fundamentos.

## UC003 - Revisar parecer

**Ator:** Parecerista.
1. Com a minuta pronta, o parecerista aciona "Revisar minuta".
2. O sistema aponta campos pendentes, parágrafos sem origem, conclusão incoerente com o resultado e ausência de menção ao Termo de Compromisso.
3. O parecerista decide sobre as correções.

## UC004 - Consultar memória institucional (planejado)

**Ator:** Parecerista.
1. O usuário formula uma pergunta em linguagem natural.
2. O sistema pesquisa a base (pareceres, precedentes, normativos, regras da COGER).
3. O sistema apresenta resposta fundamentada, com os documentos citados (no modo assistido, por meio do Copilot Chat e da mesma validação de fontes).

## UC008 - Manter a base de conhecimento

**Atores:** Administrador, Coordenador.
1. Atualiza a biblioteca no SharePoint (novos pareceres, precedentes, normativos).
2. Importa para o servidor (`scripts/importar_biblioteca.py`) - sincronização automática é planejada.
3. Reindexa (`POST /indexar` ou reinício); só o que mudou é reprocessado.
4. O Coordenador valida entendimentos novos e atualiza `regras_coger.md` (seção "A consolidar pela COGER").
5. Após alterar modelos do gerador, o Administrador exporta as categorias (`scripts/exportar_categorias.py`).

## UC009 - Acompanhar indicadores

**Ator:** Coordenador. Consulta totais por atividade, resultado, precedente mais utilizado e mês (`GET /indicadores`, ou a seção "Indicadores gerenciais" da aba).

## UC010 - Supervisionar a IA

**Ator:** Curador. Examina `metrics/ia_auditoria.jsonl` (prompts gerados, respostas aplicadas, chamadas automáticas), avalia a qualidade, procura alucinações e vieses, registra evidências e comunica desvios à Cotec (art. 12 da Portaria RFB nº 647/2026). Ferramenta de consulta à trilha: planejada.
