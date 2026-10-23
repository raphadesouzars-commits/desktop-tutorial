# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, "/home/user/desktop-tutorial/manual")
from helpers import *
from PIL import Image

BASE = "/home/user/desktop-tutorial/manual"
SHOTS = os.path.join(BASE, "assets", "screenshots")
LOGO = os.path.join(BASE, "assets", "logo_coger.png")


def figura_ajustada(doc, image_path, caption, max_width_cm=15.49, max_height_cm=20.0):
    """Insere a figura calculando width_cm a partir da proporção real do PNG,
    para nunca gerar uma altura desproporcional (e, no limite, uma página
    quase em branco) quando a imagem for um crop estreito/comprido."""
    width_cm = max_width_cm
    try:
        with Image.open(image_path) as im:
            w, h = im.size
        if w > 0 and h > 0:
            altura_no_max = max_width_cm * h / w
            if altura_no_max > max_height_cm:
                width_cm = max_height_cm * w / h
    except Exception:
        pass
    return add_figure(doc, image_path, caption, width_cm=width_cm)


def figura_pendente(doc, descricao):
    """Marcador de posição para uma figura que ainda não tem captura de tela.
    Consome um número de figura da sequência normal (para que as figuras reais
    seguintes não colidam) sem inserir imagem — apenas um texto visível."""
    import helpers as _h
    _h._FIGURE_COUNTER["n"] += 1
    n = _h._FIGURE_COUNTER["n"]
    add_muted(
        doc,
        "Figura %d (pendente) — [CAPTURA PENDENTE — %s]" % (n, descricao),
    )
    return n


reset_figure_counter()
doc = new_document()

# ---------------------------------------------------------------------------
# Capa
# ---------------------------------------------------------------------------
add_cover(
    doc,
    LOGO,
    "Manual da Suíte COGER",
    "Veritas · Nexo Coger · Nexo PAR · Oitiva 360",
    [
        "Lei nº 8.112, de 11 de dezembro de 1990 — Processo Administrativo Disciplinar; "
        "Lei nº 12.846, de 1º de agosto de 2013 — Responsabilização Administrativa (LAC)",
        "Suíte de 4 ferramentas offline/locais, integráveis mas independentes entre si",
        "Corregedoria da Receita Federal do Brasil (Coger/RFB)",
    ],
)
add_sumario(doc)

# ---------------------------------------------------------------------------
# Seção 1 — Introdução Geral
# ---------------------------------------------------------------------------
page_break(doc)
add_chapter(doc, "Seção 1", "Introdução Geral")

add_body(
    doc,
    "A **Suíte COGER** reúne quatro ferramentas de apoio ao trabalho de comissões de "
    "Processo Administrativo Disciplinar (PAD), Processo Administrativo de "
    "Responsabilização (PAR) e sindicância, no âmbito da Corregedoria da Receita "
    "Federal do Brasil. A suíte cobre dois domínios normativos distintos: o **PAD** "
    "e a sindicância, à luz da **Lei nº 8.112, de 11 de dezembro de 1990**, e o "
    "**PAR**, à luz da **Lei nº 12.846, de 1º de agosto de 2013** (Lei Anticorrupção "
    "— LAC), que trata da responsabilização objetiva de entes privados por atos "
    "lesivos à Administração. As quatro ferramentas — **Veritas**, **Nexo Coger**, "
    "**Nexo PAR** e **Oitiva 360** — são páginas HTML autocontidas, executadas "
    "inteiramente no navegador do usuário, **sem servidor, sem nuvem e sem envio de "
    "dados a terceiros**. Todo o armazenamento é local (localStorage do navegador) e "
    "a persistência entre sessões depende de exportação/importação manual de arquivos "
    "`.json` pelo próprio usuário.",
)

add_body(
    doc,
    "Este manual destina-se às **comissões de PAD/PAR/sindicância da Corregedoria** "
    "e a servidores que atuam no apoio à instrução disciplinar — presidentes e "
    "membros de comissão, secretários, e equipes técnicas que auxiliam na "
    "organização de provas, na construção do nexo fático-probatório e na condução "
    "de oitivas e interrogatórios.",
)

add_alert(
    doc,
    [
        "**Veritas** — cadastro de provas com cadeia de custódia (proveniência, hash, linha do tempo); opera em modo dual (PAD/PAR).",
        "**Nexo Coger** — mapa fato-prova-norma e apoio à indiciação no domínio **PAD**.",
        "**Nexo PAR** — mapa fato-prova-norma e apoio à Nota de Indiciação no domínio **PAR** (LAC), com cadastro de ente privado.",
        "**Oitiva 360** — apoio à condução de oitivas e interrogatórios, com roteiro e termo; opera em modo dual (PAD/PAR).",
    ],
    kind="info",
    label="As quatro ferramentas da suíte",
)

add_body(
    doc,
    "A cobertura dos dois domínios se distribui de duas formas. O **Nexo** é "
    "**bifurcado por domínio**: o **Nexo Coger** atende o PAD e o **Nexo PAR** "
    "atende o PAR, cada um em seu próprio arquivo. Já o **Veritas** e o **Oitiva "
    "360** operam em **modo dual** — um único arquivo que ajusta seu comportamento "
    "conforme o domínio do processo em curso.",
)

add_alert(
    doc,
    [
        "**Modo dual** — um único arquivo, com comportamento condicional ao domínio "
        "do processo (PAD ou PAR). É o caso do **Veritas** e do **Oitiva 360**: a "
        "mesma ferramenta acomoda os dois ritos, revelando campos e regras próprios "
        "de cada domínio conforme o tipo de processo em uso.",
        "**Modo fork** — dois arquivos independentes, um por domínio. É o caso do "
        "par **Nexo Coger** (PAD) / **Nexo PAR** (PAR): não é uma ferramenta com "
        "duas variações, mas duas ferramentas distintas que compartilham a mesma "
        "mecânica de mapa fato-prova-norma. Isso explica por que só o Nexo aparece "
        "em \"duas versões\" e o Veritas e o Oitiva 360 não.",
    ],
    kind="info",
    label="Modo dual × modo fork",
)

add_body(
    doc,
    "Cada ferramenta é **funcionalmente completa por si só** — é inteiramente "
    "possível cadastrar provas no Veritas, montar o mapa fático no Nexo Coger ou no "
    "Nexo PAR e conduzir oitivas no Oitiva 360 sem que nenhuma delas jamais troque "
    "um arquivo com as outras. As Seções 2 a 5 deste manual documentam cada "
    "ferramenta **em uso isolado**, exatamente como ela se comporta quando usada "
    "sozinha.",
)

add_body(
    doc,
    "Ainda assim, as quatro ferramentas **podem** trocar informações entre si por "
    "meio de exportação e importação de arquivos `.json` — por exemplo, provas "
    "cadastradas no Veritas podem alimentar o mapa do Nexo Coger ou do Nexo PAR, e "
    "um termo de oitiva gerado no Oitiva 360 pode ser importado como prova no "
    "Veritas. Cada contrato carrega, hoje, um campo de **domínio** (PAD/PAR) que a "
    "ferramenta receptora confere na importação. Essa integração é **opcional e "
    "aditiva**: nenhuma das ferramentas exige a outra para funcionar, e os detalhes "
    "de cada contrato de integração ficam reservados para a **Seção 6 — Integração "
    "entre as quatro ferramentas**.",
)

add_separator(doc)
add_muted(
    doc,
    "As capturas de tela deste manual foram produzidas a partir de dados fictícios, "
    "usados exclusivamente para fins de ilustração.",
)

# ---------------------------------------------------------------------------
# Seção 2 — Veritas
# ---------------------------------------------------------------------------
page_break(doc)
add_chapter(doc, "Seção 2", "Veritas (uso isolado)")

add_body(
    doc,
    "O **Veritas** é a ferramenta de cadastro de provas com cadeia de custódia da "
    "Suíte COGER. Sua epígrafe resume o propósito: *\"Toda prova, antes de provar, "
    "deve ser provada.\"* (Iacoviello). O Veritas documenta a consistência interna "
    "e a continuidade de elementos de prova digitais e físicos ao longo do "
    "processo — de onde vieram, como foram recebidos, se o conteúdo é íntegro, e "
    "quem os custodia a cada momento.",
)

add_alert(
    doc,
    ["Ferramenta de apoio à decisão. Não realiza perícia técnica, não valida assinatura digital ICP-Brasil e não substitui laudo pericial formal."],
    kind="warn",
    label="Disclaimer",
)

add_alert(
    doc,
    [
        "A cadeia de custódia tem disciplina legal expressa apenas no processo penal "
        "(art. 158-A a 158-F do CPP, Lei 13.964/2019). No PAD, sua aplicação decorre "
        "por analogia e principiologia — verdade real, devido processo, ampla defesa "
        "— reforçada pela intercambialidade doutrinária de provas entre PAD e "
        "processo penal. O Veritas não sugere vinculação normativa direta ao CPP.",
    ],
    kind="mono",
    label="Fundamentação doutrinária",
)

add_body(
    doc,
    "Nos **Dados do processo** (o cabeçalho da tela do dossiê, onde ficam o número "
    "do processo e o botão de exportação), há um campo **Tipo de processo**, "
    "**opcional**. É dele que o Veritas deriva o **domínio** do dossiê: se o tipo "
    "escolhido for um tipo PAR, o domínio passa a `par`; se for um tipo PAD ou de "
    "sindicância, o domínio é `pad`. Esse domínio é o que sensibiliza, mais adiante, "
    "as categorias de prova disponíveis (Etapa 1) e é emitido nos contratos de "
    "exportação (Seção 2.3). Preencher o Tipo de processo não é exigido para "
    "cadastrar provas.",
)

add_alert(
    doc,
    [
        "Sem **Tipo de processo** definido, o Veritas permanece **agnóstico de "
        "domínio**: aceita prova de qualquer origem, sem filtro, e não marca "
        "`pad` nem `par` no dossiê. O campo só passa a influenciar o comportamento "
        "da ferramenta quando efetivamente preenchido — dossiês antigos, sem esse "
        "campo, seguem funcionando exatamente como antes.",
    ],
    kind="info",
    label="Sem tipo de processo, o Veritas é agnóstico de domínio",
)

add_h2(doc, "2.1 O wizard de cadastro de prova nova")

add_body(
    doc,
    "O cadastro de uma nova prova é feito por um **wizard de 4 etapas** — "
    "*Identificação*, *Proveniência*, *Arquivos* e *Linha do tempo* — indicadas "
    "por uma barra de progresso no topo da tela. O botão **\"Avançar →\"** só "
    "libera a etapa seguinte se a etapa atual passar na validação; o botão "
    "**\"Voltar ←\"**, a partir da etapa 2, não é validado. Na última etapa, o "
    "botão muda para **\"Salvar item\"**, que revalida novamente as etapas 1, 2 "
    "e 3 antes de gravar o item.",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "veritas-wizard-identificacao.png"),
    "Wizard de cadastro de prova — Etapa 1, Identificação.",
)

add_h3(doc, "Etapa 1 — Identificação")

add_alert(
    doc,
    [
        "Mantenha o objeto da apuração determinado: fato, pessoa e meios de prova. "
        "Evite incorporar elementos coletados sem relação direta com a hipótese "
        "investigativa em curso.",
    ],
    kind="info",
    label="Dica — foco investigativo",
)

add_numbered(doc, 1, "**Título/descrição** — campo de texto livre. **Obrigatório**: se deixado em branco, o Veritas bloqueia o avanço com a mensagem \"Informe o título/descrição.\". Placeholder de exemplo: *Ex.: Extrato bancário — conta XXXX, período 01/2023 a 12/2023*.")
add_numbered(doc, 2, "**Categoria** — seleção em lista. **Obrigatória**: se não selecionada, a mensagem é \"Selecione a categoria.\". As opções são: Print de sistema, Documento financeiro, Comunicação (e-mail/mensagem), Foto/vídeo, Laudo/perícia, Ofício, Decisão judicial, Documento físico, Dispositivo/mídia física (HD, celular, pendrive etc.) e Outro. Existe ainda a categoria **\"Termo de oitiva\"**, mas ela é reservada — só é atribuída automaticamente quando um termo do Oitiva 360 é importado (ver Seção 6); não é um fluxo de criação manual normal.")
add_numbered(doc, 3, "**Nº/folha nos autos** — texto livre, opcional (marcado como \"opcional\" na própria tela).")
add_numbered(doc, 4, "**Vinculado à matriz de apuração** — texto livre, opcional, para anotar a que fato/hipótese este elemento de prova sustenta.")
add_numbered(doc, 5, "**Sigilo/classificação** — seleção em lista, opcional, com valor padrão \"Acesso restrito\". Opções: Público nos autos, Acesso restrito, Sigiloso.")
add_numbered(doc, 6, "**Extrato ou conteúdo integral?** — grupo de opções (\"Sim — conteúdo integral\" / \"Não — extrato/trecho parcial\"), com valor padrão \"Sim\".")

add_alert(
    doc,
    [
        "Quando o dossiê está no **domínio PAR** (Tipo de processo PAR — ver a nota "
        "de abertura desta seção), a lista de **Categoria** ganha duas opções "
        "adicionais, próprias da responsabilização de entes privados: **\"Programa "
        "de integridade\"** e **\"Informações do COAF\"**. Elas não aparecem em "
        "dossiês PAD ou sem tipo definido. A categoria **\"Prova emprestada\"** "
        "permanece comum aos dois domínios.",
    ],
    kind="info",
    label="Categorias de prova adicionais no domínio PAR",
)

add_body(
    doc,
    "Se a **Categoria** escolhida for **\"Comunicação (e-mail/mensagem)\"**, aparece um aviso adicional:",
)
add_alert(
    doc,
    [
        "Ao registrar mensagens ou gravações, observe as normas de privacidade "
        "aplicáveis e, quando pertinente, documente se houve consentimento na "
        "colaboração de quem forneceu o material.",
    ],
    kind="info",
)

add_body(
    doc,
    "Se **\"Extrato ou conteúdo integral?\"** for marcado como **\"Não\"**, surge o campo "
    "**Justificativa** (área de texto, com o próprio rótulo indicando \"obrigatória\"). "
    "Se deixada em branco, o Veritas bloqueia com \"Justificativa obrigatória para "
    "extrato parcial.\". Junto do campo aparece a dica:",
)
add_alert(
    doc,
    [
        "Cuidado: decisões não devem se fundamentar em prints de tela, áudios "
        "isolados ou trechos sem contexto. Se este é um extrato parcial, registre "
        "por que o conteúdo integral não foi anexado e avalie a necessidade de "
        "complementação.",
    ],
    kind="warn",
    label="Dica — integralidade",
)

add_h3(doc, "Etapa 2 — Proveniência")

add_body(
    doc,
    "O campo central da Etapa 2 é a escolha do **tipo de proveniência**, um grupo "
    "de opções sem rótulo próprio (é obrigatório escolher um; caso contrário, "
    "\"Selecione o tipo de proveniência.\"). Há três tipos, cada um revelando um "
    "conjunto próprio de campos:",
)

make_table(
    doc,
    headers=["Tipo", "Quando usar", "Campos revelados"],
    rows=[
        ("A) Gerado internamente",
         "Print, PDF exportado, foto de diligência — o Veritas calcula o hash no momento da coleta.",
         "Quem coletou; Contexto da coleta; Local/situação"),
        ("B) Recebido com hash oficial",
         "PJe, ofício de compartilhamento, operação conjunta — a comissão declara o hash da origem.",
         "Processo judicial de origem; Órgão expedidor; Natureza do compartilhamento; Nome/codinome da operação; Data do ofício/decisão; Data de recebimento pela Coger; Nº do ofício/expediente; Modo do hash declarado (por arquivo / pacote)"),
        ("C) Extraído de sistema com trilha própria",
         "Extração ativa pela própria Coger, com acesso institucional.",
         "Sistema de origem; ID do documento no sistema de origem; Nº do processo de origem; Usuário que extraiu; Data/hora da extração"),
    ],
    col_widths=[4.2, 6.0, 5.3],
)

add_body(
    doc,
    "No **tipo B**, ao lado dos campos de recebimento aparece o grupo **\"Modo do "
    "hash declarado pela origem\"**, com duas opções: **\"Hash declarado "
    "individualmente por arquivo\"** (o padrão) ou **\"Hash único do pacote "
    "compactado\"**. Se o modo for \"pacote\", aparecem ainda os campos **Hash "
    "declarado do pacote** e **Algoritmo declarado** (padrão \"SHA-256\"), e o "
    "Veritas exibe um aviso fixo explicando que, nesse modo, a comparação por "
    "arquivo individual não se aplica: cada arquivo é conferido, na Conferência "
    "Geral, contra o hash local originalmente registrado (consistência interna), "
    "não contra o hash do pacote.",
)

add_alert(
    doc,
    [
        "A partir daqui você documenta a **cadeia externa**: o que aconteceu antes "
        "do recebimento pela Coger não está sob seu controle direto. Registre com "
        "precisão a origem e o hash declarado — é essa comparação que sustenta a "
        "continuidade da prova.",
    ],
    kind="info",
    label="Dica — custódia externa (tipo B)",
)

add_body(
    doc,
    "Ao final da Etapa 2, independentemente do tipo escolhido, o Veritas pergunta "
    "se **\"Este item inclui um elemento físico (documento físico, HD, celular, "
    "mídia removível etc.), além do(s) arquivo(s) digital(is)?\"**. Se marcado, "
    "revela: Tipo de elemento físico (Documento físico, HD/dispositivo de "
    "armazenamento, Celular/smartphone, Mídia removível, Outro); Nº do lacre; "
    "Condição do lacre (Íntegro, Rompido, Não lacrado); Descrição do lacre "
    "(cor/característica); Local de guarda física; e Responsável pela guarda física.",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "veritas-cadeia-custodia.png"),
    "Etapa 2, Proveniência — detalhamento do tipo de proveniência e do bloco de elemento físico.",
)

add_alert(
    doc,
    [
        "Documentos físicos e dispositivos (HD, celular, mídia removível) não têm "
        "hash — a integridade deles se sustenta pelo lacre. Registre o nº do lacre, "
        "sua condição no recebimento/coleta e o local de guarda física; use "
        "\"Registrar evento → Conferência do lacre\" sempre que o objeto for "
        "reaberto ou transferido.",
    ],
    kind="info",
    label="Dica — lacre físico",
)

add_body(
    doc,
    "Nenhum campo da Etapa 2 é, individualmente, obrigatório em si — a única "
    "checagem de fato é a escolha do tipo de proveniência. Marcar o elemento "
    "físico como presente, porém, tem um efeito importante na Etapa 3: dispensa "
    "a exigência de anexar arquivo digital.",
)

add_h3(doc, "Como o Veritas calcula o hash")

add_body(
    doc,
    "O hash de cada arquivo é calculado **no momento em que o usuário anexa o "
    "arquivo** — ao clicar no botão **\"Calcular hash e adicionar\"** — e não ao "
    "salvar o item inteiro, nem automaticamente ao apenas selecionar o arquivo no "
    "campo de upload. O cálculo é feito com o algoritmo SHA-256 sobre **o "
    "conteúdo binário bruto do arquivo anexado** (os bytes do arquivo em si, não "
    "metadados como nome ou data). No mesmo instante, o Veritas grava um carimbo "
    "de data/hora local (relógio do computador do usuário).",
)

add_alert(
    doc,
    [
        "O carimbo de data/hora é o relógio deste computador, não um selo de tempo "
        "com autoridade certificadora. Tem valor para mostrar consistência interna "
        "do arquivo, não para provar o instante exato de forma inatacável.",
    ],
    kind="info",
    label="Dica — carimbo local",
)

add_body(
    doc,
    "A **comparação automática** entre o hash calculado localmente e um hash "
    "declarado pela origem só ocorre em um caso específico: proveniência do "
    "**tipo B (recebido com hash oficial)**, com **modo \"por arquivo\"**, e "
    "apenas quando o campo **\"Hash declarado pela origem (deste arquivo)\"** foi "
    "preenchido para aquele arquivo. Nesse caso o resultado é **\"Confere\"** ou "
    "**\"Diverge\"**. Em todos os demais casos — tipo A, tipo C, tipo B em modo "
    "\"pacote\", ou campo de hash declarado vazio — o resultado é **\"Não "
    "aplicável\"**.",
)

add_body(
    doc,
    "Depois de salvo o item, um novo arquivo pode ser anexado a qualquer momento "
    "para uma **Conferência de integridade**: o Veritas recalcula o hash do "
    "arquivo reanexado e o compara com a referência gravada originalmente, "
    "registrando um evento de \"Conferência\" na linha do tempo. Em caso de "
    "divergência, a observação fixa registrada é \"Divergência encontrada na "
    "conferência — ver princípio do prejuízo.\".",
)

add_alert(
    doc,
    [
        "Uma divergência ou lacuna formal na cadeia de custódia não gera nulidade "
        "automática. Registre o ocorrido com precisão e avalie se há prejuízo "
        "concreto e demonstrável para a acusação ou para a defesa — esse é o "
        "critério que prevalece, não a falha formal isolada em si.",
    ],
    kind="warn",
    label="Princípio do prejuízo",
)

add_h3(doc, "Etapa 3 — Arquivos")

add_body(
    doc,
    "Para cada arquivo anexado, o formulário oferece: **Descrição do arquivo no "
    "pacote** (texto livre, opcional); **Hash declarado pela origem (deste "
    "arquivo)** (só aparece quando a proveniência é tipo B em modo \"por "
    "arquivo\"); e o próprio **Arquivo** (seleção de arquivo), obrigatório para "
    "clicar em \"Calcular hash e adicionar\" — sem arquivo selecionado, a "
    "mensagem é \"Selecione um arquivo.\".",
)

add_body(
    doc,
    "A validação da etapa exige **ao menos um arquivo anexado**, a menos que o "
    "elemento físico tenha sido marcado como presente na Etapa 2 — nesse caso, o "
    "arquivo digital passa a ser opcional (por exemplo, uma foto do objeto "
    "lacrado). Sem arquivo e sem elemento físico, a mensagem de bloqueio é "
    "\"Adicione ao menos um arquivo (ou marque o elemento físico na "
    "Proveniência).\".",
)

add_h3(doc, "Etapa 4 — Linha do tempo")

add_body(
    doc,
    "A última etapa oferece três campos, todos opcionais e não validados: "
    "**Responsável pelo registro na ferramenta**, **Custodiante atual** e "
    "**Observações livres**. Abaixo, uma prévia mostra os eventos automáticos "
    "que serão gerados ao salvar (identificação do item, cálculo de hash de cada "
    "arquivo etc.).",
)

add_h2(doc, "2.2 Consulta e edição de prova já cadastrada")

add_body(
    doc,
    "Uma prova salva é reaberta clicando em sua linha na tabela de itens da tela "
    "do processo (ou no ícone de edição ao final da linha).",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "veritas-consulta-listagem.png"),
    "Listagem de itens cadastrados na tela do processo — consulta.",
)

add_body(doc, "**Campos que permanecem editáveis** depois de salvo (cada alteração é gravada imediatamente):")
add_bullet(doc, "Título/descrição")
add_bullet(doc, "Categoria (não pode ser esvaziada de volta para \"Selecione…\")")
add_bullet(doc, "Nº/folha nos autos")
add_bullet(doc, "Vinculado à matriz de apuração")
add_bullet(doc, "Sigilo/classificação")
add_bullet(doc, "Custodiante atual")

add_body(doc, "**Campos que ficam travados** (somente leitura) depois que o item é salvo:")
add_bullet(doc, "Todo o bloco de Proveniência — tipo e todos os subcampos (quem coletou, processo judicial de origem, hash declarado do pacote, sistema de origem etc.)")
add_bullet(doc, "O resumo de elemento físico, exceto a condição do lacre, que só muda através do evento \"Conferência do lacre\"")
add_bullet(doc, "\"Extrato ou conteúdo integral?\" e a Justificativa associada (mostrados como selo, sem campo editável)")
add_bullet(doc, "Status do item (só se altera pelo modal \"Registrar evento\")")
add_bullet(doc, "Fundamentação de contestação (só via evento)")

add_body(
    doc,
    "Arquivos podem ser **adicionados** à prova já salva (pelo mesmo formulário "
    "\"Calcular hash e adicionar\"), mas não podem ser removidos ou substituídos. "
    "Eventos de linha do tempo só são incluídos por meio do modal **\"Registrar "
    "evento\"** — nunca editados nem removidos depois de registrados. Os tipos de "
    "evento disponíveis são: Transferência de custódia, Enviado para perícia "
    "formal, Status alterado, Item descartado, Descrição/contexto registrado, e "
    "Conferência do lacre (só quando o item tem elemento físico presente).",
)

add_h2(doc, "2.3 Exportação isolada do dossiê")

add_body(
    doc,
    "O botão **\"Exportar .json\"**, disponível no cabeçalho \"Dados do processo\" "
    "e também dentro do modal \"Reiniciar dossiê\" (como \"Exportar .json "
    "antes\"), gera um arquivo contendo **o dossiê inteiro** — dados do processo, "
    "comissão, todos os itens, arquivos, proveniência e linhas do tempo — em um "
    "único JSON. O nome do arquivo segue o padrão `dossie-<número do "
    "processo>.json` (ou `dossie-veritas-digital-coger.json` se o processo não "
    "tiver número preenchido).",
)

add_alert(
    doc,
    [
        "Não confunda **\"Exportar .json\"** (exportação isolada do dossiê inteiro, "
        "para backup ou reabertura em outro navegador) com **\"Exportar provas → "
        "Nexo Coger\"** — um botão diferente, que gera apenas as provas "
        "convertidas para o catálogo canônico de tipos de prova do Nexo Coger. "
        "Essa segunda exportação é o contrato de integração com o Nexo Coger e "
        "está documentada na Seção 6 deste manual.",
    ],
    kind="warn",
    label="Atenção — não confundir as duas exportações",
)

add_body(
    doc,
    "Os **dois contratos de exportação** — o \"Exportar .json\" (dossiê inteiro) e "
    "o \"Exportar provas → Nexo Coger\" — emitem, no envelope, o campo **`dominio`** "
    "(`pad` ou `par`) derivado do Tipo de processo. É esse campo que a ferramenta "
    "receptora (Nexo Coger ou Nexo PAR) confere na importação, aceitando apenas "
    "provas do seu próprio domínio. Quando o dossiê não tem Tipo de processo "
    "definido, o envelope sai sem domínio marcado (agnóstico); o tratamento dessa "
    "conferência na importação é detalhado na Seção 6.",
)

add_body(
    doc,
    "Antes de reiniciar um dossiê (apagar os dados salvos no navegador), o "
    "Veritas sempre avisa: **\"Esta ação não pode ser desfeita — o dossiê só "
    "será recuperável se você tiver exportado o .json antes.\"**.",
)

add_h2(doc, "2.4 Reabertura de dossiê")

add_body(
    doc,
    "Um dossiê exportado anteriormente (\"Exportar .json\", Seção 2.3) pode ser "
    "reaberto por importação de arquivo `.json`. O botão de importação aparece "
    "em **dois pontos** da ferramenta: na tela inicial, ao lado de \"+ Novo "
    "dossiê\", com o rótulo **\"Importar dossiê (.json)\"**; e na tela do "
    "Processo, no cabeçalho \"Dados do processo\", como um botão pequeno de "
    "rótulo **\"Importar\"**. Em ambos os casos, selecionar o arquivo já "
    "dispara a importação — não há um botão de confirmação separado do "
    "seletor de arquivo.",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "veritas-reabertura-dossie.png"),
    "Pontos de acesso à reabertura de dossiê — tela inicial e tela do Processo.",
)

add_body(
    doc,
    "A validação, nessa ordem, é: (1) o conteúdo precisa ser um JSON válido — "
    "senão, \"Arquivo .json inválido.\"; (2) o campo `versaoEsquema` do "
    "arquivo precisa ser `\"2.0\"` — senão, \"Versão de esquema não "
    "suportada: <versão>.\", e a importação é interrompida em ambos os casos.",
)

add_alert(
    doc,
    [
        "Se já houver um dossiê aberto no navegador com pelo menos 1 item, o "
        "Veritas abre um modal de confirmação antes de importar — "
        "\"Você tem um dossiê aberto com N item(ns). A importação nunca mescla "
        "dossiês — o dossiê atual será substituído nesta sessão.\" — com os "
        "botões \"Cancelar\" e \"Substituir e importar\". Se o dossiê aberto "
        "estiver vazio (0 itens), a importação ocorre direto, sem esse modal.",
    ],
    kind="info",
    label="Substituição, nunca mesclagem",
)

add_body(
    doc,
    "Se o arquivo importado trouxer um `hashDoDossie` que não confere com o "
    "conteúdo recebido, o Veritas **não bloqueia** a importação — apenas "
    "acrescenta um alerta ao modal (\"O hashDoDossie do arquivo importado não "
    "confere com o conteúdo — possível indício de alteração externa do "
    "arquivo.\") e, ao concluir, mostra o toast \"Dossiê importado — "
    "hashDoDossie divergente, verifique a origem do arquivo.\" em vez do toast "
    "normal de sucesso. A importação prossegue de qualquer forma.",
)

add_alert(
    doc,
    [
        "Não confunda esse comportamento com o da **importação de termo de "
        "oitiva** (Seção 6.3): ali, um hash (`hash_origem`) divergente "
        "**bloqueia totalmente** a importação e nada é gravado. Na reabertura "
        "de dossiê (este fluxo), a divergência de `hashDoDossie` é apenas um "
        "aviso — a importação do dossiê inteiro segue adiante mesmo assim. São "
        "dois fluxos distintos, com políticas de bloqueio diferentes; não os "
        "trate como equivalentes.",
    ],
    kind="warn",
    label="Não confundir com o bloqueio da importação de termo de oitiva",
)

add_h2(doc, "2.5 Busca e filtro")

add_alert(
    doc,
    [
        "Não há campo de busca, filtro por categoria/status/proveniência nem "
        "ordenação de colunas na listagem de itens — a tabela mostra os itens "
        "na ordem em que foram cadastrados.",
    ],
    kind="info",
    label="Recurso inexistente",
)

add_h2(doc, "2.6 Tipos de evento — detalhamento")

add_body(
    doc,
    "A Seção 2.2 já apresentou os 6 tipos de evento disponíveis no modal "
    "\"Registrar evento\". Esta seção detalha, tipo a tipo, os campos "
    "extras pedidos e o efeito real de cada um ao salvar. O modal sempre "
    "abre pré-selecionado em \"Transferência de custódia\", e traz, ao "
    "final de qualquer tipo escolhido, os campos **Responsável** e "
    "**Observação** — nenhum dos dois é obrigatório. A opção "
    "\"Conferência do lacre\" só aparece no seletor de tipo quando o item "
    "tem elemento físico presente.",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "veritas-modal-evento.png"),
    "Modal \"Registrar evento\" — seleção do tipo de evento e campos extras dinâmicos.",
)

make_table(
    doc,
    headers=["Tipo", "Campos extras", "Efeito no item"],
    rows=[
        ("Transferência de custódia", "Novo custodiante (obrigatório)", "Atualiza custodianteAtual do item."),
        ("Enviado para perícia formal", "Arquivo (seleção)", "Só registra evento no arquivo — não altera status."),
        ("Status alterado", "Novo status; + Referência ao item substituto (se \"Substituído\") ou Fundamentação da contestação obrigatória (se \"Contestado\")", "Único fluxo que altera o campo status do item; se contestado, grava fundamentacaoContestacao."),
        ("Item descartado", "Justificativa (obrigatória)", "Força status = \"Descartado\", independentemente do status anterior."),
        ("Descrição/contexto registrado", "Escopo (Item/Arquivo) + Texto", "Só registra evento textual — não altera nenhum campo de estado."),
        ("Conferência do lacre*", "Condição do lacre nesta conferência", "Único fluxo que altera a condição do lacre após a criação do item; recalcula o indicador de integridade do item."),
    ],
    col_widths=[4.3, 6.5, 5.5],
)

add_body(
    doc,
    "* Só disponível quando o item tem elemento físico marcado como presente "
    "na Etapa 2 do wizard.",
    size=9,
)

page_break(doc)

# ---------------------------------------------------------------------------
# Seção 3 — Nexo Coger
# ---------------------------------------------------------------------------
add_chapter(doc, "Seção 3", "Nexo Coger (uso isolado)")

add_body(
    doc,
    "O **Nexo Coger** constrói o **mapa fato-prova-norma** de um processo "
    "disciplinar: para cada fato apurado, associa as provas que o sustentam e os "
    "enquadramentos legais aplicáveis, calcula automaticamente o estado "
    "probatório de cada fato, sinaliza pendências, e — quando a apuração estiver "
    "suficientemente madura — apoia a geração da minuta do termo de indiciação.",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "nexo-mapa-fato-prova-norma.png"),
    "Mapa fato-prova-norma do Nexo Coger, com arestas ligando fatos às provas vinculadas.",
)

add_alert(
    doc,
    [
        "Esta seção documenta o **Nexo Coger no domínio PAD** — a apuração de "
        "responsabilidade de servidores à luz da **Lei nº 8.112, de 11 de dezembro "
        "de 1990**. O domínio **PAR** (responsabilização de entes privados pela "
        "**Lei nº 12.846, de 1º de agosto de 2013** — LAC) é atendido por uma "
        "ferramenta própria e independente, o **Nexo PAR**, documentada na **Seção "
        "4**. Os dois compartilham a mesma mecânica de mapa fato-prova-norma "
        "(modo fork — dois arquivos, um por domínio), mas têm campos, papéis, "
        "pendências e documento final distintos.",
    ],
    kind="info",
    label="Escopo desta seção — domínio PAD",
)

add_h2(doc, "3.1 Dados do Processo")

add_body(
    doc,
    "Antes de acessar o cadastro de fatos, provas ou o mapa, o Nexo Coger "
    "exibe uma tela-gate, em tela cheia, chamada **\"Dados do Processo\"**. "
    "Ela é a primeira coisa que aparece ao abrir a ferramenta sem um "
    "processo já iniciado (rascunhos anteriores que já tenham o número do "
    "processo preenchido não veem o gate de novo — é uma tela de "
    "primeiro uso, não uma barreira a cada carregamento).",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "nexo-dados-processo.png"),
    "Tela \"Dados do Processo\" — gate exibido antes do acesso ao cadastro de fatos.",
)

add_body(doc, "Os campos, nesta ordem exata:")
add_numbered(doc, 1, "**Número do processo** — texto livre. **É o único campo que efetivamente libera o gate.**")
add_numbered(doc, 2, "**Tipo (PN CGU 27)** — seleção agrupada, com os 5 tipos reais da Portaria Normativa CGU nº 27/2022 (Investigativos: IP, SINVE, SINPA, SINAC; Acusatórios: PAD).")
add_numbered(doc, 3, "**Portaria de instauração — nº** — texto livre.")
add_numbered(doc, 4, "**Data de instauração** — data, com hint indicando que é o marco de interrupção da prescrição (art. 142, §3º, Lei 8.112/90).")
add_numbered(doc, 5, "**Presidente da comissão** — trio Nome/Cargo/Matrícula.")
add_numbered(doc, 6, "**Secretário(a)** — trio Nome/Cargo/Matrícula.")
add_numbered(doc, 7, "**Vogal(is)** — lista repetível de trios Nome/Cargo/Matrícula, com botão \"+ Adicionar vogal\" e remoção linha a linha.")

add_alert(
    doc,
    [
        "Enquanto o **Número do processo** não estiver preenchido, o botão de "
        "continuar permanece desabilitado e a tela mostra o aviso: "
        "\"Preencha ao menos o \\\"Número do processo\\\" para liberar o "
        "acesso ao cadastro de fatos, provas e ao mapa — o número também "
        "nomeia os arquivos exportados.\". Os demais 6 campos (tipo, "
        "portaria, datas, comissão) não são exigidos para liberar o gate — "
        "só o número do processo é checado.",
    ],
    kind="warn",
    label="Único campo bloqueante",
)

add_body(
    doc,
    "Cada alteração nesta tela é salva automaticamente (não há botão "
    "\"Salvar\" separado). O número do processo, além de liberar o gate, "
    "também nomeia os arquivos `.json` exportados pelo Nexo Coger — por "
    "exemplo, a exportação geral do processo segue o padrão "
    "`nexo-coger-<número>-<data>.json`, e a pauta de instrução por depoente "
    "segue `nexo-coger-pauta-<número>-<depoente>-<data>.json`.",
)

add_h2(doc, "3.2 Cadastro de um fato apurado — campo a campo")

add_body(doc, "Os campos do formulário \"Fato\" aparecem, nesta ordem exata:")

add_numbered(doc, 1, "**Título** — texto livre. **Obrigatório**: se vazio, \"Informe o título do fato.\".")
add_numbered(doc, 2, "**Descrição pormenorizada** — área de texto, com hint referenciando o \"delineamento fático claro e individualizado\" (STJ, MS 13.110/DF) e contador de caracteres.")
add_numbered(doc, 3, "**Início do período** — data.")
add_numbered(doc, 4, "**Fim do período** — data.")
add_numbered(doc, 5, "**Local** — texto livre.")
add_numbered(doc, 6, "**Data de ciência da autoridade (art. 142, §1º)** — data, com hint explicando que é o marco inicial da prescrição, e **não** a data do fato; se deixada vazia, o cálculo de prazos usa o fim do período como estimativa.")
add_numbered(doc, 7, "**Condutas individualizadas (uma por acusado)** — bloco repetível: para cada linha, seleção do acusado, área de texto para a conduta individualizada e seleção Comissiva/Omissiva. Se não há acusados cadastrados no processo, o Nexo Coger orienta a cadastrá-los primeiro.")
add_numbered(doc, 8, "**Provas vinculadas** — ver seção 3.2 abaixo.")
add_numbered(doc, 9, "**Enquadramentos legais** — ver detalhamento abaixo.")
add_numbered(doc, 10, "**Estado probatório** — ver detalhamento abaixo.")
add_numbered(doc, 11, "**Situação do fato** — ver detalhamento abaixo.")

add_h3(doc, "Enquadramento legal")

add_body(
    doc,
    "A escolha da norma **não é feita por busca em texto livre**: é uma lista de "
    "seleção agrupada por categoria (\"optgroup\"), na seguinte ordem de grupos: "
    "Lei 8.112/90 — Deveres (art. 116); Lei 8.112/90 — Proibições (art. 117); "
    "Lei 8.112/90 — Demissão (art. 132); Outras (art. 130); LAI (Lei "
    "12.527/2011); e, por fim, sem grupo visível, as normas \"Criadas pelo "
    "usuário\". O catálogo de fábrica traz **65 normas pré-cadastradas**; normas "
    "adicionais, fora desse catálogo, só podem ser criadas por um formulário "
    "separado (\"+ enquadramento\" → \"nova norma\"), sempre entrando no grupo "
    "\"Criadas pelo usuário\". Ao lado da lista, um selo colorido mostra a "
    "gravidade e a pena prevista da norma escolhida.",
)

add_body(
    doc,
    "Para cada enquadramento adicionado ao fato, o Nexo Coger pede o "
    "**Elemento subjetivo**, um grupo de opções com exatamente estas 5 "
    "alternativas, nesta ordem:",
)
add_bullet(doc, "Dolo direto")
add_bullet(doc, "Dolo eventual")
add_bullet(doc, "Negligência")
add_bullet(doc, "Imprudência")
add_bullet(doc, "Imperícia")

add_body(
    doc,
    "Se o elemento subjetivo escolhido conflitar com o que a norma exige (por "
    "exemplo, marcar \"Negligência\" em uma norma que exige dolo), o Nexo Coger "
    "exibe um aviso inline explicando a inconsistência. Depois, o campo "
    "**Fundamentação** (texto livre) fecha o bloco de cada enquadramento.",
)

add_body(
    doc,
    "Quando um fato acumula **2 ou mais enquadramentos ativos** (não afastados), "
    "surge um banner de **multiplicidade de enquadramentos**, com um pequeno "
    "assistente de 2 passos: primeiro pergunta se uma única conduta violou mais "
    "de uma hipótese legal (concurso formal) ou se apenas uma hipótese deve "
    "prevalecer (conflito aparente); se conflito aparente, pede o princípio "
    "aplicado (alternatividade, consunção, subsidiariedade ou especialidade), a "
    "norma prevalente e uma **justificativa obrigatória**.",
)

add_h3(doc, "Estado probatório")

add_body(
    doc,
    "O estado probatório de cada fato é **calculado automaticamente** pelo Nexo "
    "Coger e exibido como \"Calculado automaticamente: <valor>\". A comissão pode "
    "**sobrescrever** esse cálculo, escolhendo entre \"usar calculado\", "
    "\"Sobrescrever: suficiente\", \"Sobrescrever: indícios\" ou "
    "\"Sobrescrever: ausente\" — qualquer override exige uma **Justificativa** "
    "obrigatória. Sempre que o estado exibido (calculado ou sobrescrito) não for "
    "\"suficiente\", surge o campo **Elementos buscados**, com o hint \"O que "
    "falta provar? Vira 'elementos buscados' da próxima oitiva.\" — este campo "
    "alimenta diretamente o Oitiva 360 (ver Seção 6).",
)

add_h3(doc, "Situação do fato")

add_body(
    doc,
    "Um grupo de opções define a disposição da comissão sobre o fato: **\"Ativo "
    "— será indiciado\"** ou **\"Arquivado — apurado, não indiciado\"**. Se "
    "arquivado, o Nexo Coger explica que o fato arquivado não gera pendências e "
    "não entra na minuta, permanecendo no mapa apenas como memória da decisão, e "
    "exige uma **Justificativa do arquivamento** obrigatória, com hint pedindo a "
    "\"motivação jurídica: por que a comissão decidiu não indiciar este fato\".",
)

add_h2(doc, "3.3 Vinculação de prova a fato")

add_body(
    doc,
    "A vinculação é feita por **checkboxes de múltipla seleção**, uma por prova "
    "cadastrada — cada linha exibe o id, o título e o tipo da prova. Marcar a "
    "caixa vincula a prova ao fato; desmarcar remove o vínculo. Um botão "
    "**\"+ criar prova daqui\"** permite cadastrar uma prova nova diretamente do "
    "formulário do fato.",
)

add_body(
    doc,
    "No mapa visual, cada vínculo é desenhado como uma linha entre o cartão do "
    "fato e o cartão da prova: **traço contínuo** quando a prova é direta e sem "
    "pendências; **traço tracejado** nos demais casos. Um fato **sem nenhuma "
    "prova vinculada** recebe uma aresta tracejada vermelha terminada em seta, "
    "sinalizando a pendência crítica de lacuna probatória. Provas que não "
    "sustentam nenhum fato (\"órfãs\") aparecem visualmente deslocadas no mapa, "
    "como sinal deliberado dessa condição.",
)

add_h2(doc, "3.4 Papel de pessoa")

figura_ajustada(
    doc,
    os.path.join(SHOTS, "nexo-papel-pessoa.png"),
    "Seleção de papel do depoente no formulário de prova testemunhal/declaração de informante.",
)

add_body(doc, "O catálogo do Nexo Coger define exatamente 5 papéis de pessoa:")

make_table(
    doc,
    headers=["Papel", "Descrição resumida"],
    rows=[
        ("Investigado/Acusado", "Servidor submetido a apuração; não presta compromisso; direito ao silêncio."),
        ("Vítima", "Não presta compromisso legal; sujeita-se à denunciação caluniosa."),
        ("Testemunha", "Presta compromisso legal de dizer a verdade (art. 342, CP); dever de depor."),
        ("Declarante/Informante", "Não presta compromisso; colaboração voluntária, sem responder por falso testemunho."),
        ("Pessoa em Situação Indefinida", "Envolvimento possível, ainda sem elementos para tratar como investigado."),
    ],
    col_widths=[4.5, 11.0],
)

add_body(
    doc,
    "O seletor de papel aparece em dois pontos do Nexo Coger: (a) no formulário "
    "de prova, quando o **Tipo de prova** é \"Testemunhal\" ou \"Declaração de "
    "informante\" — junto com os campos **Deponente**, **Papel do depoente**, "
    "**Compromissada?** e o trio de campos sobre contradita; e (b) na tela "
    "**\"Revisão de pauta\"** (usada para preparar a exportação de pauta para o "
    "Oitiva 360 — ver Seção 6), no bloco \"Depoente\", com os campos **Nome** e "
    "**Papel (catálogo canônico)**.",
)

add_body(
    doc,
    "Ao trocar o **Papel do depoente** no formulário de prova, o campo "
    "**\"Compromissada?\"** é automaticamente ajustado conforme o papel "
    "escolhido: só o papel \"Testemunha\" define o valor inicial como \"Sim\"; "
    "os outros quatro papéis definem \"Não\". O usuário pode, ainda assim, "
    "sobrescrever manualmente esse valor pelo próprio campo — a mudança de papel "
    "apenas define o valor inicial, não trava o campo.",
)

add_alert(
    doc,
    [
        "Ao abrir uma prova **nova** do tipo \"Declaração de informante\" pela "
        "primeira vez, o campo \"Compromissada?\" pode nascer marcado em \"Sim\", "
        "mesmo esse papel não prevendo compromisso no catálogo. Isso se corrige "
        "automaticamente se o usuário reselecionar o papel no campo — mas, até "
        "lá, **confira manualmente** o valor de \"Compromissada?\" sempre que "
        "cadastrar uma declaração de informante nova.",
    ],
    kind="warn",
    label="Confira manualmente",
)

add_body(
    doc,
    "**Orientação prática deste manual** (não é texto exibido pela ferramenta): "
    "o papel **\"Pessoa em Situação Indefinida\"** destina-se a situações em que "
    "os autos indicam um possível envolvimento da pessoa no contexto fático, mas "
    "ainda não há elementos suficientes para tratá-la formalmente como "
    "investigada — por cautela, a ela também se faculta o direito ao silêncio, "
    "por analogia à vedação à autoincriminação, e recomenda-se consultar "
    "previamente a defesa sobre o enquadramento adotado antes de qualquer oitiva "
    "nessa condição.",
)

add_h2(doc, "3.5 Geração da indiciação")

figura_ajustada(
    doc,
    os.path.join(SHOTS, "nexo-indiciacao.png"),
    "Tela de geração da minuta do termo de indiciação.",
)

add_alert(
    doc,
    [
        "A geração da indiciação é um **ato final** da instrução — gera o "
        "documento formal de indiciação de cada acusado selecionado. Não a use "
        "prematuramente, antes que os fatos, provas e enquadramentos estejam "
        "efetivamente consolidados.",
    ],
    kind="danger",
    label="Ato final — use com cautela",
)

add_body(
    doc,
    "Antes mesmo de abrir a tela de geração, o Nexo Coger verifica se existem "
    "**pendências críticas** em qualquer fato, prova ou acusado do processo "
    "(não apenas do indiciado que se deseja gerar). Havendo qualquer uma, a "
    "geração é bloqueada com o alerta \"Há pendências críticas que impedem a "
    "indiciação. Veja o painel.\". As pendências críticas bloqueantes são:",
)
add_bullet(doc, "**P1** — Fato sem prova vinculada (alegação sem evidência), salvo se houver override de estado probatório justificado.")
add_bullet(doc, "**P2** — Fato sem enquadramento legal, crítica a partir da fase de indiciação em elaboração em diante.")
add_bullet(doc, "**P5** — Conduta não individualizada — risco de indiciação genérica (nulidade).")
add_bullet(doc, "**P8** — Alternatividade violada: enquadramentos doloso e culposo simultâneos no mesmo fato.")

add_body(
    doc,
    "Pendências **frágeis** (P3, P6a, P6b, P6c, P7) não bloqueiam a geração, mas "
    "aparecem como aviso na própria tela: \"Pendências frágeis ainda abertas: "
    "<códigos>. A minuta pode ser gerada, mas revise-as.\". O detalhamento "
    "confirmado de cada uma:",
)

make_table(
    doc,
    headers=["Código", "Descrição"],
    rows=[
        ("P3", "Prova órfã — prova cadastrada que não sustenta nenhum fato (aparece deslocada no mapa)."),
        ("P6a / P6b", "Prova vinculada não classificada como \"direta\" — reflete-se no mapa como aresta tracejada em vez de contínua (pendência frágil — não bloqueia geração de minuta, mas deve ser revisada antes de finalizar)."),
        ("P6c", "Intimação para o interrogatório com antecedência inferior a 3 dias úteis (art. 41, Lei nº 9.784/99) — calculada quando o acusado tem Notificação prévia e Interrogatório com data preenchidas (Seção 3.6). É a única pendência do sistema vinculada a um acusado, não a um fato ou prova; clicar nela abre o cadastro do próprio acusado."),
        ("P7", "Sustentação exclusivamente indiciária/informal — explicitar raciocínio indutivo. Dispara quando o fato tem ao menos uma prova vinculada e todas as provas vinculadas são do tipo \"Prova indiciária\" ou \"Declaração de informante\" (nenhuma prova documental, pericial, testemunhal, emprestada, de interrogatório ou de diligência sustenta o fato)."),
    ],
    col_widths=[2.7, 12.8],
)

add_body(
    doc,
    "Passada a checagem, a tela de geração pede: uma **checkbox por acusado "
    "cadastrado** (todas marcadas por padrão, um documento é gerado por "
    "indiciado selecionado) e a **Data do documento**, pré-preenchida com a data "
    "de hoje, usada no fecho e nas assinaturas.",
)

add_body(
    doc,
    "Ao clicar em \"Gerar minuta\", o Nexo Coger roda uma checagem de campos "
    "essenciais (`validaMinuta`) e lista tudo o que faltar, sem gerar nada até "
    "que esteja completo: número do processo, nome do presidente da comissão, "
    "nome e cargo de cada indiciado, existência de ao menos um fato ativo "
    "imputado ao indiciado, e — para cada fato ativo dele — descrição e "
    "enquadramento preenchidos.",
)

add_body(
    doc,
    "O documento gerado (\"Indiciação\") traz, nesta ordem: cabeçalho "
    "institucional e dados do processo; tabela de qualificação do servidor; "
    "\"Dos fatos e das condutas\"; \"Das provas\"; \"Do enquadramento legal\"; "
    "uma tabela-síntese de fatos × provas × enquadramentos; \"Das alegações da "
    "defesa não acatadas\"; e \"Do encerramento\", com bloco de assinatura em "
    "três colunas (Vogal | Presidente | Vogal).",
)

add_h2(doc, "3.6 Cadastro de acusado")

add_body(
    doc,
    "O formulário de acusado (`doc.acusados[]`) é um **modelo de dados "
    "totalmente separado** do sistema de papéis de pessoa (Seção 3.4) — um "
    "acusado nunca recebe um `papelId`; o conceito de \"papel\" só existe "
    "no contexto de depoente (prova testemunhal/declaração de informante) "
    "e na tela \"Revisão de pauta\".",
)

add_body(doc, "Os campos do formulário \"Acusado\" aparecem, nesta ordem exata:")

add_numbered(doc, 1, "**Nome** — texto livre. **Obrigatório**: se vazio, \"Informe o nome do acusado.\" — é o único campo bloqueante no cadastro.")
add_numbered(doc, 2, "**Matrícula (SIAPE)** — texto livre.")
add_numbered(doc, 3, "**Cargo** — texto livre. Não é exigido para salvar o cadastro, mas passa a ser obrigatório mais adiante, no momento de gerar a minuta de indiciação (Seção 3.5).")
add_numbered(doc, 4, "**Lotação** — texto livre.")
add_numbered(doc, 5, "**Qualificação complementar** — área de texto livre; funciona como campo de escape para qualquer dado de qualificação sem campo dedicado (não há campo de CPF nem de endereço no formulário).")
add_numbered(doc, 6, "**Situação funcional** — seleção com 4 opções: \"Ativo (não licenciado/afastado)\", \"Licenciado/afastado\", \"Inativo (aposentado)\" e \"Ex-servidor\".")
add_numbered(doc, 7, "**Telefone(s) móvel(is)** — texto livre, usado no bloco \"Contatos:\" dos termos de intimação.")
add_numbered(doc, 8, "**E-mail(s)** — texto livre.")
add_numbered(doc, 9, "**Alegações da defesa não acatadas** — área de texto, preenchida antes da impressão final da indiciação (também ajustável na própria tela de impressão).")
add_numbered(doc, 10, "**Bloco \"Notificação prévia\"** — três campos: \"Realizada?\" (Sim/Não), \"Data\" e \"Ref. autos\".")
add_numbered(doc, 11, "**Bloco \"Interrogatório\"** — quatro campos: \"Status\" (Pendente / Realizado / Silêncio formalizado / Cancelado), \"Data\", \"Ref. autos\" e \"Realizado após todas as provas?\" (Sim/Não).")
add_numbered(doc, 12, "**Bloco \"Contexto de oitiva\"** — condicional: só aparece quando o acusado já recebeu algum retorno de oitiva do Oitiva 360 (Seção 6.4). Lista cada item recebido com a referência do fato e da prova de origem, a citação do resumo da resposta (quando houver) e uma caixa \"Revisado\" para a comissão marcar a conferência.")

add_alert(
    doc,
    [
        "Nenhum dos campos 2 a 11 é exigido para **salvar** o cadastro do "
        "acusado — só o **Nome** bloqueia. \"Cargo\" volta a ser cobrado, "
        "mas só no momento de **gerar a minuta de indiciação**; os campos "
        "de \"Notificação prévia\" e \"Interrogatório\" não bloqueiam nada "
        "diretamente, mas alimentam o checklist de encerramento e a "
        "pendência P6c (Seção 3.9).",
    ],
    kind="info",
    label="Só o Nome é obrigatório para salvar",
)

add_body(
    doc,
    "Ao excluir um acusado, o Nexo Coger pede confirmação: \"Excluir este "
    "acusado? As condutas vinculadas a ele nos fatos serão removidas.\".",
)

add_body(
    doc,
    "Esses mesmos campos fecham o ciclo com a Seção 3.5: a **tabela de "
    "qualificação** que abre a minuta do termo de indiciação lê exatamente "
    "**Nome**, **Matrícula**, **Cargo** e **Lotação** do cadastro do "
    "acusado (mostrando \"—\" para os que estiverem vazios), acrescida da "
    "linha **\"Qualificação\"** apenas quando o campo \"Qualificação "
    "complementar\" estiver preenchido. Os demais campos do cadastro "
    "(situação funcional, telefone, e-mail, notificação prévia, "
    "interrogatório) não são lidos pela minuta de indiciação — servem a "
    "outros fins, como o checklist de encerramento e o painel de Prazos "
    "(Seção 3.9).",
)

add_h2(doc, "3.7 Cadastro de prova no Nexo Coger")

add_body(
    doc,
    "O detalhamento do formulário de prova para os tipos **Testemunhal** e "
    "**Declaração de informante** — Deponente, Papel do depoente, "
    "Compromissada?, trio de contradita — já foi apresentado na Seção 3.4 "
    "(Papel de pessoa). Esta seção cobre os campos **gerais** do formulário "
    "de prova, presentes independentemente do tipo escolhido, e o catálogo "
    "completo do campo \"Tipo de prova\".",
)

add_body(doc, "Os campos gerais do formulário \"Prova\" aparecem, nesta ordem exata:")

add_numbered(doc, 1, "**Tipo de prova** — seleção com 8 opções (ver tabela abaixo). Decide quais campos de detalhe adicionais aparecem.")
add_numbered(doc, 2, "**Título** — texto livre. **Obrigatório**: se vazio, \"Informe o título da prova.\".")
add_numbered(doc, 3, "**Descrição** — área de texto livre.")
add_numbered(doc, 4, "**Documento (ref. autos)** e **Folhas** — dupla de campos que registra a referência da prova aos autos do processo (distinta da \"Ref. autos\" da contradita, que só existe no bloco de depoente testemunhal/declaração de informante).")
add_numbered(doc, 5, "**Código do anexo (opcional)** — texto livre; se vazio, a minuta gera automaticamente \"Prova nº N\" no índice.")
add_numbered(doc, 6, "**Hash Veritas Digital - Coger** — texto livre, referência manual ao hash do item no Veritas (sem integração automática — ver Seção 6 para a integração real via arquivo).")
add_numbered(doc, 7, "**Bloco de detalhe do tipo** — ver tabela abaixo; varia conforme o \"Tipo de prova\" escolhido.")
add_numbered(doc, 8, "**Trechos significativos** — lista repetível de pares Citação / Referência, com botão para adicionar/remover linhas.")
add_numbered(doc, 9, "**Contraditório — acusado intimado da produção?** — três opções: \"Intimado\", \"Não intimado\" ou \"Não avaliado\".")

add_body(doc, "A prova também carrega uma lista de **fatos aos quais está vinculada** (`fatoIds`) — o mesmo vínculo tratado do lado do fato na Seção 3.3: marcar a checkbox no formulário do fato e vincular pelo lado da prova refletem o mesmo relacionamento.")

add_body(doc, "As 8 opções do campo **\"Tipo de prova\"**:")

make_table(
    doc,
    headers=["Tipo", "Revela bloco de detalhe próprio?", "Campos do bloco (se houver)"],
    rows=[
        ("Documental", "Não", "—"),
        ("Pericial", "Sim", "Perito; Quesitos formulados? (Sim/Não)"),
        ("Testemunhal", "Sim", "Deponente; Papel do depoente; Compromissada?; trio de contradita (Seção 3.4)"),
        ("Declaração de informante", "Sim", "Mesmo bloco de Testemunhal, só muda o valor padrão do Papel do depoente"),
        ("Interrogatório", "Não", "—"),
        ("Diligência", "Não", "—"),
        ("Prova emprestada", "Sim", "Processo de origem; Certidão de juntada?; Origem judicial?; Autorização judicial"),
        ("Prova indiciária", "Sim", "Fato secundário provado; Raciocínio indutivo"),
    ],
    col_widths=[3.6, 4.4, 7.5],
)

add_body(
    doc,
    "\"Interrogatório\" e \"Diligência\" são tipos de prova **sem nenhum "
    "campo de detalhe específico** — mesmo \"Interrogatório\" sendo, no "
    "cadastro de acusado (Seção 3.6), um ato com campos próprios "
    "(Status/Data/Ref. autos), o tipo de prova homônimo usa só os campos "
    "gerais listados acima.",
)

add_alert(
    doc,
    [
        "**Trocar o \"Tipo de prova\" zera o bloco de detalhe já "
        "preenchido.** Escolha o tipo definitivo antes de preencher o "
        "detalhe (Perito, Deponente, Processo de origem etc.) — se você "
        "mudar o tipo depois, o Nexo Coger descarta silenciosamente os "
        "dados de detalhe já digitados.",
    ],
    kind="info",
    label="Preencha o detalhe só depois de fixar o tipo",
)

add_h2(doc, "3.8 Selo de origem — retorno de oitiva")

add_body(
    doc,
    "Quando uma prova é criada no Nexo Coger a partir da exportação "
    "**\"Exportar prova(s) para o Nexo\"** do Oitiva 360 (Seção 6.4), o "
    "cartão dessa prova no mapa fato-prova-norma recebe um selo dourado "
    "**🎙**, ao lado dos demais selos do cartão de prova (como o 🌐 de "
    "origem Veritas). O tooltip do selo mostra os campos `pauta_id`, "
    "`rodada_id` e `id_ponto` do retorno de oitiva.",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "nexo-selo-oitiva.png"),
    "Selo 🎙 no cartão de prova, indicando origem em retorno de oitiva do Oitiva 360.",
)

add_alert(
    doc,
    [
        "**Atualização (rodada 2026-07-12)**: os três campos do tooltip "
        "(`pauta_id`, `rodada_id`, `id_ponto`) vêm preenchidos sempre que a "
        "prova exportada por \"Exportar prova(s) para o Nexo\" tem origem "
        "em um ponto de pauta respondido — o Oitiva 360 passou a incluir os "
        "três identificadores por item de prova nesse contrato, lidos do "
        "mesmo ponto de pauta (`estado.pautaImportada.itens`) já usado pelo "
        "contrato de retorno de contexto. Quando a prova foi **adicionada "
        "manualmente na sessão, sem vínculo de pauta**, os três campos saem "
        "`null` — comportamento correto e documentado, não uma limitação: "
        "ver audit-oitiva-360.md §10 e audit-nexo-coger.md §6.5 para o "
        "detalhe e o teste end-to-end.",
    ],
    kind="info",
    label="IDs do tooltip: preenchidos com origem de pauta, null sem ela",
)

add_body(
    doc,
    "Não confunda este selo de **prova** com o selo pré-existente, também "
    "dourado (🎙), que aparece no **cartão de fato** quando o fato recebe "
    "contexto de um retorno de oitiva importado pelo fluxo \"Exportar "
    "retorno (contexto do acusado)\" (Seção 6.4) — esse outro selo, no "
    "cartão de fato, é anterior a esta rodada de implementação e já "
    "funciona plenamente.",
)

add_h2(doc, "3.9 Toolbar lateral")

add_body(
    doc,
    "O Nexo Coger mantém uma barra lateral com quatro painéis de apoio à "
    "condução da apuração: **Pendências**, **Ordem dos fatos**, "
    "**Checklist de encerramento** e **Prazos**.",
)

add_h3(doc, "Pendências")

add_body(
    doc,
    "Lista, em tempo real, todos os códigos de pendência crítica (P1, P2, "
    "P5, P8) e frágil (P3, P6a, P6b, P6c, P7) presentes no processo — o "
    "mesmo catálogo apresentado na Seção 3.5. Clicar num item do tipo "
    "\"acusado\" (P6c) abre diretamente o cadastro do acusado correspondente.",
)

add_h3(doc, "Ordem dos fatos")

add_body(
    doc,
    "Lista apenas os **fatos ativos** (fatos arquivados nunca aparecem "
    "aqui, mas o cabeçalho informa a contagem de arquivados que não "
    "constam da minuta). A ordenação **não é cronológica nem automática "
    "por gravidade — é inteiramente manual**, feita arrastando cada linha "
    "para a posição desejada. O próprio painel avisa: \"Arraste para "
    "reordenar. Afeta apenas a sequência da minuta — não o mapa.\". Ao "
    "soltar, o Nexo Coger renumera 1..N os fatos ativos nessa nova "
    "sequência, que é exatamente a ordem em que \"Dos fatos e das "
    "condutas\" aparece na minuta de indiciação (Seção 3.5).",
)

add_h3(doc, "Checklist de encerramento")

add_body(
    doc,
    "Sempre visível (não é um painel recolhível). Traz 5 itens, quase "
    "todos calculados automaticamente a partir do estado do processo — não "
    "são checkboxes que o usuário marca diretamente:",
)

make_table(
    doc,
    headers=["Item", "Condição"],
    rows=[
        ("C1", "Notificação prévia registrada para todos os acusados."),
        ("C2", "Interrogatório realizado ou silêncio formalizado para todos, após todas as provas."),
        ("C3", "Zero pendências críticas (P1, P2, P5, P8)."),
        ("C4", "Pendências frágeis todas marcadas como revisadas (único item com insumo manual — a revisão é feita no próprio painel de Pendências, item a item, não neste checklist)."),
        ("C5", "Multiplicidades classificadas (zero pendências P4)."),
    ],
    col_widths=[1.6, 13.9],
)

add_body(
    doc,
    "Abaixo dos 5 itens, o botão \"Gerar minuta do termo de indiciação\" "
    "fica desabilitado enquanto houver qualquer pendência crítica, com a "
    "mesma mensagem já citada na Seção 3.5.",
)

add_h3(doc, "Prazos")

add_body(
    doc,
    "Calcula o **prazo de conclusão do processo** a partir da data de "
    "instauração (o mesmo campo \"Data de instauração\" da tela \"Dados do "
    "Processo\", Seção 3.1), somada ao prazo padrão do rito e a eventuais "
    "prorrogações registradas. Sem data de instauração preenchida, o "
    "painel pede que ela seja informada em vez de mostrar a barra de "
    "prazo. A barra muda de cor conforme a proximidade do vencimento "
    "(verde / âmbar com 15 dias ou menos restantes / vermelho se excedido).",
)

add_body(
    doc,
    "Quando há pendência **P6c** aberta para algum acusado, o painel exibe "
    "um aviso com link direto para o cadastro daquele acusado — e, se a "
    "cor do prazo de conclusão estiver verde, o painel força o indicador "
    "para âmbar mesmo sendo P6c uma pendência de outro assunto (intimação "
    "para o interrogatório, não prazo de conclusão do processo).",
)

add_body(
    doc,
    "Após a primeira geração bem-sucedida da minuta de indiciação, o "
    "painel de Prazos **abre automaticamente** e ganha uma subseção nova, "
    "\"Citação e defesa escrita (art. 161)\" (data da citação, meio — "
    "Pessoal ou Edital, com ajuste automático do prazo padrão de defesa —, "
    "prazo de defesa em dias, e a data calculada do termo final da defesa "
    "escrita). Esse bloco só é renderizado quando a mesma variável interna "
    "que marca \"minuta já gerada\" está ativa — por isso o painel abre "
    "sozinho justamente nesse momento: é quando ele passa a ter conteúdo "
    "novo e relevante, chamando a atenção da comissão para o prazo de "
    "defesa que passa a correr a partir da indiciação.",
)

page_break(doc)

# ---------------------------------------------------------------------------
# Seção 4 — Nexo PAR
# ---------------------------------------------------------------------------
add_chapter(doc, "Seção 4", "Nexo PAR (uso isolado)")

add_body(
    doc,
    "O **Nexo PAR** é a ferramenta de mapa fato-prova-norma da Suíte COGER para o "
    "domínio **PAR** — o Processo Administrativo de Responsabilização de entes "
    "privados, à luz da **Lei nº 12.846, de 1º de agosto de 2013** (Lei "
    "Anticorrupção — LAC). É um **fork** independente do Nexo Coger: compartilha a "
    "mesma mecânica de mapa fato-prova-norma, o mesmo design e a mesma barra "
    "lateral, mas trabalha com um objeto distinto — a **pessoa jurídica** —, um "
    "enquadramento próprio (art. 5º da LAC) e um documento final próprio, a **Nota "
    "de Indiciação**. Esta seção documenta o que **difere** do Nexo Coger; para os "
    "comportamentos herdados sem alteração, remete-se à Seção 3 (ver a nota de "
    "fecho, Seção 4.8).",
)

add_alert(
    doc,
    [
        "Três sentidos de \"nexo\" convivem nesta seção e não devem ser "
        "confundidos: **Nexo PAR** e **Nexo Coger** são nomes próprios de "
        "ferramentas; o **nexo fático-probatório** é a ligação entre um fato e as "
        "provas que o sustentam (a mecânica do mapa); e o **nexo de causalidade** é "
        "um conceito jurídico da LAC — a correlação entre o ato lesivo e o "
        "benefício ou interesse da pessoa jurídica —, que aqui vira um campo do "
        "fato (Seção 4.3).",
    ],
    kind="mono",
    label="Desambiguação — os três \"nexos\"",
)

add_h2(doc, "4.1 Identidade e Dados do Processo")

add_body(
    doc,
    "Ao abrir o Nexo PAR, aparece a mesma tela-gate **Dados do Processo** descrita "
    "na Seção 3.1, com uma diferença estrutural: o campo **Tipo de processo** já "
    "vem **fixado em PAR** — o domínio do processo é, portanto, sempre `par`, sem "
    "escolha do usuário. Os campos de portaria, datas e composição da comissão "
    "funcionam como no Nexo Coger, e, como lá, **apenas o Número do processo** "
    "libera o gate.",
)

add_body(
    doc,
    "Todos os arquivos exportados pelo Nexo PAR seguem o prefixo `nexo-par-` — a "
    "exportação geral segue `nexo-par-<número>-<data>.json` e a pauta de instrução "
    "por depoente segue `nexo-par-pauta-<número>-<depoente>-<data>.json`. Esse "
    "prefixo, somado ao campo `dominio` (`par`) emitido no envelope, é o que "
    "permite à validação de domínio na importação (Seção 6) recusar o cruzamento "
    "indevido de um arquivo PAR importado no Nexo Coger, ou vice-versa.",
)

add_h2(doc, "4.2 Cadastro do ente privado")

add_body(
    doc,
    "No lugar do cadastro de **acusado** (servidor) da Seção 3.6, o Nexo PAR "
    "cadastra o **ente privado** — a pessoa jurídica sujeita à responsabilização. "
    "Os campos do formulário aparecem nesta ordem:",
)

make_table(
    doc,
    headers=["Campo", "Rótulo exato / hint", "Obrigatoriedade"],
    rows=[
        ("Razão social", "\"Razão social\"",
         "Obrigatória — bloqueio: \"Informe a razão social do ente.\""),
        ("CNPJ", "\"CNPJ\"; hint \"14 dígitos, com ou sem máscara.\"",
         "Opcional; se preenchido, valida o formato (14 dígitos) — bloqueio: \"CNPJ inválido: informe 14 dígitos (com ou sem máscara).\""),
        ("Nome fantasia", "\"Nome fantasia (opcional)\"", "Opcional"),
        ("Faturamento bruto", "\"Faturamento bruto (opcional)\"; hint \"Base para a futura dosimetria da multa (Multa_PAR).\"",
         "Opcional"),
        ("Endereço da sede", "\"Endereço da sede (opcional)\"", "Opcional"),
    ],
    col_widths=[3.4, 7.1, 5.0],
)

add_body(
    doc,
    "Abaixo dos dados de qualificação, um bloco repetível **Representantes** "
    "registra as pessoas físicas ligadas ao ente. Cada linha tem **Nome**, **CPF "
    "(opcional)** e **Vínculo** (lista de seleção), com o botão **\"+ Adicionar "
    "representante\"**. O Vínculo oferece os **três papéis PAR** do catálogo — "
    "**Representante legal** (valor padrão), **Preposto** e "
    "**Sócio-administrador**. Enquanto nenhum representante for cadastrado, o "
    "bloco exibe o aviso \"Nenhum representante. Cadastre ao menos um "
    "representante legal (exigência P-ENTE).\".",
)

add_body(
    doc,
    "Por fim, o bloco **\"Estruturas societárias (registro, sem cálculo)\"** "
    "reúne, de forma puramente declaratória (o Nexo PAR não faz nenhum cálculo "
    "sobre eles), três registros opcionais:",
)
add_bullet(doc, "**Solidariedade — entes do mesmo grupo econômico** — bloco repetível com CNPJ, Razão social e Descrição do vínculo por linha, e o botão \"+ Adicionar ente relacionado\".")
add_bullet(doc, "**Sucessão empresarial — tipo** — lista de seleção (—, Fusão, Incorporação, Cisão), mais Descrição e Data.")
add_bullet(doc, "**Desconsideração da personalidade jurídica (art. 14 da LAC)** — checkbox \"Aplicar desconsideração da personalidade jurídica\"; quando ativada, revela o campo Fundamentação e checkboxes por representante \"atingido\" pela desconsideração.")

add_alert(
    doc,
    [
        "Cadastrar ao menos um **representante legal** é exigência do gate "
        "**P-ENTE**: a falta dele **não** impede salvar o ente, mas **bloqueia a "
        "geração da Nota de Indiciação** (Seção 4.5). Ao excluir um ente, o Nexo "
        "PAR confirma: \"Excluir este ente? As condutas vinculadas a ele nos fatos "
        "serão removidas.\".",
    ],
    kind="warn",
    label="Representante legal é exigido para indiciar",
)

figura_pendente(doc, "tela de cadastro de ente privado do Nexo PAR — razão social, CNPJ, bloco de representantes e bloco de estruturas societárias (solidariedade, sucessão, desconsideração).")

add_h2(doc, "4.3 Fato e conduta no domínio PAR")

add_body(
    doc,
    "O formulário de fato do Nexo PAR reaproveita os campos gerais da Seção 3.2 "
    "(título, descrição, período, local, condutas individualizadas, provas "
    "vinculadas, estado probatório e situação do fato), com uma diferença central "
    "no enquadramento: **não existe o campo Elemento subjetivo**. No PAD, cada "
    "enquadramento pede dolo ou culpa (Seção 3.2); no PAR, a responsabilização do "
    "ente privado é **objetiva** — independe de dolo ou culpa —, nos termos do "
    "**art. 2º da Lei nº 12.846, de 2013**. Por isso o Nexo PAR remove tanto o "
    "campo Elemento subjetivo quanto a pendência a ele associada (a P8 do Nexo "
    "Coger — ver Seção 4.5).",
)

add_body(
    doc,
    "Em seu lugar, o fato ganha o bloco **\"Interesse/benefício da PJ e nexo "
    "causal\"** (marcado com `*` quando há enquadramento LAC ativo), com o hint "
    "\"Obrigatórios quando há enquadramento LAC (pendência crítica P8-PAR se em "
    "branco).\". São dois campos:",
)
add_numbered(doc, 1, "**Interesse ou benefício da pessoa jurídica** — área de texto: em proveito de que a conduta lesiva se deu para o ente.")
add_numbered(doc, 2, "**Nexo de causalidade** — área de texto, hint \"Correlação entre o ato lesivo e o benefício/interesse apontado.\".")

add_body(
    doc,
    "Nenhum dos dois **bloqueia o salvamento** do fato — como no Nexo Coger, o "
    "fato pode ser salvo incompleto. A cobrança acontece na **geração** da Nota "
    "de Indiciação, pela pendência crítica **P8-PAR** (Seção 4.5), que dispara "
    "quando há enquadramento LAC ativo e o benefício **ou** o nexo causal está em "
    "branco.",
)

add_h2(doc, "4.4 Seletor de enquadramento — normas da LAC")

add_body(
    doc,
    "O enquadramento no Nexo PAR usa **exclusivamente** as normas da LAC (art. 5º "
    "da Lei nº 12.846, de 2013), e não o catálogo da Lei nº 8.112, de 1990, do "
    "Nexo Coger. São **11 normas**, distribuídas em **dois optgroups** — **\"Atos "
    "de corrupção em geral\"** e **\"Licitações e contratos\"** —, além do grupo "
    "residual **\"Criadas pelo usuário\"** para normas adicionadas manualmente:",
)

make_table(
    doc,
    headers=["Dispositivo", "Grupo"],
    rows=[
        ("art. 5º, I", "Atos de corrupção em geral"),
        ("art. 5º, II", "Atos de corrupção em geral"),
        ("art. 5º, III", "Atos de corrupção em geral"),
        ("art. 5º, V", "Atos de corrupção em geral"),
        ("art. 5º, IV, a", "Licitações e contratos"),
        ("art. 5º, IV, b", "Licitações e contratos"),
        ("art. 5º, IV, c", "Licitações e contratos"),
        ("art. 5º, IV, d", "Licitações e contratos"),
        ("art. 5º, IV, e", "Licitações e contratos"),
        ("art. 5º, IV, f", "Licitações e contratos"),
        ("art. 5º, IV, g", "Licitações e contratos"),
    ],
    col_widths=[5.0, 10.5],
)

add_body(
    doc,
    "Ao selecionar uma norma, sua **nota de aplicação** é exibida como hint "
    "(📌), orientando o uso do dispositivo. O rótulo mostrado é a **descrição "
    "integral** da norma (apenas sem o ponto final) — não é mais truncado como em "
    "versões anteriores, de modo que a frase aparece por inteiro tanto no seletor "
    "quanto na Nota de Indiciação.",
)

add_h2(doc, "4.5 Catálogo de pendências do fork")

add_body(
    doc,
    "O Nexo PAR herda a maior parte do catálogo de pendências da Seção 3.5, "
    "adaptando os textos que falam em \"acusado\" para \"ente privado\", "
    "**removendo** a P8 (que dependia de dolo/culpa, inexistentes no PAR) e "
    "**acrescentando** duas pendências críticas próprias, **P8-PAR** e "
    "**P-ENTE**:",
)

make_table(
    doc,
    headers=["Código", "Nível", "Descrição"],
    rows=[
        ("P1", "crítico", "Fato sem prova vinculada — alegação sem evidência (mantida, salvo override de estado probatório justificado)."),
        ("P2", "crítico*", "Fato sem enquadramento legal (*crítica a partir da indiciação em diante)."),
        ("P3", "frágil", "Prova órfã — não sustenta nenhum fato do mapa."),
        ("P4", "pendente", "Multiplicidade de enquadramentos não classificada: concurso formal ou conflito aparente?"),
        ("P5", "crítico", "Conduta não individualizada — risco de indiciação genérica (nulidade)."),
        ("P6a", "frágil", "Prova emprestada com pendência formal (certidão/autorização)."),
        ("P6b", "frágil", "Ente privado não intimado da produção desta prova (contraditório) — reescrita a partir da P6b do Nexo Coger, que falava em \"acusado\"."),
        ("P7", "frágil", "Sustentação exclusivamente indiciária/informal — explicitar raciocínio indutivo."),
        ("P8", "removida", "Não existe no PAR — a responsabilização é objetiva (art. 2º da LAC), sem dolo ou culpa a aferir."),
        ("P8-PAR", "crítico", "Fato com enquadramento LAC sem descrição de benefício/interesse ou nexo causal (nova — dispara com enquadramento ativo e benefício OU nexo em branco)."),
        ("P-ENTE", "crítico", "Processo sem ente privado cadastrado, ou ente privado sem representante legal cadastrado (nova — bloqueia a geração)."),
    ],
    col_widths=[2.1, 2.2, 11.2],
)

add_body(
    doc,
    "A pendência **P6c** do Nexo Coger (antecedência de intimação para "
    "interrogatório, art. 41 da Lei nº 9.784, de 29 de janeiro de 1999) permanece "
    "no código, mas **sem interface no PAR** — o ente privado não é interrogado. O "
    "checklist de encerramento acompanha as mudanças: **C1** \"Ente privado "
    "cadastrado com representante legal\"; **C2** \"Benefício/interesse e nexo "
    "causal descritos em todo fato com enquadramento LAC\"; **C3** \"Zero "
    "pendências críticas (P1, P2, P5, P8-PAR, P-ENTE)\".",
)

add_h2(doc, "4.6 Geração da Nota de Indiciação")

add_alert(
    doc,
    [
        "A geração da **Nota de Indiciação** é um **ato final** da instrução — "
        "produz o documento formal que imputa ao ente privado a conduta lesiva e "
        "abre o prazo de defesa. Não a gere prematuramente, antes que fatos, "
        "provas, enquadramentos e o cadastro do ente estejam consolidados.",
    ],
    kind="danger",
    label="Ato final — use com cautela",
)

add_body(
    doc,
    "Antes de gerar, o Nexo PAR roda uma checagem de campos essenciais "
    "(`validaMinuta`) e lista o que faltar, sem gerar nada até que esteja "
    "completo: **razão social** do ente, ao menos um **representante legal** "
    "cadastrado, e ao menos um **fato ativo** imputado. Pendências críticas (P1, "
    "P2, P5, P8-PAR, P-ENTE) bloqueiam a geração, como no Nexo Coger.",
)

add_body(
    doc,
    "A Nota de Indiciação gerada — cujo conteúdo mínimo atende ao **art. 17 da "
    "Instrução Normativa CGU nº 13, de 2019** — traz, nesta ordem:",
)
add_numbered(doc, 1, "**Cabeçalho institucional** — órgão, corregedoria, o título \"Nota de Indiciação\", a identificação do \"Processo Administrativo de Responsabilização (PAR) nº …\", a referência à Lei nº 12.846, de 2013 (LAC), a portaria e a linha \"Pessoa jurídica: <razão social>, CNPJ <…>\".")
add_numbered(doc, 2, "**Tabela de qualificação do ente** — razão social, CNPJ, nome fantasia e endereço da sede (quando houver) e representante legal; se a desconsideração da personalidade jurídica estiver ativa, um parágrafo em itálico invoca o art. 14 da LAC.")
add_numbered(doc, 3, "**\"Da conduta lesiva imputada ao ente privado\"** — por fato: descrição, conduta individualizada (comissiva/omissiva) e, quando preenchidos, \"Interesse ou benefício da pessoa jurídica:\" e \"Nexo de causalidade:\".")
add_numbered(doc, 4, "**\"Das provas\"** — por fato, com índice numerado e trechos significativos.")
add_numbered(doc, 5, "**\"Do enquadramento legal\"** — por fato, \"a conduta amolda-se ao <dispositivo> (<rótulo>)\", **sem** elemento subjetivo; trata concurso formal / conflito aparente quando houver multiplicidade.")
add_numbered(doc, 6, "**\"Síntese dos fatos, provas e enquadramentos\"** — tabela-resumo.")
add_numbered(doc, 7, "**\"Das alegações da defesa não acatadas\"** — bloco editável.")
add_numbered(doc, 8, "**\"Da multa, do faturamento bruto e do programa de integridade\"** — os quatro textos complementares fixos (abaixo).")
add_numbered(doc, 9, "**\"Do encerramento\"** — ressalva de adequação do enquadramento; a intimação para defesa \"no prazo de 30 (trinta) dias\" (art. 17 da IN CGU nº 13, de 2019); cidade/data; e o bloco de assinatura em três colunas.")

add_body(doc, "Os quatro textos complementares fixos da seção 8, reproduzidos literalmente:")
add_alert(
    doc,
    [
        "Faculta-se expressamente à pessoa jurídica indiciada apresentar "
        "informações e provas relativas aos parâmetros de cálculo da multa e ao "
        "seu faturamento bruto no exercício anterior ao da instauração do processo.",
        "Solicitam-se, ainda, informações e documentos necessários à análise do "
        "parâmetro previsto no inciso IV do art. 22 do Decreto nº 11.129, de 11 de "
        "julho de 2022.",
        "Fica assegurado o prazo de 30 (trinta) dias para apresentação de defesa "
        "escrita, contado da intimação desta Nota de Indiciação, podendo a pessoa "
        "jurídica apresentar, em conjunto com a defesa, evidências da existência e "
        "do funcionamento de programa de integridade, nos termos da Portaria CGU "
        "nº 909, de 7 de abril de 2025.",
        "Registra-se, por fim, a possibilidade de resolução negociada do processo, "
        "por meio de Termo de Compromisso ou de Acordo de Leniência, na forma da "
        "legislação de regência.",
    ],
    kind="mono",
    label="Textos complementares fixos da Nota de Indiciação",
)

figura_pendente(doc, "Nota de Indiciação PAR gerada — cabeçalho institucional, tabela de qualificação do ente privado e a seção \"Da multa, do faturamento bruto e do programa de integridade\".")

add_h2(doc, "4.7 Toolbar lateral — prazos do rito PAR")

add_body(
    doc,
    "A barra lateral do Nexo PAR é a mesma da Seção 3.9 (Pendências, Ordem dos "
    "fatos, Checklist de encerramento e Prazos). A diferença está nos **textos e "
    "prazos** do painel **Prazos**, adaptados do rito PAD para o rito PAR:",
)

add_bullet(doc, "**Prazo confirmado** — o painel substitui a lógica PAD de citação pessoal/edital (10/15 dias, Lei nº 8.112, de 1990) pelo bloco **\"Intimação da Nota de Indiciação e defesa escrita\"**, com o hint \"Prazo de 30 dias para defesa escrita a contar da intimação da Nota de Indiciação (art. 17, IN CGU nº 13, de 2019).\". É o único prazo PAR com fonte normativa confirmada.")
add_bullet(doc, "**Prazo de conclusão do processo** — mantém o mesmo cálculo do PAD (data de instauração + prazo em dias, editável), por ausência de fonte normativa PAR fornecida. O hint do campo é explícito: \"Prazo de conclusão do processo em dias (editável). Fonte do prazo do PAR não fornecida nesta rodada.\".")

add_alert(
    doc,
    [
        "O prazo de **conclusão do processo** no PAR usa o mesmo cálculo do PAD "
        "**por ausência de fonte normativa PAR fornecida — não se inventa prazo**. "
        "O único prazo PAR com fonte confirmada é o de 30 dias para a defesa "
        "escrita, no bloco de intimação da Nota de Indiciação. Trate o prazo de "
        "conclusão como um valor editável de referência, não como um marco legal "
        "PAR consolidado.",
    ],
    kind="warn",
    label="Prazo de conclusão sem fonte PAR confirmada",
)

add_h2(doc, "4.8 O que NÃO muda em relação ao Nexo Coger")

add_alert(
    doc,
    [
        "Para o leitor que já conhece o Nexo Coger (Seção 3), estes comportamentos "
        "são herdados **sem alteração** no Nexo PAR, e não precisam ser relidos: a "
        "**mecânica do mapa fato-prova-norma** (vínculo fato-prova-norma, arestas, "
        "provas órfãs, estado probatório calculado); a **importação de provas do "
        "Veritas** e a **importação de retorno de oitiva** do Oitiva 360; a "
        "**exportação de pauta** de instrução por depoente; o **selo 🎙** de origem "
        "em oitiva; a **barra lateral** (exceto os textos e prazos do painel "
        "Prazos, Seção 4.7); e todo o **design system**. Os contratos de "
        "integração e a validação de domínio na importação são detalhados na "
        "Seção 6.",
    ],
    kind="green",
    label="Herdado do Nexo Coger sem alteração",
)

page_break(doc)

# ---------------------------------------------------------------------------
# Seção 5 — Oitiva 360
# ---------------------------------------------------------------------------
add_chapter(doc, "Seção 5", "Oitiva 360 (uso isolado)")

add_body(
    doc,
    "O **Oitiva 360** apoia a condução de oitivas e interrogatórios: gera um "
    "roteiro de perguntas a partir do papel do depoente e da infração apurada, "
    "registra as respostas dadas durante a sessão e produz o termo de redução "
    "correspondente.",
)

add_body(
    doc,
    "O Oitiva 360 opera em **modo dual**: um único arquivo que acomoda tanto o "
    "domínio **PAD** — apuração de responsabilidade de servidores à luz da **Lei "
    "nº 8.112, de 11 de dezembro de 1990** — quanto o domínio **PAR** — "
    "responsabilização de entes privados à luz da **Lei nº 12.846, de 1º de agosto "
    "de 2013** (Lei Anticorrupção — LAC). O domínio do processo em curso "
    "condiciona quatro coisas: os **papéis de depoente** disponíveis, a lista de "
    "**categorias de infração**, os **blocos do banco de perguntas** e os itens do "
    "**checklist**. Tudo o mais — a estrutura de etapas, a geração do termo, o Kit "
    "de Incidentes, o Cartão de Mesa e o cálculo de hash na exportação — é "
    "idêntico nos dois domínios.",
)

add_alert(
    doc,
    [
        "O termo \"nexo\" não aparece como conceito próprio do Oitiva 360; quando "
        "surgir nesta seção, será sempre parte do nome de uma ferramenta receptora "
        "(**Nexo Coger**, no domínio PAD, ou **Nexo PAR**, no domínio PAR) para "
        "onde o Oitiva 360 exporta pauta e retorno.",
    ],
    kind="mono",
    label="Nota terminológica — \"nexo\" nesta seção",
)

add_body(
    doc,
    "No canto superior da tela, um **chip de domínio** (PAD, em azul-marinho, ou "
    "PAR, em dourado) indica sempre o domínio corrente do processo. Ele reflete "
    "diretamente o campo **Domínio do processo** da Matriz de Apuração (Seção 5.1) "
    "e acompanha em tempo real qualquer troca de domínio — manual ou derivada da "
    "pauta importada.",
)

add_h2(doc, "5.1 Pré-requisito — Matriz de Apuração")

figura_ajustada(
    doc,
    os.path.join(SHOTS, "oitiva-matriz-apuracao.png"),
    "Cartão \"Matriz de Apuração\" — pré-requisito obrigatório antes de adicionar depoentes.",
)

add_body(
    doc,
    "Antes de adicionar qualquer depoente, o Oitiva 360 exige o preenchimento "
    "completo do cartão **\"Matriz de Apuração (nível processo — obrigatória)\"**, "
    "com 4 campos de conteúdo, todos obrigatórios:",
)
add_numbered(doc, 1, "**Conduta investigada** — \"Qual ação ou omissão está sendo apurada?\"")
add_numbered(doc, 2, "**Investigado** — \"Quem está, em tese, vinculado à conduta?\"")
add_numbered(doc, 3, "**Elementos disponíveis** — \"Que provas/informações já constam dos autos?\"")
add_numbered(doc, 4, "**Hipótese investigativa** — \"Qual a linha de raciocínio que conecta os fatos?\"")

add_alert(
    doc,
    [
        "Preencha os quatro campos da Matriz de Apuração acima para habilitar a "
        "adição de depoentes — \"roteiro sem matriz é roteiro cego\".",
    ],
    kind="warn",
    label="Mensagem do Oitiva 360",
)

add_body(
    doc,
    "Enquanto a matriz não estiver completa, o botão \"Adicionar depoente\" "
    "permanece desabilitado. O próprio código faz uma dupla checagem no clique, "
    "por segurança.",
)

add_h3(doc, "Campo Domínio do processo — a cascata de definição")

add_body(
    doc,
    "A Matriz de Apuração traz ainda um **5º campo**, **\"Domínio do processo\"** "
    "(uma lista de seleção com os valores **PAD** e **PAR**), que decide se o "
    "processo corre no rito disciplinar (Lei nº 8.112, de 1990) ou no rito de "
    "responsabilização de entes privados (Lei nº 12.846, de 2013). É esse campo "
    "que sensibiliza os papéis, as categorias de infração, os blocos de perguntas "
    "e o checklist descritos adiante. Um processo novo nasce no domínio **PAD**. O "
    "valor efetivo do campo é definido por uma **cascata** de quatro estágios:",
)

add_numbered(doc, 1, "**Definição manual** — enquanto não houver pauta importada com domínio, o campo é uma lista **editável**: a comissão escolhe PAD ou PAR diretamente.")
add_numbered(doc, 2, "**Derivação pela pauta** — ao importar uma pauta do Nexo Coger (domínio `pad`) ou do Nexo PAR (domínio `par`), o Oitiva 360 **deriva** o domínio do processo do envelope da pauta e alinha o campo a esse valor.")
add_numbered(doc, 3, "**Trava pela pauta** — uma vez derivado da pauta, o campo fica **travado** (exibido, mas não editável), com o aviso \"🔒 Domínio derivado da pauta importada do Nexo — não editável enquanto a pauta estiver vinculada.\". A trava impede que o domínio derivado divirja da origem da pauta.")
add_numbered(doc, 4, "**Confirmação de conflito** — se a pauta importada trouxer um domínio **diferente** de um domínio já definido manualmente no processo, o Oitiva 360 **pede confirmação antes de qualquer alteração** (ver a caixa abaixo). Cancelar recusa a importação inteira, de forma atômica; confirmar troca o domínio e trava o campo na origem da pauta.")

add_alert(
    doc,
    [
        "**Troca manual com dados já cadastrados.** Se a comissão troca o domínio "
        "manualmente e já existem depoentes com papel ou categoria de infração de "
        "outro domínio, o Oitiva 360 exibe, **antes de aplicar**, um "
        "\"Trocar o domínio do processo para <PAD/PAR> afeta dados já "
        "cadastrados:\" que discrimina: as categorias de **infração** de outro "
        "domínio, que **serão LIMPAS** (voltam a \"não definida\"), e os **papéis** "
        "que não existem no novo domínio, que **serão MANTIDOS** (o dado não é "
        "apagado), apenas sinalizados \"fora do domínio\" para reclassificação. "
        "Recusar a confirmação reverte a seleção e nada é alterado.",
    ],
    kind="warn",
    label="Troca de domínio — nada é apagado silenciosamente",
)

add_alert(
    doc,
    [
        "**Conflito de domínio na importação de pauta.** Quando a pauta importada "
        "diverge do domínio manual já definido, o Oitiva 360 pergunta: "
        "\"Conflito de domínio na importação da pauta. A pauta importada é de "
        "domínio <origem>, mas este processo está configurado como <atual>. "
        "Confirmar TROCA o domínio do processo (…) e importa a pauta. Cancelar "
        "RECUSA a importação inteira — nenhum item de pauta será importado.\". Ao "
        "cancelar, a importação é recusada de forma **atômica** (nada é gravado) e "
        "aparece a mensagem-padrão de recusa por domínio (Seção 6.6).",
    ],
    kind="info",
    label="Conflito pauta × domínio manual",
)

figura_pendente(doc, "cartão Matriz de Apuração do Oitiva 360 com o 5º campo \"Domínio do processo\" (PAD/PAR) e o aviso de trava \"🔒 derivado da pauta\" quando há pauta importada vinculada.")

add_h2(doc, "5.2 Diálogo \"Adicionar depoente\"")

add_body(doc, "O diálogo pede apenas 2 campos, ambos obrigatórios:")
add_numbered(doc, 1, "**Identificação** — texto livre (placeholder: *Ex.: T-01 ou \"Depoente A\"*), com aviso: \"Use iniciais ou nome fictício — evite dados pessoais reais (LGPD).\".")
add_numbered(doc, 2, "**Elementos buscados com este depoente** — área de texto, com o apoio \"Por que ouvir ESTA pessoa? O que ela pode trazer?\".")

add_body(
    doc,
    "Se qualquer um dos dois estiver vazio, o Oitiva 360 bloqueia com "
    "\"Identificação e 'elementos buscados' são obrigatórios para adicionar o "
    "depoente.\".",
)

add_h2(doc, "5.3 Etapa 1 — Dados do Ato")

add_body(
    doc,
    "Todos os campos desta etapa são opcionais (não há validação bloqueante ao "
    "avançar). Reúnem os **dados herdados do processo** — número do processo, "
    "portaria, presidente, secretário(a) e vogais (nome/cargo/matrícula de cada "
    "um) — e os **dados do ato**: data, hora, local; **Modalidade** (Presencial "
    "ou Videoconferência); checkbox \"Há defensor constituído presente?\" (que, "
    "se marcada, revela nome e OAB do defensor); e um cartão opcional de "
    "\"Estratégia da equipe\" (quem pergunta, quem revisa, formato de abertura e "
    "momento de exibição de documentos).",
)

add_h2(doc, "5.4 Etapa 2 — Depoente")

add_body(
    doc,
    "Reforça o aviso de LGPD (\"Recomendamos usar iniciais ou nome fictício. "
    "Esta ferramenta não deve armazenar dados pessoais reais dos envolvidos\") e "
    "pede novamente **Identificação** e **Elementos buscados com este "
    "depoente**.",
)

add_body(
    doc,
    "A lista de **Papel do depoente** é **filtrada pelo domínio do processo** "
    "(Seção 5.1). Quatro papéis são **comuns** aos dois domínios; a diferença "
    "está no polo passivo: no PAD existe o papel **Investigado/Acusado**, que "
    "**não existe no domínio PAR** — em seu lugar entram os três papéis do ente "
    "privado. A tabela abaixo mostra os dois lados:",
)
make_table(
    doc,
    headers=["Papel", "Domínio", "Descrição resumida"],
    rows=[
        ("Testemunha", "PAD e PAR", "Presta compromisso legal (art. 342, CP); dever de depor."),
        ("Declarante/Informante", "PAD e PAR", "Não presta compromisso; colaboração voluntária."),
        ("Pessoa em Situação Indefinida", "PAD e PAR", "Envolvimento possível, sem elementos para tratar como investigada; silêncio facultado por cautela."),
        ("Vítima", "PAD e PAR", "Não presta compromisso; sujeita-se à denunciação caluniosa."),
        ("Investigado/Acusado", "só PAD", "Não presta compromisso; direito ao silêncio (Lei nº 13.869, de 5 de setembro de 2019); interrogatório como último ato (art. 159). NÃO aparece no domínio PAR."),
        ("Representante legal", "só PAR", "Pessoa física que representa legalmente o ente privado (papel PAR do catálogo)."),
        ("Preposto", "só PAR", "Pessoa física que age em nome do ente privado (papel PAR do catálogo)."),
        ("Sócio-administrador", "só PAR", "Sócio com poderes de administração do ente privado (papel PAR do catálogo)."),
    ],
    col_widths=[4.0, 2.4, 9.1],
)

add_alert(
    doc,
    [
        "Um depoente cadastrado com um papel que **não existe** no domínio atual "
        "(por exemplo, um depoente \"Investigado/Acusado\" após a troca do "
        "processo para PAR) **não é apagado**: continua no estado, ainda aparece "
        "marcado no seletor e na lista de depoentes, mas recebe o rótulo \"fora do "
        "domínio\" para que a comissão o reclassifique. É o mesmo comportamento da "
        "cascata de domínio descrito na Seção 5.1.",
    ],
    kind="info",
    label="Papel fora do domínio é preservado, só sinalizado",
)

add_body(
    doc,
    "Selecionar \"Testemunha\" com a infração \"art. 132, IV — enriquecimento "
    "ilícito\" (domínio PAD) revela um cartão adicional, \"Terceiro interposto\", "
    "com a checkbox \"Este depoente é possível terceiro interposto (familiar/pessoa "
    "em cujo nome está bem sob suspeita)\".",
)

add_body(
    doc,
    "O campo **Categoria de infração** é uma lista de seleção com um campo de "
    "busca ao lado (por rótulo ou dispositivo — ex.: \"sigilo\", \"art. 117, "
    "IX\"), cujo conteúdo **depende do domínio do processo**:",
)
add_bullet(doc, "**No domínio PAD** — a lista traz as normas da **Lei nº 8.112, de 1990**, e da LAI (**Lei nº 12.527, de 18 de novembro de 2011**), agrupadas por origem normativa, na mesma ordem vista no Nexo Coger: Lei 8.112/90 — Deveres (art. 116); Proibições (art. 117); Demissão (art. 132); Outras (art. 130); LAI; e Outras categorias.")
add_bullet(doc, "**No domínio PAR** — a lista é substituída pelas **11 normas da LAC** (art. 5º da Lei nº 12.846, de 2013), distribuídas em dois optgroups — \"Atos de corrupção em geral\" e \"Licitações e contratos\" — exatamente como o seletor de enquadramento do Nexo PAR (Seção 4.4). Ao selecionar uma norma LAC, sua **nota de aplicação** aparece como hint (📌).")

add_body(
    doc,
    "Há ainda um cartão opcional \"Perfil do depoente\", com **Nível de "
    "conhecimento dos fatos** (Não definido, Presenciou diretamente, Ouviu de "
    "participante direto, Teve acesso a documentos/registros, Ouviu dizer) e "
    "**Vínculos com investigado/vítima/administração** (texto livre).",
)

add_body(
    doc,
    "Para avançar da Etapa 2 para a Etapa 3, são exigidos exatamente **4 "
    "campos**: Identificação, Elementos buscados, Papel do depoente e Categoria "
    "de infração. Faltando algum, o usuário permanece na Etapa 2 e vê a "
    "mensagem \"Para avançar, preencha: \" seguida da lista dos itens "
    "faltantes.",
)

add_h2(doc, "5.5 Registro de perguntas e respostas")

add_h3(doc, "Etapa 3 — Montagem do Roteiro")

add_body(
    doc,
    "O roteiro é **gerado automaticamente** a partir da combinação de papel + "
    "infração (e, se aplicável, da marcação de terceiro interposto), organizado "
    "em 13 blocos fixos (Preparação e cenário; Acolhimento e identificação dos "
    "presentes; Abertura formal; Avisos legais e LGPD; Qualificação, praxe e "
    "compromisso/advertências; Abertura para objeções da defesa; Contexto "
    "funcional; Materialidade; Autoria e participação; Elemento subjetivo "
    "(dolo/culpa); Circunstâncias do art. 128; Palavra à defesa/reperguntas; "
    "Fechamento). Nesta etapa o usuário pode adicionar, editar ou remover "
    "perguntas — as perguntas de praxe da testemunha são fixas e não podem ser "
    "removidas. Um botão \"Regenerar roteiro\" substitui todas as perguntas "
    "atuais (inclusive as adicionadas manualmente) pelas sugestões do banco, "
    "mediante confirmação. **Não há registro de resposta nesta etapa.**",
)

add_body(
    doc,
    "O **banco de perguntas é sensível ao domínio**. No domínio PAD, aparecem os "
    "blocos próprios do rito disciplinar — inclusive \"Elemento subjetivo "
    "(dolo/culpa)\" e \"Circunstâncias do art. 128\", institutos exclusivos do PAD "
    "(a responsabilização do ente privado é objetiva, art. 2º da Lei nº 12.846, de "
    "2013, e não perquire dolo ou culpa). No domínio PAR, esses dois blocos PAD "
    "deixam de ser oferecidos e surgem **três blocos de perguntas próprios da "
    "LAC**, descritos aqui por finalidade (as perguntas literais ficam no banco da "
    "ferramenta):",
)
add_bullet(doc, "**Licitações e contratos** — explora as condutas do art. 5º, IV, da LAC: frustração ou fraude ao caráter competitivo de licitação, afastamento de licitante, fraude a contrato administrativo e manipulação do equilíbrio econômico-financeiro do contrato.")
add_bullet(doc, "**Terceiro interposto** — investiga a atuação por interposta pessoa e a ocultação de reais beneficiários (art. 5º, III e II, da LAC): quem intermediou, em nome de quem, e qual o proveito do ente privado.")
add_bullet(doc, "**Programa de integridade** — apura a existência, a abrangência e o funcionamento efetivo do programa de integridade (compliance) do ente, elemento relevante para a dosimetria da futura multa.")

add_h3(doc, "Etapa 4 — Respostas registradas")

figura_ajustada(
    doc,
    os.path.join(SHOTS, "oitiva-rodada-perguntas-respostas.png"),
    "Etapa 4 — registro das respostas dadas pelo depoente, uma pergunta por vez.",
)

add_body(
    doc,
    "Para cada pergunta do roteiro, o Oitiva 360 mostra o texto da pergunta e "
    "**uma única área de texto** para a resposta, com o placeholder \"Resposta "
    "dada pelo(a) depoente\".",
)

add_alert(
    doc,
    [
        "Não existe campo auxiliar de observação nem de marcação de relevância "
        "por pergunta — o único controle disponível, por pergunta, é a área de "
        "texto da resposta. Se sua rotina de trabalho pressupõe anotar "
        "observações à parte, registre-as em outro documento; o Oitiva 360 não "
        "oferece esse campo.",
    ],
    kind="info",
)

add_body(
    doc,
    "Se o papel do depoente tiver direito ao silêncio e esse direito tiver sido "
    "exercido, a seção inteira exibe apenas o texto \"Direito ao silêncio "
    "exercido — nenhuma pergunta foi dirigida ao(à) depoente nesta sessão.\", "
    "sem áreas de resposta.",
)

add_h2(doc, "5.6 Geração do termo")

figura_ajustada(
    doc,
    os.path.join(SHOTS, "oitiva-termo-final.png"),
    "Termo de redução gerado automaticamente ao entrar na Etapa 4.",
)

add_body(
    doc,
    "O termo é **gerado automaticamente ao entrar na Etapa 4**, sem nenhum "
    "portão formal de bloqueio — não há checagem que impeça a geração por "
    "campos vazios. Campos ainda não preenchidos (hora, local, portaria, "
    "presidente, vogais, secretário, nome) aparecem no texto gerado como "
    "traços de preenchimento (\"____\"), em vez de impedir a geração.",
)

add_body(doc, "A estrutura do termo gerado segue, nesta ordem:")
add_bullet(doc, "Cabeçalho — \"TERMO DE INTERROGATÓRIO\" (acusado), \"TERMO DE OITIVA DE TESTEMUNHA\" (testemunha) ou \"TERMO DE OITIVA\" (demais papéis).")
add_bullet(doc, "Parágrafo de abertura/qualificação — data por extenso, hora, local, portaria, composição da comissão, nome do depoente e papel.")
add_bullet(doc, "Parágrafo de qualificação civil/funcional.")
add_bullet(doc, "Parágrafo de compromisso/advertências — varia conforme o papel (compromisso legal para testemunha; silêncio constitucional para acusado; silêncio por cautela para pessoa em situação indefinida; isenção de compromisso com advertência de denunciação caluniosa para vítima; colaboração voluntária para declarante/informante).")
add_bullet(doc, "Corpo de perguntas e respostas, na ordem do roteiro.")
add_bullet(doc, "Fecho fixo de encerramento e bloco de assinaturas (Presidente, Vogal(is), Secretário(a)).")

add_body(
    doc,
    "O texto do termo pode ser editado diretamente na área de texto do próprio "
    "termo (edições manuais ficam salvas); um botão \"Regenerar termo\" "
    "substitui o texto atual (inclusive edições manuais) pelo modelo padrão, "
    "mediante confirmação.",
)

add_h2(doc, "5.7 Checklist pré-oitiva e alertas de nulidade")

add_body(
    doc,
    "Ainda na Etapa 4, o **Checklist pré-oitiva** reúne itens sempre aplicáveis "
    "(revisão da matriz, intimação regular, roteiro revisado, documentos "
    "separados, ambiente e trajes adequados) mais itens condicionais conforme o "
    "papel do depoente (por exemplo, para o papel Acusado: notificação com 3 "
    "dias úteis de antecedência, interrogatório como último ato, advertências "
    "obrigatórias), a modalidade (videoconferência: teste de conexão, avisos de "
    "gravação/LGPD) e a infração (enriquecimento ilícito: documentação "
    "patrimonial, identificação de terceiros interpostos).",
)

add_body(
    doc,
    "Os **Alertas de nulidade** comparam os itens de checklist obrigatórios "
    "para o papel selecionado contra os já marcados: se houver pendentes, "
    "lista-os; se todos estiverem confirmados, mostra confirmação positiva; se "
    "o papel não tiver exigências específicas, mostra um texto neutro.",
)

add_body(
    doc,
    "No **domínio PAR**, o checklist ganha itens condicionais próprios, cruzando "
    "o **papel PAR** do depoente com o **grupo de ato lesivo** apurado, mais um "
    "item **transversal** que aparece em toda combinação PAR — a confirmação de "
    "que o **benefício/interesse do ente e o nexo de causalidade** (art. 2º da Lei "
    "nº 12.846, de 2013) estão descritos. Nenhum desses itens ativa em processos "
    "PAD:",
)
make_table(
    doc,
    headers=["Condição (domínio PAR)", "Quando o item entra no checklist"],
    rows=[
        ("Transversal — benefício/nexo causal", "Sempre que o processo está no domínio PAR, em qualquer combinação de papel e infração."),
        ("Papel PAR (qualquer)", "Depoente com papel Representante legal, Preposto ou Sócio-administrador."),
        ("Sócio-administrador", "Depoente especificamente no papel Sócio-administrador."),
        ("Representante legal", "Depoente especificamente no papel Representante legal."),
        ("Grupo \"Licitações e contratos\"", "Infração enquadrada em uma norma LAC do grupo de licitações e contratos (art. 5º, IV)."),
        ("Ato de terceiro interposto (art. 5º, III)", "Infração enquadrada na norma da LAC de terceiro interposto/ocultação de beneficiário."),
    ],
    col_widths=[5.5, 10.0],
)

add_h2(doc, "5.8 Gerenciar múltiplos depoentes")

add_body(
    doc,
    "Antes de entrar no wizard de qualquer depoente específico, a Tela do "
    "Processo mostra a **lista de depoentes já cadastrados** — colunas "
    "Identificação, Papel, Infração, Status e ações. O **Status** exibido "
    "é o do progresso do próprio depoente no wizard (\"Rascunho\", "
    "\"Roteiro pronto\" ou \"Oitiva realizada\") — não é o mesmo conceito "
    "do status de item de pauta tratado na Seção 5.11 abaixo. Se não houver "
    "nenhum depoente ainda, a lista mostra \"Nenhum depoente adicionado "
    "ainda.\".",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "oitiva-lista-depoentes.png"),
    "Lista de depoentes cadastrados na Tela do Processo.",
)

add_body(
    doc,
    "Cada linha da lista tem dois botões: **\"Abrir depoente\"** e "
    "**\"Remover\"**. Não existe navegação de \"próximo/anterior\" entre "
    "depoentes — para alternar, é preciso fechar o wizard do depoente atual "
    "(o que devolve à lista) e clicar em \"Abrir depoente\" na linha "
    "desejada.",
)

add_alert(
    doc,
    [
        "Reabrir um depoente já cadastrado **sempre volta para a Etapa 1 "
        "(\"Dados do Ato\")**, mesmo que o wizard já esteja concluído "
        "(\"Oitiva realizada\") — não há memória da última etapa visitada. "
        "É preciso navegar manualmente pelo stepper (1 → 2 → 3 → 4) até a "
        "etapa que se deseja editar; os dados já preenchidos permanecem "
        "salvos e apenas são re-renderizados.",
    ],
    kind="warn",
    label="Edição sempre reabre na Etapa 1",
)

add_body(
    doc,
    "A remoção de um depoente é feita apenas pelo botão \"Remover\" da "
    "lista (não há atalho de remoção de dentro do wizard) e pede "
    "confirmação: \"Remover o depoente '<identificação>'? Esta ação não "
    "pode ser desfeita.\". Não há lixeira nem desfazer — a remoção é "
    "definitiva a partir da confirmação.",
)

add_h2(doc, "5.9 Kit de Incidentes")

add_body(
    doc,
    "O **Kit de Incidentes** é um banco de **17 fórmulas verbais prontas**, "
    "agrupadas por categoria (Postura da defesa, Depoimento do depoente, "
    "Condução do ato, Cuidado com o depoente, Táticas de desestabilização "
    "etc.), para o condutor da sessão usar diante de situações específicas "
    "durante a oitiva ou o interrogatório — contradita, intimidação, "
    "pergunta ofensiva, pergunta indutiva, imprecisão do depoente, "
    "contradição/possível falso testemunho, questão de ordem, abalo "
    "emocional, entre outras.",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "oitiva-kit-situacoes.png"),
    "Kit de Incidentes — painel lateral com fórmulas verbais agrupadas por categoria.",
)

add_body(
    doc,
    "Fica disponível como **painel lateral fixo, sempre visível, nas "
    "Etapas 3 e 4** do wizard — o presidente consulta a fórmula sugerida "
    "durante a sessão, sem precisar buscar.",
)

add_alert(
    doc,
    [
        "O Kit de Incidentes é **puramente conteúdo de apoio ao vivo** — "
        "consultá-lo não grava nada no processo. Não é um botão de ação "
        "nem um formulário; é só a fórmula verbal pronta para o presidente "
        "usar na hora.",
    ],
    kind="info",
)

add_h2(doc, "5.10 Cartão de Mesa")

add_body(
    doc,
    "O botão **\"Imprimir Cartão de Mesa\"**, na Etapa 4 (\"Revisão e "
    "Checklist\"), gera uma versão impressa do Kit de Incidentes: uma "
    "**grade de duas colunas** com a situação (em negrito) e a fórmula "
    "verbal completa de cada um dos 17 itens do Kit.",
)

figura_ajustada(
    doc,
    os.path.join(SHOTS, "oitiva-cartao-mesa.png"),
    "Cartão de Mesa — impressão em grade de duas colunas do Kit de Incidentes.",
)

add_body(
    doc,
    "O Cartão de Mesa **não traz dados do processo, do depoente ou do "
    "roteiro** — é o Kit de Incidentes inteiro, compactado para caber numa "
    "folha de consulta rápida sobre a mesa da comissão. O rodapé da "
    "impressão traz o texto **\"Uso interno · Consulta rápida durante o "
    "ato\"**, confirmando que o documento se destina a ser consultado "
    "durante a sessão — não é um registro/anexo do processo.",
)

add_h2(doc, "5.11 Status da pauta")

add_body(
    doc,
    "Quando há uma pauta importada do Nexo Coger, cada item da pauta passa "
    "por três estados possíveis, calculados em tempo real (não são um "
    "campo gravado com esses nomes):",
)

make_table(
    doc,
    headers=["Status", "Quando ocorre"],
    rows=[
        ("pendente", "Estado inicial de todo item, ao importar a pauta — enquanto nenhum depoente tiver selecionado esse ponto para abordar."),
        ("em_andamento", "Assim que algum depoente cadastrado marca o item da \"Pauta do Nexo\" como algo a abordar nesta sessão (Etapa 2 do wizard daquele depoente)."),
        ("concluida", "Só ao marcar a checkbox \"Marcar oitiva como realizada\", na Etapa 4 do depoente — nunca antes, nunca automaticamente."),
    ],
    col_widths=[3.5, 12.0],
)

add_body(
    doc,
    "Ao marcar \"Marcar oitiva como realizada\", cada item selecionado por "
    "aquele depoente é fechado como \"abordado\" (resposta de fato "
    "registrada) ou \"sem resposta\" (se marcado explicitamente sem "
    "resposta), e o depoente passa a status \"Oitiva realizada\". "
    "Desmarcar essa checkbox reverte apenas o status do depoente — não "
    "reverte o status já fechado do item de pauta.",
)

add_h2(doc, "5.12 Exportações e o campo de domínio")

add_body(
    doc,
    "Os dois contratos de saída do Oitiva 360 — o **termo** exportado para o "
    "Veritas (\"Exportar termo para o Veritas\") e o **retorno** exportado para o "
    "Nexo (\"Exportar retorno (contexto do acusado)\" e \"Exportar prova(s) para o "
    "Nexo\") — carregam, no envelope, o campo **`dominio`** (`pad` ou `par`), "
    "derivado do domínio corrente do processo (Seção 5.1). Quando o domínio ainda "
    "não está definido, o campo é **omitido** (nunca sai `null`). É esse campo que "
    "as ferramentas receptoras conferem na importação: o termo só entra em um "
    "dossiê Veritas de domínio compatível, e o retorno só é aceito pelo Nexo do "
    "mesmo domínio (Nexo Coger para `pad`, Nexo PAR para `par`). O tratamento "
    "completo dessa validação está na Seção 6.",
)

page_break(doc)

# ---------------------------------------------------------------------------
# Seção 6 — Integração
# ---------------------------------------------------------------------------
add_chapter(doc, "Seção 6", "Integração entre as quatro ferramentas")

add_body(
    doc,
    "As quatro ferramentas da suíte funcionam de forma inteiramente independente "
    "(Seções 2 a 5 comprovam isso), mas preveem um fluxo de integração opcional, "
    "por troca de arquivos `.json`. Com a extensão da suíte ao domínio PAR, esse "
    "fluxo **bifurca por domínio**: cada contrato de integração passou a carregar "
    "um campo **`dominio`** (`pad` ou `par`) no envelope, e cada ferramenta "
    "receptora **valida** esse campo na importação, recusando o cruzamento "
    "indevido entre os ritos. Nesta seção, sempre que aparecer isolado, o termo "
    "\"Nexo\" refere-se genericamente ao par de ferramentas de mapa — **Nexo "
    "Coger** (domínio PAD) e **Nexo PAR** (domínio PAR) —, e não ao nexo "
    "fático-probatório (a ligação fato-prova) nem ao nexo de causalidade da LAC.",
)

add_body(doc, "O ciclo típico de integração percorre, no **domínio PAD**:")
add_body(
    doc,
    "**Veritas → Nexo Coger → Oitiva 360 → Veritas → Nexo Coger** — provas "
    "cadastradas no Veritas alimentam o mapa do Nexo Coger; o Nexo Coger exporta "
    "uma pauta de pontos a apurar para o Oitiva 360; o Oitiva 360 conduz a oitiva "
    "e devolve o termo gerado (importável como prova no Veritas) e um retorno de "
    "contexto (importável de volta no Nexo Coger).",
    size=10,
)
add_body(doc, "E o **mesmo ciclo espelhado no domínio PAR**:")
add_body(
    doc,
    "**Veritas → Nexo PAR → Oitiva 360 → Veritas → Nexo PAR** — idêntico em "
    "estrutura, com o Veritas em dossiê de tipo PAR, o Oitiva 360 em modo PAR e o "
    "Nexo PAR no lugar do Nexo Coger. O Veritas e o Oitiva 360 são os mesmos "
    "arquivos nos dois ciclos (modo dual); só o Nexo troca de arquivo (modo "
    "fork). O campo `dominio` é o que mantém cada arquivo no ciclo do seu próprio "
    "domínio — um envelope PAR não entra em uma ferramenta PAD e vice-versa.",
    size=10,
)

add_h2(doc, "6.1 Veritas → Nexo Coger / Nexo PAR: exportação de provas")

add_body(
    doc,
    "No Veritas, o botão **\"Exportar provas → Nexo Coger\"** gera um arquivo "
    "`nexo-coger-provas-<número do processo>.json` contendo apenas as provas "
    "cujo tipo se mapeia para o catálogo canônico de tipos de prova do Nexo. É um "
    "contrato distinto e mais restrito do que a exportação isolada \"Exportar "
    ".json\" (Seção 2.3), que exporta o dossiê inteiro.",
)

add_body(
    doc,
    "O envelope emite o campo **`dominio`** derivado do Tipo de processo do dossiê "
    "(`pad`, `par`, ou omitido quando o dossiê é agnóstico). Na importação, o "
    "**Nexo Coger** (domínio fixo `pad`) aceita envelopes `pad` **ou sem campo** "
    "(arquivo legado, anterior às rodadas PAR) e **recusa** `par`; o **Nexo PAR** "
    "(domínio fixo `par`) aceita **apenas** `par`, recusando tanto `pad` quanto o "
    "envelope legado sem campo — no PAR não há acervo legado a preservar, pois o "
    "fork nasceu depois do campo. As mensagens de recusa seguem o padrão da Seção "
    "6.6.",
)

add_h2(doc, "6.2 Nexo Coger / Nexo PAR → Oitiva 360: exportação de pauta")

add_body(
    doc,
    "A partir da tela \"Revisão de pauta\" do Nexo (Coger ou PAR), é possível "
    "exportar uma pauta de instrução por depoente, contendo os pontos de "
    "instrução confirmados e o papel do depoente. O Nexo bloqueia essa exportação "
    "quando o nome do depoente não foi informado (\"Informe o nome do "
    "depoente.\") ou quando não há nenhum ponto de instrução confirmado "
    "(\"Nenhum ponto de instrução confirmado — nada a exportar.\"). O Oitiva 360, "
    "ao importar essa pauta, exibe um cartão \"Pauta do Nexo\" com os itens "
    "abordados na sessão e evita duplicação: reimportar a mesma pauta atualiza os "
    "itens existentes em vez de criar itens duplicados.",
)

add_body(
    doc,
    "O envelope da pauta emite **`dominio`** (`pad` no Nexo Coger, `par` no Nexo "
    "PAR). O Oitiva 360, receptor de **modo dual**, aplica a cascata da Seção 5.1: "
    "a pauta com domínio **deriva e trava** o domínio do processo; se o Oitiva 360 "
    "já tinha um domínio definido manualmente e ele **conflita** com o da pauta, a "
    "importação **pede confirmação antes de qualquer alteração** — cancelar recusa "
    "a importação inteira, de forma atômica (nada é gravado); confirmar troca o "
    "domínio e trava o campo na origem da pauta.",
)

add_h2(doc, "6.3 Oitiva 360 → Veritas: exportação do termo")

add_body(
    doc,
    "O botão **\"Exportar termo para o Veritas\"**, sempre visível na Etapa 4 do "
    "Oitiva 360, gera um arquivo de termo que carrega um `hash_origem` — um hash "
    "calculado sobre o texto do termo no momento da exportação, usado pelo "
    "Veritas para verificar a integridade do conteúdo na importação — e o campo "
    "**`dominio`** do processo (omitido quando indefinido).",
)

add_body(
    doc,
    "Ao importar esse termo, o Veritas aplica as verificações abaixo, **nesta "
    "ordem** — a validação de domínio roda **antes** da conferência de hash, para "
    "recusar cedo, antes do trabalho caro:",
)
add_alert(
    doc,
    ["Arquivo inválido: este arquivo não é um termo exportado pelo Oitiva 360 (esperado \"origem\":\"oitiva-360\", \"termo.conteudo\" e \"hash_origem\")."],
    kind="danger",
    label="1. Formato inválido — bloqueia",
)
add_alert(
    doc,
    [
        "**Domínio incompatível** — quando o dossiê tem Tipo de processo definido e "
        "o domínio do termo diverge do domínio do dossiê (ex.: termo PAR em dossiê "
        "PAD). Mensagem no padrão-base da Seção 6.6: \"Importação recusada — "
        "domínio incompatível.\" seguida de \"Domínio encontrado / Domínio esperado "
        "/ ferramenta correta / Nenhum dado foi alterado.\". Um dossiê **sem Tipo "
        "de processo** (Veritas agnóstico) aceita termo de qualquer domínio.",
    ],
    kind="danger",
    label="2. Domínio incompatível (ou termo legado em dossiê PAR) — bloqueia",
)
add_alert(
    doc,
    ["Importação bloqueada: o hash do termo não confere.", "Esperado (hash_origem): <hash>", "Calculado sobre o texto recebido: <hash>", "O conteúdo do termo pode ter sido alterado após a exportação do Oitiva 360. Nada foi importado."],
    kind="danger",
    label="3. Hash divergente — bloqueia",
)
add_alert(
    doc,
    ["Importação recusada: já existe uma prova neste dossiê com o mesmo hash_origem (<hash>). Este termo já foi importado antes — reimportação não cria uma segunda prova."],
    kind="danger",
    label="4. Duplicado — bloqueia",
)
add_alert(
    doc,
    ["Este termo foi exportado com catalogo_schema_version <X>, diferente da versão do catálogo em uso neste Veritas (<Y>). O hash já foi conferido e confere — o aviso é só sobre o vocabulário do catálogo. Deseja continuar?"],
    kind="warn",
    label="5. Versão de catálogo divergente — pede confirmação, não bloqueia",
)

add_body(
    doc,
    "Um termo importado com sucesso ganha automaticamente a categoria "
    "**\"Termo de oitiva\"** no Veritas e aparece na tela de detalhe do item com "
    "um selo \"Revisado\" ou \"Pendente de revisão\", e um botão \"Marcar como "
    "revisado\". O ícone ⏳ no topo da tela do Veritas mostra a contagem de "
    "termos pendentes de revisão.",
)

add_h2(doc, "6.4 Oitiva 360 → Nexo Coger / Nexo PAR: retorno de contexto")

add_body(
    doc,
    "Quando a sessão de oitiva aborda itens da pauta importada do Nexo, o Oitiva "
    "360 disponibiliza o botão **\"Exportar retorno (contexto do acusado)\"**, que "
    "devolve ao Nexo um resumo da resposta obtida para cada ponto de instrução "
    "abordado. Esse botão só aparece quando há itens de pauta efetivamente "
    "abordados na sessão — não existe no fluxo manual sem pauta importada. O "
    "envelope do retorno também emite o campo **`dominio`**, validado na "
    "importação: o Nexo Coger aceita `pad`/legado e recusa `par`; o Nexo PAR "
    "aceita apenas `par` (Seção 6.5).",
)

add_alert(
    doc,
    [
        "No **Nexo PAR**, o vínculo padrão do retorno de oitiva aponta para o "
        "**ente privado** cadastrado no processo (o mesmo objeto que, no Nexo "
        "Coger, seria o acusado). O retorno de contexto PAR alimenta, portanto, o "
        "cadastro do ente, não uma estrutura de acusado servidor.",
    ],
    kind="info",
    label="Retorno PAR vincula-se ao ente privado",
)

add_body(
    doc,
    "Quando esse retorno é importado no Nexo, o **fato** que ele alimenta recebe "
    "um selo dourado **🎙**, sinalizando que aquele contexto nasceu de uma sessão "
    "de oitiva e não de cadastro manual direto. Esse selo do cartão de fato é "
    "anterior às rodadas PAR e já funciona plenamente.",
)

add_body(
    doc,
    "Há ainda um **segundo selo, análogo, no cartão de prova** (não no cartão de "
    "fato): quando uma prova é criada a partir do botão \"Exportar prova(s) para o "
    "Nexo\" do Oitiva 360, ela recebe o mesmo selo dourado 🎙, com tooltip "
    "mostrando os campos `pauta_id`, `rodada_id` e `id_ponto`. Este selo de prova "
    "é detalhado na Seção 3.8 deste manual.",
)

add_alert(
    doc,
    [
        "O tooltip do selo de prova (a mesma situação da Seção 3.8) mostra "
        "os três identificadores **preenchidos** (`pauta_id`, `rodada_id`, "
        "`id_ponto`) sempre que a prova exportada por \"Exportar prova(s) "
        "para o Nexo\" tem origem em um ponto de pauta respondido. Quando a "
        "prova foi adicionada manualmente na sessão, sem vínculo de pauta, "
        "os três campos ficam `null` — comportamento correto e "
        "documentado, não uma limitação. O selo pré-existente no cartão de "
        "**fato**, mencionado acima, segue funcionando como sempre.",
    ],
    kind="info",
    label="IDs do tooltip: preenchidos com origem de pauta, null sem ela",
)

add_h2(doc, "6.5 Política de validação cruzada de domínio")

add_body(
    doc,
    "Todos os quatro contratos acima seguem uma **única política de validação**, "
    "aplicada uniformemente na importação — não há regras ad hoc por ferramenta. "
    "Ao importar qualquer envelope, a ferramenta receptora compara o `dominio` do "
    "envelope com o seu próprio domínio corrente e aplica:",
)

make_table(
    doc,
    headers=["Situação", "Comportamento"],
    rows=[
        ("Domínio do envelope igual ao domínio do receptor",
         "Importa normalmente."),
        ("Domínio do envelope diferente do domínio do receptor",
         "Recusa com mensagem clara (qual domínio o arquivo carrega, qual a ferramenta/processo espera, e qual a ferramenta correta para aquele arquivo). Nunca falha silenciosa, nunca importação parcial."),
        ("Envelope sem o campo dominio (arquivo anterior às rodadas PAR)",
         "Tratado como legado PAD: aceito pelos receptores de domínio PAD (Nexo Coger, dossiê Veritas PAD); nos receptores PAR (Nexo PAR, dossiê Veritas PAR), recusado com mensagem específica de arquivo legado."),
        ("Receptor de modo dual (Oitiva 360) sem domínio definido recebendo envelope com domínio",
         "Deriva o domínio do envelope, pela cascata da Seção 5.1 — com a confirmação de conflito lá especificada."),
    ],
    col_widths=[6.2, 9.3],
)

add_body(
    doc,
    "Essa tabela está registrada como comentário-referência no código de cada uma "
    "das quatro rotinas de importação, justamente para que os pontos de validação "
    "não divirjam em manutenções futuras.",
)

figura_pendente(doc, "exemplo de recusa por domínio — importação de um arquivo PAR em uma ferramenta PAD, com a mensagem padronizada de domínio encontrado/esperado e a indicação da ferramenta correta.")

add_h2(doc, "6.6 Mensagens de recusa padronizadas e importação atômica")

add_body(
    doc,
    "As quatro ferramentas usam a **mesma estrutura de frase** ao recusar um "
    "envelope por domínio, terminando sempre com o quarteto **domínio encontrado "
    "/ domínio esperado / ferramenta correta a usar / garantia de que nenhum dado "
    "foi alterado**. Os rótulos de domínio aparecem por extenso — \"PAD (Lei "
    "8.112/1990)\", \"PAR (Lei 12.846/2013)\" ou \"não indicado (arquivo legado, "
    "anterior às rodadas PAR)\". Dois exemplos reais:",
)

add_alert(
    doc,
    [
        "Este arquivo foi exportado de um processo PAR (Lei nº 12.846/2013 — LAC). "
        "Este é o Nexo Coger, que trabalha com processos PAD (Lei nº 8.112/1990) — "
        "importe-o no Nexo PAR. Domínio encontrado: PAR (Lei 12.846/2013). Domínio "
        "esperado: PAD (Lei 8.112/1990). Nenhum dado foi alterado.",
    ],
    kind="mono",
    label="Nexo Coger recusando um envelope PAR",
)
add_alert(
    doc,
    [
        "Este arquivo não indica domínio (formato anterior às Rodadas PAR) e não "
        "pode ser importado no Nexo PAR, que trabalha exclusivamente com processos "
        "PAR (Lei nº 12.846/2013 — LAC). No PAR não existe acervo legado a "
        "preservar. Domínio encontrado: não indicado (arquivo legado, anterior às "
        "rodadas PAR). Domínio esperado: PAR (Lei 12.846/2013). Nenhum dado foi "
        "alterado.",
    ],
    kind="mono",
    label="Nexo PAR recusando um envelope legado (sem domínio)",
)

add_alert(
    doc,
    [
        "**Importação atômica.** Nenhuma recusa por domínio deixa estado parcial: a "
        "validação roda **antes** de qualquer mutação — antes de montar o modal de "
        "revisão, antes de gravar qualquer item, antes da conferência de hash. Ou "
        "entra tudo, ou nada. A contagem de provas, itens e o domínio do receptor "
        "permanecem exatamente como estavam antes da tentativa recusada.",
    ],
    kind="green",
    label="Recusa nunca deixa estado parcial",
)

add_h2(doc, "6.7 Badges de pendência, status e domínio")

add_body(
    doc,
    "Cada ferramenta usa seu próprio conjunto de selos (badges) para sinalizar o "
    "estado de itens importados ou pendentes de revisão. Além desses, o Oitiva "
    "360 exibe no cabeçalho o **chip de domínio** (PAD/PAR), que não é um badge de "
    "item mas um indicador do domínio corrente do processo — reflete o mesmo "
    "mecanismo de cascata descrito na Seção 5.1:",
)
make_table(
    doc,
    headers=["Ferramenta", "Badges / indicadores"],
    rows=[
        ("Veritas", "termo: pendente_revisao / revisado"),
        ("Nexo Coger / Nexo PAR", "prova: pendente / vinculada — retorno: pendente_revisao / revisado"),
        ("Oitiva 360", "pauta: pendente / em_andamento / concluida — chip de domínio: PAD / PAR (cabeçalho)"),
    ],
    col_widths=[4.5, 11.0],
)

add_alert(
    doc,
    [
        "A integração entre as quatro ferramentas é **opcional e aditiva**. Cada "
        "ferramenta já funciona de forma completa sozinha, como demonstrado nas "
        "Seções 2 a 5 — a troca de arquivos `.json` apenas poupa redigitação de "
        "dados quando as ferramentas são usadas em conjunto no mesmo processo, e a "
        "validação de domínio garante que cada arquivo só seja aceito na ferramenta "
        "do rito correto.",
    ],
    kind="green",
    label="Integração é opcional",
)

page_break(doc)

# ---------------------------------------------------------------------------
# Glossário
# ---------------------------------------------------------------------------
add_h2(doc, "Glossário")

make_table(
    doc,
    headers=["Termo", "Definição"],
    rows=[
        ("Cadeia de custódia", "Registro contínuo de quem coletou, recebeu, transferiu ou custodiou uma prova, do momento em que ela surge até seu uso na decisão."),
        ("Proveniência", "Origem declarada de um elemento de prova — como e de onde ele chegou ao processo (gerado internamente, recebido de outro órgão, ou extraído de sistema)."),
        ("Hash", "Uma \"impressão digital\" numérica calculada a partir do conteúdo de um arquivo; se o arquivo muda, o hash muda — usado para verificar se um arquivo permanece idêntico ao original."),
        ("Nexo fático-probatório", "A ligação demonstrável entre um fato apurado e as provas que o sustentam (a mecânica do mapa fato-prova-norma). É um dos três sentidos de \"nexo\" na suíte — distinto do nexo de causalidade (conceito da LAC) e dos nomes próprios Nexo Coger / Nexo PAR (ferramentas)."),
        ("Nexo de causalidade", "Conceito jurídico da Lei nº 12.846, de 1º de agosto de 2013 (LAC): a correlação entre o ato lesivo e o benefício ou interesse auferido pela pessoa jurídica. No Nexo PAR, é um campo do fato (Seção 4.3). Não confundir com o nexo fático-probatório nem com os nomes das ferramentas."),
        ("Nexo Coger / Nexo PAR", "Nomes próprios das duas ferramentas de mapa fato-prova-norma da suíte: o Nexo Coger atende o domínio PAD; o Nexo PAR atende o domínio PAR. São dois arquivos independentes (modo fork). Nomear uma ferramenta \"Nexo\" não a confunde com o nexo fático-probatório nem com o nexo de causalidade."),
        ("Enquadramento legal", "O dispositivo normativo (dever, proibição, hipótese de demissão, ato lesivo da LAC etc.) em que uma conduta apurada se amolda."),
        ("Elemento subjetivo", "O grau de intenção ou de falta de cuidado do agente em relação à conduta — dolo direto, dolo eventual, negligência, imprudência ou imperícia. É instituto do domínio PAD; no PAR a responsabilização é objetiva (art. 2º da LAC) e não há elemento subjetivo."),
        ("Domínio (PAD/PAR)", "O rito normativo de um processo na suíte: PAD (e sindicância), à luz da Lei nº 8.112, de 11 de dezembro de 1990, ou PAR, à luz da Lei nº 12.846, de 1º de agosto de 2013 (LAC). O domínio condiciona campos, papéis, normas e documentos, e viaja nos contratos de integração no campo `dominio`."),
        ("Ente privado", "A pessoa jurídica sujeita à responsabilização no domínio PAR — o polo passivo do PAR, no lugar do servidor (acusado) do PAD."),
        ("Ato lesivo", "Conduta praticada em interesse ou benefício de ente privado que atenta contra a Administração Pública, tipificada no art. 5º da Lei nº 12.846, de 2013 (LAC) — inclui corrupção, fraude a licitações e contratos e obstrução da fiscalização."),
        ("Representante legal / Preposto / Sócio-administrador", "Os três papéis de pessoa física vinculada ao ente privado no domínio PAR (papéis PAR do catálogo). O representante legal é exigido para gerar a Nota de Indiciação (pendência P-ENTE)."),
        ("Programa de integridade", "Conjunto de mecanismos internos de integridade, auditoria e incentivo à denúncia de um ente privado (compliance). Sua existência e efetivo funcionamento são elemento de dosimetria da multa do PAR e podem ser apresentados com a defesa (Portaria CGU nº 909, de 7 de abril de 2025)."),
        ("Nota de Indiciação", "Documento formal que, no domínio PAR, imputa ao ente privado a conduta lesiva e abre o prazo de defesa (art. 17 da Instrução Normativa CGU nº 13, de 2019). É o equivalente PAR do termo de indiciação do PAD."),
        ("Modo dual", "Arquitetura de uma ferramenta que, em um único arquivo, acomoda os dois domínios com comportamento condicional (Veritas e Oitiva 360)."),
        ("Modo fork", "Arquitetura em que cada domínio tem seu próprio arquivo independente, compartilhando a mesma mecânica (Nexo Coger para PAD, Nexo PAR para PAR)."),
        ("Estado probatório", "Avaliação de quão bem sustentado um fato está pelas provas reunidas até o momento: suficiente, indícios, ou ausente."),
        ("Pendência crítica/frágil", "Sinalização automática de um problema no mapa fato-prova-norma; crítica bloqueia a geração da indiciação, frágil apenas alerta."),
        ("Indiciação", "Ato formal que atribui a um servidor a autoria de fato(s) apurado(s), com enquadramento legal, dando início à fase de defesa escrita."),
        ("Pauta de instrução", "Lista de pontos a apurar em uma oitiva, tipicamente originada do campo \"Elementos buscados\" do Nexo Coger."),
        ("Roteiro de oitiva", "Sequência de perguntas organizadas por blocos, gerada a partir do papel do depoente e da infração apurada."),
        ("Termo de oitiva/interrogatório", "Documento formal que registra o ato de oitiva ou interrogatório, com qualificação, compromisso/advertências e as perguntas e respostas."),
        ("Papel de pessoa", "Classificação da posição de uma pessoa no processo — Investigado/Acusado, Vítima, Testemunha, Declarante/Informante ou Pessoa em Situação Indefinida — que determina compromisso, direito ao silêncio e tratamento processual."),
        ("Matriz de Apuração", "Bloco de 4 campos (conduta, investigado, elementos disponíveis, hipótese investigativa) exigido antes de conduzir qualquer oitiva no Oitiva 360."),
        ("Badge de pendência", "Selo visual que sinaliza o estado de um item importado ou pendente de ação (ex.: pendente de revisão, vinculada, concluída)."),
    ],
    col_widths=[4.3, 11.2],
)

page_break(doc)

# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------
add_h2(doc, "Perguntas frequentes")

add_h3(doc, "Veritas")
add_numbered(doc, 1, "**O que fazer se o hash não confere ao importar uma prova (termo de oitiva)?** O Veritas bloqueia totalmente a importação e não grava nada — a mensagem exibida mostra o hash esperado e o hash calculado sobre o conteúdo recebido. Isso indica que o conteúdo do termo pode ter sido alterado após a exportação do Oitiva 360; não há como contornar esse bloqueio pela interface — é necessário obter uma nova exportação íntegra do termo.")
add_numbered(doc, 2, "**Posso editar a proveniência depois de salvar um item?** Não. Todo o bloco de proveniência (tipo e subcampos) fica travado, somente leitura, assim que o item é salvo. O mesmo vale para o elemento físico (exceto a condição do lacre, alterável apenas via evento de \"Conferência do lacre\"), para \"conteúdo integral\"/justificativa, e para o status do item.")
add_numbered(doc, 3, "**Qual a diferença entre \"Exportar .json\" e \"Exportar provas → Nexo Coger\"?** \"Exportar .json\" gera o dossiê inteiro, para backup geral. \"Exportar provas → Nexo Coger\" gera um arquivo menor, apenas com as provas convertidas para o catálogo canônico do Nexo Coger — é o contrato de integração específico entre as duas ferramentas.")
add_numbered(doc, 4, "**O carimbo de data/hora do Veritas vale como prova de quando o arquivo foi coletado?** Não com força de selo de tempo certificado — é apenas o relógio do computador do usuário no momento em que o arquivo foi anexado. Tem valor para mostrar consistência interna, não para provar o instante exato de forma inatacável.")
add_numbered(doc, 5, "**O campo Tipo de processo é obrigatório? O que muda se eu não preencher?** Não é obrigatório. Sem Tipo de processo definido, o Veritas permanece **agnóstico de domínio**: aceita prova de qualquer origem, sem filtro, não marca `pad` nem `par` no dossiê, e as categorias de prova exclusivas do PAR (Programa de integridade, Informações do COAF) não aparecem. Ao importar um termo de oitiva, um dossiê sem tipo aceita termo de qualquer domínio. O campo só passa a influenciar o comportamento quando efetivamente preenchido — dossiês antigos seguem funcionando como antes.")

add_h3(doc, "Nexo Coger")
add_numbered(doc, 1, "**Por que o papel \"Pessoa em Situação Indefinida\" não aparece separado, com instruções de uso, na tela?** O Nexo Coger não exibe nenhum texto de orientação sobre quando usar esse papel — apenas o rótulo curto aparece no seletor. A explicação jurídica completa só existe no catálogo de dados, e este manual a reproduz na Seção 3.3, junto de uma orientação prática de uso.")
add_numbered(doc, 2, "**O que acontece se eu gerar a indiciação e depois perceber um erro?** A geração da indiciação é tratada como um ato final da instrução; o Nexo Coger não oferece uma função de \"desfazer\" a geração. Corrija os dados do fato/prova/enquadramento no mapa e gere uma nova minuta quando necessário — por isso este manual recomenda revisar cuidadosamente pendências frágeis e o checklist de campos essenciais antes de gerar.")
add_numbered(doc, 3, "**Um fato arquivado precisa de enquadramento legal e provas completas?** Não. Um fato marcado como \"Arquivado\" só exige a Justificativa do arquivamento; não gera pendências e não entra na minuta de indiciação.")
add_numbered(doc, 4, "**O que fazer quando o elemento subjetivo escolhido conflita com o exigido pela norma?** O Nexo Coger apenas avisa (não bloqueia o salvamento) quando o elemento subjetivo escolhido diverge do que a norma exige — por exemplo, marcar conduta culposa em norma que exige dolo. Revise o enquadramento ou ajuste a fundamentação antes de prosseguir para a indiciação.")

add_h3(doc, "Nexo PAR")
add_numbered(doc, 1, "**Por que o Nexo PAR não tem campo de elemento subjetivo (dolo/culpa)?** Porque a responsabilização do ente privado na Lei nº 12.846, de 1º de agosto de 2013 (LAC), é **objetiva** (art. 2º): independe de dolo ou culpa. Por isso o Nexo PAR remove tanto o campo Elemento subjetivo quanto a pendência a ele associada (a P8 do Nexo Coger). Em seu lugar, o fato exige a descrição do **benefício/interesse do ente e do nexo de causalidade** — cobrados pela pendência crítica P8-PAR (Seção 4.3 e 4.5).")
add_numbered(doc, 2, "**O que acontece se eu tentar importar uma prova PAD no Nexo PAR?** A importação é **recusada**, de forma atômica (nenhum dado é gravado). O Nexo PAR aceita apenas envelopes de domínio `par`; um envelope `pad` — ou um envelope legado, sem domínio — é recusado com a mensagem padronizada de domínio (domínio encontrado / esperado / ferramenta correta), que sugere importar o arquivo no Nexo Coger. O detalhe dessa validação cruzada está na Seção 6 (Seções 6.5 e 6.6).")
add_numbered(doc, 3, "**Preciso cadastrar um representante legal para gerar a Nota de Indiciação?** Sim. A falta de ente privado cadastrado, ou de ao menos um representante legal, dispara a pendência crítica P-ENTE, que **bloqueia a geração** da Nota de Indiciação (embora não impeça salvar o cadastro do ente). Ver Seção 4.2 e 4.5.")

add_h3(doc, "Oitiva 360")
add_numbered(doc, 1, "**Preciso preencher a Matriz de Apuração toda vez?** Sim, ela é obrigatória em nível de processo — os 4 campos (conduta, investigado, elementos disponíveis, hipótese investigativa) precisam estar preenchidos antes que o botão \"Adicionar depoente\" seja habilitado. Uma vez preenchida, vale para todos os depoentes daquele processo.")
add_numbered(doc, 2, "**Existe campo de observação separado da resposta, na Etapa 4?** Não. Cada pergunta do roteiro tem apenas uma única área de texto para a resposta do depoente — não há campo auxiliar de observação nem de marcação de relevância.")
add_numbered(doc, 3, "**O termo é gerado automaticamente ou preciso clicar em algo?** É gerado automaticamente ao entrar na Etapa 4, sem bloqueio por campos vazios — campos ainda não preenchidos aparecem como \"____\" no texto. É possível editar o texto manualmente ou regenerá-lo a partir dos dados atuais do ato (com confirmação, pois substitui edições manuais).")
add_numbered(doc, 4, "**Por que não vejo o botão \"Exportar retorno (contexto do acusado)\"?** Esse botão só aparece quando a sessão aborda itens de uma pauta importada do Nexo (Coger ou PAR). No fluxo manual, sem pauta importada, ele não é exibido — apenas o botão \"Exportar termo para o Veritas\" fica sempre visível na Etapa 4.")
add_numbered(doc, 5, "**Como o domínio (PAD/PAR) é definido quando não há pauta importada?** Pela seleção **manual** no 5º campo da Matriz de Apuração (\"Domínio do processo\"), editável enquanto não houver pauta vinculada. Um processo novo nasce em PAD. Assim que uma pauta do Nexo é importada, o domínio passa a ser **derivado e travado** pela pauta (Seção 5.1).")
add_numbered(doc, 6, "**O que acontece se eu trocar de domínio com dados já preenchidos?** O Oitiva 360 mostra, **antes de aplicar**, exatamente o que será afetado: as categorias de infração de outro domínio **serão LIMPAS** (voltam a \"não definida\") e os papéis que não existem no novo domínio **serão MANTIDOS**, apenas sinalizados \"fora do domínio\" para reclassificação. Nada é apagado silenciosamente, e recusar a confirmação reverte a troca (Seção 5.1).")

# ---------------------------------------------------------------------------
# Nota editorial final
# ---------------------------------------------------------------------------
add_separator(doc)
add_muted(
    doc,
    "Este manual documenta o comportamento observado no código-fonte das quatro "
    "ferramentas em 2026. Todos os exemplos, números de processo e dados de "
    "identificação usados nas capturas de tela são fictícios, produzidos para "
    "fins exclusivamente ilustrativos. As quatro ferramentas — Veritas, Nexo "
    "Coger, Nexo PAR e Oitiva 360 — são aplicações offline/locais, sem servidor, "
    "cujo armazenamento depende do navegador do usuário e de exportação manual de "
    "arquivos .json para backup e integração.",
)

out_path = os.path.join(BASE, "Manual_Suite_COGER.docx")
doc.save(out_path)
print("saved", out_path)
