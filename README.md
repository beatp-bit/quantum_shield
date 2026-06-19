# QUANTUM SHIELD — AI Contract & Whale Concentration Risk Oracle

🏆 **Developed for the CoinMarketCap BNB HACK 2026**
🎯 **Track 2 — Strategy Skills**
🛡️ **Independent Security Oracle Layer**

QUANTUM SHIELD transforms live CoinMarketCap token data into programmatic, machine-readable JSON safety matrices for autonomous agents — computing real-time safety scores, whale concentration risk, wash trading flags, and liquidity decay alerts.

---

## 🔬 Live Score Computation — Real CMC Data

Unlike static risk oracles, QUANTUM SHIELD computes a **dynamic safety score (0–100)** from live market data on every invocation. The score changes with the market.

**Sample output — June 20, 2026:**

| Token | Safety Score | Whale Risk | Wash Flag | Slippage |
|---|---|---|---|---|
| BNB | 100.0 | medium_risk | false | 0.3% |
| ETH | 95.0 | low_risk | false | 0.3% |

---

## ⚙️ Scoring Model (100 points)

| Factor | Weight | Penalizes |
|---|---|---|
| Volume stability | 30 pts | volume_change_24h > 25% |
| Price stability 24h | 25 pts | price_change_24h > 2% |
| Price stability 7d | 20 pts | price_change_7d > 5% |
| Market cap tier | 15 pts | cap < $1B |
| 1h momentum spike | 10 pts | price_change_1h > 1% |

**Whale concentration** — derived from market cap dominance + volume change.
**Wash trading flag** — fires when volume_change_24h > 150% with price_change_24h < 3%.
**Liquidity decay alert** — fires when volume_change_24h < -60%.

---

## 🗂️ Architecture

```text
quantum_shield/
├── shield_exporter.py      # Live CMC data fetch + scoring engine
├── data/                   # CMC API integration modules
├── signals/                # Signal processing layer
├── strategy/               # Risk vector aggregation
└── .env.example            # API key configuration
```

---

## 📡 Standardized Risk Payload (JSON)

```json
{
  "status": "success",
  "unique_name": "quantum_shield_risk_oracle",
  "timestamp": 1781911855,
  "security_matrix": {
    "safety_score_rating": 100.0,
    "whale_concentration_score": "medium_risk",
    "volume_wash_trading_flag": false,
    "liquidity_decay_alert": false,
    "scoring_breakdown": {
      "volume_change_24h_pct": -22.78,
      "price_change_24h_pct": 0.5,
      "price_change_7d_pct": -3.74,
      "market_cap_usd": 78198062847
    },
    "risk_mitigation_vector": {
      "max_suggested_slippage_pct": 0.3,
      "exposure_limit_multiplier": 1.0
    },
    "composability_interface": "BNB AI Agent SDK Compliant"
  }
}
```

---

## ⛓️ Ecosystem Integration

Designed as a **plug-and-play Security Skill** for the CMC Agent Hub. Downstream agents built with the **BNB AI Agent SDK** or **Trust Wallet Agent Kit (TWAK)** can call this oracle before executing swaps to:

1. **Guard against wash trading** — skip low-quality volume signals
2. **Adjust slippage dynamically** — tighter for stable assets, wider for volatile ones
3. **Scale exposure** — reduce position size when safety score drops below threshold

---

## 🚀 Usage

```bash
# Setup
pip install requests python-dotenv

# Run
python shield_exporter.py BNB
python shield_exporter.py ETH
python shield_exporter.py '{"token_target": "SOL", "deep_scan": true}'
```

Set `CMC_API_KEY` in `.env` (see `.env.example`).

**🏷️ Tags:** Risk Oracle, Security Skill, Whale Detection, Wash Trading, BNB Chain, CoinMarketCap API, Live Scoring