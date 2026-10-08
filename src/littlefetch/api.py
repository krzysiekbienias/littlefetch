from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .config import ApiConfig


class ApiError(Exception): ...
class AuthError(ApiError): ...
class NotFound(ApiError): ...
class ServerError(ApiError): ...


class RateLimited(ApiError):
    def __init__(self, url: str, retry_after: float | None) -> None:
        super().__init__(f"429 for {url}, retry after {retry_after}")
        self.retry_after = retry_after


@dataclass(frozen=True)
class Request:
    url: str
    params: dict[str, str] = field(default_factory=dict)


def auth_headers(cfg: ApiConfig) -> dict[str, str]:
    try:
        key = cfg.api_key
    except RuntimeError as e:
        raise AuthError(str(e)) from None
    return {"Authorization": f"Bearer {key}"}


def stock_daily_aggs(cfg: ApiConfig, ticker: str, start: str, end: str) -> Request:
    path = cfg.stocks_aggs_path.format(ticker=ticker, start=start, end=end)
    return Request(cfg.base_url + path, {"adjusted": "true", "sort": "asc", "limit": "50000"})


def futures_daily_aggs(cfg: ApiConfig, contract: str, start: str, end: str) -> Request:
    path = cfg.futures_aggs_path.format(contract=contract)
    return Request(
        cfg.base_url + path,
        {
            "resolution": cfg.futures_resolution,
            "window_start.gte": start,
            "window_start.lte": end,
            "limit": str(cfg.futures_page_limit),
        },
    )


def check_status(status: int, headers: Mapping[str, str], url: str) -> None:
    if status == 200:
        return
    if status in (401, 403):
        raise AuthError(f"{status} for {url}: bad key or endpoint outside plan")
    if status == 404:
        raise NotFound(f"404 for {url}")
    if status == 429:
        ra = headers.get("Retry-After")
        raise RateLimited(url, float(ra) if ra else None)
    if status >= 500:
        raise ServerError(f"{status} for {url}")
    raise ApiError(f"unexpected {status} for {url}")


def parse_page(body: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    return body.get("results") or [], body.get("next_url")