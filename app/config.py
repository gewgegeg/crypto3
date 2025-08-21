from __future__ import annotations

import os
from typing import List, Optional

import yaml
from pydantic import BaseModel


class Settings(BaseModel):
    environment: str = os.environ.get("ENV", "dev")
    enabled_exchanges: List[str] = ["MOCK"]
    min_spread_percent: float = 0.5
    liquidity_usd: float = 1000.0
    websocket_heartbeat_sec: float = 10.0
    reconnect_base_delay_sec: float = 1.0
    reconnect_max_delay_sec: float = 30.0
    rest_poll_interval_sec: float = 2.0
    allow_vwap: bool = True

    @staticmethod
    def load(config_path: Optional[str] = None) -> "Settings":
        data = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        return Settings(**data)


settings = Settings.load(os.environ.get("APP_CONFIG"))
