# Avaliação e treino da recomendação de atividade

- `temas_coger.json`: os 119 temas das pastas de pareceres da COGER e a atividade (modelo) de cada um. Sem dados pessoais.
- `treinar_vocabulario.js`: aprende os termos de cada atividade, mede por validação cruzada e grava `../vocabulario_coger.json`.

```bash
python3 parecer/build.py
node parecer/avaliacao/treinar_vocabulario.js casos.json --gravar
python3 parecer/build.py
```

`casos.json` = `[{"tema": "...", "esperado": "<id da atividade>", "texto": "descritor ou consulta"}]`. Esse arquivo contém nomes de pessoas: **não versionar**.
Para melhorar a precisão, acrescente a ele consultas reais (pergunta 2 do SeCI) com a atividade correta e rode de novo.
