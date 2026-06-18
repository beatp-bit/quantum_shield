"""
Market Regime Detection
Determines if we are in BULL, BEAR, SIDEWAYS, or CHAOS
Now with liquidation data integration
"""

def detect_regime(token_data: dict, sentiment_score: int, liquidation_score: int = 0) -> dict:
    """
    Detect market regime based on:
    - 7d and 24h momentum
    - Sentiment score
    - Volume conviction
    - Liquidation pressure (NEW)
    """
    p7d = token_data.get("percent_change_7d", 0)
    p24h = token_data.get("percent_change_24h", 0)
    vol_change = token_data.get("volume_change_24h", 0)
    
    # Base regime logic
    base_regime = "TRANSITION"
    base_confidence = 40
    base_strategy = "WAIT — Regime changing, reduce position size"
    base_reason = "Mixed signals, no strong conviction either way"
    
    # --- BEAR conditions (structural damage) ---
    if p7d < -20 or (p7d < -10 and liquidation_score < -40):
        base_regime = "BEAR"
        base_confidence = min(90, int(abs(p7d) * 1.5) + abs(liquidation_score) // 2)
        base_strategy = "SHORT BIAS — Sell rallies, avoid catching falling knives"
        base_reason = f"Weekly loss of {p7d:.1f}%" + (f" + massive long liquidations" if liquidation_score < -40 else "")
    
    # --- BULL conditions (strong uptrend) ---
    elif p7d > 20:
        base_regime = "BULL"
        base_confidence = min(90, int(p7d * 1.5))
        base_strategy = "LONG BIAS — Buy dips, ride momentum"
        base_reason = f"Weekly gain of {p7d:.1f}% confirms uptrend"
    
    # --- SIDEWAYS (no clear trend) ---
    elif abs(p7d) < 10 and abs(p24h) < 5 and abs(liquidation_score) < 20:
        base_regime = "SIDEWAYS"
        base_confidence = 60
        base_strategy = "RANGE TRADE — Buy support, sell resistance"
        base_reason = "Price consolidating with no clear direction"
    
    # --- CHAOS (high volatility, conflicting signals) ---
    elif vol_change > 50 and abs(p24h) > 8:
        base_regime = "CHAOS"
        base_confidence = 50
        base_strategy = "STAY OUT — Unpredictable, high risk of whipsaws"
        base_reason = "Extreme volume with violent price moves"
    
    # Adjust confidence and strategy based on liquidation score
    if liquidation_score < -50:
        base_confidence = min(95, base_confidence + 15)
        base_strategy = "AGGRESSIVE SHORT — Liquidation cascade in progress"
    
    return {
        "regime": base_regime,
        "regime_short": "🔴 BEAR" if base_regime == "BEAR" else 
                        ("🟢 BULL" if base_regime == "BULL" else
                         ("🟡 SIDEWAYS" if base_regime == "SIDEWAYS" else
                          ("🟠 CHAOS" if base_regime == "CHAOS" else "⚪ TRANSITION"))),
        "confidence": base_confidence,
        "strategy": base_strategy,
        "reason": base_reason,
        "metrics": {
            "p7d": p7d,
            "p24h": p24h,
            "vol_change": vol_change,
            "liquidation_score": liquidation_score
        }
    }