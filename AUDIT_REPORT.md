# Energy Intelligence — Technical and Product Audit

## Scope

The review covers the submitted project package: SMARD data ingestion, validation and time-series processing, forecasting and tests, browser-side behavior, basic web security, GitHub Actions/Pages deployment, documentation, search discoverability, and launch messaging.

## Issues identified and addressed

1. **Wholesale-price region:** The price series is associated with the DE/LU bidding area. The code tries `DE-LU` first for compatibility with the existing tests and then `DE` if the first route fails. The region actually used is retained in metadata to avoid misleading attribution.
2. **Optimistic forecast evaluation:** The initial approach selected the best method on the same period used to report its error. The forecast logic now separates training, model selection, and final evaluation into chronological blocks.
3. **Freshness calculation:** Instead of relying on the static file generation time, the browser calculates data age relative to each visit.
4. **Industrial relevance:** Negative-price frequency, volatility and P10–P90 spread indicators were added. The interactive load-volume example is a theoretical wholesale-price-spread illustration, not an operational savings calculation.
5. **Discoverability:** Metadata includes descriptive text, relevant keywords, Open Graph tags, structured data, page titles, and deployment-generated `robots.txt`, sitemap and canonical URLs.
6. **Test coverage:** Unit tests cover region fallback, series validation, negative values, feature and forecast evaluation boundaries, SEO behavior and pipeline outage recovery.

## Test status and scope of verification

- The originally reviewed ZIP passed **18** local Python tests. The subsequent outage-recovery update passed **24** local Python tests, including 6 new recovery tests.
- JavaScript syntax was checked locally with Node.js.
- Real-time access to SMARD from the GitHub Actions runner and actual GitHub Pages publishing **have not been verified** in this environment. A successful production workflow run is still required.
- A green workflow indicates completion, but does not guarantee the dataset was refreshed. Inspect the published metadata status and timestamps.

## Remaining limitations and risks

- European day-ahead electricity-market trading moved to 15-minute intervals in late September 2025; this version works with SMARD's hourly output and is not a trading system.
- Displayed prices are **wholesale** prices, not end-user household or industrial tariffs.
- Generation/load and wholesale-price series can use different region identifiers; inspect metadata rather than assuming identical coverage.
- Model comparisons use a time-ordered split, not a fully prospective study. Generalization, interval calibration, and abnormal-market resilience remain unproven.
- No future meteorological forecasts, projected grid load, or power plant operational inputs are used.
- The flexible-load widget does not represent achievable savings. It excludes taxes, grid fees, operational constraints, timing, and implementation costs.
- SQLite is used for temporary execution in GitHub Actions. There is no permanent server database, user-authentication service, or always-on backend.
- GitHub Pages is static hosting, and scheduled workflows can be delayed.
- GitHub Actions reference action major-version tags instead of immutable commit SHAs. For security-sensitive deployments, pin verified SHAs and manage upgrades deliberately.
- SEO metadata and hashtags do not guarantee web rankings, customer acquisition, or business opportunities.

## Suggested B2B roadmap

| Priority | Feature | Business use | Prerequisites |
| --- | --- | --- | --- |
| 1 | **15-minute price signals** and low/negative-price windows | Municipal utilities, suppliers, renewable operators | Authorized finer-grained data and German daylight-saving-time testing |
| 2 | **Upload actual industrial load profiles** with operating constraints | Industrial energy managers | Upload validation, time alignment, privacy policy, operational feasibility tests |
| 3 | **Volatility and negative-price alerts** | Supplier and trading-desk monitoring; not trading instructions | Notifications, alert logic, continuously running backend, monitoring |
| 4 | **Forecasting with rolling backtests and uncertainty** | Analytics and planning teams | Weather data, rolling-origin testing, calibrated prediction intervals |
| 5 | **Automated reporting and customer API** | B2B software / management teams | Authentication, tenant isolation, SLAs and production hosting |

## Visibility and launch plan

1. Add repository topics manually under **About**; see `GITHUB_LINKEDIN_KEYWORDS.md`.
2. Once the workflow and website are verified, add the real site URL to GitHub **About → Website** and the company's LinkedIn page.
3. Explain a real energy-market question rather than claiming vague AI capabilities. Share an authentic chart, observation timestamp, model evaluation metric and source-code link.
4. Use 3–5 relevant hashtags per post. Adapt German messaging to industrial energy and utility audiences and English messaging to international technical audiences.
5. Evaluate qualified visits, employer/industry referrals, website clicks and substantive conversations, not commit counts alone.

## Publication criteria

Use the term **live platform** only after the workflow succeeds, genuine observations and their age are displayed accurately, the public website opens and its limitations are clearly documented. Until then, describe the project as an **open-source project in development**.

**Data-use warning:** The official SMARD terms should be checked for current restrictions, especially regarding wholesale-price data associated with HEDWIG. An MIT code license is not a license for the data.
