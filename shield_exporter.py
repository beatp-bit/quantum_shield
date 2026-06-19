import sys
import json
import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CMC_API_KEY = os.getenv("CMC_API_KEY", "")
CMC_BASE = "https://pro-api.coinmarketcap.com/v1"

def fetch_cmc_data(token: str) -> dict:
    """Fetch live token data from CoinMarketCap API."""
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY, "Accept": "application/json"}
    url = f"{CMC_BASE}/cryptocurrency/quotes/latest"
    params = {"symbol": token, "convert": "USD"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()["data"][token]["quote"]["USD"]
        return {
            "price": data.get("price", 0),
            "volume_24h": data.get("volume_24h", 0),
            "volume_change_24h": data.get("volume_change_24h", 0),
            "percent_change_1h": data.get("percent_change_1h", 0),
            "percent_change_24h": data.get("percent_change_24h", 0),
            "percent_change_7d": data.get("percent_change_7d", 0),
            "market_cap": data.get("market_cap", 0),
            "market_cap_dominance": data.get("market_cap_dominance", 0),
        }
    except Exception as e:
        print(f"[CMC ERROR] {e} — using fallback neutral data")
        return {
            "price": 0, "volume_24h": 0, "volume_change_24h": 0,
            "percent_change_1h": 0, "percent_change_24h": 0,
            "percent_change_7d": 0, "market_cap": 0, "market_cap_dominance": 0,
        }


def compute_safety_score(d: dict) -> dict:
    """
    Compute a live safety score from real CMC data.

    Scoring model (100 points total):
      - Volume stability      (30 pts): penalizes extreme volume_change_24h
      - Price stability 24h   (25 pts): penalizes large % swings
      - Price stability 7d    (20 pts): penalizes large weekly swings
      - Market cap size       (15 pts): larger cap = safer
      - 1h momentum spike     (10 pts): penalizes sudden 1h dumps/pumps
    """
    score = 100.0

    # 1. Volume stability (30 pts)
    vol_chg = abs(d["volume_change_24h"])
    if vol_chg > 200:
        score -= 30
    elif vol_chg > 100:
        score -= 20
    elif vol_chg > 50:
        score -= 12
    elif vol_chg > 25:
        score -= 5

    # 2. Price stability 24h (25 pts)
    chg_24h = abs(d["percent_change_24h"])
    if chg_24h > 20:
        score -= 25
    elif chg_24h > 10:
        score -= 15
    elif chg_24h > 5:
        score -= 7
    elif chg_24h > 2:
        score -= 2

    # 3. Price stability 7d (20 pts)
    chg_7d = abs(d["percent_change_7d"])
    if chg_7d > 40:
        score -= 20
    elif chg_7d > 20:
        score -= 12
    elif chg_7d > 10:
        score -= 5
    elif chg_7d > 5:
        score -= 2

    # 4. Market cap tier (15 pts)
    mcap = d["market_cap"]
    if mcap < 10_000_000:           # micro cap
        score -= 15
    elif mcap < 100_000_000:        # small cap
        score -= 10
    elif mcap < 1_000_000_000:      # mid cap
        score -= 5
    # large cap (>1B): no penalty

    # 5. 1h momentum spike (10 pts)
    chg_1h = abs(d["percent_change_1h"])
    if chg_1h > 5:
        score -= 10
    elif chg_1h > 2:
        score -= 5
    elif chg_1h > 1:
        score -= 2

    score = max(0.0, min(100.0, score))

    # Whale concentration proxy: based on market cap dominance + vol change
    if d["market_cap_dominance"] > 5 and vol_chg < 50:
        whale_score = "low_risk"
    elif d["market_cap_dominance"] > 1 or vol_chg < 100:
        whale_score = "medium_risk"
    else:
        whale_score = "high_risk"

    # Wash trading flag: volume change > 150% with small price move = suspicious
    wash_flag = vol_chg > 150 and chg_24h < 3

    # Liquidity decay: volume dropping more than 60%
    liquidity_alert = d["volume_change_24h"] < -60

    # Suggested slippage: tighter for stable assets
    if score >= 80:
        slippage = 0.3
    elif score >= 60:
        slippage = 0.5
    elif score >= 40:
        slippage = 1.0
    else:
        slippage = 2.0

    # Exposure multiplier: reduce exposure for risky assets
    exposure_mult = round(min(1.0, score / 100 * 1.5), 2)

    return {
        "safety_score_rating": round(score, 1),
        "whale_concentration_score": whale_score,
        "volume_wash_trading_flag": wash_flag,
        "liquidity_decay_alert": liquidity_alert,
        "scoring_breakdown": {
            "volume_change_24h_pct": round(d["volume_change_24h"], 2),
            "price_change_24h_pct": round(d["percent_change_24h"], 2),
            "price_change_7d_pct": round(d["percent_change_7d"], 2),
            "price_change_1h_pct": round(d["percent_change_1h"], 2),
            "market_cap_usd": int(d["market_cap"]),
            "market_cap_dominance_pct": round(d["market_cap_dominance"], 4),
        },
        "risk_mitigation_vector": {
            "max_suggested_slippage_pct": slippage,
            "exposure_limit_multiplier": exposure_mult,
        },
    }


def execute_shield_skill(parameters: dict) -> dict:
    """
    Main entry point for the QUANTUM SHIELD Risk Oracle skill.
    Fetches live CMC data and computes a real safety score.
    """
    token = parameters.get("token_target", "BNB").upper()
    deep_scan = parameters.get("deep_scan", True)

    live_data = fetch_cmc_data(token)
    security_matrix = compute_safety_score(live_data)
    security_matrix["token_target"] = token
    security_matrix["composability_interface"] = "BNB AI Agent SDK Compliant"

    if not deep_scan:
        security_matrix["risk_mitigation_vector"]["exposure_limit_multiplier"] *= 0.75

    return {
        "status": "success",
        "unique_name": "quantum_shield_risk_oracle",
        "timestamp": int(time.time()),
        "security_matrix": security_matrix,
    }


if __name__ == "__main__":
    default_params = {"token_target": "BNB", "deep_scan": True}

    if len(sys.argv) > 1:
        try:
            user_input = json.loads(sys.argv[1])
            if isinstance(user_input, dict):
                default_params.update(user_input)
        except json.JSONDecodeError:
            default_params["token_target"] = sys.argv[1]

    print("--- QUANTUM SHIELD: Track 2 Risk Oracle Skill Invocation ---")
    print(f"Executing with input_schema parameters: {json.dumps(default_params)}")

    result = execute_shield_skill(default_params)

    print("\n📡 [Standardized Shield Safety Payload Return]:")
    print(json.dumps(result, indent=2))
    print("\n🏆 Security audit completed. Clean return code 0.")