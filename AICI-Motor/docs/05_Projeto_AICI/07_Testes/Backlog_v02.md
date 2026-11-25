# Backlog Priorizado - v02

**Versão 0.3 - novembro/2026.** Substitui a v01. Prioridade: P1 (necessário para o piloto), P2 (logo após o piloto), P3 (evolução). Itens dependentes da TI estão marcados.

## Concluído

| Item | Fase |
|---|---|
| Organizar acervo (pareceres por ano, precedentes por tema, normativos, modelos) | 1 |
| Consolidar normativos básicos (Lei nº 12.813/2013, Portaria Interministerial nº 333/2013, manuais e orientações da CGU, Port. RFB nº 647/2026) | 1 |
| Estruturar metadados e coluna `Status_IA` | 1 |
| Gerador de pareceres: 68 atividades, Termo de Compromisso, multiatividade, escolha da conclusão | 1 |
| Motor: PDF/OCR, fatos, BM25, normativos, precedentes, classificação, minuta, Word, indicadores | 2 |
| Busca híbrida (mecanismo) e backend Chroma opcional | 2 |
| Camada de provedores de IA e auditoria das chamadas | 2 |
| Modo assistido com o Copilot Chat; validação de fontes; limite do prompt | 2 |
| Validação humana obrigatória (tela e API) | 2 |
| Documentação do projeto (este conjunto) | - |

## Fase 1 - Pré-requisitos do piloto

| Prio. | Item | Dependência |
|---|---|---|
| P1 | Obter a Análise de Riscos do Copilot Chat e adotar os controles | **TI** |
| P1 | Confirmar o enquadramento do AICI (art. 10) | **TI** |
| P1 | Designar o curador e aprovar a acurácia aceitável | COGER / TI |
| P1 | Confirmar o limite de prompt do Copilot Chat e ajustar `limite_caracteres` | **TI** |
| P1 | Definir o ambiente de execução e instalar o motor | **TI** |
| P1 | Carregar o acervo real e verificar a vigência dos normativos | Concepção / Coordenação |
| P1 | Preencher `regras_coger.md` (seção "A consolidar pela COGER") | Coordenação |
| P2 | Agendar a atualização periódica da base de precedentes da CGU (`atualizar_precedentes.py --md`) e mostrar a data da última atualização na tela |
| P1 | Levar a conclusão por atividade do pedido ao motor Python e acrescentar "componentes" aos demais modelos que tratam de mais de uma atividade |
| P1 | Medir, no piloto, o ganho da etapa 1 do Copilot (precisão dos precedentes com e sem) e o tempo adicional |
| P2 | Levar a etapa 1 (entender o caso) ao motor Python, com a mesma validação |
| P1 | Medir a indexação da biblioteca real (686 itens) no modo local e ajustar (leitura em segundo plano, limite de páginas) |
| P1 | Testar o modo assistido com o Copilot Chat real e ajustar o prompt (`prompts/draft.txt`) | Concepção |
| P1 | Treinar os pareceristas do piloto | Concepção |
| P1 | Formulário de registro do piloto | Concepção |
| P1 | Catalogar os precedentes principais (status de validação por documento) | Coordenação |

## Fase 2 - Qualidade e uso

| Prio. | Item |
|---|---|
| P1 | Filtro explícito por tema, ano e resultado na busca de pareceres (RF002) |
| P1 | Medir classificação e precisão dos precedentes com casos reais; ajustar palavras-chave |
| P2 | Validar a busca híbrida com `bge-m3`/`multilingual-e5-large` no acervo real e medir ganho |
| P2 | Classificação assistida pelo Copilot no modo assistido (escolha entre as candidatas) |
| P2 | Revisão inteligente da minuta pelo Copilot (modo assistido), além das regras automáticas |
| P2 | Integrar o registro de status dos documentos (`Status_IA`) ao motor |
| P2 | Validar em Windows e Edge |
| P2 | Painel de indicadores (gráficos) e visualização da trilha de auditoria para o curador |

## Fase 3 - Inteligência e integração

| Prio. | Item |
|---|---|
| P2 | Consulta à memória institucional em linguagem natural (UC004), com a mesma validação de fontes |
| P2 | Sincronização automática com o SharePoint |
| P2 | Autenticação institucional, perfis e identificação do usuário nos registros |
| P3 | Avaliar com a TI: agente publicado (Copilot Studio) ou API, para eliminar o copiar e colar |
| P3 | Armazenamento institucional da trilha de auditoria, com proteção contra alteração |
| P3 | Migração do banco para PostgreSQL |
| P3 | Criptografia em repouso, retenção e descarte automáticos |
| P3 | Unificar a geração de Word (HTML e motor) em uma só implementação |

## Fase 4 - Homologação

| Prio. | Item |
|---|---|
| P2 | Teste de segurança e varredura de vulnerabilidades |
| P2 | Integração plena com o gerador de pareceres |
| P2 | Homologação institucional e inclusão no repositório de soluções de IA autorizadas |
| P3 | Operação contínua: monitoramento, suporte, atualização periódica da base |
