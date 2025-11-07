#!/usr/bin/env python3
"""
COMPREHENSIVE CASH-COVERED PUT STRATEGY TESTER
Tests multiple strategies across multiple stocks
Saves results to C:\Trading\strategy_results
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# Configuration
OUTPUT_FOLDER = r"C:\Trading\strategy_results"
START_DATE = "2019-01-01"
END_DATE = "2024-11-01"
INITIAL_CAPITAL = 50000

# Stock Universe - Diverse selection
STOCKS = {
    # High Growth Tech
    'NVDA': 'NVIDIA',
    'TSLA': 'Tesla',
    'AMD': 'AMD',

    # Stable Blue Chips
    'KO': 'Coca-Cola',
    'JNJ': 'Johnson & Johnson',
    'PG': 'Procter & Gamble',

    # Financial
    'JPM': 'JPMorgan',
    'BAC': 'Bank of America',

    # Tech Large Cap
    'AAPL': 'Apple',
    'MSFT': 'Microsoft',

    # ETFs
    'SPY': 'S&P 500 ETF',
    'QQQ': 'Nasdaq ETF',
}

# Strategy Definitions
STRATEGIES = {
    'Conservative_5%_OTM': {
        'description': '5% Out-of-Money, 1 contract, low risk',
        'strike_offset': 0.95,  # 5% below current price
        'contracts': 1,
        'volatility_filter': None,
        'hold_period': 'weekly'
    },

    'Moderate_3%_OTM': {
        'description': '3% Out-of-Money, 1 contract',
        'strike_offset': 0.97,
        'contracts': 1,
        'volatility_filter': None,
        'hold_period': 'weekly'
    },

    'Aggressive_ATM': {
        'description': 'At-the-Money, higher premium',
        'strike_offset': 1.00,  # At current price
        'contracts': 1,
        'volatility_filter': None,
        'hold_period': 'weekly'
    },

    'Deep_OTM_10%': {
        'description': '10% Out-of-Money, safer but lower premium',
        'strike_offset': 0.90,
        'contracts': 1,
        'volatility_filter': None,
        'hold_period': 'weekly'
    },

    'VIX_Adaptive': {
        'description': 'Adjust position size based on volatility',
        'strike_offset': 0.95,
        'contracts': 'dynamic',  # Will be calculated based on VIX
        'volatility_filter': None,
        'hold_period': 'weekly'
    },

    'High_Vol_Only': {
        'description': 'Only trade when volatility > 30%, better premiums',
        'strike_offset': 0.95,
        'contracts': 1,
        'volatility_filter': 30,  # Only trade when VIX estimate > 30
        'hold_period': 'weekly'
    },

    'Monthly_5%_OTM': {
        'description': 'Monthly expiration, 5% OTM',
        'strike_offset': 0.95,
        'contracts': 1,
        'volatility_filter': None,
        'hold_period': 'monthly'
    },

    'Size_By_Price': {
        'description': 'More contracts for cheaper stocks',
        'strike_offset': 0.95,
        'contracts': 'by_price',  # More contracts when stock is cheaper
        'volatility_filter': None,
        'hold_period': 'weekly'
    },

    'Defensive_Only_Bear': {
        'description': 'Only trade when market is down (buying opportunity)',
        'strike_offset': 0.95,
        'contracts': 1,
        'volatility_filter': None,
        'hold_period': 'weekly',
        'market_filter': 'bear_only'  # Only trade after down weeks
    },
}

print("="*80)
print("🚀 COMPREHENSIVE PUT STRATEGY BACKTESTER")
print("="*80)
print(f"\nTesting {len(STRATEGIES)} strategies across {len(STOCKS)} stocks")
print(f"Time period: {START_DATE} to {END_DATE}")
print(f"Initial capital: ${INITIAL_CAPITAL:,}")

# Create output folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
print(f"Results will be saved to: {OUTPUT_FOLDER}")

# ============================================================================
# DOWNLOAD DATA FOR ALL STOCKS
# ============================================================================
print("\n" + "="*80)
print("📥 STEP 1: DOWNLOADING DATA")
print("="*80)

stock_data = {}
failed_stocks = []

for ticker, name in STOCKS.items():
    try:
        print(f"\nDownloading {ticker} ({name})...", end=" ")
        df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)

        if df.empty:
            print(f"❌ No data")
            failed_stocks.append(ticker)
            continue

        # Flatten column names if multi-level
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Convert to weekly
        df['Week'] = df.index.to_period('W')
        weekly = df.groupby('Week').agg({
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

        # Estimate VIX
        weekly['VIX_Estimate'] = weekly['Volatility_12w'] * 100 * 0.4 + 15
        weekly['VIX_Estimate'] = weekly['VIX_Estimate'].clip(lower=10, upper=80)

        # Market trend indicator
        weekly['SMA_20'] = weekly['Close'].rolling(window=20).mean()
        weekly['Trend'] = (weekly['Close'] > weekly['SMA_20']).astype(int)

        stock_data[ticker] = {
            'name': name,
            'data': weekly,
            'start_price': float(weekly['Close'].iloc[0]),
            'end_price': float(weekly['Close'].iloc[-1]),
            'weeks': len(weekly)
        }

        total_return = (stock_data[ticker]['end_price'] / stock_data[ticker]['start_price'] - 1) * 100
        print(f"✅ {len(weekly)} weeks | {total_return:+.1f}% return")

    except Exception as e:
        print(f"❌ Error: {e}")
        failed_stocks.append(ticker)

print(f"\n✅ Successfully downloaded {len(stock_data)} stocks")
if failed_stocks:
    print(f"❌ Failed: {', '.join(failed_stocks)}")

# ============================================================================
# BACKTEST ENGINE
# ============================================================================

def calculate_premium(stock_price, strike, volatility, hold_period='weekly'):
    """Simplified Black-Scholes approximation for put premium"""

    # Time to expiration
    if hold_period == 'weekly':
        tte = 7/365
    elif hold_period == 'monthly':
        tte = 30/365
    else:
        tte = 7/365

    # Moneyness
    moneyness = strike / stock_price

    # Intrinsic value
    intrinsic = max(strike - stock_price, 0)

    # Time value (simplified)
    time_value = stock_price * volatility * np.sqrt(tte) * 0.4

    # Put premium
    premium = intrinsic + time_value

    # Ensure minimum premium
    min_premium = stock_price * 0.005  # 0.5% minimum
    premium = max(premium, min_premium)

    return premium * 100  # Per contract (100 shares)

def run_backtest(ticker, stock_info, strategy_name, strategy_params):
    """Run backtest for one stock-strategy combination"""

    df = stock_info['data'].copy()
    capital = INITIAL_CAPITAL
    trades = []

    hold_period = strategy_params.get('hold_period', 'weekly')

    # Determine skip weeks for monthly
    skip = 4 if hold_period == 'monthly' else 1

    for i in range(1, len(df), skip):
        prev_week = df.iloc[i-1]
        current_week = df.iloc[i]

        prev_price = prev_week['Close']
        current_price = current_week['Close']
        vol = prev_week['Volatility_12w']
        vix = prev_week['VIX_Estimate']
        date = current_week['Date']

        # Apply volatility filter
        if strategy_params.get('volatility_filter'):
            if vix < strategy_params['volatility_filter']:
                # Skip this trade - volatility too low
                trades.append({
                    'Date': date,
                    'Stock_Price': current_price,
                    'Strike': None,
                    'Contracts': 0,
                    'Premium': 0,
                    'PnL': 0,
                    'Capital': capital,
                    'VIX': vix,
                    'Status': 'SKIPPED_LOW_VOL'
                })
                continue

        # Apply market filter
        if strategy_params.get('market_filter') == 'bear_only':
            # Only trade if previous week was down
            if prev_week['Returns'] > 0:
                trades.append({
                    'Date': date,
                    'Stock_Price': current_price,
                    'Strike': None,
                    'Contracts': 0,
                    'Premium': 0,
                    'PnL': 0,
                    'Capital': capital,
                    'VIX': vix,
                    'Status': 'SKIPPED_MARKET_UP'
                })
                continue

        # Calculate strike
        strike = prev_price * strategy_params['strike_offset']

        # Determine number of contracts
        contracts = strategy_params['contracts']
        if contracts == 'dynamic':
            # VIX-based sizing
            if vix < 15:
                contracts = 2
            elif vix < 25:
                contracts = 1
            else:
                contracts = 1  # Could go to 0 for very high VIX
        elif contracts == 'by_price':
            # More contracts for cheaper stocks
            if prev_price < 50:
                contracts = 3
            elif prev_price < 100:
                contracts = 2
            else:
                contracts = 1

        # Check if we have enough capital
        required_capital = strike * 100 * contracts
        if required_capital > capital:
            # Reduce contracts to fit capital
            contracts = int(capital / (strike * 100))
            if contracts == 0:
                trades.append({
                    'Date': date,
                    'Stock_Price': current_price,
                    'Strike': strike,
                    'Contracts': 0,
                    'Premium': 0,
                    'PnL': 0,
                    'Capital': capital,
                    'VIX': vix,
                    'Status': 'INSUFFICIENT_CAPITAL'
                })
                continue

        # Calculate premium
        premium_per_contract = calculate_premium(prev_price, strike, vol, hold_period)
        total_premium = premium_per_contract * contracts

        # Determine outcome
        if current_price >= strike:
            # Option expires OTM - keep premium
            pnl = total_premium
            status = "OTM_WIN"
        else:
            # Option assigned - buy stock at strike
            loss = (strike - current_price) * 100 * contracts
            pnl = total_premium - loss
            status = "ASSIGNED_LOSS"

        capital += pnl

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
# RUN ALL BACKTESTS
# ============================================================================
print("\n" + "="*80)
print("⚙️  STEP 2: RUNNING BACKTESTS")
print("="*80)

all_results = []
total_tests = len(stock_data) * len(STRATEGIES)
test_num = 0

for ticker, stock_info in stock_data.items():
    for strategy_name, strategy_params in STRATEGIES.items():
        test_num += 1
        print(f"\r[{test_num}/{total_tests}] Testing {ticker} with {strategy_name}...", end="")

        try:
            results_df = run_backtest(ticker, stock_info, strategy_name, strategy_params)

            if len(results_df) == 0:
                continue

            # Calculate metrics
            final_capital = results_df['Capital'].iloc[-1]
            total_return = (final_capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

            # Time period
            start_date = results_df['Date'].iloc[0]
            end_date = results_df['Date'].iloc[-1]
            years = (end_date - start_date).days / 365.25
            annualized_return = ((final_capital / INITIAL_CAPITAL) ** (1/years) - 1) * 100

            # Calculate drawdown
            results_df['Peak'] = results_df['Capital'].cummax()
            results_df['Drawdown_%'] = (results_df['Capital'] - results_df['Peak']) / results_df['Peak'] * 100
            max_drawdown = results_df['Drawdown_%'].min()

            # Win rate (only count actual trades)
            actual_trades = results_df[results_df['Contracts'] > 0]
            if len(actual_trades) > 0:
                win_rate = (actual_trades['PnL'] > 0).mean() * 100
                avg_pnl = actual_trades['PnL'].mean()
                total_trades = len(actual_trades)
            else:
                win_rate = 0
                avg_pnl = 0
                total_trades = 0

            # Buy and hold comparison
            buy_hold_return = (stock_info['end_price'] / stock_info['start_price'] - 1) * 100
            buy_hold_annualized = ((stock_info['end_price'] / stock_info['start_price']) ** (1/years) - 1) * 100

            all_results.append({
                'Ticker': ticker,
                'Stock_Name': stock_info['name'],
                'Strategy': strategy_name,
                'Strategy_Description': strategy_params['description'],
                'Final_Capital': final_capital,
                'Total_Return_%': total_return,
                'Annualized_Return_%': annualized_return,
                'Max_Drawdown_%': max_drawdown,
                'Win_Rate_%': win_rate,
                'Avg_Trade_PnL': avg_pnl,
                'Total_Trades': total_trades,
                'Years': years,
                'Buy_Hold_Total_%': buy_hold_return,
                'Buy_Hold_Annualized_%': buy_hold_annualized,
                'Outperform_BuyHold': 'YES' if annualized_return > buy_hold_annualized else 'NO'
            })

            # Save detailed results
            detail_file = os.path.join(OUTPUT_FOLDER, f"{ticker}_{strategy_name}_details.csv")
            results_df.to_csv(detail_file, index=False)

        except Exception as e:
            print(f"\n❌ Error testing {ticker} with {strategy_name}: {e}")

print(f"\n✅ Completed {len(all_results)} backtests")

# ============================================================================
# ANALYZE AND RANK RESULTS
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 3: ANALYZING RESULTS")
print("="*80)

results_df = pd.DataFrame(all_results)

# Save full results
full_results_file = os.path.join(OUTPUT_FOLDER, "all_results.csv")
results_df.to_csv(full_results_file, index=False)
print(f"\n💾 Saved full results to: all_results.csv")

# ============================================================================
# TOP STRATEGIES BY ANNUALIZED RETURN
# ============================================================================
print("\n" + "="*80)
print("🏆 TOP 20 STRATEGY-STOCK COMBINATIONS (BY ANNUALIZED RETURN)")
print("="*80)

top_20 = results_df.nlargest(20, 'Annualized_Return_%')

print(f"\n{'Rank':<5} {'Ticker':<7} {'Strategy':<25} {'Annual %':<10} {'Total %':<10} {'Max DD':<10} {'Win %':<8} {'Trades':<8}")
print("-"*105)

for idx, (i, row) in enumerate(top_20.iterrows(), 1):
    print(f"{idx:<5} {row['Ticker']:<7} {row['Strategy']:<25} {row['Annualized_Return_%']:>8.1f}% "
          f"{row['Total_Return_%']:>8.1f}% {row['Max_Drawdown_%']:>8.1f}% "
          f"{row['Win_Rate_%']:>6.1f}% {int(row['Total_Trades']):>7}")

# ============================================================================
# BEST STRATEGY PER STOCK
# ============================================================================
print("\n" + "="*80)
print("📈 BEST STRATEGY FOR EACH STOCK")
print("="*80)

best_per_stock = results_df.loc[results_df.groupby('Ticker')['Annualized_Return_%'].idxmax()]
best_per_stock = best_per_stock.sort_values('Annualized_Return_%', ascending=False)

print(f"\n{'Ticker':<7} {'Stock':<20} {'Best Strategy':<25} {'Annual %':<10} {'vs B&H':<12}")
print("-"*90)

for _, row in best_per_stock.iterrows():
    vs_bh = row['Annualized_Return_%'] - row['Buy_Hold_Annualized_%']
    print(f"{row['Ticker']:<7} {row['Stock_Name']:<20} {row['Strategy']:<25} "
          f"{row['Annualized_Return_%']:>8.1f}% {vs_bh:>+9.1f}%")

# ============================================================================
# BEST OVERALL STRATEGY
# ============================================================================
print("\n" + "="*80)
print("🎯 OVERALL STRATEGY PERFORMANCE (AVERAGED ACROSS ALL STOCKS)")
print("="*80)

strategy_avg = results_df.groupby('Strategy').agg({
    'Annualized_Return_%': 'mean',
    'Max_Drawdown_%': 'mean',
    'Win_Rate_%': 'mean',
    'Total_Trades': 'sum'
}).round(2)

strategy_avg['Outperform_Count'] = results_df.groupby('Strategy')['Outperform_BuyHold'].apply(lambda x: (x == 'YES').sum())
strategy_avg = strategy_avg.sort_values('Annualized_Return_%', ascending=False)

print(f"\n{'Strategy':<30} {'Avg Annual %':<15} {'Avg Max DD':<12} {'Avg Win %':<12} {'Beat B&H':<10}")
print("-"*90)

for strategy, row in strategy_avg.iterrows():
    print(f"{strategy:<30} {row['Annualized_Return_%']:>12.1f}% {row['Max_Drawdown_%']:>10.1f}% "
          f"{row['Win_Rate_%']:>10.1f}% {int(row['Outperform_Count'])}/{len(stock_data)}")

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("\n" + "="*80)
print("🎨 STEP 4: CREATING VISUALIZATIONS")
print("="*80)

# Create comprehensive comparison chart
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# 1. Top 10 combinations bar chart
ax1 = fig.add_subplot(gs[0, :2])
top_10 = results_df.nlargest(10, 'Annualized_Return_%')
labels = [f"{row['Ticker']}\n{row['Strategy'][:15]}" for _, row in top_10.iterrows()]
colors = plt.cm.viridis(np.linspace(0, 1, 10))
bars = ax1.barh(range(10), top_10['Annualized_Return_%'].values, color=colors)
ax1.set_yticks(range(10))
ax1.set_yticklabels(labels, fontsize=8)
ax1.set_xlabel('Annualized Return (%)', fontweight='bold')
ax1.set_title('Top 10 Strategy-Stock Combinations', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='x')
for i, (bar, val) in enumerate(zip(bars, top_10['Annualized_Return_%'].values)):
    ax1.text(val, i, f' {val:.1f}%', va='center', fontsize=9)

# 2. Strategy comparison
ax2 = fig.add_subplot(gs[0, 2])
strategy_means = strategy_avg['Annualized_Return_%'].sort_values(ascending=True)
ax2.barh(range(len(strategy_means)), strategy_means.values, color='steelblue', alpha=0.7)
ax2.set_yticks(range(len(strategy_means)))
ax2.set_yticklabels([s[:20] for s in strategy_means.index], fontsize=7)
ax2.set_xlabel('Avg Annual %', fontsize=9)
ax2.set_title('Strategy Comparison\n(Averaged)', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

# 3. Risk vs Return scatter
ax3 = fig.add_subplot(gs[1, :])
for strategy in STRATEGIES.keys():
    subset = results_df[results_df['Strategy'] == strategy]
    ax3.scatter(subset['Max_Drawdown_%'], subset['Annualized_Return_%'],
               alpha=0.6, s=100, label=strategy[:15])
ax3.set_xlabel('Max Drawdown (%)', fontweight='bold')
ax3.set_ylabel('Annualized Return (%)', fontweight='bold')
ax3.set_title('Risk vs Return: All Strategy-Stock Combinations', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax3.axhline(y=0, color='red', linestyle='--', alpha=0.5)

# 4. Win rate distribution
ax4 = fig.add_subplot(gs[2, 0])
ax4.hist(results_df['Win_Rate_%'], bins=20, color='green', alpha=0.7, edgecolor='black')
ax4.set_xlabel('Win Rate (%)', fontweight='bold')
ax4.set_ylabel('Frequency', fontweight='bold')
ax4.set_title('Win Rate Distribution', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')

# 5. Put strategy vs Buy & Hold
ax5 = fig.add_subplot(gs[2, 1])
beat_count = results_df['Outperform_BuyHold'].value_counts()
colors_pie = ['#2ecc71', '#e74c3c']
ax5.pie(beat_count.values, labels=['Lost to B&H', 'Beat B&H'], autopct='%1.1f%%',
        colors=colors_pie, startangle=90)
ax5.set_title('Put Strategy vs Buy & Hold', fontsize=11, fontweight='bold')

# 6. Stock performance comparison
ax6 = fig.add_subplot(gs[2, 2])
stock_perf = results_df.groupby('Ticker').agg({
    'Annualized_Return_%': 'max',
    'Buy_Hold_Annualized_%': 'first'
}).sort_values('Buy_Hold_Annualized_%', ascending=True)

x = np.arange(len(stock_perf))
width = 0.35
ax6.barh(x - width/2, stock_perf['Annualized_Return_%'], width, label='Best Put Strategy', alpha=0.8)
ax6.barh(x + width/2, stock_perf['Buy_Hold_Annualized_%'], width, label='Buy & Hold', alpha=0.8)
ax6.set_yticks(x)
ax6.set_yticklabels(stock_perf.index, fontsize=8)
ax6.set_xlabel('Annualized %', fontsize=9)
ax6.set_title('Best Strategy vs B&H\nby Stock', fontsize=10, fontweight='bold')
ax6.legend(fontsize=8)
ax6.grid(True, alpha=0.3, axis='x')

plt.suptitle('COMPREHENSIVE PUT STRATEGY ANALYSIS', fontsize=16, fontweight='bold', y=0.995)

chart_file = os.path.join(OUTPUT_FOLDER, "comprehensive_analysis.png")
plt.savefig(chart_file, dpi=150, bbox_inches='tight')
print(f"✅ Saved visualization to: comprehensive_analysis.png")
plt.close()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)

print(f"\n📁 Results folder: {OUTPUT_FOLDER}")
print(f"\n📊 Summary:")
print(f"   Total backtests run: {len(results_df)}")
print(f"   Strategies tested: {len(STRATEGIES)}")
print(f"   Stocks tested: {len(stock_data)}")
print(f"   Best annualized return: {results_df['Annualized_Return_%'].max():.1f}%")
print(f"   Worst annualized return: {results_df['Annualized_Return_%'].min():.1f}%")
print(f"   Times beat buy & hold: {(results_df['Outperform_BuyHold'] == 'YES').sum()}/{len(results_df)}")

print("\n🎯 Key Findings:")
best_overall = results_df.loc[results_df['Annualized_Return_%'].idxmax()]
print(f"   Best combination: {best_overall['Ticker']} with {best_overall['Strategy']}")
print(f"   Return: {best_overall['Annualized_Return_%']:.1f}% annualized ({best_overall['Total_Return_%']:.1f}% total)")

best_strategy_name = strategy_avg['Annualized_Return_%'].idxmax()
print(f"\n   Best overall strategy: {best_strategy_name}")
print(f"   Average return: {strategy_avg.loc[best_strategy_name, 'Annualized_Return_%']:.1f}%")
print(f"   Beat buy & hold: {int(strategy_avg.loc[best_strategy_name, 'Outperform_Count'])}/{len(stock_data)} times")

print("\n" + "="*80)
