from __future__ import annotations

from pathlib import Path

APP_TITLE = "Fome & Desperdício"
APP_TIMEZONE = "America/Sao_Paulo"
SECONDS_PER_YEAR = 365 * 24 * 60 * 60
REQUEST_TIMEOUT = 15
CACHE_TTL_SECONDS = 24 * 60 * 60

ROOT_DIR = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT_DIR / "data" / "snapshots"
RUNTIME_CACHE_DIR = ROOT_DIR / ".cache"

COUNTRIES = {
    "Brasil": "BRA",
    "Estados Unidos": "USA",
    "Índia": "IND",
    "China": "CHN",
    "Nigéria": "NGA",
    "África do Sul": "ZAF",
    "México": "MEX",
    "Argentina": "ARG",
    "França": "FRA",
    "Japão": "JPN",
}

WORLD_BANK_INDICATORS = {
    "population": {
        "code": "SP.POP.TOTL",
        "label": "População",
        "unit": "pessoas",
        "provider": "Banco Mundial",
    },
    "undernourishment": {
        "code": "SN.ITK.DEFC.ZS",
        "label": "Prevalência de subnutrição",
        "unit": "%",
        "provider": "FAO via Banco Mundial",
    },
    "food_insecurity": {
        "code": "SN.ITK.MSFI.ZS",
        "label": "Insegurança alimentar moderada ou grave",
        "unit": "%",
        "provider": "FAO via Banco Mundial",
    },
    "poverty": {
        "code": "SI.POV.DDAY",
        "label": "Pobreza na linha internacional",
        "unit": "%",
        "provider": "Banco Mundial",
    },
}

WORLD_BANK_API = "https://api.worldbank.org/v2"
WORLD_BANK_DOCS = (
    "https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures"
)

OWID_DATASETS = {
    "food_waste": "food-waste-per-capita",
    "meat_production": "meat-production-tonnes",
    "beef_production": "beef-and-buffalo-meat-production-tonnes",
    "pork_production": "pigmeat-production-tonnes",
    "poultry_production": "poultry-production-tonnes",
    "food_loss_index": "global-food-loss-index",
}
OWID_GRAPHS = "https://ourworldindata.org/grapher"

UNEP_REPORT_URL = (
    "https://www.unep.org/resources/publication/food-waste-index-report-2024"
)
FAO_SOFI_2026_URL = (
    "https://www.fao.org/director-general/speeches/details/launch-of-the-state-of-food-"
    "security-and-nutrition-in-the-world-%28sofi%29-2026-report-statement/"
)
WHO_NUTRITION_URL = (
    "https://www.who.int/news-room/fact-sheets/detail/infant-and-young-child-feeding"
)
