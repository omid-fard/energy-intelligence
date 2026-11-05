"""Deterministic no-network tests for outage recovery and source diagnostics."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import build as pipeline
from src import smard
from src.forecast import HOUR_MS

START = 1750000000000


def local_fixture(n=840):
    # Only for unit tests; not saved as a production dataset.
    return [(START + i * HOUR_MS, 50 + 20 * math.sin(i * math.pi / 12)) for i in range(n)]


class PipelineRecoveryTests(unittest.TestCase):
    def test_source_outage_without_cache_creates_explicit_empty_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(pipeline, 'OUTPUT', root / 'dashboard.json'), \
                 patch.object(pipeline, 'CACHE', root / 'cache.json'), \
                 patch.object(pipeline, 'fetch_market_metric', side_effect=RuntimeError('source down')):
                pipeline.main()
            result = json.loads((root / 'dashboard.json').read_text())
            self.assertEqual(result['metadata']['status'], 'source_unavailable')
            self.assertFalse(result['history']['price'])
            self.assertFalse((root / 'cache.json').exists())

    def test_source_outage_uses_only_previous_real_data_and_removes_forecast(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, cache = root / 'dashboard.json', root / 'cache.json'
            original = pipeline.build({'price': local_fixture(), 'solar': [], 'wind': [], 'load': []})
            pipeline.write_json(cache, original)
            with patch.object(pipeline, 'OUTPUT', output), \
                 patch.object(pipeline, 'CACHE', cache), \
                 patch.object(pipeline, 'fetch_market_metric', side_effect=RuntimeError('remote down')):
                pipeline.main()
            result = json.loads(output.read_text())
            self.assertEqual(result['metadata']['status'], 'cached_stale')
            self.assertEqual(result['metadata']['generated_at'], original['metadata']['generated_at'])
            self.assertEqual(result['history']['price'], original['history']['price'])
            self.assertEqual(result['forecast']['points'], [])
            self.assertEqual(json.loads(cache.read_text())['metadata']['status'], 'live')

    def test_corrupted_cache_is_not_republished(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            cache = folder / 'cache.json'
            cache.write_text(json.dumps({'metadata': {'status': 'live'}, 'history': {'price': []}}))
            result = pipeline.unavailable('offline', cache)
            self.assertEqual(result['metadata']['status'], 'source_unavailable')
            self.assertFalse(result['history']['price'])

    def test_successful_refresh_saves_authentic_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, cache = root / 'dashboard.json', root / 'cache.json'

            def stub(metric, weeks):
                if metric == 'price':
                    return local_fixture(), 'DE'
                raise RuntimeError('optional metric unavailable')

            with patch.object(pipeline, 'OUTPUT', output), \
                 patch.object(pipeline, 'CACHE', cache), \
                 patch.object(pipeline, 'fetch_market_metric', side_effect=stub):
                pipeline.main()
            result = json.loads(output.read_text())
            self.assertEqual(result['metadata']['status'], 'live')
            self.assertEqual(result['metadata']['source_regions']['price'], 'DE')
            self.assertTrue(pipeline.is_authentic_cache(json.loads(cache.read_text())))

    def test_blocked_windows_stop_early(self):
        week_stamps = [1_750_000_000_000 + 7 * 24 * HOUR_MS * i for i in range(16)]

        def stub(url, attempts=2):
            if '/index_hour.json' in url:
                return {'timestamps': week_stamps}
            raise RuntimeError('blocked')

        with patch.object(smard, 'get_json', side_effect=stub) as getter:
            with self.assertRaisesRegex(RuntimeError, 'Only 0'):
                smard.fetch_metric(4169, weeks=16, region='DE')
        self.assertEqual(getter.call_count, 1 + smard.MAX_CONSECUTIVE_WINDOW_FAILURES)

    def test_previous_real_only_rule(self):
        self.assertFalse(pipeline.is_authentic_cache({'metadata': {'status': 'live'}}))
        self.assertFalse(pipeline.is_authentic_cache({'metadata': {'status': 'source_unavailable'}}))


if __name__ == '__main__':
    unittest.main()
