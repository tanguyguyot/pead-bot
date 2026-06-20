import duckdb
import pandas as pd
import numpy as np
from time import sleep
import datetime
import yfinance as yf

def init_earnings_db(db_path):
    with duckdb.connect(db_path) as con:
        # create table
        con.execute("""
                    CREATE TABLE IF NOT EXISTS earnings ( 
                    announcement DATE NOT NULL,
                    ticker VARCHAR NOT NULL, 
                    realized_eps DOUBLE,
                    expected_eps DOUBLE,
                    surprise DOUBLE,
                    sue DOUBLE,
                    is_future BOOLEAN,
                    last_updated DATE,
                    PRIMARY KEY (announcement, ticker)
                    );
                    """
        )

def store_earnings(df, db_path):
    with duckdb.connect(db_path) as con:
        con.register('my_df', df)
        con.execute('INSERT OR REPLACE INTO earnings (announcement, ticker, realized_eps, expected_eps, surprise, sue, is_future, last_updated) SELECT announcement, ticker, realized_eps, expected_eps, surprise, sue, is_future, last_updated FROM my_df')

# new fetch earnings from yfinance

def fetch_earnings(tickers):
    earnings_df = []
    for ticker in tickers: 
        print(f'Fetching for {ticker}...')
        try:
            df = yf.Ticker(ticker).get_earnings_dates(limit=100).reset_index(drop=False).drop_duplicates(subset='Earnings Date')
            # process Earnings Date	EPS Estimate	Reported EPS	Surprise(%)
            df['is_future'] = df['Reported EPS'].isna()
            df['ticker'] = ticker
            df = df.rename(columns={
                'Earnings Date': 'announcement',
                    'Reported EPS': 'realized_eps',
                    'EPS Estimate': 'expected_eps'
                    })
            df = df.drop(columns=
                    ['Surprise(%)'])
            df['announcement'] = df['announcement'].dt.tz_convert('America/New_York').dt.date
            df['last_updated'] = datetime.datetime.now().date()
            # calculate surprise
            df['surprise'] = df.realized_eps - df.expected_eps
            earnings_df.append(df)
            
        except Exception as e:
            print(f'Error for ticker {ticker}: {e}')
            
        sleep(0.5)
    if not earnings_df: return pd.DataFrame()
    return pd.concat(earnings_df).sort_values(by='announcement', ascending=True) # sorted ancient to newest


def compute_sue(df, window=8, min_periods=4):
    df = df[~df['is_future']].copy()
    df = df.sort_values(['ticker', 'announcement'])
    def _rolling_sigma(s):
        return s.shift(1).rolling(window=window, min_periods=min_periods).std(ddof=0)
    sigma = df.groupby(by='ticker').surprise.transform(_rolling_sigma)
    df['sue'] = df['surprise'] / sigma
    return df