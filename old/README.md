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

# References

A note on honesty: this list reflects the sources behind the methodological choices in this project. Where I cite a paper, I've actually read the abstract and key sections at minimum. Citations marked **★** are the ones I'd consider essential reading; the others are deeper context.

---

## Foundational papers — Post-Earnings Announcement Drift (PEAD)

- **★ Ball, R., & Brown, P. (1968).** "An Empirical Evaluation of Accounting Income Numbers." *Journal of Accounting Research*, 6(2), 159–178. — The original documentation of price drift after earnings announcements. The starting point for the entire literature.

- **★ Bernard, V. L., & Thomas, J. K. (1989).** "Post-Earnings-Announcement Drift: Delayed Price Response or Risk Premium?" *Journal of Accounting Research*, 27, 1–36. — Formalized PEAD analysis using Standardized Unexpected Earnings (SUE). Named the anomaly. Available via [JSTOR (2491062)](https://www.jstor.org/stable/2491062).

- **Bernard, V. L., & Thomas, J. K. (1990).** "Evidence that stock prices do not fully reflect the implications of current earnings for future earnings." *Journal of Accounting and Economics*, 13(4), 305–340. — The follow-up that strengthened the underreaction interpretation.

- **Chordia, T., & Shivakumar, L. (2006).** "Earnings and Price Momentum." *Journal of Financial Economics*, 80(3), 627–656. — Connects PEAD to price momentum; useful for understanding factor exposure of the strategy.

- **★ Livnat, J., & Mendenhall, R. R. (2006).** "Comparing the Post–Earnings Announcement Drift for Surprises Calculated from Analyst and Time Series Forecasts." *Journal of Accounting Research*, 44(1), 177–205. — The standard reference for *how* to compute SUE. Read this before implementing the surprise feature.

- **Fink, J. (2021).** "A review of the Post-Earnings-Announcement Drift." *Journal of Behavioral and Experimental Finance*, 29, 100446. — Large-scale modern review of the literature. Good single-source overview.

---

## Foundational papers — Factor models and momentum

- **★ Fama, E. F., & French, K. R. (1993).** "Common risk factors in the returns on stocks and bonds." *Journal of Financial Economics*, 33(1), 3–56. — The three-factor model (market, size, value). Required reading.

- **★ Fama, E. F., & French, K. R. (2015).** "A five-factor asset pricing model." *Journal of Financial Economics*, 116(1), 1–22. — Adds profitability (RMW) and investment (CMA). Modern factor benchmark. [DOI: 10.1016/j.jfineco.2014.10.010](https://doi.org/10.1016/j.jfineco.2014.10.010)

- **★ Jegadeesh, N., & Titman, S. (1993).** "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency." *Journal of Finance*, 48(1), 65–91. — The seminal momentum paper. Closely related to PEAD.

- **★ Carhart, M. M. (1997).** "On Persistence in Mutual Fund Performance." *Journal of Finance*, 52(1), 57–82. — Introduces the Carhart four-factor model (FF3 + momentum), the standard performance attribution model used in this project.

- **Ken French Data Library.** [https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) — Free factor return data used for the regression analysis in this project.

---

## Sentiment analysis and textual finance

- **★ Loughran, T., & McDonald, B. (2011).** "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks." *Journal of Finance*, 66(1), 35–65. — Developed the Loughran-McDonald financial sentiment dictionary, which still serves as a baseline against neural models. [DOI: 10.1111/j.1540-6261.2010.01625.x](https://doi.org/10.1111/j.1540-6261.2010.01625.x)

- **Loughran, T., & McDonald, B. (2016).** "Textual Analysis in Accounting and Finance: A Survey." *Journal of Accounting Research*, 54(4), 1187–1230. — Excellent survey of the field as of mid-2010s.

- **Loughran-McDonald Master Dictionary.** University of Notre Dame Software Repository for Accounting and Finance. [https://sraf.nd.edu/loughranmcdonald-master-dictionary/](https://sraf.nd.edu/loughranmcdonald-master-dictionary/) — Free word lists, regularly updated.

- **★ Araci, D. (2019).** "FinBERT: Financial Sentiment Analysis with Pre-trained Language Models." *arXiv:1908.10063*. — Introduced FinBERT, the BERT variant fine-tuned on financial text used in this project. [arXiv link](https://arxiv.org/abs/1908.10063)

- **ProsusAI/finbert on HuggingFace.** [https://huggingface.co/ProsusAI/finbert](https://huggingface.co/ProsusAI/finbert) — The actual model weights used in this project.

- **★ Ke, Z. T., Kelly, B. T., & Xiu, D. (2019).** "Predicting Returns with Text Data." *NBER Working Paper No. 26186*. — Modern supervised sentiment extraction tied directly to return prediction. Methodologically more sophisticated than off-the-shelf FinBERT. Worth understanding even if not implementing. [NBER link](https://www.nber.org/papers/w26186)

- **Tetlock, P. C. (2007).** "Giving Content to Investor Sentiment: The Role of Media in the Stock Market." *Journal of Finance*, 62(3), 1139–1168. — Earliest influential paper linking media sentiment to returns; conceptual foundation.

---

## Methodology — backtesting, validation, leakage prevention

- **★ López de Prado, M. (2018).** *Advances in Financial Machine Learning.* Wiley. ISBN: 978-1119482086. — The reference for ML applied to finance. Chapters 1–8 cover the core methodology used here: financial data structures, labeling, sample weighting, fractional differentiation, **purged k-fold CV with embargo** (chapter 7), feature importance, and backtest overfitting. This single book informs most of the validation methodology in this project.

- **López de Prado, M. (2018).** "The 10 Reasons Most Machine Learning Funds Fail." *Journal of Portfolio Management*, 44(6), 120–133. — Compact version of the book's main warnings; free preprint available on SSRN.

- **Bailey, D. H., & López de Prado, M. (2014).** "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality." *Journal of Portfolio Management*, 40(5), 94–107. — The formal correction for multiple-testing inflation of Sharpe ratios. Used in the robustness checks.

- **Harvey, C. R., Liu, Y., & Zhu, H. (2016).** "...and the Cross-Section of Expected Returns." *Review of Financial Studies*, 29(1), 5–68. — Documents how multiple-testing problems have produced many spurious "factors" in academic finance. Healthy skepticism vaccine.

- **Grinold, R. C. (1989).** "The Fundamental Law of Active Management." *Journal of Portfolio Management*, 15(3), 30–37. — The IR ≈ IC × √BR formulation cited in the project charter.

---

## Practitioner books

- **★ Grinold, R. C., & Kahn, R. N. (1999).** *Active Portfolio Management: A Quantitative Approach for Producing Superior Returns and Controlling Risk* (2nd ed.). McGraw-Hill. — The classic reference on information ratio, alpha, and factor-based active management. Chapters 1–7 are most relevant.

- **Chincarini, L. B., & Kim, D. (2006).** *Quantitative Equity Portfolio Management.* McGraw-Hill. — Practical companion to Grinold-Kahn, lighter on theory, heavier on implementation.

- **Pedersen, L. H. (2015).** *Efficiently Inefficient: How Smart Money Invests and Market Prices Are Determined.* Princeton University Press. — Excellent overview of how systematic strategies actually work in practice. Pedersen runs AQR's research.

- **Narang, R. K. (2013).** *Inside the Black Box: A Simple Guide to Quantitative and High-Frequency Trading* (2nd ed.). Wiley. — Accessible introduction to systematic strategies, less academic than Grinold-Kahn.

---

## Behavioral and market microstructure context

- **Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998).** "Investor Psychology and Security Market Under- and Overreactions." *Journal of Finance*, 53(6), 1839–1885. — Behavioral model of underreaction that PEAD is often used to support.

- **Hong, H., & Stein, J. C. (1999).** "A Unified Theory of Underreaction, Momentum Trading, and Overreaction in Asset Markets." *Journal of Finance*, 54(6), 2143–2184. — Models slow information diffusion across investors; theoretical foundation for why PEAD persists in small caps.

---

## Software and data sources

- **yfinance.** Python library for historical equity data via Yahoo Finance. [https://github.com/ranaroussi/yfinance](https://github.com/ranaroussi/yfinance)
- **Polygon.io.** Commercial market data API, used as fallback. [https://polygon.io](https://polygon.io)
- **Finnhub.** Free-tier API for earnings, estimates, and transcripts. [https://finnhub.io](https://finnhub.io)
- **SEC EDGAR.** Free authoritative source for US filings, including XBRL fundamentals. [https://www.sec.gov/edgar](https://www.sec.gov/edgar)
- **DuckDB.** In-process analytical SQL database used for local storage. [https://duckdb.org](https://duckdb.org)
- **vectorbt.** Python backtesting library used for the strategy implementation. [https://vectorbt.dev](https://vectorbt.dev)
- **LightGBM.** Gradient boosting framework. [https://lightgbm.readthedocs.io](https://lightgbm.readthedocs.io)
- **HuggingFace Transformers.** [https://huggingface.co/docs/transformers](https://huggingface.co/docs/transformers)

---

## Recommended starting order

If you have limited time, read in this order:

1. The Wikipedia article on PEAD for the lay-of-the-land.
2. Bernard & Thomas (1989) for the founding methodology.
3. López de Prado (2018), chapters 1, 3, 4, 7 — for the methodology that protects your backtest from itself.
4. Fama & French (2015) for what your strategy will be benchmarked against.
5. Loughran & McDonald (2011) for why naive sentiment fails on financial text.
6. Araci (2019) FinBERT paper for the modern approach you'll actually use.

Total: roughly 200 pages of careful reading. Aim for two weeks alongside Phase 1.