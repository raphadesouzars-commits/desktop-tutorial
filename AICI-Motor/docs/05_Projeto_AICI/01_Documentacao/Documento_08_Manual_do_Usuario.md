# Manual do Usuário - AICI

**Para:** pareceristas da COGER. **Versão 0.3 - novembro/2026.**

## 1. O que o AICI faz (e o que não faz)

O AICI lê o PDF da consulta do SeCI, mostra os fatos, sugere a atividade, procura pareceres, precedentes e normativos parecidos e monta uma **minuta** de parecer com a origem de cada parágrafo. **Quem decide é você.** O AICI não assina, não emite o parecer e não altera a biblioteca.

Há duas abas:

- **Gerador de Parecer:** funciona sozinha e sem internet. Envie o PDF do SeCI (dados e respostas se preenchem sozinhos), escolha a atividade e gere o Word. A tela mostra só o essencial: **"Mais opções do parecer"** e **"Respostas do formulário SeCI"** ficam recolhidas (abra para conferir ou editar). Em **"Falta preencher"**, no alto, e nos **campos amarelos** da prévia, **clique para ir direto ao campo** que falta. O local de assinatura (cidade) é lembrado, e o campo do nº sugere o próximo número.
- **Análise Inteligente:** tem **dois modos**:
  - **Local (padrão, não instala nada):** a análise acontece no próprio navegador. Lê o PDF do SeCI, mostra os fatos, sugere a atividade, mostra precedentes da CGU parecidos e, se você quiser, prepara o prompt para o Copilot Chat. Consulta a biblioteca de pareceres da COGER **se você conectar a pasta sincronizada do SharePoint** (item 3.0).
  - **Motor AICI (avançado):** usa um programa em Python, que precisa estar instalado e ligado, e **consulta a biblioteca de pareceres, precedentes e normativos da COGER**.

## 2. Regras de uso seguro (leia antes)

1. **Use apenas o Copilot Chat da sua conta corporativa da RFB** (acessível pela conta corporativa, integrado ao Microsoft 365). Não cole o prompt do AICI em outro serviço de IA, nem em conta pessoal.
2. O uso do Copilot Chat com dados protegidos foi autorizado pelo CTSI **sob condições de segurança**: siga as orientações da Cotec.
3. **Você responde** pelas informações que envia à IA, por revisar o resultado e por justificar o uso (Portaria RFB nº 647/2026, art. 17).
4. Confira **sempre** fatos, enquadramento, fontes e conclusão. A IA pode errar ou inventar; o AICI descarta o que não tem fonte, mas não substitui a sua leitura.
5. Se perceber **alucinação, viés ou resultado estranho**, comunique ao canal oficial da Cotec (art. 18).
6. Não envie ao AICI arquivos que não sejam consultas do SeCI.

## 3. Passo a passo

### 3.0a Conectar a biblioteca da COGER (uma vez)
1. No SharePoint, abra a biblioteca de pareceres e clique em **Sincronizar** (o OneDrive cria a pasta no seu computador, com `01_Pareceres_Emitidos`, `02_Precedentes`, `03_Normativos`...).
2. No gerador, aba **Análise Inteligente**, cartão **Biblioteca da COGER (opcional)**: clique em **Escolher arquivos** e selecione a **pasta que contém** essas subpastas. O navegador pergunta se pode "carregar" os arquivos: confirme (nada sai do computador).
3. Aguarde a indexação (a primeira vez pode levar vários minutos; há botão **Cancelar**). Terminando, aparece "Biblioteca conectada: N pareceres, N precedentes, N normativos".
4. O índice fica guardado **neste navegador**. Nas próximas vezes a biblioteca já aparece conectada; para pegar arquivos novos, selecione a pasta de novo (só o que mudou é relido). **Esquecer biblioteca** apaga o índice do navegador.
5. **Precedentes da CGU:** a pasta `02_Precedentes/CGU_SeCI` traz **2.576 casos do SeCI/CGU** (todos os órgãos, 2014 a 2026), um por trecho. Eles entram na busca como "Precedente CGU/SeCI nº ..." (com o órgão e o resultado) e podem ir ao prompt do Copilot. Os casos da RFB também já vêm embutidos no gerador (123 casos). Pareceres da COGER têm peso maior que os da CGU, e os da RFB, maior que os de outros órgãos.
6. Ficam de fora: `_Duplicados_Revisar`, a pasta `04_Modelos_Institucionais` e `05_Projeto_AICI`. PDFs digitalizados (sem texto) são contados como "sem texto" e não são pesquisados.

### 3.0 Modo local (padrão) - o que a maioria dos usuários vai usar
1. Abra o `gerador-parecer-conflito.html` e entre na aba **Análise Inteligente** (o modo **Local** já vem marcado).
2. Em **Consulta (PDF)**, escolha o PDF do SeCI e clique em **Analisar consulta**. Tudo é lido no seu navegador; nada é enviado.
3. À direita aparecem: pontos de atenção, **fatos extraídos**, a **atividade** sugerida (você pode trocá-la, e a situação do modelo), e **precedentes da CGU** parecidos (marque os que quiser citar).
4. **Sem Copilot:** clique em **Ir ao gerador de parecer**, revise, complete os campos pendentes e gere o Word, como sempre.
5. **Com o Copilot Chat (opcional):**
   1. Em **Copilot Chat da RFB**, confira o limite de caracteres da caixa do chat (padrão 7.500; confirme com a TI) e escolha prompt completo ou prompt curto + arquivo.
   2. Clique em **1. Gerar prompt** e depois em **Copiar prompt** (no modo arquivo, baixe também o `contexto_AICI.md`).
   3. Abra o **Copilot Chat com a sua conta corporativa da RFB**, cole o prompt (e anexe o arquivo, se for o caso) e envie.
   4. Copie a resposta inteira (JSON), cole em **2. Cole aqui a resposta** e clique em **Aplicar resposta ao parecer**.
   5. O gerador confere as fontes (descarta o que não tem fonte), coloca a fundamentação no parecer e avisa na conferência. Clique em **Ir ao gerador**, **leia e revise** tudo e gere o Word.
   6. Se não gostar, **Remover fundamentação do Copilot** volta ao texto do modelo.

No modo local, o prompt leva o caso (sem CPF, matrícula, telefone, e-mail e nome), as regras da COGER, trechos da Lei nº 12.813/2013 e da Portaria Interministerial nº 333/2013, precedentes da CGU parecidos e o modelo da atividade. Se a **biblioteca da COGER estiver conectada**, leva também os pareceres, precedentes e normativos mais parecidos, com os nomes de servidores mascarados no cabeçalho (nomes no corpo do texto podem permanecer). **Não há bloqueio técnico de revisão no modo local**: a revisão é sua, no gerador.

### 3.0b Duas etapas com o Copilot (recomendado para casos difíceis)
- **Etapa 1 - entender o caso (opcional):** em **Copilot, etapa 1**, clique em **Gerar prompt da etapa 1**, copie, cole no Copilot Chat (conta corporativa) e traga a resposta (JSON) para o campo indicado; clique em **Aplicar entendimento**. O Copilot indica a atividade, termos de busca (sinônimos e vocabulário dos pareceres), incisos do art. 5º, fatos e pontos de atenção. À direita aparece o card **Entendimento do Copilot**: **você confirma** (botões "Usar esta atividade", "＋ atividade", "Marcar incisos") e pode **editar os termos de busca**; a lista de pareceres e precedentes é refeita com eles.
- **Etapa 2 - fundamentação:** o prompt da etapa 2 já leva o entendimento da etapa 1 e os pareceres/precedentes melhor escolhidos. Siga o item 5 de 3.0.
- Pule a etapa 1 quando o caso for simples ou quando a busca já trouxer bons resultados. Se a resposta da etapa 1 vier errada, use **Descartar entendimento**.
- A atividade fora da lista, incisos inexistentes e termos exagerados são descartados automaticamente. A decisão continua sua.

### 3.0c Pedido com várias atividades: conclusão por atividade
Quando a pergunta 2 do SeCI lista atividades (a, b, c...), o gerador mostra, no passo 2, **"Conclusão por atividade do pedido"**. Cada atividade ganha a sua conclusão no parecer: *sem conflito*, *sem conflito com ressalvas*, *risco relevante*, *impedimento de outra ordem* (com o fundamento) ou *não analisada neste parecer*. As sugestões vêm do modelo (no caso do modelo de conteúdo digital, por exemplo, o afiliado em plataforma digital vem como impedimento por exercício do comércio, e o canal e os cursos como autorizáveis com ressalvas). **Confira cada uma.** O Termo de Compromisso e o parágrafo de autorização passam a citar só as atividades autorizadas. Se preferir uma conclusão única, desmarque "Tratar cada atividade na conclusão".

### 3.0d PDF sem texto (OCR automático)
Alguns PDFs, como a **impressão da solicitação** emitida pelo SeCI/SERPRO, não têm texto selecionável (o texto é desenho). O gerador percebe isso e faz **OCR** sozinho, em português, no seu navegador e sem internet: aparece "OCR: lendo a página 1 de 2…" (cerca de 10 a 40 segundos por página; a primeira leitura da sessão demora um pouco mais). Os dados e as respostas são preenchidos e a tela avisa: **"o texto foi lido por OCR e pode ter erros; confira nome, matrícula, protocolo e as respostas"**. Confira sempre.

### 3.0e Escolher a atividade e a situação (e o que fazer se nada serve)
- **Temas sugeridos:** o gerador separa o que o servidor vai **fazer** do **assunto** do que ele trata e compara com os modelos, com as situações de cada modelo e com precedentes parecidos (da CGU e, se a biblioteca estiver conectada, da COGER). O número no chip mostra quantos precedentes sustentam a sugestão.
- **Situação:** as marcadas **"parecida com o caso"** têm o texto mais próximo do pedido. Leia as descrições antes de aceitar.
- **Nenhuma serve?** Escolha **"Nenhuma destas situações - redigir com base no caso concreto"**: o parecer sai com a estrutura padrão e você escreve os fundamentos (um parágrafo por linha), usa os precedentes ou aplica a resposta do Copilot.
- **Ementa:** abra **"Ementa do parecer (editar)"** para ajustar o texto; **"Restaurar"** volta ao modelo.

> Nos itens 3.1 a 3.5 a seguir, descreve-se o **modo Motor AICI (avançado)**.

### 3.1 Ligar o motor
O motor é ligado pela TI (ou por você, na estação de piloto, com `python main.py`). Na aba **Análise Inteligente**, confira o **endereço do motor** (padrão `http://127.0.0.1:8765`) e o **token**, se a TI o exigir. Clique em **Testar conexão**: deve aparecer "Conectado", o tipo de IA e o estado do índice.

### 3.2 Etapa 1 - Análise
1. Em "Consulta (PDF)", escolha o PDF emitido pelo SeCI e clique em **Enviar Consulta (PDF)**.
2. Aguarde. A tela mostra, à direita:
   - **Avisos** (leia primeiro);
   - **Fatos extraídos** (servidor, cargo, matrícula, protocolo, demanda, atividade, entidade, remuneração, vínculo, atribuições);
   - **Compromissos e ressalvas sugeridos**;
   - **Pareceres, precedentes e normativos semelhantes**, cada um com o arquivo de origem e o **motivo** da semelhança;
   - **Minuta**, com a **origem** de cada parágrafo.
3. Se o PDF for digitalizado e o OCR não estiver instalado, aparece o aviso "PDF sem texto legível": use o gerador (aba 1) e digite os dados. (No **modo local do gerador**, o OCR já vem embutido: veja o item 3.0.)

### 3.3 Etapa 2 - Validação humana
1. Em **Atividade (enquadramento)**, confira a sugestão e a confiança (alta, média ou baixa). Se estiver errada, escolha outra na lista: a minuta é refeita.
2. Em **Conclusão do caso concreto**, escolha o resultado: *sem conflito*, *sem conflito com ressalvas (autorização condicionada a Termo de Compromisso)*, *risco relevante de conflito (não autorizar)* ou *impedimento de outra ordem*. Se a conclusão difere da do modelo, **revise os fundamentos**.
3. (Opcional) **Copilot Chat** - ver item 3.5.
4. Clique em **Revisar minuta** para ver os pontos de atenção (campos pendentes, parágrafos sem origem, conclusão incoerente).
5. Marque **"Revisei os fatos extraídos, o enquadramento, as fontes e os compromissos..."**. Sem essa marca, os botões de geração ficam bloqueados.

### 3.4 Etapa 3 - Geração
- **Aplicar no gerador:** preenche a aba 1 com os dados, as respostas, a atividade e a conclusão. Você ajusta e gera o Word no gerador, como sempre.
- **Minuta do motor (.docx):** baixa o parecer pronto no padrão institucional. Informe antes o **nº do parecer** (aba 1); o ano vem da data da aba 1 e a data escrita no documento é a do dia da geração.
- **Termo de Compromisso:** aparece quando a conclusão é *com ressalvas*.
- Campos que o sistema não soube preencher aparecem **entre colchetes e em amarelo** no Word (por exemplo, `[UNIDADE]`, `[PROCESSO]`, `[NOME DO SIGNATÁRIO]`): complete-os antes de assinar.

### 3.5 Usando o Copilot Chat (modo assistido)
O Copilot Chat não se liga diretamente ao AICI; você leva o texto e traz a resposta.

1. Em **Copilot Chat da RFB**, escolha:
   - **Prompt completo**: cabe na caixa do chat (o limite é configurado pela TI); ou
   - **Prompt curto + arquivo de contexto**: leva todo o acervo recuperado como anexo.
2. Clique em **1. Gerar prompt**. O AICI mostra o prompt, quantos caracteres ocupa e se algum trecho ficou de fora.
3. Clique em **Copiar prompt**. No modo arquivo, clique também em **Baixar contexto_AICI.md**.
4. Clique em **Abrir Copilot Chat**, entre com a **conta corporativa**, cole o prompt (e anexe o arquivo, no modo arquivo) e envie.
5. O Copilot responde em **JSON**. Copie a resposta **inteira** (do primeiro `{` ao último `}`).
6. Volte ao AICI, cole em **2. Cole aqui a resposta** e clique em **Aplicar resposta à minuta**.
7. O AICI confere as fontes: parágrafo que cita fonte inexistente é descartado e a minuta avisa. A minuta passa a mostrar a fundamentação do Copilot, com as origens.
8. Se mudar a atividade ou a conclusão depois, o AICI avisa que a resposta do Copilot será descartada.

**Mensagens comuns**
| Mensagem | O que fazer |
|---|---|
| "A resposta não contém o JSON pedido" | Peça ao Copilot: "Responda apenas com o JSON do formato indicado, sem texto antes ou depois." |
| "O JSON da resposta está incompleto ou inválido" | Copie a resposta inteira; se o Copilot cortou, peça para continuar ou repetir |
| "Um parágrafo da IA foi descartado por não citar fonte válida" | Normal: o AICI não aceita fundamento sem origem. Revise a minuta |
| "O contexto não coube em ... caracteres" | Use o modo "prompt curto + arquivo" |
| "Lacuna apontada pela IA" | O acervo não tem base para esse ponto: decida você ou pesquise manualmente |

## 4. Indicadores
Ao fim de cada parecer gerado pelo motor, o AICI registra atividade, resultado, precedente mais próximo e data (sem dados pessoais). A seção **Indicadores gerenciais** mostra os totais.

## 5. Perguntas frequentes

**O AICI substitui o parecerista?** Não. A decisão e o ato são seus.
**Posso usar o Word do motor sem editar?** Deve revisar sempre; ele traz campos pendentes em amarelo.
**O Copilot pode ver os dados do servidor?** O AICI mascara CPF, matrícula, telefone, e-mail e nome antes de montar o prompt; mesmo assim, o texto livre da consulta pode conter dados: siga as orientações da Cotec.
**E se eu não tiver o motor?** Use a aba "Gerador de Parecer", que funciona offline.
**Quem corrige um parecer antigo da base?** A Coordenação: o AICI só lê a biblioteca.

## 6. Suporte
Ponto focal da TI: [a definir]. Ocorrências de IA: canal oficial da Cotec [a divulgar]. Dúvidas sobre o conteúdo (modelos, regras): Coordenação do GNP.
