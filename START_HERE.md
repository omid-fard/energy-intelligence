# Publish Energy Intelligence on GitHub — Browser-Only Guide

You do not need to install Python, Docker, or an IDE on your computer. GitHub Actions runs the Python pipeline on GitHub-hosted runners, and GitHub Pages serves the website.

## 1. Create a public repository (for a new project only)

1. Download and extract the project ZIP.
2. Open https://github.com/new.
3. Choose the repository name `energy-intelligence`, select **Public**, and use this description:
   `German electricity market intelligence: real SMARD data, negative prices, renewable energy analytics, transparent ML forecasting, Python and GitHub Pages.`
4. Do not create an additional README: the project already includes one. Select **Create repository**.

**If you already have an `energy-intelligence` repository, do not create another one.** Instead, follow the update instructions in [`FIX_GUIDE.md`](FIX_GUIDE.md).

## 2. Upload project contents, not the ZIP archive

1. In the repository, select **Add file → Upload files** (or the initial *uploading an existing file* link).
2. Open the extracted directory; ensure its hidden `.github` folder is included (on macOS, toggle hidden files with `Command + Shift + .`; on Windows, use **View → Show → Hidden items**).
3. Upload the **contents** of `energy-intelligence-main`, without adding an extra nested directory in the repository root.
4. Commit the files and confirm `.github/workflows/publish.yml` exists in the correct location.

For updates to an existing repository, the safer approach is to commit the modified files only; see `FIX_GUIDE.md`.

## 3. Enable and verify the website

1. Open **Settings → Pages**, then **Build and deployment**.
2. Set **Source** to **GitHub Actions**.
3. Open **Actions → Energy Intelligence - Refresh & Publish → Run workflow**.
4. Open the workflow run. A green result means the workflow completed, **not** necessarily that fresh source data was available. In **Fetch SMARD data and calculate forecasts**, check for `Published ... real price points`. Status `source_unavailable` means no current or validated cached observations were available; `cached_stale` means the site uses previously fetched authentic data with a warning.
5. Find the site URL in **Settings → Pages**, e.g. `https://YOUR-USERNAME.github.io/energy-intelligence/`.
6. Open the website and verify timestamps, attribution, price charts, and whether the data are actually fresh.

## 4. Configure GitHub discovery

1. In the repository, open **About → Edit**.
2. Set the description and, once deployment succeeds, the live URL in **Website**.
3. Add relevant topics without `#`, using [`GITHUB_LINKEDIN_KEYWORDS.md`](GITHUB_LINKEDIN_KEYWORDS.md).
4. Optionally pin the repository to your public GitHub profile using **Customize your pins**.

## 5. Announce the project on LinkedIn only after verification

1. Open the Hope Intelligence company page using an admin account.
2. Update its **About** description with the English or German text in `GITHUB_LINKEDIN_KEYWORDS.md`.
3. Add the verified website URL.
4. Use `LINKEDIN_LAUNCH_COPY.md` to prepare a post. Replace placeholder URLs with real links and include a screenshot of authentic results, not a fabricated chart.
5. Track relevant website visits, clicks, search visibility, and engagement from the energy sector.

## Important limitations

- `docs/data/dashboard.json` in the repository is intentionally an empty placeholder. Uploading files alone does not establish that authentic market observations were ingested.
- When SMARD is unavailable, the workflow publishes either `cached_stale` data from previously verified observations (with forecasting disabled) or a `source_unavailable` status page. It must never create fictitious production observations.
- **Data reuse:** Before publicly republishing wholesale prices, review the latest official SMARD data-use terms at https://www.smard.de/home/datennutzung and verify that redistribution is permitted. The software's MIT license does not grant a license to the underlying market data.
- Forecasts are experimental and do not guarantee commercial energy savings.
- This is a static website without a continuously running Python backend or a PostgreSQL/FastAPI service.
- Replace any placeholder GitHub username, repository URL, or public website URL before advertising the project.
