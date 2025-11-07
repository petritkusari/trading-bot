#!/usr/bin/env python3
"""
RISK-HEDGED PORTFOLIO ANALYZER
Finds portfolio combinations that maximize returns while minimizing catastrophic risk
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

OUTPUT_FOLDER = r"C:\Trading\risk_hedged_analysis"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("="*100)
print("RISK-HEDGED PORTFOLIO ANALYZER")
print("="*100)

# Load results
df = pd.read_csv(r"C:\Trading\ultimate_results\ultimate_results.csv")

# Focus on full period and safe strategies
full_period = df[df['Period'] == 'Full_2019_2024'].copy()
safe = full_period[full_period['Safe_100%'] == True].copy()

print(f"\nAnalyzing {len(safe)} safe strategies from 2019-2024 period...")

# ============================================================================
# ANALYZE MARKET CORRELATIONS
# ============================================================================
print("\n" + "="*100)
print("STEP 1: ANALYZING MARKET CORRELATIONS")
print("="*100)

# Get top strategies per market
top_per_market = safe.groupby('Ticker').apply(
    lambda x: x.nlargest(3, 'Annualized_%')
).reset_index(drop=True)

print(f"\nTop markets for safe 100%+ strategies:")
market_stats = safe.groupby('Ticker').agg({
    'Annualized_%': ['mean', 'max', 'count'],
    'Max_DD_%': 'mean'
}).round(1)
market_stats.columns = ['Avg_Annual', 'Max_Annual', 'Count', 'Avg_DD']
market_stats = market_stats.sort_values('Avg_Annual', ascending=False)

print(f"\n{'Market':<8} {'Type':<12} {'Avg Annual%':<14} {'Max Annual%':<14} {'Strategies':<12} {'Avg DD%':<10}")
print("-"*90)

market_types = {}
for ticker in market_stats.index:
    mtype = full_period[full_period['Ticker'] == ticker]['Market_Type'].iloc[0]
    market_types[ticker] = mtype
    row = market_stats.loc[ticker]
    print(f"{ticker:<8} {mtype:<12} {row['Avg_Annual']:>12.1f}% {row['Max_Annual']:>12.1f}% "
          f"{int(row['Count']):>10} {row['Avg_DD']:>8.1f}%")

# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================
print("\n" + "="*100)
print("STEP 2: CORRELATION BETWEEN MARKETS")
print("="*100)

# Download and analyze correlations
print("\nAnalyzing historical price correlations...")
import yfinance as yf

tickers_to_analyze = list(market_stats.head(10).index)
correlations = {}

try:
    # Download data
    data = {}
    for ticker in tickers_to_analyze:
        try:
            df_price = yf.download(ticker, start='2019-01-01', end='2024-11-01', progress=False)
            if not df_price.empty:
                if isinstance(df_price.columns, pd.MultiIndex):
                    df_price.columns = df_price.columns.get_level_values(0)
                data[ticker] = df_price['Close'].pct_change()
        except:
            pass

    if len(data) > 1:
        # Create correlation matrix
        returns_df = pd.DataFrame(data)
        corr_matrix = returns_df.corr()

        print("\nCorrelation Matrix (Daily Returns):")
        print("Values: -1 = perfect negative, 0 = uncorrelated, +1 = perfect positive")
        print("\n" + str(corr_matrix.round(2)))

        # Find pairs with low/negative correlation
        print("\nBEST HEDGE PAIRS (Low/Negative Correlation):")
        pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                ticker1 = corr_matrix.columns[i]
                ticker2 = corr_matrix.columns[j]
                corr = corr_matrix.iloc[i, j]
                pairs.append((ticker1, ticker2, corr))

        pairs.sort(key=lambda x: x[2])
        print("\nTop 10 hedge pairs:")
        for ticker1, ticker2, corr in pairs[:10]:
            print(f"  {ticker1:<6} vs {ticker2:<6}: {corr:>6.2f}")

except Exception as e:
    print(f"Could not compute correlations: {e}")

# ============================================================================
# PORTFOLIO CONSTRUCTION - MULTIPLE LAYERS OF PROTECTION
# ============================================================================
print("\n" + "="*100)
print("STEP 3: CONSTRUCTING RISK-HEDGED PORTFOLIOS")
print("="*100)

# Define portfolio strategies with different risk profiles
PORTFOLIOS = {
    'Ultra_Safe_100': {
        'description': 'Target 100% with maximum safety - diversified, stop-losses, hedged',
        'allocations': [
            {'market': 'VXX', 'pct': 0.20, 'strategy': 'Daily_50pct_OTM5', 'notes': 'Volatility hedge'},
            {'market': 'QQQ', 'pct': 0.15, 'strategy': 'Weekly_All_In_95', 'notes': 'Stable index'},
            {'market': 'SPY', 'pct': 0.15, 'strategy': 'Weekly_All_In_95', 'notes': 'Broad market'},
            {'market': 'GLD', 'pct': 0.10, 'strategy': 'Weekly_All_In_95', 'notes': 'Safe haven'},
            {'market': 'TSLA', 'pct': 0.10, 'strategy': 'Weekly_75pct_ATM_SL25', 'notes': 'Growth with SL'},
            {'market': 'COIN', 'pct': 0.10, 'strategy': 'Weekly_All_In_95', 'notes': 'Crypto exposure'},
            {'market': 'Cash', 'pct': 0.20, 'strategy': 'Reserve', 'notes': 'Emergency fund'},
        ],
        'rules': {
            'max_loss_per_position': 0.05,  # 5% max per position
            'portfolio_stop_loss': 0.20,  # Exit all if down 20%
            'rebalance': 'monthly',
        }
    },

    'Balanced_150': {
        'description': 'Target 150% with good safety - some leverage, hedged',
        'allocations': [
            {'market': 'VXX', 'pct': 0.25, 'strategy': 'Daily_75pct_ATM', 'notes': 'Vol hedge + returns'},
            {'market': 'COIN', 'pct': 0.20, 'strategy': 'Weekly_All_In_95', 'notes': 'High returns'},
            {'market': 'TSLA', 'pct': 0.15, 'strategy': 'Weekly_All_In_95', 'notes': 'Growth'},
            {'market': 'QQQ', 'pct': 0.15, 'strategy': 'Weekly_All_In_97', 'notes': 'Index core'},
            {'market': 'MSTR', 'pct': 0.10, 'strategy': 'Weekly_All_In_95', 'notes': 'Bitcoin proxy'},
            {'market': 'Cash', 'pct': 0.15, 'strategy': 'Reserve', 'notes': 'Buffer'},
        ],
        'rules': {
            'max_loss_per_position': 0.08,
            'portfolio_stop_loss': 0.25,
            'rebalance': 'monthly',
        }
    },

    'Market_Neutral': {
        'description': 'Hedged with VXX - profits in up and down markets',
        'allocations': [
            {'market': 'VXX', 'pct': 0.40, 'strategy': 'Weekly_All_In_ATM', 'notes': 'Short vol = long crashes'},
            {'market': 'TSLA', 'pct': 0.20, 'strategy': 'Weekly_All_In_95', 'notes': 'Growth position'},
            {'market': 'QQQ', 'pct': 0.20, 'strategy': 'Weekly_All_In_95', 'notes': 'Index position'},
            {'market': 'Cash', 'pct': 0.20, 'strategy': 'Reserve', 'notes': 'Safety buffer'},
        ],
        'rules': {
            'max_loss_per_position': 0.10,
            'portfolio_stop_loss': 0.30,
            'rebalance': 'weekly',
        }
    },

    'Crash_Proof': {
        'description': 'Designed to profit from market crashes',
        'allocations': [
            {'market': 'VXX', 'pct': 0.50, 'strategy': 'Weekly_Momentum_AllIn', 'notes': 'Massive crash profits'},
            {'market': 'GLD', 'pct': 0.15, 'strategy': 'Weekly_All_In_95', 'notes': 'Safe haven'},
            {'market': 'UUP', 'pct': 0.10, 'strategy': 'Weekly_All_In_95', 'notes': 'USD strength'},
            {'market': 'QQQ', 'pct': 0.10, 'strategy': 'Weekly_All_In_95', 'notes': 'Small market exposure'},
            {'market': 'Cash', 'pct': 0.15, 'strategy': 'Reserve', 'notes': 'Dry powder'},
        ],
        'rules': {
            'max_loss_per_position': 0.12,
            'portfolio_stop_loss': 0.35,
            'rebalance': 'weekly',
        }
    },
}

# Calculate expected returns for each portfolio
print("\nPORTFOLIO ANALYSIS:")
print("="*100)

portfolio_results = []

for port_name, port_config in PORTFOLIOS.items():
    print(f"\n{port_name}: {port_config['description']}")
    print("-"*90)

    expected_return = 0
    max_loss = 0
    weighted_dd = 0
    allocations_detail = []

    for alloc in port_config['allocations']:
        market = alloc['market']
        pct = alloc['pct']
        strat = alloc['strategy']

        if market == 'Cash':
            allocations_detail.append({
                'Market': 'Cash',
                'Allocation': f"{pct*100:.0f}%",
                'Strategy': 'Reserve',
                'Expected_Return': '0%',
                'Max_DD': '0%',
                'Notes': alloc['notes']
            })
            continue

        # Find this strategy's performance
        matching = safe[(safe['Ticker'] == market) & (safe['Strategy'] == strat)]

        if len(matching) > 0:
            perf = matching.iloc[0]
            ret = perf['Annualized_%'] / 100
            dd = perf['Max_DD_%']

            contribution = pct * ret
            expected_return += contribution
            weighted_dd += pct * abs(dd)

            allocations_detail.append({
                'Market': market,
                'Allocation': f"{pct*100:.0f}%",
                'Strategy': strat[:20],
                'Expected_Return': f"{ret*100:.0f}%",
                'Max_DD': f"{dd:.1f}%",
                'Contribution': f"{contribution*100:.0f}%",
                'Notes': alloc['notes']
            })

    # Calculate max portfolio loss
    max_portfolio_loss = port_config['rules']['portfolio_stop_loss'] * 100

    # Display
    print(f"\n{'Market':<8} {'Alloc':<8} {'Strategy':<22} {'Return':<10} {'MaxDD':<10} {'Contrib':<10} {'Notes':<20}")
    print("-"*110)
    for detail in allocations_detail:
        print(f"{detail['Market']:<8} {detail['Allocation']:<8} {detail['Strategy']:<22} "
              f"{detail['Expected_Return']:<10} {detail.get('Max_DD', 'N/A'):<10} "
              f"{detail.get('Contribution', 'N/A'):<10} {detail['Notes']:<20}")

    print(f"\nPORTFOLIO METRICS:")
    print(f"  Expected Annual Return: {expected_return*100:.1f}%")
    print(f"  Weighted Average Drawdown: {weighted_dd:.1f}%")
    print(f"  Maximum Portfolio Loss (stop-loss): {max_portfolio_loss:.0f}%")
    print(f"  Risk-Adjusted Return (Return/MaxLoss): {expected_return*100/max_portfolio_loss:.2f}")

    portfolio_results.append({
        'Portfolio': port_name,
        'Expected_Return_%': expected_return * 100,
        'Weighted_DD_%': weighted_dd,
        'Max_Loss_%': max_portfolio_loss,
        'Risk_Adj_Return': expected_return * 100 / max_portfolio_loss,
    })

# ============================================================================
# WORST CASE ANALYSIS
# ============================================================================
print("\n" + "="*100)
print("STEP 4: WORST-CASE SCENARIO ANALYSIS")
print("="*100)

print("\nWhat happens if individual positions go to ZERO?")
print("-"*90)

for port_name, port_config in PORTFOLIOS.items():
    print(f"\n{port_name}:")

    for alloc in port_config['allocations']:
        market = alloc['market']
        pct = alloc['pct']

        if market == 'Cash':
            continue

        # If this position goes to zero
        position_value = pct * 50000
        max_loss_this_position = position_value

        print(f"  {market} goes to $0: Lose ${max_loss_this_position:,.0f} ({pct*100:.0f}% of portfolio)")

    # Portfolio stop-loss kicks in before total loss
    stop_loss_pct = port_config['rules']['portfolio_stop_loss']
    max_portfolio_loss_dollars = 50000 * stop_loss_pct

    print(f"\n  PORTFOLIO STOP-LOSS: Exits at ${max_portfolio_loss_dollars:,.0f} loss ({stop_loss_pct*100:.0f}%)")
    print(f"  Remaining capital: ${50000 - max_portfolio_loss_dollars:,.0f}")

# ============================================================================
# STRESS TEST - COVID CRASH PERFORMANCE
# ============================================================================
print("\n" + "="*100)
print("STEP 5: STRESS TEST - COVID CRASH (Feb-Apr 2020)")
print("="*100)

covid_data = df[df['Period'] == 'COVID_Crash_2020'].copy()

print("\nHow would each portfolio perform during COVID crash?")
print("-"*90)

for port_name, port_config in PORTFOLIOS.items():
    print(f"\n{port_name}:")

    total_covid_return = 0

    for alloc in port_config['allocations']:
        market = alloc['market']
        pct = alloc['pct']
        strat = alloc['strategy']

        if market == 'Cash':
            continue

        # Find COVID performance
        matching = covid_data[(covid_data['Ticker'] == market) & (covid_data['Strategy'] == strat)]

        if len(matching) > 0:
            perf = matching.iloc[0]
            ret = perf['Annualized_%'] / 100
            contribution = pct * ret
            total_covid_return += contribution

            print(f"  {market} ({strat[:15]}): {ret*100:>8.1f}% × {pct*100:.0f}% = {contribution*100:>8.1f}% contribution")
        else:
            print(f"  {market}: No data")

    print(f"\n  TOTAL COVID PERIOD RETURN: {total_covid_return*100:.1f}% (annualized)")
    print(f"  Starting $50K would become: ${50000 * (1 + total_covid_return):,.0f}")

# ============================================================================
# RECOMMENDATIONS
# ============================================================================
print("\n" + "="*100)
print("FINAL RECOMMENDATIONS")
print("="*100)

results_df = pd.DataFrame(portfolio_results)
results_df = results_df.sort_values('Risk_Adj_Return', ascending=False)

print("\nPortfolio Rankings by Risk-Adjusted Return:")
print(f"\n{'Portfolio':<20} {'Expected Return':<16} {'Max Loss':<12} {'Risk-Adj':<10}")
print("-"*70)

for _, row in results_df.iterrows():
    print(f"{row['Portfolio']:<20} {row['Expected_Return_%']:>14.1f}% "
          f"{row['Max_Loss_%']:>10.0f}% {row['Risk_Adj_Return']:>8.2f}")

# Save results
results_file = os.path.join(OUTPUT_FOLDER, "portfolio_analysis.csv")
results_df.to_csv(results_file, index=False)

print(f"\n💾 Saved analysis to: {results_file}")

print("\n" + "="*100)
print("ANALYSIS COMPLETE")
print("="*100)
