import unittest
import os
import time
from kivy.clock import Clock
from kivy.tests.common import GraphicUnitTest
from Dashboard import DashboardApp, SignInPanel
from kivy.core.window import Window
from kivy.input.providers.mouse import MouseMotionEvent

class TestEnvironmentalApp(GraphicUnitTest):
    @classmethod
    def setUpClass(cls):
        # Prevent the app from timing out or hanging on hardware
        os.environ['KIVY_USE_DEFAULT_CONFIG'] = '1'

    def test_login_panel_validation(self):
        """Test if the sign-in panel correctly identifies empty fields."""
        app = DashboardApp()
        # We manually build the panel to test its internal logic
        panel = SignInPanel(switch_cb=lambda x: None, success_cb=lambda x: None)
        
        # Simulate empty login attempt
        panel.username._input.text = ""
        panel.password._input.text = ""
        panel._on_sign_in()
        
        # Verify the error message appeared
        self.assertEqual(panel._error.text, "Please enter your username and password")
        self.assertGreater(panel._error.opacity, 0)


    def test_navigation_bar_switching(self):
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

    def test_theme_colors(self):
        """Ensure the global theme constants are correctly applied."""
        from Dashboard import ACCENT
        # Check that the green accent color is correct (approximate float match)
        self.assertAlmostEqual(ACCENT[0], 0.267, places=2)
        self.assertAlmostEqual(ACCENT[1], 1.000, places=2)

if __name__ == '__main__':
    unittest.main()