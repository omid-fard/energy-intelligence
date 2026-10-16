"""Rolling-lag 24-hour hourly forecast with separate selection and final test blocks.

Inputs are historical day-ahead market prices and calendar features. This is an
illustrative forecast of the 24 hours *after the latest observation*, not a
continuous 15-minute trading signal or a trading/dispatch recommendation.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

HOUR_MS = 3_600_000
LOCAL = ZoneInfo('Europe/Berlin')


def features(stamp: int, known: dict[int, float]) -> list[float] | None:
    lagged = [known.get(stamp - lag * HOUR_MS) for lag in (24, 48, 168)]
    if any(value is None for value in lagged):
        return None
    dt = datetime.fromtimestamp(stamp / 1000, tz=timezone.utc).astimezone(LOCAL)
    hour = dt.hour + dt.minute / 60
    weekday = dt.weekday()
    doy = dt.timetuple().tm_yday
    return [
        math.sin(2 * math.pi * hour / 24), math.cos(2 * math.pi * hour / 24),
        math.sin(2 * math.pi * weekday / 7), math.cos(2 * math.pi * weekday / 7),
        math.sin(2 * math.pi * doy / 365.25), math.cos(2 * math.pi * doy / 365.25),
        float(dt.month), float(weekday >= 5),
        *map(float, lagged), lagged[0] - lagged[1], lagged[0] - lagged[2],
    ]


def rounded(number: float | None) -> float | None:
    return round(float(number), 3) if number is not None and math.isfinite(float(number)) else None


def model_factory() -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        max_iter=140, max_leaf_nodes=16, learning_rate=0.05,
        min_samples_leaf=24, l2_regularization=1.0, early_stopping=False, random_state=42,
    )


def errors(true: np.ndarray, pred: np.ndarray) -> tuple[float, float]:
    return float(mean_absolute_error(true, pred)), float(np.sqrt(mean_squared_error(true, pred)))


def make_forecast(points: list[tuple[int, float]]) -> dict:
    clean = sorted({int(t): float(v) for t, v in points
                    if math.isfinite(float(t)) and math.isfinite(float(v))}.items())
    if len(clean) < 500:
        return {'status': 'insufficient_data', 'message': 'Requires >=500 valid hourly observations',
                'points': [], 'validation': None}
    known = dict(clean)
    stamps, feature_rows, targets = [], [], []
    for stamp, price in clean:
        row = features(stamp, known)
        if row is not None:
            stamps.append(stamp)
            feature_rows.append(row)
            targets.append(price)
    if len(stamps) < 300:
        return {'status': 'insufficient_data', 'message': 'Insufficient uninterrupted 24/48/168-hour lag coverage',
                'points': [], 'validation': None}

    X, y = np.asarray(feature_rows), np.asarray(targets)
    window = min(168, max(48, len(y) // 5))
    training_end, selection_end = len(y) - 2 * window, len(y) - window
    if training_end < 150:
        return {'status': 'insufficient_data', 'message': 'Insufficient pre-validation training history',
                'points': [], 'validation': None}
    model = model_factory()
    model.fit(X[:training_end], y[:training_end])

    def candidate_predictions(start: int, end: int):
        timepoints = stamps[start:end]
        return {
            'machine_learning': model.predict(X[start:end]),
            'yesterday': np.asarray([known[t - 24 * HOUR_MS] for t in timepoints]),
            'last_week': np.asarray([known[t - 168 * HOUR_MS] for t in timepoints]),
        }

    # Choose using validation only; evaluate the chosen method on untouched later test.
    selection_predictions = candidate_predictions(training_end, selection_end)
    selection_mae = {key: errors(y[training_end:selection_end], values)[0]
                     for key, values in selection_predictions.items()}
    selected = min(selection_mae, key=selection_mae.get)
    test_predictions = candidate_predictions(selection_end, len(y))
    test_mae = {}
    test_rmse = {}
    for name, pred in test_predictions.items():
        test_mae[name], test_rmse[name] = errors(y[selection_end:], pred)

    # After evaluation, train the selected ML method on all historical observations.
    if selected == 'machine_learning':
        model.fit(X, y)
    latest = clean[-1][0]
    predictions = []
    for horizon in range(1, 25):
        stamp = latest + horizon * HOUR_MS
        row = features(stamp, known)
        if row is None:
            return {'status': 'insufficient_data',
                    'message': 'Recent hours missing required 24/48/168-hour prices',
                    'points': [], 'validation': None}
        if selected == 'machine_learning':
            predicted = float(model.predict(np.asarray([row]))[0])
        elif selected == 'yesterday':
            predicted = known[stamp - 24 * HOUR_MS]
        else:
            predicted = known[stamp - 168 * HOUR_MS]
        predictions.append({
            'ts': datetime.fromtimestamp(stamp / 1000, tz=timezone.utc).isoformat().replace('+00:00', 'Z'),
            'value': rounded(predicted),
        })

    return {
        'status': 'ok', 'selected_method': selected,
        'methods': {
            'machine_learning': 'scikit-learn HistGradientBoostingRegressor, calendar and lag features',
            'yesterday': '24-hour seasonal naive baseline',
            'last_week': '168-hour seasonal naive baseline',
        },
        'message': 'Illustrative forecast: 24 hours after the latest historical price point.',
        'validation': {
            'method': 'Time-ordered train / selection / untouched test blocks; rolling lag features.',
            'train_count': training_end, 'validation_count': window, 'test_count': window,
            'holdout_count': window, 'usable_history_count': len(y),
            'selected_on': 'validation_mae',
            'validation_mae_eur_mwh': {k: rounded(v) for k, v in selection_mae.items()},
            'mae_eur_mwh': {k: rounded(v) for k, v in test_mae.items()},
            'rmse_eur_mwh': {k: rounded(v) for k, v in test_rmse.items()},
            'selected': selected,
            'caveat': 'Single retrospective chronological test; not forward-proven live accuracy.',
        },
        'points': predictions,
    }
