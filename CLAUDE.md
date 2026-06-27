# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

Quantitative research pipeline backtesting Post-Earnings Announcement Drift (PEAD) on S&P 600 SmallCap stocks. The strategy scores stocks by SUE (Standardized Unexpected Earnings), computes market-adjusted excess returns over a 21-trading-day holding window, and analyses return dispersion across SUE deciles.

## Commands

All commands assume the virtualenv is active: `source .venv/bin/activate`

```bash
# Run the full pipeline (fetches data, computes returns, saves plot)
cd src/pead && python main.py

# Run tests
pytest tests/

# Run a single test
pytest tests/test_data_prices.py::test_columns
```

**Known issue:** `tests/test_data_prices.py` imports `init_db` which was renamed to `init_prices_db` — the tests will fail until updated.

## Architecture

### Data flow

```
yfinance → fetch_prices() → DuckDB prices.db
yfinance → fetch_earnings() → compute_sue() → DuckDB earnings.db
prices.db + earnings.db → compute_all_returns() → SUE-decile plot
```

### Core modules (`src/pead/`)

**`earnings.py`** — EPS data and SUE computation
- `fetch_earnings(tickers)`: pulls up to 100 quarters of EPS history per ticker via `yf.Ticker.get_earnings_dates()`; computes `surprise = realized_eps − expected_eps`
- `compute_sue(df, window=8, min_periods=4)`: rolling std of surprise with `shift(1)` (no look-ahead); `sue = surprise / sigma`
- Storage: `init_earnings_db` / `store_earnings` / `load_earnings` against `earnings.db`

**`data_prices.py`** — OHLCV price history
- `fetch_prices(tickers, start, end)`: calls `yf.download` per ticker; normalises MultiIndex columns; stores `adj_close`, `close`, OHLV, `volume`
- Storage: `init_prices_db` / `store_prices` / `load_prices` / `query_prices` against `prices.db`
- `INSERT OR REPLACE` upsert semantics — safe to re-fetch and re-store

**`compute.py`** — Event-study return calculation
- `compute_event_return(announcement, ticker_prices_df, market_df, entry_offset=2, hold=21)`: enters `entry_offset` trading days after the announcement, exits `hold` days later; computes `stock_return − market_return` (market-adjusted, not factor-adjusted)
- Market benchmark is **IJR** (iShares S&P 600 ETF), fetched separately in `main.py`
- `compute_all_returns(earnings_df, prices_df, market_df)`: applies `compute_event_return` row-by-row, drops rows where SUE or excess return is NaN

### Storage

Two DuckDB files in `data/`:
- `prices.db` — table `prices (date DATE, ticker VARCHAR, adj_close, close, high, low, open, volume)`, PK `(date, ticker)`
- `earnings.db` — table `earnings (announcement DATE, ticker VARCHAR, realized_eps, expected_eps, surprise, sue, is_future, last_updated)`, PK `(announcement, ticker)`

### Universe

S&P 600 SmallCap tickers loaded from `s&p600list.txt`. `main.py` randomly samples 150 tickers per run (`random.seed(123)` for reproducibility).

## Key methodological constraints

- **No look-ahead in SUE:** `compute_sue` uses `shift(1)` so the sigma is computed from prior quarters only.
- **Entry offset = +2 trading days** after announcement: avoids overnight gap / stale quote issues.
- **Holding period = 21 trading days** (~1 calendar month).
- Every feature must have a verifiable "as-of" timestamp — cut anything that can't be proven knowable at trade time.

## What is not yet implemented

- Carhart 4-factor regression (factor data from Ken French Data Library)
- Walk-forward validation with purged/embargoed CV (López de Prado ch. 7)
- NLP/sentiment layer (FinBERT on earnings call transcripts)
- vectorbt backtest with transaction costs
- Point-in-time universe membership (current code uses today's S&P 600 list, introducing survivorship bias)
