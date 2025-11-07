#!/usr/bin/env python3
"""
Alternative Portfolio Backtest - REALISTIC VERSION
Uses fixed $50K capital (no aggressive compounding) for clearer comparison
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_weekly_fridays(start_date, end_date):
    """Generate list of Friday dates for weekly options"""
    fridays = []
    current = start_date
    while current <= end_date:
        if current.weekday() == 4:
            fridays.append(current)
        current += timedelta(days=1)
    return fridays

def calculate_atm_strike(price):
    """Calculate ATM strike price"""
    if price < 25:
        return round(price * 2) / 2
    elif price < 100:
        return round(price)
    elif price < 200:
        return round(price / 5) * 5
    else:
        return round(price / 10) * 10

def estimate_premium(price, iv, days=7):
    """Estimate ATM PUT premium"""
    return price * iv * np.sqrt(days / 365)

def backtest_realistic(tickers, allocations, stop_losses, start_date, end_date, capital=50000):
    """
    Realistic backtest with FIXED capital allocation
    """

    print(f"\nBacktesting: {', '.join(tickers)}")
    print(f"Period: {start_date.date()} to {end_date.date()}")

    # Download data
    print("Downloading data...")
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date - timedelta(days=30),
                           end=end_date + timedelta(days=7), progress=False)
            if not df.empty:
                data[ticker] = df['Close']
                print(f"  {ticker}: OK")
        except:
            print(f"  {ticker}: ERROR")

    # IV estimates
    iv_estimates = {
        'VXX': 0.80, 'COIN': 0.80, 'RIOT': 0.80,
        'TSLA': 0.60, 'PLTR': 0.60,
        'QQQ': 0.25, 'IWM': 0.25
    }

    # Get Fridays
    fridays = get_weekly_fridays(start_date, end_date)

    results = []
    cumulative_pnl = 0
    max_capital = capital
    max_drawdown = 0

    for i, friday in enumerate(fridays[:-1]):
        next_friday = fridays[i + 1]
        entry_date = friday - timedelta(days=3)

        week_pnl = 0
        week_positions = []
        week_valid = True

        for ticker in tickers:
            if ticker not in data:
                week_valid = False
                break

            try:
                # Get prices
                entry_series = data[ticker][data[ticker].index >= entry_date]
                exit_series = data[ticker][data[ticker].index >= next_friday]

                if len(entry_series) == 0 or len(exit_series) == 0:
                    week_valid = False
                    break

                entry_price = float(entry_series.iloc[0])
                exit_price = float(exit_series.iloc[0])

                # Position sizing - FIXED based on initial capital
                allocation = allocations.get(ticker, 0)
                allocated_capital = capital * allocation
                strike = calculate_atm_strike(entry_price)
                contracts = max(1, int(allocated_capital / (strike * 100)))

                # Calculate P&L
                iv = iv_estimates.get(ticker, 0.50)
                premium = estimate_premium(entry_price, iv)
                premium_collected = premium * contracts * 100

                # Assignment check
                if exit_price < strike:
                    loss = (strike - exit_price) * contracts * 100
                    net_pnl = premium_collected - loss
                else:
                    net_pnl = premium_collected

                # Stop-loss check
                price_drop = (entry_price - exit_price) / entry_price
                stop = stop_losses.get(ticker, 0.15)

                if price_drop > stop:
                    # Stop triggered
                    max_loss = allocated_capital * stop
                    net_pnl = max(-max_loss + premium_collected, net_pnl)

                week_pnl += net_pnl

                week_positions.append({
                    'ticker': ticker,
                    'entry': entry_price,
                    'exit': exit_price,
                    'strike': strike,
                    'contracts': contracts,
                    'pnl': net_pnl
                })

            except (IndexError, KeyError):
                week_valid = False
                break

        if not week_valid:
            continue

        cumulative_pnl += week_pnl
        current_capital = capital + cumulative_pnl

        # Track drawdown
        if current_capital > max_capital:
            max_capital = current_capital

        dd = (max_capital - current_capital) / max_capital
        if dd > max_drawdown:
            max_drawdown = dd

        results.append({
            'date': next_friday,
            'week_pnl': week_pnl,
            'cumulative_pnl': cumulative_pnl,
            'capital': current_capital,
            'positions': week_positions
        })

    # Calculate metrics
    df = pd.DataFrame(results)
    total_return = cumulative_pnl / capital
    years = len(results) / 52
    annualized = (1 + total_return) ** (1 / years) - 1
    win_rate = len(df[df['week_pnl'] > 0]) / len(df)
    avg_weekly = df['week_pnl'].mean()
    avg_weekly_pct = (avg_weekly / capital) * 100

    return {
        'tickers': tickers,
        'weeks': len(results),
        'years': years,
        'initial_capital': capital,
        'final_capital': capital + cumulative_pnl,
        'total_pnl': cumulative_pnl,
        'total_return_pct': total_return * 100,
        'annualized_pct': annualized * 100,
        'max_drawdown_pct': max_drawdown * 100,
        'win_rate_pct': win_rate * 100,
        'avg_weekly_pnl': avg_weekly,
        'avg_weekly_pct': avg_weekly_pct,
        'best_week': df['week_pnl'].max(),
        'worst_week': df['week_pnl'].min(),
        'results': df
    }

def print_comparison(orig, alt):
    """Print side-by-side comparison"""

    print(f"\n{'='*80}")
    print(f"{'BACKTEST COMPARISON: ORIGINAL vs ALTERNATIVE':^80}")
    print(f"{'='*80}\n")

    print(f"{'PORTFOLIO':<25} {'ORIGINAL':<25} {'ALTERNATIVE':<25}")
    print(f"{'-'*80}")
    print(f"{'Tickers:':<25} {', '.join(orig['tickers']):<25} {', '.join(alt['tickers']):<25}")
    print()

    print(f"{'PERFORMANCE METRICS':<25} {'ORIGINAL':<25} {'ALTERNATIVE':<25} {'DIFFERENCE'}")
    print(f"{'-'*80}")

    metrics = [
        ('Period (years)', f"{orig['years']:.1f}", f"{alt['years']:.1f}", ""),
        ('Weeks tested', f"{orig['weeks']}", f"{alt['weeks']}", ""),
        ('', '', '', ''),
        ('Initial Capital', f"${orig['initial_capital']:,.0f}", f"${alt['initial_capital']:,.0f}", ""),
        ('Final Capital', f"${orig['final_capital']:,.0f}", f"${alt['final_capital']:,.0f}",
         f"${alt['final_capital'] - orig['final_capital']:+,.0f}"),
        ('Total P&L', f"${orig['total_pnl']:,.0f}", f"${alt['total_pnl']:,.0f}",
         f"${alt['total_pnl'] - orig['total_pnl']:+,.0f}"),
        ('', '', '', ''),
        ('Total Return', f"{orig['total_return_pct']:.1f}%", f"{alt['total_return_pct']:.1f}%",
         f"{alt['total_return_pct'] - orig['total_return_pct']:+.1f}%"),
        ('Annualized Return', f"{orig['annualized_pct']:.1f}%", f"{alt['annualized_pct']:.1f}%",
         f"{alt['annualized_pct'] - orig['annualized_pct']:+.1f}%"),
        ('Avg Weekly Return', f"{orig['avg_weekly_pct']:.2f}%", f"{alt['avg_weekly_pct']:.2f}%",
         f"{alt['avg_weekly_pct'] - orig['avg_weekly_pct']:+.2f}%"),
        ('', '', '', ''),
        ('Max Drawdown', f"{orig['max_drawdown_pct']:.1f}%", f"{alt['max_drawdown_pct']:.1f}%",
         f"{alt['max_drawdown_pct'] - orig['max_drawdown_pct']:+.1f}%"),
        ('Win Rate', f"{orig['win_rate_pct']:.1f}%", f"{alt['win_rate_pct']:.1f}%",
         f"{alt['win_rate_pct'] - orig['win_rate_pct']:+.1f}%"),
        ('', '', '', ''),
        ('Best Week', f"${orig['best_week']:,.0f}", f"${alt['best_week']:,.0f}",
         f"${alt['best_week'] - orig['best_week']:+,.0f}"),
        ('Worst Week', f"${orig['worst_week']:,.0f}", f"${alt['worst_week']:,.0f}",
         f"${alt['worst_week'] - orig['worst_week']:+,.0f}"),
    ]

    for row in metrics:
        if len(row) == 4:
            label, o, a, d = row
            print(f"{label:<25} {o:<25} {a:<25} {d}")
        else:
            print()

    print(f"\n{'='*80}")
    print("ANALYSIS:")
    print(f"{'='*80}\n")

    # Performance comparison
    ret_diff = alt['annualized_pct'] - orig['annualized_pct']
    dd_diff = alt['max_drawdown_pct'] - orig['max_drawdown_pct']
    wr_diff = alt['win_rate_pct'] - orig['win_rate_pct']

    if ret_diff >= -20 and dd_diff <= 5:
        print("[VERDICT] ALTERNATIVE IS ACCEPTABLE")
        print(f"  - Similar annualized return ({ret_diff:+.1f}% difference)")
        print(f"  - Comparable risk profile (DD: {dd_diff:+.1f}%)")
        print(f"  - Win rate: {alt['win_rate_pct']:.1f}% vs {orig['win_rate_pct']:.1f}%")
        print("\n  >> The cheaper alternatives can replace the originals")

    elif ret_diff < -50:
        print("[VERDICT] ALTERNATIVE IS SIGNIFICANTLY WORSE")
        print(f"  - Much lower returns ({ret_diff:.1f}% difference)")
        print(f"  - Higher risk (DD: {dd_diff:+.1f}%)")
        print(f"  - Lower win rate ({wr_diff:+.1f}%)")
        print("\n  >> The alternatives DO NOT adequately replace the originals")

    else:
        print("[VERDICT] ALTERNATIVE IS SOMEWHAT WEAKER")
        print(f"  - Lower returns ({ret_diff:+.1f}%)")
        print(f"  - Risk: {dd_diff:+.1f}% {('higher' if dd_diff > 0 else 'lower')}")
        print(f"  - Win rate: {wr_diff:+.1f}% {('lower' if wr_diff < 0 else 'higher')}")
        print("\n  >> Consider if the tradeoff is acceptable for your capital constraints")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    start = datetime(2019, 1, 1)
    end = datetime(2024, 10, 31)

    print("="*80)
    print("REALISTIC PORTFOLIO COMPARISON")
    print("Fixed $50K capital allocation (no aggressive compounding)")
    print("="*80)

    # Original
    print("\n[1/2] Testing ORIGINAL portfolio...")
    original = backtest_realistic(
        ['VXX', 'COIN', 'TSLA', 'QQQ'],
        {'VXX': 0.25, 'COIN': 0.25, 'TSLA': 0.25, 'QQQ': 0.15},
        {'VXX': 0.30, 'COIN': 0.15, 'TSLA': 0.15, 'QQQ': 0.15},
        start, end
    )

    # Alternative
    print("\n[2/2] Testing ALTERNATIVE portfolio...")
    alternative = backtest_realistic(
        ['VXX', 'RIOT', 'PLTR', 'IWM'],
        {'VXX': 0.25, 'RIOT': 0.25, 'PLTR': 0.25, 'IWM': 0.15},
        {'VXX': 0.30, 'RIOT': 0.15, 'PLTR': 0.15, 'IWM': 0.15},
        start, end
    )

    # Compare
    print_comparison(original, alternative)

    # Save
    with open("C:\\Trading\\alternative_realistic_results.txt", "w") as f:
        f.write("REALISTIC PORTFOLIO COMPARISON\n")
        f.write("="*80 + "\n\n")
        f.write(f"Test date: {datetime.now()}\n")
        f.write(f"Period: {start.date()} to {end.date()}\n\n")

        f.write("ORIGINAL PORTFOLIO (VXX, COIN, TSLA, QQQ):\n")
        f.write(f"  Annualized Return: {original['annualized_pct']:.1f}%\n")
        f.write(f"  Max Drawdown: {original['max_drawdown_pct']:.1f}%\n")
        f.write(f"  Win Rate: {original['win_rate_pct']:.1f}%\n")
        f.write(f"  Final Capital: ${original['final_capital']:,.0f}\n\n")

        f.write("ALTERNATIVE PORTFOLIO (VXX, RIOT, PLTR, IWM):\n")
        f.write(f"  Annualized Return: {alternative['annualized_pct']:.1f}%\n")
        f.write(f"  Max Drawdown: {alternative['max_drawdown_pct']:.1f}%\n")
        f.write(f"  Win Rate: {alternative['win_rate_pct']:.1f}%\n")
        f.write(f"  Final Capital: ${alternative['final_capital']:,.0f}\n\n")

        f.write("DIFFERENCE:\n")
        f.write(f"  Return: {alternative['annualized_pct'] - original['annualized_pct']:+.1f}% points\n")
        f.write(f"  Drawdown: {alternative['max_drawdown_pct'] - original['max_drawdown_pct']:+.1f}% points\n")
        f.write(f"  Win Rate: {alternative['win_rate_pct'] - original['win_rate_pct']:+.1f}% points\n")

    print(f"Results saved to: C:\\Trading\\alternative_realistic_results.txt")
