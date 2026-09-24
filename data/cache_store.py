from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from utils.constants import RUNTIME_CACHE_DIR


def _path(namespace: str, key: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
    return RUNTIME_CACHE_DIR / f"{namespace}-{digest}.json"


def save_json(namespace: str, key: str, payload: Any) -> None:
    """Guarda a última resposta válida para uso durante indisponibilidade da fonte."""
    try:
        RUNTIME_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        target = _path(namespace, key)
        temporary = target.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
        os.replace(temporary, target)
    except OSError:
        # Cache em disco é uma proteção adicional; falhar ao gravá-lo não derruba o app.
        return


def load_json(namespace: str, key: str) -> Any | None:
    try:
        return json.loads(_path(namespace, key).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

