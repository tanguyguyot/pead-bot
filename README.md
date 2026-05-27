# PEAD-ML: A Quant Research Project on Post-Earnings Announcement Drift

## Phase 0 — Project Charter

**Author:** [Your name]
**Date:** May 2026
**Status:** Locked

---

## 1. Project purpose

Build a portfolio-grade quantitative research pipeline that tests whether a machine learning model combining fundamentals, technicals, and earnings-call sentiment can systematically exploit Post-Earnings Announcement Drift (PEAD) in US small-cap equities.

The project optimizes for three outcomes, in order of priority:

1. **Demonstrate rigorous methodology** suitable for a quant research portfolio.
2. **Generate genuine learning** in finance theory, time-series ML, and research infrastructure.
3. **Optional:** if results are robust, deploy with modest personal capital.

The project does **not** optimize for: selling signals, building a newsletter, or any third-party monetization.

---

## 2. Hypothesis

> Among Russell 2000 constituents, stocks with extreme positive (negative) Standardized Unexpected Earnings (SUE), confirmed by positive (negative) earnings-call sentiment and supportive technical context, exhibit predictable cross-sectional return differentials over a 21-trading-day horizon, net of standard factor exposures (market, size, value, momentum, profitability) and transaction costs.

**Null hypothesis:** No statistically significant alpha after controlling for Fama-French 5-factor + momentum exposures.

**Falsifiable success criterion:** see Section 6.

---

## 3. Universe

- **Primary universe:** Russell 2000 constituents (US small caps).
- **Point-in-time correctness:** universe membership must reflect index composition at each historical date, not today's composition.
- **Filters applied:**
  - Stock price > $5 at earnings date (avoid penny stocks where costs dominate).
  - Average daily dollar volume > $1M over prior 20 days (liquidity floor).
  - Excluded: ADRs, REITs, BDCs, SPACs (different earnings dynamics).
- **Universe data source:** iShares IWM holdings history (manual) or CRSP via WRDS if accessible; fallback is approximation via Russell reconstitution dates (June each year).
- **Phase 7 extension:** STOXX Europe Small 200 once US pipeline is validated.

---

## 4. Strategy specification

### Signal generation

For each earnings announcement in the universe:

- **Event window:** earnings announcement date = day 0.
- **Information cutoff:** all features must use data available by end of day +1 (to capture post-announcement reaction and call transcript).
- **Prediction target:** cumulative excess return over Russell 2000 from day +2 close to day +23 close (21 trading days).

### Two parallel strategy implementations

**Track A — Academic long-short decile portfolios:**
- Each Friday, score all stocks that had earnings in the prior 5 trading days.
- Long top decile, short bottom decile.
- Equal-weighted within deciles.
- Hold 21 trading days.
- Rebalance weekly (overlapping portfolios).
- Use for academic-style backtest, factor analysis, GitHub writeup.

**Track B — Retail-executable long-only:**
- Same scoring, but long-only top quintile.
- Maximum 10 concurrent positions.
- Equal-weighted position sizing.
- Hold 21 trading days unless stop-loss hit (-15% from entry).
- Cash when fewer than 3 signals available.
- Use to answer "could I actually trade this?"

### Out of scope (Phase 0)

- Options, leveraged ETFs, intraday execution.
- Macro overlays (regime filters, VIX-based switching).
- Position sizing optimization (Kelly, risk parity) — equal-weight only for v1.

---

## 5. Features (planned)

To be refined in Phase 3, but locking the categories now:

| Category | Examples | Source |
|----------|----------|--------|
| Earnings surprise | SUE (EPS), revenue surprise, guidance change | I/B/E/S via WRDS or Finnhub/FMP |
| Fundamentals | YoY revenue growth, margin trend, leverage, ROIC | SEC EDGAR (XBRL) or FMP |
| Technicals | 3m/6m/12m momentum, volatility, RSI, distance from 200dma, volume z-score | yfinance / Polygon |
| Sentiment (announcement) | FinBERT score on PR headline + first 500 words | NewsAPI + headline scrape |
| Sentiment (call) | FinBERT on call transcript Q&A vs prepared remarks | Finnhub transcripts or scraping |
| Cross-sectional | Sector-relative rank for above features | Computed |
| Microstructure | Day 0 volume spike, day 0–1 return, gap | Computed |

**Hard rule:** every feature must have a verifiable "as-of" timestamp. If I can't prove a feature was knowable at the time, it's cut.

---

## 6. Success criteria

These are committed to **before** seeing results.

### Primary success criteria (must hit all three)

1. **Information Ratio > 0.5** on Track A, net of 10 bps round-trip costs, over 2021–2024 out-of-sample period.
2. **Statistically significant alpha** at p < 0.05 in Fama-French 5-factor + momentum regression.
3. **Beats naive SUE-only baseline** (no ML, no sentiment) by ≥ 20% in risk-adjusted terms on the same period.

### Robustness checks

- Max drawdown < 1.5x Russell 2000 max drawdown over same period.
- Performance positive in at least 3 of 4 out-of-sample years.
- Deflated Sharpe Ratio (López de Prado) remains positive after correction.
- No single year accounts for >50% of total alpha.

### Honesty commitment

The full project is published regardless of outcome. If hypothesis fails, the writeup pivots to "Why naive PEAD doesn't work in 2020s small caps: a post-mortem." This is equally portfolio-worthy.

---

## 7. Data sources (Phase 1 will validate)

| Need | Primary | Fallback | Cost |
|------|---------|----------|------|
| Prices, splits, dividends | yfinance | Polygon.io | Free / $30/mo |
| Russell 2000 historical membership | iShares IWM holdings archive | Manual reconstitution | Free / time |
| Earnings dates + estimates | Finnhub free tier | FMP, Yahoo | Free / $30/mo |
| Earnings call transcripts | Finnhub | Manual scrape from press releases | Free / time |
| Fundamentals | SEC EDGAR (XBRL) | FMP, SimFin | Free |
| News headlines | NewsAPI free tier | RSS aggregation | Free / $50/mo |
| Factor returns | Ken French data library | — | Free |

**Budget cap:** €0–50/month for data. Anything above this needs to demonstrate clear value first.

---

## 8. Validation methodology

- **Walk-forward, expanding window.**
  - Initial training: 2015–2018.
  - First test fold: 2019. Then retrain through 2019, test 2020. Etc.
- **Purged and embargoed cross-validation** (López de Prado) for hyperparameter tuning within each training period. Embargo = 21 days (matches holding period).
- **No peeking at 2021–2024.** Final out-of-sample period touched only once, at the end. If I look at it and re-tune, I lose all statistical validity.
- **Realistic costs:** 5 bps commission + 5 bps slippage = 10 bps each side, 20 bps round-trip. Sensitivity analysis at 10 / 30 / 50 bps.

---

## 9. Tech stack (locked)

- **Language:** Python 3.11+.
- **Data store:** DuckDB + Parquet (local, no cloud needed for this scale).
- **ML:** scikit-learn for baselines, LightGBM for main model. PyTorch only if Phase 5 explores deep learning.
- **NLP:** HuggingFace transformers, FinBERT (`ProsusAI/finbert`).
- **Backtest:** vectorbt (fast, Pythonic) for v1; possibly Zipline-Reloaded later.
- **Analysis:** pandas, numpy, statsmodels (factor regressions), scipy.
- **Visualization:** matplotlib + seaborn for static, Plotly for interactive.
- **Repo:** GitHub, public from day 1. README updated weekly.
- **Environment:** uv for dependency management, pyproject.toml.

---

## 10. Out-of-scope (explicit non-goals)

To prevent scope creep, the following are explicitly **not** part of this project:

- Live trading infrastructure (broker API integration, order management).
- Real-time data pipelines (everything is end-of-day batch).
- Options or derivatives.
- Cryptocurrency.
- Web frontend beyond a simple Streamlit dashboard at the end.
- Multi-asset portfolio construction (no bonds, commodities, FX).
- ESG, alternative data beyond news sentiment.
- Reinforcement learning approaches.

If something feels essential later, it gets added as Phase 8+, after v1 ships.

---

## 11. Deliverables

At project end:

1. **Public GitHub repository** with reproducible code, README, environment file.
2. **Written research report** (~15–25 pages, PDF) covering hypothesis, methodology, results, honest discussion of limitations. Modeled on academic finance papers but accessible.
3. **Streamlit dashboard** showing strategy performance, feature importances, current signals.
4. **One blog post** (your own site or Medium) summarizing the project for a technical-but-non-finance audience.
5. **Optional:** TikTok vulgarization videos on individual concepts (factor models, PEAD, sentiment analysis) — at your discretion.

---

# Timeline — 8 to 10 weeks to v1

You're at home full-time until September, so I'm assuming roughly 25–30 hours/week available for the project (leaving plenty of room for life). This timeline is aggressive but reasonable, with a working end-to-end pipeline by week 5 and refinements through week 9.

**Critical principle:** finish an ugly end-to-end version first, *then* improve each piece. Do NOT spend 3 weeks perfecting data ingestion before any model has been trained. The biggest mistake juniors make is over-investing in early phases.

## Week 1 — Foundations and minimal data

**Goals:**
- Repo set up (GitHub, uv, pyproject.toml, pre-commit hooks, README skeleton).
- DuckDB store initialized.
- Russell 2000 universe loaded for one snapshot date (start with today's, fix point-in-time in week 2).
- Daily prices for ~500 stocks downloaded via yfinance (subset to start).
- Read Bernard & Thomas (1989) and Chordia & Shivakumar (2006).

**Deliverable:** repo exists, you can query "give me 1 year of prices for AAPL" from your local store.

## Week 2 — Earnings data and point-in-time universe

**Goals:**
- Finnhub API integration for earnings dates and estimates.
- Compute SUE for every earnings event in your universe, 2015–2024.
- Solve point-in-time universe: download iShares IWM historical holdings or build approximation via Russell reconstitution dates.
- Sanity checks: plot distribution of SUE, count events per year, check for obvious data errors.

**Deliverable:** a `earnings_events` table with ~30,000+ rows of (ticker, date, SUE, etc.).

## Week 3 — Naive PEAD baseline (the MOST IMPORTANT week)

**Goals:**
- Implement vanilla PEAD: rank by SUE quintile, long top / short bottom, hold 21 days.
- Build minimal backtest in vectorbt.
- Compute first set of metrics: Sharpe, IR, max DD, hit rate.
- Run on 2015–2024 with no ML, no sentiment.

**Why this week matters:** you now have a baseline number to beat. Every fancy thing you add later must justify itself against this. If naive PEAD gives IR 0.4, your ML+sentiment must get >0.5 net of costs, or it added nothing.

**Deliverable:** one notebook, one chart: "naive PEAD on Russell 2000, 2015–2024." Possibly a blog post.

## Week 4 — Feature engineering (non-sentiment)

**Goals:**
- Add technical features: momentum windows, volatility, volume spikes, RSI.
- Add cross-sectional ranks within sector.
- Add microstructure features: day 0 return, gap, volume z-score.
- Pull basic fundamentals from FMP or EDGAR (revenue growth, margins).

**Deliverable:** feature matrix joined to earnings events, ready for ML.

## Week 5 — First ML model + walk-forward validation

**Goals:**
- LightGBM regression model predicting 21-day excess return.
- Implement purged + embargoed walk-forward CV (this is the hard part — budget 2–3 days).
- Train on 2015–2018, test on 2019. Compare to naive baseline.
- Run factor regression on strategy returns.

**Deliverable:** **end-to-end pipeline working.** This is your v0.5. Everything from here is refinement.

## Week 6 — Sentiment layer (FinBERT)

**Goals:**
- Set up FinBERT inference pipeline (HuggingFace, can run on CPU for small batches).
- Get earnings press release headlines + first paragraph for each event.
- Compute sentiment scores, add to feature matrix.
- Retrain model, measure incremental improvement.

**Deliverable:** sentiment features integrated, ablation study showing their marginal contribution.

## Week 7 — Earnings call transcripts (the ambitious part)

**Goals:**
- Source transcripts (Finnhub or scraping). Start with subset — top 200 most-traded names — to validate before scaling.
- Separate Q&A from prepared remarks (Q&A is more informative per literature).
- FinBERT on transcript sections.
- Add as features, ablation study.

**Risk:** transcript data is messy. If sourcing kills the week, simplify to "headline + press release sentiment only" and call it done. Don't let this phase eat the project.

**Deliverable:** transcript sentiment integrated OR documented as "tried, here's why I scoped it down."

## Week 8 — Full out-of-sample test (the moment of truth)

**Goals:**
- Lock all model choices, hyperparameters.
- Run on 2021–2024 walk-forward. **Do not look at these results until the model is locked.**
- Compute all success criteria from Section 6.
- Run robustness checks: regime analysis, drawdowns, factor exposures.

**Deliverable:** verdict. Did the hypothesis hold? If yes, celebrate briefly then write up. If no, diagnose and write up the post-mortem.

## Week 9 — Writeup and dashboard

**Goals:**
- Research report (PDF, ~15–25 pages).
- Streamlit dashboard showing key results.
- README polished, repo cleaned, examples runnable.
- Blog post drafted.

**Deliverable:** project shippable. Recruiter-ready.

## Week 10 — Buffer / European extension start

**Goals:**
- If on schedule: start STOXX Europe Small 200 port as Phase 7.
- If behind: catch up, refine, polish.
- Either way: post the GitHub link publicly.

---

## Risk register

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Data sourcing eats weeks 1–3 | High | Start with yfinance + Finnhub free tiers, don't optimize early |
| Transcript data infeasible | Medium | Fallback to headline sentiment only |
| Strategy doesn't beat baseline | Medium | Honest writeup as a post-mortem is still portfolio-worthy |
| Scope creep (deep learning, options, etc.) | High | Section 10 is the law |
| Burnout from 25h/week intensity | Medium | Plan 1 full day off per week, no exceptions |
| September arrives, project unfinished | Medium | Week 8 is the hard cutoff for new features |

---

## Definition of done

The project is "done" when:

1. The GitHub repo is public, well-documented, and runs end-to-end with one command.
2. The research report is published.
3. The strategy has been honestly evaluated against the Section 6 criteria.
4. You can defend every methodological choice in a 1-hour conversation with a quant researcher.

That's the bar. Anything beyond is bonus.# pead-bot
