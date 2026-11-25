# Visão do Produto - AICI

**Versão 0.3 - novembro/2026**

## 1. Declaração de visão

> Para os pareceristas da COGER que analisam consultas e pedidos de autorização sobre conflito de interesses, o **AICI** é um assistente de memória institucional que localiza precedentes, normativos e fundamentos já consolidados e monta uma minuta rastreável de parecer, **mantendo a decisão sempre com o parecerista**. Diferentemente de um chatbot genérico, o AICI só raciocina sobre o acervo da própria COGER.

## 2. Situação atual

A COGER produz pareceres de conflito de interesse utilizando conhecimento acumulado em pareceres anteriores, precedentes, normativos e modelos institucionais.

Parte significativa desse conhecimento encontra-se atualmente incorporada ao sistema `gerador-parecer-conflito.html`: 68 atividades, 163 situações (cada uma com a conclusão, os fundamentos e a origem em parecer real), leitura do formulário SeCI em PDF, múltiplas atividades no mesmo parecer, escolha da conclusão do caso concreto, Termo de Compromisso, consulta a precedentes da CGU e conferência de coerência. O gerador funciona offline, sem enviar dados para fora do navegador.

Limites do estado atual:

- a escolha da atividade e a pesquisa de precedentes dependem de o parecerista já saber o que procurar;
- o acervo de pareceres emitidos (centenas de documentos) não é pesquisável por sentido, apenas por nome de arquivo;
- não há medição de uso nem trilha de decisão.

## 3. Problema que o produto resolve

| Dor | Efeito |
|---|---|
| Pesquisa manual de precedentes em centenas de arquivos | Tempo gasto e risco de omitir precedente relevante |
| Entendimentos espalhados em documentos | Divergências entre pareceres semelhantes |
| Conhecimento na memória de poucos pareceristas | Dificulta a formação de novos pareceristas |
| Sem rastreabilidade das fontes de cada fundamento | Revisão e auditoria mais lentas |
| Sem indicadores | Gestão sem visão dos temas recorrentes |

## 4. Usuários

| Perfil | Necessidade | Uso principal |
|---|---|---|
| Parecerista (usuário principal) | Analisar a consulta com rapidez e consistência | Enviar o PDF, revisar fatos e enquadramento, escolher a conclusão, gerar o Word |
| Coordenador do grupo de pareceristas | Uniformizar entendimentos e revisar | Consultar indicadores, validar entendimentos novos na base |
| Parecerista novato | Aprender a linha da COGER | Ver precedentes semelhantes, justificativas e modelos |
| Curador da IA (exigência de governança) | Monitorar qualidade e desvios | Consultar a trilha de auditoria das chamadas à IA |
| Equipe de TI | Operar e dar suporte | Configuração, indexação, monitoramento |

## 5. Proposta de valor e diferenciais

1. **Conhecimento no acervo, não no código.** Atividades, textos, regras e instruções à IA são arquivos editáveis; a evolução não exige reescrever o sistema.
2. **Sempre com a base.** A IA nunca recebe só o caso: o contexto leva normativos, precedentes, pareceres, modelos e as regras da COGER.
3. **Rastreabilidade.** Cada parágrafo da minuta informa a origem (parecer/ano ou normativo); parágrafo de IA sem fonte válida é descartado.
4. **Decisão humana garantida.** A geração do documento só é liberada após a validação do parecerista (bloqueio técnico na tela e na API).
5. **Funciona sem IA e com o Copilot Chat da RFB.** Sem IA, o AICI monta a minuta a partir dos modelos institucionais. Com IA, usa o **Copilot Chat** da conta corporativa (aprovado pelo CTSI em 18/06/2026): o AICI prepara o prompt com o caso e o acervo, o parecerista o leva ao chat e cola a resposta, que o AICI **valida contra o acervo** antes de aproveitar. A camada de IA é substituível (Azure OpenAI, agente Copilot Studio ou outro modelo homologado, se a TI disponibilizar acesso programático).
6. **Preserva o que já funciona.** O Word gerado segue o padrão atual dos pareceres e o gerador offline continua disponível.

## 6. Funcionalidades

### 6.1 Disponíveis no protótipo

| Grupo | Funcionalidade |
|---|---|
| Entrada | Upload do PDF do SeCI; OCR para PDF digitalizado; extração do servidor, cargo, matrícula, protocolo e das respostas 1 a 10 |
| Análise | Fatos estruturados; enquadramento em uma das 68 atividades, com grau de confiança; precedentes, pareceres e normativos semelhantes com a justificativa da similaridade |
| Minuta | Relatório, fundamentos e conclusão; resultado sugerido (sem conflito, com ressalvas, risco relevante, outro); compromissos e ressalvas |
| Decisão | O parecerista confirma ou altera a atividade e a conclusão; a minuta é refeita |
| Documentos | Parecer, Termo de Compromisso (autorização com ressalvas) e despacho em Word editável, a partir de modelos |
| Qualidade | Revisão de consistência (campos pendentes, parágrafo sem fonte, conclusão incoerente com o resultado) |
| Gestão | Indicadores por atividade, resultado, precedente mais utilizado e mês; trilha de auditoria |
| IA | **Copilot Chat assistido** (prompt e arquivo de contexto prontos; resposta colada e validada: fontes existentes, resultado, ressalvas); provedores automáticos opcionais (`copilot`, `azure`, `openai`) se a TI disponibilizar API; busca híbrida (BM25 + embeddings locais) opcional |

### 6.2 Planejadas

- Consulta à memória institucional em linguagem natural, com resposta fundamentada e documentos citados.
- Integração com o SharePoint (sincronização automática da biblioteca).
- Catalogação assistida do acervo (status de validação humana de cada documento).
- Painel de indicadores em ambiente Microsoft 365.
- Autenticação institucional (hoje, token de acesso simples).

## 7. Princípios do produto

1. A decisão final pertence ao parecerista.
2. A IA é consultiva; toda sugestão deve ser validada.
3. Documentos institucionais têm prioridade sobre conhecimento externo.
4. Os precedentes da COGER têm maior peso interpretativo.
5. Nenhum documento da biblioteca é alterado automaticamente.
6. Nunca inventar fundamento: sem base no acervo, o sistema diz que não há base.

## 8. Fluxo de uso (visão do usuário)

```
1. Análise            Enviar o PDF -> o AICI mostra fatos, enquadramento, normativos,
                      precedentes, pareceres semelhantes e compromissos
2. Validação humana   O parecerista confere, ajusta atividade e conclusão e marca a revisão
   (opcional)         Copilot Chat: gera o prompt, leva ao chat, cola a resposta -> o AICI valida as fontes
3. Geração            Word do parecer / Termo de Compromisso / despacho,
                      ou preenchimento do gerador offline para edição fina
```

## 9. Métricas de sucesso

| Métrica | Meta | Como medir |
|---|---|---|
| Precisão dos precedentes | ≥ 80% | Avaliação do parecerista sobre os 4 primeiros resultados, em amostra de consultas reais |
| Classificação da atividade | ≥ 85% | Comparar a atividade sugerida com a escolhida/confirmada |
| Satisfação do parecerista | ≥ 4 em 5 | Pesquisa ao fim do piloto |
| Tempo de localização de precedentes | Redução > 50% | Tempo cronometrado com e sem o AICI |
| Pareceres sem validação humana | 0 | Bloqueio técnico e auditoria |

## 10. Restrições e conformidade

- Portaria RFB nº 647/2026 (política de IA): supervisão humana (art. 4º, I; art. 5º), IA somente homologada (art. 15), dados pessoais e sigilosos apenas se autorizados (art. 16), curador e acurácia para IA generativa (arts. 11 e 12), registros e auditoria (arts. 19 e 20). Ver o Documento 05.
- Copilot Chat: uso autorizado pelo CTSI (18/06/2026), inclusive com dados protegidos por sigilo legal, **condicionado à adoção integral dos controles da Análise de Riscos específica**; acessível pela conta corporativa da RFB e integrado ao Microsoft 365.
- LGPD e sigilo funcional: os pareceres e as consultas contêm dados pessoais e devem permanecer em ambiente institucional controlado.

## 11. Roadmap

| Etapa | Conteúdo |
|---|---|
| Agora | Piloto em estação/ambiente institucional, com o Copilot Chat em modo assistido (ou sem IA); obtenção da Análise de Riscos e confirmação do enquadramento do AICI com a Cotec |
| Próxima | Medição das metas com casos reais; busca semântica validada; avaliação de alternativas de integração (agente Copilot Studio, API) com a TI |
| Depois | Consulta em linguagem natural; integração com SharePoint e Microsoft 365; indicadores em painel |
| Longo prazo | Homologação institucional como sistema; evolução contínua da base e das regras da COGER |

## 12. Fora da visão

O AICI não decide, não assina, não substitui o juízo do parecerista e não altera a biblioteca por conta própria.
