from __future__ import annotations

from typing import Any

import requests

from utils.constants import REQUEST_TIMEOUT

USER_AGENT = "FomeDesperdicioObservatorio/1.0 (painel educacional; dados publicos)"


def get(url: str, *, params: dict[str, Any] | None = None) -> requests.Response:
    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json,text/csv,*/*"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response

