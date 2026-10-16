import unittest

from src.smard import parse_series, open_db, save_observations, load_observations


class SmardTests(unittest.TestCase):
    def test_parse_series_handles_null_and_duplicates(self):
        value = parse_series({'series': [[1800000, 4.5], [1800000, 5.5], [3600000, None], [7200000, float('nan')], [10800000, -13.7]]})
        self.assertEqual(value, [(1800000, 5.5), (10800000, -13.7)])

    def test_parse_requires_series(self):
        with self.assertRaises(ValueError):
            parse_series({})

    def test_sql_upsert(self):
        db = open_db()
        save_observations(db, 'price', [(3600000, 10), (7200000, 12)])
        save_observations(db, 'price', [(3600000, 14)])
        self.assertEqual(load_observations(db, 'price'), [(3600000, 14.0), (7200000, 12.0)])
        db.close()


if __name__ == '__main__':
    unittest.main()
