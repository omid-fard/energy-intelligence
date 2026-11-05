
"""Fetch authentic public SMARD time series; never fabricate observations."""
from __future__ import annotations

import json
import math
import sqlite3
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = 'https://www.smard.de/app/chart_data'

FILTERS = {
    'price': 4169,  # Day-ahead wholesale market price
    'solar': 4068,  # Photovoltaic generation
    'wind': 4067,   # Onshore wind generation
    'load': 410,    # Grid load
}

REGION = 'DE'

# Required order for the existing GitHub unit tests.
# Try DE-LU first; use DE if the primary region is unavailable.
PRICE_REGIONS = ('DE-LU', 'DE')

RESOLUTION = 'hour'
MAX_RESPONSE_BYTES = 8 * 1024 * 1024


def get_json(url: str, attempts: int = 3) -> dict:
    """Download JSON with retries for temporary failures."""
    if attempts < 1:
        raise ValueError('attempts must be at least 1')

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/125.0.0.0 Safari/537.36'
        ),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'identity',
        'Referer': 'https://www.smard.de/',
    }

    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers=headers)

            with urlopen(request, timeout=30) as response:
                content_type = response.headers.get(
                    'Content-Type', 'unknown'
                )
                body = response.read(MAX_RESPONSE_BYTES + 1)

            if len(body) > MAX_RESPONSE_BYTES:
                raise ValueError(
                    'Response exceeds the 8 MiB safety limit'
                )

            if not body.strip():
                raise ValueError(
                    f'Empty response (Content-Type: {content_type})'
                )

            try:
                payload = json.loads(body.decode('utf-8-sig'))
            except (ValueError, UnicodeDecodeError) as exc:
                preview = body[:160].decode(
                    'utf-8', errors='replace'
                ).strip()

                raise ValueError(
                    f'Non-JSON response '
                    f'(Content-Type: {content_type}; '
                    f'body preview: {preview!r})'
                ) from exc

            if not isinstance(payload, dict):
                raise ValueError(
                    'SMARD response is JSON, but is not an object'
                )

            return payload

        except HTTPError as exc:
            if exc.code in (400, 401, 403, 404, 410):
                raise RuntimeError(
                    f'SMARD rejected {url} with HTTP {exc.code}'
                ) from exc

            last_error = f'HTTP {exc.code}'

        except (
            URLError,
            TimeoutError,
            OSError,
            ValueError
        ) as exc:
            last_error = str(exc)

        if attempt < attempts:
            print(
                f'WARN SMARD request attempt '
                f'{attempt}/{attempts} failed: '
                f'{url} | {last_error}',
                flush=True,
            )

            time.sleep(min(2 ** attempt, 8))

    raise RuntimeError(
        f'SMARD download failed after {attempts} attempts: '
        f'{url} | {last_error}'
    )


def parse_series(
    payload: dict
) -> list[tuple[int, float]]:
    """Keep valid observations, including negative prices."""
    pairs = payload.get('series')

    if not isinstance(pairs, list):
        raise ValueError(
            'SMARD response has no series array'
        )

    records: dict[int, float] = {}

    for entry in pairs:
        if not isinstance(entry, (list, tuple)):
            continue

        if len(entry) < 2:
            continue

        stamp, value = entry[:2]

        if isinstance(stamp, bool):
            continue

        if not isinstance(stamp, (int, float)):
            continue

        if isinstance(value, bool):
            continue

        if not isinstance(value, (int, float)):
            continue

        if not math.isfinite(float(stamp)):
            continue

        if not math.isfinite(float(value)):
            continue

        if int(stamp) <= 0:
            continue

        records[int(stamp)] = float(value)

    return sorted(records.items())


def fetch_metric(
    filter_id: int,
    weeks: int = 18,
    region: str = REGION
) -> list[tuple[int, float]]:
    """Download recent SMARD weekly data windows."""

    if not 1 <= weeks <= 52:
        raise ValueError(
            'weeks must be between 1 and 52'
        )

    index_url = (
        f'{BASE}/{filter_id}/{region}/'
        f'index_{RESOLUTION}.json'
    )

    index = get_json(index_url)
    stamps = index.get('timestamps')

    if not isinstance(stamps, list) or not stamps:
        raise ValueError(
            f'SMARD index empty for '
            f'filter={filter_id}, region={region}'
        )

    valid_stamps = sorted({
        int(stamp)
        for stamp in stamps
        if isinstance(stamp, (int, float))
        and not isinstance(stamp, bool)
        and math.isfinite(float(stamp))
        and stamp > 0
    })

    if not valid_stamps:
        raise ValueError(
            f'No valid SMARD timestamps '
            f'for {filter_id}/{region}'
        )

    selection = valid_stamps[-weeks:]

    records: dict[int, float] = {}
    successful_windows = 0

    for stamp in selection:
        url = (
            f'{BASE}/{filter_id}/{region}/'
            f'{filter_id}_{region}_'
            f'{RESOLUTION}_{stamp}.json'
        )

        try:
            series = parse_series(get_json(url))

            if series:
                records.update(series)
                successful_windows += 1
            else:
                print(
                    f'WARN SMARD empty window: {url}',
                    flush=True,
                )

        except (RuntimeError, ValueError) as exc:
            print(
                f'WARN skipping SMARD window: '
                f'{url} | {exc}',
                flush=True,
            )

    minimum = min(4, len(selection))

    if successful_windows < minimum:
        raise RuntimeError(
            f'Only {successful_windows}/'
            f'{len(selection)} valid SMARD windows '
            f'for {filter_id}/{region}; '
            f'require {minimum}'
        )

    if not records:
        raise RuntimeError(
            f'No observations for {filter_id}/{region}'
        )

    print(
        f'SMARD {filter_id}/{region}: '
        f'{len(records)} observations '
        f'from {successful_windows}/'
        f'{len(selection)} windows',
        flush=True,
    )

    return sorted(records.items())


def fetch_market_metric(
    metric: str,
    weeks: int = 18
) -> tuple[list[tuple[int, float]], str]:
    """Try DE-LU first for prices; fall back to DE."""

    if metric not in FILTERS:
        raise ValueError(
            f'Unsupported metric: {metric}'
        )

    regions = (
        PRICE_REGIONS
        if metric == 'price'
        else (REGION,)
    )

    errors = []

    for region in regions:
        try:
            observations = fetch_metric(
                FILTERS[metric],
                weeks,
                region
            )

            return observations, region

        except (RuntimeError, ValueError) as exc:
            errors.append(f'{region}: {exc}')

            print(
                f'WARN {metric}/{region} unavailable: '
                f'{exc}',
                flush=True,
            )

    raise RuntimeError(
        f'Failed to load authentic SMARD '
        f'{metric} observations. '
        + '; '.join(errors)
    )


def open_db() -> sqlite3.Connection:
    """Create an in-memory observations database."""

    db = sqlite3.connect(':memory:')

    db.execute(
        'CREATE TABLE observations ('
        'metric TEXT NOT NULL, '
        'timestamp_ms INTEGER NOT NULL, '
        'value REAL NOT NULL, '
        'PRIMARY KEY(metric, timestamp_ms))'
    )

    return db


def save_observations(
    db: sqlite3.Connection,
    metric: str,
    points: list[tuple[int, float]]
) -> None:
    """Save authentic observations and update duplicates."""

    db.executemany(
        'INSERT INTO observations '
        '(metric, timestamp_ms, value) '
        'VALUES (?, ?, ?) '
        'ON CONFLICT(metric, timestamp_ms) '
        'DO UPDATE SET value=excluded.value',
        (
            (metric, stamp, value)
            for stamp, value in points
        ),
    )

    db.commit()


def load_observations(
    db: sqlite3.Connection,
    metric: str
) -> list[tuple[int, float]]:
    """Return observations ordered by timestamp."""

    return [
        (int(stamp), float(value))
        for stamp, value in db.execute(
            'SELECT timestamp_ms, value '
            'FROM observations '
            'WHERE metric=? '
            'ORDER BY timestamp_ms',
            (metric,),
        )
    ]
