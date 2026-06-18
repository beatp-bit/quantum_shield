import math

def calculate_atr(token_data: dict, period: int = 14) -> float:
    p24h = abs(token_data.get('percent_change_24h', 0))
    price = token_data.get('price', 0)
    if p24h > 10:
        return price * 0.08
    elif p24h > 5:
        return price * 0.05
    else:
        return price * 0.03

def dynamic_stop_loss(price: float, atr: float, direction: str, multiplier: float = 1.5) -> float:
    if direction == "SHORT":
        return round(price + (atr * multiplier), 2)
    else:
        return round(price - (atr * multiplier), 2)

def position_sizing(capital: float, confidence: int, risk_per_trade: float = 0.02) -> float:
    if confidence >= 70:
        risk_multiplier = 1.0
    elif confidence >= 50:
        risk_multiplier = 0.5
    else:
        risk_multiplier = 0.25
    risk_amount = capital * risk_per_trade * risk_multiplier
    return round(risk_amount, 2)