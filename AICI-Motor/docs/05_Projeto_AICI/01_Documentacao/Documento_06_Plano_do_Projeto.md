# Plano do Projeto

**AICI - Assistente Inteligente para Conflitos de Interesse - Versão 0.3 - novembro/2026**

Prazos e esforço serão fixados com a Cotec e o patrocinador após a Fase 2; este plano define a estrutura, os marcos e os critérios.

## 1. Estrutura Analítica do Projeto (EAP)

| # | Pacote de trabalho | Entregas | Situação |
|---|---|---|---|
| 1 | **Gerenciamento** | TAP, plano, riscos, comunicação, atas | Em andamento |
| 2 | **Biblioteca e conhecimento** | Acervo organizado (pareceres por ano, precedentes por tema, normativos, modelos); metadados; `regras_coger.md` | Concluído (acervo); contínuo (governança) |
| 3 | **Gerador de pareceres (HTML)** | 68 atividades/163 situações, Termo, multiatividade, leitura de PDF | Concluído; contínuo |
| 4 | **Motor AICI** | Leitura de PDF/OCR, fatos, recuperação, classificação, minuta, Word, indicadores, auditoria | Concluído (protótipo) |
| 5 | **IA - Copilot Chat** | Modo assistido, validação de resposta, auditoria | Concluído (protótipo); validar com o Copilot real |
| 6 | **Governança de IA** | Enquadramento (art. 10), Análise de Riscos, curador, acurácia, canal de ocorrências | Pendente (TI/CTSI/COGER) |
| 7 | **Infraestrutura e segurança** | Ambiente, HTTPS/autenticação, retenção, criptografia, parecer de segurança | Pendente (TI) |
| 8 | **Testes e qualidade** | Testes automatizados; protocolo de medição das metas; piloto | Parcial |
| 9 | **Implantação e capacitação** | Piloto, treinamento, manual, suporte, operação | Pendente |
| 10 | **Evolução** | Busca semântica validada, consulta em linguagem natural, SharePoint, painel | Planejado |

## 2. Marcos e critérios de aceite

| Marco | Critério | Responsável |
|---|---|---|
| M1 - Protótipo concluído | Fluxo completo com testes automatizados passando | Concepção (concluído) |
| M2 - Governança esclarecida | Enquadramento do AICI confirmado; Análise de Riscos recebida; curador designado; acurácia aprovada | Cotec / COGER |
| M3 - Ambiente pronto | Serviço em execução em ambiente institucional, com HTTPS, autenticação e biblioteca sincronizada | Cotec |
| M4 - Piloto iniciado | Grupo de pareceristas treinado; protocolo de medição aprovado | COGER |
| M5 - Piloto concluído | Metas medidas (Documento Plano de Testes); relatório do curador | COGER / Curador |
| M6 - Decisão de expansão | Cotec e COGER decidem continuar, ajustar ou encerrar | Patrocinador |

## 3. Papéis e responsabilidades (RACI)

R = executa, A = responde, C = consultado, I = informado.

| Atividade | Concepção | Coordenação GNP | Pareceristas | Cotec/TI | Curador | CTSI |
|---|---|---|---|---|---|---|
| Requisitos e regras de negócio | R | A | C | C | I | - |
| Manutenção da biblioteca | C | A | R | I | I | - |
| Validação de entendimentos novos (`regras_coger.md`) | C | A/R | C | - | I | - |
| Desenvolvimento do motor e do gerador | A/R | I | C | C | I | - |
| Enquadramento e Análise de Riscos | C | C | - | A/R | C | I |
| Ambiente e segurança | C | I | - | A/R | I | - |
| Acurácia aceitável | C | A | R | C | R | I |
| Monitoramento da IA | I | C | C | C | A/R | I |
| Piloto e medição | R | A | R | C | R | I |
| Capacitação | R | A | I | C | C | - |

## 4. Plano de comunicação

| O quê | Para quem | Quando | Meio |
|---|---|---|---|
| Situação do projeto | Patrocinador e Coordenação | Mensal | Relatório curto |
| Pendências com a TI | Cotec (ponto focal) | Conforme resposta aos itens do Documento 04 | E-mail / reunião |
| Resultado do piloto | Patrocinador, Cotec, CTSI | Ao fim do piloto | Relatório e apresentação |
| Orientação de uso | Pareceristas | Antes do piloto e a cada mudança relevante | Treinamento + Manual do Usuário |
| Ocorrências de IA | Canal oficial da Cotec | Imediato | Canal a divulgar pela Cotec |

Atas de reunião seguem o modelo `ATA_PADRAO`.

## 5. Gestão de mudanças e versões

- Código e documentação versionados em repositório; testes automatizados antes de cada entrega.
- Mudanças em modelos de atividade: alterar o gerador HTML, regenerar e exportar as categorias (`scripts/exportar_categorias.py`), executar os testes.
- Mudanças em `regras_coger.md` (seção manual), `prompts/` e `templates/institucional.json` passam pela Coordenação.
- Mudanças na API são registradas no Backlog e comunicadas ao gerador.

## 6. Gestão da qualidade

- Metas de acurácia propostas (Termo de Abertura, item 3.2), a aprovar pela COGER.
- Protocolo de medição no Plano de Testes (Documento 07_Testes).
- Auditoria da IA pelo curador (trilha `ia_auditoria.jsonl`).
- Revisão humana obrigatória de todo parecer.

## 7. Capacitação (art. 22 da Portaria RFB nº 647/2026)

| Público | Conteúdo | Quando |
|---|---|---|
| Pareceristas | Uso do AICI em três etapas; uso seguro do Copilot Chat (somente conta corporativa); revisão de sugestões; reconhecer alucinação e viés; como comunicar ocorrências | Antes do piloto |
| Curador | Trilha de auditoria; avaliação de qualidade; registro de evidências | Antes do piloto |
| Coordenação | Governança da base e das regras da COGER; indicadores | Antes do piloto |
| TI | Instalação, configuração, operação, monitoramento | Na implantação |

## 8. Premissas, restrições e riscos

Ver Termo de Abertura (itens 7, 8 e 10) e Documento 07 (Análise de Riscos e Controles).

## 9. Orçamento

Desenvolvimento interno, sem contratação prevista. Custos de infraestrutura e licenças (Copilot Chat já disponível aos usuários E5) a informar pela Cotec.
