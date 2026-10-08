from __future__ import annotations

from typing import Any

import requests

from .api import Request, check_status, parse_page


def fetch_all(session: requests.Session, req: Request, timeout: float = 20.0) -> list[dict[str, Any]]:
    bars: list[dict[str, Any]] = []
    url: str | None = req.url
    params: dict[str, str] | None = req.params
    while url:
        resp = session.get(url, params=params, timeout=timeout)
        check_status(resp.status_code, resp.headers, resp.url)
        page, url = parse_page(resp.json())
        bars.extend(page)
        params = None  # next_url niesie już całe query
    return bars