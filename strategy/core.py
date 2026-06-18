"""
Decision Engine Core
Combines all signals into a single actionable verdict.
"""

def combine_signals(
    token_symbol: str,
    regime: dict,
    sentiment: dict,
    liquidation_signal: dict,
    rsi_signal: dict,
    price_data: dict
) -> dict:
    """
    Weighted combination of all signals.
    Weights (CMC-only version):
    - Regime: 40%
    - Sentiment: 35%
    - RSI: 25%
    """
    
    # --- Extract scores ---
    regime_score = _regime_to_score(regime)
    sentiment_score = sentiment.get('score', 0)
    rsi_score = rsi_signal.get('score', 0)
    
    # --- Apply weights ---
    total_score = (
        regime_score * 0.40 +
        sentiment_score * 0.35 +
        rsi_score * 0.25
    )
    
    # Clamp to -100 / +100
    total_score = max(-100, min(100, total_score))
    
    # --- Determine signal ---
    if total_score <= -60:
        signal = "SELL / SHORT 🔴"
        action = "SHORT"
        intensity = "AGGRESSIVE"
        confidence = min(95, int(abs(total_score) * 1.2))
    elif total_score <= -30:
        signal = "SELL / SHORT 🟠"
        action = "SHORT"
        intensity = "MODERATE"
        confidence = min(85, int(abs(total_score) * 1.1))
    elif total_score <= -10:
        signal = "CAUTIOUS SHORT 🟡"
        action = "CAUTIOUS_SHORT"
        intensity = "LIGHT"
        confidence = min(70, int(abs(total_score) * 1.0))
    elif total_score >= 60:
        signal = "BUY / LONG 🔵"
        action = "LONG"
        intensity = "AGGRESSIVE"
        confidence = min(95, int(total_score * 1.2))
    elif total_score >= 30:
        signal = "BUY / LONG 🟢"
        action = "LONG"
        intensity = "MODERATE"
        confidence = min(85, int(total_score * 1.1))
    elif total_score >= 10:
        signal = "CAUTIOUS LONG 🟡"
        action = "CAUTIOUS_LONG"
        intensity = "LIGHT"
        confidence = min(70, int(total_score * 1.0))
    else:
        signal = "HOLD / WAIT ⚪"
        action = "HOLD"
        intensity = "NONE"
        confidence = 50
    
    # --- Generate reasoning ---
    reasons = _generate_reasons(
        regime_score, sentiment_score, rsi_score,
        regime, sentiment, rsi_signal
    )
    
    # --- Suggested levels ---
    current_price = price_data.get('price', 0)
    levels = {}
    
    if action in ["SHORT", "CAUTIOUS_SHORT"]:
        levels = {
            "entry": current_price,
            "stop_loss": round(current_price * 1.05, 2),
            "take_profit_1": round(current_price * 0.95, 2),
            "take_profit_2": round(current_price * 0.88, 2),
            "take_profit_3": round(current_price * 0.80, 2),
        }
    elif action in ["LONG", "CAUTIOUS_LONG"]:
        levels = {
            "entry": current_price,
            "stop_loss": round(current_price * 0.95, 2),
            "take_profit_1": round(current_price * 1.05, 2),
            "take_profit_2": round(current_price * 1.12, 2),
            "take_profit_3": round(current_price * 1.20, 2),
        }
    
    return {
        "signal": signal,
        "action": action,
        "intensity": intensity,
        "confidence": confidence,
        "total_score": total_score,
        "components": {
            "regime": regime_score,
            "sentiment": sentiment_score,
            "rsi": rsi_score
        },
        "reasons": reasons,
        "levels": levels
    }


def _regime_to_score(regime: dict) -> int:
    """Convert regime to a directional score (-100 to +100)."""
    regime_name = regime.get('regime', 'TRANSITION')
    confidence = regime.get('confidence', 50)
    
    if regime_name == "BEAR":
        return -int(60 + (confidence * 0.3))
    elif regime_name == "BULL":
        return int(60 + (confidence * 0.3))
    elif regime_name == "CHAOS":
        return 0
    elif regime_name == "SIDEWAYS":
        return 0
    else:
        return -20  # TRANSITION = slight bear bias


def _generate_reasons(regime_score, sentiment_score, rsi_score,
                      regime, sentiment, rsi_signal) -> list:
    """Generate human-readable reasons for the decision."""
    reasons = []
    
    if regime_score < -40:
        reasons.append(f"Regime: {regime.get('regime', '?')} ({regime.get('confidence', 0)}% confidence)")
    elif regime_score < -20:
        reasons.append(f"Regime: {regime.get('regime', '?')} — bearish bias")
    
    if sentiment_score < -40:
        reasons.append(f"Sentiment: {sentiment.get('label', '?')} ({sentiment_score:+d}) — fear dominating")
    elif sentiment_score < -20:
        reasons.append(f"Sentiment: {sentiment.get('label', '?')} — mild fear")
    elif sentiment_score > 40:
        reasons.append(f"Sentiment: {sentiment.get('label', '?')} ({sentiment_score:+d}) — greed")
    
    if rsi_score < -10:
        reasons.append(f"RSI: bearish alignment (score {rsi_score:+d})")
    elif rsi_score > 10:
        reasons.append(f"RSI: bullish alignment (score {rsi_score:+d})")
    
    if not reasons:
        reasons.append("Mixed signals — no strong conviction")
    
    return reasons