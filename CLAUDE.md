# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

Quantitative research pipeline backtesting Post-Earnings Announcement Drift (PEAD) on S&P 600 SmallCap stocks. The strategy scores stocks by SUE (Standardized Unexpected Earnings), computes market-adjusted excess returns over a 21-trading-day holding window, and analyses return dispersion across SUE deciles.

`CONTEXT.md` is the project's master document (in French) — read it for the research hypothesis, current results, and roadmap. Key finding so far: there is **no monotonic directional PEAD** on this universe; returns form a U-shape across SUE deciles (both extremes positive), driven by a minority of extreme names.

## Working language

The user works in **French** and codes themselves — provide theory, specs, and frank reviews, but do not write code in their place beyond boilerplate. Empirical verification beats theory ("the actual output wins over the theory").

## Commands

All commands assume the virtualenv is active: `source .venv/bin/activate`

```bash
# Run the full pipeline (fetches data, computes returns, saves decile plot to ../plots/)
cd src/pead && python main.py

# Run tests
pytest tests/

# Run a single test
pytest tests/test_data_prices.py::test_columns
```

**`main.py` must be run from `src/pead/`** — it uses bare imports (`from compute import *`) and relative paths (`../data/`, `../plots/`, `../s&p600list.txt`).

**Known test issues** in `tests/test_data_prices.py` (currently failing):
- imports `init_db`, which was renamed to `init_prices_db`
- imports from the `pead.data_prices` package path, but the package is not installed and there is no `pyproject.toml`/`setup.py`; `src/` must be on `PYTHONPATH`.

## Architecture

### Data flow

```
yfinance → fetch_prices() → DuckDB prices.db
yfinance → fetch_earnings() → compute_sue() → DuckDB earnings.db
prices.db + earnings.db → compute_all_returns() → SUE-decile plot
```

### Core modules (`src/pead/`)

**`earnings.py`** — EPS data and SUE computation
- `fetch_earnings(tickers)`: pulls up to 100 quarters of EPS history per ticker via `yf.Ticker.get_earnings_dates()`; normalises announcement dates **before** dedup (otherwise intraday timestamps mask duplicates); computes `surprise = realized_eps − expected_eps` by hand
- `compute_sue(df, window=8, min_periods=4)`: rolling std of surprise with `shift(1)` (no look-ahead); `sue = surprise / sigma`; drops `is_future` rows and `inf` SUE (sigma=0)
- Storage: `init_earnings_db` / `store_earnings` / `load_earnings` against `earnings.db`

**`data_prices.py`** — OHLCV price history
- `fetch_prices(tickers, start, end)`: calls `yf.download` per ticker with `auto_adjust=False` (keeps both raw `close` and `adj_close`); normalises MultiIndex columns and dates to naive `datetime64[us]`
- Storage: `init_prices_db` / `store_prices` / `load_prices` / `query_prices` against `prices.db`
- `ON CONFLICT DO UPDATE` upsert semantics — idempotent, safe to re-fetch and re-store

**`compute.py`** — Event-study return calculation
- `compute_event_return(announcement, ticker_prices_df, market_df, entry_offset=2, hold=21, min_price=5, min_dollar_volume=1e6)`: locates day 0 via positional `searchsorted` on the price table (used as a trading-day calendar); enters `entry_offset` trading days after the announcement, exits `hold` days later; returns `stock_return − market_return` (market-adjusted, **not** factor-adjusted). Quality filters: raw entry `close` > $5, and 20-day mean dollar-volume before the announcement > $1M.
- Market benchmark is **IJR** (iShares S&P 600 ETF), fetched separately in `main.py` (note: a `print` in `main.py` mislabels it "IJW").
- `compute_all_returns(earnings_df, prices_df, market_df)`: pre-groups prices into a dict, applies `compute_event_return` row-by-row, drops rows where SUE or excess return is NaN

### Storage

Two DuckDB files in `data/`:
- `prices.db` — table `prices (date, ticker, adj_close, close, high, low, open, volume)`, PK `(date, ticker)`
- `earnings.db` — table `earnings (announcement, ticker, realized_eps, expected_eps, surprise, sue, is_future, last_updated)`, PK `(announcement, ticker)`

### Universe

S&P 600 SmallCap tickers loaded from `s&p600list.txt`. `main.py` uses `random.choices(..., k=150)` (sampling **with replacement**, `random.seed(123)` for reproducibility) — draws may repeat.

## Key methodological constraints

- **No look-ahead in SUE:** `compute_sue` uses `shift(1)` so sigma comes from prior quarters only. Day 0 is always the announcement date, never the fiscal period end.
- **Entry offset = +2 trading days** after announcement: neutralises after-hours/pre-market publication-time uncertainty and the non-capturable initial jump, isolating the drift.
- **Holding period = 21 trading days** (~1 calendar month); counted in trading sessions via the price table, never calendar days.
- **Survivorship bias is assumed and documented:** the universe uses today's S&P 600 list, so returns are likely optimistic. Point-in-time membership is a future chantier.
- Every feature must have a verifiable "as-of" timestamp — cut anything that can't be proven knowable at trade time.

## What is not yet implemented

- Statistical tests on decile alpha (t-test + Wilcoxon; regression of return on |SUE|)
- Market model / CAR (OLS β on ~120 pre-announcement sessions) to replace raw excess return
- Carhart / Fama-French factor regression (factor data from Ken French Data Library)
- Walk-forward validation with purged/embargoed CV (López de Prado, embargo = 21 days)
- LightGBM model; NLP/sentiment layer (FinBERT on earnings transcripts)
- vectorbt backtest with transaction costs (20 bps round-trip, sensitivity 10/30/50)
