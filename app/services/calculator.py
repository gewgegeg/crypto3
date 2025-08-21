from __future__ import annotations

from typing import Dict, List, Optional

from ..core.spreads import calculate_midprice, calculate_raw_spread_percent, apply_fees_to_spread
from ..core.symbols import split_symbol
from ..models import SpreadMetrics, SpreadOpportunity


def compute_spread_for_pair(
    exchanges_prices: Dict[str, float],
    exchange_fees_bps: Dict[str, float],
    symbol: str,
    min_spread_percent: float,
) -> Optional[SpreadOpportunity]:
    items = list(exchanges_prices.items())
    if len(items) < 2:
        return None
    # choose two extremes
    items.sort(key=lambda kv: kv[1])
    ex_a, price_a = items[0]
    ex_b, price_b = items[-1]
    raw = calculate_raw_spread_percent(price_a, price_b)
    if raw is None or raw < min_spread_percent:
        return None
    fee_a = exchange_fees_bps.get(ex_a, 20.0)
    fee_b = exchange_fees_bps.get(ex_b, 20.0)
    net = apply_fees_to_spread(raw, fee_a, fee_b)
    base, quote = split_symbol(symbol)
    metrics = SpreadMetrics(
        raw_spread_percent=raw,
        net_spread_percent=net,
        midprice_a=None,
        midprice_b=None,
    )
    return SpreadOpportunity(
        base=base,
        quote=quote,
        symbol=symbol,
        exchange_a=ex_a,
        exchange_b=ex_b,
        price_a=price_a,
        price_b=price_b,
        metrics=metrics,
    )
