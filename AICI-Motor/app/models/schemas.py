"""Modelos de dados trocados entre módulos e pela API."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Resultado = Literal["sem_conflito", "sem_conflito_ressalvas", "conflito", "outro"]


class Servidor(BaseModel):
    nome: str = ""
    cargo: str = ""
    matricula: str = ""
    unidade: str = ""
    processo: str = ""
    protocolo: str = ""
    tipo: Literal["pedido", "consulta", ""] = ""


class Fatos(BaseModel):
    """Saída do Módulo 3. Os campos principais seguem a especificação do projeto."""
    atividade: str = ""
    entidade: str = ""
    remuneracao: str = ""
    vinculo: str = ""
    descricao: str = ""
    atribuicoes: list[str] = Field(default_factory=list)
    servidor: Servidor = Field(default_factory=Servidor)
    respostas: dict[int, str] = Field(default_factory=dict)  # perguntas 1 a 10 do formulário SeCI
    origem: str = "heuristica"                                # heuristica | heuristica+ia


class Trecho(BaseModel):
    """Um pedaço recuperado da base de conhecimento, sempre com a origem."""
    id: str
    tipo: Literal["parecer", "precedente", "normativo", "modelo", "regra"]
    titulo: str
    fonte: str                      # caminho relativo em knowledge/
    texto: str
    tema: str = ""
    ano: str = ""
    numero: str = ""
    score: float = 0.0
    motivo: str = ""               # por que foi recuperado (termos em comum, tema)
    origem: str = "COGER"
    extra: dict = Field(default_factory=dict)


class Candidata(BaseModel):
    id: str
    nome: str
    score: float
    confianca: Literal["alta", "media", "baixa"]
    motivos: list[str] = Field(default_factory=list)


class Classificacao(BaseModel):
    escolhida: Optional[Candidata] = None
    candidatas: list[Candidata] = Field(default_factory=list)
    metodo: str = "lexical"
    avisos: list[str] = Field(default_factory=list)


class Paragrafo(BaseModel):
    texto: str
    tipo: Literal["p", "cit", "it"] = "p"             # parágrafo numerado, citação ou item de lista
    fontes: list[str] = Field(default_factory=list)   # RN: sempre informar a origem de cada entendimento


class Secao(BaseModel):
    titulo: str
    paragrafos: list[Paragrafo] = Field(default_factory=list)


class Minuta(BaseModel):
    """Estrutura institucional fixa: I - RELATÓRIO, II - FUNDAMENTAÇÃO, III - CONCLUSÃO."""
    secoes: list[Secao] = Field(default_factory=list)
    resultado_sugerido: Resultado = "sem_conflito_ressalvas"
    ressalvas: list[str] = Field(default_factory=list)
    modo: str = "offline"           # offline | copilot
    atividade_id: str = ""          # categoria do HTML em que a minuta se baseia
    variante_id: str = ""           # variante (situação) do modelo usada como base
    avisos: list[str] = Field(default_factory=list)


class Analise(BaseModel):
    consulta_id: int
    fatos: Fatos
    classificacao: Classificacao
    precedentes: list[Trecho] = Field(default_factory=list)
    pareceres: list[Trecho] = Field(default_factory=list)
    normativos: list[Trecho] = Field(default_factory=list)
    modelos: list[Trecho] = Field(default_factory=list)
    minuta: Optional[Minuta] = None
    avisos: list[str] = Field(default_factory=list)


class PedidoAnalise(BaseModel):
    consulta_id: int
    gerar_minuta: bool = True


class PedidoParecer(BaseModel):
    consulta_id: int
    documento: Literal["parecer", "termo", "despacho"] = "parecer"
    resultado: Optional[Resultado] = None       # escolha do parecerista (decisão humana, RN001)
    atividade_id: Optional[str] = None           # categoria confirmada/ajustada pelo parecerista
    minuta: Optional[Minuta] = None              # minuta revisada/editada na tela
    numero: str = ""
    ano: str = ""
    destino: str = ""                            # despacho
    validado: bool = False                       # o parecerista revisou fatos, enquadramento, fontes e compromissos (obrigatório)


class PedidoPacote(BaseModel):
    consulta_id: int
    resultado: Optional[Resultado] = None
    atividade_id: Optional[str] = None


class Pacote(BaseModel):
    """Material para o parecerista levar ao Copilot Chat (modo assistido)."""
    prompt: str                      # instrução + contexto, dentro do limite de caracteres do chat
    prompt_curto: str                # só a instrução: use com o arquivo de contexto anexado
    contexto_md: str                 # contexto completo, para anexar ao chat como arquivo
    limite_caracteres: int
    caracteres: int
    truncado: bool = False
    ids: list[str] = Field(default_factory=list)
    url_chat: str = ""
    avisos: list[str] = Field(default_factory=list)


class PedidoResposta(BaseModel):
    consulta_id: int
    texto: str                       # resposta colada do Copilot Chat
    modo: Literal["texto", "arquivo"] = "texto"   # como o contexto foi levado ao chat
    resultado: Optional[Resultado] = None
    atividade_id: Optional[str] = None
