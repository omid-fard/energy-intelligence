import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.build import analytics, build, percentile
from src.forecast import HOUR_MS, make_forecast
from src.site_meta import pages_url, write_metadata
from src.smard import fetch_market_metric, fetch_metric, parse_series

START = 1740000000000


def timeseries(n=820, price=75.0):
    return [(START + i * HOUR_MS, price + 20 * math.sin(2 * math.pi * i / 24)) for i in range(n)]


class ReleaseTests(unittest.TestCase):
    def test_region_fallback_is_attributed(self):
        def stub(filter_id, weeks, region):
            if region == 'DE-LU':
                raise RuntimeError('fake unavailable zone')
            return [(1234000, 9)]
        with patch('src.smard.fetch_metric', side_effect=stub):
            points, region = fetch_market_metric('price', weeks=4)
        self.assertEqual(region, 'DE')
        self.assertEqual(points[0][1], 9)

    def test_market_series_uses_de_lu_first(self):
        with patch('src.smard.fetch_metric', return_value=[(1234000, 9)]) as mock_fetch:
            _, region = fetch_market_metric('price', weeks=4)
        self.assertEqual(region, 'DE-LU')
        self.assertEqual(mock_fetch.call_args.kwargs['region'], 'DE-LU')

    def test_hourly_window_validation(self):
        with self.assertRaises(ValueError):
            fetch_metric(4169, weeks=100)

    def test_invalid_nan_timestamp_rejected(self):
        parsed = parse_series({'series': [[float('nan'), 10], [123456, -25], [123457, float('inf')]]})
        self.assertEqual(parsed, [(123456, -25.)])

    def test_percentile_math(self):
        self.assertAlmostEqual(percentile([10, 20, 30], 10), 12)
        self.assertAlmostEqual(percentile([10, 20, 30], 90), 28)

    def test_negative_prices_and_volatility(self):
        items = [(START + n * HOUR_MS, n - 90) for n in range(168)]
        metrics = analytics(items)
        self.assertEqual(metrics['negative_price_hours'], 90)
        self.assertGreater(metrics['p10_p90_spread_eur_mwh'], 0)
        self.assertEqual(metrics['points'], 168)

    def test_selected_model_test_is_separate_from_selection(self):
        forecast = make_forecast(timeseries())
        report = forecast['validation']
        self.assertEqual(forecast['status'], 'ok')
        self.assertEqual(report['selected_on'], 'validation_mae')
        self.assertEqual(report['validation_count'], report['test_count'])
        self.assertIn('validation_mae_eur_mwh', report)
        self.assertIn('mae_eur_mwh', report)
        self.assertEqual(len(forecast['points']), 24)

    def test_generated_output_no_synthetic_price_claim(self):
        # Test fixture is synthetic; this test checks schema only, never published.
        prices = timeseries()
        payload = build({'price': prices, 'solar': [], 'wind': [], 'load': []}, {'price': 'DE'})
        self.assertEqual(payload['metadata']['source_regions']['price'], 'DE')
        self.assertEqual(payload['analytics']['negative_price_hours'], 0)
        self.assertEqual(payload['metadata']['resolution'], 'hour')

    def test_repository_url_and_sitemap(self):
        self.assertEqual(pages_url('example-org/energy-intelligence'),
                         'https://example-org.github.io/energy-intelligence/')
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'index.html').write_text('<head><!-- SITE_URL_METADATA --></head>', encoding='utf-8')
            url = write_metadata('example-org/energy-intelligence', folder)
            self.assertIn('canonical', (folder/'index.html').read_text())
            self.assertIn(url, (folder/'sitemap.xml').read_text())
            self.assertIn('Sitemap:', (folder/'robots.txt').read_text())

    def test_bad_repository_name_blocked(self):
        for repo in ('bad', 'org/../../bad', '/energy', 'org/repo name'):
            with self.assertRaises(ValueError):
                pages_url(repo)

    def test_initial_placeholder_is_not_fake_data(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root/'docs/data/dashboard.json').read_text())
        self.assertNotEqual(data['metadata']['status'], 'live')
        self.assertFalse(data['history']['price'])


if __name__ == '__main__':
    unittest.main()
