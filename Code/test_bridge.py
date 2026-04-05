"""
Tests for the Bridge helper methods in bridge.py.

Run from the Code/ directory:
    python -m unittest test_bridge

Covers:
    _parse_row()        — splits a DB row into stats and alerts
    _compute_flags()    — compares stats against averages to get up/down flags
    _format_deltas()    — formats delta strings for dashboard display
    _alerts_to_dicts()  — converts raw alert fields to dashboard-ready dicts
    _compute_average()  — fetches and averages real DB data over a time window
"""

import unittest
import datetime

from bridge import Bridge


# ── Shared Bridge instance ────────────────────────────────────────────────────
# One instance is reused across all test classes so we only open one DB
# connection for the whole test run.
_bridge = Bridge()


# ── Known-good sample row (taken from unit_tests.py test_returns_correct_data)─
# Index:   0   1                       2              3      4     5      6    7      8   9         10  11  12  13  14   15
MAIZE_ROW = (2, '2022-01-01 00:00:00', 'site_maize', 14.83, 97.1, 0.872, 1.0, 0.397, 9, 'warning', 1,  1,  0,  0,  0,  0.5)

EXPECTED_STATS  = [14.83, 97.1, 0.872, 1.0, 0.397, 9, 0.5]   # cols 3-8 + col 15
EXPECTED_ALERTS = ['warning', 1, 1, 0, 0, 0]                  # cols 9-14


# ─────────────────────────────────────────────────────────────────────────────
class TestParseRow(unittest.TestCase):
    """_parse_row() must correctly split a DB row into stats and alerts."""

    def test_stats_correct_values(self):
        stats, _ = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(stats, EXPECTED_STATS)

    def test_stats_length(self):
        # 6 environmental readings + rain = 7 total
        stats, _ = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(len(stats), 7)

    def test_alerts_correct_values(self):
        _, alerts = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(alerts, EXPECTED_ALERTS)

    def test_alerts_length(self):
        # status + 5 integer flags = 6 total
        _, alerts = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(len(alerts), 6)

    def test_rain_is_last_stat(self):
        # wx_rain_mm_hr is col 15 — must end up as the 7th stat, not lost
        stats, _ = _bridge._parse_row(MAIZE_ROW)
        self.assertEqual(stats[-1], 0.5)


# ─────────────────────────────────────────────────────────────────────────────
class TestComputeFlags(unittest.TestCase):
    """_compute_flags() must return True/False per stat vs average, or None if no average."""

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


# ─────────────────────────────────────────────────────────────────────────────
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
        self.assertIn("°C",    deltas[0])  # air_temp
        self.assertIn("%",     deltas[1])  # humidity
        self.assertIn("lux",   deltas[3])  # light
        self.assertIn("mm/hr", deltas[6])  # rain

    def test_output_length(self):
        stats    = [1, 2, 3, 4, 5, 6, 7]
        averages = [1, 2, 3, 4, 5, 6, 7]
        deltas = _bridge._format_deltas(stats, averages)
        self.assertEqual(len(deltas), 7)


# ─────────────────────────────────────────────────────────────────────────────
class TestAlertsToDicts(unittest.TestCase):
    """_alerts_to_dicts() must convert raw alert flags into correctly structured dicts."""

    def _make_alerts(self, status='normal', triggered=0, pest_action=0,
                     pest_outbreak=0, disease_mod=0, disease_high=0):
        """Helper: build an alerts list with named arguments for readability."""
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
        # disease_high (critical) + pest_action (warning) — critical must be first
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


# ─────────────────────────────────────────────────────────────────────────────
class TestComputeAverage(unittest.TestCase):
    """_compute_average() must return a 7-item list from real DB data, or None if no data."""

    def test_returns_list_when_data_exists(self):
        # 2022-02-01 is well into the dataset — 14 days of prior data available
        ts = datetime.datetime(2022, 2, 1, 0, 0, 0)
        result = _bridge._compute_average(ts)
        self.assertIsInstance(result, list)

    def test_returns_seven_values(self):
        ts = datetime.datetime(2022, 2, 1, 0, 0, 0)
        result = _bridge._compute_average(ts)
        self.assertEqual(len(result), 7)

    def test_air_temp_average_in_plausible_range(self):
        # Average air temperature should be a reasonable outdoor value
        ts = datetime.datetime(2022, 2, 1, 0, 0, 0)
        result = _bridge._compute_average(ts)
        self.assertTrue(-10 < result[0] < 50,
                        f"Air temp average out of plausible range: {result[0]}")

    def test_humidity_average_in_plausible_range(self):
        # Relative humidity must be between 0 and 100
        ts = datetime.datetime(2022, 2, 1, 0, 0, 0)
        result = _bridge._compute_average(ts)
        self.assertTrue(0 <= result[1] <= 100,
                        f"Humidity average out of range: {result[1]}")

    def test_returns_none_when_no_data(self):
        # Timestamp well before the dataset starts — no rows will be found
        ts = datetime.datetime(2021, 1, 1, 0, 0, 0)
        result = _bridge._compute_average(ts)
        self.assertIsNone(result)


# ─────────────────────────────────────────────────────────────────────────────
class TestTick(unittest.TestCase):
    """
    tick() must fetch real DB rows and populate self.maize/brassica/orchard.

    We call tick(0) directly — the dt argument is ignored by tick() itself,
    and Clock is only used in start(), so no Kivy app is needed here.

    A fresh Bridge is created for this class so the shared _bridge timestamp
    is not affected.
    """

    @classmethod
    def setUpClass(cls):
        cls.b = Bridge()
        cls.initial_timestamp = cls.b.timestamp
        cls.b.tick(0)   # single tick — populates maize/brassica/orchard

    @classmethod
    def tearDownClass(cls):
        cls.b.conn.close()

    # ── Site dicts exist after a tick ─────────────────────────────────────────

    def test_maize_populated(self):
        self.assertIsNotNone(self.b.maize)

    def test_brassica_populated(self):
        self.assertIsNotNone(self.b.brassica)

    def test_orchard_populated(self):
        self.assertIsNotNone(self.b.orchard)

    # ── Each site dict has the four expected keys ──────────────────────────────

    def test_site_dict_keys(self):
        for site in (self.b.maize, self.b.brassica, self.b.orchard):
            self.assertIn("stats",  site)
            self.assertIn("flags",  site)
            self.assertIn("deltas", site)
            self.assertIn("alerts", site)

    # ── Stats list ────────────────────────────────────────────────────────────

    def test_stats_has_seven_values(self):
        for site in (self.b.maize, self.b.brassica, self.b.orchard):
            self.assertEqual(len(site["stats"]), 7)

    # ── Flags list ────────────────────────────────────────────────────────────

    def test_flags_has_seven_values(self):
        for site in (self.b.maize, self.b.brassica, self.b.orchard):
            self.assertEqual(len(site["flags"]), 7)

    def test_flags_are_bool_or_none(self):
        # Near the start of the dataset there may be no 14-day average yet,
        # so None is valid; otherwise each flag must be a bool
        for site in (self.b.maize, self.b.brassica, self.b.orchard):
            for flag in site["flags"]:
                self.assertIn(flag, (True, False, None))

    # ── Deltas list ───────────────────────────────────────────────────────────

    def test_deltas_has_seven_values(self):
        for site in (self.b.maize, self.b.brassica, self.b.orchard):
            self.assertEqual(len(site["deltas"]), 7)

    def test_deltas_are_strings(self):
        for site in (self.b.maize, self.b.brassica, self.b.orchard):
            for d in site["deltas"]:
                self.assertIsInstance(d, str)

    # ── Alerts list ───────────────────────────────────────────────────────────

    def test_alerts_is_nonempty_list(self):
        # _alerts_to_dicts always returns at least an "All Clear" entry
        for site in (self.b.maize, self.b.brassica, self.b.orchard):
            self.assertIsInstance(site["alerts"], list)
            self.assertGreater(len(site["alerts"]), 0)

    def test_each_alert_has_required_keys(self):
        for site in (self.b.maize, self.b.brassica, self.b.orchard):
            for alert in site["alerts"]:
                self.assertIn("level",   alert)
                self.assertIn("title",   alert)
                self.assertIn("summary", alert)
                self.assertIn("detail",  alert)

    # ── Timestamp advances ────────────────────────────────────────────────────

    def test_timestamp_advances_15_minutes(self):
        expected = self.initial_timestamp + datetime.timedelta(minutes=15)
        self.assertEqual(self.b.timestamp, expected)


if __name__ == '__main__':
    unittest.main()
