# M2 Validation and Findings — Spec & Threat Lead

**Role:** Spec & Threat Lead  
**Project:** Polymarket signal analysis (2024 US Presidential Election)  
**Purpose:** Map M2 data and anomaly results to the threat model and Gherkin Spec; document validation outcomes and decisions.

---

## 1. M2 Inputs from Teammates

| Artifact | Owner | Description |
|----------|--------|-------------|
| `trump_2024_features_m2.csv` | Data engineer | Cleaned/featured data: `date`, `price`, `price_change`, `daily_return_pct`, `rolling_volatility_7d`, `ma_7d`. |
| `volatility_anomaly_results.csv` | Quant / analyst | Same schema plus `abs_daily_return`, `is_anomaly`, `anomaly_reason`. Anomaly rule: e.g. 2σ, 3× rolling volatility, and/or top 10% (absolute daily return). |
| `multi_event_comparison.csv` | Analyst | Event-based comparison: 川普遇刺日 (Trump assassination attempt 2024-07-13), 最大涨幅日, 最大跌幅日, 最大波动日; with 是否异常 and 异常原因. |

**Data scope:** Daily series only (no order book, no per-minute volume, no account-level data).

---

## 2. Mapping: Implementation → Threat Model & Spec

| Threat (Threat Model) | Gherkin scenario | Can we validate with M2 data? | M2 implementation |
|------------------------|------------------|-------------------------------|--------------------|
| **Wash Trading** | Detect wash trading | **No** | Requires two accounts as counterparties in 1-min window; we have no account/tick data. |
| **Volume Spike** | Detect volume spike | **Partial** | Spec uses per-minute volume (V_T ≥ 10×M) + price change ≥ 2%. We have daily returns and volatility only; “large daily return + high volatility” is a daily proxy. |
| **Spread Manipulation** | Detect spread widening | **No** | Requires bid-ask spread; we have no order book. |
| **Flash Move / Whale Move** | Detect flash crash/pump | **Partial** | Spec uses 5-min window, 5% move, reversal, 3× volume. Our data is daily; the analyst’s rule (2σ, 3× volatility, top 10% return) flags **sharp daily moves** and is a **proxy** for the same family of threats (whale/flash). |
| **Spoofing** | Detect large order then cancel | **No** | Requires order-level timestamps and cancels; we have no order book. |

**Conclusion:** With current M2 data we can only **partially** validate scenarios that depend on **daily price/volatility**. Wash Trading, Spread Manipulation, and Spoofing remain **not verifiable** until order book or tick data is available.

---

## 3. Validation Performed

### 3.1 Traceability: Anomaly rule ↔ Threat model

- The analyst’s anomaly logic (“2σ, 3× volatility, top 10%”) is **aligned with** the threat model’s **Whale Move** and **Volume Spike** observable signals (large price move, elevated volatility).
- It does **not** implement the exact Gherkin thresholds (e.g. 1 min, 10× volume, 5-min window) because the data is daily.

### 3.2 Ground Truth: Known event (Trump assassination attempt)

- **Event:** 川普遇刺日 (Trump assassination attempt) — **2024-07-13** in `multi_event_comparison.csv`.
- **Result:** 是否异常 = **否** (not flagged by the current rule on that day).
- **Next day:** **2024-07-14** is flagged in `volatility_anomaly_results.csv` as anomaly (True, "2σ,3倍波动率,前10%").
- **Finding:** The known shock date (07-13) was not flagged; the following day (07-14) was. This suggests either (a) the main price move was reflected on 07-14 in our series, or (b) the rule is more sensitive to the follow-through day. For Spec & Threat: we **record this** as Ground Truth evidence and leave the rule as-is unless the team decides to add an “event-window” (e.g. T+1) rule later.

### 3.3 Anomaly dates (for Ground Truth / review)

Dates flagged as anomaly in `volatility_anomaly_results.csv` (is_anomaly = True), for cross-check with news/events:

- 2024-01-05, 01-06, 01-08, 01-23  
- 2024-04-19  
- 2024-05-14, 05-15, 05-21, 05-31  
- 2024-07-02, 07-04, **07-14**, 07-19, 07-20, 07-27  
- 2024-08-01, 08-05, 08-08, 08-11, 08-18  
- 2024-09-07, 09-12  
- 2024-10-08, 10-16, 10-18, 10-22, 10-24, 10-25  
- 2024-11-02, 11-03  

*(Visualization/validation role can use this list for news/social-media checks.)*

---

## 4. Decisions and Spec/Threat Model Status

| Decision | Status |
|-----------|--------|
| **Threat model** | No change. Five threats and observable signals remain as in `THREAT_MODEL.md`. |
| **Gherkin Spec** | No change. Scenarios stay as in `SPEC_GHERKIN.feature`; they define the **target** behaviour when order book/tick data exists. |
| **M2 interpretation** | Daily volatility anomaly detection is treated as a **proxy** for Whale Move / Flash Move (and partly Volume Spike) only; it does not replace or alter the Spec. |
| **Trump event (07-13 vs 07-14)** | Documented as finding; no spec change unless the team adopts an explicit event-window (e.g. T+1) rule. |

---

## 5. M2 Evidence (Spec & Threat Lead)

- **Document:** This file (`M2_VALIDATION_AND_FINDINGS.md`): mapping of M2 artifacts to threat model and Spec, validation summary, Ground Truth note, and decision log.
- **No new diagram or new scenarios:** M2 work is validation and mapping only; threat diagram and Gherkin scenarios are unchanged.
