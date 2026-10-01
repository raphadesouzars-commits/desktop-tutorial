# Análise Combinatória com Restrição por Grupos
### Padrão EBMSP/Bahiana (PROSEF) — 10 questões objetivas (listagem de casos antes do cálculo)

---

## BLOCO 1 — RESUMO DIDÁTICO

### 1.1 Princípio Fundamental da Contagem (PFC)
Se uma decisão pode ser tomada em etapas sucessivas e independentes, o número total de possibilidades é o **produto** do número de opções de cada etapa. Toda a análise combinatória de grupos com restrição deriva desse princípio, aplicado etapa por etapa dentro de cada caso.

### 1.2 Combinação simples
Usada sempre que a **ordem não importa** — formar comissões, equipes, comitês, escalas:

**C(n,p) = n! / [p!·(n−p)!]**

### 1.3 Por que restrição por grupos exige listar casos, e não calcular direto
Quando a condição do problema é do tipo "pelo menos X de um subgrupo", "no máximo Y de outro", "as categorias devem estar todas representadas" ou "duas pessoas não podem estar juntas", uma única combinação **não** resolve o problema — ela captura apenas uma composição possível, entre várias. É necessário:

1. **Listar por escrito, de forma exaustiva**, todas as composições (casos) que satisfazem a restrição.
2. Para cada caso, calcular o **produto** das combinações independentes envolvidas (um fator por subgrupo).
3. **Somar os produtos** de todos os casos válidos — a soma se justifica porque os casos são mutuamente exclusivos (regra da adição).

### 1.4 Quadro-síntese: reconhecendo a estratégia pela palavra-chave do enunciado

| Palavra-chave no enunciado | Estratégia de listagem de casos |
|---|---|
| "pelo menos k" | listar do caso *k* até o caso máximo fisicamente possível, e somar todos |
| "no máximo k" | listar do caso 0 até o caso *k*, e somar todos |
| "exatamente k" | um único caso — mas, se houver mais de uma dimensão (dois subgrupos), ainda é preciso decompor em produto de combinações |
| "duas pessoas específicas não podem estar juntas" | separar em subcasos mutuamente exclusivos: nenhuma das duas / só uma / só a outra — **ou** usar o complementar (total − casos com as duas juntas) |
| "todas as categorias devem estar representadas" (3 ou mais grupos) | listar todas as distribuições (a, b, c, ...) cuja soma é o total pedido, com cada parte ≥ 1 e dentro do limite de cada grupo |

### 1.5 Duas estratégias equivalentes
- **Estratégia direta (soma de casos válidos):** listar e somar apenas os casos que satisfazem a restrição — é a exigida nesta lista.
- **Estratégia complementar:** total sem restrição menos os casos que a violam. É útil como **conferência** do resultado, mas não substitui a listagem exigida no enunciado de cada questão.

### 1.6 Dicas práticas — armadilhas mais comuns (o que os distratores exploram)

- **Parar em uma etapa intermediária**: somar apenas parte dos casos válidos e esquecer o(s) caso(s) restante(s) — em especial os casos-extremos (todo o grupo de um único subtipo).
- **Confundir quantificadores**: tratar "pelo menos k" como se fosse "exatamente k", ou "no máximo k" como se fosse "exatamente k".
- **Trocar a base do grupo**: aplicar a combinação sobre o subgrupo errado (por exemplo, calcular C sobre o total de médicos quando a pergunta se refere aos enfermeiros).
- **Ignorar a exclusão mútua**: ao lidar com "duas pessoas não podem estar juntas", esquecer de separar em subcasos e simplesmente aplicar uma combinação única sobre o restante do grupo.
- **Confundir o total sem restrição com a resposta final**: apresentar C(n,p) do grupo completo, ignorando por completo a condição do enunciado.

### 1.7 Cuidado metodológico (aplica-se às 10 questões)
A resposta correta de cada questão depende exclusivamente da **listagem completa e correta dos casos válidos** e da soma dos produtos correspondentes — nunca de atalhos, fórmulas memorizadas sem justificativa ou generalizações que pulem a etapa de decomposição em casos.

---

## BLOCO 2 — QUESTÕES OBJETIVAS

**Instrução para todas as questões:** antes de calcular, **liste por escrito todos os casos possíveis** que atendem à condição do enunciado. Só depois calcule o produto de cada caso e some os resultados.

---

**Questões 1 e 2** (estímulo comum)

Uma unidade de saúde pública conta com uma equipe de 8 médicos e 5 enfermeiros disponíveis para compor forças-tarefa de fiscalização sanitária. Cada força-tarefa é formada por 4 profissionais, escolhidos entre os 13 disponíveis.

*(Texto elaborado para fins didáticos, com base em situações de organização de equipes de saúde pública.)*

**Questão 1**

Para a primeira força-tarefa, a coordenação exige que a comissão tenha **pelo menos 2 enfermeiros**.

O número de comissões distintas que podem ser formadas nessas condições é:

A) 280
B) 355
C) 360
D) 365
E) 630

**Questão 2**

Para uma segunda força-tarefa, com outra finalidade, a coordenação exige, ao contrário, que a comissão tenha **no máximo 1 enfermeiro**.

O número de comissões distintas que podem ser formadas nessas condições é:

A) 70
B) 280
C) 350
D) 420
E) 715

---

**QUESTÃO 3**

Uma comissão de licitação de um hospital público deve ser formada por 3 servidores, escolhidos entre 7 disponíveis. Dois desses servidores, João e Maria, são cônjuges e, por regra de compliance, **não podem integrar a mesma comissão**.

O número de comissões possíveis, respeitando essa restrição, é:

A) 5
B) 20
C) 25
D) 30
E) 35

---

**QUESTÃO 4**

Um programa de residência médica tem 9 residentes disponíveis para escala de plantão: 5 da Clínica Médica e 4 da Cirurgia. Deve-se escalar 3 residentes, com a exigência de que **haja pelo menos um representante de cada especialidade** (a escala não pode ser composta só por residentes de uma delas).

O número de escalas possíveis é:

A) 60
B) 70
C) 74
D) 80
E) 84

---

**QUESTÃO 5**

Um comitê de ética em pesquisa de uma faculdade de saúde deve ser formado por 4 integrantes, escolhidos entre 6 professores e 3 estudantes de graduação, com a exigência de **pelo menos 1 estudante** no comitê.

O número de comitês possíveis é:

A) 90
B) 105
C) 111
D) 115
E) 126

---

**QUESTÃO 6**

Um time amador de futebol reúne 12 jogadores disponíveis para a partida: 7 destros e 5 canhotos. O técnico deve escalar 5 titulares, exigindo que **pelo menos 3 sejam destros**.

O número de escalações possíveis é:

A) 350
B) 525
C) 546
D) 560
E) 792

---

**QUESTÃO 7**

Um laboratório recebeu 10 tubos de amostra para uma bateria de testes: 6 do grupo controle e 4 do grupo teste. Serão selecionados 4 tubos para uma análise específica, com a condição de que **no máximo 1 tubo seja do grupo teste**.

O número de seleções possíveis é:

A) 15
B) 80
C) 95
D) 120
E) 210

---

**QUESTÃO 8**

Um centro acadêmico precisa formar uma comissão de 3 representantes discentes, escolhidos entre 5 candidatos do curso de Medicina e 6 candidatos do curso de Enfermagem, com a exigência de que a comissão tenha **pelo menos 2 representantes de Medicina**.

O número de comissões possíveis é:

A) 10
B) 60
C) 70
D) 75
E) 165

---

**QUESTÃO 9**

Uma equipe de 8 enfermeiros de um hospital precisa ser dividida em dois grupos de plantão: 3 no plantão noturno e 5 no plantão diurno. Dois enfermeiros específicos, X e Y, têm um conflito de escala registrado e **não podem ser alocados no mesmo plantão**.

O número de divisões possíveis, respeitando essa restrição, é:

A) 20
B) 26
C) 30
D) 36
E) 56

---

**QUESTÃO 10**

Um congresso científico organizará uma mesa-redonda com 4 vagas, a serem preenchidas entre 4 cardiologistas, 3 pneumologistas e 2 infectologistas disponíveis. A organização exige que **as três especialidades estejam representadas** na mesa (nenhuma pode ficar de fora).

O número de mesas-redondas possíveis é:

A) 36
B) 48
C) 60
D) 72
E) 126

---

## BLOCO 3 — GABARITO COM RESOLUÇÃO EXPLICATIVA

| Questão | Alternativa Correta |
|---|---|
| 1 | D |
| 2 | C |
| 3 | D |
| 4 | B |
| 5 | C |
| 6 | C |
| 7 | C |
| 8 | C |
| 9 | C |
| 10 | D |

---

### Questão 1 — Resolução

**Casos possíveis (pelo menos 2 enfermeiros, comissão de 4, 5 enf. + 8 méd.):**
- Caso 1: 2 enfermeiros + 2 médicos
- Caso 2: 3 enfermeiros + 1 médico
- Caso 3: 4 enfermeiros + 0 médico

**Cálculo de cada caso:**
- Caso 1: C(5,2)·C(8,2) = 10·28 = 280
- Caso 2: C(5,3)·C(8,1) = 10·8 = 80
- Caso 3: C(5,4)·C(8,0) = 5·1 = 5

**Soma:** 280 + 80 + 5 = **365** → alternativa **D**.

- A) 280 — *parar em etapa intermediária*: soma apenas o Caso 1 e esquece os Casos 2 e 3.
- B) 355 — *erro de execução*: repete o raciocínio correto, mas calcula C(8,2) como 27 em vez de 28.
- C) 360 — *parar em etapa intermediária*: soma os Casos 1 e 2 (280+80) e esquece o Caso 3 (o caso-extremo "todos enfermeiros").
- E) 630 — *base de contagem errada*: troca a restrição "pelo menos 2" por "no máximo 2", somando os casos com 0, 1 e 2 enfermeiros.

### Questão 2 — Resolução

**Casos possíveis (no máximo 1 enfermeiro, comissão de 4, mesmo grupo de 8 méd. + 5 enf.):**
- Caso 1: 0 enfermeiros + 4 médicos
- Caso 2: 1 enfermeiro + 3 médicos

**Cálculo:**
- Caso 1: C(5,0)·C(8,4) = 1·70 = 70
- Caso 2: C(5,1)·C(8,3) = 5·56 = 280

**Soma:** 70 + 280 = **350** → alternativa **C**.

- A) 70 — *parar em etapa intermediária*: só o Caso 1, esquecendo o Caso 2.
- B) 280 — *confusão entre quantificadores*: só o Caso 2, tratando "no máximo 1" como "exatamente 1".
- D) 420 — *erro de execução*: soma os dois casos, mas com erro pontual em C(8,3) (calculado como 70 em vez de 56).
- E) 715 — é C(13,4), o total de comissões sem qualquer restrição sobre a composição — ignora a condição do enunciado.

### Questão 3 — Resolução

**Casos possíveis (comissão de 3 entre 7, sendo que João e Maria não podem estar juntos; 5 pessoas além deles):**
- Caso 1: nenhum dos dois (João e Maria de fora) + 3 dos outros 5
- Caso 2: só João + 2 dos outros 5
- Caso 3: só Maria + 2 dos outros 5

**Cálculo:**
- Caso 1: C(5,3) = 10
- Caso 2: C(5,2) = 10
- Caso 3: C(5,2) = 10

**Soma:** 10 + 10 + 10 = **30** → alternativa **D**.

- A) 5 — erro grosseiro de execução, calcula apenas parte de um caso.
- B) 20 — *parar em etapa intermediária*: soma apenas dois dos três casos válidos.
- C) 25 — *erro de execução*: calcula um dos C(5,2) como 5 em vez de 10.
- E) 35 — é o total sem qualquer restrição, C(7,3) = 35 — ignora a exclusão de João e Maria juntos.

### Questão 4 — Resolução

**Casos possíveis (escala de 3, pelo menos 1 de cada especialidade, 5 Clínica + 4 Cirurgia):**
- Caso 1: 1 Clínica + 2 Cirurgia
- Caso 2: 2 Clínica + 1 Cirurgia

**Cálculo:**
- Caso 1: C(5,1)·C(4,2) = 5·6 = 30
- Caso 2: C(5,2)·C(4,1) = 10·4 = 40

**Soma:** 30 + 40 = **70** → alternativa **B**.

- A) 60 — *erro de execução*: soma incompleta, com erro pontual em um dos produtos.
- C) 74 — total sem restrição (84) menos apenas "só Cirurgia" (C(4,3)=4) — *esquece de excluir também "só Clínica"*.
- D) 80 — total sem restrição (84) menos apenas "só Clínica" (C(5,3)=10) — *esquece de excluir também "só Cirurgia"*.
- E) 84 — é C(9,3), total sem nenhuma restrição de especialidade.

### Questão 5 — Resolução

**Casos possíveis (comitê de 4, pelo menos 1 estudante, 6 professores + 3 estudantes):**
- Caso 1: 1 estudante + 3 professores
- Caso 2: 2 estudantes + 2 professores
- Caso 3: 3 estudantes + 1 professor

**Cálculo:**
- Caso 1: C(3,1)·C(6,3) = 3·20 = 60
- Caso 2: C(3,2)·C(6,2) = 3·15 = 45
- Caso 3: C(3,3)·C(6,1) = 1·6 = 6

**Soma:** 60 + 45 + 6 = **111** → alternativa **C**.

- A) 90 — *parar em etapa intermediária*: soma apenas os Casos 1 e 2, com erro pontual.
- B) 105 — *erro de execução*: soma os três casos, mas com falha pontual em C(6,3) (usado como 18 em vez de 20).
- D) 115 — *erro de execução*: falha pontual em C(6,2) (usado como 16,3 em vez de 15).
- E) 126 — é C(9,4), total sem restrição — ignora a exigência de ao menos 1 estudante.

### Questão 6 — Resolução

**Casos possíveis (escalação de 5, pelo menos 3 destros, 7 destros + 5 canhotos):**
- Caso 1: 3 destros + 2 canhotos
- Caso 2: 4 destros + 1 canhoto
- Caso 3: 5 destros + 0 canhoto

**Cálculo:**
- Caso 1: C(7,3)·C(5,2) = 35·10 = 350
- Caso 2: C(7,4)·C(5,1) = 35·5 = 175
- Caso 3: C(7,5)·C(5,0) = 21·1 = 21

**Soma:** 350 + 175 + 21 = **546** → alternativa **C**.

- A) 350 — *parar em etapa intermediária*: apenas o Caso 1.
- B) 525 — *parar em etapa intermediária*: soma os Casos 1 e 2, esquecendo o caso-extremo "todos destros" (Caso 3).
- D) 560 — *erro de execução*: falha no Caso 3, tratando C(7,5) como 35 em vez de 21.
- E) 792 — é C(12,5), total sem restrição.

### Questão 7 — Resolução

**Casos possíveis (seleção de 4 tubos, no máximo 1 do grupo teste, 6 controle + 4 teste):**
- Caso 1: 0 teste + 4 controle
- Caso 2: 1 teste + 3 controle

**Cálculo:**
- Caso 1: C(4,0)·C(6,4) = 1·15 = 15
- Caso 2: C(4,1)·C(6,3) = 4·20 = 80

**Soma:** 15 + 80 = **95** → alternativa **C**.

- A) 15 — *parar em etapa intermediária*: só o Caso 1.
- B) 80 — *confusão entre quantificadores*: só o Caso 2, tratando "no máximo 1" como "exatamente 1".
- D) 120 — *erro de execução*: C(6,3) tratado como 30 em vez de 20.
- E) 210 — é C(10,4), total sem restrição.

### Questão 8 — Resolução

**Casos possíveis (comissão de 3, pelo menos 2 de Medicina, 5 Medicina + 6 Enfermagem):**
- Caso 1: 2 Medicina + 1 Enfermagem
- Caso 2: 3 Medicina + 0 Enfermagem

**Cálculo:**
- Caso 1: C(5,2)·C(6,1) = 10·6 = 60
- Caso 2: C(5,3)·C(6,0) = 10·1 = 10

**Soma:** 60 + 10 = **70** → alternativa **C**.

- A) 10 — *parar em etapa intermediária*: só o Caso 2.
- B) 60 — *parar em etapa intermediária*: só o Caso 1, esquecendo o caso-extremo "todos de Medicina".
- D) 75 — *erro de execução*: falha pontual no Caso 1.
- E) 165 — é C(11,3), total sem restrição.

### Questão 9 — Resolução

**Casos possíveis (grupo noturno de 3 e diurno de 5, X e Y não no mesmo grupo; 6 pessoas além de X e Y):**
- Caso 1: X no noturno, Y no diurno → faltam 2 vagas no noturno, escolhidas entre os outros 6
- Caso 2: Y no noturno, X no diurno → faltam 2 vagas no noturno, escolhidas entre os outros 6

**Cálculo:**
- Caso 1: C(6,2) = 15
- Caso 2: C(6,2) = 15

**Soma:** 15 + 15 = **30** → alternativa **C**.

- A) 20 — *erro de execução*: um dos C(6,2) tratado como 5 em vez de 15.
- B) 26 — armadilha clássica: é exatamente o número de divisões **proibidas** (X e Y juntos no noturno, C(6,1)=6, mais juntos no diurno, C(6,3)=20; total 26) — confunde o complemento com a resposta.
- D) 36 — *erro de execução*: soma incorreta com falha pontual.
- E) 56 — é C(8,3), total de divisões sem qualquer restrição.

### Questão 10 — Resolução

**Casos possíveis (mesa de 4, com as 3 especialidades representadas: 4 cardio + 3 pneumo + 2 infecto):**
- Caso 1: 1 cardio + 1 pneumo + 2 infecto
- Caso 2: 1 cardio + 2 pneumo + 1 infecto
- Caso 3: 2 cardio + 1 pneumo + 1 infecto

**Cálculo:**
- Caso 1: C(4,1)·C(3,1)·C(2,2) = 4·3·1 = 12
- Caso 2: C(4,1)·C(3,2)·C(2,1) = 4·3·2 = 24
- Caso 3: C(4,2)·C(3,1)·C(2,1) = 6·3·2 = 36

**Soma:** 12 + 24 + 36 = **72** → alternativa **D**.

- A) 36 — *parar em etapa intermediária*: apenas o Caso 3.
- B) 48 — *parar em etapa intermediária*: soma dos Casos 1 e 2 com erro, esquecendo o Caso 3.
- C) 60 — *parar em etapa intermediária*: soma dos Casos 2 e 3, esquecendo o Caso 1.
- E) 126 — é C(9,4), total sem restrição — ignora a exigência de representação das três especialidades.
