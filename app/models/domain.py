from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, Field


class ExchangeInfo(BaseModel):
    name: str
    online: bool = False
    latency_ms: Optional[float] = None
    status: Literal["online", "degraded", "offline"] = "offline"


class ExchangeFee(BaseModel):
    exchange: str
    maker_bps: float = 10.0
    taker_bps: float = 20.0
    withdraw_fee: Dict[str, float] = Field(default_factory=dict)


class RiskNote(BaseModel):
    id: str
    severity: Literal["info", "warning", "critical"] = "info"
    note: str
    exchange: Optional[str] = None
    symbol: Optional[str] = None


class Ticker(BaseModel):
    exchange: str
    symbol: str
    price: float
    volume_24h: Optional[float] = None
    ts: Optional[float] = None


class OrderBookLevel(BaseModel):
    price: float
    size: float


class OrderBookSnapshot(BaseModel):
    exchange: str
    symbol: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    ts: Optional[float] = None


class SpreadMetrics(BaseModel):
    raw_spread_percent: float
    net_spread_percent: Optional[float] = None
    liquidity_adjusted_percent: Optional[float] = None
    midprice_a: Optional[float] = None
    midprice_b: Optional[float] = None


class SpreadOpportunity(BaseModel):
    base: str
    quote: str
    symbol: str
    exchange_a: str
    exchange_b: str
    price_a: float
    price_b: float
    metrics: SpreadMetrics

