from __future__ import annotations

from typing import Dict, List, Type

from ..exchanges import REGISTRY, ExchangeConnector


def build_connectors(enabled: List[str]) -> Dict[str, ExchangeConnector]:
    connectors: Dict[str, ExchangeConnector] = {}
    for name in enabled:
        cls = REGISTRY.get(name.upper())
        if not cls:
            continue
        connectors[name.upper()] = cls(name=name.upper())
    return connectors
