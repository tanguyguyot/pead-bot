## Finance theory you need to know

I'll structure this as: (1) the conceptual foundations, (2) the specific PEAD literature, (3) the metrics for evaluating strategies, (4) the practitioner concepts. I'll keep it dense but linear.

### 1. Conceptual foundations

**Efficient Market Hypothesis (EMH).** Three forms — weak (prices reflect past prices), semi-strong (prices reflect all public info), strong (prices reflect all info, including private). Reality: markets are *mostly* efficient *most* of the time, but pockets of inefficiency exist, especially in less-covered names (small caps, foreign markets). Your entire project is a bet that semi-strong efficiency is incomplete in small caps. This is academically defensible — see Fama-French's later work conceding factor anomalies.

**Factor investing.** The dominant modern paradigm. Returns are decomposed into exposure to common factors:
- **Market (beta):** the most basic — does it move with the market?
- **Size (SMB, Small Minus Big):** small caps historically outperform large caps long-term (with more volatility).
- **Value (HML, High Minus Low book-to-market):** cheap stocks outperform expensive ones.
- **Momentum (UMD/MOM):** recent winners keep winning over 3–12 month horizons. *This is the factor most related to PEAD.*
- **Quality:** profitable, low-leverage firms outperform.
- **Low volatility:** boring stocks have better risk-adjusted returns than theory predicts.

The Fama-French 3-factor (market, size, value), 5-factor (+ profitability, investment), and Carhart 4-factor (+ momentum) models are essential reading. When you backtest a strategy, you need to show its returns aren't just exposure to these known factors — that's called "alpha" (excess return after controlling for factor exposures). **A strategy with high returns but high momentum loading isn't generating alpha, it's just a momentum bet.**

**Risk premia vs anomalies.** A risk premium is compensation for bearing risk (e.g., stocks pay more than bonds because they're riskier). An anomaly is a return pattern that *can't* be explained by risk — it's a market inefficiency. PEAD is widely considered an anomaly (limited attention, slow information diffusion), not a risk premium. This matters because anomalies can be arbitraged away, while risk premia persist.

### 2. The PEAD literature specifically

**The original finding (Bernard & Thomas, 1989, 1990).** After a positive earnings surprise, stocks drift up for 60+ trading days. After a negative surprise, they drift down. The drift is monotonic in surprise magnitude. The proposed explanation: investors under-react to earnings news, especially the implications for future earnings.

**The standard surprise metric: SUE (Standardized Unexpected Earnings).**

$$SUE = \frac{\text{Actual EPS} - \text{Expected EPS}}{\sigma(\text{Earnings})}$$

Where expected EPS is either analyst consensus (I/B/E/S) or a time-series model. The standardization matters — a $0.05 beat on a high-volatility earner is different from $0.05 on a stable utility.

**Why PEAD persists (proposed explanations):**
- Limited investor attention (especially in small caps with low coverage)
- Anchoring bias — analysts revise forecasts too slowly
- Transaction costs / short-sale constraints limiting arbitrage (especially small caps)
- Risk-based explanations (less popular now)

**Modern refinements:**
- *Earnings call sentiment matters as much as the number.* Loughran-McDonald financial dictionary, FinBERT, and more recently LLM-based extraction of forward guidance.
- *Revenue surprise matters separately from EPS surprise.*
- *Guidance changes* (management forward guidance) often matter more than the print itself.
- *PEAD is stronger when accompanied by analyst revisions in the same direction.*
- *PEAD is stronger for "extreme" surprises and weaker for marginal ones.*

**Required reading (genuinely required, not just suggested):**
- Bernard & Thomas (1989) "Post-Earnings-Announcement Drift" — the original.
- Chordia & Shivakumar (2006) "Earnings and Price Momentum" — connects PEAD to momentum.
- Loughran & McDonald (2011) on textual analysis in finance.
- Ke, Kelly & Xiu (2019) on FinBERT-style sentiment + returns.

### 3. Strategy evaluation metrics

You need to internalize these. Reporting just "annualized return" marks you as an amateur.

**Return metrics:**
- **CAGR (Compound Annual Growth Rate):** the geometric mean annual return.
- **Excess return:** return above benchmark (e.g., Russell 2000).
- **Alpha (Jensen's alpha):** return above what's predicted by factor exposures. Run a regression of strategy returns on factor returns; the intercept is alpha.

**Risk-adjusted metrics (the real stuff):**
- **Sharpe ratio:** (Return − Risk-free rate) / Volatility. Higher = better. Above 1.0 is good, above 2.0 is suspiciously good for retail.
- **Sortino ratio:** like Sharpe but only penalizes downside volatility. More forgiving but more relevant.
- **Information Ratio (IR):** (Strategy return − Benchmark return) / Tracking error. This is what hedge funds actually care about. IR > 0.5 is decent, > 1.0 is excellent.
- **Calmar ratio:** CAGR / Max Drawdown. Good for understanding pain.
- **Max Drawdown:** the worst peak-to-trough decline. Critical for understanding if you'd survive psychologically.

**Trade-level metrics:**
- **Hit rate / win rate:** % of trades that are profitable. *Less important than people think* — you can be profitable with 40% hit rate if your winners are bigger than losers.
- **Profit factor:** gross profit / gross loss. Above 1.5 is decent.
- **Average win / average loss ratio.**

**Statistical robustness:**
- **t-statistic of returns:** is your edge statistically significant or noise? A Sharpe of 0.5 over 10 years is more credible than Sharpe of 2.0 over 1 year.
- **Deflated Sharpe Ratio (López de Prado):** corrects Sharpe for multiple testing / backtest overfitting. Critical concept.

### 4. Practitioner concepts that separate amateurs from pros

**Look-ahead bias.** Using information that wouldn't have been available at the time. Example: using "restated" financials from EDGAR when at the time the original (later-restated) version was published.

**Survivorship bias.** Backtesting on today's index constituents instead of point-in-time constituents. Stocks that went bankrupt or got delisted aren't in your universe today, so you systematically over-estimate returns.

**Data snooping / p-hacking.** Trying 50 strategies, finding one that works, claiming victory. Statistically, by chance alone, 2–3 of 50 will look great. *This is the single biggest sin in quant research.* Solution: pre-register your hypotheses (write down what you'll test *before* you test it), then test on hold-out data you've never touched.

**Transaction costs.** Bid-ask spreads, broker commissions, slippage (market impact when you trade). For small caps, total round-trip costs are often 20–50 bps, not 5–10. This destroys most paper strategies.

**Capacity.** How much capital can the strategy absorb before it stops working? Small-cap strategies often have low capacity — works for €100k, doesn't for €100M. *This actually plays in your favor as a retail-scale researcher.*

**Regime dependence.** A strategy that worked 2010–2019 might die 2020–2023. Market regimes (bull, bear, high-vol, low-vol, rising rates, falling rates) matter. Always look at strategy performance by regime.

**Walk-forward validation.** Train on 2015–2018, test on 2019. Then retrain on 2015–2019, test on 2020. Repeat. This mimics how you'd actually deploy. K-fold cross-validation is invalid for time series.

**Purged and embargoed CV (López de Prado).** When labels span multiple days (e.g., "21-day return"), training and test sets can leak into each other even with simple train/test splits. You need to "purge" overlapping observations and add an "embargo" buffer. This is technical but critical.

### Books to actually read (prioritized)

1. **"Active Portfolio Management" — Grinold & Kahn.** The hedge fund bible on alpha, information ratio, factor models. Dense but foundational. Read chapters 1–7.
2. **"Advances in Financial Machine Learning" — Marcos López de Prado.** The modern ML-for-finance reference. Read chapters 1–8 carefully. Skip later chapters initially.
3. **"Quantitative Equity Portfolio Management" — Chincarini & Kim.** More practical, less theoretical.
4. **Fama & French's papers on the 3-factor and 5-factor models.** Free online, ~30 pages each.

For PEAD specifically, read the original Bernard & Thomas papers — they're shorter than you'd expect and remarkably readable.

### One more concept I want to flag for you

**"The Grinold Fundamental Law of Active Management":**

$$IR \approx IC \times \sqrt{BR}$$

Where IR is information ratio, IC is the "information coefficient" (correlation between your forecast and realized returns), and BR is the breadth (number of independent bets per year).

This formula is profound. It says: even a *tiny* edge (IC = 0.05, basically noise) can produce a meaningful IR if you make many independent bets. This is why systematic small-cap strategies work — you're making 100s of small, weakly-predictive bets, not 5 big confident ones. Internalize this.

---

That's the theory dump. Once you've digested it (or at least know it exists and can come back to it), reply and I'll write the Phase 0 one-pager with concrete decisions locked in. I'll also include a 4-month timeline aligned with your September start date at EFG.


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