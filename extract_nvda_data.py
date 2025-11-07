#!/usr/bin/env python3
"""
NVDA Historical Data Extractor + Strategy Backtest
Saves all data and results to C:\Trading folder
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Configuration
OUTPUT_FOLDER = r"C:\Trading"
START_DATE = "2019-01-01"
END_DATE = "2024-11-01"
TICKER = "NVDA"

# Create output folder if it doesn't exist
print("="*80)
print("🚀 NVDA HISTORICAL DATA EXTRACTION + BACKTEST")
print("="*80)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
    print(f"✅ Created folder: {OUTPUT_FOLDER}")
else:
    print(f"✅ Using existing folder: {OUTPUT_FOLDER}")

# ============================================================================
# STEP 1: DOWNLOAD HISTORICAL DATA
# ============================================================================
print(f"\n📥 Step 1: Downloading {TICKER} historical data from Yahoo Finance...")
print(f"   Date range: {START_DATE} to {END_DATE}")

try:
    nvda = yf.download(TICKER, start=START_DATE, end=END_DATE, progress=False)

    if nvda.empty:
        print("❌ Error: No data downloaded. Check your internet connection.")
        exit(1)

    # Flatten column names if multi-level
    if isinstance(nvda.columns, pd.MultiIndex):
        nvda.columns = nvda.columns.get_level_values(0)

    print(f"✅ Successfully downloaded {len(nvda)} days of data!")
    print(f"   Date range: {nvda.index[0].date()} to {nvda.index[-1].date()}")
    close_min = float(nvda['Close'].min())
    close_max = float(nvda['Close'].max())
    print(f"   Price range: ${close_min:.2f} - ${close_max:.2f}")
    
    # Save raw daily data
    daily_file = os.path.join(OUTPUT_FOLDER, f"{TICKER}_daily_prices.csv")
    nvda.to_csv(daily_file)
    print(f"\n💾 Saved daily prices to: {daily_file}")
    
    # Display summary statistics
    print(f"\n📊 Summary Statistics:")
    close_mean = float(nvda['Close'].mean())
    close_std = float(nvda['Close'].std())
    print(f"   Average Close: ${close_mean:.2f}")
    print(f"   Std Deviation: ${close_std:.2f}")
    print(f"   Highest Close: ${close_max:.2f} on {nvda['Close'].idxmax().date()}")
    print(f"   Lowest Close:  ${close_min:.2f} on {nvda['Close'].idxmin().date()}")
    
    # Show COVID crash
    covid = nvda[(nvda.index >= '2020-02-01') & (nvda.index <= '2020-04-01')]
    if len(covid) > 0:
        covid_high = float(covid['Close'].max())
        covid_low = float(covid['Close'].min())
        covid_drop = (covid_low / covid_high - 1) * 100
        covid_high_date = covid['Close'].idxmax().date()
        covid_low_date = covid['Close'].idxmin().date()
        print(f"\n💥 COVID Crash (Feb-Apr 2020):")
        print(f"   High: ${covid_high:.2f} on {covid_high_date}")
        print(f"   Low:  ${covid_low:.2f} on {covid_low_date}")
        print(f"   Drop: {covid_drop:.1f}%")

    # Show 2022 bear market
    bear22 = nvda[(nvda.index >= '2022-01-01') & (nvda.index <= '2022-12-31')]
    if len(bear22) > 0:
        bear_high = float(bear22['Close'].max())
        bear_low = float(bear22['Close'].min())
        bear_drop = (bear_low / bear_high - 1) * 100
        bear_high_date = bear22['Close'].idxmax().date()
        bear_low_date = bear22['Close'].idxmin().date()
        print(f"\n🐻 2022 Bear Market:")
        print(f"   High: ${bear_high:.2f} on {bear_high_date}")
        print(f"   Low:  ${bear_low:.2f} on {bear_low_date}")
        print(f"   Drop: {bear_drop:.1f}%")
    
except Exception as e:
    print(f"❌ Error downloading data: {e}")
    print("\n💡 Make sure you have yfinance installed:")
    print("   pip install yfinance pandas numpy matplotlib")
    exit(1)

# ============================================================================
# STEP 2: CONVERT TO WEEKLY DATA
# ============================================================================
print("\n📊 Step 2: Converting to weekly data...")

nvda['Week'] = nvda.index.to_period('W')
weekly = nvda.groupby('Week').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).reset_index()
weekly['Date'] = weekly['Week'].dt.to_timestamp()

# Calculate returns and volatility
weekly['Returns'] = weekly['Close'].pct_change()
weekly['Volatility_12w'] = weekly['Returns'].rolling(window=12).std() * np.sqrt(52)
weekly['Volatility_12w'].fillna(weekly['Volatility_12w'].mean(), inplace=True)

# Simulate VIX (crude approximation)
weekly['VIX_Estimate'] = weekly['Volatility_12w'] * 100 * 0.4 + 15
weekly['VIX_Estimate'] = weekly['VIX_Estimate'].clip(lower=10, upper=80)

# Save weekly data
weekly_file = os.path.join(OUTPUT_FOLDER, f"{TICKER}_weekly_prices.csv")
weekly.to_csv(weekly_file, index=False)
print(f"✅ Processed {len(weekly)} weeks of data")
print(f"💾 Saved weekly prices to: {weekly_file}")

# ============================================================================
# STEP 3: RUN STRATEGY BACKTESTS
# ============================================================================
print("\n🎯 Step 3: Running strategy backtests...")

INITIAL_CAPITAL = 50000
SHARES_PER_CONTRACT = 100

strategies = {
    'Original': {
        'capital': INITIAL_CAPITAL,
        'results': [],
        'description': 'Original Linda 1 - 3 contracts, no protection'
    },
    'Cash_Fortress': {
        'capital': INITIAL_CAPITAL,
        'results': [],
        'description': 'Cash Fortress - 1 contract, 60% cash reserve'
    },
    'Dynamic': {
        'capital': INITIAL_CAPITAL,
        'results': [],
        'description': 'Dynamic Allocation - VIX-based sizing'
    },
}

print(f"\nSimulating {len(strategies)} strategies over {len(weekly)-1} weeks...\n")

for i in range(1, len(weekly)):
    prev_week = weekly.iloc[i-1]
    current_week = weekly.iloc[i]
    
    prev_price = prev_week['Close']
    current_price = current_week['Close']
    vol = prev_week['Volatility_12w']
    vix = prev_week['VIX_Estimate']
    date = current_week['Date']
    
    weekly_vol = vol * np.sqrt(1/52)
    strike = prev_price * (1 - 1.0 * weekly_vol)
    
    # === ORIGINAL STRATEGY ===
    contracts = 3
    premium = max(prev_price * weekly_vol * 0.4 * np.exp(-1.0**2 / (2 * weekly_vol**2)) * 100, 40) * contracts
    
    if current_price >= strike:
        pnl = premium
        status = "OTM"
    else:
        loss = (strike - current_price) * 100 * contracts
        pnl = premium - loss
        status = "ASSIGNED"
    
    strategies['Original']['capital'] += pnl
    strategies['Original']['results'].append({
        'Date': date,
        'NVDA_Price': current_price,
        'Strike': strike,
        'Contracts': contracts,
        'Premium': premium,
        'PnL': pnl,
        'Capital': strategies['Original']['capital'],
        'VIX': vix,
        'Status': status
    })
    
    # === CASH FORTRESS ===
    contracts = 1
    premium = max(prev_price * weekly_vol * 0.4 * np.exp(-1.0**2 / (2 * weekly_vol**2)) * 100, 40) * contracts
    
    if current_price >= strike:
        pnl = premium
        status = "OTM"
    else:
        loss = (strike - current_price) * 100 * contracts
        # Simulate having cash to absorb/average down
        pnl = premium - loss * 0.8
        status = "ASSIGNED_ABSORBED"
    
    strategies['Cash_Fortress']['capital'] += pnl
    strategies['Cash_Fortress']['results'].append({
        'Date': date,
        'NVDA_Price': current_price,
        'Strike': strike,
        'Contracts': contracts,
        'Premium': premium,
        'PnL': pnl,
        'Capital': strategies['Cash_Fortress']['capital'],
        'VIX': vix,
        'Status': status
    })
    
    # === DYNAMIC ALLOCATION ===
    if vix < 15:
        contracts = 2
        allocation = "35%"
    elif vix < 25:
        contracts = 1
        allocation = "20%"
    else:
        contracts = 1
        allocation = "10%"
    
    premium = max(prev_price * weekly_vol * 0.4 * np.exp(-1.0**2 / (2 * weekly_vol**2)) * 100, 40) * contracts
    hedge_cost = 30 if (vix > 25 and i % 4 == 0) else 0
    
    if current_price >= strike:
        pnl = premium - hedge_cost
        status = "OTM"
    else:
        loss = (strike - current_price) * 100 * contracts
        pnl = premium - loss - hedge_cost
        status = "ASSIGNED"
    
    strategies['Dynamic']['capital'] += pnl
    strategies['Dynamic']['results'].append({
        'Date': date,
        'NVDA_Price': current_price,
        'Strike': strike,
        'Contracts': contracts,
        'Allocation': allocation,
        'Premium': premium,
        'Hedge_Cost': hedge_cost,
        'PnL': pnl,
        'Capital': strategies['Dynamic']['capital'],
        'VIX': vix,
        'Status': status
    })

# Convert results to DataFrames
for name in strategies:
    strategies[name]['df'] = pd.DataFrame(strategies[name]['results'])
    df = strategies[name]['df']
    
    # Calculate drawdowns
    df['Peak'] = df['Capital'].cummax()
    df['Drawdown_%'] = (df['Capital'] - df['Peak']) / df['Peak'] * 100
    
    # Save detailed results
    detail_file = os.path.join(OUTPUT_FOLDER, f"backtest_{name}_details.csv")
    df.to_csv(detail_file, index=False)
    print(f"💾 Saved {name} details to: backtest_{name}_details.csv")

# ============================================================================
# STEP 4: CALCULATE AND DISPLAY RESULTS
# ============================================================================
print("\n" + "="*80)
print("📈 BACKTEST RESULTS WITH REAL HISTORICAL DATA")
print("="*80)

results_summary = []

for name, data in strategies.items():
    df = data['df']
    
    final_capital = df['Capital'].iloc[-1]
    total_return = (final_capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    max_dd = df['Drawdown_%'].min()
    win_rate = (df['PnL'] > 0).mean() * 100
    avg_weekly = df['PnL'].mean()
    worst_week = df['PnL'].min()
    best_week = df['PnL'].max()
    
    results_summary.append({
        'Strategy': name,
        'Description': data['description'],
        'Final_Capital': final_capital,
        'Total_Return_%': total_return,
        'Max_Drawdown_%': max_dd,
        'Win_Rate_%': win_rate,
        'Avg_Weekly_PnL': avg_weekly,
        'Best_Week': best_week,
        'Worst_Week': worst_week
    })

results_df = pd.DataFrame(results_summary).sort_values('Total_Return_%', ascending=False)

# Display summary table
print(f"\n{'Strategy':<20} {'Final Value':<15} {'Return':<12} {'Max DD':<10} {'Win Rate':<10} {'Avg Week':<12}")
print("-"*85)
for _, row in results_df.iterrows():
    print(f"{row['Strategy']:<20} ${row['Final_Capital']:>13,.0f} {row['Total_Return_%']:>10.1f}% "
          f"{row['Max_Drawdown_%']:>9.1f}% {row['Win_Rate_%']:>9.1f}% ${row['Avg_Weekly_PnL']:>10.0f}")

# COVID crash analysis
print(f"\n💥 COVID CRASH PERFORMANCE (Feb-Apr 2020):")
for name, data in strategies.items():
    df = data['df']
    covid_df = df[(df['Date'] >= '2020-02-01') & (df['Date'] <= '2020-04-15')]
    if len(covid_df) > 0:
        covid_pnl = covid_df['PnL'].sum()
        start_cap = df[df['Date'] < '2020-02-01']['Capital'].iloc[-1] if len(df[df['Date'] < '2020-02-01']) > 0 else INITIAL_CAPITAL
        end_cap = covid_df['Capital'].iloc[-1]
        covid_return = (end_cap - start_cap) / start_cap * 100
        print(f"   {name:<20} Total P&L: ${covid_pnl:>+8,.0f} | Return: {covid_return:>+6.1f}%")

# 2022 bear market analysis
print(f"\n🐻 2022 BEAR MARKET PERFORMANCE:")
for name, data in strategies.items():
    df = data['df']
    bear_df = df[(df['Date'] >= '2022-01-01') & (df['Date'] <= '2022-12-31')]
    if len(bear_df) > 0:
        bear_pnl = bear_df['PnL'].sum()
        start_cap = df[df['Date'] < '2022-01-01']['Capital'].iloc[-1] if len(df[df['Date'] < '2022-01-01']) > 0 else INITIAL_CAPITAL
        end_cap = bear_df['Capital'].iloc[-1]
        bear_return = (end_cap - start_cap) / start_cap * 100
        print(f"   {name:<20} Total P&L: ${bear_pnl:>+8,.0f} | Return: {bear_return:>+6.1f}%")

# Save summary
summary_file = os.path.join(OUTPUT_FOLDER, "backtest_summary.csv")
results_df.to_csv(summary_file, index=False)
print(f"\n💾 Saved summary to: {summary_file}")

# ============================================================================
# STEP 5: CREATE VISUALIZATIONS
# ============================================================================
print("\n🎨 Step 5: Creating visualizations...")

# Main comparison chart
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.3)

colors = {
    'Original': '#e74c3c',
    'Cash_Fortress': '#2ecc71',
    'Dynamic': '#f39c12'
}

# 1. Portfolio value over time
ax1 = fig.add_subplot(gs[0, :])
for name in strategies.keys():
    df = strategies[name]['df']
    ax1.plot(df['Date'], df['Capital'], label=name.replace('_', ' '), 
             color=colors[name], linewidth=2.5, alpha=0.8)

ax1.axhline(y=INITIAL_CAPITAL, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
ax1.axvspan(pd.Timestamp('2020-02-01'), pd.Timestamp('2020-04-15'), 
            alpha=0.15, color='red', label='COVID Crash')
ax1.axvspan(pd.Timestamp('2022-01-01'), pd.Timestamp('2022-12-31'), 
            alpha=0.15, color='orange', label='2022 Bear')

ax1.set_title('Portfolio Value Over Time (Real NVDA Data)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Date')
ax1.set_ylabel('Portfolio Value ($)')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# 2. Drawdown comparison
ax2 = fig.add_subplot(gs[1, :])
for name in strategies.keys():
    df = strategies[name]['df']
    ax2.plot(df['Date'], df['Drawdown_%'], label=name.replace('_', ' '), 
             color=colors[name], linewidth=1.5, alpha=0.8)
    ax2.fill_between(df['Date'], 0, df['Drawdown_%'], alpha=0.15, color=colors[name])

ax2.set_title('Drawdown Comparison', fontsize=14, fontweight='bold')
ax2.set_xlabel('Date')
ax2.set_ylabel('Drawdown (%)')
ax2.legend(loc='lower left')
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='black', linewidth=0.8)

# 3. NVDA price history
ax3 = fig.add_subplot(gs[2, 0])
ax3.plot(weekly['Date'], weekly['Close'], color='#3498db', linewidth=1.5)
ax3.set_title('NVDA Price History', fontsize=12, fontweight='bold')
ax3.set_xlabel('Date')
ax3.set_ylabel('Price ($)')
ax3.grid(True, alpha=0.3)

# 4. Returns comparison
ax4 = fig.add_subplot(gs[2, 1])
names = [row['Strategy'].replace('_', ' ') for _, row in results_df.iterrows()]
returns = [row['Total_Return_%'] for _, row in results_df.iterrows()]
bar_colors = [colors[row['Strategy']] for _, row in results_df.iterrows()]
bars = ax4.barh(names, returns, color=bar_colors, alpha=0.7)
ax4.axvline(x=0, color='black', linewidth=1)
ax4.set_title('Total Returns Comparison', fontsize=12, fontweight='bold')
ax4.set_xlabel('Return (%)')
ax4.grid(True, alpha=0.3, axis='x')
for i, (bar, val) in enumerate(zip(bars, returns)):
    ax4.text(val, i, f' {val:.1f}%', va='center', fontsize=10)

# 5. Max drawdown comparison
ax5 = fig.add_subplot(gs[3, 0])
names = [row['Strategy'].replace('_', ' ') for _, row in results_df.iterrows()]
dds = [row['Max_Drawdown_%'] for _, row in results_df.iterrows()]
bar_colors = [colors[row['Strategy']] for _, row in results_df.iterrows()]
bars = ax5.barh(names, dds, color=bar_colors, alpha=0.7)
ax5.axvline(x=0, color='black', linewidth=1)
ax5.set_title('Maximum Drawdowns', fontsize=12, fontweight='bold')
ax5.set_xlabel('Max Drawdown (%)')
ax5.grid(True, alpha=0.3, axis='x')
for i, (bar, val) in enumerate(zip(bars, dds)):
    ax5.text(val, i, f' {val:.1f}%', va='center', fontsize=10)

# 6. Summary table
ax6 = fig.add_subplot(gs[3, 1])
ax6.axis('off')

table_data = [['Strategy', 'Final Value', 'Return', 'Max DD', 'Win Rate']]
for _, row in results_df.iterrows():
    table_data.append([
        row['Strategy'].replace('_', ' '),
        f"${row['Final_Capital']:,.0f}",
        f"{row['Total_Return_%']:+.1f}%",
        f"{row['Max_Drawdown_%']:.1f}%",
        f"{row['Win_Rate_%']:.1f}%"
    ])

table = ax6.table(cellText=table_data, cellLoc='center', loc='center',
                  colWidths=[0.25, 0.20, 0.15, 0.15, 0.15])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.5)

# Style header
for i in range(5):
    cell = table[(0, i)]
    cell.set_facecolor('#34495e')
    cell.set_text_props(weight='bold', color='white')

ax6.set_title('Performance Summary', fontsize=12, fontweight='bold', pad=20)

# Save main chart
chart_file = os.path.join(OUTPUT_FOLDER, "backtest_results.png")
plt.savefig(chart_file, dpi=150, bbox_inches='tight')
print(f"✅ Saved main chart to: {chart_file}")

plt.close()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ EXTRACTION AND BACKTEST COMPLETE!")
print("="*80)

print(f"\n📁 All files saved to: {OUTPUT_FOLDER}\n")
print("Files created:")
print(f"   1. {TICKER}_daily_prices.csv - Daily historical prices")
print(f"   2. {TICKER}_weekly_prices.csv - Weekly aggregated data")
print(f"   3. backtest_summary.csv - Strategy comparison summary")
print(f"   4. backtest_Original_details.csv - Original strategy details")
print(f"   5. backtest_Cash_Fortress_details.csv - Cash Fortress details")
print(f"   6. backtest_Dynamic_details.csv - Dynamic strategy details")
print(f"   7. backtest_results.png - Visualization chart")

print("\n🎯 Next Steps:")
print("   1. Review the CSV files in Excel or a text editor")
print("   2. View backtest_results.png for visual comparison")
print("   3. Upload the files to Claude for detailed analysis")

print("\n" + "="*80)
