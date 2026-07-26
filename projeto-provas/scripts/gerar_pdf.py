#!/usr/bin/env python3
"""
Converte um .md de questões (resumo + questões + gabarito) em PDF no padrão
visual Bahiana/PROSEF (ver ../CLAUDE.md e ../template/especificacao_visual.md).

Uso:
    python scripts/gerar_pdf.py questoes-md/absorcao_intestinal.md
    python scripts/gerar_pdf.py questoes-md/absorcao_intestinal.md --sem-gabarito

O script NUNCA reescreve ou resume o conteúdo do .md — apenas diagrama.
Se a estrutura de entrada não seguir o formato esperado (Passo 2 do
CLAUDE.md), o script para e explica o problema em vez de tentar adivinhar.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import markdown as md_lib
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "template"
OUTPUT_DIR = BASE_DIR / "output"

# Ver template/especificacao_visual.md (extraída dos PDFs em referencia/).
INSTITUICAO_PADRAO = "BAHIANA"
SUBTITULO_INSTITUICAO_PADRAO = "Escola de Medicina e Saúde Pública"
PROCESSO_SELETIVO_PADRAO = "PROSEF"
NOME_PROVA_PADRAO = "Simulado"
INSTRUCAO_PADRAO = (
    "Leia atentamente o resumo antes de responder. Assinale apenas uma "
    "alternativa por questão."
)

MD_EXTENSIONS = ["tables", "sane_lists"]


class FormatoInvalidoError(Exception):
    """Levantada quando o .md de entrada não segue o formato esperado."""


@dataclass
class Alternativa:
    letra: str
    texto: str


@dataclass
class Questao:
    numero: str
    texto_suporte_html: str
    fonte: str | None
    comando_html: str
    alternativas: list[Alternativa]


@dataclass
class ItemGabarito:
    numero: str
    correta: str
    justificativa_html: str


@dataclass
class Documento:
    titulo: str
    resumo_html: str
    questoes: list[Questao] = field(default_factory=list)
    gabarito: list[ItemGabarito] = field(default_factory=list)


def _sem_acentos_maiusculo(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).upper()


def _md_para_html(texto: str) -> str:
    return md_lib.markdown(texto.strip(), extensions=MD_EXTENSIONS)


HEADER_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$", re.MULTILINE)
BLOCO_RE = re.compile(r"^BLOCO\s+\d+\b", re.IGNORECASE)


def _varrer_cabecalhos_de_secao(
    texto: str, exigir_prefixo_bloco: bool
) -> tuple[int | None, int | None, int | None]:
    resumo_pos = questoes_pos = gabarito_pos = None

    for m in HEADER_RE.finditer(texto):
        titulo_bruto = m.group(2).strip()
        if exigir_prefixo_bloco and not BLOCO_RE.match(titulo_bruto):
            continue
        titulo_normalizado = _sem_acentos_maiusculo(titulo_bruto)
        # Um cabeçalho que menciona mais de uma palavra-chave (ex.: um
        # subtítulo descritivo como "Resumo didático + 10 questões
        # objetivas") não é um marcador de seção de verdade — é só texto
        # descritivo. Só conta cabeçalho com exatamente uma palavra-chave.
        palavras_chave_presentes = sum(
            palavra in titulo_normalizado
            for palavra in ("RESUMO", "QUESTOES", "GABARITO")
        )
        if palavras_chave_presentes != 1:
            continue
        if gabarito_pos is None and "GABARITO" in titulo_normalizado:
            gabarito_pos = m.start()
        elif questoes_pos is None and "QUESTOES" in titulo_normalizado:
            questoes_pos = m.start()
        elif resumo_pos is None and "RESUMO" in titulo_normalizado:
            resumo_pos = m.start()

    return resumo_pos, questoes_pos, gabarito_pos


def _localizar_secoes(texto: str) -> tuple[int, int, int, int]:
    """Retorna as posições (início) dos cabeçalhos de resumo, questões e
    gabarito, mais o tamanho do texto, para fatiar o documento em 3 blocos."""
    # Os .md reais do projeto "Bahiana" usam cabeçalhos "BLOCO N — ...";
    # priorizar esse padrão evita confundir um subtítulo qualquer (ex.: "##
    # 10 questões objetivas inéditas...", logo abaixo do título) com o
    # marcador de seção de verdade. Só cai para a varredura solta (qualquer
    # cabeçalho com uma palavra-chave) se não houver cabeçalhos "BLOCO N".
    resumo_pos, questoes_pos, gabarito_pos = _varrer_cabecalhos_de_secao(
        texto, exigir_prefixo_bloco=True
    )
    if questoes_pos is None or gabarito_pos is None:
        resumo_pos, questoes_pos, gabarito_pos = _varrer_cabecalhos_de_secao(
            texto, exigir_prefixo_bloco=False
        )

    if questoes_pos is None:
        raise FormatoInvalidoError(
            "Não encontrei um cabeçalho de seção para as questões "
            '(esperado algo como "## Questões"). Verifique o .md de entrada.'
        )
    if gabarito_pos is None:
        raise FormatoInvalidoError(
            "Não encontrei um cabeçalho de seção para o gabarito "
            '(esperado algo como "## Gabarito e Justificativas"). '
            "Verifique o .md de entrada."
        )
    if gabarito_pos < questoes_pos:
        raise FormatoInvalidoError(
            "A seção de gabarito aparece antes da seção de questões no "
            ".md — verifique a ordem das seções (resumo, questões, gabarito)."
        )
    if resumo_pos is not None and resumo_pos >= questoes_pos:
        raise FormatoInvalidoError(
            "O cabeçalho de resumo que encontrei aparece depois (ou junto) "
            "do cabeçalho de questões — provavelmente confundi um subtítulo "
            "descritivo com o marcador de seção. Verifique os cabeçalhos do "
            ".md (a seção de resumo deve vir antes da de questões)."
        )
    if resumo_pos is None:
        resumo_pos = 0

    return resumo_pos, questoes_pos, gabarito_pos, len(texto)


QUESTAO_HEADER_RE = re.compile(
    r"^(?:#{1,6}\s+|\*\*)\s*QUEST[ÃA]O\s*0*([0-9]+)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)

ALTERNATIVA_RE = re.compile(
    r"^[ \t]*([A-E])\)[ \t]+(.+?)\s*$", re.MULTILINE
)

FONTE_RE = re.compile(
    r"^[ \t]*[*_]{0,2}\(?\s*Fonte\s*:?\s*(.*?)\s*\)?[*_]{0,2}[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)


def _extrair_fonte_de_paragrafo(paragrafo: str) -> str | None:
    """Reconhece tanto o formato explícito ("Fonte: ...") quanto um
    parágrafo inteiro em itálico simples (*...*), convenção usada para a
    referência da fonte do texto-suporte em alguns .md reais."""
    p = paragrafo.strip()
    m = FONTE_RE.match(p)
    if m:
        return m.group(1).strip()
    if (
        len(p) >= 2
        and p.startswith("*")
        and p.endswith("*")
        and not p.startswith("**")
        and not p.endswith("**")
    ):
        texto = p[1:-1].strip()
        texto = re.sub(r"^\(?\s*Fonte\s*:?\s*", "", texto, flags=re.IGNORECASE)
        return texto.rstrip(")").strip()
    return None


def _dividir_por_questao(bloco: str) -> list[tuple[str, str]]:
    """Divide um bloco de texto em (numero, conteudo) por cabeçalho de questão."""
    marcadores = list(QUESTAO_HEADER_RE.finditer(bloco))
    if not marcadores:
        raise FormatoInvalidoError(
            "Não encontrei nenhum cabeçalho de questão (esperado algo como "
            '"### Questão 1") dentro da seção de questões/gabarito.'
        )
    partes = []
    for i, m in enumerate(marcadores):
        inicio = m.end()
        fim = marcadores[i + 1].start() if i + 1 < len(marcadores) else len(bloco)
        partes.append((m.group(1), bloco[inicio:fim].strip()))
    return partes


def _parsear_questao(numero: str, conteudo: str) -> Questao:
    alternativas_match = list(ALTERNATIVA_RE.finditer(conteudo))
    letras_encontradas = [m.group(1).upper() for m in alternativas_match]

    if letras_encontradas != ["A", "B", "C", "D", "E"]:
        raise FormatoInvalidoError(
            f"Questão {numero}: esperava alternativas A) a E), em ordem e "
            f"nesse formato exato, mas encontrei: {letras_encontradas or 'nenhuma'}. "
            "Corrija o .md de entrada em vez de adivinhar a estrutura."
        )

    inicio_alternativas = alternativas_match[0].start()
    corpo_antes = conteudo[:inicio_alternativas].strip()

    paragrafos = [p for p in re.split(r"\n\s*\n", corpo_antes) if p.strip()]
    if not paragrafos:
        raise FormatoInvalidoError(
            f"Questão {numero}: não encontrei texto de comando antes das "
            "alternativas. Verifique o .md de entrada."
        )

    comando_md = paragrafos[-1]
    resto = paragrafos[:-1]

    fonte = None
    texto_suporte_paragrafos = []
    for p in resto:
        if fonte is None:
            candidato = _extrair_fonte_de_paragrafo(p)
            if candidato is not None:
                fonte = candidato
                continue
        texto_suporte_paragrafos.append(p)

    texto_suporte_md = "\n\n".join(texto_suporte_paragrafos)

    alternativas = [
        Alternativa(letra=m.group(1).upper(), texto=m.group(2).strip())
        for m in alternativas_match
    ]

    return Questao(
        numero=numero,
        texto_suporte_html=_md_para_html(texto_suporte_md) if texto_suporte_md else "",
        fonte=fonte,
        comando_html=_md_para_html(comando_md),
        alternativas=alternativas,
    )


TABELA_GABARITO_LINHA_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([A-E])\s*\|", re.IGNORECASE | re.MULTILINE
)


def _parsear_gabarito(bloco: str) -> list[ItemGabarito]:
    linhas_tabela = list(TABELA_GABARITO_LINHA_RE.finditer(bloco))
    if not linhas_tabela:
        raise FormatoInvalidoError(
            "Não encontrei a tabela 'Questão | Alternativa Correta' na "
            "seção de gabarito. Verifique o formato da tabela no .md."
        )
    corretas = {m.group(1): m.group(2).upper() for m in linhas_tabela}

    fim_tabela = linhas_tabela[-1].end()
    resto = bloco[fim_tabela:]

    justificativas = dict(_dividir_por_questao(resto)) if QUESTAO_HEADER_RE.search(resto) else {}

    itens = []
    for numero, correta in corretas.items():
        justificativa_md = justificativas.get(numero, "")
        if not justificativa_md:
            raise FormatoInvalidoError(
                f"Gabarito: não encontrei a justificativa da questão {numero} "
                '(esperado um cabeçalho "### Questão '
                f'{numero}" com a justificativa de cada alternativa).'
            )
        itens.append(
            ItemGabarito(
                numero=numero,
                correta=correta,
                justificativa_html=_md_para_html(justificativa_md),
            )
        )
    return itens


def parsear_documento(caminho: Path) -> Documento:
    texto = caminho.read_text(encoding="utf-8")

    titulo_match = re.search(r"^#\s+(.*\S)\s*$", texto, re.MULTILINE)
    titulo = titulo_match.group(1) if titulo_match else caminho.stem.replace("_", " ").title()

    resumo_ini, questoes_ini, gabarito_ini, fim = _localizar_secoes(texto)

    resumo_bloco = texto[resumo_ini:questoes_ini]
    resumo_sem_header = HEADER_RE.sub("", resumo_bloco, count=1).strip()

    questoes_bloco = texto[questoes_ini:gabarito_ini]
    questoes_sem_header = HEADER_RE.sub("", questoes_bloco, count=1).strip()

    gabarito_bloco = texto[gabarito_ini:fim]
    gabarito_sem_header = HEADER_RE.sub("", gabarito_bloco, count=1).strip()

    questoes = [
        _parsear_questao(numero, conteudo)
        for numero, conteudo in _dividir_por_questao(questoes_sem_header)
    ]
    gabarito = _parsear_gabarito(gabarito_sem_header)

    numeros_questoes = {q.numero for q in questoes}
    numeros_gabarito = {g.numero for g in gabarito}
    if numeros_questoes != numeros_gabarito:
        raise FormatoInvalidoError(
            "As questões da seção de questões e as da seção de gabarito não "
            f"batem. Questões: {sorted(numeros_questoes, key=int)} | "
            f"Gabarito: {sorted(numeros_gabarito, key=int)}."
        )

    return Documento(
        titulo=titulo,
        resumo_html=_md_para_html(resumo_sem_header),
        questoes=questoes,
        gabarito=gabarito,
    )


def slugify(texto: str) -> str:
    texto = _sem_acentos_maiusculo(texto).lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return texto or "prova"


def renderizar_pdf(
    doc: Documento,
    caminho_saida: Path,
    incluir_gabarito: bool,
    instituicao: str,
    subtitulo_instituicao: str,
    processo_seletivo: str,
    nome_prova: str,
    instrucao: str,
) -> None:
    # Import local para não exigir dependências nativas do weasyprint em
    # quem só quer testar o parsing (ex.: em ambientes sem libpango etc.).
    from weasyprint import HTML

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("prova.html")

    html_final = template.render(
        titulo=doc.titulo,
        instituicao=instituicao,
        subtitulo_instituicao=subtitulo_instituicao,
        processo_seletivo=processo_seletivo,
        nome_prova=nome_prova,
        instrucao=instrucao,
        resumo_html=doc.resumo_html,
        questoes=doc.questoes,
        incluir_gabarito=incluir_gabarito,
        gabarito=doc.gabarito,
    )

    HTML(string=html_final, base_url=str(TEMPLATE_DIR)).write_pdf(str(caminho_saida))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo_md", type=Path, help="Arquivo .md em questoes-md/")
    parser.add_argument(
        "--sem-gabarito",
        action="store_true",
        help="Gera apenas resumo + questões, sem a seção de gabarito.",
    )
    parser.add_argument(
        "--instituicao", default=INSTITUICAO_PADRAO,
        help=f"Nome da instituição no cabeçalho/rodapé (padrão: {INSTITUICAO_PADRAO}).",
    )
    parser.add_argument(
        "--processo-seletivo", default=PROCESSO_SELETIVO_PADRAO,
        help=f"Nome do processo seletivo no cabeçalho (padrão: {PROCESSO_SELETIVO_PADRAO}).",
    )
    parser.add_argument(
        "--subtitulo-instituicao", default=SUBTITULO_INSTITUICAO_PADRAO,
        help=f"Subtítulo sob o nome da instituição (padrão: {SUBTITULO_INSTITUICAO_PADRAO}).",
    )
    parser.add_argument(
        "--nome-prova", default=NOME_PROVA_PADRAO,
        help=f"Nome da prova na barra escura do cabeçalho (padrão: {NOME_PROVA_PADRAO}).",
    )
    parser.add_argument(
        "--instrucao", default=INSTRUCAO_PADRAO,
        help="Texto da barra de instrução no topo da 1ª página.",
    )
    parser.add_argument(
        "--saida", type=Path, default=None,
        help="Caminho do PDF de saída (padrão: output/[tema]_[data].pdf).",
    )
    args = parser.parse_args()

    if not args.arquivo_md.exists():
        print(f"Erro: arquivo não encontrado: {args.arquivo_md}", file=sys.stderr)
        sys.exit(1)

    try:
        doc = parsear_documento(args.arquivo_md)
    except FormatoInvalidoError as e:
        print(f"Erro de formato em {args.arquivo_md}:\n  {e}", file=sys.stderr)
        sys.exit(1)

    if args.saida:
        caminho_saida = args.saida
    else:
        OUTPUT_DIR.mkdir(exist_ok=True)
        sufixo = "_sem-gabarito" if args.sem_gabarito else ""
        caminho_saida = OUTPUT_DIR / f"{slugify(doc.titulo)}{sufixo}_{date.today().isoformat()}.pdf"

    renderizar_pdf(
        doc,
        caminho_saida,
        incluir_gabarito=not args.sem_gabarito,
        instituicao=args.instituicao,
        subtitulo_instituicao=args.subtitulo_instituicao,
        processo_seletivo=args.processo_seletivo,
        nome_prova=args.nome_prova,
        instrucao=args.instrucao,
    )
    print(f"PDF gerado: {caminho_saida}")


if __name__ == "__main__":
    main()
