# ETH Addendum: Spec & Threat Mapping Note

**Role:** Spec & Threat Lead  
**Purpose:** Explain how newly added ETH teammate files map to the existing threat model and Gherkin spec, and what remains out-of-scope under current data granularity.

---

## 1. New teammate files reviewed

- `new files from teammates/eth_etf_history.csv`
- `new files from teammates/eth_with_indicators.csv`
- `new files from teammates/volatility_anomaly_results_eth.csv`
- `new files from teammates/multi_event_comparison_eth.csv`
- `new files from teammates/volatility_analysis_report_eth.txt`

Data is **daily-level** (price/return/rolling volatility + anomaly flags).  
No orderbook, no counterparty, no cancel/fill microstructure.

---

## 2. Mapping to existing threat model and Gherkin scenarios

| Threat / Scenario | Can ETH files validate it now? | Reason |
|---|---|---|
| **Wash Trading** (`Scenario 1`) | **No** | Requires account-level counterparties within short windows; not present in daily ETH files. |
| **Volume Spike** (`Scenario 2`) | **Partial** | Spec requires minute-level volume + minute price change. ETH files provide daily return/volatility proxies only. |
| **Spread Manipulation** (`Scenario 3`) | **No** | Requires bid-ask spread from orderbook; missing in ETH files. |
| **Flash Move / Whale-like move** (`Scenario 4`) | **Partial** | Spec is 5-minute move/reversal + volume condition. ETH daily extremes and high volatility can be treated as coarse proxy signals only. |
| **Spoofing** (`Scenario 5`) | **No** | Requires order placement/cancel behavior; unavailable in current ETH data. |

**Key rule boundary:**  
Current ETH pipeline can produce **risk flags for review**, not definitive manipulation labels.

---

## 3. What the ETH outputs add (useful for Spec & Threat)

From `volatility_analysis_report_eth.txt` and `multi_event_comparison_eth.csv`:

- A quantified anomaly summary (anomaly days and reason distribution).
- Event-date comparison rows (`max_gain_date`, `max_loss_date`, `max_volatility_date`) for validation workflow.
- Very large daily moves (e.g., extreme return dates) that justify review escalation.

For threat-model interpretation:

- These outputs strengthen **"something abnormal happened"** detection at daily level.
- They do **not** by themselves prove wash trading, spoofing, or insider misconduct.
- Ground-truth linkage (news/context checks) is still required before causal claims.

---

## 4. Recommended statement for repo/readout

Use this sentence consistently in docs/slides:

> "For ETH ETF data, daily anomaly outputs are treated as **investigation triggers**.  
> Confirmation of market manipulation requires finer-grained orderbook/counterparty evidence."

---

## 5. What should be pushed to GitHub

At minimum, push:

1. The 5 ETH teammate files under `new files from teammates/`
2. This note: `spec-and-threat/ETH_SPEC_THREAT_MAPPING_NOTE.md`

This ensures the repository contains both:

- the new ETH quantitative outputs, and
- the Spec/Threat owner's accountability note explaining validation scope and limits.

