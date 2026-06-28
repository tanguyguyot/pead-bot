# PEAD-ML — Document maître du projet

> Document de référence unique. Remplace les récaps précédents. Structure : contexte → problématique → méthode → avancement détaillé → prochaines étapes.

---

# PARTIE I — CADRAGE

## 1. Contexte

**Qui.** Data scientist junior français, fort en ML/Data Science, débutant en finance (apprend la finance au fil du projet). Démarre en septembre un graduate program chez **EFG Bank (Genève)**, côté IT/data technique.

**Pourquoi ce projet.** Construire un projet de portfolio qui démontre une rigueur méthodologique de niveau quant, pour servir de **levier de carrière** (recruteurs quant/fintech, évolution interne à EFG vers des rôles quant/portfolio analytics). Objectifs secondaires : monter en compétences réelles en ML appliqué à la finance ; éventuellement, si un signal exploitable émerge, l'utiliser avec un capital personnel modeste.

**Ce que le projet n'est PAS.** Pas une machine à fric. Les pistes "vendre des signaux / newsletter payante" ont été écartées (peu rentables + contraintes de compliance d'une banque privée). La vraie valeur = compétences + crédibilité professionnelle.

**Mode de travail.** L'utilisateur code lui-même ; l'assistant fournit théorie, specs et reviews franches, mais ne code pas à sa place (sauf boilerplate). Vérification empirique systématique ("la sortie réelle prime sur la théorie"). Langue : français.

## 2. Introduction au sujet : le PEAD

Le **Post-Earnings Announcement Drift** est une anomalie de marché documentée depuis Ball & Brown (1968) et formalisée par Bernard & Thomas (1989) : après une publication de résultats trimestriels qui **surprend** le marché, le cours continue de « dériver » dans la direction de la surprise pendant plusieurs semaines. Le marché **sous-réagit** à l'information, et cette sous-réaction se corrige lentement.

Cette anomalie contredit l'hypothèse d'efficience semi-forte des marchés. Elle est attribuée à : attention limitée des investisseurs, diffusion lente de l'information, révisions trop lentes des analystes, et contraintes d'arbitrage (surtout sur les small caps). Elle s'est **dégradée sur les large caps US** depuis ~2005 (arbitrage), mais resterait présente sur les segments moins efficients (small caps, marchés étrangers).

## 3. Problématique

> **Un modèle systématique exploitant la surprise sur résultats (mesurée par le SUE) peut-il générer un rendement excédentaire significatif sur les small caps US, net de coûts et de biais ?**

Décomposée en sous-questions (inspirées du cadre du PDF de référence étudié) :
1. **Existence** : une stratégie basée sur le SUE génère-t-elle un alpha significativement positif ?
2. **Monotonie/direction** : le rendement croît-il de façon monotone avec le SUE (signature classique du PEAD) ?
3. **Magnitude** : l'amplitude de la surprise (|SUE|) prédit-elle l'amplitude du rendement ?
4. **Robustesse** : le résultat survit-il aux coûts de transaction, au biais du survivant, et à différentes périodes ?

## 4. Méthode (vue d'ensemble)

**Univers.** S&P SmallCap 600 (small caps US à filtre de qualité). Sous-échantillon de ~150 tickers tirés aléatoirement (seed fixe). Choix motivé par : PEAD plus présent sur small caps ; liste publique accessible ; corroboré par le PDF étudié qui conclut que le PEAD est inexploitable sur large caps et suggère les small caps.

**Mesure de la surprise — le SUE (Standardized Unexpected Earnings) :**
```
surprise = EPS_réalisé − EPS_attendu (consensus analystes)
SUE = surprise / σ(8 dernières surprises, EXCLUANT le trimestre courant)
```
La standardisation rend les surprises comparables entre titres (régularité propre à chaque société). σ via fenêtre glissante avec `shift(1)` pour éviter la contamination par la surprise courante.

**Mesure du rendement — rendement excédentaire :**
```
excess_return = R_titre − R_benchmark   sur la fenêtre [entrée, sortie]
```
- Benchmark : **IJR** (ETF S&P 600), pour matcher l'univers.
- Entrée : **+2 séances** après l'annonce (jour 0). Le +2 neutralise l'incertitude sur l'heure de publication (after-hours/pre-market) et évite le « jump » initial non capturable, pour isoler le *drift*.
- Sortie : **+23 séances** (= +2 entrée + 21 séances de détention, fenêtre PEAD classique).
- Comptage en **séances de bourse** (positionnel via la table de prix comme calendrier), jamais en jours calendaires.

**Évolution méthodologique identifiée (à intégrer) :** remplacer le rendement excédentaire brut (qui suppose bêta=1) par un **rendement anormal via market model** : estimer α et β du titre en OLS sur ~120 séances pré-annonce, puis AR = R_réel − (α + β·R_marché), et CAR = somme des AR sur la fenêtre. C'est le standard académique des event studies (vu dans le repo GitHub étudié), plus rigoureux car il neutralise le bêta propre du titre. À adopter en phase de rigueur.

**Sources de données.** Prix ET earnings via **yfinance** (`get_earnings_dates(limit=100)` donne 50-100 trimestres sur small caps, gratuit, sans quota dur — découvert empiriquement après avoir éliminé FMP [small caps payantes], Finnhub [4 trimestres], Alpha Vantage [quota 25/jour]). Source validée par croisement externe.

**Stack technique.** Python 3.12, DuckDB (stockage colonnaire embarqué) + Parquet, pandas/numpy. À venir : statsmodels (tests + régressions), LightGBM, FinBERT, vectorbt. Repo `~/Code/pead-bot/`, package `src/pead/`.

**Garde-fous méthodologiques (les ennemis à combattre).**
- **Look-ahead bias** : jour 0 = date d'annonce (jamais fin de période fiscale) ; σ du SUE sur surprises passées uniquement ; période out-of-sample jamais touchée jusqu'au test final.
- **Survivorship bias** : univers basé sur composition 2026 → rendements probablement optimistes. **Assumé et documenté** ; correction point-in-time (historique des delistings) = chantier futur difficile.
- **Cohérence des données** : dates en `datetime64` naïf partout ; mapping par nom ; idempotence ; winsorisation des SUE extrêmes.

---

# PARTIE II — AVANCEMENT DÉTAILLÉ

## 5. Ce qui est FAIT et VALIDÉ (Semaine 1-2)

### Couche prix (`prices.py`)
Table DuckDB `prices` (date, ticker, adj_close, close, high, low, open, volume), PK (date, ticker). `fetch_prices` : yfinance `auto_adjust=False` (garde close brut ET ajusté), dates normalisées `datetime64[us]` naïf, dropna, gestion d'erreur par ticker, dédoublonnage. Idempotent. Lecture via `load_prices`.

### Couche earnings (`earnings.py`)
Table `earnings` (announcement, ticker, realized_eps, expected_eps, surprise, sue, is_future, last_updated), PK (announcement, ticker). `fetch_earnings` : yfinance, **normalisation date AVANT dédoublonnage** (sinon doublons masqués par l'heure), surprise recalculée à la main. `compute_sue` : σ glissant via `groupby('ticker')['surprise'].transform(shift(1).rolling(8,min4).std())`.

### Croisement prix × earnings
`compute_event_return` : `searchsorted` positionnel pour le jour 0, gardes de bornes (haute ET basse), prix titre par position / marché par date, filtres qualité (prix brut > 5$, dollar-volume moyen 20j > 1M$). `compute_all_returns` : pré-groupe les prix en dict, boucle sur événements, accumule, dropna.

### Validation de yfinance comme source
- Cohérence interne (30 tickers) : doublons rares (corrigés), trous légitimes (cycle annuel), pas de corruption.
- Croisement externe (ADMA, UNFI, DGII) : dates parfaites, réalisé excellent, estimé cohérent (variabilité mineure documentée).

## 6. RÉSULTATS obtenus (état actuel)

Pipeline sur **131 tickers, 6601 événements**. Graphe rendement moyen/médian par décile de SUE, avant et après winsorisation + filtres qualité.

**Résultat principal : PAS de PEAD directionnel monotone.** Le pattern est un **U** : les deux extrêmes (grosses surprises positives ET négatives) ont un rendement positif, le milieu est plat/négatif. Les filtres et la winsorisation ne changent pas cette structure. Forte asymétrie (moyenne ≫ médiane partout) → rendements tirés par une minorité de valeurs extrêmes.

**Interprétation (hypothèses) :**
1. C'est peut-être la **magnitude** (|SUE|), pas la direction, qui compte → à tester (Piste 1).
2. Le décile bas positif s'explique peut-être par **sur-réaction puis rebond** (en entrant à +2 on capture le rebond, pas la baisse).
3. Ou par le **biais du survivant** (les small caps à mauvaise surprise survivantes sont les rescapées).

**Ce résultat « négatif » est une réussite méthodologique**, pas un échec — rigueur et lucidité. **Corroboré indépendamment** par le PDF étudié (PEAD naïf inexploitable, magnitude non prédictive : 1 titre sur 11 sensible).

## 7. Apports des recherches externes (PDF + repo GitHub)

**Du PDF (Aaron & Dmitri, large caps, fenêtre 3j) — à reprendre :** cadre statistique rigoureux = **t-test + Wilcoxon** (exiger les deux), **régression alpha ~ log(surprise)** avec test de pente, vérif normalité (Shapiro-Wilk, Q-Q), analyse par sous-groupes. Confirme le choix small caps.

**Du repo GitHub (outil PEAD, actions NSE) — à considérer :** le **market model + CAR** (estimer β sur 120j pré-annonce, calculer rendement anormal) au lieu de l'excès brut — standard des event studies, neutralise le bêta. Eux n'ont PAS de backtesting (le tien ira plus loin).

**Points où ce projet est déjà supérieur :** SUE standardisé (vs surprise brute/YoY), estimations analystes réelles, fenêtre 21j fidèle au PEAD (vs 3j), entrée +2 mieux raisonnée, backtesting rigoureux à venir, FinBERT prévu (vs TextBlob).

---

# PARTIE III — PROCHAINES ÉTAPES

## 8. Immédiat (finir l'exploration — Semaine 2)
1. **Tests statistiques** (reprise du PDF) : t-test + Wilcoxon sur l'alpha des déciles extrêmes ; régression alpha ~ |SUE| avec test de pente (= Piste 1 formalisée). Transforme les graphes descriptifs en résultats étayés. **Priorité haute, rapide, fort impact.**
2. Tester le classement par **|SUE|** (magnitude) vs SUE signé.
3. Optionnel : tester l'offset d'entrée (+1 vs +2) pour départager sur-réaction/rebond.
4. **Commit + documenter** le pattern en U et les hypothèses.

## 9. Semaine 3 (cœur méthodologique)
Formaliser une **stratégie backtestée rigoureusement** :
- Baseline naïve d'abord (à battre pour justifier le ML).
- Métriques : Sharpe, Sortino, **Information Ratio**, max drawdown, Calmar, t-stat, **Deflated Sharpe**.
- **Coûts de transaction** (20 bps round-trip, sensibilité 10/30/50).
- **Walk-forward** + **purged & embargoed CV** (embargo 21j).
- Régression Fama-French 5F + momentum pour isoler l'alpha.
- Envisager le passage au **market model/CAR** ici (rigueur).

## 10. Phases ultérieures
- Phase 3 : feature engineering (fondamentaux, technique, cross-sectional, microstructure) + winsorisation systématique.
- Phase 4 : modèle LightGBM (purged walk-forward CV).
- Phases 6-7 : sentiment FinBERT (news + transcripts).
- Phase 8 : test out-of-sample final (jamais touché avant).
- Phase 9 : writeup, dashboard Streamlit, dockerisation, GitHub Actions.
- Extensions : small caps européennes (STOXX Europe Small 200) ; correction du biais du survivant.

## 11. Références clés
Ball & Brown (1968), Bernard & Thomas (1989/1990), Livnat & Mendenhall (2006) [SUE], Fama-French (1993/2015), Carhart (1997), Jegadeesh-Titman (1993), Loughran-McDonald (2011), Araci (2019) [FinBERT], López de Prado (2018) [purged CV, Deflated Sharpe], Grinold-Kahn (1999). Loi de Grinold : IR ≈ IC × √breadth.