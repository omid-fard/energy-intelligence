# Energy Intelligence ⚡

**German Electricity Market Analytics · Negative Power Prices · Renewable Energy · Transparent ML Forecasting**

**Energy Intelligence** is an open-source, bilingual (German/English) electricity-market intelligence dashboard by **Hope Intelligence**. It turns public data from **Bundesnetzagentur | SMARD.de** into interactive market analysis, explainable price signals, a transparent machine-learning research forecast, and an educational flexibility scenario.

**Audience:** energy suppliers, utilities (Stadtwerke), energy traders, renewable energy developers, industrial energy managers, data engineers and Python/ML professionals.

> **Deployment status:** Source code and automated tests are available in this repository. Real production-data ingestion and the public dashboard must be verified after first successful GitHub Actions execution. The checked-in `docs/data/dashboard.json` is an intentionally **empty** status file — never fabricated market observations.

## What does it do?

| Capability | Deliverable | Business relevance |
| --- | --- | --- |
| **Data engineering** | SMARD ingestion, validation, retry logic, deduplication, SQLite staging in CI | Reproducible electricity-market data pipeline |
| **Market analytics** | Wholesale price, photovoltaic, onshore wind, grid load and 7-day market signals | Historical energy-market monitoring |
| **Forecast research** | 24 hourly extrapolations; ML vs 24h/7d naive baselines; separate selection and test blocks | Transparent comparison of forecasting methods |
| **Public interactive website** | German/English responsive dashboard deployed on GitHub Pages | Shareable, install-free proof of engineering work |

### Energy-industry additions

- **Negative-price analysis:** historical count of hours with prices below EUR 0/MWh over the most recent 168 hours.
- **Volatility and P10–P90 spread:** simple historical risk/exposure indicators.
- **Flexible-load illustration:** user-selected MWh volume multiplied by the historical P90–P10 wholesale spread. **This is *not* an achievable cost-savings estimate**, tariff quote, operational dispatch instruction, or financial recommendation.
- **Data provenance and freshness:** SMARD attribution, measured timestamps and stale data warnings.
- **Bilingual content and discoverability:** descriptive page titles, structured schema, Open Graph tags, automatically generated canonical URL, robots.txt and sitemap.xml after deployment.

## Technology

Python 3.11 · NumPy · scikit-learn · SQLite (temporary CI staging) · JavaScript · CSS · SVG · GitHub Actions · GitHub Pages · Unit testing · SMARD open energy data.

There is **no continuously running backend**, no persistent production database and no paid hosting requirement for the static demo. Python executes during scheduled GitHub Actions refreshes; the browser reads a generated JSON artifact.

## Quick deployment — no local IDE or terminal

**Follow [`START_HERE_FA.md`](START_HERE_FA.md) for the step-by-step Persian guide.**

1. Create a public GitHub repository named `energy-intelligence` using the `main` branch.
2. Unzip the release and upload **all of its contents**, including the hidden `.github` directory. Do not upload the ZIP as one file.
3. Set **Settings → Pages → Source: GitHub Actions**.
4. Run **Actions → Energy Intelligence - Refresh & Publish → Run workflow**. It will fetch actual SMARD data, run tests and publish the website. A failure prevents publishing an invented/fake dataset.
5. After the workflow succeeds, use the real Pages URL provided in Settings → Pages. Visit the site and confirm its freshness timestamp and data source before sharing.
6. Add the public link to the repository **About → Website** and publish your company-page announcement with **both live-demo and GitHub source links**.
7. In **About → Topics**, paste the relevant topic keywords from [`GITHUB_LINKEDIN_KEYWORDS.md`](GITHUB_LINKEDIN_KEYWORDS.md).

The workflow may be delayed by GitHub scheduling, and remote SMARD availability cannot be guaranteed.

## Architecture

```text
German electricity market / SMARD API (real time series, hourly aggregation)
                          │
                    GitHub Actions
                          │
                   Python ingestion
               retry · validation · QC
                          │
                 SQLite (in-memory)
                          │
           historical market indicators
             train → select → test
          scikit-learn + simple baselines
                          │
               docs/data/dashboard.json
                          │
                GitHub Pages static
                   DE / EN dashboard
```

## How the forecast is evaluated

1. Only authentic, observed wholesale prices are processed in production. Training inputs include local calendar effects and the prices 24, 48 and 168 hours earlier.
2. The usable series is ordered chronologically and divided into **training**, **model-selection validation**, and a **later untouched test block**.
3. The method with the best *validation* MAE is selected from a histogram-based gradient boosting regressor, a 24-hour naive forecast, and a 168-hour naive forecast.
4. All candidates are evaluated on the separate **test** block. The site displays test MAE for the selected method and comparison baseline.
5. For the forward estimate, selected ML models are refit on available historical observations. The next 24 **hourly** values after the last historical timestamp are predicted — **not necessarily the next calendar day**.

**Limits:** This is one historical split, not prospective validation; production accuracy, uncertainty bounds and performance under changing market conditions have not been established. The dashboard does not produce calibrated prediction intervals. It does not claim to trade in 15-minute markets. A simple baseline can be selected instead of machine learning when its validation MAE is lower.

## Market data and limitations

- **Source:** [Bundesnetzagentur | SMARD.de](https://www.smard.de/)
- **Data reuse:** [CC BY 4.0 and attribution](https://www.smard.de/home/datennutzung) — data license is separate from the MIT license covering code.
- **Market:** DE/LU day-ahead wholesale electricity prices (with fallback to a SMARD `DE` series only if available and clearly disclosed); solar/onshore wind/grid load are `DE` series.
- **Time series used:** `hour` from SMARD; **EU day-ahead trading moved to 15-minute intervals on 30 September 2025**. Hourly market charts here are **not** a 15-minute trading product.
- **Units:** EUR/MWh for prices, MWh per hourly interval for energy series.
- **Not included:** household retail tariffs, taxes, grid fees, transmission constraints, imbalance charges, weather forecast inputs, full historical provenance/version snapshots, guaranteed cost reductions, industrial production schedules.
- **Freshness:** the browser compares the latest actual SMARD observation timestamp with the *current* time; old data is flagged even when CI stops running.
- **License:** [MIT (software)](LICENSE); **CC BY 4.0 (SMARD datasets)**.

## Local verification (optional)

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.build  # requires access to SMARD; never uses synthetic production data
```

## Source tree

```text
.github/workflows/publish.yml    GitHub Pages deployment + refresh
.github/dependabot.yml          Dependency-update proposals
docs/index.html / app.js        Bilingual interactive dashboard
src/smard.py                    SMARD ingestion and provenance
src/build.py                    Analytics, data quality, generated JSON
src/forecast.py                 Validation-selected forecasting methods
src/site_meta.py                Canonical URL, robots, sitemap
/tests/                         Deterministic unit tests
GITHUB_LINKEDIN_KEYWORDS.md     Search terms + ready-to-paste GitHub settings
LINKEDIN_LAUNCH_COPY.md         Honest English/German company launch posts
AUDIT_REPORT_FA.md              Code audit, remaining gaps and B2B roadmap
```

## Business roadmap

**Next high-value features:** 15-minute day-ahead price analysis; configurable industrial load profile and real plant constraints; scheduled API-based alerts; peak-shaving and demand-response scenario exploration; weather-enhanced forward forecasting and rolling backtests. These are **ideas for future work**, not features falsely claimed as implemented.

### Get involved

Engineers, utilities and corporate energy teams are welcome to propose requirements and open GitHub issues. For a production or company-specific deployment, additional requirements gathering and validation are needed.

**Owned and maintained as an open-source project by Hope Intelligence.** Not affiliated with or endorsed by Bundesnetzagentur.
