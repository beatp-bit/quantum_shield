from indicators.rsi_cmc import get_rsi_for_timeframes

def get_rsi_values(symbol: str = "BTC") -> dict:
    # Recupera RSI daily (CMC supporta solo daily)
    rsi_data = get_rsi_for_timeframes(symbol.upper(), timeframes=['1d'], period=14)
    rsi_daily = rsi_data.get('1d', 50)
    
    # Per 1h,4h,1w usiamo valori neutri (50) poiché CMC non li fornisce
    def zone(val):
        if val >= 70: return "OVERBOUGHT"
        if val <= 30: return "OVERSOLD"
        if val <= 40: return "WEAK"
        if val >= 60: return "STRONG"
        return "NEUTRAL"
    
    total_score = 0
    reasons = []
    if rsi_daily < 30:
        total_score -= 15
        reasons.append(f"Daily RSI oversold ({rsi_daily})")
    elif rsi_daily < 40:
        total_score -= 5
        reasons.append(f"Daily RSI weak ({rsi_daily})")
    elif rsi_daily > 70:
        total_score += 15
        reasons.append(f"Daily RSI overbought ({rsi_daily})")
    
    return {
        "rsi_1h": 50.0,
        "rsi_4h": 50.0,
        "rsi_daily": rsi_daily,
        "rsi_weekly": 50.0,
        "zone_1h": "NEUTRAL",
        "zone_4h": "NEUTRAL",
        "zone_daily": zone(rsi_daily),
        "zone_weekly": "NEUTRAL",
        "signal": {
            "score": total_score,
            "action": "HOLD" if abs(total_score) < 10 else ("SHORT" if total_score < 0 else "LONG"),
            "signal": "HOLD",
            "reasons": reasons
        }
    }