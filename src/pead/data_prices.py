import pandas as pd
import duckdb
import yfinance as yf
from time import sleep

def init_prices_db(db_path):
    with duckdb.connect(db_path) as con:
        # create table
        con.execute("""
                    CREATE TABLE IF NOT EXISTS prices ( 
                    date DATE NOT NULL, 
                    ticker VARCHAR NOT NULL, 
                    adj_close DOUBLE,
                    close DOUBLE, 
                    high DOUBLE, 
                    low DOUBLE,  
                    open DOUBLE, 
                    volume BIGINT,
                    PRIMARY KEY (date, ticker)
                    );
                    """
        )


def fetch_prices(tickers, start, end):
    frames = []

    for ticker in tickers:
        try:
            rows = yf.download(ticker,start=start, end=end, auto_adjust=False).reset_index()
            if rows.empty:
                print(f"[skip] {ticker}: no data")
                continue
            
            # Map columns correctly
            if isinstance(rows.columns, pd.MultiIndex):
                rows.columns = rows.columns.get_level_values(0)
            rows['ticker'] = ticker
            rows = rows.rename(columns={
                'index': 'date', 'Ticker': 'ticker', 'Open': 'open', 'Close': 'close', 'High': 'high', 'Low': 'low', 'Adj Close': 'adj_close', 'Volume': 'volume'
            })
            rows['date'] = rows['date'].dt.tz_localize(None).dt.normalize().astype('datetime64[us]')
            # Remove NA values if any
            prev_lines = rows.shape[0]
            rows = rows.dropna(subset=['close', 'adj_close'])
            if rows.shape[0] < prev_lines:
                print(f'Removed {prev_lines - rows.shape[0]} lines due to NA values in close/adj_close')

            frames.append(rows)
        except Exception as e:
            print(f'An error occurred for ticker {ticker}: {e}. \n Continuing...')
            continue
        finally:
            sleep(0.3)
    if not frames:
        print("No data fetched for any ticker.")
        return pd.DataFrame()
    
    df = pd.concat(frames, ignore_index=True).drop_duplicates(subset=['date', 'ticker'])
    return df

def store_prices(df, db_path):
    with duckdb.connect(db_path) as con:
        con.register('my_df', df)
        con.execute("""
            INSERT INTO prices (date, ticker, adj_close, close, high, low, open, volume)
            SELECT date, ticker, adj_close, close, high, low, open, volume FROM my_df
            ON CONFLICT (date, ticker) DO UPDATE SET
                adj_close = EXCLUDED.adj_close,
                close = EXCLUDED.close,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                open = EXCLUDED.open,
                volume = EXCLUDED.volume
        """)
    
def query_prices(ticker, db_path) -> pd.DataFrame:
    with duckdb.connect(db_path) as con:
        query = 'SELECT * FROM prices WHERE ticker = ?'
        output = con.execute(query, [ticker]).fetchdf()
        if output.empty:
            print(f'Specified ticker {ticker} returned empty')
    return output

def load_prices(db_path):
    with duckdb.connect(db_path) as con:
        return con.execute("SELECT * FROM prices").df()
    
if __name__ == '__main__':
    begin='2022-01-01'
    end='2026-12-31'

    k = fetch_prices(['DORM'], begin, end)
    print(k)