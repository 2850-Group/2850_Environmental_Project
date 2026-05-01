import unittest
import datetime
from bridge import Bridge

_bridge = Bridge()

MAIZE_ROW = (2, '2022-01-01 00:00:00', 'site_maize', 14.83, 97.1, 0.872, 1.0, 0.397, 9, 'warning', 1,  1,  0,  0,  0,  0.5)
EXPECTED_STATS  = [14.83, 97.1, 0.872, 1.0, 0.397, 9, 0.5]
EXPECTED_ALERTS = ['warning', 1, 1, 0, 0, 0]

class TestParseRow(unittest.TestCase):
    """_parse_row() should split a DB row into stats and alerts"""

    def test_stats_correct_values(self):
        stats, _ = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(stats, EXPECTED_STATS)

    def test_stats_length(self):
        stats, _ = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(len(stats), 7)

    def test_alerts_correct_values(self):
        _, alerts = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(alerts, EXPECTED_ALERTS)

    def test_alerts_length(self):
        _, alerts = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(len(alerts), 6)

    def test_rain_is_last_stat(self):
        stats, _ = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(stats[-1], 0.5)

class TestComputeFlags(unittest.TestCase):
    """_compute_flags() should return True/False per stat vs average, or None if no average"""

    def test_all_above_average(self):
        stats    = [10, 20, 30, 40, 50, 60, 70]
        averages = [5,  15, 25, 35, 45, 55, 65]
        flags = _bridge._compute_flags(stats, averages)
        self.assertTrue(all(flags))

    def test_all_below_average(self):
        stats    = [1, 2, 3, 4, 5, 6, 7]
        averages = [10, 20, 30, 40, 50, 60, 70]
        flags = _bridge._compute_flags(stats, averages)
        self.assertTrue(all(f is False for f in flags))

    def test_mixed_above_and_below(self):
        stats    = [10, 1,  10, 1]
        averages = [5,  10, 5,  10]
        flags = _bridge._compute_flags(stats, averages)
        self.assertEqual(flags, [True, False, True, False])

    def test_no_average_returns_none_per_stat(self):
        stats = [1, 2, 3, 4, 5, 6, 7]
        flags = _bridge._compute_flags(stats, None)
        self.assertEqual(flags, [None] * 7)

    def test_output_length_matches_stats(self):
        stats    = [1, 2, 3]
        averages = [1, 2, 3]
        flags = _bridge._compute_flags(stats, averages)
        self.assertEqual(len(flags), len(stats))

class TestFormatDeltas(unittest.TestCase):
    """_format_deltas() must return correctly signed, unit-suffixed strings."""

    def test_no_average_returns_dashes(self):
        stats  = [1, 2, 3, 4, 5, 6, 7]
        deltas = _bridge._format_deltas(stats, None)
        self.assertEqual(deltas, ["–"] * 7)

    def test_positive_delta_has_plus_sign(self):
        stats    = [15.0, 50.0, 0.5, 10.0, 0.5, 5.0, 1.0]
        averages = [10.0, 40.0, 0.3,  5.0, 0.2, 3.0, 0.5]
        deltas = _bridge._format_deltas(stats, averages)
        for d in deltas:
            self.assertTrue(d.startswith("+"), f"Expected '+' prefix, got: {d}")

    def test_negative_delta_has_minus_sign(self):
        stats    = [5.0, 30.0, 0.1, 2.0, 0.1, 1.0, 0.1]
        averages = [10.0, 40.0, 0.3, 5.0, 0.2, 3.0, 0.5]
        deltas = _bridge._format_deltas(stats, averages)
        for d in deltas:
            self.assertTrue(d.startswith("-"), f"Expected '-' prefix, got: {d}")

    def test_units_appended_correctly(self):
        stats    = [15.0, 50.0, 0.5, 10.0, 0.5, 5.0, 1.0]
        averages = [10.0, 40.0, 0.3,  5.0, 0.2, 3.0, 0.5]
        deltas = _bridge._format_deltas(stats, averages)
        self.assertIn("°C",    deltas[0])
        self.assertIn("%",     deltas[1])
        self.assertIn("lux",   deltas[3])
        self.assertIn("mm/hr", deltas[6])

    def test_output_length(self):
        stats    = [1, 2, 3, 4, 5, 6, 7]
        averages = [1, 2, 3, 4, 5, 6, 7]
        deltas = _bridge._format_deltas(stats, averages)
        self.assertEqual(len(deltas), 7)

class TestAlertsToDicts(unittest.TestCase):
    """_alerts_to_dicts() should convert raw alert flags into correctly structured dicts"""

    def _make_alerts(self, status='normal', triggered=0, pest_action=0, pest_outbreak=0, disease_mod=0, disease_high=0):
        return [status, triggered, pest_action, pest_outbreak, disease_mod, disease_high]

    def test_no_flags_returns_all_clear(self):
        result = _bridge._alerts_to_dicts(self._make_alerts())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "All Clear")
        self.assertEqual(result[0]["level"], "normal")

    def test_disease_high_is_critical(self):
        result = _bridge._alerts_to_dicts(self._make_alerts(disease_high=1))
        titles  = [d["title"] for d in result]
        levels  = [d["level"] for d in result]
        self.assertIn("High Disease Risk", titles)
        self.assertIn("critical", levels)

    def test_pest_outbreak_is_critical(self):
        result = _bridge._alerts_to_dicts(self._make_alerts(pest_outbreak=1))
        titles = [d["title"] for d in result]
        levels = [d["level"] for d in result]
        self.assertIn("Pest Outbreak", titles)
        self.assertIn("critical", levels)

    def test_disease_mod_is_warning(self):
        result = _bridge._alerts_to_dicts(self._make_alerts(disease_mod=1))
        self.assertEqual(result[0]["level"], "warning")
        self.assertEqual(result[0]["title"], "Moderate Disease Risk")

    def test_pest_action_is_warning(self):
        result = _bridge._alerts_to_dicts(self._make_alerts(pest_action=1))
        self.assertEqual(result[0]["level"], "warning")
        self.assertEqual(result[0]["title"], "Pest Action Required")

    def test_multiple_flags_returns_multiple_dicts(self):
        result = _bridge._alerts_to_dicts(
            self._make_alerts(disease_high=1, pest_outbreak=1, disease_mod=1)
        )
        self.assertEqual(len(result), 3)

    def test_criticals_come_before_warnings(self):
        result = _bridge._alerts_to_dicts(
            self._make_alerts(disease_high=1, pest_action=1)
        )
        self.assertEqual(result[0]["level"], "critical")
        self.assertEqual(result[1]["level"], "warning")

    def test_each_dict_has_required_keys(self):
        result = _bridge._alerts_to_dicts(self._make_alerts(disease_high=1))
        for d in result:
            self.assertIn("level",   d)
            self.assertIn("title",   d)
            self.assertIn("summary", d)
            self.assertIn("detail",  d)

    def test_status_string_appears_in_summary(self):
        result = _bridge._alerts_to_dicts(
            self._make_alerts(status='warning', pest_action=1)
        )
        self.assertIn("warning", result[0]["summary"])

if __name__ == '__main__':
    unittest.main()
