# Polymarket Anomaly Detection — Gherkin Spec 
# Project: Presidential Election Odds Anomaly Detection | Role: Spec & Threat 

Feature: Detect anomalous odds/trading behaviour in Polymarket presidential election market
  As an analysis system,
  We want to automatically flag suspected manipulation or anomalies from order book and trade data,
  So that we can perform manual review and compliance checks.

  # ========== Scenario 1: Wash Trading ==========
  Scenario: Detect wash trading
    Given there exist two accounts A and B
    And within a continuous 1-minute window A and B are counterparties in at least 10 trades
    And the market mid-price change over that 1 minute is less than 0.1%
    When the system runs wash-trading detection on that time window
    Then the time window shall be flagged as "suspected wash trading / fake volume"
    And the system shall output accounts A, B and the time range for manual review

  # ========== Scenario 2: Volume Spike ==========
  Scenario: Detect volume spike
    Given the median per-minute volume M over the past 7 days has been computed
    And the volume in some minute T is V_T
    When V_T >= 10 * M
    And the price change in that minute is at least 2%
    Then minute T shall be flagged as "volume anomaly"
    And the system shall suggest Ground Truth comparison with news/social media for that day

  # ========== Scenario 3: Spread Manipulation ==========
  Scenario: Detect sudden spread widening (spread spike)
    Given the 95th percentile of bid-ask spread (ask - bid) over the past 24 hours S_95 has been computed
    And the current spread at some time is S_now
    When S_now > 2 * S_95
    And this condition persists for more than 5 minutes
    Then that period shall be flagged as "liquidity anomaly / spread anomaly"
    And the system shall record the start/end time and spread series for that period

  # ========== Scenario 4: Flash Move (Crash / Pump) ==========
  Scenario: Detect short-term sharp price move (flash crash or pump)
    Given "short-term" is defined as a 5-minute window
    And "sharp" is defined as price move of at least 5% from the window start
    When within 5 minutes price moves up or down by at least 5% and then reverses significantly
    And volume in that 5 minutes is more than 3 times the recent same-period average
    Then that 5-minute window shall be flagged as "suspected flash crash / pump"
    And the system shall output max drawdown and volume in the window for verification

  # ========== Scenario 5: Spoofing (Large order then cancel) ==========
  Scenario: Detect large order placed then quickly cancelled (spoofing)
    Given an account places a one-sided order at time T1 whose size is at least 50% of the top 5 levels on that side of the book
    And that order is fully cancelled within 1 minute without any fill
    When the system detects this "large order – short-time cancel" pattern
    Then that account's behaviour in that period shall be flagged as "suspected spoofing"
    And the system shall record account, market, time and order size
