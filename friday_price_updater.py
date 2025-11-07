#!/usr/bin/env python3
"""
Automatically fetch Friday closing prices and update strategy tracker
Run this on Friday after market close (4pm ET) or anytime after
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import glob
import os

def get_latest_tracker_file():
    """Find the most recent strategy simulation file"""
    files = glob.glob("C:\\Trading\\Strategy_Simulation_*.xlsx")
    if not files:
        print("ERROR: No strategy simulation files found!")
        print("Run: python weekly_strategy_tracker.py first")
        return None

    # Get most recent file
    latest = max(files, key=os.path.getctime)
    return latest


def get_friday_prices(tickers):
    """Fetch Friday closing prices"""
    print(f"\nFetching Friday closing prices...")
    prices = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            # Get last 5 days to ensure we catch Friday
            data = stock.history(period='5d')
            if not data.empty:
                # Get most recent close (should be Friday if run after market close)
                friday_price = data['Close'].iloc[-1]
                prices[ticker] = friday_price
                print(f"  {ticker}: ${friday_price:.2f}")
        except Exception as e:
            print(f"  ERROR fetching {ticker}: {e}")

    return prices


def update_excel_with_friday_prices(filename):
    """Update Excel file with Friday prices and calculate results"""

    print(f"\nOpening file: {filename}")
    wb = openpyxl.load_workbook(filename)
    ws = wb.active

    # Find the tickers in the Monday section (starting around row 9)
    print("\nLooking for positions...")

    monday_positions = {}
    row = 9  # Start scanning from row 9
    while row < 50:  # Don't scan forever
        ticker_cell = ws[f'A{row}'].value
        if ticker_cell and isinstance(ticker_cell, str) and ticker_cell.isupper():
            # Found a ticker
            strike = ws[f'E{row}'].value
            if strike:
                monday_positions[ticker_cell] = {
                    'row': row,
                    'strike': strike,
                    'premium': ws[f'F{row}'].value,
                    'contracts': ws[f'G{row}'].value,
                }
                print(f"  Found: {ticker_cell} @ ${strike}")
        row += 1

    if not monday_positions:
        print("ERROR: Could not find positions in Excel file!")
        return

    # Get Friday prices
    tickers = list(monday_positions.keys())
    friday_prices = get_friday_prices(tickers)

    # Find Friday section (starts around row 20+)
    print("\nUpdating Friday section...")
    friday_row_start = None
    row = 15
    while row < 50:
        cell_value = ws[f'A{row}'].value
        if cell_value and "FRIDAY" in str(cell_value).upper():
            friday_row_start = row + 2  # Data starts 2 rows after header
            break
        row += 1

    if not friday_row_start:
        print("ERROR: Could not find Friday section!")
        return

    # Update Friday prices
    row = friday_row_start
    for ticker in monday_positions.keys():
        if ticker in friday_prices:
            friday_price = friday_prices[ticker]
            strike = monday_positions[ticker]['strike']

            # Update Friday price (column B)
            ws[f'B{row}'].value = friday_price
            ws[f'B{row}'].number_format = '$#,##0.00'

            # Determine if assigned
            is_itm = friday_price < strike
            ws[f'E{row}'].value = "YES" if is_itm else "NO"

            print(f"  {ticker}: Friday ${friday_price:.2f} vs Strike ${strike:.2f} - {'ASSIGNED' if is_itm else 'EXPIRED'}")

            row += 1

    # Save updated file
    output_filename = filename.replace('.xlsx', '_FRIDAY_UPDATED.xlsx')
    wb.save(output_filename)

    print(f"\n{'='*60}")
    print(f"Updated file saved: {output_filename}")
    print(f"{'='*60}")
    print(f"\nOpen the file to see your complete P&L results!")

    return output_filename


def main():
    """Main function"""
    print("="*60)
    print("FRIDAY PRICE UPDATER")
    print("="*60)

    # Find latest tracker file
    tracker_file = get_latest_tracker_file()
    if not tracker_file:
        return

    print(f"\nFound tracker: {os.path.basename(tracker_file)}")

    # Update with Friday prices
    updated_file = update_excel_with_friday_prices(tracker_file)

    if updated_file:
        print(f"\n✅ SUCCESS!")
        print(f"\nNext steps:")
        print(f"1. Open: {os.path.basename(updated_file)}")
        print(f"2. Review your P&L results")
        print(f"3. See how the strategy performed this week")
        print(f"4. Run weekly_strategy_tracker.py again for next week!")


if __name__ == "__main__":
    main()
