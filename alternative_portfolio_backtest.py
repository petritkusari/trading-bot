#!/usr/bin/env python3
"""
Alternative Portfolio Backtest
Compares original portfolio (VXX, COIN, TSLA, QQQ) with alternatives (VXX, RIOT, PLTR, IWM)
Uses tiered stop-loss: VXX 30%, stocks 15%
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
        if current.weekday() == 4:  # Friday
            fridays.append(current)
        current += timedelta(days=1)
    return fridays

def calculate_atm_strike(price):
    """Calculate ATM strike price based on stock price"""
    if price < 25:
        return round(price * 2) / 2
    elif price < 100:
        return round(price)
    elif price < 200:
        return round(price / 5) * 5
    else:
        return round(price / 10) * 10

def estimate_premium(price, iv, days=7):
    """Estimate ATM PUT premium using simplified Black-Scholes"""
    return price * iv * np.sqrt(days / 365)

def backtest_portfolio(tickers, allocations, stop_losses, start_date, end_date, initial_capital=50000):
    """
    Backtest the portfolio with weekly ATM puts

    Parameters:
    - tickers: list of ticker symbols
    - allocations: dict of allocation percentages
    - stop_losses: dict of stop-loss percentages
    - start_date, end_date: date range
    - initial_capital: starting capital
    """

    print(f"\n{'='*70}")
    print(f"BACKTESTING: {', '.join(tickers)}")
    print(f"Period: {start_date.date()} to {end_date.date()}")
    print(f"{'='*70}\n")

    # Download historical data
    print("Downloading price data...")
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date - timedelta(days=30),
                           end=end_date + timedelta(days=7), progress=False)
            if not df.empty:
                data[ticker] = df['Close']
                print(f"  {ticker}: {len(df)} days")
            else:
                print(f"  {ticker}: NO DATA - Will skip")
        except Exception as e:
            print(f"  {ticker}: ERROR - {e}")

    if len(data) < len(tickers):
        print(f"\nWARNING: Only got data for {len(data)}/{len(tickers)} tickers")

    # Get weekly Fridays
    fridays = get_weekly_fridays(start_date, end_date)
    print(f"\nTotal weeks to test: {len(fridays)}")

    # Implied volatility estimates
    iv_estimates = {
        'VXX': 0.80, 'VIXY': 0.80, 'VXXB': 0.80,
        'COIN': 0.80, 'RIOT': 0.80,
        'TSLA': 0.60, 'PLTR': 0.60,
        'QQQ': 0.25, 'IWM': 0.25, 'SPY': 0.20
    }

    # Track results
    results = []
    capital = initial_capital
    equity_curve = [initial_capital]
    max_capital = initial_capital
    max_drawdown = 0

    weeks_tested = 0
    weeks_skipped = 0

    for i, friday in enumerate(fridays[:-1]):  # Skip last Friday (no next week)
        next_friday = fridays[i + 1]

        # Get prices for entry (Monday/Tuesday area)
        entry_date = friday - timedelta(days=3)  # Tuesday before Friday

        week_positions = []
        week_valid = True

        # Build positions for this week
        for ticker in tickers:
            if ticker not in data:
                week_valid = False
                break

            try:
                # Entry price
                entry_series = data[ticker][data[ticker].index >= entry_date]
                if len(entry_series) == 0:
                    week_valid = False
                    break
                entry_price = float(entry_series.iloc[0])

                # Exit price
                exit_series = data[ticker][data[ticker].index >= next_friday]
                if len(exit_series) == 0:
                    week_valid = False
                    break
                exit_price = float(exit_series.iloc[0])

                # Calculate position
                strike = calculate_atm_strike(entry_price)
                iv = iv_estimates.get(ticker, 0.50)
                premium = estimate_premium(entry_price, iv)

                # Position sizing
                allocation = allocations.get(ticker, 0)
                capital_allocated = capital * allocation
                contracts = int(capital_allocated / (strike * 100))
                contracts = max(1, contracts)  # At least 1 contract

                # P&L calculation
                premium_collected = premium * contracts * 100

                # Check if assigned (price below strike)
                if exit_price < strike:
                    # Assigned - loss on stock
                    loss_per_share = strike - exit_price
                    assignment_loss = loss_per_share * contracts * 100
                    net_pnl = premium_collected - assignment_loss
                else:
                    # Not assigned - keep premium
                    net_pnl = premium_collected

                # Check stop-loss
                price_move = (exit_price - entry_price) / entry_price
                stop_loss = stop_losses.get(ticker, 0.15)
                stop_hit = price_move < -stop_loss

                if stop_hit:
                    # Stop triggered - cap loss at stop level
                    max_loss = capital_allocated * stop_loss
                    net_pnl = min(net_pnl, -max_loss + premium_collected)

                week_positions.append({
                    'ticker': ticker,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'strike': strike,
                    'premium': premium,
                    'contracts': contracts,
                    'pnl': net_pnl,
                    'stop_hit': stop_hit
                })

            except (IndexError, KeyError):
                week_valid = False
                break

        if not week_valid:
            weeks_skipped += 1
            continue

        # Calculate week P&L
        week_pnl = sum(p['pnl'] for p in week_positions)
        capital += week_pnl

        # Track metrics
        if capital > max_capital:
            max_capital = capital

        drawdown = (max_capital - capital) / max_capital
        if drawdown > max_drawdown:
            max_drawdown = drawdown

        equity_curve.append(capital)

        results.append({
            'date': next_friday,
            'week_pnl': week_pnl,
            'capital': capital,
            'return_pct': week_pnl / (capital - week_pnl),
            'positions': week_positions
        })

        weeks_tested += 1

        # Progress
        if weeks_tested % 50 == 0:
            print(f"  Processed {weeks_tested} weeks...")

    print(f"\nCompleted: {weeks_tested} weeks tested, {weeks_skipped} weeks skipped")

    # Calculate performance metrics
    if not results:
        print("ERROR: No valid weeks to analyze!")
        return None

    df_results = pd.DataFrame(results)

    total_return = (capital - initial_capital) / initial_capital
    years = len(results) / 52
    annualized_return = (1 + total_return) ** (1 / years) - 1

    winning_weeks = len(df_results[df_results['week_pnl'] > 0])
    win_rate = winning_weeks / len(results)

    avg_weekly_return = df_results['return_pct'].mean()

    # Count stop hits
    total_stops = sum(1 for week in results for pos in week['positions'] if pos['stop_hit'])

    return {
        'tickers': tickers,
        'results': df_results,
        'initial_capital': initial_capital,
        'final_capital': capital,
        'total_return': total_return,
        'annualized_return': annualized_return,
        'years': years,
        'weeks': len(results),
        'win_rate': win_rate,
        'avg_weekly_return': avg_weekly_return,
        'max_drawdown': max_drawdown,
        'equity_curve': equity_curve,
        'stop_hits': total_stops,
    }

def print_results(name, stats):
    """Print backtest results"""
    if not stats:
        return

    print(f"\n{'='*70}")
    print(f"{name}")
    print(f"{'='*70}")
    print(f"Portfolio: {', '.join(stats['tickers'])}")
    print(f"Period: {stats['years']:.1f} years ({stats['weeks']} weeks)")
    print(f"\nPERFORMANCE:")
    print(f"  Initial Capital:      ${stats['initial_capital']:,.0f}")
    print(f"  Final Capital:        ${stats['final_capital']:,.0f}")
    print(f"  Total Return:         {stats['total_return']*100:.1f}%")
    print(f"  Annualized Return:    {stats['annualized_return']*100:.1f}%")
    print(f"  Avg Weekly Return:    {stats['avg_weekly_return']*100:.2f}%")
    print(f"\nRISK METRICS:")
    print(f"  Max Drawdown:         {stats['max_drawdown']*100:.1f}%")
    print(f"  Win Rate:             {stats['win_rate']*100:.1f}%")
    print(f"  Stop-Loss Triggers:   {stats['stop_hits']}")
    print(f"\nBest Week:  ${stats['results']['week_pnl'].max():,.0f}")
    print(f"Worst Week: ${stats['results']['week_pnl'].min():,.0f}")

def compare_portfolios(original, alternative):
    """Compare two portfolio results"""
    print(f"\n{'='*70}")
    print("COMPARISON: ORIGINAL vs ALTERNATIVE")
    print(f"{'='*70}")
    print(f"\n{'Metric':<30} {'Original':<20} {'Alternative':<20} {'Difference'}")
    print(f"{'-'*80}")

    metrics = [
        ('Annualized Return',
         f"{original['annualized_return']*100:.1f}%",
         f"{alternative['annualized_return']*100:.1f}%",
         f"{(alternative['annualized_return'] - original['annualized_return'])*100:+.1f}%"),

        ('Max Drawdown',
         f"{original['max_drawdown']*100:.1f}%",
         f"{alternative['max_drawdown']*100:.1f}%",
         f"{(alternative['max_drawdown'] - original['max_drawdown'])*100:+.1f}%"),

        ('Win Rate',
         f"{original['win_rate']*100:.1f}%",
         f"{alternative['win_rate']*100:.1f}%",
         f"{(alternative['win_rate'] - original['win_rate'])*100:+.1f}%"),

        ('Avg Weekly Return',
         f"{original['avg_weekly_return']*100:.2f}%",
         f"{alternative['avg_weekly_return']*100:.2f}%",
         f"{(alternative['avg_weekly_return'] - original['avg_weekly_return'])*100:+.2f}%"),

        ('Final Capital',
         f"${original['final_capital']:,.0f}",
         f"${alternative['final_capital']:,.0f}",
         f"${alternative['final_capital'] - original['final_capital']:+,.0f}"),
    ]

    for metric, orig, alt, diff in metrics:
        print(f"{metric:<30} {orig:<20} {alt:<20} {diff}")

    print(f"\n{'='*70}")
    print("VERDICT:")

    # Performance comparison
    ret_diff = (alternative['annualized_return'] - original['annualized_return']) * 100
    dd_diff = (alternative['max_drawdown'] - original['max_drawdown']) * 100

    if abs(ret_diff) < 50:  # Within 50% points
        if alternative['max_drawdown'] < original['max_drawdown']:
            print("  ALTERNATIVE IS BETTER - Similar returns with lower risk")
        elif abs(dd_diff) < 5:  # Within 5% points
            print("  ALTERNATIVE IS COMPARABLE - Similar risk/return profile")
        else:
            print("  ALTERNATIVE IS SIMILAR - Slight differences in risk")
    elif ret_diff > 0:
        print("  ALTERNATIVE IS BETTER - Higher returns")
    else:
        print("  ORIGINAL IS BETTER - Higher returns")

    print(f"{'='*70}")

if __name__ == "__main__":
    # Date range
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2024, 10, 31)

    # ORIGINAL PORTFOLIO
    original_tickers = ['VXX', 'COIN', 'TSLA', 'QQQ']
    original_allocations = {
        'VXX': 0.25,
        'COIN': 0.25,
        'TSLA': 0.25,
        'QQQ': 0.15
    }
    original_stops = {
        'VXX': 0.30,
        'COIN': 0.15,
        'TSLA': 0.15,
        'QQQ': 0.15
    }

    # ALTERNATIVE PORTFOLIO
    alt_tickers = ['VXX', 'RIOT', 'PLTR', 'IWM']
    alt_allocations = {
        'VXX': 0.25,
        'RIOT': 0.25,
        'PLTR': 0.25,
        'IWM': 0.15
    }
    alt_stops = {
        'VXX': 0.30,
        'RIOT': 0.15,
        'PLTR': 0.15,
        'IWM': 0.15
    }

    print("STRATEGY ALTERNATIVE PORTFOLIO BACKTEST")
    print("Testing if cheaper alternatives maintain performance")

    # Run backtests
    print("\n" + "="*70)
    print("PHASE 1: Testing ORIGINAL Portfolio")
    print("="*70)
    original_results = backtest_portfolio(
        original_tickers,
        original_allocations,
        original_stops,
        start_date,
        end_date
    )

    print("\n" + "="*70)
    print("PHASE 2: Testing ALTERNATIVE Portfolio")
    print("="*70)
    alternative_results = backtest_portfolio(
        alt_tickers,
        alt_allocations,
        alt_stops,
        start_date,
        end_date
    )

    # Print results
    if original_results:
        print_results("ORIGINAL PORTFOLIO RESULTS", original_results)

    if alternative_results:
        print_results("ALTERNATIVE PORTFOLIO RESULTS", alternative_results)

    # Compare
    if original_results and alternative_results:
        compare_portfolios(original_results, alternative_results)

        # Save detailed results
        with open("C:\\Trading\\alternative_backtest_results.txt", "w") as f:
            f.write("ALTERNATIVE PORTFOLIO BACKTEST RESULTS\n")
            f.write("="*70 + "\n\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Period: {start_date.date()} to {end_date.date()}\n\n")

            f.write("ORIGINAL PORTFOLIO:\n")
            f.write(f"  Tickers: {', '.join(original_tickers)}\n")
            f.write(f"  Annualized Return: {original_results['annualized_return']*100:.1f}%\n")
            f.write(f"  Max Drawdown: {original_results['max_drawdown']*100:.1f}%\n")
            f.write(f"  Win Rate: {original_results['win_rate']*100:.1f}%\n\n")

            f.write("ALTERNATIVE PORTFOLIO:\n")
            f.write(f"  Tickers: {', '.join(alt_tickers)}\n")
            f.write(f"  Annualized Return: {alternative_results['annualized_return']*100:.1f}%\n")
            f.write(f"  Max Drawdown: {alternative_results['max_drawdown']*100:.1f}%\n")
            f.write(f"  Win Rate: {alternative_results['win_rate']*100:.1f}%\n\n")

            f.write("VERDICT:\n")
            ret_diff = (alternative_results['annualized_return'] - original_results['annualized_return']) * 100
            f.write(f"  Return Difference: {ret_diff:+.1f}% points\n")
            f.write(f"  Risk Difference: {(alternative_results['max_drawdown'] - original_results['max_drawdown'])*100:+.1f}% points\n")

        print(f"\nDetailed results saved to: C:\\Trading\\alternative_backtest_results.txt")
