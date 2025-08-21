from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..models import ExchangeInfo, ExchangeFee, Ticker, OrderBookSnapshot, SpreadOpportunity


class InMemoryStore(BaseModel):
    exchanges: Dict[str, ExchangeInfo] = {}
    fees: Dict[str, ExchangeFee] = {}
    symbols: Dict[str, List[str]] = {}
    tickers: Dict[str, Dict[str, Ticker]] = defaultdict(dict)
    orderbooks: Dict[str, Dict[str, OrderBookSnapshot]] = defaultdict(dict)
    spreads: List[SpreadOpportunity] = []

    class Config:
        arbitrary_types_allowed = True


store = InMemoryStore()
store_lock = asyncio.Lock()
