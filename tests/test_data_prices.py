# tests/test_data_prices.py
import pytest
import pandas as pd
from pead.data_prices import fetch_prices, init_db, store_prices, query_prices

# Un seul fetch réseau partagé par tous les tests (rapide)
@pytest.fixture(scope="module")
def sample_df():
    return fetch_prices(['AAPL', 'MSFT'], '2024-01-01', '2024-02-01')

def test_columns(sample_df):
    expected = {'date', 'ticker', 'adj_close', 'close', 'high', 'low', 'open', 'volume'}
    assert set(sample_df.columns) == expected

def test_not_empty(sample_df):
    assert len(sample_df) > 0

def test_ticker_labels(sample_df):
    # aurait attrapé ton bug "AAPL en dur"
    assert set(sample_df['ticker'].unique()) == {'AAPL', 'MSFT'}

def test_prices_distinct(sample_df):
    # AAPL et MSFT ne peuvent pas avoir le même prix moyen
    a = sample_df[sample_df.ticker == 'AAPL']['close'].mean()
    m = sample_df[sample_df.ticker == 'MSFT']['close'].mean()
    assert a != m

def test_no_duplicates_after_double_store(tmp_path):
    # idempotence : stocker deux fois ne crée pas de doublons
    db = str(tmp_path / "test.duckdb")
    init_db(db)
    df = fetch_prices(['AAPL'], '2024-01-01', '2024-02-01')
    store_prices(df, db)
    store_prices(df, db)  # deuxième fois
    out = query_prices('AAPL', db)
    assert out.duplicated(subset=['date', 'ticker']).sum() == 0