# Fome & Desperdício

Painel público, mobile first, construído exclusivamente com Streamlit. A aplicação
contrapõe indicadores de fome e insegurança alimentar a estimativas de desperdício,
sem apresentar taxas matemáticas como eventos detectados em tempo real.

## O que funciona nesta versão

- contador em toneladas de alimentos desperdiçados desde 00:00, derivado do total anual do UNEP;
- equivalência estimada em refeições e pessoas alimentadas por um dia, com hipóteses visíveis;
- estimativa diária de mortes infantis **associadas** à má nutrição, com ressalva explícita;
- totais globais mais recentes de fome e insegurança alimentar publicados pela FAO;
- consulta por país de população, subnutrição, insegurança alimentar e pobreza;
- desperdício por pessoa e por setor para os países disponíveis;
- gráficos históricos e comparações responsivas em Plotly;
- mapa mundial interativo em Plotly Choropleth, com ISO-3, normalização e detalhes por país;
- produção de carne bovina/búfalo, suína e de aves separada de perda/desperdício;
- cache de 24 horas, timeout HTTP e fallback para a última resposta válida em disco;
- metodologia, ano, fonte, valor original, fórmula e data de consulta visíveis.

Não há Flask, Django, FastAPI, React ou servidor separado. O Streamlit é responsável
pela aplicação inteira.

## Estrutura

```text
.
├── .streamlit/
│   └── config.toml
├── components/
│   ├── __init__.py
│   ├── cards.py
│   ├── charts.py
│   ├── mobile_ui.py
│   └── world_map.py
├── data/
│   ├── snapshots/
│   │   └── official_global_indicators.json
│   ├── __init__.py
│   ├── cache_store.py
│   ├── fao.py
│   ├── http_client.py
│   ├── models.py
│   ├── owid.py
│   ├── unep.py
│   ├── who.py
│   └── world_bank.py
├── services/
│   ├── __init__.py
│   ├── calculations.py
│   ├── counters.py
│   ├── data_service.py
│   └── world_map_data.py
├── tests/
│   └── test_calculations.py
├── utils/
│   ├── __init__.py
│   ├── constants.py
│   └── formatting.py
├── .gitignore
├── app.py
├── pytest.ini
├── README.md
└── requirements.txt
```

## Como executar

Requer Python 3.11 ou mais recente.

No PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

No Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

O navegador normalmente abre em `http://localhost:8501`.

Para rodar os testes de cálculo:

```bash
python -m pip install pytest
pytest -q
```

## Fontes integradas

### UNEP

`data/unep.py` lê um recorte local, auditável e versionado do *Food Waste Index
Report 2024*. O relatório estima 1,052 bilhão de toneladas de desperdício em 2022 nos
setores de varejo, serviços de alimentação e domicílios. A aplicação converte toneladas
para kg e divide por 31.536.000 para obter uma taxa média, sem fazer nova chamada de
rede a cada segundo.

Fonte: <https://www.unep.org/resources/publication/food-waste-index-report-2024>

### FAO / FAOSTAT

`data/fao.py` contém os indicadores globais do SOFI 2026 e um adaptador funcional para
CSV oficial do FAOSTAT. Séries nacionais de subnutrição e insegurança alimentar vêm da
FAO por meio da API do Banco Mundial. A camada `data/owid.py` também consome arquivos
Grapher pequenos cujas fontes originais estão identificadas como FAO/UNEP.

Fonte: <https://www.fao.org/faostat/en/#data>

### OMS

`data/who.py` expõe a estimativa publicada de 2,4 milhões de mortes infantis anuais
associadas à má nutrição materna e infantil (referência epidemiológica de 2021). O texto
da interface evita tratar associação como causalidade individual.

Fonte: <https://www.who.int/news-room/fact-sheets/detail/infant-and-young-child-feeding>

### Banco Mundial

`data/world_bank.py` usa a API v2 documentada para população, pobreza e indicadores da
FAO. A consulta define timeout, filtra o período, conserva apenas ano/valor/país, usa
`@st.cache_data` e salva a última resposta válida em `.cache/`.

Documentação: <https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures>

### Our World in Data

`data/owid.py` consome a API CSV Grapher para desperdício por pessoa, índice de perda e
produção de carne. O adaptador identifica a fonte original e mantém o link direto do
dataset. Os arquivos usados são pequenos e ficam em cache por 24 horas.

Dataset de desperdício: <https://ourworldindata.org/grapher/food-waste-per-capita>

## Como funcionam os contadores

O valor anual oficial é separado da estimativa derivada:

```text
taxa média por segundo = valor anual / 31.536.000
estimativa de hoje = taxa média × segundos decorridos desde 00:00
```

Os resultados principais são exibidos em toneladas. Quilogramas permanecem somente
quando são a unidade mais natural, como nos indicadores por pessoa.

### Equivalência em refeições

O cálculo nutricional reproduz o cenário conservador do UNEP para o desperdício
domiciliar:

```text
parcela potencialmente comestível = desperdício total × 60% domiciliar × 25% comestível
refeições potenciais = parcela comestível em kg / 0,420 kg
pessoas por um dia = refeições potenciais / 3
```

O UNEP usa 420 g por refeição e mostra que a hipótese conservadora de 25% de partes
comestíveis nos domicílios equivale a aproximadamente 376 bilhões de refeições por ano.
Para explicitar a dimensão energética, o painel adota 2.100 kcal por pessoa/dia e três
refeições, resultando em 700 kcal por refeição e densidade implícita de cerca de
1.667 kcal/kg. Essa referência é próxima de rações operacionais do WFP; não é uma
prescrição individual.

Fontes metodológicas:

- UNEP Food Waste Index 2024: <https://www.unep.org/resources/publication/food-waste-index-report-2024>
- FAO/OMS, necessidades energéticas humanas: <https://www.fao.org/4/y5686e/y5686e04.htm>
- Referência operacional de ração do WFP: <https://executiveboard.wfp.org/document_download/WFP-145552>

Alimentos têm diferentes teores de água, energia e nutrientes. A estimativa não considera
segurança sanitária, deterioração, coleta, transporte, preparo ou acesso e não significa
que o volume desperdiçado esteja efetivamente disponível para redistribuição.

`@st.fragment(run_every="1s")` redesenha somente os cards animados. Dados remotos não
são consultados dentro do fragmento. O fuso usado para reiniciar o dia é
`America/Sao_Paulo`.

## Ausências e limitações

- Ausência é mostrada como “Dado não disponível”, nunca como zero.
- Não existe, nesta versão, uma base recente e comparável capaz de sustentar um contador
  global de carne desperdiçada em kg por espécie. A aplicação mostra produção e a taxa
  agregada de perda pré-varejo, mas não multiplica indevidamente uma pela outra.
- Estimativas nacionais de desperdício podem ser extrapoladas pelo UNEP e ter diferentes
  graus de confiança.
- As equivalências em refeições e pessoas são cenários ilustrativos. Necessidades
  energéticas variam por idade, sexo, massa corporal, saúde e atividade física.
- Anos variam entre indicadores; o painel mostra o ano real de cada série.

## Como adicionar um indicador

1. Confirme um endpoint público ou obtenha o CSV/JSON oficial.
2. Crie ou amplie o adaptador em `data/`, sempre retornando `Indicator` ou
   `SeriesResult` de `data/models.py`.
3. Aplique `@st.cache_data`, timeout e tratamento de resposta inválida. Se o arquivo for
   grande, leia somente as colunas necessárias e filtre cedo.
4. Registre fonte, URL, unidade, ano, valor original, fórmula e data da consulta.
5. Faça cálculos derivados em `services/`, nunca escondidos no componente visual.
6. Monte o card em `components/cards.py` e o gráfico em `components/charts.py`.
7. Adicione testes para conversões e para o comportamento de dados ausentes.

Se a fonte não oferecer API estável, use o adaptador `load_official_csv` de `data/fao.py`
como modelo. Não crie endpoints nem preencha lacunas com valores fictícios.
