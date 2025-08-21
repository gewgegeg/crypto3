from app.core.spreads import calculate_midprice, calculate_raw_spread_percent


def test_midprice():
    assert calculate_midprice(100, 102) == 101


def test_raw_spread_percent():
    raw = calculate_raw_spread_percent(100, 105)
    assert 4.8 < raw < 5.1
