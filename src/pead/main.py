from compute import *
from data_prices import *
from earnings import *
import random as rd
import matplotlib.pyplot as plt
import os

if __name__ == '__main__':
    rd.seed(123)
    prices_db_path = '../data/prices.db'
    earnings_db_path = '../data/earnings.db'
    plots_path = '../plots/'
    start="2010-01-01"
    end="2026-06-20"

    print(os.curdir)
    with open('../s&p600list.txt') as f:
        sp600_tickers = [k.strip() for k in f.read().replace("\'", "").replace("[", "").split(",\n")]

    tickers = rd.choices(sp600_tickers, k=150)

    print(f'Now analyzing from {start} to {end} the following {len(tickers)} tickers (S&P600 SmallCaps) ; Compared with IJW')
    print(', '.join(tickers))

    init_prices_db(prices_db_path)
    init_earnings_db(earnings_db_path)

    market_df = fetch_prices(['IJR'], start, end)

    prices_df = fetch_prices(tickers, start, end)

    store_prices(prices_df, prices_db_path)

    earnings_df = fetch_earnings(tickers)

    earnings_df = compute_sue(earnings_df)

    store_earnings(earnings_df, earnings_db_path)


    returns = compute_all_returns(earnings_df, prices_df, market_df)


    # Plot results

    returns['sue_decile'] = pd.qcut(returns.sue, 10)
    means = returns.groupby('sue_decile').excess_return.mean()
    medians = returns.groupby('sue_decile').excess_return.median()

    fig, ax = plt.subplots(figsize=(14,6))

    ind = np.arange(10)
    width = 0.3

    ax.bar(ind - 0.15, means, width=0.3, label='mean')
    ax.bar(ind + 0.15, medians, width=0.3, label='median')
    ax.set_xticks(ind, labels=list(means.index.astype(str)))
    ax.legend()
    ax.plot()
    plt.savefig(plots_path + 'return_decile_plot')

