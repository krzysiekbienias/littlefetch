import requests

from .api import auth_headers, futures_daily_aggs, stock_daily_aggs
from .config import load_config
from .sync_client import fetch_all


def main() -> None:
    cfg = load_config()
    with requests.Session() as s:
        s.headers.update(auth_headers(cfg))

        fut = fetch_all(s, futures_daily_aggs(cfg, "CLZ6", "2026-01-01", "2026-10-07"), cfg.timeout_s)
        print(f"CLZ6: {len(fut)} bars, first: {fut[0] if fut else None}")

        stk = fetch_all(s, stock_daily_aggs(cfg, "AAPL", "2024-10-08", "2026-10-07"), cfg.timeout_s)
        print(f"AAPL: {len(stk)} bars, first: {stk[0] if stk else None}")


if __name__ == "__main__":
    main()