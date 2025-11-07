#!/usr/bin/env python3
"""
TIERED STOP-LOSS BACKTEST
Tests the user's brilliant idea: Different stop-losses for VXX vs stocks
- VXX: 30% stop-loss (needs time for crash protection)
- Stocks: 15% or 10% stop-loss (cut losers early)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
INITIAL_CAPITAL = 50000
INITIAL_DATE = '2019-01-01'
END_DATE = '2024-11-01'

# Portfolio Allocation
PORTFOLIO = {
    'VXX': {
        'allocation': 0.25,  # 25% of capital
        'stop_loss': 0.30,   # 30% stop on VXX position
        'strike_offset': 0.75,  # Sell 75% ATM (more conservative for VXX)
    },
    'COIN': {
        'allocation': 0.25,
        'stop_loss': 0.15,   # Will test 15% and 10%
        'strike_offset': 1.00,  # ATM
    },
    'TSLA': {
        'allocation': 0.25,
        'stop_loss': 0.15,
        'strike_offset': 1.00,
    },
    'QQQ': {
        'allocation': 0.15,
        'stop_loss': 0.15,
        'strike_offset': 1.00,
    },
    # 10% cash reserve
}

# Premium estimation (weekly IV-based)
PREMIUM_MULTIPLIERS = {
    'VXX': 0.08,  # 8% weekly premium (high volatility)
    'COIN': 0.06,  # 6% weekly premium
    'TSLA': 0.05,  # 5% weekly premium
    'QQQ': 0.03,  # 3% weekly premium (safer)
}

# Transaction costs
COST_PER_CONTRACT = 1.30  # $0.65 per side
SLIPPAGE_PCT = 0.05  # 5% of premium


def download_price_data(tickers, start, end):
    """Download historical price data"""
    print(f"\nDownloading data for: {', '.join(tickers)}")
    data = {}

    for ticker in tickers:
        print(f"  Fetching {ticker}...")
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
            if df.empty:
                print(f"  WARNING: No data for {ticker}")
                continue
            df = df[['Close']].copy()
            df.columns = [ticker]
            data[ticker] = df
        except Exception as e:
            print(f"  ERROR fetching {ticker}: {e}")
            continue

    # Combine all into one dataframe
    if not data:
        raise ValueError("No data downloaded!")

    combined = pd.concat(data.values(), axis=1)
    combined = combined.fillna(method='ffill')  # Forward fill missing data

    print(f"  Downloaded {len(combined)} days of data")
    return combined


def estimate_weekly_premium(current_price, strike_offset, premium_mult):
    """
    Estimate weekly put premium based on strike and volatility
    This is a simplified Black-Scholes approximation
    """
    strike = current_price * strike_offset

    # Premium is roughly:
    # - Intrinsic value (if ITM)
    # - + Time value (volatility-based)

    intrinsic = max(0, strike - current_price)
    time_value = current_price * premium_mult

    total_premium = intrinsic + time_value

    # Account for transaction costs
    net_premium = total_premium * (1 - SLIPPAGE_PCT) - (COST_PER_CONTRACT / 100)

    return max(net_premium, 0)


def simulate_put_outcome(entry_price, strike, exit_price):
    """
    Simulate P&L from selling a cash-secured put

    Returns:
    - profit: Total profit/loss
    - assigned: Whether we were assigned (bought stock)
    """
    if exit_price >= strike:
        # Put expires worthless, we keep premium
        return 'expired', 0
    else:
        # We're assigned - buy stock at strike
        # Loss = (Strike - Current Price) per share
        assignment_loss = (strike - exit_price) * 100  # per contract
        return 'assigned', assignment_loss


def backtest_tiered_stops(stock_stop_loss=0.15, verbose=True):
    """
    Run backtest with tiered stop-losses

    Args:
        stock_stop_loss: Stop-loss % for stocks (0.10 or 0.15)
        verbose: Print progress

    Returns:
        results dict with performance metrics
    """

    if verbose:
        print(f"\n{'='*70}")
        print(f"TIERED STOP-LOSS BACKTEST")
        print(f"VXX Stop: 30% | Stock Stop: {stock_stop_loss*100:.0f}%")
        print(f"{'='*70}")

    # Update stock stop-losses
    for ticker in ['COIN', 'TSLA', 'QQQ']:
        if ticker in PORTFOLIO:
            PORTFOLIO[ticker]['stop_loss'] = stock_stop_loss

    # Download data
    tickers = list(PORTFOLIO.keys())
    prices = download_price_data(tickers, INITIAL_DATE, END_DATE)

    # Resample to weekly (Friday closes)
    weekly_prices = prices.resample('W-FRI').last()

    if verbose:
        print(f"\n{len(weekly_prices)} weeks of trading data")

    # Initialize tracking
    capital = INITIAL_CAPITAL
    position_capital = {ticker: INITIAL_CAPITAL * PORTFOLIO[ticker]['allocation']
                       for ticker in tickers}
    position_pnl = {ticker: 0.0 for ticker in tickers}
    active_positions = {ticker: True for ticker in tickers}  # Track if position still active

    trade_log = []
    equity_curve = [INITIAL_CAPITAL]
    weeks_traded = 0
    total_trades = 0
    winning_trades = 0

    max_capital = INITIAL_CAPITAL
    max_drawdown = 0
    stopped_out = {ticker: False for ticker in tickers}

    # Simulate weekly trading
    for i in range(1, len(weekly_prices)):
        week_start = weekly_prices.index[i-1]
        week_end = weekly_prices.index[i]

        week_return = 0
        trades_this_week = 0

        for ticker in tickers:
            # Skip if position is stopped out
            if not active_positions[ticker]:
                continue

            # Get prices
            entry_price = weekly_prices.loc[week_start, ticker]
            exit_price = weekly_prices.loc[week_end, ticker]

            if pd.isna(entry_price) or pd.isna(exit_price):
                continue

            # Calculate position size
            pos_capital = position_capital[ticker]
            if pos_capital <= 0:
                continue

            # Calculate strike and premium
            strike_offset = PORTFOLIO[ticker]['strike_offset']
            strike = entry_price * strike_offset
            premium_mult = PREMIUM_MULTIPLIERS[ticker]

            weekly_premium = estimate_weekly_premium(entry_price, strike_offset, premium_mult)

            # Determine number of contracts
            contracts = int(pos_capital / (strike * 100))
            if contracts == 0:
                continue

            # Total premium collected
            premium_collected = weekly_premium * entry_price * 100 * contracts

            # Simulate outcome
            outcome, assignment_loss = simulate_put_outcome(entry_price, strike, exit_price)

            if outcome == 'expired':
                # Win: keep premium
                profit = premium_collected
                winning_trades += 1
            else:
                # Assigned: premium - loss
                profit = premium_collected - assignment_loss * contracts

            # Update position P&L
            position_pnl[ticker] += profit
            position_capital[ticker] += profit
            capital += profit

            # Track trade
            trade_log.append({
                'week': week_end,
                'ticker': ticker,
                'entry_price': entry_price,
                'strike': strike,
                'exit_price': exit_price,
                'contracts': contracts,
                'premium': premium_collected,
                'outcome': outcome,
                'profit': profit,
                'position_pnl': position_pnl[ticker],
                'position_capital': position_capital[ticker],
            })

            total_trades += 1
            trades_this_week += 1

            # CHECK POSITION-LEVEL STOP-LOSS
            initial_pos_capital = INITIAL_CAPITAL * PORTFOLIO[ticker]['allocation']
            position_loss_pct = (initial_pos_capital - position_capital[ticker]) / initial_pos_capital
            position_stop = PORTFOLIO[ticker]['stop_loss']

            if position_loss_pct >= position_stop:
                if verbose:
                    print(f"\n!!! {ticker} STOPPED OUT at {position_loss_pct*100:.1f}% loss !!!")
                    print(f"    Week: {week_end.date()}")
                    print(f"    Position capital: ${position_capital[ticker]:,.0f} (started ${initial_pos_capital:,.0f})")

                # Stop this position
                active_positions[ticker] = False
                stopped_out[ticker] = True

                # Add remaining capital to cash
                # (in reality, this position allocation becomes cash)

        # Track equity
        equity_curve.append(capital)
        weeks_traded += 1

        # Calculate drawdown
        if capital > max_capital:
            max_capital = capital
        current_dd = (max_capital - capital) / max_capital
        if current_dd > max_drawdown:
            max_drawdown = current_dd

    # Calculate metrics
    total_return = (capital - INITIAL_CAPITAL) / INITIAL_CAPITAL
    years = len(weekly_prices) / 52
    annualized_return = ((capital / INITIAL_CAPITAL) ** (1/years)) - 1
    win_rate = winning_trades / total_trades if total_trades > 0 else 0

    results = {
        'stock_stop': stock_stop_loss,
        'final_capital': capital,
        'total_return_pct': total_return * 100,
        'annualized_return_pct': annualized_return * 100,
        'max_drawdown_pct': max_drawdown * 100,
        'win_rate_pct': win_rate * 100,
        'total_trades': total_trades,
        'weeks_traded': weeks_traded,
        'years': years,
        'stopped_out': stopped_out,
        'position_pnl': position_pnl,
        'final_position_capital': position_capital,
        'equity_curve': equity_curve,
        'trade_log': trade_log,
    }

    return results


def compare_scenarios():
    """Compare traditional 30% vs tiered stop-losses"""

    print("\n" + "="*70)
    print("COMPARING STOP-LOSS STRATEGIES")
    print("="*70)

    scenarios = []

    # Scenario 1: Stock stops at 15%
    print("\n\n### SCENARIO 1: VXX 30% Stop, Stocks 15% Stop ###")
    results_15 = backtest_tiered_stops(stock_stop_loss=0.15, verbose=True)
    scenarios.append(('VXX 30% / Stocks 15%', results_15))

    # Scenario 2: Stock stops at 10%
    print("\n\n### SCENARIO 2: VXX 30% Stop, Stocks 10% Stop ###")
    results_10 = backtest_tiered_stops(stock_stop_loss=0.10, verbose=True)
    scenarios.append(('VXX 30% / Stocks 10%', results_10))

    # Generate comparison report
    print("\n\n" + "="*70)
    print("COMPARISON REPORT")
    print("="*70)

    comparison = pd.DataFrame([
        {
            'Strategy': name,
            'Final Capital': f"${res['final_capital']:,.0f}",
            'Total Return %': f"{res['total_return_pct']:.1f}%",
            'Annualized %': f"{res['annualized_return_pct']:.1f}%",
            'Max Drawdown %': f"{res['max_drawdown_pct']:.1f}%",
            'Win Rate %': f"{res['win_rate_pct']:.1f}%",
            'Trades': res['total_trades'],
            'VXX Stopped': 'Yes' if res['stopped_out']['VXX'] else 'No',
            'COIN Stopped': 'Yes' if res['stopped_out']['COIN'] else 'No',
            'TSLA Stopped': 'Yes' if res['stopped_out']['TSLA'] else 'No',
            'QQQ Stopped': 'Yes' if res['stopped_out']['QQQ'] else 'No',
        }
        for name, res in scenarios
    ])

    print("\n" + comparison.to_string(index=False))

    # Detailed position P&L
    print("\n\n" + "="*70)
    print("POSITION-LEVEL P&L BREAKDOWN")
    print("="*70)

    for name, res in scenarios:
        print(f"\n{name}:")
        print("-" * 50)
        for ticker in ['VXX', 'COIN', 'TSLA', 'QQQ']:
            initial = INITIAL_CAPITAL * PORTFOLIO[ticker]['allocation']
            final = res['final_position_capital'][ticker]
            pnl = res['position_pnl'][ticker]
            stopped = "STOPPED OUT" if res['stopped_out'][ticker] else "Active"

            print(f"  {ticker:6s}: ${initial:>8,.0f} -> ${final:>8,.0f}  "
                  f"(P&L: ${pnl:>8,.0f})  [{stopped}]")

    # Save detailed results
    print("\n\nSaving detailed results...")
    for name, res in scenarios:
        filename = name.replace(' ', '_').replace('/', '_')
        trade_df = pd.DataFrame(res['trade_log'])
        trade_df.to_csv(f"C:\\Trading\\{filename}_trades.csv", index=False)
        print(f"  Saved: {filename}_trades.csv")

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)

    return scenarios


if __name__ == "__main__":
    results = compare_scenarios()
