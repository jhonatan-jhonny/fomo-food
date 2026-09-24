from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from components.cards import (
    availability_notice,
    calculation_details,
    info_card,
    metric_card,
    source_status,
)
from components.charts import grouped_bar, horizontal_bar, line_chart, multi_line_chart
from components.mobile_ui import hero, inject_styles, section_intro
from components.world_map import render_world_map, render_world_map_summary
from data.fao import (
    global_food_insecurity,
    global_healthy_diet_unaffordable,
    global_undernourishment,
)
from data.models import Indicator
from data.owid import fetch_grapher
from data.unep import environmental_facts, global_food_waste
from data.who import (
    child_nutrition_indicators,
    malnutrition_associated_deaths,
    protein_energy_malnutrition_deaths,
)
from data.world_bank import fetch_indicator
from services.calculations import estimate_feeding_potential, kg_to_tonnes
from services.counters import counter_values
from services.data_service import country_dashboard, production_by_category
from utils.constants import (
    APP_TIMEZONE,
    APP_TITLE,
    CONSERVATIVE_EDIBLE_SHARE,
    COUNTRIES,
    FAO_ENERGY_REQUIREMENTS_URL,
    FAO_SOFI_2026_URL,
    HOUSEHOLD_WASTE_SHARE,
    REFERENCE_DAILY_KCAL,
    REFERENCE_MEAL_KG,
    REFERENCE_MEALS_PER_DAY,
    UNEP_REPORT_URL,
    WFP_RATION_REFERENCE_URL,
    WHO_GHE_URL,
    WHO_JME_URL,
    WHO_NUTRITION_URL,
    WORLD_BANK_INDICATORS,
)
from utils.formatting import (
    format_compact_br,
    format_number_br,
    format_value,
)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_styles()

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


@st.fragment(run_every="1s")
def live_mortality_counter(deaths: Indicator) -> None:
    """Anima uma taxa estatística; nenhuma API é chamada neste fragmento."""
    mortality = counter_values(float(deaths.value or 0))
    metric_card(
        "Estimativa acumulada hoje",
        format_number_br(mortality["today"], 0),
        "mortes por desnutrição proteico-energética · todas as idades",
        (
            f"Estimativa matemática baseada no total anual da OMS ({deaths.year}). "
            "Não representa mortes detectadas neste instante."
        ),
        "primary",
    )


@st.fragment(run_every="1s")
def live_food_waste_counters(food_waste: Indicator) -> None:
    """Atualiza somente taxas derivadas do total anual do UNEP."""
    food = counter_values(float(food_waste.value or 0))
    nutrition = estimate_feeding_potential(
        food["today"],
        HOUSEHOLD_WASTE_SHARE,
        CONSERVATIVE_EDIBLE_SHARE,
        REFERENCE_MEAL_KG,
        REFERENCE_DAILY_KCAL,
        REFERENCE_MEALS_PER_DAY,
    )

    metric_card(
        "Alimentos desperdiçados hoje",
        format_number_br(kg_to_tonnes(food["today"]), 0),
        "toneladas · estimativa acumulada",
        (
            "Estimativa em tempo real baseada no último dado oficial disponível: "
            f"total anual do UNEP ({food_waste.year}). Não é medição ao vivo."
        ),
        "primary",
    )
    metric_card(
        "Desperdício por segundo",
        format_number_br(kg_to_tonnes(food["per_second"]), 2),
        "toneladas/s · taxa média",
        "O fluxo real não é uniforme ao longo do dia.",
    )
    metric_card(
        "Equivalência alimentar do cenário documentado",
        format_compact_br(nutrition["meals"]),
        "refeições potenciais",
        (
            f"Ou cerca de {format_compact_br(nutrition['person_days'])} pessoas por 1 dia. "
            "Usa somente 25% da parcela domiciliar, conforme cenário conservador do UNEP; "
            "não converte todo o desperdício."
        ),
        "positive",
    )


def render_home() -> None:
    hero()
    food_waste = global_food_waste()
    pem_deaths = protein_energy_malnutrition_deaths()
    child_deaths = malnutrition_associated_deaths()
    child_indicators = child_nutrition_indicators()
    hunger = global_undernourishment()
    food_insecurity = global_food_insecurity()
    healthy_diet = global_healthy_diet_unaffordable()

    live_food_waste_counters(food_waste)
    render_world_map_summary()

    section_intro(
        "Fome no mundo",
        "Três medidas diferentes da privação alimentar",
        "Cada indicador responde a uma pergunta distinta e mantém seu próprio ano de referência.",
    )
    metric_card(
        "Pessoas subnutridas no mundo",
        format_compact_br(hunger.value),
        f"pessoas · {hunger.year} · FAO / SOFI 2026",
        "Estimativa central de subnutrição crônica; a FAO usa este indicador para medir a fome.",
        "primary",
    )
    metric_card(
        "Insegurança alimentar moderada ou grave",
        format_compact_br(food_insecurity.value),
        f"pessoas · {food_insecurity.year} · FAO / SOFI 2026",
        "Mede dificuldade regular de acesso a alimentos adequados; não equivale à subnutrição crônica.",
    )
    metric_card(
        "Sem condições de pagar uma dieta saudável",
        format_compact_br(healthy_diet.value),
        f"pessoas · {healthy_diet.year} · FAO / SOFI 2026",
        "Acessibilidade considera preços, renda e despesas não alimentares essenciais.",
    )
    metric_card(
        "Mortes por desnutrição proteico-energética",
        format_number_br(pem_deaths.value, 0),
        f"mortes/ano · todas as idades · {pem_deaths.year}",
        (
            f"OMS Global Health Estimates. Média matemática: "
            f"{format_number_br(float(pem_deaths.value or 0) / 365, 0)} por dia; "
            "não inclui todas as mortes em que a má nutrição apenas contribuiu para o risco."
        ),
    )

    st.markdown(
        '<div class="source-strip"><strong>Estimativa em tempo real baseada no último dado '
        "oficial disponível.</strong> O contador abaixo distribui estatisticamente o total anual; "
        "não detecta eventos individuais.</div>",
        unsafe_allow_html=True,
    )
    live_mortality_counter(pem_deaths)
    calculation_details(pem_deaths, "Como este contador é calculado?")

    section_intro(
        "Crianças e fome",
        "Indicadores infantis, sem misturar faixas etárias",
        "Os valores abaixo descrevem crianças e não alimentam o contador de todas as idades.",
    )
    for indicator in child_indicators:
        suffix = "crianças" if indicator.unit == "crianças" else indicator.unit
        metric_card(
            indicator.label,
            format_compact_br(indicator.value)
            if indicator.unit == "crianças"
            else format_number_br(indicator.value, 1),
            f"{suffix} · {indicator.year} · {indicator.source}",
            indicator.note,
            "primary" if indicator.key == "child_severe_wasting" else "",
        )
    metric_card(
        "Mortes de crianças associadas à má nutrição materna e infantil",
        format_compact_br(child_deaths.value),
        f"mortes/ano · {child_deaths.year} · OMS",
        (
            "Indicador amplo de associação epidemiológica. Não significa que a má nutrição "
            "tenha sido registrada como causa direta em cada morte. A ficha da OMS usa "
            "“child deaths” sem detalhar uma faixa etária mais específica para esse total."
        ),
    )
    metric_card(
        "Mortes infantis diretamente atribuídas à desnutrição aguda grave",
        "Dado não disponível",
        "total global comparável",
        (
            "Não foi localizado um total mundial oficial que meça exclusivamente essa causa "
            "direta com metodologia comparável. Ausência de dado não significa zero."
        ),
    )
    info_card(
        "A fome nem sempre aparece como causa direta da morte.",
        (
            "A desnutrição enfraquece o organismo e aumenta o risco de morte por doenças como "
            "diarreia, pneumonia e outras infecções. Por isso, existem diferenças entre mortes "
            "diretamente causadas pela desnutrição e mortes em que a desnutrição contribuiu para o risco."
        ),
    )

    section_intro(
        "Desperdício de alimentos",
        "Peso, origem e limites da equivalência alimentar",
        "Os valores principais são exibidos em toneladas; indicadores por habitante permanecem em kg.",
    )
    metric_card(
        "Alimentos desperdiçados por ano",
        format_number_br(kg_to_tonnes(float(food_waste.value or 0)), 0),
        f"toneladas/ano · {food_waste.year} · UNEP",
        "Varejo, serviços de alimentação e domicílios; inclui partes comestíveis e não comestíveis.",
        "primary",
    )
    metric_card(
        "Desperdício por habitante",
        "132",
        "kg/pessoa/ano · 2022 · UNEP",
        "Média global dos três setores medidos pelo Food Waste Index 2024.",
    )
    metric_card("Origem: residências", "60%", "do total global · 2022 · UNEP")
    metric_card(
        "Origem: serviços de alimentação", "28%", "do total global · 2022 · UNEP"
    )
    metric_card("Origem: varejo", "12%", "do total global · 2022 · UNEP")
    info_card(
        "Nem tudo que entra nas estatísticas de desperdício poderia ser servido em um prato.",
        (
            "As estatísticas de desperdício alimentar podem incluir partes não comestíveis, como "
            "ossos, cascas, caroços e outras partes descartadas dos alimentos. Por isso, uma tonelada "
            "de desperdício não significa necessariamente uma tonelada de comida que poderia alimentar pessoas."
        ),
        "caution",
    )
    with st.expander("Entenda melhor"):
        st.markdown(
            """
- O desperdício pode incluir partes comestíveis e não comestíveis.
- Países podem usar metodologias e níveis de cobertura diferentes.
- Peso desperdiçado não pode ser convertido diretamente em refeições sem conhecer a composição dos alimentos.
- Uma estimativa de refeições deve usar somente a parcela comestível quando houver base confiável.

Por isso, o FOMO não transforma automaticamente todo o total global em refeições. A equivalência exibida no início aparece apenas porque o relatório do UNEP publica um cenário conservador específico para a parcela domiciliar.
            """
        )
    calculation_details(food_waste, "Como este contador é calculado?")
    with st.expander("Como a equivalência alimentar foi estimada?"):
        st.markdown(
            f"""
**Cenário ilustrativo e conservador — não é uma promessa de distribuição.**

1. O [UNEP Food Waste Index 2024]({UNEP_REPORT_URL}) atribui **60%** do desperdício global aos domicílios.
2. O relatório aplica, em seu cenário conservador, **25% de partes comestíveis** somente ao desperdício domiciliar e usa **420 g por refeição**.
3. O painel usa **2.100 kcal por pessoa/dia** e **3 refeições por dia** como referência operacional aproximada.

**Fórmula:** desperdício total × 60% domiciliar × 25% comestível ÷ 0,420 kg = refeições potenciais.

**Pessoas por 1 dia:** refeições potenciais ÷ 3.

A referência é próxima de rações operacionais de [2.100 kcal/dia do WFP]({WFP_RATION_REFERENCE_URL}). A [FAO/OMS ressalta]({FAO_ENERGY_REQUIREMENTS_URL}) que necessidades variam por idade, sexo, massa corporal e atividade. A estimativa não considera segurança sanitária, deterioração, coleta, conservação, transporte, preparo ou acesso e não afirma que esse volume esteja recuperável.
            """
        )

    environment = environmental_facts()
    section_intro(
        "O que esses números significam?",
        "Medidas relacionadas, mas não intercambiáveis",
        "A leitura responsável exige observar definição, população, ano e método de cada número.",
    )
    info_card(
        "Subnutrição, insegurança alimentar e dieta saudável medem coisas diferentes.",
        (
            "Uma pessoa pode enfrentar dificuldade de acesso a alimentos sem cumprir o critério de "
            "subnutrição crônica. Também pode consumir calorias suficientes e ainda não conseguir pagar "
            "uma dieta variada e nutricionalmente adequada."
        ),
    )
    info_card(
        "Contadores animados são estimativas, não sensores.",
        (
            "Eles dividem um total anual pelo número de segundos do ano e mostram o acumulado médio "
            "desde 00:00. Nenhuma morte ou descarte individual é detectado pelo site."
        ),
    )
    section_intro("Impacto climático", "O desperdício também aquece o planeta")
    metric_card(
        "Perda e desperdício de alimentos",
        environment["value"],
        environment["unit"],
        environment["note"],
    )

    section_intro(
        "Fontes e metodologia",
        "Cada card pode ser auditado",
        "Os períodos diferem porque as organizações atualizam cada indicador em calendários próprios.",
    )
    calculation_details(hunger, "Subnutrição: fonte e método")
    calculation_details(food_insecurity, "Insegurança alimentar: fonte e método")
    calculation_details(healthy_diet, "Dieta saudável: fonte e método")
    for indicator in child_indicators:
        calculation_details(indicator, f"{indicator.label}: fonte e método")
    calculation_details(child_deaths, "Mortalidade infantil associada: fonte e limite")
    now = datetime.now(ZoneInfo(APP_TIMEZONE)).strftime("%d/%m/%Y %H:%M")
    source_status("FAO, IFAD, UNICEF, WFP e OMS — SOFI", "2025 (relatório 2026)", now)
    source_status("UNICEF / OMS / Banco Mundial — JME", "2024 (edição 2025)", now)
    source_status("OMS — Global Health Estimates", "2021 (publicado em 2024)", now)
    source_status("UNEP — Food Waste Index", "2022 (relatório 2024)", now)
    with st.expander("Abrir fontes oficiais"):
        st.markdown(
            f"""
- [FAO — SOFI 2026]({FAO_SOFI_2026_URL})
- [OMS — Global Health Estimates]({WHO_GHE_URL})
- [UNICEF / OMS / Banco Mundial — Joint Child Malnutrition Estimates]({WHO_JME_URL})
- [OMS — Infant and young child feeding]({WHO_NUTRITION_URL})
- [UNEP — Food Waste Index Report 2024]({UNEP_REPORT_URL})
            """
        )


def _render_indicator(indicator: Indicator, compact: bool = True) -> None:
    if not indicator.available:
        metric_card(indicator.label, "Dado não disponível", note=indicator.note)
        return
    metric_card(
        indicator.label,
        format_value(indicator.value, indicator.unit, compact),
        f"último período: {indicator.year}",
        indicator.note,
    )
    calculation_details(indicator)


def render_world() -> None:
    section_intro(
        "Mundo",
        "Veja um país",
        "Cada card informa seu próprio ano. Ausência de dados nunca é convertida em zero.",
    )
    country_name = st.selectbox("Escolha o país", list(COUNTRIES), index=0)
    code = COUNTRIES[country_name]
    with st.spinner("Consultando fontes públicas e cache local…"):
        dashboard = country_dashboard(code)

    population = dashboard["population"]
    undernourishment = dashboard["undernourishment"]
    food_insecurity = dashboard["food_insecurity"]
    poverty = dashboard["poverty"]
    waste = dashboard["food_waste"]
    waste_total = dashboard["food_waste_total"]
    assert isinstance(population, Indicator)
    assert isinstance(undernourishment, Indicator)
    assert isinstance(food_insecurity, Indicator)
    assert isinstance(poverty, Indicator)
    assert isinstance(waste, Indicator)
    assert isinstance(waste_total, Indicator)

    st.subheader(country_name)
    _render_indicator(population)
    _render_indicator(undernourishment, compact=False)
    if dashboard["undernourished_people"] is not None:
        metric_card(
            "Pessoas subnutridas — valor derivado",
            format_compact_br(dashboard["undernourished_people"]),
            f"estimativa usando população do mesmo ano ({undernourishment.year})",
            "Percentual de subnutrição × população; a incerteza do indicador original permanece.",
        )
    _render_indicator(food_insecurity, compact=False)
    _render_indicator(waste_total)
    _render_indicator(waste, compact=False)
    _render_indicator(poverty, compact=False)

    metric_card(
        "Mortalidade associada à desnutrição",
        "Dado não disponível",
        note="Não foi localizada série nacional comparável nesta primeira versão. Ausência não significa zero.",
    )

    series = dashboard["series"]
    under_series = series["undernourishment"]
    if under_series.available:
        st.plotly_chart(
            line_chart(
                under_series.data,
                f"Subnutrição em {country_name}",
                "% da população",
            ),
            width="stretch",
            config=PLOT_CONFIG,
        )
    else:
        availability_notice()

    waste_series = dashboard["waste_series"]
    if isinstance(waste_series, pd.DataFrame) and not waste_series.empty:
        sectors = [
            item
            for item in ("Retail", "Out-of-home consumption", "Household")
            if item in waste_series.columns
        ]
        translated = {
            "Retail": "Varejo",
            "Out-of-home consumption": "Fora do lar",
            "Household": "Domicílios",
        }
        melted = waste_series.melt(
            id_vars="year", value_vars=sectors, var_name="sector", value_name="value"
        )
        melted["sector"] = melted["sector"].map(translated)
        st.plotly_chart(
            grouped_bar(
                melted,
                "year",
                "value",
                "sector",
                "Desperdício por setor",
                "kg por pessoa/ano",
            ),
            width="stretch",
            config=PLOT_CONFIG,
        )

    errors = [result.error for result in series.values() if result.error]
    if errors:
        st.warning(
            "Uma ou mais fontes estão temporariamente indisponíveis; quando possível, foi usado o último cache válido."
        )


def render_meat() -> None:
    section_intro(
        "Carne",
        "Produção não é desperdício",
        "Esta seção mantém as duas medidas separadas para não fabricar precisão.",
    )
    metric_card(
        "Perda pré-varejo: carne e produtos animais",
        "14,0%",
        "taxa global economicamente ponderada · 2023",
        "A FAO usa peso econômico para agregar commodities. Aplicar 14% diretamente às toneladas produzidas seria metodologicamente incorreto.",
    )
    metric_card(
        "Carne desperdiçada em kg",
        "Dado não disponível",
        "bovina · suína · aves · outras",
        "Sem uma série recente, global e comparável por categoria cobrindo perdas e consumo final, o painel não cria um contador.",
    )
    with st.expander("Fonte e limite metodológico"):
        st.markdown(
            "Fonte da taxa: [FAO — Food Loss Index](https://www.fao.org/statistics/"
            "highlights-archive/highlights-detail/on-the-international-day-of-awareness-of-food-loss-and-waste--learn-how-fao-is-leveraging-data-to-save-food-and-advance-the-2030-agenda/). "
            "O índice cobre perdas da pós-colheita até antes do varejo; não mede o desperdício doméstico."
        )

    country_name = st.selectbox(
        "Produção por país", list(COUNTRIES), index=0, key="meat_country"
    )
    frame, errors = production_by_category(COUNTRIES[country_name])
    if frame.empty:
        availability_notice("Fonte de produção temporariamente indisponível.")
    else:
        recent = frame[
            frame["year"] >= max(frame["year"].max() - 20, frame["year"].min())
        ]
        st.plotly_chart(
            multi_line_chart(
                recent,
                f"Produção de carne — {country_name}",
                "toneladas",
                "category",
            ),
            width="stretch",
            config=PLOT_CONFIG,
        )
        st.caption(
            "Fonte: FAOSTAT, processado por Our World in Data. O gráfico mostra produção, não perda ou desperdício."
        )
    if errors:
        st.warning("Parte das séries está temporariamente indisponível.")


def _food_waste_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    result = fetch_grapher("food_waste")
    frame = result.data
    if frame.empty:
        return frame, frame, frame
    sectors = [
        column
        for column in ("Retail", "Out-of-home consumption", "Household")
        if column in frame.columns
    ]
    data = frame.copy()
    data["value"] = data[sectors].sum(axis=1)

    codes = set(COUNTRIES.values())
    countries = data[(data["code"].isin(codes)) & (data["year"] == data["year"].max())][
        ["entity", "value"]
    ]
    region_names = [
        "Africa (UN)",
        "Asia (UN)",
        "Europe (UN)",
        "Latin America and the Caribbean (UN)",
        "Northern America (UN)",
        "Oceania (UN)",
    ]
    regions = data[
        (data["entity"].isin(region_names)) & (data["year"] == data["year"].max())
    ][["entity", "value"]]
    world = data[data["entity"] == "World"]
    return countries, regions, world


def render_charts() -> None:
    section_intro(
        "Gráficos",
        "Uma pergunta por vez",
        "No celular, escolha o gráfico para manter leitura e desempenho confortáveis.",
    )
    chart_name = st.selectbox(
        "Visualização",
        [
            "Evolução da subnutrição",
            "Evolução da insegurança alimentar",
            "Evolução do desperdício",
            "Desperdício por região",
            "Comparação entre países",
            "Produção de carne",
        ],
    )

    if chart_name in {"Evolução da subnutrição", "Evolução da insegurança alimentar"}:
        key = "undernourishment" if "subnutrição" in chart_name else "food_insecurity"
        definition = WORLD_BANK_INDICATORS[key]
        result = fetch_indicator("WLD", definition["code"])
        if result.available:
            st.plotly_chart(
                line_chart(result.data, chart_name, "% da população"),
                width="stretch",
                config=PLOT_CONFIG,
            )
            st.caption(
                f"Fonte: {result.source}. Último ano disponível: {int(result.data.year.max())}."
            )
        else:
            availability_notice("Fonte temporariamente indisponível.")
        return

    countries, regions, world = _food_waste_frames()
    if chart_name == "Evolução do desperdício":
        if world.empty:
            availability_notice("Fonte temporariamente indisponível.")
        else:
            st.plotly_chart(
                line_chart(world[["year", "value"]], chart_name, "kg por pessoa/ano"),
                width="stretch",
                config=PLOT_CONFIG,
            )
            st.caption(
                "A série comparável possui dois pontos (2019 e 2022); não há interpolação."
            )
    elif chart_name == "Desperdício por região":
        if regions.empty:
            availability_notice("Dado regional temporariamente indisponível.")
        else:
            st.plotly_chart(
                horizontal_bar(regions, chart_name, "kg por pessoa/ano"),
                width="stretch",
                config=PLOT_CONFIG,
            )
    elif chart_name == "Comparação entre países":
        if countries.empty:
            availability_notice("Dados de comparação temporariamente indisponíveis.")
        else:
            st.plotly_chart(
                horizontal_bar(countries, chart_name, "kg por pessoa/ano"),
                width="stretch",
                config=PLOT_CONFIG,
            )
            st.caption(
                "A comparação é descritiva. Não implica causalidade com fome ou mortalidade."
            )
    elif chart_name == "Produção de carne":
        frame, _ = production_by_category("WLD")
        if frame.empty:
            availability_notice("Dados de produção temporariamente indisponíveis.")
        else:
            recent = frame[frame["year"] >= frame["year"].max() - 20]
            st.plotly_chart(
                multi_line_chart(recent, chart_name, "toneladas", "category"),
                width="stretch",
                config=PLOT_CONFIG,
            )
            st.caption("Produção não é sinônimo de perda ou desperdício.")


def render_methodology() -> None:
    section_intro("Transparência", "Metodologia")
    st.markdown(
        """
Organismos internacionais não registram fome, mortalidade ou desperdício alimento por
alimento e pessoa por pessoa em tempo real. Os números animados deste painel são
**estimativas matemáticas**, não sensores de eventos.

Para um total anual `V`, a taxa média é `V ÷ 31.536.000`. O acumulado exibido é essa
taxa multiplicada pelos segundos decorridos desde 00:00 no fuso de São Paulo. Eventos
reais não acontecem uniformemente durante o dia e o contador volta a zero à meia-noite.

“Mortes por desnutrição proteico-energética” é uma estimativa de causa básica do Global
Health Estimates da OMS, para todas as idades. Já “associada à má nutrição” descreve uma
associação epidemiológica infantil mais ampla. Nenhuma das duas medidas significa que uma
morte individual tenha sido observada naquele segundo. Do mesmo modo, apresentar fome e
desperdício lado a lado evidencia uma contradição social, mas **não estabelece causalidade**
entre as duas medidas.

A equivalência em refeições usa somente um cenário conservador para a fração domiciliar
potencialmente comestível. Ela expressa uma ordem de grandeza energética, não a quantidade
que poderia ser coletada e entregue com segurança. Necessidades calóricas e a composição
dos alimentos variam entre pessoas, lugares e períodos.
        """
    )

    st.subheader("Separação entre dados e estimativas")
    st.markdown(
        """
- Dados oficiais mantêm a unidade, o ano e a fonte originais.
- Conversões e taxas aparecem no expander “Como este número foi calculado?”.
- Valores ausentes aparecem como “Dado não disponível”, nunca como zero.
- Respostas de rede ficam em cache por 24 horas. Se uma atualização falhar, o app tenta
  usar a última resposta válida salva localmente e avisa o usuário.
- O fragmento que anima os contadores roda a cada segundo, mas não consulta APIs.
        """
    )

    st.subheader("Fontes e última atualização")
    now = datetime.now(ZoneInfo(APP_TIMEZONE))
    source_status(
        "UNEP — Food Waste Index",
        "2022 (relatório 2024)",
        now.strftime("%d/%m/%Y %H:%M"),
    )
    source_status("FAO — SOFI", "2025 (relatório 2026)", now.strftime("%d/%m/%Y %H:%M"))
    source_status(
        "OMS — Global Health Estimates",
        "2021 (publicado em 2024)",
        now.strftime("%d/%m/%Y %H:%M"),
    )
    source_status(
        "UNICEF / OMS / Banco Mundial — JME",
        "2024 (edição 2025)",
        now.strftime("%d/%m/%Y %H:%M"),
    )
    source_status(
        "Banco Mundial / FAO — séries nacionais",
        "varia por indicador",
        now.strftime("%d/%m/%Y %H:%M"),
    )
    source_status(
        "Our World in Data / FAO / UNEP",
        "varia por série",
        now.strftime("%d/%m/%Y %H:%M"),
    )

    with st.expander("Links das fontes"):
        st.markdown(
            f"""
- [UNEP — Food Waste Index Report 2024]({UNEP_REPORT_URL})
- [FAO — SOFI 2026]({FAO_SOFI_2026_URL})
- [FAO — FAOSTAT](https://www.fao.org/faostat/en/#data)
- [OMS — Global Health Estimates]({WHO_GHE_URL})
- [UNICEF / OMS / Banco Mundial — Joint Child Malnutrition Estimates]({WHO_JME_URL})
- [OMS — alimentação de lactentes e crianças]({WHO_NUTRITION_URL})
- [Banco Mundial — documentação da API](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures)
- [Our World in Data — Food waste per capita](https://ourworldindata.org/grapher/food-waste-per-capita)
            """
        )


def main() -> None:
    pages = ["Início", "Mapa mundial", "Mundo", "Carne", "Gráficos", "Metodologia"]
    page = st.selectbox("Navegação", pages, label_visibility="collapsed")
    if page == "Início":
        render_home()
    elif page == "Mapa mundial":
        render_world_map()
    elif page == "Mundo":
        render_world()
    elif page == "Carne":
        render_meat()
    elif page == "Gráficos":
        render_charts()
    else:
        render_methodology()


if __name__ == "__main__":
    main()
