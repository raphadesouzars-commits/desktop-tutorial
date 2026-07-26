# Equilíbrio Químico e Oxirredução
### Padrão EBMSP/Bahiana (PROSEF) — Refação da Q35 + 8 questões objetivas de treino

---

## BLOCO 1 — RESUMO DIDÁTICO

### 1.1 Número de oxidação (Nox) — regras essenciais

- Substância simples (ex.: Cl2, O2, Na metálico): Nox = 0 para todos os átomos.
- Íon monoatômico: Nox = carga do íon.
- Em compostos, a soma dos (Nox × número de átomos) de cada elemento é igual à carga total da espécie — 0 para molécula neutra, a carga do íon para um íon composto.
- Oxigênio: geralmente −2. Hidrogênio: geralmente +1. Metais alcalinos (Na, K...): sempre +1 em compostos.
- **Oxidação:** o átomo perde elétrons → o Nox **aumenta**.
- **Redução:** o átomo ganha elétrons → o Nox **diminui**.
- **Agente oxidante:** a espécie que provoca a oxidação de outra — ela mesma é **reduzida**.
- **Agente redutor:** a espécie que provoca a redução de outra — ela mesma é **oxidada**.

### 1.2 Equilíbrio químico e Princípio de Le Chatelier

Um sistema em equilíbrio, quando perturbado, desloca-se no sentido que **minimiza** a perturbação.

| Perturbação | Efeito sobre o equilíbrio |
|---|---|
| Aumento de concentração de um reagente | desloca para a **direita** (sentido direto) |
| Aumento de concentração de um produto | desloca para a **esquerda** (sentido inverso) |
| Aumento de pressão (redução de volume) | desloca para o lado com **menor** número de mols gasosos |
| Diminuição de pressão (aumento de volume) | desloca para o lado com **maior** número de mols gasosos |
| Aumento de temperatura | desloca no sentido **endotérmico** |
| Diminuição de temperatura | desloca no sentido **exotérmico** |

**Atenção — regra da pressão em sistemas heterogêneos:** só contam, na comparação do número de mols, as espécies no **estado gasoso**. Sólidos, líquidos e soluções aquosas não entram nessa contagem, mas **não impedem** o deslocamento: se há gás formado em apenas um dos lados da equação, a variação de pressão desloca o equilíbrio mesmo que o outro lado seja só sólido/aquoso — é exatamente o caso do sistema NaClO/HCl/Cl2 explorado nesta lista.

A constante de equilíbrio (Kc ou Kp) só se altera com **variação de temperatura** — nunca com variação de pressão, volume ou concentração.

### 1.3 Quadro-síntese: palavras-chave e armadilhas típicas

| Expressão no enunciado ou na alternativa | O que verificar antes de aceitar como correta |
|---|---|
| "sofre oxidação / redução" | conferir o **sentido real** da variação do Nox (aumentou ou diminuiu?), nunca aceitar por associação intuitiva |
| "agente oxidante / agente redutor" | lembrar que o agente oxidante **se reduz**, e o agente redutor **se oxida** — é o erro de troca mais comum da disciplina |
| "aumento/diminuição de pressão desloca para..." | identificar **qual lado tem mais mols de gás**, contando apenas as espécies gasosas |
| "não desloca porque é aquoso/sólido" | verificar se há **pelo menos um gás** em algum dos lados — se houver, o critério da pressão se aplica |
| "a constante de equilíbrio muda com a pressão" | falso por definição: Kc/Kp só variam com **temperatura** |

### 1.4 Cuidado metodológico (aplica-se a todas as questões)

A resposta correta de cada questão depende do **balanço técnico exato** — Nox átomo a átomo, ou contagem exata de mols gasosos de cada lado — nunca de generalizações do tipo "toda pressão maior forma mais produto" ou "toda reação de neutralização libera mais gás". Cada alternativa deve ser verificada isoladamente contra o mecanismo real da reação descrita no enunciado.

---

## BLOCO 2 — REFAZENDO A Q35 (equilíbrio + oxirredução, NaClO/HCl/Cl2)

### Enunciado (base: simulado oficial Bahiana)

> O hipoclorito de sódio (NaClO) é amplamente utilizado no tratamento e na desinfecção da água de piscinas para eliminar micro-organismos patogênicos. No entanto, para garantir a eficácia do processo e a segurança dos banhistas, o pH da água deve ser rigorosamente controlado. Caso ocorra uma redução drástica do pH devido à adição excessiva ou inadequada de ácido clorídrico (HCl) — utilizado para correção de alcalinidade —, ocorre uma reação que resulta na liberação de cloro gasoso (Cl2), um gás denso, de odor forte e altamente irritante para o sistema respiratório.
>
> NaClO(aq) + 2HCl(aq) ⇌ NaCl(aq) + Cl2(g) + H2O(l)

Considerando as informações do texto e a análise da equação que representa um sistema em equilíbrio químico, assinale a alternativa correta:

A) A diminuição da pressão sobre o sistema reacional favorece o deslocamento do equilíbrio no sentido direto, aumentando a liberação do cloro gasoso (Cl2) para o ambiente.
B) O átomo de cloro presente no hipoclorito de sódio (NaClO) sofre um processo de oxidação na reação direta, aumentando o seu número de oxidação (Nox).
C) A adição contínua de cloro gasoso (Cl2) ao sistema em equilíbrio desloca a reação no sentido direto, reduzindo a concentração dos reagentes (NaClO e HCl).
D) O hipoclorito de sódio (NaClO) atua prioritariamente como agente redutor na formação do cloro gasoso.
E) O aumento do pH da água (pela adição de uma base) desloca o equilíbrio no sentido de formação de mais cloro gasoso (Cl2).

### ⚠️ Nota importante antes da resolução

O arquivo `BANCO_QUESTOES_ANCORA_SIMULADO.md` deste projeto traz essa questão com o gabarito marcado como **B**. Refazendo o balanço de Nox átomo a átomo (abaixo), a alternativa B está **quimicamente incorreta** — o cloro do NaClO sofre **redução**, não oxidação. A alternativa tecnicamente correta, pela química da reação, é a **A**. Sinalizo essa divergência explicitamente para que você confira com seu professor ou com o gabarito oficial antes de usar este item como âncora de estudo — não vou reproduzir o erro do banco sem avisar.

### Resolução comentada

**Passo 1 — Balanço de Nox átomo por átomo.**
Do lado esquerdo há 3 átomos de cloro: 1 no NaClO (Nox +1) e 2 no HCl (Nox −1 cada). Do lado direito há também 3: 1 no NaCl (Nox −1) e 2 no Cl2 (Nox 0 cada).

Um dos cloros do HCl permanece com Nox −1 (torna-se o Cl do NaCl — não muda, é "espectador" do ponto de vista redox). Sobram o cloro do NaClO (+1) e o outro cloro do HCl (−1), que se tornam os dois átomos de Cl2 (Nox 0):
- Cl do NaClO: +1 → 0 → **ganha 1 elétron → é reduzido**.
- Cl do HCl (o segundo): −1 → 0 → **perde 1 elétron → é oxidado**.

Logo, o NaClO é o **agente oxidante** (ele mesmo se reduz) e o HCl atua, em parte, como **agente redutor** (uma fração do seu cloro se oxida).

**Passo 2 — Análise de cada alternativa.**

- **A) Correta.** Do lado dos reagentes não há gás (NaClO e HCl estão em solução aquosa); do lado dos produtos há 1 mol de Cl2(g). Diminuir a pressão favorece o lado com maior número de mols gasosos — nesse caso, o lado dos produtos —, deslocando o equilíbrio no sentido direto e aumentando a liberação de Cl2(g).
- **B) Incorreta** — *inversão direta*. Inverte o sentido da variação de Nox do cloro do NaClO: ele é **reduzido** (+1→0), não oxidado.
- **C) Incorreta** — *inversão direta*. Pelo Princípio de Le Chatelier, adicionar um **produto** (Cl2) desloca o equilíbrio no sentido **inverso**, aumentando — e não reduzindo — a concentração dos reagentes.
- **D) Incorreta** — *atribuição cruzada / inversão de conceito*. O NaClO é o agente **oxidante** (seu cloro é reduzido), não o agente redutor.
- **E) Incorreta** — *extrapolação/inversão lógica indevida*. Adicionar uma base neutraliza H+ do meio, o que equivale a remover HCl (um reagente); pelo Le Chatelier, isso desloca o equilíbrio no sentido **inverso**, reduzindo — e não aumentando — a liberação de Cl2(g).

**Gabarito tecnicamente correto: A.**

---

## BLOCO 3 — QUESTÕES DE TREINO

**Questões 1, 2 e 3** (estímulo comum)

O cloro é um elemento químico presente em diversas espécies do cotidiano, com diferentes números de oxidação em cada uma delas. O hipoclorito de sódio (NaClO) é o princípio ativo da água sanitária, usada na desinfecção doméstica e no tratamento de água. O gás cloro (Cl2), liberado acidentalmente em incidentes com produtos de limpeza incompatíveis, é altamente tóxico e irritante ao sistema respiratório. Já o ácido clorídrico (HCl) é um componente natural do suco gástrico humano, essencial à digestão, além de amplamente empregado como agente de limpeza industrial.

*(Texto elaborado para fins didáticos, com base em usos correntes de compostos clorados.)*

**Questão 1**

O número de oxidação (Nox) do átomo de cloro no hipoclorito de sódio (NaClO) é:

A) −1
B) 0
C) +1
D) +3
E) +5

**Questão 2**

O número de oxidação (Nox) do átomo de cloro na molécula de gás cloro (Cl2) é:

A) −1
B) 0
C) +1
D) +2
E) +7

**Questão 3**

O número de oxidação (Nox) do átomo de cloro no ácido clorídrico (HCl) é:

A) −1
B) 0
C) +1
D) +3
E) +5

---

**QUESTÃO 4**

Uma indústria utiliza, em ambiente controlado, a reação entre hipoclorito de sódio e ácido clorídrico para geração controlada de cloro gasoso, conforme a equação:

NaClO(aq) + 2HCl(aq) ⇌ NaCl(aq) + Cl2(g) + H2O(l)

Considerando a variação do número de oxidação do cloro nas espécies envolvidas, é correto afirmar:

A) O cloro do NaClO tem seu Nox reduzido de +1 para 0, atuando o NaClO como agente oxidante.
B) O cloro do NaClO tem seu Nox aumentado de +1 para +3, atuando como agente redutor.
C) O cloro do HCl tem seu Nox reduzido de −1 para −3, atuando o HCl como agente oxidante.
D) Nenhum átomo de cloro sofre variação de Nox nessa reação, que não é classificada como reação de oxirredução.
E) O cloro do NaClO e o cloro do HCl sofrem, ambos, redução simultânea, sem que haja oxidação em nenhuma espécie envolvida.

---

**QUESTÃO 5**

A síntese industrial da amônia (processo Haber-Bosch), essencial à produção de fertilizantes nitrogenados e à segurança alimentar global, ocorre segundo o equilíbrio:

N2(g) + 3H2(g) ⇌ 2NH3(g)

O aumento da pressão sobre esse sistema em equilíbrio, mantida a temperatura constante, favorece:

A) o deslocamento do equilíbrio no sentido de formação de maior quantidade de NH3(g), pois esse é o lado com menor número de mols gasosos.
B) o deslocamento do equilíbrio no sentido de formação de maior quantidade de N2(g) e H2(g), pois o aumento de pressão sempre favorece os reagentes.
C) nenhuma alteração na posição do equilíbrio, pois a pressão não influencia sistemas em que todas as espécies são gasosas.
D) o deslocamento do equilíbrio no sentido inverso, uma vez que o aumento de pressão desloca sempre para o lado de maior número de mols gasosos.
E) a diminuição da constante de equilíbrio Kc, alterando permanentemente a proporção entre produtos e reagentes.

---

**QUESTÃO 6**

Em fornos de calcinação utilizados na produção de cal virgem para tratamento de água e construção civil, ocorre o equilíbrio:

CaCO3(s) ⇌ CaO(s) + CO2(g)

O aumento da pressão sobre esse sistema em equilíbrio, a temperatura constante, favorece:

A) o deslocamento do equilíbrio no sentido inverso, com a formação de mais CaCO3(s), pois esse é o lado com menor número de mols gasosos.
B) o deslocamento do equilíbrio no sentido direto, aumentando a formação de CO2(g), pois o aumento de pressão favorece sempre a formação de produtos.
C) nenhum deslocamento, pois CaCO3(s) e CaO(s) são sólidos e não participam do equilíbrio de pressão do sistema.
D) o deslocamento do equilíbrio no sentido inverso, mas com liberação simultânea de mais CO2(g) para compensar o aumento de pressão.
E) a duplicação do valor da constante de equilíbrio Kp, uma vez que a pressão parcial do CO2 é diretamente alterada.

---

**Questões 7 e 8** (estímulo comum)

Uma indústria química opera, em reator fechado, a reação em equilíbrio:

NaClO(aq) + 2HCl(aq) ⇌ NaCl(aq) + Cl2(g) + H2O(l)

utilizada para geração controlada de cloro gasoso destinado a processos de desinfecção industrial.

*(Texto elaborado para fins didáticos, com base em processos industriais de geração controlada de cloro.)*

**Questão 7**

A diminuição da pressão sobre esse sistema, mantida a temperatura constante,

A) favorece o deslocamento do equilíbrio no sentido direto, aumentando a liberação de Cl2(g).
B) favorece o deslocamento do equilíbrio no sentido inverso, reduzindo a liberação de Cl2(g), pois a diminuição de pressão sempre desloca o equilíbrio para o lado dos reagentes.
C) não altera a posição do equilíbrio, pois o NaClO e o HCl estão em solução aquosa, e não no estado gasoso.
D) favorece a formação de mais NaClO(aq) e HCl(aq), consumindo o Cl2(g) previamente formado no sistema.
E) desloca o equilíbrio no sentido direto, mas reduz simultaneamente a quantidade de Cl2(g) presente no sistema.

**Questão 8**

Considere as afirmações a seguir sobre esse mesmo sistema:

I. O átomo de cloro do NaClO sofre redução, tendo seu Nox reduzido de +1 para 0.
II. A diminuição da pressão sobre o sistema favorece a liberação de mais Cl2(g).

Com base na análise dessas afirmações, é correto afirmar que

A) as afirmações I e II estão corretas.
B) apenas a afirmação I está correta, pois a pressão não interfere no deslocamento desse equilíbrio.
C) apenas a afirmação II está correta, pois o cloro do NaClO sofre oxidação, e não redução.
D) as afirmações I e II estão incorretas, pois o NaClO atua como agente redutor nessa reação.
E) as afirmações I e II se contradizem entre si, não podendo ambas serem verdadeiras simultaneamente.

---

## BLOCO 4 — GABARITO COM RESOLUÇÃO EXPLICATIVA

| Questão | Alternativa Correta |
|---|---|
| 1 | C |
| 2 | B |
| 3 | A |
| 4 | A |
| 5 | A |
| 6 | A |
| 7 | A |
| 8 | A |

---

### Questão 1 — Resolução
No NaClO: Na = +1, O = −2. Soma = 0 → Nox(Cl) + 1 − 2 = 0 → **Nox(Cl) = +1** → alternativa **C**.
- A) −1 — *padrão real aplicado ao caso errado*: é o Nox do Cl no HCl.
- B) 0 — *padrão real aplicado ao caso errado*: é o Nox do Cl no Cl2 (substância simples).
- D) +3 — *padrão real aplicado ao caso errado*: é o Nox do Cl no NaClO2 (clorito), estado de oxidação real do cloro, mas no composto errado.
- E) +5 — mesmo mecanismo: Nox do Cl no NaClO3 (clorato).

### Questão 2 — Resolução
Cl2 é substância simples: por definição, **Nox = 0** para todos os átomos → alternativa **B**.
- A) −1, C) +1, D) +2, E) +7 — todos são Nox reais que o cloro assume em outros compostos (HCl, NaClO, ClO2, HClO4), mas nunca na forma elementar — *padrão real aplicado ao caso errado* em todos os distratores.

### Questão 3 — Resolução
No HCl: H = +1. Soma = 0 → **Nox(Cl) = −1** → alternativa **A**.
- B) 0 — Nox do Cl2 elementar.
- C) +1 — Nox do Cl no NaClO.
- D) +3, E) +5 — Nox do Cl em clorito e clorato, respectivamente — *padrão real aplicado ao caso errado* em todos os distratores.

### Questão 4 — Resolução
Conforme detalhado na refação da Q35: o cloro do NaClO vai de +1 para 0 (**reduzido**), tornando o NaClO o **agente oxidante** → alternativa **A**.
- B) *inversão direta* combinada a *padrão real aplicado ao caso errado*: inverte o sentido da variação e ainda erra o valor final.
- C) *violação de regra estrutural verificável*: inventa uma variação de Nox impossível para o cloro nesse contexto (−3 não corresponde ao balanço real da reação).
- D) *negação categórica*: nega que haja variação de Nox, quando claramente há.
- E) *violação de regra estrutural verificável*: afirma que ambos os cloros são reduzidos sem que haja oxidação, o que viola a própria definição de reação redox (toda redução é acompanhada de uma oxidação).

### Questão 5 — Resolução
Reagentes: 1+3 = 4 mols de gás. Produtos: 2 mols de gás. O aumento de pressão favorece o lado com **menor** número de mols gasosos — os produtos (NH3) → alternativa **A**.
- B) *absolutização/generalização categórica*: "sempre favorece os reagentes" ignora que a regra depende da contagem de mols de cada lado.
- C) *negação categórica*: nega o efeito da pressão num sistema onde ele claramente existe.
- D) *inversão direta*: descreve a regra ao contrário (diz que favorece o lado de maior número de mols).
- E) *violação de regra estrutural verificável*: Kc só varia com temperatura, nunca com pressão.

### Questão 6 — Resolução
Único gás do sistema: CO2, presente apenas nos produtos (1 mol). O aumento de pressão favorece o lado com **menor** número de mols gasosos — os reagentes (zero mols gasosos) —, deslocando para a formação de mais CaCO3(s) → alternativa **A**.
- B) *inversão direta*: descreve o sentido oposto ao correto.
- C) *negação categórica*: nega que haja deslocamento pelo fato de dois participantes serem sólidos, ignorando que basta um gás em um dos lados para o critério da pressão se aplicar.
- D) *extrapolação/inversão lógica indevida*: contradiz-se internamente — afirma deslocamento inverso e, ao mesmo tempo, mais liberação de CO2, que é o produto do sentido direto.
- E) *violação de regra estrutural verificável*: Kp não varia com pressão.

### Questão 7 — Resolução
Único gás do sistema: Cl2, presente apenas nos produtos. Diminuir a pressão favorece o lado com **maior** número de mols gasosos — os produtos —, deslocando no sentido direto e aumentando a liberação de Cl2(g) → alternativa **A**.
- B) *inversão direta*: descreve o sentido oposto ao correto.
- C) *negação categórica*: nega que haja deslocamento por os reagentes serem aquosos, ignorando a presença do gás Cl2 no sistema.
- D) *inversão direta*: descreve o efeito oposto ao correto (consumo do Cl2, quando na verdade ele é liberado).
- E) *extrapolação/inversão lógica indevida*: contradiz-se — diz que desloca no sentido direto, mas que a quantidade de Cl2 diminui, quando o sentido direto é justamente o que forma mais Cl2.

### Questão 8 — Resolução
A afirmação I está correta (ver Questão 4/refação da Q35: o Cl do NaClO é reduzido de +1 para 0). A afirmação II também está correta (ver Questão 7: diminuir a pressão favorece o lado com mais mols de gás, o lado do Cl2) → alternativa **A**.
- B) *negação categórica*: nega incorretamente o efeito da pressão sobre esse equilíbrio.
- C) *inversão direta*: inverte o sentido da variação de Nox do cloro do NaClO.
- D) *atribuição cruzada / inversão de conceito*: atribui ao NaClO o papel de agente redutor, quando ele é o agente oxidante (seu cloro é reduzido).
- E) Afirma uma contradição entre I e II que não existe — as duas afirmações tratam de fenômenos independentes (redox e deslocamento por pressão) e são simultaneamente verdadeiras.
