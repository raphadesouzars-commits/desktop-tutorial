# Plano de Testes - v02

**Versão 0.3 - novembro/2026.** Substitui a v01. Resultados dos testes automatizados: `Resultados_dos_Testes_Automatizados.md`.

## 1. Objetivo

Validar a qualidade técnica do AICI e a qualidade das respostas (precisão dos precedentes, acerto da classificação, utilidade da minuta), em três níveis: testes automatizados (técnicos), verificações no navegador e **piloto com casos reais** (qualidade).

## 2. Níveis de teste

| Nível | O que cobre | Quem executa | Situação |
|---|---|---|---|
| Automatizado | Leitura de PDF, extração de fatos, indexação, recuperação, classificação, contexto e provedores de IA, modo assistido, API, geração de Word, segurança básica | Desenvolvimento (`python -m pytest -q`) | 22 testes passando |
| Verificação no navegador | Aba "Análise Inteligente" ponta a ponta contra o motor real (upload, decisão, Word, Copilot assistido, indicadores) e o gerador offline | Desenvolvimento (Chromium) | Realizada |
| Aceitação (piloto) | Qualidade das respostas com consultas reais | Pareceristas, Coordenação, Curador | **Pendente** |
| Segurança | Varredura de vulnerabilidades e teste de intrusão | TI | **Pendente** |
| Ambiente institucional | Instalação e execução em Windows/Edge e no servidor da RFB | TI | **Pendente** |

## 3. Cenários de aceitação (piloto)

Para cada cenário: entrada, resultado esperado e critério.

| # | Cenário | Entrada | Resultado esperado | Critério |
|---|---|---|---|---|
| C1 | Docência em instituição privada | Consulta de servidor para lecionar em curso superior privado | Recupera precedentes de docência/magistério; enquadra em magistério; sugere ressalvas de horário e informação privilegiada | Atividade correta; ≥ 3 de 4 precedentes aplicáveis |
| C2 | Participação em conselho de administração | Consulta para integrar conselho de administração de empresa privada | Aponta os principais riscos (art. 5º, II e III, da Lei nº 12.813/2013) e precedentes de conselhos | Riscos apontados; conclusão coerente com a base |
| C3 | Síndico de condomínio | Consulta para ser síndico do próprio condomínio | Apresenta os compromissos normalmente utilizados; Termo de Compromisso | Compromissos corretos; Termo gerado |
| C4 | Advocacia | Consulta de servidor que pretende advogar | Identifica o conflito potencial e as vedações aplicáveis | Conflito identificado; encaminhamento correto |
| C5 | Atividade de comércio/afiliado digital | Pedido para vender produtos digitais por plataforma | Reconhece a questão do exercício de comércio (art. 117, X, da Lei nº 8.112/1990) | Fundamentação cita o dispositivo correto |
| C6 | Várias atividades no mesmo pedido | Pedido com 2 ou 3 atividades | Conclusão única agrupada; fundamentos por atividade | Coerência da conclusão |
| C7 | Atividade fora das categorias | Atividade incomum | Usa o modelo genérico com baixa confiança e avisa | Aviso presente; nada inventado |
| C8 | PDF digitalizado | PDF sem texto | Aviso (ou OCR, se instalado) | Sem falha; mensagem clara |
| C9 | Conclusão divergente do modelo | Parecerista troca a conclusão sugerida | Conclusão e ementa mudam; aviso para revisar os fundamentos | Aviso presente |
| C10 | Resposta do Copilot com fonte inventada | Colar resposta com marcador inexistente | Parágrafo descartado; aviso | Nenhum fundamento sem origem na minuta |
| C11 | Resposta do Copilot fora do formato | Colar texto sem JSON | Recusa com orientação | Mensagem clara |
| C12 | Tentativa de gerar sem revisão | Chamar a geração sem validação | Recusada (HTTP 422) | Bloqueio na tela e na API |

## 4. Protocolo de medição

| Métrica | Amostra | Procedimento | Meta |
|---|---|---|---|
| Classificação | Todas as consultas do piloto (sugestão: ≥ 30) | Comparar a 1ª candidata com a atividade confirmada | ≥ 85% |
| Precisão dos precedentes | Idem | O parecerista marca os aplicáveis entre os 4 primeiros | ≥ 80% |
| Tempo de localização | Subamostra pareada | Cronometrar com e sem o AICI | Redução > 50% |
| Satisfação | Todos os pareceristas | Questionário 1 a 5 | ≥ 4 |
| Fundamentação do Copilot | Casos com o modo assistido | % aproveitado / descartado; alucinações | Registrar |

Casos-teste devem usar consultas reais **tratadas conforme a política de dados**; consultas sintéticas servem apenas para testes técnicos.

## 5. Critérios de entrada e saída

- **Entrada:** pré-requisitos do Plano de Implantação (Documento 10, item 2) atendidos e testes automatizados passando.
- **Saída:** metas medidas e relatadas ao patrocinador, à Cotec e ao curador; incidentes tratados.

## 6. Ambiente de teste

- Automatizado: qualquer máquina com Python 3.12+ e `requirements.txt`; os testes usam arquivos temporários e dados sintéticos (não usam o acervo real).
- Piloto: ambiente institucional definido pela Cotec.

## 7. Riscos dos testes

Amostra pequena ou enviesada; consultas reais com dados pessoais (tratar conforme a política); resposta do Copilot variar entre execuções (registrar a versão e a data).
