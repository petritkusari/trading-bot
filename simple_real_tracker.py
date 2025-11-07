#!/usr/bin/env python3
"""
SIMPLE REAL TRACKER - Works Every Time!
Uses actual stock prices, real strikes, 1 contract each
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def get_stock_price(ticker):
    """Get current stock price"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d')
        if not data.empty:
            return data['Close'].iloc[-1]
    except:
        pass
    return None


def calculate_strike(price):
    """Calculate ATM strike"""
    if price < 25:
        return round(price * 2) / 2  # $0.50 increments
    elif price < 100:
        return round(price)  # $1 increments
    elif price < 200:
        return round(price / 5) * 5  # $5 increments
    else:
        return round(price / 10) * 10  # $10 increments


def estimate_premium(price, iv=0.50):
    """Estimate weekly ATM PUT premium"""
    # Simplified: Weekly ATM premium ≈ Price * IV * sqrt(7/365)
    return price * iv * (7/365) ** 0.5


def create_simple_tracker():
    """Create simple tracker that WORKS"""

    print("="*60)
    print("SIMPLE REAL OPTIONS TRACKER")
    print("="*60)

    # Choose tradeable stocks (under $150/share ideally)
    stocks = {
        'VXX': {'name': 'VIX ETF', 'iv': 0.80},
        'AMD': {'name': 'AMD', 'iv': 0.55},
        'PLTR': {'name': 'Palantir', 'iv': 0.60},
        'F': {'name': 'Ford', 'iv': 0.45},
    }

    print("\nFetching current prices...")
    positions = []

    for ticker, info in stocks.items():
        price = get_stock_price(ticker)
        if price:
            strike = calculate_strike(price)
            premium = estimate_premium(price, info['iv'])

            positions.append({
                'ticker': ticker,
                'name': info['name'],
                'price': price,
                'strike': strike,
                'premium': premium,
            })

            print(f"  {ticker:6s} (${price:6.2f}): Strike ${strike:.2f}, Premium ~${premium:.2f}")

    if len(positions) < 4:
        print("\nWarning: Could only fetch", len(positions), "stocks")
        # Try alternatives
        alternatives = ['BAC', 'SOFI', 'NIO', 'RIVN']
        for ticker in alternatives:
            if len(positions) >= 4:
                break
            price = get_stock_price(ticker)
            if price:
                strike = calculate_strike(price)
                premium = estimate_premium(price, 0.50)
                positions.append({
                    'ticker': ticker,
                    'name': ticker,
                    'price': price,
                    'strike': strike,
                    'premium': premium,
                })

    # Create Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Strategy This Week"

    # Styling
    blue_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    white_font = Font(bold=True, color="FFFFFF", size=11)
    yellow_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    green_fill = PatternFill(start_color="C6E0B4", end_color="C6E0B4", fill_type="solid")

    today = datetime.now()
    friday = today + timedelta(days=(4 - today.weekday()) % 7)
    if friday == today:
        friday += timedelta(days=7)

    # Title
    ws['A1'] = "THIS WEEK'S STRATEGY SIMULATION"
    ws['A1'].font = Font(bold=True, size=14, color="0070C0")
    ws.merge_cells('A1:H1')
    ws['A1'].alignment = Alignment(horizontal='center')

    ws['A2'] = f"Week: {today.strftime('%b %d')} - {friday.strftime('%b %d, %Y')}"
    ws.merge_cells('A2:H2')
    ws['A2'].alignment = Alignment(horizontal='center')

    # Section 1: TODAY'S SETUP
    row = 4
    ws[f'A{row}'] = "WHAT TO SELL TODAY (MONDAY)"
    ws[f'A{row}'].font = Font(bold=True, size=12, color="FFFFFF")
    ws[f'A{row}'].fill = blue_fill
    ws.merge_cells(f'A{row}:H{row}')

    row += 1
    headers = ['Stock', 'Today Price', 'Strike', 'Contracts', 'Premium/Share', 'Total Premium', 'Capital Needed', 'Notes']
    for col, header in enumerate(headers, 1):
        ws.cell(row=row, column=col).value = header
        ws.cell(row=row, column=col).fill = blue_fill
        ws.cell(row=row, column=col).font = white_font
        ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')

    row += 1
    data_start = row

    total_premium = 0
    for pos in positions:
        ws[f'A{row}'] = pos['ticker']
        ws[f'B{row}'] = pos['price']
        ws[f'B{row}'].number_format = '$#,##0.00'
        ws[f'C{row}'] = pos['strike']
        ws[f'C{row}'].number_format = '$#,##0.00'
        ws[f'D{row}'] = 1
        ws[f'E{row}'] = pos['premium']
        ws[f'E{row}'].number_format = '$#,##0.00'
        ws[f'F{row}'] = pos['premium'] * 100
        ws[f'F{row}'].number_format = '$#,##0'
        ws[f'G{row}'] = pos['strike'] * 100
        ws[f'G{row}'].number_format = '$#,##0'
        ws[f'H{row}'] = f"Sell {pos['strike']:.0f} PUT"

        total_premium += pos['premium'] * 100
        row += 1

    data_end = row - 1

    # Total
    ws[f'E{row}'] = "TOTAL:"
    ws[f'E{row}'].font = Font(bold=True)
    ws[f'F{row}'] = f"=SUM(F{data_start}:F{data_end})"
    ws[f'F{row}'].font = Font(bold=True)
    ws[f'F{row}'].number_format = '$#,##0'
    ws[f'F{row}'].fill = green_fill

    # Section 2: FRIDAY RESULTS
    row += 3
    ws[f'A{row}'] = "FRIDAY RESULTS (FILL IN YELLOW ON FRIDAY)"
    ws[f'A{row}'].font = Font(bold=True, size=12, color="FFFFFF")
    ws[f'A{row}'].fill = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
    ws.merge_cells(f'A{row}:H{row}')

    row += 1
    headers2 = ['Stock', 'Friday Close', 'Strike', 'Up/Down %', 'Assigned?', 'Premium', 'Loss', 'NET P&L']
    for col, header in enumerate(headers2, 1):
        ws.cell(row=row, column=col).value = header
        ws.cell(row=row, column=col).fill = blue_fill
        ws.cell(row=row, column=col).font = white_font
        ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')

    row += 1
    friday_start = row

    for i in range(len(positions)):
        monday_row = data_start + i

        ws[f'A{row}'] = positions[i]['ticker']

        # Friday close - USER FILLS
        ws[f'B{row}'].fill = yellow_fill
        ws[f'B{row}'].number_format = '$#,##0.00'

        # Strike
        ws[f'C{row}'] = f"=C{monday_row}"
        ws[f'C{row}'].number_format = '$#,##0.00'

        # Up/Down %
        ws[f'D{row}'] = f"=IF(B{row}=\"\",\"\",(B{row}-B{monday_row})/B{monday_row})"
        ws[f'D{row}'].number_format = '0.0%'

        # Assigned?
        ws[f'E{row}'] = f'=IF(B{row}="","",IF(B{row}<C{row},"YES","NO"))'

        # Premium (always keep)
        ws[f'F{row}'] = f"=F{monday_row}"
        ws[f'F{row}'].number_format = '$#,##0'

        # Loss if assigned
        ws[f'G{row}'] = f'=IF(E{row}="YES",(C{row}-B{row})*100,0)'
        ws[f'G{row}'].number_format = '$#,##0'

        # NET P&L
        ws[f'H{row}'] = f'=F{row}-G{row}'
        ws[f'H{row}'].number_format = '$#,##0'

        row += 1

    friday_end = row - 1

    # Weekly Summary
    row += 1
    ws[f'A{row}'] = "WEEKLY PROFIT/LOSS:"
    ws[f'A{row}'].font = Font(bold=True, size=12)
    ws[f'H{row}'] = f"=SUM(H{friday_start}:H{friday_end})"
    ws[f'H{row}'].font = Font(bold=True, size=12)
    ws[f'H{row}'].number_format = '$#,##0'
    ws[f'H{row}'].fill = green_fill

    row += 1
    ws[f'A{row}'] = "WEEKLY RETURN %:"
    ws[f'A{row}'].font = Font(bold=True)
    ws[f'H{row}'] = f"=H{row-1}/SUM(G{data_start}:G{data_end})"
    ws[f'H{row}'].font = Font(bold=True)
    ws[f'H{row}'].number_format = '0.0%'
    ws[f'H{row}'].fill = green_fill

    # Instructions
    row += 3
    ws[f'A{row}'] = "HOW TO USE:"
    ws[f'A{row}'].font = Font(bold=True, color="C00000")
    ws.merge_cells(f'A{row}:H{row}')

    row += 1
    instructions = [
        "1. TODAY: Review what you would sell (Section 1)",
        "2. FRIDAY: Fill in YELLOW cells (Friday closing price for each stock)",
        "3. Check your NET P&L and weekly return!",
        "",
        "How it works:",
        f"  - Today you SELL 1 PUT contract for each stock",
        f"  - You collect ~${total_premium:.0f} total premium",
        f"  - On Friday:",
        f"      If stock ABOVE strike = PUT expires, you keep premium (PROFIT!)",
        f"      If stock BELOW strike = You're assigned, buy 100 shares",
        "",
        "Example:",
        f"  VXX closes Friday at $36 (above ${positions[0]['strike']:.0f} strike)",
        f"    Result: Keep ${positions[0]['premium']*100:.0f} premium = PROFIT!",
        "",
        f"  VXX closes Friday at $32 (below ${positions[0]['strike']:.0f} strike)",
        f"    Premium: ${positions[0]['premium']*100:.0f}",
        f"    Loss: $(${positions[0]['strike']:.0f}-$32)*100 = $300",
        f"    NET: ${positions[0]['premium']*100:.0f} - $300 = DEPENDS ON NUMBERS",
    ]

    for inst in instructions:
        ws[f'A{row}'] = inst
        if inst and inst[0].isdigit():
            ws[f'A{row}'].font = Font(bold=True)
        elif "Example:" in inst or "How it works:" in inst:
            ws[f'A{row}'].font = Font(bold=True)
        ws.merge_cells(f'A{row}:H{row}')
        row += 1

    # Column widths
    for i, width in enumerate([10, 12, 10, 12, 12, 14, 14, 14], 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Save
    filename = f"C:\\Trading\\Simple_Tracker_{today.strftime('%Y%m%d')}.xlsx"
    wb.save(filename)

    print(f"\n{'='*60}")
    print(f"TRACKER CREATED: {filename}")
    print(f"{'='*60}")
    print(f"\nPositions:")
    for pos in positions:
        print(f"  {pos['ticker']:6s}: SELL 1 ${pos['strike']:.0f} PUT -> ${pos['premium']*100:.0f} premium")
    print(f"\nTotal Premium: ${total_premium:.0f}")
    print(f"\nFILL IN FRIDAY PRICES IN YELLOW CELLS!")

    return filename


if __name__ == "__main__":
    create_simple_tracker()
