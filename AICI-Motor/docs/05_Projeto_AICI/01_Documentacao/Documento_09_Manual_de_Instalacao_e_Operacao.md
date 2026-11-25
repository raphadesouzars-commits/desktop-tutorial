# Manual de Instalação e Operação - AICI-Motor

**Para:** equipe de TI e administrador do sistema. **Versão 0.3 - novembro/2026.** Estes passos foram exercitados em Linux (Python 3.13). **Windows e outros ambientes não foram validados.**

## 1. Requisitos

| Item | Requisito |
|---|---|
| Sistema | Linux ou Windows (a validar) |
| Python | 3.12 ou superior |
| Memória / disco | Modestos sem embeddings; 8 a 16 GB e alguns GB de disco para embeddings locais; cerca de 2 GB adicionais para OCR (estimativas, não medidas com o acervo real) |
| Rede | Entrada: usuários da COGER (via proxy HTTPS); saída: nenhuma obrigatória (o modo padrão não chama serviço externo) |
| Pacotes | `requirements.txt` (obrigatórios); `requirements-opcional.txt` (embeddings, Chroma, OCR) |

## 2. Instalação

```bash
unzip AICI-Motor.zip && cd AICI-Motor
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q                # confere o ambiente: todos os testes devem passar
python main.py                     # sobe em http://127.0.0.1:8765
```

Verificação: `GET /saude` deve responder `{"status":"ok", ...}`; a documentação interativa está em `/docs`.

Opcionais:

```bash
pip install sentence-transformers numpy    # busca por sentido (embeddings locais)
pip install easyocr                        # OCR de PDF digitalizado (puxa PyTorch)
pip install chromadb                       # backend vetorial alternativo
```

## 3. Estrutura de pastas

| Pasta | Função | Dados pessoais |
|---|---|---|
| `app/` | Código do motor | Não |
| `config/` | `settings.yaml` e `categorias.json` | Não |
| `knowledge/` | Base de conhecimento (pareceres, precedentes, normativos, modelos, `regras_coger.md`) | Sim (pareceres, precedentes) |
| `prompts/`, `templates/` | Instruções à IA; modelos Word e textos institucionais | Não |
| `uploads/`, `output/`, `metrics/`, `vectorstore/` | Operação, saídas, auditoria, índice | **Sim** |
| `scripts/` | Importação da biblioteca, exportação de categorias, geração de `regras_coger.md`, criação dos templates | Não |
| `tests/` | Testes automatizados | Não |

## 3a. Variáveis de ambiente

| Variável | Uso |
|---|---|
| `AICI_TOKEN` | Se definida, toda rota exige o cabeçalho `X-AICI-Token` com esse valor |
| `AICI_HOME` | Base do projeto (padrão: a pasta do código) |
| `AICI_CONFIG` | Caminho alternativo do `settings.yaml` |
| `AICI_COPILOT_TOKEN`, `AICI_AZURE_KEY`, `AICI_OPENAI_KEY` | Credenciais de provedores automáticos (só se a TI disponibilizar API); **nunca** no arquivo de configuração |

## 4. Configuração (`config/settings.yaml`)

| Chave | Padrão | Descrição |
|---|---|---|
| `servidor.host` / `porta` | `127.0.0.1` / `8765` | Escuta. Só altere atrás de proxy HTTPS com autenticação |
| `servidor.cors_origens` | `["null", "http://localhost:8765", "http://127.0.0.1:8765"]` | Origens autorizadas a chamar a API; inclua o endereço onde o HTML for hospedado |
| `caminhos.*` | pastas do projeto | Onde ficam conhecimento, índice, uploads, saídas, métricas, banco |
| `indexador.backend` | `lexical` | `lexical` (BM25) ou `chroma` |
| `recuperacao.top_k_*` | 4 | Quantos itens por tipo |
| `recuperacao.peso_coger` | 1,25 | Peso dos documentos da COGER |
| `recuperacao.embeddings.habilitado` | `false` | Liga a busca híbrida; `modelo` pode ser o caminho de uma pasta local |
| `ocr.habilitado` | `true` | OCR para PDF sem texto |
| `ia.provider` | `offline` | `offline`, `mock`, `copilot`, `azure`, `openai` |
| `ia.anonimizar` | `true` | Mascara identificadores antes de enviar à IA |
| `ia.copilot_chat.limite_caracteres` | 7500 | **Limite do prompt do Copilot Chat: confirme o valor real e ajuste** |
| `ia.copilot_chat.url` | `https://m365.cloud.microsoft/chat` | Link do botão "Abrir Copilot Chat" |
| `ia.auditoria.habilitada` / `registrar_conteudo` | `true` / `true` | Trilha de cada chamada à IA, com prompt e resposta mascarados |

## 5. Base de conhecimento

```bash
python scripts/importar_biblioteca.py /caminho/da/biblioteca            # copia/atualiza
python scripts/importar_biblioteca.py /caminho/da/biblioteca --sincronizar   # também apaga o que saiu da origem
curl -X POST http://127.0.0.1:8765/indexar                               # reindexa (incremental)
```

A pasta de origem deve ter `01_Pareceres_Emitidos`, `02_Precedentes`, `03_Normativos`, `04_Modelos_Institucionais`. `_Duplicados_Revisar` é ignorada. Nomes `PA_<número>_<ano>_<Tema>` geram os metadados. A indexação também ocorre ao iniciar o motor; só arquivos novos ou alterados são reprocessados. Use `POST /indexar?completo=true` para refazer tudo.

Sincronização automática com o SharePoint: **planejada** (hoje, copiar por rotina da TI para a pasta de origem e executar o script).

Regras da COGER:

```bash
python scripts/gerar_regras_coger.py      # regenera knowledge/regras_coger.md; preserva a seção "A consolidar pela COGER"
```

Se um modelo de atividade for alterado no gerador HTML: `python scripts/exportar_categorias.py`.

## 6. Hospedagem do gerador HTML e CORS

O `gerador-parecer-conflito.html` funciona aberto como arquivo ou hospedado. A aba "Análise Inteligente" precisa alcançar o motor: se o HTML for hospedado em outro endereço, inclua essa origem em `servidor.cors_origens`. Em rede interna, publique o motor atrás de proxy HTTPS e informe o endereço na aba.

## 7. Execução como serviço (exemplo Linux/systemd)

```ini
[Unit]
Description=AICI-Motor
After=network.target

[Service]
WorkingDirectory=/opt/aici/AICI-Motor
Environment=AICI_TOKEN=<definido pela TI>
ExecStart=/opt/aici/AICI-Motor/.venv/bin/python main.py
Restart=on-failure
User=aici

[Install]
WantedBy=multi-user.target
```

O equivalente em Windows (serviço ou tarefa agendada) fica a critério da TI. Não há imagem de contêiner pronta; ela pode ser construída a partir de `requirements.txt`.

## 8. Operação rotineira

| Tarefa | Frequência | Como |
|---|---|---|
| Atualizar a base | Quando houver pareceres/normativos novos | Seção 5 |
| Verificar a saúde | Diária ou por monitoramento | `GET /saude` |
| Cópia de segurança | Conforme política da TI | `knowledge/`, `config/`, `templates/`, `prompts/`, `metrics/`, `output/` (índice pode ser refeito) |
| Revisar a trilha de IA | Conforme rotina do curador | `metrics/ia_auditoria.jsonl` |
| Atualizar dependências | Conforme política da TI | `pip install -U -r requirements.txt` e `python -m pytest -q` |
| Descarte de dados | Conforme política de retenção (a definir) | Remover consultas antigas de `uploads/` e `output/` |

## 9. Solução de problemas

| Sintoma | Causa provável | Ação |
|---|---|---|
| A aba mostra "Não foi possível falar com o motor" | Motor desligado, endereço errado ou CORS | Verificar `python main.py`, o endereço na aba e `cors_origens` |
| HTTP 401 | Token ausente ou errado | Conferir `AICI_TOKEN` e o campo "Token" na aba |
| "PDF sem texto legível" | PDF digitalizado sem OCR | Instalar `easyocr` ou usar o gerador offline |
| Nenhum normativo/parecer recuperado | Base vazia ou não indexada | Seção 5; `POST /indexar` |
| `sentence-transformers não instalado` | Embeddings habilitados sem o pacote | Instalar ou desabilitar `recuperacao.embeddings` |
| Prompt do Copilot sem alguns trechos | Limite de caracteres | Ajustar `ia.copilot_chat.limite_caracteres` (conforme a TI) ou usar prompt curto + arquivo |
| Word com campos amarelos | Dados não presentes no PDF (unidade, processo, signatário) | Completar no Word; normal |
| Teste falhando após atualizar | Dependência incompatível | Reverter a versão do pacote |

## 10. Segurança operacional

- Mantenha o motor em `127.0.0.1` ou atrás de proxy HTTPS com autenticação institucional; defina `AICI_TOKEN`.
- Restrinja o acesso às pastas `uploads/`, `output/`, `metrics/`, `vectorstore/` e `knowledge/pareceres|precedentes` (contêm dados pessoais).
- Não versione nem envie esses dados por e-mail.
- Credenciais só em variáveis de ambiente.
- Aplique a criptografia em repouso, a retenção e os controles definidos pela Cotec e pela Análise de Riscos.

## 11. Desinstalação
Parar o serviço, copiar o que for necessário, e apagar a pasta do projeto, incluindo `uploads/`, `output/`, `metrics/` e `vectorstore/`, conforme a política de descarte.
