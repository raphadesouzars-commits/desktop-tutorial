# Manual Teórico-Prático da Calculadora de Multa PAR
## Corregedoria da Receita Federal do Brasil

---

## Sumário

1. [Introdução e Finalidade](#1-introdução-e-finalidade)
2. [Fundamento Legal](#2-fundamento-legal)
3. [Estrutura Geral da Calculadora](#3-estrutura-geral-da-calculadora)
4. [Etapa 0 — Base de Cálculo: Faturamento Bruto](#4-etapa-0--base-de-cálculo-faturamento-bruto)
5. [Etapa 1 — Vantagens Auferida e Pretendida](#5-etapa-1--vantagens-auferida-e-pretendida)
6. [Etapa 2 — Agravante: Concurso de Atos Lesivos (Art. 22, I)](#6-etapa-2--agravante-concurso-de-atos-lesivos-art-22-i)
7. [Etapa 3 — Agravante: Ciência/Tolerância Hierárquica (Art. 22, II)](#7-etapa-3--agravante-ciênciatolerância-hierárquica-art-22-ii)
8. [Etapa 4 — Agravante: Interrupção e Descumprimento (Art. 22, III)](#8-etapa-4--agravante-interrupção-e-descumprimento-art-22-iii)
9. [Etapa 5 — Agravante: Situação Econômica do Infrator (Art. 22, IV)](#9-etapa-5--agravante-situação-econômica-do-infrator-art-22-iv)
10. [Etapa 6 — Agravante: Reincidência (Art. 22, V)](#10-etapa-6--agravante-reincidência-art-22-v)
11. [Etapa 7 — Agravante: Valor dos Contratos com o Ente Lesado (Art. 22, VI)](#11-etapa-7--agravante-valor-dos-contratos-com-o-ente-lesado-art-22-vi)
12. [Etapa 8 — Atenuante: Não Consumação (Art. 23, I)](#12-etapa-8--atenuante-não-consumação-art-23-i)
13. [Etapa 9 — Atenuante: Ressarcimento e Devolução (Art. 23, II)](#13-etapa-9--atenuante-ressarcimento-e-devolução-art-23-ii)
14. [Etapa 10 — Atenuante: Colaboração (Art. 23, III)](#14-etapa-10--atenuante-colaboração-art-23-iii)
15. [Etapa 11 — Atenuante: Admissão Voluntária (Art. 23, IV)](#15-etapa-11--atenuante-admissão-voluntária-art-23-iv)
16. [Etapa 12 — Atenuante: Programa de Integridade (Art. 23, V)](#16-etapa-12--atenuante-programa-de-integridade-art-23-v)
17. [Etapa 13 — Publicação Extraordinária (Art. 6º, II, Lei nº 12.846/2013)](#17-etapa-13--publicação-extraordinária-art-6º-ii-lei-nº-128462013)
18. [Cálculo Final e Verificação dos Limites Legais (Art. 25)](#18-cálculo-final-e-verificação-dos-limites-legais-art-25)
19. [Relatório Final e Impressão](#19-relatório-final-e-impressão)
20. [Fluxo Resumido do Cálculo](#20-fluxo-resumido-do-cálculo)
21. [Perguntas Frequentes e Pontos de Atenção](#21-perguntas-frequentes-e-pontos-de-atenção)

---

## 1. Introdução e Finalidade

A **Calculadora de Multa PAR** é uma ferramenta de apoio à decisão desenvolvida pela Corregedoria da Receita Federal do Brasil para uso nos Processos Administrativos de Responsabilização (PAR) instaurados com base na Lei Anticorrupção (Lei nº 12.846/2013) e seu decreto regulamentador (Decreto nº 11.129/2022).

A ferramenta tem como objetivos:

- **Padronizar** a dosimetria das sanções pecuniárias aplicadas às pessoas jurídicas;
- **Transparência** — cada percentual aplicado está vinculado a um dispositivo legal específico;
- **Rastreabilidade** — o relatório final gerado documenta todos os parâmetros utilizados, servindo como instrumento de instrução processual;
- **Reduzir erros** de cálculo, especialmente nas interações entre os limites mínimo, máximo, vantagem auferida e alíquota preliminar.

A calculadora funciona integralmente **offline** (não depende de servidores externos), sendo adequada para uso em ambientes com restrições de conectividade.

---

## 2. Fundamento Legal

### Lei nº 12.846/2013 — Lei Anticorrupção (LAC)

| Dispositivo | Conteúdo |
|---|---|
| Art. 5º | Tipificação dos atos lesivos à administração pública |
| Art. 6º, I | Multa de 0,1% a 20% do faturamento bruto |
| Art. 6º, II | Publicação extraordinária da decisão condenatória |

### Decreto nº 11.129/2022

| Dispositivo | Conteúdo |
|---|---|
| Art. 20 | Base de cálculo: faturamento bruto do último exercício anterior ao PAR |
| Art. 21 | Hipótese subsidiária: ausência de faturamento no exercício anterior |
| Art. 22 | Fatores agravantes (I a VI) |
| Art. 23 | Fatores atenuantes (I a V) |
| Art. 24 | Publicação extraordinária e critérios de prazo |
| Art. 25 | Limites mínimo e máximo da multa |
| Art. 26 | Métodos de apuração da vantagem auferida (I a III) |

### Orientações complementares

- **IN CGU nº 1/2015** — metodologia de avaliação do programa de integridade;
- **Guia CGU de Responsabilização de Pessoas Jurídicas** — parâmetros interpretativos e tabelas de referência;
- **Tabela 5 do Guia CGU** — escalonamento dos percentuais de ressarcimento (Art. 23, II).

---

## 3. Estrutura Geral da Calculadora

A calculadora é organizada em **14 etapas sequenciais** (Steps 0 a 13), agrupadas em três blocos funcionais:

```
┌──────────────────────────────────────────────────────┐
│  BLOCO A — BASE DE CÁLCULO                           │
│  Etapa 0: Faturamento Bruto                          │
│  Etapa 1: Vantagens Auferida e Pretendida            │
├──────────────────────────────────────────────────────┤
│  BLOCO B — DOSIMETRIA (AGRAVANTES E ATENUANTES)      │
│  Etapas 2–7:  Agravantes (Art. 22, I a VI)           │
│  Etapas 8–12: Atenuantes (Art. 23, I a V)            │
├──────────────────────────────────────────────────────┤
│  BLOCO C — RESULTADO                                 │
│  Etapa 13: Publicação Extraordinária                 │
│  Resultado Final + Verificação dos Limites (Art. 25) │
└──────────────────────────────────────────────────────┘
```

A navegação é feita pelos botões **"Próximo →"** e **"← Anterior"** em cada etapa. O sistema calcula e exibe o resultado automaticamente ao final da Etapa 13.

---

## 4. Etapa 0 — Base de Cálculo: Faturamento Bruto

### Fundamento

> **Art. 20 do Decreto nº 11.129/2022.** A multa prevista no inciso I do *caput* do art. 6º da Lei nº 12.846/2013 terá como base de cálculo o **faturamento bruto da pessoa jurídica no último exercício anterior ao da instauração do PAR**, excluídos os tributos.

> **Art. 21.** Caso a pessoa jurídica comprovadamente não tenha tido faturamento no último exercício anterior ao da instauração do PAR, deve-se considerar como base de cálculo da multa o valor do **último faturamento bruto apurado** pela pessoa jurídica, excluídos os tributos incidentes sobre vendas, que terá seu valor atualizado pelo IPCA até o último dia do exercício anterior ao da instauração do PAR.

### Campos da etapa

| Campo | Descrição |
|---|---|
| **Ano de Instauração do PAR** | Ano em que o PAR foi formalmente instaurado |
| **Exercício de Referência do Faturamento** | Calculado automaticamente (Ano PAR − 1). Editável manualmente para casos especiais |
| **Faturamento Bruto Ajustado (R$)** | Valor final que será utilizado como base de cálculo |

### Fluxo de decisão

```
A PJ teve faturamento no exercício anterior ao PAR?
│
├─ SIM → Informar faturamento do exercício de referência
│        (via calculadora DRE, Simples Nacional ou valor direto)
│
└─ NÃO → Informar o último faturamento bruto apurado,
          já atualizado pelo IPCA até o último dia do
          exercício anterior ao PAR (Art. 21)
```

> **Atenção:** Como a calculadora funciona offline, a **atualização pelo IPCA** deve ser realizada previamente, utilizando a **Calculadora do Cidadão (BCB/IPCA)** disponível no site do Banco Central do Brasil. Informe o valor já corrigido no campo correspondente.

### Modos de apuração do faturamento (calculadora integrada)

A calculadora integrada oferece três formas de apurar o faturamento bruto:

1. **DRE (Regime Geral/RFB):** Receita Bruta de Vendas − Tributos sobre Vendas (conforme art. 20, *caput*);
2. **Simples Nacional (ME ou EPP):** conforme LC nº 123/2006, art. 3º, §1º — receita bruta total apurada nas declarações do Simples;
3. **Estimativa pela autoridade (art. 20, §1º, III):** hipótese residual, quando não há dados contábeis disponíveis — a autoridade apura o faturamento com base em outros elementos.

> Quando não houver faturamento no exercício anterior, utiliza-se o **último faturamento bruto apurado** (Art. 21), atualizado pelo IPCA.

---

## 5. Etapa 1 — Vantagens Auferida e Pretendida

### Fundamento

> **Art. 25 c/c Art. 26 do Decreto nº 11.129/2022.**

A lei distingue duas figuras jurídicas distintas com funções específicas na dosimetria:

| Conceito | Definição | Função na multa |
|---|---|---|
| **Vantagem Auferida** | Ganho real e efetivamente obtido com o ato lesivo | **Piso mínimo inafastável** — a multa não pode ser inferior à vantagem auferida (Art. 25, I) |
| **Vantagem Pretendida** | Ganho planejado/visado, ainda que não concretizado | Utilizada para o cálculo do **teto máximo** — o limite superior considera o maior valor entre a vantagem auferida e a pretendida (Art. 25, II) |

> **Atenção crítica:** Não confundir as duas figuras. Inflar o piso com a vantagem pretendida é erro metodológico. A calculadora trata cada valor na sua função legal correta.

### Métodos de apuração da Vantagem Auferida

A calculadora oferece quatro modos de apuração:

#### Modo DIRETO
Informar o valor já apurado externamente, ou zero (quando a vantagem não é estimável).

#### Art. 26, I — Diferença entre receita e custos lícitos
Método aplicável quando há receita auferida indevidamente (ex.: contratos administrativos obtidos por meio ilícito).

```
Vantagem = Receita Auferida − CMV/CSP − Despesas Lícitas − IRPJ/CSLL
```

Suporta múltiplos exercícios (multi-anos) com tratamento de prejuízos acumulados.

#### Art. 26, II — Custos e despesas não suportados
Valor correspondente aos custos e despesas que a pessoa jurídica deixou de suportar em razão do ilícito. Exemplos: tributos não recolhidos, multas regulatórias evitadas, encargos não pagos.

#### Art. 26, III — Acréscimo patrimonial por ação/omissão do Poder Público
Acréscimo patrimonial que não teria ocorrido sem o ato lesivo. Exemplos: diferencial de taxa de juros subsidiada obtida indevidamente, uso de informação privilegiada, exploração indevida de atividade.

---

## 6. Etapa 2 — Agravante: Concurso de Atos Lesivos (Art. 22, I)

### Fundamento
Agravante pelo **concurso de atos lesivos**, apurado pelo cruzamento entre:
- **Linhas:** quantidade de **condutas ilícitas** praticadas;
- **Colunas:** número de **espécies distintas** de atos lesivos do art. 5º da LAC.

### Tabela de percentuais

| Condutas ↓ / Espécies → | 1 espécie | 2 espécies | 3 espécies | 4 ou mais |
|---|---|---|---|---|
| 1 conduta (ato isolado) | — | 0,5% | 1,0% | 1,5% |
| 2 condutas | 0,5% | 1,0% | 1,5% | 2,0% |
| 3 condutas | 1,0% | 1,5% | 2,0% | 2,5% |
| 4 condutas | 1,5% | 2,0% | 2,5% | 3,0% |
| 5 condutas | 2,0% | 2,5% | 3,0% | 3,5% |
| 6 condutas | 2,5% | 3,0% | 3,5% | 4,0% |
| 7 ou mais condutas | 3,0% | 3,5% | 4,0% | 4,0% |

> **Nota:** A célula "1 conduta / 1 espécie" é tecnicamente inaplicável como agravante (não há concurso), portanto marcada como "—".

### Como preencher
Selecione na matriz a célula correspondente ao caso concreto. O sistema registra automaticamente o percentual da célula selecionada.

---

## 7. Etapa 3 — Agravante: Ciência/Tolerância Hierárquica (Art. 22, II)

### Fundamento
Agravante pela **tolerância ou ciência do corpo diretivo ou gerencial** em relação ao ato lesivo. O percentual varia conforme a posição hierárquica do agente com conhecimento/tolerância, medida a partir do topo da estrutura.

### Tabela de percentuais

| Nível hierárquico | % |
|---|---|
| Ausência de conhecimento do ilícito pelo corpo diretivo e gerencial | 0% |
| Tolerância/ciência do 5º nível hierárquico abaixo dos administradores | 1,0% |
| Tolerância/ciência do 4º nível hierárquico abaixo dos administradores | 1,5% |
| Tolerância/ciência do 3º nível hierárquico abaixo dos administradores | 2,0% |
| Tolerância/ciência do 2º nível hierárquico (imediatamente abaixo) | 2,5% |
| Tolerância/ciência dos sócios, acionistas ou administradores | 3,0% |

> Quanto mais próximo do topo da estrutura estiver o agente com ciência/tolerância, maior o agravante.

---

## 8. Etapa 4 — Agravante: Interrupção e Descumprimento (Art. 22, III)

### Fundamento
O Art. 22, III contempla **três hipóteses distintas**. A calculadora avalia cada uma em abas separadas e aplica automaticamente o **maior percentual** entre as três.

### Aba a) Interrupção no Fornecimento de Serviço Público

| Situação | % |
|---|---|
| Ausência de interrupção | 0% |
| Até 1 semana ou vila/povoado | 1,0% |
| Até 2 semanas ou cidade até 500 mil hab. | 2,0% |
| Até 3 semanas ou cidade com +500 mil hab./Estado | 3,0% |
| Mais de 4 semanas ou 2 ou mais Estados | 4,0% |

### Aba b) Interrupção na Execução de Obra Contratada

Matriz bidimensional: **período de interrupção** (linhas) × **percentual residual da obra** (colunas):

| Período ↓ / Residual → | < 10% | Até 30% | Até 50% | Até 70% | > 70% |
|---|---|---|---|---|---|
| Até 6 meses | 0,5% | 1,0% | 1,5% | 2,0% | 2,5% |
| Até 1 ano | 1,0% | 1,5% | 2,0% | 2,5% | 3,0% |
| Até 2 anos | 1,5% | 2,0% | 2,5% | 3,0% | 3,5% |
| Mais de 2 anos | 2,0% | 2,5% | 3,0% | 3,5% | 4,0% |

### Aba c) Descumprimento de Requisitos Regulatórios

| Situação | % |
|---|---|
| Ausência de descumprimento | 0% |
| Parcial, com prestação do serviço | 1,0% |
| Total, com prestação do serviço | 2,0% |
| Parcial, sem prestação do serviço | 3,0% |
| Total, sem prestação do serviço | 4,0% |

> O sistema aplica automaticamente o maior valor entre as três abas.

---

## 9. Etapa 5 — Agravante: Situação Econômica do Infrator (Art. 22, IV)

### Fundamento
Aplica-se **1% fixo** quando a pessoa jurídica apresenta, **cumulativamente**, os três indicadores de boa situação econômica:

| Indicador | Fórmula |
|---|---|
| **Solvência geral** superior a 1 | (Ativo Circulante + Ativo Não Circulante) ÷ (Passivo Circulante + Passivo Não Circulante) |
| **Liquidez geral** superior a 1 | (Ativo Circulante + Ativo Realizável a Longo Prazo) ÷ (Passivo Circulante + Passivo Não Circulante) |
| **Lucro líquido positivo** | Último exercício anterior ao PAR |

| Situação | % |
|---|---|
| Algum dos indicadores não é atendido | 0% |
| Todos os três indicadores atendidos cumulativamente | 1,0% |

> A calculadora disponibiliza uma **sub-calculadora integrada** para apurar os índices de solvência e liquidez a partir do Balanço Patrimonial e da DRE, caso esses dados não estejam pré-calculados.

---

## 10. Etapa 6 — Agravante: Reincidência (Art. 22, V)

### Fundamento
**Reincidência** é a ocorrência de nova infração tipificada como ato lesivo pelo art. 5º da LAC — idêntica ou não à anterior — em **menos de cinco anos**, contados da **publicação do julgamento** da infração anterior.

> No caso de **acordo de leniência**, o prazo é contado a partir da data de celebração do acordo até cinco anos após a declaração de seu cumprimento.

| Situação | % |
|---|---|
| Não — sem reincidência | 0% |
| Sim — nova infração em menos de 5 anos do julgamento anterior | 3,0% |

---

## 11. Etapa 7 — Agravante: Valor dos Contratos com o Ente Lesado (Art. 22, VI)

### Fundamento
Considera o **somatório dos contratos, convênios, acordos e demais instrumentos** mantidos ou pretendidos com o órgão/entidade lesado nos **anos da prática do ato lesivo**.

### Tabela de faixas

| Somatório dos instrumentos | % |
|---|---|
| Até R$ 500 mil | 0% |
| Superior a R$ 500 mil até R$ 1,5 milhão | 1,0% |
| Superior a R$ 1,5 milhão até R$ 10 milhões | 2,0% |
| Superior a R$ 10 milhões até R$ 50 milhões | 3,0% |
| Superior a R$ 50 milhões até R$ 250 milhões | 4,0% |
| Superior a R$ 250 milhões | 5,0% |

---

## 12. Etapa 8 — Atenuante: Não Consumação (Art. 23, I)

### Fundamento
Aplica-se quando o ato lesivo **não chegou a produzir seus efeitos plenos** (tentativa).

| Situação | % |
|---|---|
| Ato lesivo consumado | 0% |
| Ato lesivo não consumado (tentativa) | −0,5% |

---

## 13. Etapa 9 — Atenuante: Ressarcimento e Devolução (Art. 23, II)

### Fundamento
Atenuante de até **1,0%** pela **devolução espontânea da vantagem auferida** e/ou **ressarcimento dos danos** resultantes do ato lesivo, conforme Tabela 5 do Guia CGU.

### Tabela de situações

| Situação | % |
|---|---|
| Ausência de devolução espontânea da vantagem e do ressarcimento dos danos | 0% |
| Devolução da vantagem auferida **sem** ressarcimento dos danos; **ou** ressarcimento dos danos **sem** devolução da vantagem | −0,5% |
| Devolução espontânea da vantagem auferida **e** ressarcimento dos danos | −1,0% |
| Devolução da vantagem auferida e inexistência/falta de comprovação de danos; **ou** ressarcimento dos danos e inexistência/ausência de estimativa da vantagem | −1,0% |
| Inexistência ou falta de comprovação de vantagem auferida e de danos | −1,0% |

> A aplicação do **percentual máximo de 1,0%** exige a confirmação expressa de que houve devolução integral. Se desmarcada a confirmação de integralidade, o percentual aplicado é reduzido para 0,5%.

---

## 14. Etapa 10 — Atenuante: Colaboração (Art. 23, III)

### Fundamento
Atenuante pelo **grau de colaboração** da pessoa jurídica durante a investigação ou o PAR, reconhecida ainda que não haja admissão de responsabilidade. Cada condição acrescenta **0,5%**, com teto de **1,5%**.

### Condições (cumuláveis)

| Condição | % |
|---|---|
| Ausência de colaboração | 0% |
| Admitiu a prática do ato | +0,5% |
| Forneceu elementos para a apuração | +0,5% |
| Renunciou aos prazos processuais | +0,5% |

> As condições são **cumuláveis** (checkboxes independentes). O sistema soma automaticamente os percentuais marcados, respeitando o teto de 1,5%.

---

## 15. Etapa 11 — Atenuante: Admissão Voluntária (Art. 23, IV)

### Fundamento
Atenuante pela **admissão voluntária da responsabilidade**, avaliada em dois eixos:
- **Conteúdo:** parcial ou total;
- **Tempestividade:** antes da instauração do PAR, no prazo de defesa, no prazo das alegações finais, ou após as alegações finais.

### Tabela de percentuais

| Condição | % |
|---|---|
| Sem admissão | 0% |
| Parcial — após alegações finais | −0,25% |
| Total — após alegações finais | −0,5% |
| Parcial — no prazo das alegações finais | −0,5% |
| Total — no prazo das alegações finais | −1,0% |
| Parcial — no prazo de defesa | −1,0% |
| Total — no prazo de defesa | −1,5% |
| Parcial — antes da instauração do PAR | −1,5% |
| Total — antes da instauração do PAR | −2,0% |

> Admissões mais abrangentes (total) e mais precoces (antes da instauração) recebem os maiores descontos.

---

## 16. Etapa 12 — Atenuante: Programa de Integridade (Art. 23, V)

### Fundamento
Atenuante de até **5%** pela **comprovada existência e efetiva aplicação** de programa de integridade, avaliado conforme o Capítulo V do Decreto nº 11.129/2022 e a IN CGU nº 1/2015.

> **Regra temporal (Art. 23, parágrafo único, III):** o percentual máximo de 5% somente é atribuível quando o programa for **anterior** à prática do ato lesivo. Programas instituídos após o ato lesivo recebem percentual reduzido (bloco APJ-Posterior).

### Fórmula de cálculo

```
Atenuante = [COI × MPI] + APJ
```

Onde:
- **COI** — Cultura Organizacional e Instâncias de Governança;
- **MPI** — Mecanismos, Políticas e Procedimentos de Integridade;
- **APJ** — Atuação da Pessoa Jurídica em relação ao ato lesivo.

O resultado é limitado ao **teto de 5%**.

### Fluxo

```
Existe programa de integridade?
│
├─ NÃO (ou não comprovado) → 0%
│
└─ SIM → Abrir avaliação completa
          (planilha estruturada CGU — Anexo IV)
          → Resultado calculado automaticamente
          → Atenuante apurada (com teto de 5%)
```

> A avaliação do programa é realizada por meio de questionário estruturado com dezenas de perguntas organizadas nos blocos COI, MPI e APJ, com orientações sobre quais itens se aplicam (MPE, M&A, licitações etc.).

---

## 17. Etapa 13 — Publicação Extraordinária (Art. 6º, II, Lei nº 12.846/2013)

### Fundamento

> **Art. 6º, II, da Lei nº 12.846/2013 c/c Art. 24 do Decreto nº 11.129/2022.**

A **publicação extraordinária da decisão condenatória** é sanção autônoma, aplicada conjuntamente com a multa. Seu prazo é dosimetrado a partir da **Alíquota de Referência**, calculada após a apuração da multa final.

### Apuração da Alíquota de Referência

O sistema aplica automaticamente um de dois cenários:

| Cenário | Regra | Alíquota de Referência |
|---|---|---|
| **A — Regra Geral** | Multa final resultou da aplicação direta da alíquota preliminar (Arts. 22 e 23), sem interferência dos limites do Art. 25 | A própria **alíquota preliminar** da dosimetria |
| **B — Regra de Exceção** | Multa final foi alterada pelos limites mínimo/máximo ou pela vantagem auferida (Art. 25) | Recalculada pela fórmula: **(Valor Final da Multa ÷ Faturamento Bruto) × 100** |

> A identificação do cenário correto e o cálculo da alíquota de referência são feitos **automaticamente** pelo sistema com base nos dados inseridos nas etapas anteriores. O instrumento processual deve registrar qual cenário se aplicou e a alíquota resultante.

---

## 18. Cálculo Final e Verificação dos Limites Legais (Art. 25)

### Fórmula da multa bruta

```
Multa Bruta = Faturamento Bruto × Índice de Dosimetria

Índice de Dosimetria = Σ(Agravantes) − Σ(Atenuantes)
```

### Verificação dos limites legais (Art. 25, Decreto nº 11.129/2022)

Após calculada a multa bruta, o sistema verifica os três vínculos legais:

| Limite | Regra | Efeito |
|---|---|---|
| **Piso — Vantagem Auferida (Art. 25, I)** | A multa não pode ser inferior à vantagem auferida | Se multa bruta < vantagem auferida → multa = vantagem auferida |
| **Teto — Vantagem Pretendida (Art. 25, II)** | A multa não pode exceder o maior valor entre a vantagem auferida e a pretendida | Se multa bruta > maior vantagem → multa = maior vantagem |
| **Faixas do Art. 22, III** | Limites legais mínimo (R$ 6 mil) e máximo (R$ 60 milhões) nas hipóteses do Art. 22, III | Aplicável somente quando o cálculo pelo faturamento é impossível (Art. 26) |

### Casos especiais na dosimetria

**Índice final negativo ou zero:**
> Quando a soma das agravantes menos a soma das atenuantes resultar em valor negativo ou zero (Art. 25, §2º do Decreto nº 11.129/2022), a multa é fixada no **valor do piso mínimo** (vantagem auferida). O sistema informa automaticamente essa condição.

**Índice positivo mas multa menor que o piso:**
> A multa é elevada ao valor da vantagem auferida.

**Multa menor que R$ 6 mil ou maior que R$ 60 milhões (Art. 22, III):**
> Aplicável apenas nas hipóteses residuais em que o faturamento não puder ser apurado.

### Estrutura do relatório de resultado

O painel final exibe uma tabela completa com:

```
BASE DE CÁLCULO
  Ano de Instauração do PAR
  Faturamento Bruto
  Vantagem Auferida (Ganho Real Obtido)
  Vantagem Pretendida (Ganho Planejado/Visado)
  ↳ Maior valor (referência para o teto)
  ↳ Metodologia adotada

AGRAVANTES — ART. 22
  Art. 22, I  — Concurso de atos lesivos
  Art. 22, II — Ciência/Tolerância hierárquica
  Art. 22, III — Interrupção/Descumprimento (maior)
    ↳ a) Serviço Público
    ↳ b) Obra Contratada
    ↳ c) Descumprimento Regulatório
  Art. 22, IV — Situação econômica do infrator
  Art. 22, V  — Reincidência
  Art. 22, VI — Valor dos contratos com ente lesado
  Soma das Agravantes (+)

ATENUANTES — ART. 23
  Art. 23, I  — Não Consumação
  Art. 23, II — Ressarcimento / Devolução
  Art. 23, III — Colaboração
  Art. 23, IV — Admissão Voluntária
  Art. 23, V  — Programa de Integridade
    ↳ Detalhamento da avaliação
  Soma das Atenuantes (−)

RESULTADO DO CÁLCULO
  Índice Final (Dosimetria)
  Multa Bruta Calculada
  Piso Legal (Vantagem Auferida)
  Teto Legal (Maior Vantagem)
  MULTA FINAL APLICÁVEL

PUBLICAÇÃO EXTRAORDINÁRIA
  Alíquota de Referência
  Cenário Aplicado (A ou B)
  Prazo da Publicação
```

---

## 19. Relatório Final e Impressão

### Impressão do Relatório Final (PDF)

O botão **"Imprimir Relatório Final (PDF)"** aciona o modo de impressão do navegador. O relatório impresso tem as seguintes características:

- **Fundo branco** — sem imagens de fundo (adequado para uso processual);
- **Identidade visual institucional** simplificada (sem o logo decorativo superior);
- Todos os parâmetros e percentuais utilizados na dosimetria;
- Textos explicativos de cada agravante/atenuante aplicado;
- Valor final proposto da multa e prazo da publicação extraordinária.

> Para gerar o PDF, utilize a opção "Salvar como PDF" na janela de impressão do navegador (Ctrl+P ou Cmd+P).

### Botões adicionais

| Botão | Função |
|---|---|
| **Imprimir Avaliação PI** | Imprime somente a avaliação do programa de integridade (Etapa 12), sem o restante da dosimetria |
| **Gerar Minuta de Relatório** | Gera um texto dissertativo em forma de minuta para inserção direta na peça processual |
| **← Recomeçar** | Reinicia o formulário do zero (todos os campos são zerados) |

### Minuta de Relatório

A minuta gerada automaticamente produz um texto técnico-jurídico descrevendo:
- A base de cálculo utilizada e sua fundamentação;
- Cada agravante e atenuante aplicado, com o percentual e o dispositivo legal;
- O índice final de dosimetria;
- A verificação dos limites legais e o valor final proposto;
- A sanção de publicação extraordinária e seu prazo.

Esse texto pode ser copiado e inserido diretamente na instrução processual, sendo editável conforme as particularidades do caso.

---

## 20. Fluxo Resumido do Cálculo

```
1. Faturamento Bruto (Base de Cálculo)
   └─ Regra geral: exercício anterior ao PAR (Art. 20)
   └─ Regra especial: último faturamento + IPCA (Art. 21)

2. Vantagens Auferida e Pretendida (Art. 26)
   └─ Auferida → piso mínimo da multa
   └─ Pretendida → referência para o teto máximo

3. Agravantes (Art. 22, I a VI) → soma dos percentuais
   I   Concurso de atos lesivos        (0% a 4,0%)
   II  Ciência/Tolerância hierárquica  (0% a 3,0%)
   III Interrupção/Descumprimento      (0% a 4,0%)
   IV  Situação econômica              (0% ou 1,0%)
   V   Reincidência                    (0% ou 3,0%)
   VI  Contratos com o ente lesado     (0% a 5,0%)

4. Atenuantes (Art. 23, I a V) → soma dos percentuais
   I   Não consumação                  (0% ou 0,5%)
   II  Ressarcimento/Devolução         (0% a 1,0%)
   III Colaboração                     (0% a 1,5%)
   IV  Admissão voluntária             (0% a 2,0%)
   V   Programa de integridade         (0% a 5,0%)

5. Índice Final = Σ Agravantes − Σ Atenuantes

6. Multa Bruta = Faturamento × Índice Final

7. Verificação dos Limites (Art. 25):
   └─ Piso: max(Multa Bruta, Vantagem Auferida)
   └─ Teto: min(resultado, max(Vant. Auferida, Vant. Pretendida))
   └─ Se índice ≤ 0: multa = piso mínimo (vantagem auferida)

8. Alíquota de Referência (para Publicação Extraordinária)
   └─ Cenário A: alíquota preliminar da dosimetria
   └─ Cenário B: (Multa Final ÷ Faturamento) × 100

9. Prazo da Publicação Extraordinária
```

---

## 21. Perguntas Frequentes e Pontos de Atenção

### O sistema é validado por órgão oficial?
A calculadora foi desenvolvida pela Corregedoria da Receita Federal do Brasil como ferramenta de apoio à dosimetria. Os percentuais e critérios implementados refletem o Decreto nº 11.129/2022, a IN CGU nº 1/2015 e o Guia CGU. O resultado gerado é uma **proposta fundamentada**, sujeita à deliberação da autoridade competente.

### Por que a calculadora funciona offline?
A ferramenta foi projetada para ser utilizada em ambientes com restrições de acesso à internet (sistemas de processo digital, redes corporativas isoladas). Nenhum dado inserido é transmitido a servidores externos.

### Como tratar a atualização pelo IPCA?
A calculadora não realiza a atualização automática pelo IPCA por ser offline. Quando necessário (Art. 21 — ausência de faturamento no exercício anterior), o valor deve ser corrigido previamente usando a **Calculadora do Cidadão** do Banco Central (disponível em: bcb.gov.br → Calculadora do Cidadão → IPCA). O valor corrigido é então inserido no campo correspondente.

### O que acontece se o índice de dosimetria for negativo?
Quando a soma das atenuantes supera a soma das agravantes, o índice fica negativo. Nos termos do Art. 25, §2º do Decreto nº 11.129/2022, a multa é fixada **no valor mínimo**, que corresponde à **vantagem auferida**. Se a vantagem auferida for zero ou não estimável, aplica-se o piso legal de R$ 6 mil nas hipóteses cabíveis (Art. 22, III).

### Como distinguir vantagem auferida de pretendida na prática?
- **Auferida:** valor efetivamente recebido, economizado ou patrimonializado pela PJ em decorrência do ato ilícito — verificado nos documentos e extratos do caso;
- **Pretendida:** valor planejado que seria obtido caso o ato ilícito fosse plenamente executado — inferido de proposta, contrato, projeção ou estimativa.

### O programa de integridade posterior ao ato lesivo pode atenuar?
Sim, mas com percentual reduzido. O **bloco APJ-Posterior** da avaliação do programa de integridade avalia as medidas corretivas adotadas pela PJ após a descoberta do ato lesivo. Apenas o **percentual máximo de 5%** é exclusivo de programas preexistentes (Art. 23, parágrafo único, III).

### O que é a célula D15 citada na calculadora?
Refere-se à célula da planilha de referência CGU (Anexo IV do Guia de Responsabilização), usada como parâmetro de equivalência nas fórmulas do bloco de avaliação do programa de integridade. A calculadora replica essa lógica internamente.

### Como gerar o PDF para o processo?
1. Preencha todas as etapas até o resultado final;
2. Clique em **"Imprimir Relatório Final (PDF)"**;
3. Na janela do navegador, selecione **"Salvar como PDF"** como destino de impressão;
4. Ajuste a escala se necessário (recomendado: 80–100%);
5. Salve o arquivo com nome identificador do PAR (ex.: `Multa_PAR_2024_001.pdf`).

---

*Manual elaborado com base no conteúdo e na lógica da Calculadora de Multa PAR — Corregedoria da Receita Federal do Brasil.*
*Fundamentos: Lei nº 12.846/2013; Decreto nº 11.129/2022; IN CGU nº 1/2015; Guia CGU de Responsabilização de Pessoas Jurídicas.*
