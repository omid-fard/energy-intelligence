"""Download authentic SMARD data, compute auditable metrics, build public JSON."""
from __future__ import annotations

import json
import math
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

from src.forecast import HOUR_MS, make_forecast
from src.smard import FILTERS, fetch_market_metric, load_observations, open_db, save_observations

OUTPUT = Path(__file__).resolve().parents[1] / 'docs' / 'data' / 'dashboard.json'


def iso(stamp: int) -> str:
    return datetime.fromtimestamp(stamp / 1000, tz=timezone.utc).isoformat().replace('+00:00', 'Z')


def serialize(points: list[tuple[int, float]]) -> list[dict]:
    return [{'ts': iso(stamp), 'value': round(value, 3)} for stamp, value in points]


def percentile(sorted_values: list[float], percentile_number: int) -> float:
    """Linear interpolation between adjacent observations (no external dependencies)."""
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
        'p10_eur_mwh': round(p10, 2), 'p90_eur_mwh': round(p90, 2),
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
                'license': 'CC BY 4.0', 'market': 'German/Luxembourg day-ahead wholesale market',
                'generated_at': now.isoformat().replace('+00:00', 'Z'),
                'latest_price_timestamp': iso(latest), 'lag_hours_at_build': round(gap, 1),
                'resolution': 'hour', 'underlying_market_resolution': '15 min since 2025-09-30',
                'price_unit': 'EUR/MWh', 'energy_unit': 'MWh/hourly interval',
                'historical_observations': len(prices),
                'source_regions': source_regions or {'price': 'DE-LU', 'solar': 'DE', 'wind': 'DE', 'load': 'DE'},
                'available_metrics': [key for key in FILTERS if history[key]],
                'data_quality': {'recent_24h_observations': len(day),
                                 'forecast_requires_complete_lags': True,
                                 'real_market_data_only': True},
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


def main():
    metrics = {}
    regions = {}
    weeks = int(os.getenv('SMARD_WEEKS', '18'))
    for metric in FILTERS:
        try:
            observations, region = fetch_market_metric(metric, weeks=weeks)
            metrics[metric] = observations
            regions[metric] = region
            print(f'Loaded {metric}: {len(observations)} observations ({region})', flush=True)
        except (ValueError, RuntimeError) as exc:
            if metric == 'price':
                raise RuntimeError(f'Cannot publish without genuine SMARD prices: {exc}') from exc
            print(f'WARN optional series {metric}: {exc}', flush=True)
            metrics[metric] = []
    payload = build(metrics, regions)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False,
                                 separators=(',', ':')), encoding='utf-8')
    print(f'Wrote {OUTPUT}: {OUTPUT.stat().st_size} bytes')


if __name__ == '__main__':
    main()
