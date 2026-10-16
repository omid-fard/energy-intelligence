import math
import unittest
from datetime import datetime, timezone
from src.forecast import HOUR_MS, features, make_forecast
from src.build import build


START = int(datetime(2026, 3, 1, tzinfo=timezone.utc).timestamp() * 1000)


def fake_prices(n=800):
    return [(START + i*HOUR_MS, 60 + 18*math.sin(2*math.pi*(i%24)/24) + (i%7)*0.3) for i in range(n)]


class ForecastTests(unittest.TestCase):
    def test_too_few_samples(self):
        forecast = make_forecast(fake_prices(100))
        self.assertEqual(forecast['status'], 'insufficient_data')

    def test_features_use_lagged_values(self):
        prices = fake_prices(300)
        lookup = dict(prices)
        row = features(prices[200][0], lookup)
        self.assertIsNotNone(row)
        self.assertAlmostEqual(row[8], prices[176][1])

    def test_forecast_24_hours_and_validation(self):
        forecast = make_forecast(fake_prices())
        self.assertEqual(forecast['status'], 'ok', forecast.get('message'))
        self.assertEqual(len(forecast['points']), 24)
        self.assertEqual(forecast['validation']['holdout_count'], 126)
        self.assertIn(forecast['selected_method'], ('machine_learning', 'yesterday', 'last_week'))

    def test_pipeline_builds_real_schema_from_local_fixture(self):
        prices = fake_prices()
        data = build({'price': prices, 'solar': prices[-100:], 'wind': [], 'load': []})
        self.assertEqual(len(data['forecast']['points']), 24)
        self.assertIn('Bundesnetzagentur | SMARD.de', data['metadata']['source'])
        self.assertEqual(len(data['history']['price']), 800)


if __name__ == '__main__':
    unittest.main()
