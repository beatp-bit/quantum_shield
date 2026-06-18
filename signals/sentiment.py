"""
Sentiment Analysis Module
Converts raw CMC data into a sentiment score from -100 (extreme fear) to +100 (extreme greed)
"""

def analyze_sentiment(token_data: dict, global_data: dict) -> dict:
    """
    Calculate sentiment score based on:
    - Price momentum (1h, 24h, 7d)
    - Volume action
    - Market cap change
    - BTC dominance (risk-off indicator)
    """
    score = 0
    signals = []
    
    # --- 1. Price Momentum (max 40 points) ---
    p1h = token_data.get("percent_change_1h", 0)
    p24h = token_data.get("percent_change_24h", 0)
    p7d = token_data.get("percent_change_7d", 0)
    
    # 24h momentum (most important for short-term sentiment)
    if p24h > 10:
        score += 30
        signals.append(f"🟢 Strong 24h pump: +{p24h:.1f}% — Greed building")
    elif p24h > 5:
        score += 20
        signals.append(f"🟢 Good 24h gain: +{p24h:.1f}% — Positive sentiment")
    elif p24h > 2:
        score += 10
        signals.append(f"🟡 Mild gain: +{p24h:.1f}% — Cautious optimism")
    elif p24h < -10:
        score -= 30
        signals.append(f"🔴 Crash: {p24h:.1f}% in 24h — Panic selling")
    elif p24h < -5:
        score -= 20
        signals.append(f"🔴 Strong drop: {p24h:.1f}% — Fear dominating")
    elif p24h < -2:
        score -= 10
        signals.append(f"🟠 Slight drop: {p24h:.1f}% — Mild fear")
    else:
        signals.append(f"⚡ Flat 24h: {p24h:+.1f}% — Neutral")
    
    # 1h momentum (short-term impulse)
    if p1h > 3:
        score += 10
        signals.append(f"🟢 1h impulse: +{p1h:.1f}% — Short-term buying pressure")
    elif p1h < -3:
        score -= 10
        signals.append(f"🔴 1h dump: {p1h:.1f}% — Immediate selling")
    
    # 7d trend (structural damage assessment)
    if p7d < -30:
        score -= 25
        signals.append(f"💀 Brutal week: {p7d:.1f}% in 7d — Structural damage")
    elif p7d < -15:
        score -= 15
        signals.append(f"⚠️ Bad week: {p7d:.1f}% — Bearish structure")
    elif p7d > 20:
        score += 15
        signals.append(f"📈 Amazing week: +{p7d:.1f}% — Bullish structure")
    
    # --- 2. Volume Action (max 20 points) ---
    vol_change = token_data.get("volume_change_24h", 0)
    
    if vol_change > 50 and p24h > 0:
        score += 15
        signals.append(f"🟢 Volume exploding +{vol_change:.0f}% with green candle — Real buying")
    elif vol_change > 30 and p24h > 0:
        score += 10
        signals.append(f"🟡 Volume up +{vol_change:.0f}% — Interest increasing")
    elif vol_change > 50 and p24h < 0:
        score -= 15
        signals.append(f"🔴 Volume spike +{vol_change:.0f}% on red candle — Panic selling")
    elif vol_change < -30:
        score -= 5
        signals.append(f"⚪ Volume drying up {vol_change:.0f}% — Low conviction")
    
    # --- 3. Market Context (max 20 points) ---
    mcap_change = global_data.get("market_cap_change_24h", 0)
    btc_dom = global_data.get("btc_dominance", 50)
    
    if mcap_change > 2:
        score += 10
        signals.append(f"🟢 Total market cap growing +{mcap_change:.1f}% — Tide rising")
    elif mcap_change < -2:
        score -= 10
        signals.append(f"🔴 Total market cap shrinking {mcap_change:.1f}% — Tide falling")
    
    # BTC dominance: high = risk-off (bad for alts), low = risk-on (good for alts)
    if btc_dom > 60:
        score -= 10
        signals.append(f"⚠️ BTC dominance high ({btc_dom:.1f}%) — Capital flowing to safety, alts suffer")
    elif btc_dom < 45:
        score += 10
        signals.append(f"🟢 BTC dominance low ({btc_dom:.1f}%) — Altseason potential")
    
    # --- Clamp and label ---
    score = max(-100, min(100, score))
    
    if score >= 70:
        label = "EXTREME GREED 🤑"
    elif score >= 40:
        label = "GREED 😏"
    elif score >= 15:
        label = "MILD GREED 🙂"
    elif score > -15:
        label = "NEUTRAL 😐"
    elif score > -40:
        label = "MILD FEAR 😟"
    elif score > -70:
        label = "FEAR 😨"
    else:
        label = "EXTREME FEAR 😱"
    
    return {
        "score": score,
        "label": label,
        "signals": signals
    }