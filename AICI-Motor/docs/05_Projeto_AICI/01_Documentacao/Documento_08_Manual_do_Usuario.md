# Manual do Usuário - AICI

**Para:** pareceristas da COGER. **Versão 0.3 - novembro/2026.**

## 1. O que o AICI faz (e o que não faz)

O AICI lê o PDF da consulta do SeCI, mostra os fatos, sugere a atividade, procura pareceres, precedentes e normativos parecidos e monta uma **minuta** de parecer com a origem de cada parágrafo. **Quem decide é você.** O AICI não assina, não emite o parecer e não altera a biblioteca.

Há duas abas:

- **Gerador de Parecer:** funciona sozinha e sem internet. Você escolhe a atividade, preenche os dados e gera o Word.
- **Análise Inteligente (motor AICI):** usa o motor (programa em Python) para analisar o PDF. Se o motor não estiver ligado, só esta aba fica indisponível.

## 2. Regras de uso seguro (leia antes)

1. **Use apenas o Copilot Chat da sua conta corporativa da RFB** (acessível pela conta corporativa, integrado ao Microsoft 365). Não cole o prompt do AICI em outro serviço de IA, nem em conta pessoal.
2. O uso do Copilot Chat com dados protegidos foi autorizado pelo CTSI **sob condições de segurança**: siga as orientações da Cotec.
3. **Você responde** pelas informações que envia à IA, por revisar o resultado e por justificar o uso (Portaria RFB nº 647/2026, art. 17).
4. Confira **sempre** fatos, enquadramento, fontes e conclusão. A IA pode errar ou inventar; o AICI descarta o que não tem fonte, mas não substitui a sua leitura.
5. Se perceber **alucinação, viés ou resultado estranho**, comunique ao canal oficial da Cotec (art. 18).
6. Não envie ao AICI arquivos que não sejam consultas do SeCI.

## 3. Passo a passo

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
3. Se o PDF for digitalizado e o OCR não estiver instalado, aparece o aviso "PDF sem texto legível": use o gerador (aba 1) e digite os dados.

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
