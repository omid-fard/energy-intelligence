# Energy Intelligence — Fix and Deployment Guide

This release was prepared from the uploaded project ZIP. No real electricity prices were invented or bundled. Synthetic fixtures are used **only in tests**. Production observations must originate from an authorized real data source.

## Files to update in the GitHub repository

| Repository path | Action | Purpose |
| --- | --- | --- |
| `.github/workflows/publish.yml` | Replace | Restore and save a cache of previously verified data; publish a clearly labeled status page during a source outage |
| `src/smard.py` | Replace | Bounded network retries, clearer error diagnostics, and early exit after repeated window failures |
| `src/build.py` | Replace | Generate `source_unavailable` or `cached_stale` output without inventing observations; validate cached data |
| `docs/app.js` | Replace | Show accurate freshness and outage messages; do not present old forecasts as future predictions |
| `docs/index.html` | Replace | Update the data attribution and rights message |
| `tests/test_pipeline_recovery.py` | Add | Six new test scenarios for recovery, caching and valid observations |
| `README.md` | Replace | Document the failure modes, limitations and deployment requirements |
| `START_HERE.md` | Add | English-only setup and verification steps (replaces `START_HERE_FA.md`) |
| `AUDIT_REPORT.md` | Add | English-only technical and product audit (replaces `AUDIT_REPORT_FA.md`) |
| `FIX_GUIDE.md` | Add | This English-only guide (replaces `FIX_GUIDE_FA.md`) |

**Remove** the old `START_HERE_FA.md` and `AUDIT_REPORT_FA.md` files (and `FIX_GUIDE_FA.md` if previously uploaded). They are replaced by the English names above.

`src/forecast.py`, `src/site_meta.py`, `docs/style.css` and the image assets were not changed as part of the outage fix.

## Update methods

**Using Git locally:** Extract `energy-intelligence-english.zip`. Copy the contents of `energy-intelligence-main` to the root of the existing local repository, taking care to delete the obsolete `_FA.md` files. Check the changes, then commit and push.

**Using the GitHub browser:** Open each path in the table, select **Edit**, replace the file contents with the corresponding version from the archive and commit. Use **Add file → Create new file** for new documents and tests. Remove the obsolete `_FA.md` files using the repository's file-delete action.

Prefer committing all interdependent program changes together. If committing one file at a time, intermediary scheduled workflows may fail until all related changes land.

Suggested commit message:

`Fix SMARD outage handling and standardize English documentation`

## Interpret GitHub Actions results

1. **Run Python unit tests:** Existing tests plus outage-recovery tests must pass.
2. **Fetch SMARD data and calculate forecasts:** Check the log for one of these outcomes:
   - `Published N real price points`: authentic data were retrieved and processed; the valid cache was refreshed.
   - `Published status: cached_stale`: the source was unavailable, verified historical data were reused with a visible warning and the forecast was disabled.
   - `Published status: source_unavailable`: the source was unavailable and no valid previous data existed; the site reports missing data instead of displaying a fabricated chart.
3. **Deploy website:** Verify that the site is reachable. A **green workflow does not establish that prices are fresh**. Check the metadata timestamp and status independently.
4. If **Run Python unit tests** fails, diagnose that test failure from the log; it is separate from SMARD connectivity.

## Verification limitations

Python tests and JavaScript syntax checks were executed locally. External SMARD calls from GitHub Actions and actual GitHub Pages publication were not tested here. A production workflow run is necessary for those checks.

## Data rights

Review the official conditions at https://www.smard.de/home/datennutzung before publishing wholesale electricity-price data. In particular, check the current terms related to HEDWIG; this project does not claim permission to republish such data. The MIT license applies to the source code, not automatically to the underlying market dataset.
