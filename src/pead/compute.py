
import pandas as pd
import numpy as np
import datetime

def compute_all_returns(earnings_df, prices_df, market_df, entry_offset=2, hold=21, min_price=5, min_dollar_volume=1e6):
    prices_by_ticker = {
                        ticker: g.sort_values('date').reset_index(drop=True)
                        for ticker, g in prices_df.groupby('ticker')
                        }
    market_sorted = market_df.sort_values('date').reset_index(drop=True)

    final_earnings_df = earnings_df.copy()
    final_earnings_df['excess_return'] = np.nan
    
    returns = []
    for row in final_earnings_df.itertuples():
        sub = prices_by_ticker.get(row.ticker)
        if sub is None:
            returns.append(np.nan)
            continue
        returns.append(compute_event_return(row.announcement, sub, market_sorted, entry_offset, hold, min_price, min_dollar_volume))
    final_earnings_df['excess_return'] = returns

    return final_earnings_df.dropna(subset=['sue', 'excess_return'])


def compute_event_return(announcement, ticker_prices_df, market_df, entry_offset=2, hold=21, min_price=5, min_dollar_volume=1e6):

    if ticker_prices_df.empty:
        return np.nan

    idx = np.searchsorted(ticker_prices_df['date'], announcement, side='left')
    entry_idx = idx + entry_offset
    exit_idx = entry_idx + hold
    
    # borne haute : exit hors plage
    if exit_idx >= len(ticker_prices_df):
        return np.nan
    
    # borne basse : annonce avant le début des prix disponibles
    if idx == 0 and ticker_prices_df['date'].iloc[0] > announcement:
        return np.nan

    entry_price = ticker_prices_df['adj_close'].iloc[entry_idx]
    exit_price = ticker_prices_df['adj_close'].iloc[exit_idx]
    entry_date = ticker_prices_df['date'].iloc[entry_idx]
    exit_date = ticker_prices_df['date'].iloc[exit_idx]

    entry_market = market_df.loc[market_df['date'] == entry_date, 'adj_close']
    exit_market = market_df.loc[market_df['date'] == exit_date, 'adj_close']
    if entry_market.empty or exit_market.empty:
        return np.nan
    
    # quality filter 1 : entry price > 5
    entry_close_raw = ticker_prices_df['close'].iloc[entry_idx]
    if entry_close_raw < min_price:
        return np.nan
    
    # quality filter 2: volume * prix moyen 20 séances avant l'annonce > seuil
    if idx <= 20:
        return np.nan
    else:
        window = ticker_prices_df.iloc[idx-20:idx]
        mean_dollar_volume = (window['close'] * window['volume']).mean()
        if mean_dollar_volume < min_dollar_volume:
            return np.nan

    return (exit_price / entry_price - 1) - (exit_market.iloc[0] / entry_market.iloc[0] - 1)

