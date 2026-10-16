"""Fetch public SMARD time series. Never fabricate production observations."""
from __future__ import annotations

import json
import math
import sqlite3
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = 'https://www.smard.de/app/chart_data'
FILTERS = {
    'price': 4169,  # Day-ahead wholesale price; Germany/Luxembourg bidding area
    'solar': 4068,  # photovoltaic generation
    'wind': 4067,   # onshore wind generation
    'load': 410,    # grid load
}
REGION = 'DE'
PRICE_REGIONS = ('DE-LU', 'DE')  # source-specific region variants; try official bidding zone first
RESOLUTION = 'hour'


def get_json(url: str, attempts: int = 3) -> dict:
    """Retry transient failures, fail fast on 404 (e.g. unsupported filter/region)."""
    for attempt in range(attempts):
        try:
            request = Request(url, headers={
                'User-Agent': 'EnergyIntelligence/2.0 (open-source-energy-dashboard)',
                'Accept': 'application/json',
            })
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if not isinstance(payload, dict):
                raise ValueError('SMARD returned a non-object JSON response')
            return payload
        except HTTPError as exc:
            if exc.code in (400, 404):
                raise RuntimeError(f'SMARD endpoint rejected request ({exc.code}): {url}') from exc
            if attempt == attempts - 1:
                raise RuntimeError(f'Unable to retrieve {url}: HTTP {exc.code}') from exc
        except (URLError, TimeoutError, ValueError) as exc:
            if attempt == attempts - 1:
                raise RuntimeError(f'Unable to retrieve {url}: {exc}') from exc
        time.sleep(1.5 * (attempt + 1))
    raise AssertionError('unreachable')


def parse_series(payload: dict) -> list[tuple[int, float]]:
    """Discard missing/non-finite data, keep legitimate negative wholesale prices."""
    pairs = payload.get('series')
    if not isinstance(pairs, list):
        raise ValueError('SMARD response has no series array')
    records = {}
    for entry in pairs:
        if not isinstance(entry, list) or len(entry) < 2:
            continue
        stamp, value = entry[:2]
        if isinstance(stamp, bool) or not isinstance(stamp, (int, float)):
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(stamp)) or not math.isfinite(float(value)):
            continue
        if int(stamp) <= 0:
            continue
        records[int(stamp)] = float(value)
    return sorted(records.items())


def fetch_metric(filter_id: int, weeks: int = 18, region: str = REGION) -> list[tuple[int, float]]:
    """Read at most the newest N indexed windows with known region/granularity."""
    if not 1 <= weeks <= 52:
        raise ValueError('weeks must be between 1 and 52')
    index = get_json(f'{BASE}/{filter_id}/{region}/index_{RESOLUTION}.json')
    stamps = index.get('timestamps', [])
    if not isinstance(stamps, list) or not stamps:
        raise ValueError(f'SMARD index empty for filter={filter_id}, region={region}')
    stamps = sorted({int(s) for s in stamps if isinstance(s, (int, float))
                     and not isinstance(s, bool) and math.isfinite(float(s)) and s > 0})
    if not stamps:
        raise ValueError('No valid weekly timestamps')
    records = {}
    successful_windows = 0
    selection = stamps[-weeks:]
    for stamp in selection:
        url = f'{BASE}/{filter_id}/{region}/{filter_id}_{region}_{RESOLUTION}_{stamp}.json'
        try:
            data = parse_series(get_json(url))
            if data:
                records.update(data)
                successful_windows += 1
        except (ValueError, RuntimeError) as exc:
            print(f'WARN skipped {filter_id}/{region}/{stamp}: {exc}', flush=True)
    if successful_windows < min(4, len(selection)):
        raise RuntimeError(f'Only {successful_windows} of {len(selection)} valid SMARD windows for {filter_id}/{region}')
    return sorted(records.items())


def fetch_market_metric(metric: str, weeks: int = 18) -> tuple[list[tuple[int, float]], str]:
    """Price uses the DE-LU bidding-area series when available; disclose fallback."""
    if metric not in FILTERS:
        raise ValueError(f'Unsupported metric: {metric}')
    regions = PRICE_REGIONS if metric == 'price' else (REGION,)
    errors = []
    for region in regions:
        try:
            return fetch_metric(FILTERS[metric], weeks=weeks, region=region), region
        except (RuntimeError, ValueError) as exc:
            errors.append(f'{region}: {exc}')
            print(f'WARN {metric} region {region} unavailable: {exc}', flush=True)
    raise RuntimeError(f'Failed to load {metric}; ' + '; '.join(errors))


def open_db() -> sqlite3.Connection:
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE observations (metric TEXT NOT NULL, timestamp_ms INTEGER NOT NULL, '
               'value REAL NOT NULL, PRIMARY KEY(metric, timestamp_ms))')
    return db


def save_observations(db: sqlite3.Connection, metric: str, points: list[tuple[int, float]]) -> None:
    db.executemany('INSERT INTO observations (metric, timestamp_ms, value) VALUES (?, ?, ?) '
                   'ON CONFLICT(metric, timestamp_ms) DO UPDATE SET value=excluded.value',
                   ((metric, stamp, value) for stamp, value in points))
    db.commit()


def load_observations(db: sqlite3.Connection, metric: str) -> list[tuple[int, float]]:
    return [(int(t), float(v)) for t, v in db.execute(
        'SELECT timestamp_ms, value FROM observations WHERE metric=? ORDER BY timestamp_ms', (metric,))]
