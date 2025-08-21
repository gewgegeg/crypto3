from __future__ import annotations

import asyncio
import random
import time
from typing import AsyncIterator, Dict, Iterable, List

from .base import ExchangeConnector, PriceStreamEvent
from ..core.symbols import normalize_symbol


class MockExchangeConnector(ExchangeConnector):
    def __init__(self, name: str = "MOCK"):
        super().__init__(name)
        self._symbols = [
            "BTC-USDT",
            "ETH-USDT",
            "SOL-USDT",
            "XRP-USDT",
        ]

    async def get_symbols(self) -> List[str]:
        await asyncio.sleep(0.01)
        return self._symbols

    async def get_fees(self) -> Dict:
        await asyncio.sleep(0.01)
        return {
            "maker_bps": 10.0,
            "taker_bps": 20.0,
            "withdraw_fee": {"BTC": 0.0005, "ETH": 0.003, "USDT": 1.0},
        }

    async def get_price_stream(self, pairs: Iterable[str]) -> AsyncIterator[PriceStreamEvent]:
        follow = [normalize_symbol(p) for p in pairs]
        while True:
            for sym in follow:
                price = self._price_for(sym)
                payload = {
                    "price": price,
                    "volume_24h": random.uniform(1000000, 50000000),
                    "ts": time.time(),
                }
                yield PriceStreamEvent(type="TICKER", symbol=sym, exchange=self.name, payload=payload)
            await asyncio.sleep(0.5)

    async def get_orderbook(self, pairs: Iterable[str]) -> AsyncIterator[PriceStreamEvent]:
        follow = [normalize_symbol(p) for p in pairs]
        while True:
            for sym in follow:
                mid = self._price_for(sym)
                bids = [[round(mid * (1 - i * 0.0005), 2), random.uniform(0.1, 5.0)] for i in range(1, 11)]
                asks = [[round(mid * (1 + i * 0.0005), 2), random.uniform(0.1, 5.0)] for i in range(1, 11)]
                payload = {"bids": bids, "asks": asks, "ts": time.time()}
                yield PriceStreamEvent(type="ORDERBOOK", symbol=sym, exchange=self.name, payload=payload)
            await asyncio.sleep(1.0)

    def _price_for(self, symbol: str) -> float:
        base = symbol.split("-")[0]
        anchor = {
            "BTC": 65000.0,
            "ETH": 3200.0,
            "SOL": 140.0,
            "XRP": 0.55,
        }.get(base, 10.0)
        # Random walk
        return round(anchor * (1 + random.uniform(-0.005, 0.005)), 2)
