# -*- coding: utf-8 -*-
"""
Ajusta o Plano de Estudos (Praticante de Prático) para iniciar em 06/07/2026,
mantendo a prova prevista para setembro/2027.

O QUE ESTE SCRIPT FAZ:
1. Desloca as datas das Semanas 1 a 50 em +56 dias (8 semanas) — Fase 1 (semanas
   1-26) e o corpo principal da Fase 2 (semanas 27-50) ficam com o MESMO
   conteúdo, apenas em datas posteriores.
2. Substitui o bloco das antigas Semanas 51-56 (6 semanas de fechamento da
   Fase 2) por um bloco condensado de apenas 2 semanas (novas Semanas 51-52),
   já posicionado imediatamente após a nova Semana 50.
3. Atualiza os textos globais fixos (barra lateral "Início" e frase de
   abertura do dashboard).
4. Atualiza o array PHASES (períodos e cargas horárias de F1/F2/F3).

NÃO faz: não cria o conteúdo detalhado da Fase 3 (isso fica para uma sessão
futura dedicada, quando o calendário real já estiver fixado).

USO:
    python3 ajustar_plano_datas.py /caminho/para/Plano_de_Estudos_Standalone.html

O script cria um backup automático (.bak) antes de sobrescrever o arquivo.
"""
import re
import sys
import shutil
import datetime as dt

MESES = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',
         7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}
MESES_INV = {v: k for k, v in MESES.items()}

SHIFT = dt.timedelta(days=56)

FASE3_BLOCK = """['w53',3,53,'Revisão sistemática final — Manobrabilidade e Arte Naval','05–11/Jul/2027 · Semana 53','Manobrabilidade + Arte Naval',33,
  'Primeira semana da Fase 3. Revisão ativa de todos os tópicos de Manobrabilidade (1–8) e Arte Naval (Fases 1 e 2) apenas por mapas mentais e fichas — sem releitura de livros, exceto onde uma lacuna específica exigir. Dois simulados disciplinares cronometrados.',
  [['Seg','#e1f5ee','#085041',5,'Revisão ativa Manobrabilidade — tópicos 1 a 4 (mapas mentais e fichas)','Resistência, propulsão, lemes e controlabilidade — sem leitura nova'],
   ['Ter','#e1f5ee','#085041',5,'Revisão ativa Manobrabilidade — tópicos 5 a 8 + simulado cronometrado (40 q.)','Parada, águas rasas, forças ambientais, documentos a bordo · meta >= 70%'],
   ['Qua','#e6f1fb','#185fa5',5,'Revisão ativa Arte Naval — nomenclatura, governo, atracação/desatracação','Mapas mentais e fichas — sem leitura nova'],
   ['Qui','#e6f1fb','#185fa5',5,'Revisão ativa Arte Naval — pilot transfer, MPX, emergências (STS/SBM) + simulado (40 q.)','Meta >= 70%'],
   ['Sex','#534ab7','#eeedfe',5,'Releitura cruzada dos mapas mentais — identificar as últimas lacunas reais','Produto da semana: lista priorizada de pontos residuais'],
   ['Sab','#185fa5','#e6f1fb',7,'Simulado misto Manobrabilidade + Arte Naval — 50 q. cronometradas (condição de prova)','Meta >= 70% · registrar no Controle de Exercícios'],
   ['Dom','#f1efe8','#5f5e5a',1,'Organização e preparo Semana 54','Máximo 1h']],
  ['Mapas mentais de Manobrabilidade e Arte Naval revisados integralmente','Simulado Manobrabilidade (40 q.) realizado com meta >= 70%','Simulado Arte Naval (40 q.) realizado com meta >= 70%','Simulado misto (50 q.) realizado com meta >= 70%'],
  []],

['w54',3,54,'Revisão sistemática final — Navegação, Meteorologia, Comunicações e CG','12–18/Jul/2027 · Semana 54','Navegação + Meteorologia + Comunicações + CG',33,
  'Revisão ativa de Navegação (COLREG, radar, marés, balizamento, BRM, planejamento, VTS), Meteorologia, Comunicações (GMDSS, IMO SMCP) e Capitania dos Portos/CG (NORMAM, tráfego marítimo) — apenas por mapas mentais e fichas. Simulados disciplinares cronometrados.',
  [['Seg','#534ab7','#eeedfe',5,'Revisão ativa Navegação — COLREG, radar, marés e balizamento','Mapas mentais e fichas — sem leitura nova'],
   ['Ter','#534ab7','#eeedfe',5,'Revisão ativa Navegação — BRM, planejamento de viagem, VTS, canal + simulado (40 q.)','Meta >= 70%'],
   ['Qua','#3b6d11','#eaf3de',5,'Revisão ativa Meteorologia — sistemas sinóticos, ondas, PIANC 117 + simulado (30 q.)','Meta >= 65%'],
   ['Qui','#0c447c','#e6f1fb',5,'Revisão ativa Comunicações — GMDSS, fraseologia IMO SMCP + simulado (20 q.)','Meta >= 65%'],
   ['Sex','#085041','#e1f5ee',5,'Revisão ativa Capitania dos Portos/CG — NORMAM e tráfego marítimo + simulado (20 q.)','Meta >= 65%'],
   ['Sab','#534ab7','#eeedfe',7,'Simulado misto Navegação + Meteorologia + Comunicações + CG — 50 q. cronometradas','Meta >= 68% · registrar no Controle de Exercícios'],
   ['Dom','#f1efe8','#5f5e5a',1,'Organização e preparo Semana 55','Máximo 1h']],
  ['Mapas mentais de Navegação, Meteorologia, Comunicações e CG revisados integralmente','Simulados disciplinares (Navegação, Meteorologia, Comunicações, CG) realizados','Simulado misto (50 q.) realizado com meta >= 68%'],
  []],

['w55',3,55,'Revisão sistemática final — Legislação e tópicos finais do CP','19–25/Jul/2027 · Semana 55','Legislação + Direito Processual + Economia Marítima',33,
  'Revisão integral de Legislação (Lei 9.537/1997, Lei 14.813/2024, Decreto 2.596/1998, NORMAM-311 e correlatas, Lei dos Portos) apenas pelas fichas. Revisão de Direito Processual Marítimo (Pimenta), Ética/Conduta Profissional/Direitos Humanos, Economia Marítima e Amazônia Azul, e Meio Ambiente (tópicos 6, 7 e 8 do CP).',
  [['Seg','#a32d2d','#fcebeb',5,'Revisão integral de Legislação — LESTA, Lei 14.813/2024, Decreto 2.596/1998, NORMAM-311','Apenas pelas fichas — sem releitura dos diplomas integrais'],
   ['Ter','#a32d2d','#fcebeb',5,'Revisão integral de Legislação — Lei dos Portos, Tribunal Marítimo, NORMAMs correlatas + simulado (40 q.)','Meta >= 70%'],
   ['Qua','#633806','#faeeda',5,'Revisão — Direito Processual Marítimo (Pimenta) + Ética, conduta profissional e Direitos Humanos','Mapas mentais e fichas'],
   ['Qui','#633806','#faeeda',5,'Revisão — Economia Marítima e Amazônia Azul + Meio Ambiente (poluição por navios) + simulado (30 q.)','Meta >= 60%'],
   ['Sex','#a32d2d','#fcebeb',5,'Releitura cruzada de todas as fichas de legislação — últimas lacunas reais','Produto da semana: lista final de pontos residuais de legislação'],
   ['Sab','#a32d2d','#fcebeb',7,'Simulado integrado Legislação + tópicos finais do CP — 50 q. cronometradas','Meta >= 68% · registrar no Controle de Exercícios'],
   ['Dom','#f1efe8','#5f5e5a',1,'Organização e preparo Semana 56','Máximo 1h']],
  ['Legislação revisada integralmente pelas fichas','Direito Processual Marítimo, Ética e Direitos Humanos revisados','Economia Marítima, Amazônia Azul e Meio Ambiente revisados','Simulado integrado (50 q.) realizado com meta >= 68%'],
  []],

['w56',3,56,'Prova real completa cronometrada nº 1 — PSCPP/2011','26/Jul–01/Ago/2027 · Semana 56','Simulado real cronometrado',33,
  'Primeira das três provas reais de praticagem realizadas em condição integral de prova (mesmo número de questões, mesmo tempo oficial). Correção comentada questão a questão. Análise de padrões de erro (disciplina, tipo de armadilha, tempo gasto) e reforço dirigido.',
  [['Seg','#faeeda','#633806',5,'Prova real completa cronometrada — PSCPP/2011 (Prova Amarela), tempo oficial','Sem consulta · condição idêntica à prova real'],
   ['Ter','#faeeda','#633806',5,'Correção detalhada — gabarito comentado, questão a questão','Registrar cada erro no Controle de Exercícios com a causa'],
   ['Qua','#faeeda','#633806',5,'Análise de padrões de erro — disciplina, tipo de armadilha, tempo gasto por questão','Identificar os 3 principais padrões a corrigir'],
   ['Qui','#faeeda','#633806',5,'Reforço dirigido nos 3 principais pontos de erro identificados','Releitura cirúrgica das fontes primárias correspondentes'],
   ['Sex','#faeeda','#633806',5,'Atualização das fichas e mapas mentais com os pontos reforçados','Fechar o ciclo de reforço da semana'],
   ['Sab','#faeeda','#633806',7,'20 questões de verificação focadas nos pontos reforçados + revisão geral leve','Confirmar recuperação antes da Semana 57'],
   ['Dom','#f1efe8','#5f5e5a',1,'Organização e preparo Semana 57','Máximo 1h']],
  ['Prova real PSCPP/2011 realizada em condição cronometrada integral','Correção comentada completa registrada no Controle de Exercícios','3 principais padrões de erro identificados e reforçados'],
  []],

['w57',3,57,'Prova real completa cronometrada nº 2 — PSCPP/2012 (Prova Rosa)','02–08/Ago/2027 · Semana 57','Simulado real cronometrado',33,
  'Segunda prova real em condição integral de prova. Mesma metodologia de correção e reforço da Semana 56, agora comparando a evolução de desempenho entre as duas provas reais já realizadas.',
  [['Seg','#faeeda','#633806',5,'Prova real completa cronometrada — PSCPP/2012 (Prova Rosa), tempo oficial','Sem consulta · condição idêntica à prova real'],
   ['Ter','#faeeda','#633806',5,'Correção detalhada — gabarito comentado, questão a questão','Registrar cada erro no Controle de Exercícios com a causa'],
   ['Qua','#faeeda','#633806',5,'Análise comparativa PSCPP/2011 vs. PSCPP/2012 — evoluiu, estagnou ou regrediu?','Por disciplina e por tipo de questão'],
   ['Qui','#faeeda','#633806',5,'Reforço dirigido nos pontos de erro que se repetiram nas duas provas','Prioridade máxima: erros recorrentes'],
   ['Sex','#faeeda','#633806',5,'Atualização das fichas e mapas mentais com os pontos reforçados','Fechar o ciclo de reforço da semana'],
   ['Sab','#faeeda','#633806',7,'20 questões de verificação focadas + revisão geral leve','Confirmar recuperação antes da Semana 58'],
   ['Dom','#f1efe8','#5f5e5a',1,'Organização e preparo Semana 58','Máximo 1h']],
  ['Prova real PSCPP/2012 realizada em condição cronometrada integral','Análise comparativa entre as duas provas reais registrada','Erros recorrentes entre as duas provas identificados e reforçados'],
  []],

['w58',3,58,'Prova real completa cronometrada nº 3 — PSCPP/2008 + reforço geral','09–15/Ago/2027 · Semana 58','Simulado real cronometrado',33,
  'Terceira e última prova real em condição integral de prova. Análise comparativa das três provas reais realizadas na Fase 3. Reforço final dirigido em todas as disciplinas e verificação de 100% dos checklists de conteúdo programático.',
  [['Seg','#faeeda','#633806',5,'Prova real completa cronometrada — PSCPP/2008, tempo oficial','Sem consulta · condição idêntica à prova real'],
   ['Ter','#faeeda','#633806',5,'Correção detalhada — gabarito comentado, questão a questão','Registrar cada erro no Controle de Exercícios com a causa'],
   ['Qua','#faeeda','#633806',5,'Análise comparativa das 3 provas reais (2011, 2012, 2008) — evolução de desempenho','Por disciplina e por tipo de questão'],
   ['Qui','#faeeda','#633806',5,'Reforço final dirigido nas lacunas remanescentes — todas as disciplinas','Última oportunidade de reforço antes dos simulados finais'],
   ['Sex','#faeeda','#633806',5,'Releitura final de mapas mentais e fichas — checklist de 100% do CP','Nenhum subtópico do Conteúdo Programático pode ficar pendente'],
   ['Sab','#185fa5','#e6f1fb',7,'Simulado geral integrado — 80 questões (todas as disciplinas, condição real)','Meta >= 70% · registrar no Controle de Exercícios'],
   ['Dom','#f1efe8','#5f5e5a',1,'Organização e preparo Semana 59','Máximo 1h']],
  ['Prova real PSCPP/2008 realizada em condição cronometrada integral','Análise comparativa das 3 provas reais completa','Checklist de 100% do Conteúdo Programático verificado','Simulado geral integrado (80 q.) realizado com meta >= 70%'],
  []],

['w59',3,59,'Reforço cirúrgico final e simulado geral integrado','16–22/Ago/2027 · Semana 59','Todas as disciplinas',35,
  'Última semana de conteúdo ativo antes da desaceleração final. Reforço cirúrgico nos últimos pontos de lacuna identificados na Semana 58. Revisão geral de todas as disciplinas apenas por fichas e mapas mentais. Simulado geral integrado final, em tudo idêntico ao formato oficial (100 questões, tempo oficial, sem consulta).',
  [['Seg','#faeeda','#633806',5,'Reforço cirúrgico nos últimos pontos de lacuna (baseado na Semana 58)','Foco total nos 2-3 pontos mais críticos remanescentes'],
   ['Ter','#e1f5ee','#085041',5,'Revisão geral — Manobrabilidade + Arte Naval (apenas fichas e mapas mentais)','Sem leitura nova'],
   ['Qua','#534ab7','#eeedfe',5,'Revisão geral — Navegação + Meteorologia + Comunicações + CG (fichas e mapas)','Sem leitura nova'],
   ['Qui','#a32d2d','#fcebeb',5,'Revisão geral — Legislação + tópicos finais do CP (fichas e mapas)','Sem leitura nova'],
   ['Sex','#f1efe8','#5f5e5a',5,'Preparação do simulado final — descanso leve, organização do material e do local de prova','Reduzir a carga mental antes do simulado de sábado'],
   ['Sab','#185fa5','#e6f1fb',7,'Simulado geral integrado final — 100 questões, tempo oficial, sem consulta','Condição idêntica à prova oficial · registrar no Controle de Exercícios'],
   ['Dom','#faeeda','#633806',3,'Análise do simulado final + checklist de 100% de todo o programa','Última verificação de prontidão antes da Semana 60']],
  ['Reforço cirúrgico final concluído','Revisão geral de todas as disciplinas (fichas/mapas) realizada','Simulado geral integrado final (100 q.) realizado em condição oficial','Checklist de 100% de todo o programa (Fases 1, 2 e 3) verificado'],
  []],

['w60',3,60,'Semana de desaceleração e preparação para a prova','23–29/Ago/2027 · Semana 60','Desaceleração e logística',18,
  'Última semana antes do período de descanso final pré-prova. Sem leitura nova e sem simulados longos. Apenas releitura leve das fichas e mapas mentais já criados, um simulado curto de aquecimento e organização da logística do dia da prova (documentos, local, horário, materiais permitidos).',
  [['Seg','#e1f5ee','#085041',3,'Releitura leve — fichas e mapas mentais de Manobrabilidade e Arte Naval','Sem questões — apenas releitura visual'],
   ['Ter','#534ab7','#eeedfe',3,'Releitura leve — fichas e mapas mentais de Navegação, Meteorologia, Comunicações e CG','Sem questões — apenas releitura visual'],
   ['Qua','#a32d2d','#fcebeb',3,'Releitura leve — fichas e mapas mentais de Legislação e tópicos finais do CP','Sem questões — apenas releitura visual'],
   ['Qui','#faeeda','#633806',3,'Simulado de aquecimento — 20 questões mistas, no ritmo da prova','Sem objetivo de nota — apenas manter o ritmo'],
   ['Sex','#f1efe8','#5f5e5a',2,'Organização da logística do dia da prova','Documentos exigidos, local, horário, materiais permitidos, trajeto'],
   ['Sab','#f1efe8','#5f5e5a',3,'Descanso ativo + revisão visual rápida dos mapas mentais (30 min por disciplina)','Sem leitura de livros ou diplomas'],
   ['Dom','#f1efe8','#5f5e5a',1,'Descanso e preparação mental para a prova','Sem estudo — apenas descanso']],
  ['Logística do dia da prova 100% organizada','Releitura leve de todas as fichas concluída','Simulado de aquecimento realizado, sem foco em nota'],
  []]"""
  # exatamente 8 semanas -> preserva o dia da semana

CONDENSED_BLOCK = """['w51',2,51,'Diagnóstico final e reforço dirigido — Fase 2','21–27/Jun/2027 · Semana 51','Todas as disciplinas',33,
  'Quatro simulados temáticos condensados (Manobrabilidade avançada, Arte Naval avançada, Meteorologia+Comunicações+CG, Navegação avançada — 25 questões cada) seguidos de reforço imediato nas piores lacunas. Substitui o ciclo de diagnóstico+reforço de duas semanas por uma semana de maior intensidade.',
  [['Seg','#085041','#e1f5ee',5,'Simulado Manobrabilidade Fase 2 (25 q.) + análise de erros','Meta >= 65% · reforço dirigido no mesmo dia'],
   ['Ter','#185fa5','#e6f1fb',5,'Simulado Arte Naval Fase 2 (25 q.) + análise de erros','Meta >= 65% · reforço dirigido no mesmo dia'],
   ['Qua','#3b6d11','#eaf3de',5,'Simulado Meteorologia + Comunicações + CG (25 q.) + análise','Meta >= 60% · reforço dirigido no mesmo dia'],
   ['Qui','#534ab7','#eeedfe',5,'Simulado Navegação Fase 2 (25 q.) + análise de erros','Meta >= 65% · reforço dirigido no mesmo dia'],
   ['Sex','#faeeda','#633806',5,'Reforço intensivo nas 2 disciplinas com maior lacuna','Releitura das fontes primárias + 20 questões focadas por disciplina'],
   ['Sab','#faeeda','#633806',7,'Simulado misto de verificação — 30 questões (disciplinas recuperadas)','Confirmar recuperação >= 65% antes de seguir para a Semana 52'],
   ['Dom','#f1efe8','#5f5e5a',1,'Organização e preparo Semana 52','Máximo 1h']],
  ['4 simulados temáticos (25 q. cada) realizados e analisados','Reforço dirigido nas 2 piores disciplinas concluído','Simulado misto de verificação (30 q.) com meta >= 65%'],
  []],

['w52',2,52,'Revisão integrada final e fechamento da Fase 2','28/Jun–04/Jul/2027 · Semana 52','Todas as disciplinas',35,
  'Revisão integrada condensada de Manobrabilidade, Arte Naval e Navegação+Meteorologia (Fases 1 e 2), com um simulado por disciplina no mesmo dia, seguida de simulado integrado final, verificação de checklists e preparação para a Fase 3 (revisão e simulados finais).',
  [['Seg','#e1f5ee','#085041',5,'Revisão ativa Manobrabilidade (tópicos 1–8) + simulado integrado (40 q.)','Meta >= 70% · registrar no Controle de Exercícios'],
   ['Ter','#e6f1fb','#185fa5',5,'Revisão ativa Arte Naval (Fases 1 e 2) + simulado integrado (40 q.)','Meta >= 70% · registrar no Controle de Exercícios'],
   ['Qua','#534ab7','#eeedfe',5,'Revisão ativa Navegação + Meteorologia + simulado integrado (40 q.)','Meta >= 65% · registrar no Controle de Exercícios'],
   ['Qui','#a32d2d','#fcebeb',5,'Revisão integrada de Legislação — releitura de fichas (Fases 1 e 2)','Não os diplomas integrais — apenas as fichas criadas'],
   ['Sex','#185fa5','#e6f1fb',5,'Simulado integrado Fases 1+2 — 80 questões (todas as disciplinas)','Meta >= 68% · 2 horas cronometradas'],
   ['Sab','#185fa5','#e6f1fb',7,'Verificação de 100% dos checklists + organização de todo o material','Pasta 00_GESTAO/ — arquivo de revisão completo da Fase 2'],
   ['Dom','#f1efe8','#5f5e5a',3,'Análise final do simulado integrado + briefing da Fase 3','Identificar as principais lacunas residuais para a Fase 3 · transição planejada']],
  ['Simulados integrados de Manobrabilidade, Arte Naval e Navegação+Meteorologia (40 q. cada) realizados','Simulado integrado Fases 1+2 (80 q.) realizado com meta >= 68%','Checklists da Fase 2 — 100% verificados','Material da Fase 2 organizado e arquivado','Principais lacunas residuais para a Fase 3 identificadas'],
  [['Essencial','Todo o material produzido na Fase 2','Mapas, fichas, flashcards — pasta 00_GESTAO/']]]"""


def fmt_period(d_ini, d_fim, n):
    if d_ini.month == d_fim.month:
        s = f"{d_ini.day:02d}–{d_fim.day:02d}/{MESES[d_fim.month]}/{d_fim.year}"
    elif d_ini.year == d_fim.year:
        s = f"{d_ini.day:02d}/{MESES[d_ini.month]}–{d_fim.day:02d}/{MESES[d_fim.month]}/{d_fim.year}"
    else:
        s = f"{d_ini.day:02d}/{MESES[d_ini.month]}/{d_ini.year}–{d_fim.day:02d}/{MESES[d_fim.month]}/{d_fim.year}"
    return f"{s} · Semana {n}"


def parse_period(s):
    m = re.match(r"(\d{2})(?:/([A-Za-z]{3})(?:/(\d{4}))?)?–(\d{2})/([A-Za-z]{3})/(\d{4})", s)
    if not m:
        raise ValueError(f"Não foi possível interpretar o período: {s!r}")
    d1, mon1, year1_explicit, d2, mon2, year2 = m.groups()
    year2 = int(year2)
    mon2_n = MESES_INV[mon2]
    mon1_n = MESES_INV[mon1] if mon1 else mon2_n
    year1 = int(year1_explicit) if year1_explicit else (year2 if mon1_n <= mon2_n else year2 - 1)
    return dt.date(year1, mon1_n, int(d1)), dt.date(year2, mon2_n, int(d2))


def main(path):
    backup = path + ".bak"
    shutil.copy(path, backup)
    print(f"Backup criado em: {backup}")

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # 1) Substituir bloco das semanas 51-56 pelo bloco condensado 51-52
    i = content.find("['w51',2,51")
    if i == -1:
        print("AVISO: bloco da Semana 51 não encontrado — etapa de condensação pulada "
              "(arquivo pode já ter sido ajustado, ou a estrutura mudou).")
    else:
        j = content.find("\n\n];", i)
        if j == -1:
            raise RuntimeError("Não encontrei o fim do array que contém as semanas 51-56.")
        old_block = content[i:j]
        if not old_block.rstrip().endswith("]]]"):
            raise RuntimeError("O bloco encontrado não termina como esperado — revisar manualmente antes de continuar.")
        content = content[:i] + CONDENSED_BLOCK + content[j:]
        print("Bloco das semanas 51–56 substituído pelo bloco condensado 51–52.")

    # 2) Deslocar datas das semanas 1 a 50 em +56 dias
    pattern = re.compile(r"'(w(\d+))',(\d+),(\d+),\s*('[^']*'),\s*'([^']*Semana \d+)'")
    count = 0

    def repl(m):
        nonlocal count
        wid, _n_in_id, ph, n, title, period = m.groups()
        n = int(n)
        if n > 50:
            return m.group(0)
        d_ini, d_fim = parse_period(period)
        new_ini, new_fim = d_ini + SHIFT, d_fim + SHIFT
        count += 1
        return f"'{wid}',{ph},{n},{title},'{fmt_period(new_ini, new_fim, n)}'"

    content = pattern.sub(repl, content)
    print(f"Datas deslocadas em +56 dias para {count} semanas (esperado: 50).")
    if count != 50:
        print("ATENÇÃO: número de semanas deslocadas diferente de 50 — revisar antes de prosseguir.")

    # 3) Textos globais fixos
    content = content.replace(
        '<div class="sb-meta-val">11 Mai 26</div>',
        '<div class="sb-meta-val">06 Jul 26</div>'
    )
    content = content.replace(
        'Início em 11 de maio de 2026',
        'Início em 06 de julho de 2026'
    )

    # 4) Array PHASES
    content = content.replace(
        "{id:1,label:'F1',title:'Fundamentos e imersão',period:'11 Mai – 31 Out 2026',hours:'~600h'",
        "{id:1,label:'F1',title:'Fundamentos e imersão',period:'06 Jul 2026 – 03 Jan 2027',hours:'~650h'"
    )
    content = content.replace(
        "{id:2,label:'F2',title:'Aprofundamento técnico',period:'Nov 2026 – Mai 2027',hours:'~980h'",
        "{id:2,label:'F2',title:'Aprofundamento técnico',period:'04 Jan – 04 Jul 2027',hours:'~890h'"
    )
    content = content.replace(
        "{id:3,label:'F3',title:'Revisão e simulados',period:'Jun – Set 2027',hours:'~650h'",
        "{id:3,label:'F3',title:'Revisão e simulados',period:'05 Jul – 29 Ago 2027 (8 semanas)',hours:'~250h'"
    )

    # 5) Inserir as Semanas 53-60 (Fase 3) logo após a Semana 52
    i2 = content.find("['w52'")
    if i2 == -1:
        print("AVISO: Semana 52 não encontrada — etapa de inserção da Fase 3 pulada.")
    else:
        j2 = content.find("\n\n];", i2)
        if j2 == -1:
            raise RuntimeError("Não encontrei o fim do array que contém a Semana 52.")
        old_w52_entry = content[i2:j2]
        if not old_w52_entry.rstrip().endswith("]]]"):
            raise RuntimeError("A entrada da Semana 52 não termina como esperado — revisar manualmente.")
        content = content[:i2] + old_w52_entry + ",\n" + FASE3_BLOCK.strip() + content[j2:]
        print("Semanas 53-60 (Fase 3) inseridas após a Semana 52.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Arquivo atualizado com sucesso:", path)
    print("\nPróximo passo recomendado: validar a sintaxe JS e os dados, por exemplo")
    print("extraindo o conteúdo entre as tags <script> e rodando `node --check`.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 ajustar_plano_datas.py /caminho/para/Plano_de_Estudos_Standalone.html")
        sys.exit(1)
    main(sys.argv[1])
