# WIP

import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import time
import os

load_dotenv()

# Alpaca API credentials
API_KEY = os.environ.get('fakekey')
SECRET_KEY = os.environ.get('fakesecret')
BASE_URL = 'https://paper-api.alpaca.markets/'

from backtest_meanreversion import symbols

# initialize Alpaca API
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

# dictionary to store buy prices
portfolio = {}

def buy_stock(symbol, dollars, stop_loss=.04, take_profit=.08):
    """
    Buy a stock using Alpaca API based on dollar amount.
    :param symbol: Ticker symbol of the stock to buy
    :param dollars: Dollar amount to invest in the stock
    :param stop_loss: Stop loss percentage (e.g., 0.05 for 5%)
    :param take_profit: Take profit percentage (e.g., 0.10 for 10%)
    """

    try:

        # take current price, round quantity down because complex order needs money
        current_price = float(api.get_latest_trade(symbol).price)
        qty = int(dollars // current_price)


        if qty < 1:
            print(f"Insufficient dollars to buy at least 1 share of {symbol}.")
            return
        
        # Get the latest price of the stock
        current_price = float(api.get_latest_trade(symbol).price)
        qty = int(round(dollars / current_price, 4))  # Calculate shares to buy (rounded to 4 decimal places)

        stop_loss_price = round(current_price * (1 - stop_loss), 2)
        take_profit_price = round(current_price * (1 + take_profit), 2)

        # Place a market order to buy the stock
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='market',
            time_in_force='day',
            order_class='bracket',  # Use complex bracket orders
            stop_loss={'stop_price': stop_loss_price},
            take_profit={'limit_price': take_profit_price},
        )

        portfolio[symbol] = {'buy_price': current_price, 'qty': qty}

        print(f"Bought {qty} shares of {symbol} at ${current_price:.2f} for ${dollars:.2f}")

    except Exception as e:
        print(f"Error buying stock: {e}")



def sell_stock(symbol, dollars):
    """
    Sell a stock using Alpaca API based on dollar amount.
    :param symbol: Ticker symbol of the stock to sell
    :param dollars: Dollar amount of the stock to sell
    """
    try:
        # Get the latest price of the stock
        current_price = float(api.get_latest_trade(symbol).price)
        qty_to_sell = round(dollars / current_price, 4)  # Calculate shares to sell (rounded to 4 decimal places)

        # Ensure the portfolio contains enough shares
        if symbol in portfolio and portfolio[symbol]['qty'] >= qty_to_sell:
            api.submit_order(
                symbol=symbol,
                qty=qty_to_sell,
                side='sell',
                type='market',
                time_in_force='gtc'
            )

            # Update portfolio
            portfolio[symbol]['qty'] -= qty_to_sell
            if portfolio[symbol]['qty'] == 0:
                del portfolio[symbol]

            print(f"Sold {qty_to_sell} shares of {symbol} for approximately ${dollars:.2f}")

        else:
            print(f"Insufficient shares to sell for {symbol}.")

    except Exception as e:
        print(f"Error selling stock: {e}")

num_stocks = len(symbols)
dollars = 9999 / num_stocks

for stock in symbols:
    buy_stock(stock, dollars, .03, .08)
    time.sleep(2)
