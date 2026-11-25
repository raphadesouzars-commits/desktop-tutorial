# Termo de Abertura do Projeto (TAP)

## Assistente Inteligente para Conflitos de Interesse (AICI)

| Campo | Conteúdo |
|---|---|
| Projeto | AICI - Assistente Inteligente para Conflitos de Interesse |
| Versão do documento | 0.2 - rascunho para análise da Cotec/TI (novembro/2026) |
| Patrocinador | COGER - Corregedoria da Receita Federal |
| Unidade demandante | Coordenação responsável pelos pareceres de conflito de interesses (Coger/GNP - Grupo Nacional dos Pareceristas) |
| Responsável pela concepção | Raphael Albuquerque de Souza |
| Gerente do projeto | [a designar] |
| Curador da solução de IA generativa | [a designar - exigência do art. 11 da Portaria RFB nº 647/2026] |
| Ponto focal da TI | [a designar pela Cotec] |
| Situação | Protótipo funcional (motor + gerador) concluído; aguardando definição de IA homologada, ambiente e enquadramento na governança de IA |

---

## 1. Contexto e justificativa

A COGER analisa consultas e pedidos de autorização para o exercício de atividade privada formulados pelos servidores por meio do SeCI (Sistema Eletrônico de Prevenção de Conflito de Interesses da CGU), nos termos da Lei nº 12.813/2013, da Portaria Interministerial MP/CGU nº 333/2013 e da Portaria SE/ME nº 15.966/2020.

O conhecimento necessário à análise está disperso em centenas de pareceres emitidos (hoje organizados na biblioteca da COGER por ano e por tema), em precedentes da CGU, em normativos e em modelos de redação. A pesquisa manual de precedentes, a repetição de fundamentos e a uniformização de entendimentos consomem tempo do parecerista e dependem da memória individual.

O projeto transforma esse acervo em uma **memória institucional pesquisável**, usada para apoiar - nunca substituir - o parecerista.

## 2. Finalidade

Desenvolver solução institucional de apoio à análise de conflitos de interesse utilizando técnicas de Inteligência Artificial compatíveis com a política de IA da Receita Federal (Portaria RFB nº 647/2026).

## 3. Objetivos

### 3.1 Objetivos estratégicos

1. Preservar a memória institucional.
2. Uniformizar entendimentos.
3. Reduzir o tempo de elaboração dos pareceres.
4. Melhorar a recuperação de precedentes.
5. Aumentar a consistência das análises.
6. Apoiar a formação de novos pareceristas.

### 3.2 Objetivos específicos (mensuráveis)

| Objetivo | Indicador | Meta inicial |
|---|---|---|
| Recuperar precedentes úteis | Precisão dos precedentes apresentados (avaliada pelo parecerista) | ≥ 80% |
| Enquadrar a atividade | Acerto da classificação sugerida | ≥ 85% |
| Reduzir esforço de pesquisa | Redução do tempo de localização de precedentes frente à pesquisa manual | > 50% |
| Aceitação | Satisfação do parecerista | ≥ 4 em 5 |
| Segurança de uso | Pareceres emitidos sem revisão humana | 0 (bloqueio técnico) |

As metas são hipóteses de partida e devem ser confirmadas pela área de negócio como "nível de acurácia aceitável" (Portaria RFB nº 647/2026, art. 11).

## 4. Benefícios esperados

- Redução do esforço de pesquisa.
- Reaproveitamento do conhecimento acumulado.
- Ganho de produtividade.
- Maior padronização de linguagem e de entendimentos.
- Apoio à tomada de decisão, com rastreabilidade de fontes.
- Indicadores gerenciais sobre atividades consultadas e resultados (temas recorrentes, precedentes mais usados).

## 5. Escopo

### 5.1 Dentro do escopo

1. Leitura do PDF da consulta do SeCI (com OCR para PDF digitalizado) e extração dos fatos.
2. Base de conhecimento: pareceres, precedentes, normativos, modelos institucionais e regras da COGER.
3. Busca de precedentes e de normativos (lexical e, opcionalmente, semântica).
4. Classificação da atividade entre as categorias já adotadas pela COGER (68 atividades, 163 situações modeladas).
5. Minuta de parecer na estrutura institucional (I - Relatório, II - Fundamentos, III - Conclusão), com a origem de cada parágrafo.
6. Documentos Word editáveis: parecer, Termo de Compromisso e despacho.
7. Revisão de consistência da minuta.
8. Indicadores gerenciais e trilha de auditoria.
9. Camada de IA substituível (provedor homologado a definir), com funcionamento integral também **sem** IA.

### 5.2 Fora do escopo (nesta fase)

- Decisão automática sobre conflito de interesses ou assinatura de pareceres.
- Alteração automática de documentos da biblioteca pela IA.
- Treinamento ou ajuste fino (fine-tuning) de modelos.
- Integração direta com o SeCI (a entrada é o PDF emitido pelo sistema).
- Atendimento a outros temas da Corregedoria além de conflito de interesses.

## 6. Entregas já realizadas (situação em novembro/2026)

| Entrega | Situação |
|---|---|
| Gerador de pareceres (HTML, funciona offline) - 68 atividades, 163 situações, múltiplas atividades, Termo de Compromisso, leitura do formulário SeCI em PDF | Concluído |
| Biblioteca da COGER reorganizada (pareceres por ano, precedentes por tema, normativos, modelos) com planilha de metadados | Concluído |
| Normativos básicos na biblioteca (Lei nº 12.813/2013, Portaria Interministerial nº 333/2013, manuais e orientações da CGU, Portaria RFB nº 647/2026) | Concluído (faltam itens pendentes, ver Documento 04) |
| Motor AICI (Python/FastAPI): leitura de PDF, extração de fatos, recuperação, classificação, minuta, DOCX, indicadores, auditoria | Concluído em protótipo (testes automatizados) |
| Aba "Análise Inteligente" no gerador, com validação humana obrigatória | Concluído |
| Documentação inicial (este conjunto) | Em elaboração |
| Integração com IA homologada | **Pendente de definição pela TI** |
| Implantação em ambiente institucional e piloto | Pendente |

## 7. Premissas

1. O gerador atual continua sendo usado normalmente durante todo o projeto (evolução incremental, sem interrupção do processo).
2. A decisão final e o ato administrativo permanecem com o parecerista (art. 5º, parágrafo único, da Portaria RFB nº 647/2026).
3. A biblioteca da COGER (SharePoint) será a fonte da base de conhecimento.
4. A TI informará se existe forma homologada de acesso programático a IA generativa e em quais condições.

## 8. Restrições

1. Uso exclusivo de IA desenvolvida, contratada ou homologada pela RFB, em ambiente seguro (art. 15 da Portaria RFB nº 647/2026).
2. Inserção de dados pessoais ou sigilosos em solução de IA somente se expressamente autorizada (art. 16). Os pareceres e as consultas contêm dados pessoais.
3. Casos de uso de IA devem ser submetidos previamente à Cotec (art. 10) e, por ser IA generativa, exigem curador, nível de acurácia aceitável e monitoramento contínuo (art. 11).
4. Preferência por ambientes sob governança técnica da RFB e avaliação da Cotec para modelos externos ou não soberanos (art. 14).
5. Desenvolvimento aderente ao processo de desenvolvimento interno de sistemas institucionais da Cotec (Portaria RFB/Sucor/Cotec nº 41/2017), a confirmar.

## 9. Partes interessadas

| Parte | Interesse / papel |
|---|---|
| COGER (patrocinador) | Patrocínio, priorização, decisões de negócio |
| Pareceristas da Coger/GNP | Usuários principais; validam sugestões; avaliam a qualidade |
| Coordenação do Grupo Nacional dos Pareceristas | Aprova entendimentos consolidados e conteúdo de `regras_coger.md` |
| Cotec (TI) | Governança tecnológica de IA, ambiente, segurança, homologação |
| CTSI | Deliberação sobre o caso de uso de IA |
| Segurança da informação e proteção de dados | Parecer sobre tratamento de dados pessoais e sigilosos |
| Comissão de Ética da RFB | Destinatária dos pareceres e Termos de Compromisso |

## 10. Riscos iniciais

| # | Risco | Prob. | Impacto | Resposta |
|---|---|---|---|---|
| R1 | Não haver IA homologada acessível por API | Média | Médio | Operar em modo sem IA (já funcional); tratar IA como camada opcional |
| R2 | Restrição ao envio de dados pessoais/sigilosos à IA (art. 16) | Alta | Alto | Mascaramento antes do envio; solicitar autorização expressa; ambiente institucional/soberano |
| R3 | IA sugerir fundamento inexistente (alucinação) | Média | Alto | Contexto restrito ao acervo, fontes obrigatórias, descarte de parágrafo sem fonte, revisão humana obrigatória, curador |
| R4 | Qualidade da busca insuficiente sem busca semântica | Média | Médio | Busca híbrida com embeddings locais; medir com casos reais |
| R5 | Acervo desatualizado ou com entendimentos divergentes | Média | Alto | Governança da biblioteca (status "Validado_Humano"), prioridade para precedentes recentes e para as regras da COGER |
| R6 | Dependência de uma pessoa (concepção e manutenção) | Média | Médio | Documentação, testes automatizados, conhecimento em arquivos (não em código), ponto focal da TI |
| R7 | Dados pessoais do acervo expostos por falha de controle de acesso | Baixa | Alto | Execução em ambiente institucional, autenticação, dados fora do controle de versão, parecer de segurança |
| R8 | Excesso de confiança do usuário nas sugestões | Média | Alto | Validação humana obrigatória (bloqueio técnico), avisos de baixa confiança, treinamento (art. 22) |
| R9 | Demora da governança de IA atrasar o piloto | Alta | Médio | Piloto sem IA, em estação institucional, enquanto tramita a submissão à Cotec |

## 11. Abordagem e fases

| Fase | Conteúdo | Situação |
|---|---|---|
| 0 - Preparação | Organizar acervo, consolidar normativos, estruturar metadados | Concluída |
| 1 - Protótipo | Motor sem IA, gerador, aba de análise, testes | Concluída |
| 2 - Governança e ambiente | Submissão à Cotec/CTSI, definição de IA, ambiente, parecer de segurança, curador | Em andamento (depende da TI) |
| 3 - Piloto | Grupo restrito de pareceristas, casos reais, medição das metas | Pendente |
| 4 - Inteligência adicional | Busca semântica, classificação assistida, consulta em linguagem natural | Parcial (busca semântica implementada, não validada) |
| 5 - Integração e homologação | Integração plena com o gerador, homologação institucional | Pendente |

Prazos e esforço serão definidos com a Cotec após a Fase 2.

## 12. Critérios de sucesso e de encerramento do piloto

1. Metas do item 3.2 atingidas em amostra representativa de consultas reais.
2. Nenhum incidente de segurança ou de vazamento de dados pessoais.
3. Todas as sugestões rastreáveis até a fonte; nenhum parecer gerado sem validação humana.
4. Aprovação do curador e da Cotec para a continuidade.

## 13. Normas e referências

- Lei nº 12.813/2013 (conflito de interesses) e Portaria Interministerial MP/CGU nº 333/2013.
- Lei nº 8.112/1990, art. 117 (vedações).
- Portaria SE/ME nº 15.966/2020 (procedimentos no âmbito do MF).
- Portaria RFB nº 647/2026 - Política de Inteligência Artificial da RFB.
- Portaria RFB/Sucor/Cotec nº 41/2017 - desenvolvimento e manutenção de sistemas institucionais (Modelo de Desenvolvimento Interno).
- Portaria Normativa CGU nº 234/2025 (revoga a Portaria CGU nº 57/2019).
- Manual de Tratamento de Conflito de Interesses (CGU, 2022) e demais orientações da CGU.

## 14. Aprovações

| Papel | Nome | Data | Assinatura |
|---|---|---|---|
| Patrocinador (COGER) | | | |
| Responsável pela concepção | Raphael Albuquerque de Souza | | |
| Representante da Cotec | | | |
| Curador da solução | | | |
