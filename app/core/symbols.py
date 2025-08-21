from __future__ import annotations

import re


def normalize_symbol(symbol: str) -> str:
    if symbol is None:
        return symbol
    s = symbol.strip().upper()
    s = s.replace("_", "-")
    if "-" not in s:
        # Insert dash between base and quote if missing (common: BTCUSDT)
        match = re.match(r"^([A-Z0-9]+?)(USD[T|C]?|USDC|USDT|BTC|ETH|BNB|EUR|USD|TRY|BUSD|FDUSD|DAI|TUSD|PAX|USTC)$", s)
        if match:
            base, quote = match.group(1), match.group(2)
            s = f"{base}-{quote}"
    return s


def split_symbol(symbol: str) -> tuple[str, str]:
    norm = normalize_symbol(symbol)
    base, quote = norm.split("-")
    return base, quote
