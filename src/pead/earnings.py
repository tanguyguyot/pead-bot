import duckdb
import requests
from time import sleep
import pandas as pd
import numpy as np

def init_db(db_path):
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
                    expected_revenue DOUBLE,
                    realized_revenue DOUBLE,
                    is_future BOOLEAN,
                    last_updated DATE,
                    PRIMARY KEY (announcement, ticker)
                    );
                    """
        )

def store_earnings(df, db_path):
    with duckdb.connect(db_path) as con:
        con.register('my_df', df)
        con.execute('INSERT OR REPLACE INTO earnings (announcement, ticker, realized_eps, expected_eps, surprise, sue, expected_revenue, realized_revenue, is_future, last_updated) SELECT announcement, ticker, realized_eps, expected_eps, surprise, sue, expected_revenue, realized_revenue, is_future, last_updated FROM my_df')

def fetch_earnings(tickers, api_key):
    earnings_df = []
    endpoint = 'https://financialmodelingprep.com/stable/earnings'
    # (announcement, ticker, realized_eps, expected_eps, surprise, sue, expected_revenue, realized_revenue, is_future, last_updated)
    for ticker in tickers:
        print(f'Fetching for {ticker}...')
        url = f'{endpoint}?symbol={ticker}&apikey={api_key}'
        try:
            r = requests.get(url)
            if r.status_code == 200:
                if r.json() == []:
                    print(f'error HTTPS 200 BUT json is empty! For ticker {ticker}')
                    continue
                df = pd.DataFrame(r.json())
                # process df symbol	date	epsActual	epsEstimated	revenueActual	revenueEstimated	lastUpdated
                df['is_future'] = df['epsActual'].isna()
                df = df.rename(columns={'symbol': 'ticker',
                        'date': 'announcement',
                        'epsActual': 'realized_eps',
                        'epsEstimated': 'expected_eps',
                        'revenueEstimated': 'expected_revenue',
                            'revenueActual': 'realized_revenue',
                            'lastUpdated': 'last_updated'
                        })
                # calculate sue and surprise
                df['surprise'] = df.realized_eps - df.expected_eps
                earnings_df.append(df)
            else:
                print(f'Error on HTTP request {r.status_code}')
            
        except Exception as e:
            print(f'Error for ticker {ticker}: {e}')
        sleep(1)
    return pd.concat(earnings_df).sort_values(by='announcement', ascending=True) # sorted ancient to newest


def compute_sue(df, window=8, min_periods=4):
    df = df.sort_values(['ticker', 'announcement']).copy()
    def _rolling_sigma(s):
        return s.shift(1).rolling(window=window, min_periods=min_periods).std(ddof=0)
    sigma = df.groupby(by='ticker').surprise.transform(_rolling_sigma)
    df['sue'] = df['surprise'] / sigma
    return df
