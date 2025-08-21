from __future__ import annotations

import asyncio
import time
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import ORJSONResponse, PlainTextResponse
from prometheus_client import CollectorRegistry, Gauge, generate_latest

from ..config import settings
from ..models import ExchangeInfo, SpreadOpportunity
from ..services.state import store, store_lock


router = APIRouter(default_response_class=ORJSONResponse)


@router.get("/exchanges", response_model=List[ExchangeInfo])
async def get_exchanges() -> List[ExchangeInfo]:
    return list(store.exchanges.values())


@router.get("/pairs")
async def get_pairs(exchange: str) -> List[str]:
    ex = exchange.upper()
    return store.symbols.get(ex, [])


@router.get("/spreads")
async def get_spreads(
    base: Optional[str] = None,
    quote: Optional[str] = None,
    min_spread: float = Query(default=settings.min_spread_percent),
    exA: Optional[str] = None,
    exB: Optional[str] = None,
) -> List[SpreadOpportunity]:
    opportunities = [s for s in store.spreads if s.metrics.raw_spread_percent >= min_spread]
    if base:
        opportunities = [s for s in opportunities if s.base == base.upper()]
    if quote:
        opportunities = [s for s in opportunities if s.quote == quote.upper()]
    if exA:
        opportunities = [s for s in opportunities if s.exchange_a == exA.upper()]
    if exB:
        opportunities = [s for s in opportunities if s.exchange_b == exB.upper()]
    return opportunities


@router.get("/opportunities")
async def get_top_opportunities(limit: int = 20) -> List[SpreadOpportunity]:
    return sorted(store.spreads, key=lambda s: s.metrics.net_spread_percent or s.metrics.raw_spread_percent, reverse=True)[:limit]


@router.get("/stats")
async def get_stats() -> Dict:
    return {
        "exchanges_online": sum(1 for e in store.exchanges.values() if e.online),
        "symbols_tracked": sum(len(v) for v in store.symbols.values()),
        "spreads_count": len(store.spreads),
        "timestamp": time.time(),
    }


@router.get("/health", response_class=PlainTextResponse)
async def health() -> str:
    return "ok"


@router.get("/metrics")
async def metrics() -> ORJSONResponse:
    registry = CollectorRegistry()
    g_exchanges = Gauge("exchanges_online", "Number of online exchanges", registry=registry)
    g_spreads = Gauge("spreads_count", "Number of spread entries", registry=registry)
    g_exchanges.set(sum(1 for e in store.exchanges.values() if e.online))
    g_spreads.set(len(store.spreads))
    return ORJSONResponse(generate_latest(registry))


@router.websocket("/ws/stream")
async def ws_stream(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = {"type": "HEARTBEAT", "ts": time.time()}
            await ws.send_json(data)
            await asyncio.sleep(settings.websocket_heartbeat_sec)
    except WebSocketDisconnect:
        return
