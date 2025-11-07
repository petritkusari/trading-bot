#!/usr/bin/env python3
"""
TIERED STOP-LOSS BACKTEST (FIXED VERSION)
Simple, accurate simulation of tiered stop-losses
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Configuration
INITIAL_CAPITAL = 50000
START_DATE = '2019-01-01'
END_DATE = '2024-11-01'

# Portfolio allocation
ALLOCATIONS = {
    'VXX': 0.25,   # 25%
    'COIN': 0.25,  # 25%
    'TSLA': 0.25,  # 25%
    'QQQ': 0.15,   # 15%
    # 10% cash
}

# Weekly premium rates (simplified - based on typical IV)
WEEKLY_PREMIUM_RATES = {
    'VXX': 0.06,   # 6% weekly (very high IV)
    'COIN': 0.05,  # 5% weekly
    'TSLA': 0.04,  # 4% weekly
    'QQQ': 0.025,  # 2.5% weekly
}

# Assignment probability (% chance put expires ITM)
ASSIGNMENT_PROB = {
    'VXX': 0.35,   # 35% chance
    'COIN': 0.30,  # 30% chance
    'TSLA': 0.25,  # 25% chance
    'QQQ': 0.15,   # 15% chance
}

def download_data():
    """Download price data"""
    print("Downloading price data...")
    tickers = list(ALLOCATIONS.keys())

    all_data = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)
            if not df.empty:
                df_close = df[['Close']].copy()
                df_close.columns = [ticker]
                all_data.append(df_close)
        except Exception as e:
            print(f"  Warning: Could not download {ticker}: {e}")

    if not all_data:
        raise ValueError("No data downloaded!")

    prices = pd.concat(all_data, axis=1)
    weekly = prices.resample('W-FRI').last().fillna(method='ffill')
    print(f"  {len(weekly)} weeks of data")
    return weekly


def simulate_trade(current_price, premium_rate, assignment_prob):
    """
    Simulate one week of selling cash-secured put

    Returns: (profit_pct, assigned)
    - profit_pct: % return on capital for this trade
    - assigned: whether we got assigned
    """
    # Collect premium
    premium_pct = premium_rate

    # Check if assigned (simplified: random based on probability)
    if np.random.random() < assignment_prob:
        # Assigned - stock dropped
        # Assume average loss of 5-10% on assignment
        stock_drop_pct = np.random.uniform(0.05, 0.10)
        loss_pct = stock_drop_pct

        net_return = premium_pct - loss_pct
        return net_return, True
    else:
        # Not assigned - keep premium
        return premium_pct, False


def backtest(vxx_stop=0.30, stock_stop=0.15, verbose=True):
    """
    Run backtest with tiered stops

    Args:
        vxx_stop: Stop-loss for VXX position (default 30%)
        stock_stop: Stop-loss for other positions (default 15%)
    """

    if verbose:
        print(f"\n{'='*60}")
        print(f"Backtest: VXX {vxx_stop*100:.0f}% Stop | Stocks {stock_stop*100:.0f}% Stop")
        print(f"{'='*60}")

    # Download data
    prices = download_data()

    # Initialize positions
    positions = {}
    for ticker, allocation in ALLOCATIONS.items():
        stop_loss = vxx_stop if ticker == 'VXX' else stock_stop
        positions[ticker] = {
            'initial_capital': INITIAL_CAPITAL * allocation,
            'current_capital': INITIAL_CAPITAL * allocation,
            'total_pnl': 0,
            'stop_loss': stop_loss,
            'active': True,
            'stopped_week': None,
            'trades': 0,
            'wins': 0,
        }

    # Track overall portfolio
    weeks_traded = 0
    total_portfolio_value = INITIAL_CAPITAL

    equity_curve = [INITIAL_CAPITAL]
    max_equity = INITIAL_CAPITAL
    max_drawdown = 0

    # Trade week by week
    for week_idx in range(1, len(prices)):
        week_date = prices.index[week_idx]
        week_pnl = 0

        for ticker in ALLOCATIONS.keys():
            pos = positions[ticker]

            # Skip if stopped out
            if not pos['active']:
                continue

            # Get price (not really used in simplified model)
            price = prices.loc[week_date, ticker]
            if pd.isna(price):
                continue

            # Simulate trade
            premium_rate = WEEKLY_PREMIUM_RATES[ticker]
            assign_prob = ASSIGNMENT_PROB[ticker]

            return_pct, assigned = simulate_trade(price, premium_rate, assign_prob)

            # Calculate P&L
            trade_pnl = pos['current_capital'] * return_pct

            # Update position
            pos['current_capital'] += trade_pnl
            pos['total_pnl'] += trade_pnl
            pos['trades'] += 1
            if return_pct > 0:
                pos['wins'] += 1

            week_pnl += trade_pnl

            # Check stop-loss
            loss_pct = (pos['initial_capital'] - pos['current_capital']) / pos['initial_capital']

            if loss_pct >= pos['stop_loss']:
                pos['active'] = False
                pos['stopped_week'] = week_date
                if verbose:
                    print(f"  {ticker} STOPPED OUT at week {week_idx} ({week_date.date()}): "
                          f"{loss_pct*100:.1f}% loss")

        # Update portfolio
        total_portfolio_value += week_pnl
        equity_curve.append(total_portfolio_value)
        weeks_traded += 1

        # Track drawdown
        if total_portfolio_value > max_equity:
            max_equity = total_portfolio_value
        dd = (max_equity - total_portfolio_value) / max_equity
        if dd > max_drawdown:
            max_drawdown = dd

    # Calculate results
    total_return = (total_portfolio_value - INITIAL_CAPITAL) / INITIAL_CAPITAL
    years = weeks_traded / 52
    annualized = ((total_portfolio_value / INITIAL_CAPITAL) ** (1/years)) - 1

    results = {
        'final_capital': total_portfolio_value,
        'total_return_pct': total_return * 100,
        'annualized_pct': annualized * 100,
        'max_drawdown_pct': max_drawdown * 100,
        'weeks_traded': weeks_traded,
        'years': years,
        'positions': positions,
        'equity_curve': equity_curve,
    }

    return results


def compare_strategies():
    """Compare different stop-loss configurations"""

    print("\n" + "="*70)
    print("TIERED STOP-LOSS COMPARISON")
    print("="*70)

    scenarios = []

    # Scenario 1: Traditional 30% portfolio stop (simulated)
    print("\n### BASELINE: All positions 30% stop ###")
    baseline = backtest(vxx_stop=0.30, stock_stop=0.30, verbose=False)
    scenarios.append(('Traditional 30% All', baseline))

    # Scenario 2: Tiered 30% VXX / 15% stocks
    print("\n### TIERED: VXX 30% / Stocks 15% ###")
    tiered_15 = backtest(vxx_stop=0.30, stock_stop=0.15, verbose=True)
    scenarios.append(('Tiered VXX 30% / Stocks 15%', tiered_15))

    # Scenario 3: Tiered 30% VXX / 10% stocks
    print("\n### TIERED: VXX 30% / Stocks 10% ###")
    tiered_10 = backtest(vxx_stop=0.30, stock_stop=0.10, verbose=True)
    scenarios.append(('Tiered VXX 30% / Stocks 10%', tiered_10))

    # Print comparison
    print("\n\n" + "="*70)
    print("COMPARISON TABLE")
    print("="*70)

    comparison_data = []
    for name, res in scenarios:
        comparison_data.append({
            'Strategy': name,
            'Final Capital': f"${res['final_capital']:,.0f}",
            'Total Return': f"{res['total_return_pct']:.1f}%",
            'Annualized': f"{res['annualized_pct']:.1f}%",
            'Max DD': f"{res['max_drawdown_pct']:.1f}%",
            'Years': f"{res['years']:.1f}",
        })

    df = pd.DataFrame(comparison_data)
    print("\n" + df.to_string(index=False))

    # Position-level breakdown
    print("\n\n" + "="*70)
    print("POSITION-LEVEL RESULTS")
    print("="*70)

    for name, res in scenarios:
        print(f"\n{name}:")
        print("-" * 60)
        for ticker, pos in res['positions'].items():
            status = "STOPPED" if not pos['active'] else "Active"
            win_rate = (pos['wins'] / pos['trades'] * 100) if pos['trades'] > 0 else 0

            print(f"  {ticker:6s}: ${pos['initial_capital']:>8,.0f} -> ${pos['current_capital']:>8,.0f}  "
                  f"P&L: ${pos['total_pnl']:>8,.0f}  WR: {win_rate:>4.1f}%  [{status}]")

    # Analysis
    print("\n\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)

    baseline_return = baseline['annualized_pct']
    tiered15_return = tiered_15['annualized_pct']
    tiered10_return = tiered_10['annualized_pct']

    baseline_dd = baseline['max_drawdown_pct']
    tiered15_dd = tiered_15['max_drawdown_pct']
    tiered10_dd = tiered_10['max_drawdown_pct']

    print(f"\n1. RETURN COMPARISON:")
    print(f"   Traditional 30%:  {baseline_return:.1f}% annualized")
    print(f"   Tiered 15%:       {tiered15_return:.1f}% annualized ({tiered15_return - baseline_return:+.1f}%)")
    print(f"   Tiered 10%:       {tiered10_return:.1f}% annualized ({tiered10_return - baseline_return:+.1f}%)")

    print(f"\n2. RISK COMPARISON:")
    print(f"   Traditional 30%:  {baseline_dd:.1f}% max drawdown")
    print(f"   Tiered 15%:       {tiered15_dd:.1f}% max drawdown ({tiered15_dd - baseline_dd:+.1f}%)")
    print(f"   Tiered 10%:       {tiered10_dd:.1f}% max drawdown ({tiered10_dd - baseline_dd:+.1f}%)")

    print(f"\n3. RISK-ADJUSTED RETURN:")
    print(f"   Traditional 30%:  {baseline_return / max(baseline_dd, 1):.2f} (return/DD ratio)")
    print(f"   Tiered 15%:       {tiered15_return / max(tiered15_dd, 1):.2f} (return/DD ratio)")
    print(f"   Tiered 10%:       {tiered10_return / max(tiered10_dd, 1):.2f} (return/DD ratio)")

    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)

    return scenarios


if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)

    results = compare_strategies()
