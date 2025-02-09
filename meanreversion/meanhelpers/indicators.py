import pandas as pd


# function to calculate percentage gain over n days
def calculate_gains(df, start_date, n):
    end_date = start_date - pd.Timedelta(days=n)
    # Filter rows based on the index (dates)

    filtered_data = df[(df.index <= start_date) & (df.index > end_date)]
    # Calculate percentage gains
    gains = (filtered_data.iloc[-1] - filtered_data.iloc[0]) / filtered_data.iloc[0] * 100
    return gains.sort_values(ascending=False)

# function to calculate RSI
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# function to calculate SMA
def calculate_ema(prices, window):
    return prices.ewm(span=window, adjust=False).mean()

def calculate_close_volatility(df, window=14):
    # calculate daily absolute changes for each stock
    daily_changes = df.diff().abs()

    # calculate rolling average of daily changes (volatility)
    close_volatility = daily_changes.rolling(window=window).mean()

    return close_volatility


def calculate_atr(high, low, close, window=14):
    high_low = high - low
    high_close = abs(high - close.shift(1))
    low_close = abs(low - close.shift(1))
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=window).mean()
    
    return atr