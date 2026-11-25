import json
import shutil
import sys
from pathlib import Path

import pymupdf as fitz
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.config import carregar  # noqa: E402
from app.services.ai_provider import MockProvider  # noqa: E402

SECI_LINHAS = [
    "Controladoria Geral da União", "Sistema Eletrônico de Conflito de Interesses", "Emitido em:", "27/09/2023",
    "Dados cadastrais", "CPF: 123.456.789-09   Nome Completo: MARIA APARECIDA DE SOUZA LIMA",
    "Matrícula: 1234567   Cargo emprego: AUDITORA-FISCAL DA RECEITA FEDERAL",
    "Telefone (com DDD): (71) 98888-7777   E-mail: MARIA.LIMA@EXEMPLO.GOV.BR",
    "Dados da solicitação", "Protocolo: 00096.000123/2023-45   Tipo de Solicitação: Pedido de Autorização",
    "1 - Sua dúvida tem relação com qual (quais) das situações que podem configurar conflito de interesses no exercício de",
    "cargo ou emprego no âmbito do Poder Executivo federal, descritas no art. 5º da Lei nº 12.813/2013:",
    "III - Exercer, direta ou indiretamente, atividade incompatível com as atribuições do cargo;",
    "2 - Descreva a atividade que você pretende exercer fora da administração pública ou a situação que suscita sua dúvida:",
    "Pretendo lecionar como professora universitária na Universidade Particular Exemplo, em curso de Direito Tributário,",
    "duas noites por semana, com remuneração de R$ 3.500,00 por mês.",
    "3 - Você estaria vinculado a outra pessoa, empresa, associação ou organização durante o exercício dessa atividade?",
    "Sim, vínculo de professora horista com a Universidade Particular Exemplo.",
    "4 - Essa pessoa física ou jurídica mantém algum vínculo com o órgão ou entidade em que você trabalha? Se sim, descreva-o.",
    "Não",
    "5 - Quais são as atribuições de seu cargo ou emprego público?",
    "Auditora Fiscal da Receita Federal na equipe de fiscalização.",
    "6 - Quais atividades você exerce efetivamente em sua atual lotação?",
    "Fiscalização de pessoas jurídicas.",
    "7 - Você lida ou tem acesso a informações sigilosas ou privilegiadas no exercício de seu cargo ou emprego público? Se sim, descreva-as.",
    "Sim, informações fiscais.",
    "8 - No desempenho de sua função pública você exerce poder decisório capaz de interferir nos interesses de pessoa com quem pretende se relacionar?",
    "Não",
    "9 - Descreva como a situação que suscita sua dúvida poderia gerar um conflito entre seus interesses privados e o exercício de sua função pública.",
    "Não vislumbro conflito.",
    "10 - A partir das informações prestadas, você gostaria de receber:",
    "Autorização",
]


def pdf_seci(linhas=SECI_LINHAS) -> bytes:
    doc = fitz.open()
    for i in range(0, len(linhas), 24):
        pg = doc.new_page()
        y = 50
        for ln in linhas[i:i + 24]:
            pg.insert_text((30, y), ln, fontsize=7.5, fontname="helv")
            y += 14
    b = doc.tobytes(); doc.close()
    return b


def pdf_em_branco() -> bytes:
    doc = fitz.open(); doc.new_page(); b = doc.tobytes(); doc.close(); return b


@pytest.fixture
def pdf_consulta():
    return pdf_seci()


@pytest.fixture
def settings(tmp_path):
    k = tmp_path / "knowledge"
    for sub in ("pareceres", "precedentes", "normativos", "modelos"):
        (k / sub).mkdir(parents=True)
    shutil.copytree(RAIZ / "knowledge" / "modelos", k / "modelos", dirs_exist_ok=True)
    shutil.copytree(RAIZ / "knowledge" / "normativos", k / "normativos", dirs_exist_ok=True)
    shutil.copyfile(RAIZ / "knowledge" / "regras_coger.md", k / "regras_coger.md")
    (k / "pareceres" / "PA_145_2025_Docencia.txt").write_text(
        "Parecer Coger/GNP nº 145/2025. Docência em instituição de ensino superior privada. Professor universitário, "
        "lecionar em curso de graduação noturno, compatibilidade de horários, remuneração por hora-aula. Não configura "
        "conflito de interesses desde que observadas as ressalvas. Magistério é permitido pelo art. 5º da Lei 12.813.", encoding="utf8")
    (k / "pareceres" / "PA_211_2026_Sindico.txt").write_text(
        "Parecer Coger/GNP nº 211/2026. Síndico de condomínio residencial onde reside. Administração de condomínio, "
        "assembleia, taxa condominial, sem finalidade lucrativa.", encoding="utf8")
    (k / "precedentes").joinpath("Docencia").mkdir()
    (k / "precedentes" / "Docencia" / "PA_087_2024_Docencia.txt").write_text(
        "Precedente. Professor em faculdade particular de Direito. Aulas de pós-graduação. Magistério, ressalvada a "
        "informação privilegiada e a compatibilidade de horários.", encoding="utf8")
    base = RAIZ
    return carregar(sobrescrever={"caminhos": {
        "knowledge": str(k), "vectorstore": str(tmp_path / "vs"), "uploads": str(tmp_path / "up"), "output": str(tmp_path / "out"),
        "metrics": str(tmp_path / "met"), "banco": str(tmp_path / "met" / "t.db"),
        "prompts": str(base / "prompts"), "templates": str(base / "templates"), "categorias": str(base / "config" / "categorias.json")}})


IAFalsa = MockProvider   # provedor simulado: respostas programadas por trecho do prompt
