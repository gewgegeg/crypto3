from app.core.symbols import normalize_symbol


def test_normalize_symbol_inserts_dash():
    assert normalize_symbol("BTCUSDT") == "BTC-USDT"
    assert normalize_symbol("eth_usdt").upper() == "ETH-USDT"
