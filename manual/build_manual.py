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


reset_figure_counter()
doc = new_document()

# ---------------------------------------------------------------------------
# Capa
# ---------------------------------------------------------------------------
add_cover(
    doc,
    LOGO,
    "Manual da Suíte COGER",
    "Veritas · Nexo Coger · Oitiva 360",
    [
        "Lei nº 8.112, de 11 de dezembro de 1990 — Processo Administrativo Disciplinar",
        "Suíte de 3 ferramentas offline/locais, integráveis mas independentes entre si",
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
    "A **Suíte COGER** reúne três ferramentas de apoio ao trabalho de comissões de "
    "Processo Administrativo Disciplinar (PAD), Processo Administrativo de "
    "Responsabilização (PAR) e sindicância, no âmbito da Corregedoria da Receita "
    "Federal do Brasil, à luz da **Lei nº 8.112, de 11 de dezembro de 1990**. As três "
    "ferramentas — **Veritas**, **Nexo Coger** e **Oitiva 360** — são páginas HTML "
    "autocontidas, executadas inteiramente no navegador do usuário, **sem servidor, "
    "sem nuvem e sem envio de dados a terceiros**. Todo o armazenamento é local "
    "(localStorage do navegador) e a persistência entre sessões depende de "
    "exportação/importação manual de arquivos `.json` pelo próprio usuário.",
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
        "**Veritas** — cadastro de provas com cadeia de custódia (proveniência, hash, linha do tempo).",
        "**Nexo Coger** — mapa fato-prova-norma, apoio à construção da indiciação.",
        "**Oitiva 360** — apoio à condução de oitivas e interrogatórios, com roteiro e termo.",
    ],
    kind="info",
    label="As três ferramentas da suíte",
)

add_body(
    doc,
    "Cada ferramenta é **funcionalmente completa por si só** — é inteiramente "
    "possível cadastrar provas no Veritas, montar o mapa fático no Nexo Coger e "
    "conduzir oitivas no Oitiva 360 sem que nenhuma delas jamais troque um arquivo "
    "com as outras. As Seções 2, 3 e 4 deste manual documentam cada ferramenta "
    "**em uso isolado**, exatamente como ela se comporta quando usada sozinha.",
)

add_body(
    doc,
    "Ainda assim, as três ferramentas **podem** trocar informações entre si por "
    "meio de exportação e importação de arquivos `.json` — por exemplo, provas "
    "cadastradas no Veritas podem alimentar o mapa do Nexo Coger, e um termo de "
    "oitiva gerado no Oitiva 360 pode ser importado como prova no Veritas. Essa "
    "integração é **opcional e aditiva**: nenhuma das ferramentas exige a outra "
    "para funcionar, e os detalhes de cada contrato de integração ficam reservados "
    "para a **Seção 5 — Integração entre as três ferramentas**.",
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
add_numbered(doc, 2, "**Categoria** — seleção em lista. **Obrigatória**: se não selecionada, a mensagem é \"Selecione a categoria.\". As opções são: Print de sistema, Documento financeiro, Comunicação (e-mail/mensagem), Foto/vídeo, Laudo/perícia, Ofício, Decisão judicial, Documento físico, Dispositivo/mídia física (HD, celular, pendrive etc.) e Outro. Existe ainda a categoria **\"Termo de oitiva\"**, mas ela é reservada — só é atribuída automaticamente quando um termo do Oitiva 360 é importado (ver Seção 5); não é um fluxo de criação manual normal.")
add_numbered(doc, 3, "**Nº/folha nos autos** — texto livre, opcional (marcado como \"opcional\" na própria tela).")
add_numbered(doc, 4, "**Vinculado à matriz de apuração** — texto livre, opcional, para anotar a que fato/hipótese este elemento de prova sustenta.")
add_numbered(doc, 5, "**Sigilo/classificação** — seleção em lista, opcional, com valor padrão \"Acesso restrito\". Opções: Público nos autos, Acesso restrito, Sigiloso.")
add_numbered(doc, 6, "**Extrato ou conteúdo integral?** — grupo de opções (\"Sim — conteúdo integral\" / \"Não — extrato/trecho parcial\"), com valor padrão \"Sim\".")

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
        "está documentada na Seção 5 deste manual.",
    ],
    kind="warn",
    label="Atenção — não confundir as duas exportações",
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
        "oitiva** (Seção 5.3): ali, um hash (`hash_origem`) divergente "
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
    "alimenta diretamente o Oitiva 360 (ver Seção 5).",
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
    "Oitiva 360 — ver Seção 5), no bloco \"Depoente\", com os campos **Nome** e "
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
        ("P6c", "(pendência frágil — não bloqueia geração de minuta, mas deve ser revisada antes de finalizar; descrição completa não confirmada no levantamento de código disponível)."),
        ("P7", "(pendência frágil — não bloqueia geração de minuta, mas deve ser revisada antes de finalizar; descrição completa não confirmada no levantamento de código disponível)."),
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

add_alert(
    doc,
    [
        "Este manual não detalha campo a campo o formulário de acusado além "
        "do que foi efetivamente confirmado no levantamento de código: o "
        "**nome** é obrigatório — se deixado em branco, o Nexo Coger bloqueia "
        "com a mensagem \"Informe o nome do acusado.\". Ao excluir um "
        "acusado, o Nexo Coger pede confirmação: \"Excluir este acusado? As "
        "condutas vinculadas a ele nos fatos serão removidas.\". Os demais "
        "campos do formulário (cargo, matrícula, lotação etc., citados de "
        "passagem em outras partes deste manual, como na tabela de "
        "qualificação da indiciação) não foram auditados campo a campo — "
        "evite tomar esta seção como um roteiro completo do formulário.",
    ],
    kind="info",
    label="Cobertura parcial — seja cauteloso",
)

add_h2(doc, "3.7 Cadastro de prova no Nexo Coger")

add_body(
    doc,
    "O detalhamento do formulário de prova para os tipos **Testemunhal** e "
    "**Declaração de informante** — Deponente, Papel do depoente, "
    "Compromissada?, trio de contradita — já foi apresentado na Seção 3.4 "
    "(Papel de pessoa). Esta seção cobre os campos **gerais** do formulário "
    "de prova, presentes independentemente do tipo escolhido.",
)

add_body(
    doc,
    "Confirmados no levantamento: o campo **Título** é obrigatório — se "
    "vazio, o Nexo Coger bloqueia com \"Informe o título da prova.\"; o "
    "**Tipo de prova** é o campo que decide quais campos de detalhe "
    "adicionais aparecem (entre eles, Testemunhal e Declaração de "
    "informante, que revelam o bloco de depoente da Seção 3.4); e a prova "
    "carrega uma lista de **fatos aos quais está vinculada** (`fatoIds`), "
    "que é o mesmo vínculo tratado do lado do fato na Seção 3.3 — marcar a "
    "checkbox no formulário do fato e vincular pelo lado da prova refletem "
    "o mesmo relacionamento.",
)

add_alert(
    doc,
    [
        "Os demais campos gerais do formulário de prova (por exemplo, "
        "referência aos autos, categoria/tipo específico fora de "
        "testemunhal/declaração) não foram auditados campo a campo neste "
        "levantamento — este manual documenta com detalhe apenas o que foi "
        "efetivamente confirmado no código-fonte.",
    ],
    kind="info",
    label="Cobertura parcial",
)

add_h2(doc, "3.8 Selo de origem — retorno de oitiva")

add_body(
    doc,
    "Quando uma prova é criada no Nexo Coger a partir da exportação "
    "**\"Exportar prova(s) para o Nexo\"** do Oitiva 360 (Seção 5.1), o "
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
        "**Limitação técnica conhecida**: hoje, os três campos do tooltip "
        "(`pauta_id`, `rodada_id`, `id_ponto`) aparecem vazios. O selo "
        "aparece corretamente sempre que a prova tem a marca de origem de "
        "oitiva preenchida, mas o Oitiva 360 ainda não emite esses três "
        "identificadores nesse contrato de exportação específico "
        "(\"Exportar prova(s) para o Nexo\") — a infraestrutura do selo já "
        "está pronta para exibi-los assim que o Oitiva 360 passar a "
        "enviá-los, mas por ora a rastreabilidade até a pauta/rodada/ponto "
        "exatos não está disponível por esse caminho.",
    ],
    kind="info",
    label="IDs do tooltip ainda vazios",
)

add_body(
    doc,
    "Não confunda este selo de **prova** com o selo pré-existente, também "
    "dourado (🎙), que aparece no **cartão de fato** quando o fato recebe "
    "contexto de um retorno de oitiva importado pelo fluxo \"Exportar "
    "retorno (contexto do acusado)\" (Seção 5.4) — esse outro selo, no "
    "cartão de fato, é anterior a esta rodada de implementação e já "
    "funciona plenamente.",
)

add_h2(doc, "3.9 Toolbar lateral")

add_body(
    doc,
    "O Nexo Coger mantém uma barra lateral com painéis de apoio à condução "
    "da apuração. O mais detalhado e mais bem documentado neste manual é o "
    "**painel de Pendências**, que lista, em tempo real, todos os códigos "
    "de pendência crítica (P1, P2, P5, P8) e frágil (P3, P6a, P6b, P6c, P7) "
    "presentes no processo — o mesmo catálogo apresentado na Seção 3.5.",
)

add_alert(
    doc,
    [
        "Os demais painéis citados na interface — **Ordem dos fatos**, "
        "**Checklist de encerramento** e **Prazos** — existem (por exemplo, "
        "a variável de estado `prazosSecOpen` é acionada automaticamente "
        "logo após a primeira geração bem-sucedida de minuta, abrindo o "
        "painel de Prazos), mas este manual não confirma, campo a campo, "
        "as interações internas de cada um desses três painéis — o "
        "levantamento de código disponível não teve profundidade suficiente "
        "para documentá-los com o mesmo detalhamento do painel de "
        "Pendências. Evite tomar esta seção como um roteiro completo da "
        "toolbar lateral.",
    ],
    kind="info",
    label="Cobertura parcial dos demais painéis",
)

page_break(doc)

# ---------------------------------------------------------------------------
# Seção 4 — Oitiva 360
# ---------------------------------------------------------------------------
add_chapter(doc, "Seção 4", "Oitiva 360 (uso isolado)")

add_body(
    doc,
    "O **Oitiva 360** apoia a condução de oitivas e interrogatórios: gera um "
    "roteiro de perguntas a partir do papel do depoente e da infração apurada, "
    "registra as respostas dadas durante a sessão e produz o termo de redução "
    "correspondente.",
)

add_h2(doc, "4.1 Pré-requisito — Matriz de Apuração")

figura_ajustada(
    doc,
    os.path.join(SHOTS, "oitiva-matriz-apuracao.png"),
    "Cartão \"Matriz de Apuração\" — pré-requisito obrigatório antes de adicionar depoentes.",
)

add_body(
    doc,
    "Antes de adicionar qualquer depoente, o Oitiva 360 exige o preenchimento "
    "completo do cartão **\"Matriz de Apuração (nível processo — obrigatória)\"**, "
    "com 4 campos, todos obrigatórios:",
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

add_h2(doc, "4.2 Diálogo \"Adicionar depoente\"")

add_body(doc, "O diálogo pede apenas 2 campos, ambos obrigatórios:")
add_numbered(doc, 1, "**Identificação** — texto livre (placeholder: *Ex.: T-01 ou \"Depoente A\"*), com aviso: \"Use iniciais ou nome fictício — evite dados pessoais reais (LGPD).\".")
add_numbered(doc, 2, "**Elementos buscados com este depoente** — área de texto, com o apoio \"Por que ouvir ESTA pessoa? O que ela pode trazer?\".")

add_body(
    doc,
    "Se qualquer um dos dois estiver vazio, o Oitiva 360 bloqueia com "
    "\"Identificação e 'elementos buscados' são obrigatórios para adicionar o "
    "depoente.\".",
)

add_h2(doc, "4.3 Etapa 1 — Dados do Ato")

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

add_h2(doc, "4.4 Etapa 2 — Depoente")

add_body(
    doc,
    "Reforça o aviso de LGPD (\"Recomendamos usar iniciais ou nome fictício. "
    "Esta ferramenta não deve armazenar dados pessoais reais dos envolvidos\") e "
    "pede novamente **Identificação** e **Elementos buscados com este "
    "depoente**.",
)

add_body(doc, "O **Papel do depoente** repete o mesmo catálogo de 5 papéis já apresentado na Seção 3.3:")
make_table(
    doc,
    headers=["Papel", "Descrição resumida"],
    rows=[
        ("Testemunha", "Presta compromisso legal (art. 342, CP); dever de depor."),
        ("Declarante/Informante", "Não presta compromisso; colaboração voluntária."),
        ("Pessoa em Situação Indefinida", "Envolvimento possível, sem elementos para tratar como investigada; silêncio facultado por cautela."),
        ("Vítima", "Não presta compromisso; sujeita-se à denunciação caluniosa."),
        ("Investigado/Acusado", "Não presta compromisso; direito ao silêncio (Lei 13.869/2019); interrogatório como último ato (art. 159)."),
    ],
    col_widths=[4.5, 11.0],
)

add_body(
    doc,
    "Selecionar \"Testemunha\" com a infração \"art. 132, IV — enriquecimento "
    "ilícito\" revela um cartão adicional, \"Terceiro interposto\", com a "
    "checkbox \"Este depoente é possível terceiro interposto (familiar/pessoa em "
    "cujo nome está bem sob suspeita)\".",
)

add_body(
    doc,
    "O campo **Categoria de infração** é uma lista de seleção com um campo de "
    "busca ao lado (por rótulo ou dispositivo — ex.: \"sigilo\", \"art. 117, "
    "IX\"), populada com **52 normas** agrupadas por origem normativa, na "
    "mesma ordem de grupos vista no Nexo Coger: Lei 8.112/90 — Deveres (art. "
    "116); Proibições (art. 117); Demissão (art. 132); Outras (art. 130); LAI "
    "(Lei 12.527/2011); e Outras categorias.",
)

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

add_h2(doc, "4.5 Registro de perguntas e respostas")

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

add_h2(doc, "4.6 Geração do termo")

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

add_h2(doc, "4.7 Checklist pré-oitiva e alertas de nulidade")

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

add_h2(doc, "4.8 Gerenciar múltiplos depoentes")

add_body(
    doc,
    "Antes de entrar no wizard de qualquer depoente específico, a Tela do "
    "Processo mostra a **lista de depoentes já cadastrados** — colunas "
    "Identificação, Papel, Infração, Status e ações. O **Status** exibido "
    "é o do progresso do próprio depoente no wizard (\"Rascunho\", "
    "\"Roteiro pronto\" ou \"Oitiva realizada\") — não é o mesmo conceito "
    "do status de item de pauta tratado na Seção 4.11 abaixo. Se não houver "
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

add_h2(doc, "4.9 Kit de Incidentes")

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

add_h2(doc, "4.10 Cartão de Mesa")

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

add_h2(doc, "4.11 Status da pauta")

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

page_break(doc)

# ---------------------------------------------------------------------------
# Seção 5 — Integração
# ---------------------------------------------------------------------------
add_chapter(doc, "Seção 5", "Integração entre as três ferramentas")

add_body(
    doc,
    "Embora Veritas, Nexo Coger e Oitiva 360 funcionem de forma inteiramente "
    "independente (Seções 2 a 4 comprovam isso), a suíte prevê um fluxo de "
    "integração opcional, por troca de arquivos `.json`, que percorre "
    "tipicamente o ciclo: **Veritas → Nexo Coger → Oitiva 360 → Veritas → Nexo "
    "Coger**. Provas cadastradas no Veritas alimentam o mapa do Nexo Coger; o "
    "Nexo Coger exporta uma pauta de pontos a apurar para o Oitiva 360; o "
    "Oitiva 360 conduz a oitiva e devolve, de volta, o termo gerado (importável "
    "como prova no Veritas) e um retorno de contexto (importável de volta no "
    "Nexo Coger).",
)

add_h2(doc, "5.1 Veritas → Nexo Coger: exportação de provas")

add_body(
    doc,
    "No Veritas, o botão **\"Exportar provas → Nexo Coger\"** gera um arquivo "
    "`nexo-coger-provas-<número do processo>.json` contendo apenas as provas "
    "cujo tipo se mapeia para o catálogo canônico de tipos de prova do Nexo "
    "Coger. É um contrato distinto e mais restrito do que a exportação isolada "
    "\"Exportar .json\" (Seção 2.3), que exporta o dossiê inteiro.",
)

add_h2(doc, "5.2 Nexo Coger → Oitiva 360: exportação de pauta")

add_body(
    doc,
    "A partir da tela \"Revisão de pauta\" do Nexo Coger, é possível exportar "
    "uma pauta de instrução por depoente, contendo os pontos de instrução "
    "confirmados e o papel do depoente. O Nexo Coger bloqueia essa exportação "
    "quando o nome do depoente não foi informado (\"Informe o nome do "
    "depoente.\") ou quando não há nenhum ponto de instrução confirmado "
    "(\"Nenhum ponto de instrução confirmado — nada a exportar.\"). O Oitiva 360, "
    "ao importar essa pauta, exibe um cartão \"Pauta do Nexo\" com os itens "
    "abordados na sessão e evita duplicação: reimportar a mesma pauta atualiza "
    "os itens existentes em vez de criar itens duplicados.",
)

add_h2(doc, "5.3 Oitiva 360 → Veritas: exportação do termo")

add_body(
    doc,
    "O botão **\"Exportar termo para o Veritas\"**, sempre visível na Etapa 4 do "
    "Oitiva 360, gera um arquivo de termo que carrega um `hash_origem` — um hash "
    "calculado sobre o texto do termo no momento da exportação, usado pelo "
    "Veritas para verificar a integridade do conteúdo na importação.",
)

add_body(
    doc,
    "Ao importar esse termo, o Veritas aplica três verificações bloqueantes e "
    "uma não bloqueante, cujas mensagens exatas são:",
)
add_alert(
    doc,
    ["Arquivo inválido: este arquivo não é um termo exportado pelo Oitiva 360 (esperado \"origem\":\"oitiva-360\", \"termo.conteudo\" e \"hash_origem\")."],
    kind="danger",
    label="1. Formato inválido — bloqueia",
)
add_alert(
    doc,
    ["Importação bloqueada: o hash do termo não confere.", "Esperado (hash_origem): <hash>", "Calculado sobre o texto recebido: <hash>", "O conteúdo do termo pode ter sido alterado após a exportação do Oitiva 360. Nada foi importado."],
    kind="danger",
    label="2. Hash divergente — bloqueia",
)
add_alert(
    doc,
    ["Importação recusada: já existe uma prova neste dossiê com o mesmo hash_origem (<hash>). Este termo já foi importado antes — reimportação não cria uma segunda prova."],
    kind="danger",
    label="3. Duplicado — bloqueia",
)
add_alert(
    doc,
    ["Este termo foi exportado com catalogo_schema_version <X>, diferente da versão do catálogo em uso neste Veritas (<Y>). O hash já foi conferido e confere — o aviso é só sobre o vocabulário do catálogo. Deseja continuar?"],
    kind="warn",
    label="4. Versão de catálogo divergente — pede confirmação, não bloqueia",
)

add_body(
    doc,
    "Um termo importado com sucesso ganha automaticamente a categoria "
    "**\"Termo de oitiva\"** no Veritas e aparece na tela de detalhe do item com "
    "um selo \"Revisado\" ou \"Pendente de revisão\", e um botão \"Marcar como "
    "revisado\". O ícone ⏳ no topo da tela do Veritas mostra a contagem de "
    "termos pendentes de revisão.",
)

add_h2(doc, "5.4 Oitiva 360 → Nexo Coger: retorno de contexto do acusado")

add_body(
    doc,
    "Quando a sessão de oitiva aborda itens da pauta importada do Nexo Coger, o "
    "Oitiva 360 disponibiliza o botão **\"Exportar retorno (contexto do "
    "acusado)\"**, que devolve ao Nexo Coger um resumo da resposta obtida para "
    "cada ponto de instrução abordado. Esse botão só aparece quando há itens de "
    "pauta efetivamente abordados na sessão — não existe no fluxo manual sem "
    "pauta importada.",
)

add_body(
    doc,
    "Quando esse retorno é importado no Nexo Coger, o **fato** que ele "
    "alimenta recebe um selo dourado **🎙**, sinalizando que aquele contexto "
    "nasceu de uma sessão de oitiva e não de cadastro manual direto. Esse "
    "selo do cartão de fato é anterior a esta rodada de implementação e já "
    "funciona plenamente.",
)

add_body(
    doc,
    "Há ainda um **segundo selo, análogo, no cartão de prova** (não no "
    "cartão de fato): quando uma prova é criada a partir do botão "
    "\"Exportar prova(s) para o Nexo\" do Oitiva 360, ela recebe o mesmo "
    "selo dourado 🎙, com tooltip mostrando os campos `pauta_id`, "
    "`rodada_id` e `id_ponto`. Este selo de prova é detalhado na Seção 3.8 "
    "deste manual.",
)

add_alert(
    doc,
    [
        "**Limitação técnica conhecida** (a mesma da Seção 3.8): hoje, os "
        "três identificadores do tooltip do selo de prova (`pauta_id`, "
        "`rodada_id`, `id_ponto`) aparecem vazios, porque o Oitiva 360 ainda "
        "não emite esses três campos nesse contrato específico de "
        "exportação de prova. O selo em si já funciona — aparece "
        "corretamente sempre que a prova carrega a marca de origem de "
        "oitiva — mas a rastreabilidade completa até a pauta/rodada/ponto "
        "exatos ainda não está disponível por esse caminho. O selo "
        "pré-existente no cartão de **fato**, mencionado acima, não tem essa "
        "limitação e já funciona integralmente.",
    ],
    kind="info",
    label="Selo de prova — IDs do tooltip ainda vazios",
)

add_h2(doc, "5.5 Badges de pendência e status")

add_body(
    doc,
    "Cada ferramenta usa seu próprio conjunto de selos (badges) para sinalizar "
    "o estado de itens importados ou pendentes de revisão:",
)
make_table(
    doc,
    headers=["Ferramenta", "Badges"],
    rows=[
        ("Veritas", "termo: pendente_revisao / revisado"),
        ("Nexo Coger", "prova: pendente / vinculada — retorno: pendente_revisao / revisado"),
        ("Oitiva 360", "pauta: pendente / em_andamento / concluida"),
    ],
    col_widths=[4.0, 11.5],
)

add_alert(
    doc,
    [
        "A integração entre Veritas, Nexo Coger e Oitiva 360 é **opcional e "
        "aditiva**. Cada ferramenta já funciona de forma completa sozinha, como "
        "demonstrado nas Seções 2, 3 e 4 — a troca de arquivos `.json` apenas "
        "poupa redigitação de dados quando as três são usadas em conjunto no "
        "mesmo processo.",
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
        ("Nexo fático-probatório", "A ligação demonstrável entre um fato apurado e as provas que o sustentam."),
        ("Enquadramento legal", "O dispositivo normativo (dever, proibição, hipótese de demissão etc.) em que uma conduta apurada se amolda."),
        ("Elemento subjetivo", "O grau de intenção ou de falta de cuidado do agente em relação à conduta — dolo direto, dolo eventual, negligência, imprudência ou imperícia."),
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

add_h3(doc, "Nexo Coger")
add_numbered(doc, 1, "**Por que o papel \"Pessoa em Situação Indefinida\" não aparece separado, com instruções de uso, na tela?** O Nexo Coger não exibe nenhum texto de orientação sobre quando usar esse papel — apenas o rótulo curto aparece no seletor. A explicação jurídica completa só existe no catálogo de dados, e este manual a reproduz na Seção 3.3, junto de uma orientação prática de uso.")
add_numbered(doc, 2, "**O que acontece se eu gerar a indiciação e depois perceber um erro?** A geração da indiciação é tratada como um ato final da instrução; o Nexo Coger não oferece uma função de \"desfazer\" a geração. Corrija os dados do fato/prova/enquadramento no mapa e gere uma nova minuta quando necessário — por isso este manual recomenda revisar cuidadosamente pendências frágeis e o checklist de campos essenciais antes de gerar.")
add_numbered(doc, 3, "**Um fato arquivado precisa de enquadramento legal e provas completas?** Não. Um fato marcado como \"Arquivado\" só exige a Justificativa do arquivamento; não gera pendências e não entra na minuta de indiciação.")
add_numbered(doc, 4, "**O que fazer quando o elemento subjetivo escolhido conflita com o exigido pela norma?** O Nexo Coger apenas avisa (não bloqueia o salvamento) quando o elemento subjetivo escolhido diverge do que a norma exige — por exemplo, marcar conduta culposa em norma que exige dolo. Revise o enquadramento ou ajuste a fundamentação antes de prosseguir para a indiciação.")

add_h3(doc, "Oitiva 360")
add_numbered(doc, 1, "**Preciso preencher a Matriz de Apuração toda vez?** Sim, ela é obrigatória em nível de processo — os 4 campos (conduta, investigado, elementos disponíveis, hipótese investigativa) precisam estar preenchidos antes que o botão \"Adicionar depoente\" seja habilitado. Uma vez preenchida, vale para todos os depoentes daquele processo.")
add_numbered(doc, 2, "**Existe campo de observação separado da resposta, na Etapa 4?** Não. Cada pergunta do roteiro tem apenas uma única área de texto para a resposta do depoente — não há campo auxiliar de observação nem de marcação de relevância.")
add_numbered(doc, 3, "**O termo é gerado automaticamente ou preciso clicar em algo?** É gerado automaticamente ao entrar na Etapa 4, sem bloqueio por campos vazios — campos ainda não preenchidos aparecem como \"____\" no texto. É possível editar o texto manualmente ou regenerá-lo a partir dos dados atuais do ato (com confirmação, pois substitui edições manuais).")
add_numbered(doc, 4, "**Por que não vejo o botão \"Exportar retorno (contexto do acusado)\"?** Esse botão só aparece quando a sessão aborda itens de uma pauta importada do Nexo Coger. No fluxo manual, sem pauta importada, ele não é exibido — apenas o botão \"Exportar termo para o Veritas\" fica sempre visível na Etapa 4.")

# ---------------------------------------------------------------------------
# Nota editorial final
# ---------------------------------------------------------------------------
add_separator(doc)
add_muted(
    doc,
    "Este manual documenta o comportamento observado no código-fonte das três "
    "ferramentas em 2026. Todos os exemplos, números de processo e dados de "
    "identificação usados nas capturas de tela são fictícios, produzidos para "
    "fins exclusivamente ilustrativos. As três ferramentas — Veritas, Nexo "
    "Coger e Oitiva 360 — são aplicações offline/locais, sem servidor, cujo "
    "armazenamento depende do navegador do usuário e de exportação manual de "
    "arquivos .json para backup e integração.",
)

out_path = os.path.join(BASE, "Manual_Suite_COGER.docx")
doc.save(out_path)
print("saved", out_path)
