#!/usr/bin/env python3
"""
Create Weekly Strategy Tracking Spreadsheet
Simulates the strategy with TODAY's data, then validates on Friday
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def get_current_prices():
    """Get current market prices for our portfolio"""
    tickers = ['VXX', 'VIXY', 'COIN', 'TSLA', 'QQQ', 'AAPL', 'SPY']

    print("Fetching current market prices...")
    prices = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period='5d')
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                prices[ticker] = current_price
                print(f"  {ticker}: ${current_price:.2f}")
        except Exception as e:
            print(f"  Error fetching {ticker}: {e}")

    return prices


def calculate_atm_strike(price):
    """Calculate ATM strike (round to nearest $5 or appropriate increment)"""
    if price < 50:
        # Round to nearest $2.50
        return round(price * 2) / 2
    elif price < 200:
        # Round to nearest $5
        return round(price / 5) * 5
    else:
        # Round to nearest $10
        return round(price / 10) * 10


def estimate_premium(price, strike, days_to_expiry=2, iv_pct=0.40):
    """
    Rough estimate of PUT premium using simplified Black-Scholes

    Args:
        price: Current stock price
        strike: Strike price
        days_to_expiry: Days until expiration
        iv_pct: Implied volatility (40% default)
    """
    # Simplified premium estimation
    # Premium ≈ Intrinsic Value + Time Value

    intrinsic = max(0, strike - price)

    # Time value (very rough approximation)
    # Higher IV = higher premium
    time_value = price * iv_pct * (days_to_expiry / 365) ** 0.5

    total_premium = intrinsic + time_value

    return round(total_premium, 2)


def create_weekly_tracker():
    """Create Excel tracker for this week's strategy simulation"""

    # Get current prices
    prices = get_current_prices()

    # Portfolio allocation (from strategy)
    capital = 50000
    allocations = {
        'VXX': 0.25,    # 25% - Can use VIXY if VXX not available
        'COIN': 0.25,   # 25%
        'TSLA': 0.25,   # 25%
        'QQQ': 0.15,    # 15%
        # 10% cash reserve
    }

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Week Strategy Simulation"

    # Header styling
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)

    today = datetime.now()
    friday = today + timedelta(days=(4 - today.weekday()) % 7)

    # Title
    ws['A1'] = "WEEKLY OPTIONS STRATEGY SIMULATION"
    ws['A1'].font = Font(bold=True, size=14)
    ws.merge_cells('A1:H1')

    ws['A2'] = f"Start Date: {today.strftime('%Y-%m-%d')}"
    ws['A3'] = f"Expiration: {friday.strftime('%Y-%m-%d')} (Friday)"
    ws['A4'] = f"Initial Capital: ${capital:,.0f}"

    # Section 1: POSITIONS TO TAKE
    row = 6
    ws[f'A{row}'] = "POSITIONS TO TAKE (MONDAY/TODAY)"
    ws[f'A{row}'].font = Font(bold=True, size=12, color="0070C0")
    ws.merge_cells(f'A{row}:H{row}')

    row += 1
    headers = ['Ticker', 'Allocation %', 'Capital $', 'Current Price', 'ATM Strike', 'PUT Premium Est.', 'Contracts', 'Total Premium']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')

    # Add position data
    row += 1
    start_data_row = row

    for ticker, alloc_pct in allocations.items():
        # Use VIXY if VXX not available
        actual_ticker = ticker
        if ticker == 'VXX' and ticker not in prices:
            if 'VIXY' in prices:
                actual_ticker = 'VIXY'
            else:
                continue

        if actual_ticker not in prices:
            continue

        price = prices[actual_ticker]
        allocation_capital = capital * alloc_pct
        strike = calculate_atm_strike(price)

        # Estimate IV based on ticker
        iv_dict = {'VXX': 0.80, 'VIXY': 0.80, 'COIN': 0.60, 'TSLA': 0.50, 'QQQ': 0.25, 'AAPL': 0.30, 'SPY': 0.20}
        iv = iv_dict.get(actual_ticker, 0.40)

        premium = estimate_premium(price, strike, days_to_expiry=2, iv_pct=iv)
        contracts = int(allocation_capital / (strike * 100))
        total_premium = premium * 100 * contracts

        ws[f'A{row}'] = actual_ticker
        ws[f'B{row}'] = f"{alloc_pct*100:.0f}%"
        ws[f'C{row}'] = allocation_capital
        ws[f'C{row}'].number_format = '$#,##0'
        ws[f'D{row}'] = price
        ws[f'D{row}'].number_format = '$#,##0.00'
        ws[f'E{row}'] = strike
        ws[f'E{row}'].number_format = '$#,##0.00'
        ws[f'F{row}'] = premium
        ws[f'F{row}'].number_format = '$#,##0.00'
        ws[f'G{row}'] = contracts
        ws[f'H{row}'] = total_premium
        ws[f'H{row}'].number_format = '$#,##0.00'

        row += 1

    end_data_row = row - 1

    # Total premium row
    ws[f'A{row}'] = "TOTAL PREMIUM COLLECTED"
    ws[f'A{row}'].font = Font(bold=True)
    ws[f'H{row}'] = f"=SUM(H{start_data_row}:H{end_data_row})"
    ws[f'H{row}'].font = Font(bold=True)
    ws[f'H{row}'].number_format = '$#,##0.00'
    ws[f'H{row}'].fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")

    # Section 2: FRIDAY RESULTS (TO BE FILLED IN)
    row += 3
    ws[f'A{row}'] = "FRIDAY CLOSING PRICES (FILL IN ON FRIDAY)"
    ws[f'A{row}'].font = Font(bold=True, size=12, color="C00000")
    ws.merge_cells(f'A{row}:G{row}')

    row += 1
    headers2 = ['Ticker', 'Friday Close', 'Strike', 'ITM?', 'Assignment?', 'P&L per Contract', 'Total P&L']
    for col, header in enumerate(headers2, 1):
        cell = ws.cell(row=row, column=col)
        cell.value = header
        cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    row += 1
    friday_start_row = row

    # Add ticker rows for Friday data
    for ticker in allocations.keys():
        actual_ticker = ticker
        if ticker == 'VXX' and ticker not in prices and 'VIXY' in prices:
            actual_ticker = 'VIXY'

        if actual_ticker not in prices:
            continue

        ws[f'A{row}'] = actual_ticker
        ws[f'B{row}'] = ""  # User fills in
        ws[f'B{row}'].number_format = '$#,##0.00'
        ws[f'B{row}'].fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

        # Get strike from above
        data_row = start_data_row + list(allocations.keys()).index(ticker)
        ws[f'C{row}'] = f"=E{data_row}"
        ws[f'C{row}'].number_format = '$#,##0.00'

        # ITM check
        ws[f'D{row}'] = f'=IF(B{row}<C{row},"YES","NO")'

        # Assignment (user decision)
        ws[f'E{row}'] = ""  # User fills: YES or NO
        ws[f'E{row}'].fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

        # P&L calculation
        premium_cell = f"F{data_row}"
        ws[f'F{row}'] = f'=IF(E{row}="YES", {premium_cell}*100 - (C{row}-B{row})*100, {premium_cell}*100)'
        ws[f'F{row}'].number_format = '$#,##0.00'

        # Total P&L
        contracts_cell = f"G{data_row}"
        ws[f'G{row}'] = f'=F{row}*{contracts_cell}'
        ws[f'G{row}'].number_format = '$#,##0.00'

        row += 1

    friday_end_row = row - 1

    # Summary
    row += 1
    ws[f'A{row}'] = "WEEKLY PROFIT/LOSS"
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'G{row}'] = f"=SUM(G{friday_start_row}:G{friday_end_row})"
    ws[f'G{row}'].font = Font(bold=True, size=12)
    ws[f'G{row}'].number_format = '$#,##0.00'
    ws[f'G{row}'].fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")

    row += 1
    ws[f'A{row}'] = "WEEKLY RETURN %"
    ws[f'A{row}'].font = Font(bold=True)
    ws[f'G{row}'] = f"=G{row-1}/{capital}"
    ws[f'G{row}'].font = Font(bold=True)
    ws[f'G{row}'].number_format = '0.00%'
    ws[f'G{row}'].fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")

    # Instructions
    row += 3
    ws[f'A{row}'] = "INSTRUCTIONS:"
    ws[f'A{row}'].font = Font(bold=True, size=11, color="C00000")

    row += 1
    instructions = [
        "1. Review the positions above - this is what you would sell TODAY",
        "2. On FRIDAY, fill in the yellow cells with actual closing prices",
        "3. Mark 'YES' or 'NO' for Assignment (if stock below strike, you're assigned)",
        "4. Spreadsheet will automatically calculate your P&L",
        "5. Compare actual results to estimated premiums",
        "6. Create new sheet for next week and repeat!",
        "",
        "YELLOW CELLS = You need to fill these in on Friday",
        "GREEN CELLS = Automatic calculations",
    ]

    for instruction in instructions:
        ws[f'A{row}'] = instruction
        row += 1

    # Column widths
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 18
    ws.column_dimensions['G'].width = 15
    ws.column_dimensions['H'].width = 18

    # Save file
    filename = f"C:\\Trading\\Strategy_Simulation_{today.strftime('%Y%m%d')}.xlsx"
    wb.save(filename)

    print(f"\n{'='*60}")
    print(f"Excel tracker created: {filename}")
    print(f"{'='*60}")
    print(f"\nWhat to do:")
    print(f"1. Open the file and review today's positions")
    print(f"2. On Friday ({friday.strftime('%Y-%m-%d')}), fill in closing prices")
    print(f"3. Mark which positions got assigned")
    print(f"4. See your actual P&L!")

    return filename


if __name__ == "__main__":
    create_weekly_tracker()
