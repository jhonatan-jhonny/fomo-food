from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from components.cards import (
    availability_notice,
    calculation_details,
    metric_card,
    source_status,
)
from components.charts import grouped_bar, horizontal_bar, line_chart, multi_line_chart
from components.mobile_ui import hero, inject_styles, section_intro
from components.world_map import render_world_map
from data.fao import global_food_insecurity, global_undernourishment
from data.models import Indicator
from data.owid import fetch_grapher
from data.unep import environmental_facts, global_food_waste
from data.who import malnutrition_associated_deaths
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
    HOUSEHOLD_WASTE_SHARE,
    REFERENCE_DAILY_KCAL,
    REFERENCE_MEAL_KG,
    REFERENCE_MEALS_PER_DAY,
    UNEP_REPORT_URL,
    WFP_RATION_REFERENCE_URL,
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
def live_global_counters(food_waste: Indicator, deaths: Indicator) -> None:
    """Atualiza só os contadores; nenhuma API é chamada neste fragmento."""
    food = counter_values(float(food_waste.value or 0))
    mortality = counter_values(float(deaths.value or 0))
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
        "toneladas · estimativa",
        f"Taxa média derivada do total anual do UNEP ({food_waste.year}).",
        "primary",
    )
    metric_card(
        "Equivalência alimentar estimada",
        format_compact_br(nutrition["meals"]),
        "refeições potenciais",
        (
            f"Ou cerca de {format_compact_br(nutrition['person_days'])} pessoas por 1 dia. "
            "Cenário conservador para a parcela domiciliar comestível; não representa alimento efetivamente recuperável."
        ),
        "positive",
    )
    metric_card(
        "Mortes infantis associadas à má nutrição hoje",
        format_number_br(mortality["today"], 0),
        "estimativa estatística",
        "Não representa mortes detectadas neste instante e não atribui causalidade individual.",
    )
    metric_card(
        "Desperdício por segundo",
        format_number_br(kg_to_tonnes(food["per_second"]), 2),
        "toneladas/s · taxa média",
        "O fluxo real não é uniforme ao longo do dia.",
    )


def render_home() -> None:
    hero()
    food_waste = global_food_waste()
    deaths = malnutrition_associated_deaths()
    hunger = global_undernourishment()
    food_insecurity = global_food_insecurity()

    st.markdown(
        '<div class="source-strip"><strong>Estimativa em tempo real</strong> calculada '
        "a partir dos dados oficiais mais recentes disponíveis. Não é uma medição ao vivo "
        "de eventos individuais.</div>",
        unsafe_allow_html=True,
    )
    live_global_counters(food_waste, deaths)

    metric_card(
        "Pessoas em situação de fome / subnutrição",
        format_compact_br(hunger.value),
        f"estimativa global · {hunger.year}",
        "Indicador de subnutrição crônica publicado pela FAO.",
    )
    metric_card(
        "Insegurança alimentar moderada ou grave",
        format_compact_br(food_insecurity.value),
        f"pessoas · {food_insecurity.year}",
        "É um indicador distinto da subnutrição crônica.",
    )
    metric_card(
        "Desperdício por pessoa",
        "132",
        "kg/pessoa/ano · 2022",
        "Média global nos setores de varejo, serviços de alimentação e domicílios.",
    )

    environment = environmental_facts()
    section_intro("Impacto", "O desperdício também aquece o planeta")
    metric_card(
        "Perda e desperdício de alimentos",
        environment["value"],
        environment["unit"],
        environment["note"],
    )

    calculation_details(food_waste, "Como o contador de alimentos foi calculado?")
    with st.expander("Como a equivalência em refeições foi estimada?"):
        st.markdown(
            f"""
**Cenário ilustrativo e conservador — não é uma promessa de distribuição.**

1. O [UNEP Food Waste Index 2024]({UNEP_REPORT_URL}) estima que os domicílios
   respondem por **60%** do desperdício global.
2. O mesmo relatório aplica, como limite conservador, **25% de partes comestíveis**
   ao desperdício domiciliar e usa **420 g por refeição**.
3. Para expressar a massa também em energia, adotamos **2.100 kcal por pessoa/dia**
   como referência operacional aproximada e **3 refeições por dia**. Isso equivale a
   700 kcal por refeição e a uma densidade implícita de aproximadamente
   **1.667 kcal/kg**.

**Fórmula:** desperdício total × 60% × 25% ÷ 0,420 kg = refeições potenciais.

**Pessoas por 1 dia:** refeições potenciais ÷ 3.

A referência energética é próxima de rações operacionais de aproximadamente
[2.100 kcal/dia do WFP]({WFP_RATION_REFERENCE_URL}). A
[FAO/OMS ressalta]({FAO_ENERGY_REQUIREMENTS_URL}) que necessidades energéticas variam
por idade, sexo, massa corporal e atividade. Alimentos também variam muito em água,
densidade calórica, qualidade nutricional e segurança. O cálculo não considera coleta,
conservação, transporte, preparo ou acesso e **não pressupõe que todo desperdício possa
ser reaproveitado**.
            """
        )
    calculation_details(deaths, "Como a estimativa de mortalidade foi calculada?")
    calculation_details(hunger, "Fonte do indicador de fome")


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
        st.warning("Uma ou mais fontes estão temporariamente indisponíveis; quando possível, foi usado o último cache válido.")


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

    country_name = st.selectbox("Produção por país", list(COUNTRIES), index=0, key="meat_country")
    frame, errors = production_by_category(COUNTRIES[country_name])
    if frame.empty:
        availability_notice("Fonte de produção temporariamente indisponível.")
    else:
        recent = frame[frame["year"] >= max(frame["year"].max() - 20, frame["year"].min())]
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
    regions = data[(data["entity"].isin(region_names)) & (data["year"] == data["year"].max())][
        ["entity", "value"]
    ]
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
            st.caption(f"Fonte: {result.source}. Último ano disponível: {int(result.data.year.max())}.")
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
            st.caption("A série comparável possui dois pontos (2019 e 2022); não há interpolação.")
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
            st.caption("A comparação é descritiva. Não implica causalidade com fome ou mortalidade.")
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

“Associada à má nutrição” descreve uma associação epidemiológica publicada pela OMS.
Não significa que uma morte individual tenha sido observada ou atribuída naquele segundo.
Do mesmo modo, apresentar fome e desperdício lado a lado evidencia uma contradição social,
mas **não estabelece causalidade** entre as duas medidas.

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
    source_status("UNEP — Food Waste Index", "2022 (relatório 2024)", now.strftime("%d/%m/%Y %H:%M"))
    source_status("FAO — SOFI", "2025 (relatório 2026)", now.strftime("%d/%m/%Y %H:%M"))
    source_status("OMS — má nutrição e mortalidade infantil", "2021", now.strftime("%d/%m/%Y %H:%M"))
    source_status("Banco Mundial / FAO — séries nacionais", "varia por indicador", now.strftime("%d/%m/%Y %H:%M"))
    source_status("Our World in Data / FAO / UNEP", "varia por série", now.strftime("%d/%m/%Y %H:%M"))

    with st.expander("Links das fontes"):
        st.markdown(
            f"""
- [UNEP — Food Waste Index Report 2024]({UNEP_REPORT_URL})
- [FAO — FAOSTAT](https://www.fao.org/faostat/en/#data)
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
