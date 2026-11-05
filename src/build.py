"""Download genuine SMARD data and publish a transparent, failure-safe dashboard.

The production pipeline never fabricates observations. When SMARD is unreachable,
publish a clearly marked stale authentic cache or an explicitly empty status page.
"""
from __future__ import annotations

import copy
import json
import math
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

from src.forecast import HOUR_MS, make_forecast
from src.smard import FILTERS, fetch_market_metric, load_observations, open_db, save_observations

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs' / 'data' / 'dashboard.json'
CACHE = ROOT / '.cache' / 'dashboard.json'


def iso(stamp: int) -> str:
    return datetime.fromtimestamp(stamp / 1000, tz=timezone.utc).isoformat().replace('+00:00', 'Z')


def serialize(points: list[tuple[int, float]]) -> list[dict]:
    return [{'ts': iso(stamp), 'value': round(value, 3)} for stamp, value in points]


def percentile(sorted_values: list[float], percentile_number: int) -> float:
    """Linear interpolation between adjacent observations."""
    if not sorted_values:
        raise ValueError('Empty prices')
    position = (len(sorted_values) - 1) * percentile_number / 100
    low, high = math.floor(position), math.ceil(position)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (position - low)


def analytics(prices: list[tuple[int, float]]) -> dict:
    latest = prices[-1][0]
    values = [value for stamp, value in prices if latest - 168 * HOUR_MS < stamp <= latest]
    ordered = sorted(values)
    p10, p90 = percentile(ordered, 10), percentile(ordered, 90)
    return {
        'window': 'up to 168 recent hourly observations',
        'points': len(values),
        'negative_price_hours': sum(v < 0 for v in values),
        'price_volatility_std_eur_mwh': round(statistics.pstdev(values), 2) if len(values) > 1 else 0,
        'p10_eur_mwh': round(p10, 2),
        'p90_eur_mwh': round(p90, 2),
        'p10_p90_spread_eur_mwh': round(p90 - p10, 2),
    }


def build(metrics: dict[str, list[tuple[int, float]]], source_regions: dict | None = None) -> dict:
    db = open_db()
    try:
        for name, observations in metrics.items():
            if name not in FILTERS:
                raise ValueError(f'Unexpected metric: {name}')
            save_observations(db, name, observations)
        prices = load_observations(db, 'price')
        if len(prices) < 500:
            raise RuntimeError(f'Insufficient real hourly price observations: {len(prices)}')
        latest = prices[-1][0]
        day = [v for stamp, v in prices if latest - 24 * HOUR_MS < stamp <= latest]
        if not day:
            raise RuntimeError('No prices within the last 24 hours of the observation window')
        now = datetime.now(timezone.utc)
        gap = (now.timestamp() * 1000 - latest) / HOUR_MS
        if gap < -36:
            raise RuntimeError('Latest SMARD timestamp is implausibly far in the future')
        history = {key: serialize(load_observations(db, key)[-24 * 45:]) for key in FILTERS}
        forecast = make_forecast(prices)
        if forecast['status'] != 'ok':
            print('NOTICE forecast unavailable:', forecast['message'], flush=True)
        return {
            'metadata': {
                'project': 'Energy Intelligence', 'status': 'live',
                'source': 'Bundesnetzagentur | SMARD.de', 'source_url': 'https://www.smard.de/',
                # SMARD currently advises against reuse of wholesale-price data;
                # do not misrepresent a blanket permission as covering prices.
                'market_price_reuse_notice': 'Review SMARD/HEDWIG wholesale price reuse guidance before public reuse',
                'market': 'German/Luxembourg day-ahead wholesale market',
                'generated_at': now.isoformat().replace('+00:00', 'Z'),
                'latest_price_timestamp': iso(latest), 'lag_hours_at_build': round(gap, 1),
                'resolution': 'hour', 'underlying_market_resolution': '15 min since 2025-09-30',
                'price_unit': 'EUR/MWh', 'energy_unit': 'MWh/hourly interval',
                'historical_observations': len(prices),
                'source_regions': source_regions or {'price': 'DE-LU', 'solar': 'DE', 'wind': 'DE', 'load': 'DE'},
                'available_metrics': [key for key in FILTERS if history[key]],
                'data_quality': {
                    'recent_24h_observations': len(day),
                    'forecast_requires_complete_lags': True,
                    'real_market_data_only': True,
                },
            },
            'summary': {
                'current_price': round(prices[-1][1], 2),
                'avg_price_24h': round(sum(day) / len(day), 2),
                'min_price_24h': round(min(day), 2),
                'max_price_24h': round(max(day), 2),
            },
            'history': history, 'analytics': analytics(prices), 'forecast': forecast,
        }
    finally:
        db.close()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replace prevents corrupt JSON after a failed write.
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(',', ':')),
        encoding='utf-8',
    )
    temporary.replace(path)


def is_authentic_cache(payload: object) -> bool:
    """Only reuse a prior valid *real* publication, never an empty placeholder."""
    if not isinstance(payload, dict):
        return False
    meta = payload.get('metadata')
    history = payload.get('history')
    if not isinstance(meta, dict) or not isinstance(history, dict):
        return False
    if meta.get('status') != 'live' or meta.get('source') != 'Bundesnetzagentur | SMARD.de':
        return False
    if not isinstance(meta.get('data_quality'), dict) or meta['data_quality'].get('real_market_data_only') is not True:
        return False
    if not isinstance(meta.get('historical_observations'), int) or meta['historical_observations'] < 500:
        return False
    prices = history.get('price')
    if not isinstance(prices, list) or len(prices) < 24:
        return False
    try:
        observed = [(datetime.fromisoformat(row['ts'].replace('Z', '+00:00')), row['value'])
                    for row in prices]
        return (
            all(t.tzinfo is not None and isinstance(v, (float, int)) and not isinstance(v, bool)
                and math.isfinite(float(v)) for t, v in observed)
            and all(observed[i][0] < observed[i+1][0] for i in range(len(observed)-1))
            and observed[-1][0].isoformat() == datetime.fromisoformat(
                meta['latest_price_timestamp'].replace('Z', '+00:00')
            ).isoformat()
        )
    except (TypeError, ValueError, KeyError, AttributeError, OverflowError):
        return False


def unavailable(reason: str, cache_path: Path | None = None) -> dict:
    """Preserve verified old observations, or explicitly publish no data."""
    cache_path = CACHE if cache_path is None else cache_path
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding='utf-8'))
            if is_authentic_cache(cached):
                result = copy.deepcopy(cached)
                result['metadata']['status'] = 'cached_stale'
                result['metadata']['refresh_error'] = reason[:350]
                result['metadata']['cache_used'] = True
                result['metadata'].pop('license', None)
                result['metadata']['market_price_reuse_notice'] = (
                    'Review SMARD/HEDWIG wholesale price reuse guidance before public reuse'
                )
                # Old forward projections must not be shown as future predictions.
                result['forecast'] = {
                    'status': 'unavailable', 'message': 'Source unavailable; historical data only',
                    'points': [], 'validation': None,
                }
                return result
            print('WARN found cache but authenticity validation failed', flush=True)
        except (OSError, ValueError, TypeError) as exc:
            print(f'WARN invalid saved dashboard cache: {exc}', flush=True)
    return {
        'metadata': {
            'project': 'Energy Intelligence', 'status': 'source_unavailable',
            'source': 'Bundesnetzagentur | SMARD.de',
            'generated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'refresh_error': reason[:350], 'real_market_data_only': True,
        },
        'summary': {}, 'analytics': {},
        'history': {name: [] for name in FILTERS},
        'forecast': {'status': 'unavailable', 'points': [], 'validation': None},
    }


def set_fresh_output(fresh: bool) -> None:
    # Used only by a GitHub Actions step output, not as data provenance.
    path = os.environ.get('GITHUB_OUTPUT')
    if path:
        with open(path, 'a', encoding='utf-8') as output:
            output.write(f'fresh={str(fresh).lower()}\n')


def main() -> None:
    metrics: dict[str, list[tuple[int, float]]] = {}
    regions: dict[str, str] = {}
    weeks = int(os.getenv('SMARD_WEEKS', '18'))

    # Only genuine SMARD observations reach build().
    try:
        for metric in FILTERS:
            try:
                observations, region = fetch_market_metric(metric, weeks=weeks)
                metrics[metric] = observations
                regions[metric] = region
                print(f'Loaded {metric}: {len(observations)} observations ({region})', flush=True)
            except (ValueError, RuntimeError) as exc:
                if metric == 'price':
                    raise RuntimeError(f'Cannot refresh genuine SMARD prices: {exc}') from exc
                print(f'WARN optional series {metric}: {exc}', flush=True)
                metrics[metric] = []
        payload = build(metrics, regions)
    except (RuntimeError, ValueError) as exc:
        reason = str(exc)
        print(f'::warning title=SMARD refresh unavailable::{reason[:500]}', flush=True)
        payload = unavailable(reason)
        write_json(OUTPUT, payload)
        set_fresh_output(False)
        print(f'Published status: {payload["metadata"]["status"]}; no fabricated observations', flush=True)
        return

    write_json(OUTPUT, payload)
    write_json(CACHE, payload)
    set_fresh_output(True)
    print(f'Published {len(payload["history"]["price"])} real price points; '
          f'JSON size: {OUTPUT.stat().st_size} bytes', flush=True)


if __name__ == '__main__':
    main()
