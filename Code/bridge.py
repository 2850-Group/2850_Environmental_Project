import sqlite3
import datetime
from datetime import timedelta
from kivy.clock import Clock
from Database.Queries.get_row_based_on_date import row_by_timestamp
from Database.Queries.calculate_average_for_x_days import data_over_x_days
from Database.Queries.calculate_average_for_x_days import average_data_all_rows
from Database.Queries.calculate_average_for_x_days import remove_record_null

import os
DB_PATH = os.path.join(os.path.dirname(__file__), "Database", "Queries", "pest_control.db")

TICK_INTERVAL = 3  # seconds

SITE_MAIZE    = 0
SITE_BRASSICA = 1
SITE_ORCHARD  = 2

AVERAGE_WINDOW_DAYS = 14

STAT_LABELS = ["air_temp", "humidity", "leaf_wetness", "light", "vibration", "pest_count", "rain"]
# [air_temp, humidity, leaf_wetness, light, vibration, pest_count, rain]
STAT_UNITS  = ["°C", "%", "", " lux", "", "", " mm/hr"]

LEVEL_CRITICAL = "critical"
LEVEL_WARNING  = "warning"
LEVEL_NORMAL   = "normal"

class Bridge:
    """
    connects pest_control to dashboard

    each tick we: fetch site rows for timestamp
    parse these rows into stats/alerts
    find average over last AVERAGE_WINDOW_DAYS
    produce flags (up/down) per stat
    stores all this in self.maize/brassica/orchard so dashboard can read them
    """

    def __init__(self, start_year=2022, start_month=1, start_day=1, start_hour=0, start_minute=0):
        """
        opens db connection, initialises timestamp

        Parameters
        ----------
        start_year, start_month, start_day, start_hour, start_minute : int
            where we start reading data from
        """
        self.conn   = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.timestamp     = datetime.datetime(start_year, start_month, start_day, start_hour, start_minute, 0)
        self.end_timestamp = datetime.datetime(2023, 12, 31, 23, 15, 0)
        self._clock_event        = None
        self.average_window_days = AVERAGE_WINDOW_DAYS
        self.on_tick             = None
        self.maize    = None
        self.brassica = None
        self.orchard  = None

    def start(self):
        """
        starts simulation
        """
        print(f"Bridge: starting from {self.timestamp}")
        self._clock_event = Clock.schedule_interval(self.tick, TICK_INTERVAL)

    def stop(self):
        """
        close db connection
        """
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None
        self.conn.close()
        print("Bridge: stopped.")

    def tick(self, dt):
        """
        called every TICK_INTERVAL seconds
        advances time by 15 mins, fetches db rows, parses db rows, find averages+flags

        Parameters
        ----------
        dt : float
            time delta since last call 
        """

        if self.timestamp >= self.end_timestamp:
            print("Bridge: reached end of dataset.")
            self.stop()
            return

        # fetch rows for each site at this timestamp
        rows = row_by_timestamp(self.conn, self.cursor, self.timestamp)

        if not rows or len(rows) < 3:
            # skip if timestamp is missing data
            print(f"Bridge [{self.timestamp}]: incomplete data, skipping.")
            self.timestamp += timedelta(minutes=15)
            return

        maize    = rows[SITE_MAIZE]
        brassica = rows[SITE_BRASSICA]
        orchard  = rows[SITE_ORCHARD]

        # parse each row into stats/alerts
        maize_stats,    maize_alerts    = self._parse_row(maize)
        brassica_stats, brassica_alerts = self._parse_row(brassica)
        orchard_stats,  orchard_alerts  = self._parse_row(orchard)

        # cross-site average for now, should add individual average later???
        averages = self._compute_average(self.timestamp)

        # if returns true: current > average
        maize_flags    = self._compute_flags(maize_stats, averages)
        brassica_flags = self._compute_flags(brassica_stats, averages)
        orchard_flags  = self._compute_flags(orchard_stats, averages)

        # format deltas and convert allerts to dicts
        maize_deltas    = self._format_deltas(maize_stats, averages)
        brassica_deltas = self._format_deltas(brassica_stats, averages)
        orchard_deltas  = self._format_deltas(orchard_stats, averages)

        maize_alert_dicts    = self._alerts_to_dicts(maize_alerts)
        brassica_alert_dicts = self._alerts_to_dicts(brassica_alerts)
        orchard_alert_dicts  = self._alerts_to_dicts(orchard_alerts)

        # these store latest data for each stie (dashboard should read this)
        self.maize    = {"stats": maize_stats,    "flags": maize_flags,
                         "deltas": maize_deltas,  "alerts": maize_alert_dicts}
        self.brassica = {"stats": brassica_stats, "flags": brassica_flags,
                         "deltas": brassica_deltas, "alerts": brassica_alert_dicts}
        self.orchard  = {"stats": orchard_stats,  "flags": orchard_flags,
                         "deltas": orchard_deltas,  "alerts": orchard_alert_dicts}

        #temp
        #self._debug_print(maize,    maize_stats,    maize_alerts,    maize_flags)
        #self._debug_print(brassica, brassica_stats, brassica_alerts, brassica_flags)
        #self._debug_print(orchard,  orchard_stats,  orchard_alerts,  orchard_flags)

        if self.on_tick:
            self.on_tick(self.maize, self.brassica, self.orchard)

        # advance simulation
        self.timestamp += timedelta(minutes=15)


    def _parse_row(self, row):
        """
        splits row into stats and alerts lists

        Stats: air_temp, humidity, leaf_wetness, light, vibration, pest_trap_count, rain

        Alerts: status, alert_triggered, alert_pest_action, alert_pest_outbreak, alert_disease_moderate, alert_disease_high

        Parameters
        ----------
        row : tuple
            row from pest_monitoring

        Returns
        -------
        stats : list
        alerts : list
        """
        stats  = list(row[3:9]) + [row[15]]
        alerts = list(row[9:15])

        return stats, alerts

    def _compute_average(self, timestamp):
        """
        find AVERAGE_WINDOW_DAYS rolling average

        fetches all rows in the window, strips rows with null/empty values, then averages the stat columns

        Parameters
        ----------
        timestamp : datetime.datetime
            Upper bound of the averaging window (current simulation time)

        Returns
        -------
        list or None
        [air_temp, humidity, leaf_wetness, light, vibration, pest_trap_count, rain], or None if there is not enough clean data yet
        """
        raw = data_over_x_days(self.conn, self.cursor, timestamp, self.average_window_days)
        if not raw:
            return None

        clean = remove_record_null(raw)
        if not clean:
            return None

        return average_data_all_rows(clean)

    def _compute_flags(self, stats, averages):
        """
        compares each current stat against the average from last window

        Parameters
        ----------
        stats : list
            current stat values from _parse_row
        averages : list or None
            rooling average values from _compute_average or None if no average available

        Returns
        -------
        list of bool or None
            one entry per stat: True = above average (up arrow)
            False = below average (down arrow)
            None = no average
        """
        if averages is None:
            return [None] * len(stats)
        return [s > a for s, a in zip(stats, averages)]

    def _format_deltas(self, stats, averages):
        """
        produces delta string for each stat

        returns '-' if no average available yet
        otherwise returns strings like '+1.2degreeC' // '-3%' etc

        Parameters
        ----------
        stats    : list  - current stat values
        averages : list or None - rolling average values or None.

        Returns
        -------
        list of str
            one formatted string per stat
        """
        if averages is None:
            return ["–"] * len(stats)
        return [
            f"{(s - a):+.1f}{unit}"
            for s, a, unit in zip(stats, averages, STAT_UNITS)
        ]

    def _alerts_to_dicts(self, alerts):
        """
        converts alerts fields into list of alert dicts, so dashboard can display directly 

        Parameters
        ----------
        alerts : list
            Six values from _parse_row: [status, triggered, pest_action, pest_outbreak, disease_moderate, disease_high]

        Returns
        -------
        list of dict
            Each dict has keys: "level", "title", "summary", "detail".
        """
        status, triggered, pest_action, pest_outbreak, disease_mod, disease_high = alerts
        result = []

        if disease_high:
            result.append({
                "level":   LEVEL_CRITICAL,
                "title":   "High Disease Risk",
                "summary": f"Status: {status}",
                "detail":  "Disease risk is critically high. Immediate action required."
            })
        if pest_outbreak:
            result.append({
                "level":   LEVEL_CRITICAL,
                "title":   "Pest Outbreak",
                "summary": f"Status: {status}",
                "detail":  "Pest outbreak detected. Immediate action required."
            })
        if disease_mod:
            result.append({
                "level":   LEVEL_WARNING,
                "title":   "Moderate Disease Risk",
                "summary": f"Status: {status}",
                "detail":  "Disease risk is elevated. Monitor closely."
            })
        if pest_action:
            result.append({
                "level":   LEVEL_WARNING,
                "title":   "Pest Action Required",
                "summary": f"Status: {status}",
                "detail":  "Pest levels require attention."
            })

        if not result:
            result.append({
                "level":   LEVEL_NORMAL,
                "title":   "All Clear",
                "summary": f"Status: {status}",
                "detail":  "No active alerts at this time."
            })

        return result
        
'''
    def _debug_print(self, row, stats, alerts, flags):
        stat_labels  = ["air_temp", "humidity", "leaf_wet",
                        "light", "vibration", "pest_count", "rain"]
        alert_labels = ["status", "triggered", "pest_action",
                        "pest_outbreak", "disease_mod", "disease_high"]

        site = row[2]
        time = row[1]
        print(f"\n  [{time}]  site={site}")
        for label, val, flag in zip(stat_labels, stats, flags):
            arrow = "▲" if flag else ("▼" if flag is False else "–")
            print(f"    {label:<14} {val}  {arrow}")
        for label, val in zip(alert_labels, alerts):
            print(f"    {label:<14} {val}")
'''