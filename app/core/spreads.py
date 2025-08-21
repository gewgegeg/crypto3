from __future__ import annotations

from typing import Iterable, List, Tuple


def calculate_midprice(best_bid: float, best_ask: float) -> float:
    if best_bid is None or best_ask is None:
        return None
    return (best_bid + best_ask) / 2.0


def calculate_vwap(levels: Iterable[Tuple[float, float]], notional_in_quote: float) -> float:
    remaining_quote = notional_in_quote
    total_base_filled = 0.0
    total_cost_quote = 0.0
    for price, size in levels:
        if remaining_quote <= 0:
            break
        available_quote_at_level = price * size
        take_quote = min(available_quote_at_level, remaining_quote)
        base_taken = take_quote / price
        total_base_filled += base_taken
        total_cost_quote += take_quote
        remaining_quote -= take_quote
    if remaining_quote > 0 or total_base_filled == 0:
        return None
    return total_cost_quote / total_base_filled


def calculate_raw_spread_percent(price_a: float, price_b: float) -> float:
    if price_a is None or price_b is None:
        return None
    if price_a <= 0 or price_b <= 0:
        return None
    # percentage difference relative to mid of two prices
    mid = (price_a + price_b) / 2.0
    return (abs(price_a - price_b) / mid) * 100.0


def apply_fees_to_spread(raw_spread_percent: float, taker_bps_a: float, taker_bps_b: float) -> float:
    if raw_spread_percent is None:
        return None
    # Convert bps to percent and subtract both sides taker fees
    total_fee_percent = (taker_bps_a + taker_bps_b) / 100.0
    return raw_spread_percent - total_fee_percent
