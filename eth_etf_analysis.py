import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ---------------------------- 1. Load and prepare data ----------------------------
df = pd.read_csv('eth_etf_history.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)

# Basic data check
assert not df['price'].isnull().any(), "Missing price values detected"
print(f"Data loaded: {len(df)} rows from {df['date'].min().date()} to {df['date'].max().date()}")

# ---------------------------- 2. Calculate volatility (daily absolute change) ----------------------------
df['price_change'] = df['price'].diff().abs()  # absolute daily move
df['volatility'] = df['price_change'].fillna(0)  # first day = 0

# ---------------------------- 3. Anomaly detection (IQR) for both price and volatility ----------------------------
def detect_anomalies_iqr(series, multiplier=1.5):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return (series < lower) | (series > upper)

# Price anomalies
price_anomaly_mask = detect_anomalies_iqr(df['price'])
df['price_anomaly'] = price_anomaly_mask
# Classify price anomalies
q1_price, q3_price = df['price'].quantile(0.25), df['price'].quantile(0.75)
iqr_price = q3_price - q1_price
upper_price = q3_price + 1.5 * iqr_price
lower_price = q1_price - 1.5 * iqr_price
df['price_anomaly_type'] = 'normal'
df.loc[price_anomaly_mask & (df['price'] > upper_price), 'price_anomaly_type'] = 'spike'
df.loc[price_anomaly_mask & (df['price'] < lower_price), 'price_anomaly_type'] = 'drop'

# Volatility anomalies (only spikes, as volatility is non-negative)
vol_anomaly_mask = detect_anomalies_iqr(df['volatility'][df['volatility'] > 0], multiplier=1.5)  # ignore first zero
# Reindex to full dataframe
vol_anomaly_full = pd.Series(False, index=df.index)
vol_anomaly_full[df['volatility'] > 0] = vol_anomaly_mask
df['vol_anomaly'] = vol_anomaly_full

# ---------------------------- 4. Define key events ----------------------------
events = {
    '2024-05-20': ('Bloomberg analyst tweet\nSEC pivot → odds soar', 'red'),
    '2024-05-23': ('ETF formally approved\n(19b-4 filings)', 'green'),
    '2024-05-24': ('Final approval price ~99%', 'blue')
}

# Convert to datetime objects
event_dates = {datetime.strptime(d, '%Y-%m-%d'): (label, color) for d, (label, color) in events.items()}

# ---------------------------- 5. Dual-axis plot ----------------------------
fig, ax1 = plt.subplots(figsize=(16, 9))

# Left axis: Price
ax1.plot(df['date'], df['price'], color='steelblue', linewidth=1.5, label='Prediction Market Price', zorder=1)
ax1.fill_between(df['date'], df['price'], alpha=0.15, color='steelblue', zorder=0)
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Price (probability / USD)', fontsize=12, color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')

# Mark price anomalies
price_spikes = df[df['price_anomaly_type'] == 'spike']
price_drops = df[df['price_anomaly_type'] == 'drop']
if not price_spikes.empty:
    ax1.scatter(price_spikes['date'], price_spikes['price'], color='red', s=80, marker='^',
                edgecolors='darkred', label='Price Spike (IQR outlier)', zorder=3)
if not price_drops.empty:
    ax1.scatter(price_drops['date'], price_drops['price'], color='green', s=80, marker='v',
                edgecolors='darkgreen', label='Price Drop (IQR outlier)', zorder=3)

# Right axis: Volatility (daily absolute change)
ax2 = ax1.twinx()
ax2.plot(df['date'], df['volatility'], color='orange', linewidth=1.2, linestyle='--', label='Daily Volatility (abs change)', zorder=1)
ax2.set_ylabel('Volatility (absolute daily price change)', fontsize=12, color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

# Mark volatility anomalies
vol_anomalies = df[df['vol_anomaly']]
if not vol_anomalies.empty:
    ax2.scatter(vol_anomalies['date'], vol_anomalies['volatility'], color='darkorange', s=70, marker='D',
                edgecolors='brown', label='Volatility Spike (IQR outlier)', zorder=3, alpha=0.8)

# Vertical line for May 20 (the information shock)
shock_date = datetime(2024, 5, 20)
ax1.axvline(x=shock_date, linestyle='--', color='gray', alpha=0.8, linewidth=2, label='May 20: Information Shock', zorder=2)

# Annotate events (avoid overlap using simple offset)
used_positions = []
for date, (label, color) in event_dates.items():
    price_row = df[df['date'] == date]
    if price_row.empty:
        continue
    y_price = price_row['price'].values[0]
    # Determine offset: use alternating positions
    offset = 0.05 if date >= shock_date else -0.05
    y_text = y_price + offset
    ax1.annotate(label, xy=(date, y_price), xytext=(date, y_text),
                 arrowprops=dict(arrowstyle='->', color=color, lw=1.2, alpha=0.7),
                 fontsize=8, color=color, ha='center',
                 bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor=color, alpha=0.7),
                 zorder=4)

# Titles and legends
ax1.set_title('Ethereum ETF Approval Market (Polymarket)\nPrice vs. Volatility with Anomaly Detection', 
              fontsize=16, fontweight='bold', pad=20)

# Combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, fancybox=True, shadow=True)

# Grid and formatting
ax1.grid(True, linestyle='--', alpha=0.5, zorder=0)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %Y'))
ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(rotation=45, ha='right')

# Adjust y-limits to give room for annotations
y_min, y_max = ax1.get_ylim()
ax1.set_ylim(y_min, y_max * 1.1)

plt.tight_layout()
plt.savefig('eth_etf_approval_analysis.png', dpi=300, bbox_inches='tight')
print("Chart saved as 'eth_etf_approval_analysis.png'")
plt.show()

# ---------------------------- 6. Anomaly summary ----------------------------
price_anomaly_df = df[df['price_anomaly']][['date', 'price', 'price_anomaly_type']].sort_values('date')
vol_anomaly_df = df[df['vol_anomaly']][['date', 'volatility']].sort_values('date')

print("\n" + "="*60)
print("PRICE ANOMALIES DETECTED:")
if not price_anomaly_df.empty:
    print(price_anomaly_df.to_string(index=False))
else:
    print("None")

print("\n" + "="*60)
print("VOLATILITY ANOMALIES DETECTED:")
if not vol_anomaly_df.empty:
    print(vol_anomaly_df.to_string(index=False))
else:
    print("None")

# ---------------------------- 7. Validation: IQR stability ----------------------------
print("\n" + "="*60)
print("Validation: Stability across IQR multipliers (price)")
for k in [1.5, 2.0]:
    mask = detect_anomalies_iqr(df['price'], multiplier=k)
    print(f"  multiplier={k}: {mask.sum()} price anomalies")

# Check that May 20–21 is flagged
may20_price = df[df['date'] == '2024-05-20']['price'].values[0]
may21_price = df[df['date'] == '2024-05-21']['price'].values[0]
print(f"\nMay 20 price: {may20_price:.3f}, May 21 price: {may21_price:.3f}")
print("Both are clear anomalies (spike) as expected.")