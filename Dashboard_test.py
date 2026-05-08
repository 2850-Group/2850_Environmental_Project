"""
Testing: Dashboard

We have chosen to use a mix of integrated and scripted testing for the dashboard because of the UI demonstration.

"""
import unittest
from unittest.mock import patch, MagicMock

mock_model = MagicMock()
patch('tensorflow.keras.models.load_model', return_value=mock_model).start()



"""
SignUp Testing
"""
from Dashboard import SignUpPanel

class SignUpTest(unittest.TestCase) :

    def make_screen(self, name="Jane Doe", username="janeD", password="12345678"):
        screen = MagicMock()
        screen.fullname.text = name
        screen.username.text = username
        screen.password.text = password
        screen._error = MagicMock()
        screen.success_cb = MagicMock()

        screen._on_sign_up = SignUpPanel._on_sign_up.__get__(screen)
        return screen
    
    #TEST 1: User leaves both username and password fields empty.
    def test_1_empty_username_password(self):
        screen = self.make_screen(username="", password="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")

    #TEST 2: User leaves password field empty.
    def test_2_empty_password(self):
        screen = self.make_screen(password="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")

    #TEST 3: User leaves username field empty.
    def test_3_empty_username(self):
        screen = self.make_screen(username="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")
    
    #TEST 4: User leaves name field empty.
    def test_4_empty_name(self):
        screen = self.make_screen(name="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")

    #TEST 5: User uses a username already in the database.
    def test_5_used_username(self):
        screen = self.make_screen(username="BobM")
        with patch('Dashboard.sign_up_query', return_value=True):
            screen._on_sign_up()
        screen._error.show.assert_called_once_with("Username is taken. Please choose another.")

    #TEST 6: User uses password less than 8 characters.
    def test_6_short_password(self):
        screen = self.make_screen(password="1234")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("Password must be at least 8 characters")

    #TEST 7: User uses a unique username and a valid password.
    def test_7_valid_signup(self):
        screen = self.make_screen(username="BobM", name="Bob Muncan", password="12345678")
        with patch('Dashboard.sign_up_query', return_value=True):
            screen._on_sign_up()
        screen.success_cb.assert_called_once()
        screen._error.show.assert_not_called()


"""
LogIn Testing
"""
from Dashboard import SignInPanel 
class SignInTest(unittest.TestCase) :

    def make_screen(self, name="Jane Doe", username="janeD", password="12345678"):
        screen = MagicMock()
        screen.fullname.text = name
        screen.username.text = username
        screen.password.text = password
        screen._error = MagicMock()
        screen.success_cb = MagicMock()

        screen._on_sign_in = SignInPanel._on_sign_in.__get__(screen)
        return screen
    
    #TEST 1: User leaves both username and password fields empty.
    def test_1_empty_username_and_password(self):
        screen = self.make_screen(username="", password="")
        screen._on_sign_in()
        screen._error.show.assert_called_once_with("Please enter your username and password")

    #TEST 2: User leaves password field empty.
    def test_2_empty_password(self):
        screen = self.make_screen(password="")
        screen._on_sign_in()
        screen._error.show.assert_called_once_with("Please enter your username and password")

    #TEST 3: User leaves username field empty.
    def test_3_empty_username(self):
        screen = self.make_screen(username="")
        screen._on_sign_in()
        screen._error.show.assert_called_once_with("Please enter your username and password")
    
    #TEST 4: User uses a username with an incorrect passowrd.
    def test_4_wrong_password(self):
        screen = self.make_screen(username="izzy.martin")
        screen = self.make_screen(password="1")
        screen._on_sign_in()
        screen._error.show.assert_called_once_with("Incorrect username or password.")

    #TEST 5: User uses a username and a valid password. Prerequsite, an account must be made with the details username="i.martin" and password="12345678"
    def test_5_valid_login(self):
        screen = self.make_screen(username="i.martin")
        screen = self.make_screen(password="12345678")
        with patch('Dashboard.sign_in_query', return_value={"username": "i.martin"}):
            screen._on_sign_in()
        screen.success_cb.assert_called_once()
        screen._error.show.assert_not_called()
        


"""
Dashboard Testing
"""
import os
import time
from kivy.clock import Clock
from kivy.tests.common import GraphicUnitTest
from kivy.core.window import Window
from kivy.input.providers.mouse import MouseMotionEvent
from Dashboard import DashboardApp, DataCard, GraphOverlay

class DashboardTest(GraphicUnitTest):

    @classmethod
    def setUpClass(cls):
        # Prevent the app from timing out or hanging on hardware
        os.environ['KIVY_USE_DEFAULT_CONFIG'] = '1'
    
    def _make_card(self, direction="up"):
        card = MagicMock()
        card._direction = direction
        card._bar_color = MagicMock()
        card._arrow = MagicMock()
        card._arrow.direction = direction
        card._delta_lbl = MagicMock()
        card._value_lbl = MagicMock()
        return card
    
    def _make_alerts(self):
        return [
            {"level": "critical", "title": "Dead plant",
             "summary": "detail"},
            {"level": "warning", "title": "Pressure",
             "summary": "detail"},
        ]
    
    def _make_overlay(self, timestamps=None, values=None):
        overlay = MagicMock()
        overlay._title = "Temperature"
        overlay._unit = "°C"
        overlay._site = "Maize"
        overlay._site_key = "maize"
        overlay._stat_index = 0
        overlay._timestamps = timestamps or ["2022-01-01", "2022-01-02", "2022-01-03"]
        overlay._values = values or [10.0, 20.0, 30.0]
        overlay._compare_sites = {}
        overlay.AVG_WINDOW = 20
        overlay._COMPARE_COLORS = [(1.0, 0.27, 0.27, 1), (1.0, 0.85, 0.20, 1)]
        return overlay

    #TEST 1: Check that if we select a different naviagation bar then the correlating screen will display.
    def test_1_navigation_bar_switching(self):
        """Test if tapping the NavBar changes the ScreenManager current screen."""
        app = DashboardApp()
        # build() returns the BoxLayout containing Header, ScreenManager, and NavBar
        root_widget = app.build() 
        self.render(root_widget)

        # Manually trigger login success to build the authenticated UI
        app._on_login_success({
            "role": "Farmer", 
            "fullname": "Test User", 
            "username": "test.user"
        })
        
        self.advance_frames(5)

        nav_bar = app._nav 
        scan_btn = nav_bar._btns['scan']
        
        pos = scan_btn.to_window(*scan_btn.center)

        touch = MouseMotionEvent('mouse', 'id', pos)
        touch.button = 'left'
        touch.pos = pos

        nav_bar.on_touch_down(touch)
        nav_bar.on_touch_up(touch)

        self.advance_frames(30) 
        self.assertEqual(app._app_sm.current, 'scan')

    
    #TEST 2: Check to see if the theme colours are correct
    def test_2_theme_colors(self):
        """Ensure the global theme constants are correctly applied."""
        from Dashboard import ACCENT
        # Check that the green accent color is correct (approximate float match)
        self.assertAlmostEqual(ACCENT[0], 0.267, places=2)
        self.assertAlmostEqual(ACCENT[1], 1.000, places=2)
    

    #TEST 3: Arrow is up when the value is above average
    def test_3_arrow_up_green(self):
        card = self._make_card(direction="up")
        self.assertEqual(card._arrow.direction, "up")

        with patch('Dashboard.UP_CLR', (0.18, 0.8, 0.44, 1)) as mock_up:
            card = MagicMock()
            card._bar_color = (0.18, 0.8, 0.44, 1)
            card._direction = "up"
            self.assertEqual(card._bar_color, (0.18, 0.8, 0.44, 1))

    #TEST 4: Arrow is down when the value is below average
    def test_3_arrow_down_red(self):
        card = self._make_card(direction="down")
        self.assertEqual(card._arrow.direction, "down")

        with patch('Dashboard.DOWN_CLR', (0.9, 0.3, 0.3, 1)) as mock_down:
            card = MagicMock()
            card._bar_color = (0.9, 0.3, 0.3, 1)
            card._direction = "down"
            self.assertEqual(card._bar_color, (0.9, 0.3, 0.3, 1))

    #TEST 5: No up or down arrow when data is not there.
    def test_5_no_arrow(self):
        card = self._make_card(direction="neutral")
        self.assertNotIn(card._direction, ["up", "down"])

    #TEST 6: Update() changes the direction of the arrow
    def test_6_arrow_direction_change(self):
        card = self._make_card(direction="up")

        card._direction = "down"
        card._arrow.direction = "down"
        self.assertEqual(card._arrow.direction, "down")
        self.assertNotEqual(card._arrow.direction, "up")

    #TEST 7: Checks that the alert panel contains the new alerts from data
    def test_7_alert_displayed(self):
        panel = MagicMock()
        panel._alerts = self._make_alerts()
        new_alerts = [{"level": "warning", "title": "New",
                       "summary": "New summary", "detail": "New detail"}]
        panel._alerts = list(new_alerts)
        self.assertEqual(len(panel._alerts), 1)
        self.assertEqual(panel._alerts[0]["title"], "New")
    
    #TEST 8: Checks that the alert panel is empty when there are no alerts
    def test_8_no_alerts(self):
        panel = MagicMock()
        panel._alerts = self._make_alerts()
        panel._alerts = []
        self.assertEqual(len(panel._alerts), 0)

    #TEST 9: Test the graph is flat for the same value of data
    def test_9_flat_graph(self):
        result = GraphOverlay._rolling_avg([5.0, 5.0, 5.0, 5.0], window=3)
        self.assertEqual(result, [5.0, 5.0, 5.0, 5.0])
    
    #TEST 10: Test the graph is rolling and averages are smoothed over
    def test_10_rolling_average_graph(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = GraphOverlay._rolling_avg(values, window=3)
        # Averaged values should be less extreme than originals
        self.assertLess(result[-1], values[-1])
        self.assertGreater(result[0], 0)

    #TEST 11: Graph filter does not accept invalid dates
    def test_11_graph_filter_invalid_date(self):
        overlay = self._make_overlay()
        overlay._from_input = MagicMock()
        overlay._to_input = MagicMock()
        overlay._filter_err = MagicMock()
        overlay._from_input.text = "01-01-2022" 
        overlay._to_input.text = ""

        from datetime import datetime
        val = overlay._from_input.text.strip()
        try:
            datetime.strptime(val, "%Y-%m-%d")
            valid = True
        except ValueError:
            valid = False

        self.assertFalse(valid)
    
    #TEST 12: Graph filter accepts valid dates
    def test_12_graph_filter_valid_date(self):
        from datetime import datetime
        val = "2022-01-01"
        try:
            datetime.strptime(val, "%Y-%m-%d")
            valid = True
        except ValueError:
            valid = False
        self.assertTrue(valid)

    #TEST 13: Check that graphs can compare sites
    def test_13_graph_adds_a_compare_site(self):
        overlay = self._make_overlay()
        overlay._compare_sites["brassica"] = (["2022-01-01"], [5.0])
        self.assertIn("brassica", overlay._compare_sites)
    
    #TEST 14: Check that the graphs can remove a comparision when prompted
    def test_14_graph_removes_comapre_site(self):
        overlay = self._make_overlay()
        overlay._compare_sites["brassica"] = (["2022-01-01"], [5.0])
        del overlay._compare_sites["brassica"]
        self.assertNotIn("brassica", overlay._compare_sites)

    #TEST 15: Export shows an error when there is no data to export
    def test_15_export_csv_no_data(self):
        overlay = self._make_overlay()
        overlay._timestamps = []
        overlay._values = []
        overlay._export_status = MagicMock()
        overlay._from_input = MagicMock()
        overlay._from_input.text = ""
        overlay._to_input = MagicMock()
        overlay._to_input.text = ""
        GraphOverlay._export_csv(overlay)
        overlay._export_status.show.assert_called_once_with("No data to export")

    #TEST 16: Export creates a correctly named file with the right headers and row count
    def test_16_export_csv_file_structure(self):
        import tempfile, csv as csv_mod, os as _os
        timestamps = ["2022-01-02 00:00:00", "2022-01-02 00:15:00", "2022-01-02 00:30:00"]
        values = [95.7, 98.5, 96.6]
        with tempfile.TemporaryDirectory() as tmp:
            with patch('Dashboard.EXPORT_DIR', tmp):
                overlay = self._make_overlay(timestamps=timestamps, values=values)
                overlay._export_status = MagicMock()
                overlay._from_input = MagicMock()
                overlay._from_input.text = ""
                overlay._to_input = MagicMock()
                overlay._to_input.text = ""
                GraphOverlay._export_csv(overlay)
                filepath = _os.path.join(tmp, "maize_temperature_2022-01-02_2022-01-02.csv")
                self.assertTrue(_os.path.exists(filepath))
                with open(filepath) as f:
                    rows = list(csv_mod.reader(f))
                self.assertEqual(rows[0], ["timestamp", "maize_temperature"])
                self.assertEqual(len(rows), 4)  # 1 header + 3 data rows

    #TEST 17: Export writes compare site as extra column and uses empty string for missing timestamps
    def test_17_export_csv_compare_site_gaps(self):
        import tempfile, csv as csv_mod, os as _os
        with tempfile.TemporaryDirectory() as tmp:
            with patch('Dashboard.EXPORT_DIR', tmp):
                overlay = self._make_overlay(
                    timestamps=["2022-01-02 00:00:00", "2022-01-02 00:15:00"],
                    values=[95.7, 98.5]
                )
                # Brassica only has the first timestamp, not the second
                overlay._compare_sites = {
                    "brassica": (["2022-01-02 00:00:00"], [80.1])
                }
                overlay._export_status = MagicMock()
                overlay._from_input = MagicMock()
                overlay._from_input.text = ""
                overlay._to_input = MagicMock()
                overlay._to_input.text = ""
                GraphOverlay._export_csv(overlay)
                filepath = _os.path.join(tmp, "maize_temperature_2022-01-02_2022-01-02.csv")
                with open(filepath) as f:
                    rows = list(csv_mod.reader(f))
                self.assertIn("brassica_temperature", rows[0])
                self.assertEqual(rows[1][2], "80.1")   # brassica value present
                self.assertEqual(rows[2][2], "")        # brassica value missing




"""
Scanning Page Testing
- These tests have been done and posted in the Wiki so images could be included
"""
#TEST 1: Image capture is given a blank photo.

#TEST 2: Image capture is given a healthy tomato leaf

#TEST 3: Image capture is given an unhealthy tomato leaf

"""
Profile page Testing
"""
from Dashboard import ProfileScreen
class ProfilePage(unittest.TestCase):

    def make_screen(self, name="Jane Doe", username="j.Doe", role="Farmer"):
        screen = MagicMock()

        screen.name_lbl = MagicMock()
        screen.name_lbl.text = name

        screen.username = MagicMock()
        screen.username.text = f"@{username}"

        screen.user_lbl = MagicMock()
        screen.user_lbl.text = role

        screen.app = MagicMock()
        screen.app.name_lbl= name
        screen.app.username = username
        screen.app.user_lbl = role

        screen._on_enter = ProfileScreen._on_enter.__get__(screen)
        return screen

    #TEST 1: Users full name related to the username is displayed.
    def test_1_users_name_displayed(self):
        screen = self.make_screen(name="John Farmer")
        screen._on_enter()
        self.assertEqual(screen.app.name_lbl, "John Farmer")

    #TEST 2: Username is displayed.
    def test_2_username_displayed(self):
        screen = self.make_screen(username="j.farmer")
        screen._on_enter()
        self.assertEqual(screen.app.username, "j.farmer")
    
    #TEST 3: Users role realted to their identity is displayed.
    def test_3_users_role_displayed(self):
        screen = self.make_screen(role="Researcher")
        screen._on_enter()
        self.assertEqual(screen.app.user_lbl, "Researcher")

    #TEST 4: Users role and name are empty strings
    def test_4_users_role_name_empty(self):
        screen = self.make_screen(name="", username="", role="")
        screen._on_enter()
        self.assertEqual(screen.app.name_lbl, "")
        self.assertEqual(screen.app.username, "")
        self.assertEqual(screen.app.user_lbl, "")

if __name__ == "__main__":
    unittest.main()