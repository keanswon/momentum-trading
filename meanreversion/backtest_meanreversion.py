import pandas as pd
import numpy as np
import os
from tabulate import tabulate
from datetime import datetime, timedelta
import pickle

from meanhelpers.indicators import calculate_rsi, calculate_ema, calculate_gains, calculate_close_volatility

NUM_DAYS_BEFORE = 25
RSI_LOW = 50
RSI_HIGH = 60
TOP_N = 5
STOP_LOSS = 4
TAKE_PROFIT = 8
START_DATE = '2024-12-23'
NUM_WEEKS = 5

def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
    return None


def main():
    change = run(START_DATE, NUM_DAYS_BEFORE, TOP_N, NUM_WEEKS, STOP_LOSS, TAKE_PROFIT, RSI_LOW, RSI_HIGH)
    print(f'{(change - 1) * 100:.3f}%')

# function to get the next trading day if there is a holiday so we don't have to exclude weeks
def get_next_trading_day(df, date, max_days=15):
    trading_days = df.index
    future_days = trading_days[trading_days >= date]
    
    # Limit to the next `max_days` trading days
    return future_days[:max_days] if not future_days.empty else []


# Backtesting function
# pre-conditions: pandas dataframe, a monday date, n days before, top n performers, stop_loss, take_profit
def backtest(df, monday, n, top_n=5, stop_loss=2.5, take_profit=7, rsi_window=14, rsi_low=40, rsi_high=70):
    # Calculate gains over n days
    gains = calculate_gains(df, monday, n)
    
    # debugging to make sure stocks displayed were actual top % gainers
    # print(gains)
    top_gainers = gains.index  # Get all stocks sorted by performance

    results = []

    for stock in top_gainers:
        stock_prices = df[stock]  # Get price series for the stock
        
        # calculate RSI, SMA
        rsi = calculate_rsi(stock_prices, window=rsi_window)
        sma_5 = calculate_ema(stock_prices, window=5)
        sma_20 = calculate_ema(stock_prices, window=20)

        
        # Check if the stock meets RSI and SMA criteria on the given Monday
        if monday not in rsi.index or monday not in sma_5.index or monday not in sma_20.index:
            continue  # Skip if indicators can't be calculated
        if not (rsi_low <= rsi[monday] <= rsi_high):  # RSI condition
            continue
        if sma_5[monday] <= sma_20[monday]:  # SMA condition
            continue

        trading_week = df.index[(df.index >= monday) & (df.index <= monday + pd.Timedelta(days=6))]  # Restrict to the week
        week_data = stock_prices.loc[trading_week]

        buy_price = week_data.iloc[0]
        
        for price in week_data:
            change = (price - buy_price) / buy_price * 100
            if change <= -stop_loss:
                results.append({'Stock': stock, 'Outcome': 'Stop Loss', 'Change': change})
                break
            elif change >= take_profit:
                results.append({'Stock': stock, 'Outcome': 'Take Profit', 'Change': change})
                break
        else:
            week_end_change = (week_data.iloc[-1] - buy_price) / buy_price * 100
            results.append({'Stock': stock, 'Outcome': 'End of Week', 'Change': week_end_change})

        # stop once we've selected the top N stocks meeting criteria
        if len(results) >= top_n:
            break

    return pd.DataFrame(results)


df = load_data(os.path.join('stockdata','stockdata.pkl'))


def run(start, num_days_before, top_n, num_weeks, stop_loss, take_profit, rsi_low, rsi_high):
    initial_investment_per_stock = 100

    start_date = datetime.strptime(start, '%Y-%m-%d')

    dates = [start_date + timedelta(days=7 * i) for i in range(num_weeks)]

    total_percent = 1

    for date in dates:

        mon = pd.Timestamp(date)

        next_trading_days = get_next_trading_day(df, mon, max_days=5)  # Look ahead up to 5 trading days
        if next_trading_days.empty:
            print(f"No trading days found after {date}. Skipping...")
            continue

        mon = next_trading_days[0]

        results = backtest(df, mon, n=num_days_before, top_n=top_n, stop_loss=stop_loss, take_profit=take_profit, rsi_low=rsi_low, rsi_high=rsi_high)

        num_stocks = len(results)
        total_investment = initial_investment_per_stock * num_stocks

        if results.empty:
            print(f"No data available for the week of {date}. Skipping...")
            continue

        results['Dollar Change'] = (results['Change'] / 100) * initial_investment_per_stock
        total_dollar_change = results['Dollar Change'].sum()
        total_percentage_change = (total_dollar_change / total_investment) * 100

        total_percent *= (total_percentage_change / 100 + 1)

        symbols = results['Stock'] # to use in trader file

    print('Week of', date)
    print(f"\t{tabulate(results, tablefmt='grid')}")
    print(f"Last week's Percentage Change: {total_percentage_change:.2f}%")

    print(f'total for {len(dates)} weeks of trading')
    print(f'cumulative % change: {total_percent:.3f}')

    return total_percent

if __name__ == "__main__":
    main()
