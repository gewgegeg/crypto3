from __future__ import annotations

import abc
from typing import AsyncIterator, Dict, Iterable, List, Optional

from pydantic import BaseModel


class PriceStreamEvent(BaseModel):
    type: str  # TICKER or ORDERBOOK
    symbol: str
    exchange: str
    payload: dict


class ExchangeConnector(abc.ABC):
    name: str

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    async def get_symbols(self) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_fees(self) -> Dict:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_price_stream(self, pairs: Iterable[str]) -> AsyncIterator[PriceStreamEvent]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_orderbook(self, pairs: Iterable[str]) -> AsyncIterator[PriceStreamEvent]:
        raise NotImplementedError
