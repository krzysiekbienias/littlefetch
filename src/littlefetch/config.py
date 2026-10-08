from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ApiConfig:
    base_url: str
    api_key_env: str
    timeout_s: float
    stocks_aggs_path: str
    futures_aggs_path: str
    futures_resolution: str
    futures_page_limit: int

    @property
    def api_key(self) -> str:
        key = os.environ.get(self.api_key_env)
        if not key:
            raise RuntimeError(
                f"{self.api_key_env} not set (run with: uv run --env-file .env ...)"
            )
        return key


def load_config(path: str | Path | None = None) -> ApiConfig:
    path = Path(path or os.environ.get("LITTLEFETCH_CONFIG", "config.toml"))
    with path.open("rb") as f:
        raw = tomllib.load(f)
    return ApiConfig(**raw["api"])