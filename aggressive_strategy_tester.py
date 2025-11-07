#!/usr/bin/env python3
"""
AGGRESSIVE PUT STRATEGY TESTER - TARGET: 100%+ ANNUAL RETURNS
Tests high-risk, high-reward strategies
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# Configuration
OUTPUT_FOLDER = r"C:\Trading\aggressive_results"
START_DATE = "2019-01-01"
END_DATE = "2024-11-01"
INITIAL_CAPITAL = 50000

# Focus on volatile, high-premium stocks
STOCKS = {
    'TSLA': 'Tesla',
    'NVDA': 'NVIDIA',
    'AMD': 'AMD',
    'COIN': 'Coinbase',
    'MSTR': 'MicroStrategy',
    'QQQ': 'Nasdaq ETF',
    'PLTR': 'Palantir',
    'RIVN': 'Rivian',
}

# AGGRESSIVE STRATEGY DEFINITIONS
STRATEGIES = {
    'Daily_ATM_Aggressive': {
        'description': 'Daily ATM puts, 2x leverage, high frequency',
        'frequency': 'daily',
        'strike_offset': 1.00,  # At the money
        'contracts': 2,
        'use_margin': True,
        'margin_multiplier': 2.0
    },

    'Daily_ITM_Premium_Hunter': {
        'description': 'Daily In-the-Money puts for maximum premium',
        'frequency': 'daily',
        'strike_offset': 1.02,  # 2% ITM - higher premium
        'contracts': 1,
        'use_margin': False,
        'margin_multiplier': 1.0
    },

    'Daily_Scalper_3x': {
        'description': 'Daily trades, 3x contracts, quick gains',
        'frequency': 'daily',
        'strike_offset': 0.98,  # 2% OTM
        'contracts': 3,
        'use_margin': True,
        'margin_multiplier': 3.0
    },

    'Weekly_Leveraged_5x': {
        'description': 'Weekly with 5x leverage - maximum aggression',
        'frequency': 'weekly',
        'strike_offset': 0.97,
        'contracts': 5,
        'use_margin': True,
        'margin_multiplier': 5.0
    },

    'Daily_Momentum_Rider': {
        'description': 'Daily puts only when stock trending up (momentum)',
        'frequency': 'daily',
        'strike_offset': 0.99,
        'contracts': 2,
        'use_margin': True,
        'margin_multiplier': 2.0,
        'momentum_filter': True
    },

    'Daily_High_Vol_Max_Premium': {
        'description': 'Daily puts only when VIX>25, max contracts',
        'frequency': 'daily',
        'strike_offset': 1.00,
        'contracts': 4,
        'use_margin': True,
        'margin_multiplier': 3.0,
        'vix_filter': 25
    },

    'Daily_Close_ITM': {
        'description': 'Daily 1% ITM for higher premium',
        'frequency': 'daily',
        'strike_offset': 1.01,
        'contracts': 2,
        'use_margin': True,
        'margin_multiplier': 2.0
    },

    'Wheel_Strategy_Aggressive': {
        'description': 'Sell puts, get assigned, sell calls (simulated)',
        'frequency': 'weekly',
        'strike_offset': 0.97,
        'contracts': 2,
        'use_margin': True,
        'margin_multiplier': 2.0,
        'wheel_mode': True
    },

    'Daily_Range_Bound': {
        'description': 'Daily puts when stock pulls back 2%+ (buy the dip)',
        'frequency': 'daily',
        'strike_offset': 0.98,
        'contracts': 3,
        'use_margin': True,
        'margin_multiplier': 2.5,
        'pullback_filter': 0.02  # Only trade after 2% drop
    },

    'Daily_Compounding_Beast': {
        'description': 'Daily ATM, reinvest ALL profits, compound aggressively',
        'frequency': 'daily',
        'strike_offset': 1.00,
        'contracts': 'compound',  # Use all available capital
        'use_margin': True,
        'margin_multiplier': 2.0,
        'compound_mode': True
    },

    'Weekly_All_In_Risk': {
        'description': 'Weekly ATM, use 100% of capital every trade',
        'frequency': 'weekly',
        'strike_offset': 1.00,
        'contracts': 'all_in',
        'use_margin': False,
        'margin_multiplier': 1.0
    },

    'Daily_Volatility_Harvester': {
        'description': 'Daily 0.5% ITM during high vol, more contracts',
        'frequency': 'daily',
        'strike_offset': 1.005,
        'contracts': 'dynamic_vol',  # More when vol is high
        'use_margin': True,
        'margin_multiplier': 2.5
    },
}

print("="*80)
print("🚀 AGGRESSIVE PUT STRATEGY BACKTESTER - TARGET: 100% ANNUAL RETURN")
print("="*80)
print(f"\nTesting {len(STRATEGIES)} aggressive strategies")
print(f"Stocks: {', '.join(STOCKS.keys())}")
print(f"Time period: {START_DATE} to {END_DATE}")
print(f"Initial capital: ${INITIAL_CAPITAL:,}")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ============================================================================
# DOWNLOAD DATA
# ============================================================================
print("\n" + "="*80)
print("📥 DOWNLOADING DATA")
print("="*80)

stock_data = {}

for ticker, name in STOCKS.items():
    try:
        print(f"\nDownloading {ticker} ({name})...", end=" ")
        df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)

        if df.empty or len(df) < 100:
            print(f"❌ Insufficient data")
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Calculate daily metrics
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)
        df['Volatility'].fillna(df['Volatility'].mean(), inplace=True)

        # VIX estimate
        df['VIX_Estimate'] = df['Volatility'] * 100 * 0.5 + 15
        df['VIX_Estimate'] = df['VIX_Estimate'].clip(lower=10, upper=80)

        # Momentum indicators
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['Momentum'] = (df['Close'] > df['SMA_5']).astype(int)

        # Pullback detector
        df['High_5d'] = df['High'].rolling(window=5).max()
        df['Pullback'] = (df['High_5d'] - df['Close']) / df['High_5d']

        stock_data[ticker] = {
            'name': name,
            'data': df,
            'start_price': float(df['Close'].iloc[0]),
            'end_price': float(df['Close'].iloc[-1]),
            'days': len(df)
        }

        total_return = (stock_data[ticker]['end_price'] / stock_data[ticker]['start_price'] - 1) * 100
        print(f"✅ {len(df)} days | {total_return:+.1f}% return")

    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n✅ Downloaded {len(stock_data)} stocks")

# ============================================================================
# PREMIUM CALCULATOR
# ============================================================================
def calculate_premium(stock_price, strike, volatility, frequency='weekly'):
    """Enhanced premium calculator"""

    if frequency == 'daily':
        tte = 1/252
    elif frequency == 'weekly':
        tte = 5/252
    else:
        tte = 5/252

    moneyness = strike / stock_price
    intrinsic = max(strike - stock_price, 0)

    # Enhanced time value for ITM/ATM
    if moneyness >= 1.0:  # ITM or ATM
        time_value = stock_price * volatility * np.sqrt(tte) * 0.6
    else:  # OTM
        time_value = stock_price * volatility * np.sqrt(tte) * 0.4

    premium = intrinsic + time_value
    min_premium = stock_price * 0.003

    return max(premium, min_premium) * 100

# ============================================================================
# BACKTEST ENGINE
# ============================================================================
def run_aggressive_backtest(ticker, stock_info, strategy_name, strategy_params):
    """Aggressive backtesting engine"""

    df = stock_info['data'].copy()
    capital = INITIAL_CAPITAL
    trades = []
    positions = 0  # For wheel strategy

    frequency = strategy_params.get('frequency', 'weekly')
    use_margin = strategy_params.get('use_margin', False)
    margin_mult = strategy_params.get('margin_multiplier', 1.0)

    # Determine iteration
    if frequency == 'daily':
        indices = range(1, len(df))
    else:  # weekly
        indices = range(5, len(df), 5)

    max_capital_ever = capital

    for i in indices:
        if i >= len(df):
            break

        prev_day = df.iloc[i-1]
        current_day = df.iloc[i]

        prev_price = prev_day['Close']
        current_price = current_day['Close']
        vol = prev_day['Volatility']
        vix = prev_day['VIX_Estimate']
        date = current_day.name

        # Apply filters
        if strategy_params.get('momentum_filter'):
            if prev_day['Momentum'] == 0:  # Not trending up
                continue

        if strategy_params.get('vix_filter'):
            if vix < strategy_params['vix_filter']:
                continue

        if strategy_params.get('pullback_filter'):
            if prev_day['Pullback'] < strategy_params['pullback_filter']:
                continue

        # Calculate strike
        strike = prev_price * strategy_params['strike_offset']

        # Determine contracts
        contracts = strategy_params['contracts']

        if contracts == 'compound':
            # Use maximum available capital
            available = capital * margin_mult if use_margin else capital
            contracts = int(available / (strike * 100))
            contracts = max(1, min(contracts, 10))  # Cap at 10

        elif contracts == 'all_in':
            # Use all capital
            contracts = int(capital / (strike * 100))
            contracts = max(1, contracts)

        elif contracts == 'dynamic_vol':
            # More contracts when volatility is high
            if vix > 30:
                contracts = 4
            elif vix > 20:
                contracts = 3
            else:
                contracts = 2

        # Check capital requirements
        required_capital = strike * 100 * contracts
        available_capital = capital * margin_mult if use_margin else capital

        if required_capital > available_capital:
            contracts = int(available_capital / (strike * 100))

        if contracts == 0:
            continue

        # Calculate premium
        premium_per_contract = calculate_premium(prev_price, strike, vol, frequency)
        total_premium = premium_per_contract * contracts

        # Determine outcome
        if current_price >= strike:
            # OTM - keep premium
            pnl = total_premium
            status = "WIN"
        else:
            # Assigned
            loss = (strike - current_price) * 100 * contracts

            # For wheel strategy, reduce loss (selling calls would offset)
            if strategy_params.get('wheel_mode'):
                # Simulate covered call premium
                call_premium = current_price * 0.015 * contracts * 100
                loss = loss * 0.7  # Reduced loss due to calls
                pnl = total_premium - loss + call_premium
                status = "ASSIGNED_WHEEL"
            else:
                pnl = total_premium - loss
                status = "LOSS"

        # Update capital
        capital += pnl

        # Track max capital for drawdown
        if capital > max_capital_ever:
            max_capital_ever = capital

        # Stop if blown up
        if capital < INITIAL_CAPITAL * 0.3:  # Down 70%
            trades.append({
                'Date': date,
                'Stock_Price': current_price,
                'Strike': strike,
                'Contracts': contracts,
                'Premium': total_premium,
                'PnL': pnl,
                'Capital': capital,
                'Status': 'BLOWN_UP'
            })
            break

        trades.append({
            'Date': date,
            'Stock_Price': current_price,
            'Strike': strike,
            'Contracts': contracts,
            'Premium': total_premium,
            'PnL': pnl,
            'Capital': capital,
            'VIX': vix,
            'Status': status
        })

    return pd.DataFrame(trades)

# ============================================================================
# RUN BACKTESTS
# ============================================================================
print("\n" + "="*80)
print("⚙️  RUNNING AGGRESSIVE BACKTESTS")
print("="*80)

all_results = []
total_tests = len(stock_data) * len(STRATEGIES)
test_num = 0

for ticker, stock_info in stock_data.items():
    for strategy_name, strategy_params in STRATEGIES.items():
        test_num += 1
        print(f"\r[{test_num}/{total_tests}] {ticker} + {strategy_name}...", end="")

        try:
            results_df = run_aggressive_backtest(ticker, stock_info, strategy_name, strategy_params)

            if len(results_df) == 0:
                continue

            # Calculate metrics
            final_capital = results_df['Capital'].iloc[-1]
            total_return = (final_capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

            # Time period
            start_date = results_df['Date'].iloc[0]
            end_date = results_df['Date'].iloc[-1]
            years = (end_date - start_date).days / 365.25

            if years > 0 and final_capital > 0:
                annualized_return = ((final_capital / INITIAL_CAPITAL) ** (1/years) - 1) * 100
            else:
                annualized_return = total_return / years if years > 0 else 0

            # Drawdown
            results_df['Peak'] = results_df['Capital'].cummax()
            results_df['Drawdown_%'] = (results_df['Capital'] - results_df['Peak']) / results_df['Peak'] * 100
            max_drawdown = results_df['Drawdown_%'].min()

            # Win stats
            actual_trades = results_df[results_df['Contracts'] > 0]
            if len(actual_trades) > 0:
                win_rate = (actual_trades['PnL'] > 0).mean() * 100
                avg_win = actual_trades[actual_trades['PnL'] > 0]['PnL'].mean() if (actual_trades['PnL'] > 0).any() else 0
                avg_loss = actual_trades[actual_trades['PnL'] < 0]['PnL'].mean() if (actual_trades['PnL'] < 0).any() else 0
                total_trades = len(actual_trades)
            else:
                win_rate = 0
                avg_win = 0
                avg_loss = 0
                total_trades = 0

            # Check if blown up
            blown_up = 'BLOWN_UP' in results_df['Status'].values

            all_results.append({
                'Ticker': ticker,
                'Stock_Name': stock_info['name'],
                'Strategy': strategy_name,
                'Description': strategy_params['description'],
                'Final_Capital': final_capital,
                'Total_Return_%': total_return,
                'Annualized_Return_%': annualized_return,
                'Max_Drawdown_%': max_drawdown,
                'Win_Rate_%': win_rate,
                'Avg_Win': avg_win,
                'Avg_Loss': avg_loss,
                'Total_Trades': total_trades,
                'Years': years,
                'Blown_Up': 'YES' if blown_up else 'NO',
                'Over_100%': 'YES' if annualized_return >= 100 else 'NO'
            })

            # Save details
            detail_file = os.path.join(OUTPUT_FOLDER, f"{ticker}_{strategy_name}_details.csv")
            results_df.to_csv(detail_file, index=False)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

print(f"\n✅ Completed {len(all_results)} backtests")

# ============================================================================
# ANALYZE RESULTS
# ============================================================================
print("\n" + "="*80)
print("📊 ANALYZING RESULTS")
print("="*80)

results_df = pd.DataFrame(all_results)

# Save full results
full_file = os.path.join(OUTPUT_FOLDER, "aggressive_results_full.csv")
results_df.to_csv(full_file, index=False)

# Filter out blown up accounts
survived = results_df[results_df['Blown_Up'] == 'NO'].copy()
survived = survived.sort_values('Annualized_Return_%', ascending=False)

print("\n" + "="*80)
print("🏆 TOP 20 STRATEGIES (BY ANNUALIZED RETURN)")
print("="*80)

top_20 = survived.head(20)

print(f"\n{'Rank':<5} {'Ticker':<7} {'Strategy':<30} {'Annual %':<12} {'Total %':<12} {'Max DD':<10} {'Win %':<8} {'Trades':<8}")
print("-"*120)

for idx, (i, row) in enumerate(top_20.iterrows(), 1):
    marker = "🎯" if row['Annualized_Return_%'] >= 100 else ""
    print(f"{idx:<5} {row['Ticker']:<7} {row['Strategy']:<30} {marker}{row['Annualized_Return_%']:>10.1f}% "
          f"{row['Total_Return_%']:>10.1f}% {row['Max_Drawdown_%']:>8.1f}% "
          f"{row['Win_Rate_%']:>6.1f}% {int(row['Total_Trades']):>7}")

# ============================================================================
# STRATEGIES OVER 100% ANNUAL
# ============================================================================
print("\n" + "="*80)
print("🎯 STRATEGIES ACHIEVING 100%+ ANNUAL RETURNS")
print("="*80)

over_100 = survived[survived['Annualized_Return_%'] >= 100].sort_values('Annualized_Return_%', ascending=False)

if len(over_100) > 0:
    print(f"\n✅ Found {len(over_100)} strategies achieving 100%+ annual returns!\n")

    print(f"{'Ticker':<7} {'Strategy':<30} {'Annual %':<12} {'Total %':<12} {'Max DD':<10} {'Win %':<8} {'Blown Up':<10}")
    print("-"*120)

    for _, row in over_100.iterrows():
        print(f"{row['Ticker']:<7} {row['Strategy']:<30} {row['Annualized_Return_%']:>10.1f}% "
              f"{row['Total_Return_%']:>10.1f}% {row['Max_Drawdown_%']:>8.1f}% "
              f"{row['Win_Rate_%']:>6.1f}% {row['Blown_Up']:<10}")

    # Best overall
    best = over_100.iloc[0]
    print(f"\n🏆 WINNER: {best['Ticker']} with {best['Strategy']}")
    print(f"   Annual Return: {best['Annualized_Return_%']:.1f}%")
    print(f"   Total Return: {best['Total_Return_%']:.1f}%")
    print(f"   Max Drawdown: {best['Max_Drawdown_%']:.1f}%")
    print(f"   Win Rate: {best['Win_Rate_%']:.1f}%")
    print(f"   Total Trades: {int(best['Total_Trades'])}")

else:
    print("\n❌ No strategies achieved 100%+ annual returns")
    print(f"   Highest: {survived['Annualized_Return_%'].max():.1f}%")

# ============================================================================
# SURVIVAL RATE
# ============================================================================
print("\n" + "="*80)
print("💀 SURVIVAL ANALYSIS")
print("="*80)

blown_up_count = (results_df['Blown_Up'] == 'YES').sum()
survival_rate = (1 - blown_up_count / len(results_df)) * 100

print(f"\nTotal strategies tested: {len(results_df)}")
print(f"Blown up (lost 70%+): {blown_up_count}")
print(f"Survived: {len(results_df) - blown_up_count}")
print(f"Survival rate: {survival_rate:.1f}%")

# ============================================================================
# STRATEGY RANKINGS
# ============================================================================
print("\n" + "="*80)
print("📊 STRATEGY PERFORMANCE (AVERAGED, SURVIVED ONLY)")
print("="*80)

strategy_stats = survived.groupby('Strategy').agg({
    'Annualized_Return_%': ['mean', 'max'],
    'Max_Drawdown_%': 'mean',
    'Win_Rate_%': 'mean',
    'Over_100%': lambda x: (x == 'YES').sum()
}).round(2)

strategy_stats.columns = ['Avg_Annual_%', 'Max_Annual_%', 'Avg_DD_%', 'Avg_Win_%', 'Over_100_Count']
strategy_stats = strategy_stats.sort_values('Avg_Annual_%', ascending=False)

print(f"\n{'Strategy':<35} {'Avg Annual':<12} {'Best':<12} {'Avg DD':<10} {'Win %':<10} {'100%+':<8}")
print("-"*100)

for strategy, row in strategy_stats.iterrows():
    marker = "⭐" if row['Over_100_Count'] > 0 else ""
    print(f"{strategy:<35} {marker}{row['Avg_Annual_%']:>10.1f}% {row['Max_Annual_%']:>10.1f}% "
          f"{row['Avg_DD_%']:>8.1f}% {row['Avg_Win_%']:>8.1f}% {int(row['Over_100_Count']):>6}")

# ============================================================================
# VISUALIZATION
# ============================================================================
print("\n" + "="*80)
print("🎨 CREATING VISUALIZATIONS")
print("="*80)

fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(4, 3, hspace=0.35, wspace=0.3)

# 1. Top strategies
ax1 = fig.add_subplot(gs[0, :2])
top_15 = survived.nlargest(15, 'Annualized_Return_%')
labels = [f"{row['Ticker']}\n{row['Strategy'][:20]}" for _, row in top_15.iterrows()]
colors = ['gold' if r >= 100 else 'steelblue' for r in top_15['Annualized_Return_%']]
bars = ax1.barh(range(15), top_15['Annualized_Return_%'].values, color=colors, alpha=0.8)
ax1.set_yticks(range(15))
ax1.set_yticklabels(labels, fontsize=7)
ax1.set_xlabel('Annualized Return (%)', fontweight='bold', fontsize=10)
ax1.set_title('Top 15 Aggressive Strategies', fontsize=14, fontweight='bold')
ax1.axvline(x=100, color='red', linestyle='--', linewidth=2, label='100% Target')
ax1.grid(True, alpha=0.3, axis='x')
ax1.legend()
for i, (bar, val) in enumerate(zip(bars, top_15['Annualized_Return_%'].values)):
    ax1.text(val, i, f' {val:.0f}%', va='center', fontsize=8, fontweight='bold')

# 2. Strategy comparison
ax2 = fig.add_subplot(gs[0, 2])
strategy_avg = strategy_stats['Avg_Annual_%'].sort_values(ascending=True)
colors2 = ['gold' if v >= 50 else 'steelblue' for v in strategy_avg.values]
ax2.barh(range(len(strategy_avg)), strategy_avg.values, color=colors2, alpha=0.7)
ax2.set_yticks(range(len(strategy_avg)))
ax2.set_yticklabels([s[:25] for s in strategy_avg.index], fontsize=6)
ax2.set_xlabel('Avg Annual %', fontsize=8)
ax2.set_title('Strategy Comparison', fontsize=11, fontweight='bold')
ax2.axvline(x=100, color='red', linestyle='--', alpha=0.5)
ax2.grid(True, alpha=0.3, axis='x')

# 3. Risk vs Return
ax3 = fig.add_subplot(gs[1, :])
for strategy in survived['Strategy'].unique():
    subset = survived[survived['Strategy'] == strategy]
    ax3.scatter(abs(subset['Max_Drawdown_%']), subset['Annualized_Return_%'],
               alpha=0.6, s=80, label=strategy[:20])
ax3.set_xlabel('Max Drawdown (%) - Absolute', fontweight='bold')
ax3.set_ylabel('Annualized Return (%)', fontweight='bold')
ax3.set_title('Risk vs Return - Aggressive Strategies', fontsize=14, fontweight='bold')
ax3.axhline(y=100, color='red', linestyle='--', linewidth=2, alpha=0.7, label='100% Target')
ax3.grid(True, alpha=0.3)
ax3.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=6)

# 4. Win rate distribution
ax4 = fig.add_subplot(gs[2, 0])
ax4.hist(survived['Win_Rate_%'], bins=20, color='green', alpha=0.7, edgecolor='black')
ax4.set_xlabel('Win Rate (%)', fontweight='bold')
ax4.set_ylabel('Frequency', fontweight='bold')
ax4.set_title('Win Rate Distribution', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')
ax4.axvline(x=survived['Win_Rate_%'].mean(), color='red', linestyle='--', label=f"Mean: {survived['Win_Rate_%'].mean():.1f}%")
ax4.legend()

# 5. Return distribution
ax5 = fig.add_subplot(gs[2, 1])
ax5.hist(survived['Annualized_Return_%'], bins=25, color='purple', alpha=0.7, edgecolor='black')
ax5.set_xlabel('Annualized Return (%)', fontweight='bold')
ax5.set_ylabel('Frequency', fontweight='bold')
ax5.set_title('Return Distribution', fontsize=11, fontweight='bold')
ax5.axvline(x=100, color='red', linestyle='--', linewidth=2, label='100% Target')
ax5.axvline(x=survived['Annualized_Return_%'].mean(), color='orange', linestyle='--', label=f"Mean: {survived['Annualized_Return_%'].mean():.1f}%")
ax5.grid(True, alpha=0.3, axis='y')
ax5.legend()

# 6. Survival vs Blown Up
ax6 = fig.add_subplot(gs[2, 2])
survival_counts = results_df['Blown_Up'].value_counts()
colors_pie = ['#2ecc71', '#e74c3c']
labels_pie = [f'Survived\n({survival_counts.get("NO", 0)})', f'Blown Up\n({survival_counts.get("YES", 0)})']
ax6.pie([survival_counts.get('NO', 0), survival_counts.get('YES', 0)],
        labels=labels_pie, autopct='%1.1f%%', colors=colors_pie, startangle=90)
ax6.set_title('Survival Rate', fontsize=11, fontweight='bold')

# 7. Best stock performance
ax7 = fig.add_subplot(gs[3, :])
stock_best = survived.loc[survived.groupby('Ticker')['Annualized_Return_%'].idxmax()]
stock_best = stock_best.sort_values('Annualized_Return_%', ascending=True)
colors7 = ['gold' if v >= 100 else 'steelblue' for v in stock_best['Annualized_Return_%']]
bars7 = ax7.barh(range(len(stock_best)), stock_best['Annualized_Return_%'].values, color=colors7, alpha=0.8)
ax7.set_yticks(range(len(stock_best)))
ax7.set_yticklabels([f"{row['Ticker']} - {row['Strategy'][:20]}" for _, row in stock_best.iterrows()], fontsize=8)
ax7.set_xlabel('Annualized Return (%)', fontweight='bold')
ax7.set_title('Best Strategy per Stock', fontsize=12, fontweight='bold')
ax7.axvline(x=100, color='red', linestyle='--', linewidth=2, label='100% Target')
ax7.grid(True, alpha=0.3, axis='x')
ax7.legend()
for i, (bar, val) in enumerate(zip(bars7, stock_best['Annualized_Return_%'].values)):
    ax7.text(val, i, f' {val:.0f}%', va='center', fontsize=8, fontweight='bold')

plt.suptitle(f'AGGRESSIVE STRATEGIES ANALYSIS - TARGET: 100% ANNUAL RETURN',
             fontsize=16, fontweight='bold', y=0.998)

chart_file = os.path.join(OUTPUT_FOLDER, "aggressive_analysis.png")
plt.savefig(chart_file, dpi=150, bbox_inches='tight')
print(f"✅ Saved visualization to: aggressive_analysis.png")
plt.close()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ AGGRESSIVE BACKTEST COMPLETE!")
print("="*80)

print(f"\n📁 Results saved to: {OUTPUT_FOLDER}")
print(f"\n📊 Summary:")
print(f"   Total tests: {len(results_df)}")
print(f"   Survived: {len(survived)}")
print(f"   Blown up: {blown_up_count}")
print(f"   Survival rate: {survival_rate:.1f}%")
print(f"   Strategies over 100%: {len(over_100)}")
print(f"   Best return: {survived['Annualized_Return_%'].max():.1f}%")
print(f"   Average return (survived): {survived['Annualized_Return_%'].mean():.1f}%")

print("\n" + "="*80)
