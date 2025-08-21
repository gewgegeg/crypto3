from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .config import settings
from .exchanges import REGISTRY
from .services.registry import build_connectors
from .services.state import store, store_lock
from .models import ExchangeInfo, ExchangeFee


log = logging.getLogger("app")


def create_app() -> FastAPI:
    app = FastAPI(title="Crypto Spread Scanner", version="0.1.0")
    app.include_router(api_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        # Initialize exchange connectors
        connectors = build_connectors(settings.enabled_exchanges)
        async with store_lock:
            for name in connectors.keys():
                store.exchanges[name] = ExchangeInfo(name=name, online=True, status="online")
        # Load symbols and fees for mock
        await _bootstrap_data(connectors)
        # Start background computations
        app.state.bg_tasks = [
            asyncio.create_task(_recompute_spreads_periodically()),
        ]

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        with contextlib.suppress(Exception):
            for task in getattr(app.state, "bg_tasks", []):
                task.cancel()

    return app


async def _bootstrap_data(connectors: Dict[str, object]) -> None:
    for name, conn in connectors.items():
        try:
            symbols = await conn.get_symbols()
            fees = await conn.get_fees()
            async with store_lock:
                store.symbols[name] = symbols
                store.fees[name] = ExchangeFee(exchange=name, **fees)
        except Exception as e:
            log.exception("Failed to bootstrap %s: %s", name, e)


async def _recompute_spreads_periodically() -> None:
    from .services.calculator import compute_spread_for_pair
    while True:
        try:
            entries = []
            fees_bps = {ex: (store.fees.get(ex).taker_bps if store.fees.get(ex) else 20.0) for ex in store.symbols.keys()}
            # For demo, simulate latest tickers using mid of mock orderbooks or prices list
            for symbol in sorted(set(sum(store.symbols.values(), []))):
                # synthesize prices per exchange
                ex_prices = {}
                for ex in store.symbols.keys():
                    # Use a simple random-ish price to produce differences
                    import random
                    base = 1.0 + (hash((ex, symbol)) % 100) / 1000.0
                    ex_prices[ex] = base * (100.0 + (hash(symbol) % 100))
                opp = compute_spread_for_pair(ex_prices, fees_bps, symbol, settings.min_spread_percent)
                if opp:
                    entries.append(opp)
            async with store_lock:
                store.spreads = entries
        except Exception:
            log.exception("Failed to recompute spreads")
        await asyncio.sleep(2.0)


app = create_app()
