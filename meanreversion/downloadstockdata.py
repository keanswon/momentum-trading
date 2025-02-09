"""
file to download stock data for many symbols
"""

# download s&p 500

"""

strategy: 

check top 12 month performers on S&P 500, buy top performers for 1 month

strategy from algovibes

"""

import yfinance as yf
import pandas as pd
import numpy as np
import pickle
import os

DATA_FOLDER = "stockdata"

def save_data(data, filepath):
        with open(filepath, "wb") as f:
            pickle.dump(data, f)

def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
    return None


def download_snp():
    # folder for saving data
    data_folder = DATA_FOLDER
    os.makedirs(data_folder, exist_ok=True)

    data_filepath = os.path.join(data_folder, "stockdata.pkl")
    alt_filepath = os.path.join(data_folder, "stockdata.csv")

    start = '2023-01-01' # start from two years ago
    overall = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]

    stocks = overall.Symbol.tolist() # take stock symbols

    print("Downloading data from yfinance...")
    df = yf.download(stocks, start=start)['Close']
    df.index = pd.to_datetime(df.index)
    save_data(df, data_filepath)

    data = pd.DataFrame(df)
    data.to_csv(alt_filepath)

if __name__ == "__main__":
    download_snp()
