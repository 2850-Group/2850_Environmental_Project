
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import (
    Color, Rectangle, RoundedRectangle, Line, Ellipse,
    Canvas, Triangle
)
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty, StringProperty, NumericProperty, ListProperty
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.animation import Animation
from datetime import datetime
import random
import math

#Colour Palette
BG         = (0.06, 0.07, 0.10, 1)      # near-black page bg
CARD_BG    = (0.11, 0.13, 0.18, 1)      # card bg
SURFACE2   = (0.15, 0.18, 0.24, 1)      # slightly lighter surface
ACCENT     = (0.22, 0.60, 0.95, 1)      # blue accent
ACCENT2    = (0.15, 0.82, 0.68, 1)      # teal
UP_CLR     = (0.20, 0.85, 0.50, 1)      # green = rising
DOWN_CLR   = (0.95, 0.35, 0.35, 1)      # red = falling
NEUTRAL    = (0.85, 0.85, 0.85, 1)      # neutral text
DIM        = (0.50, 0.55, 0.62, 1)      # secondary text
BAR_BG     = (0.08, 0.10, 0.14, 1)      # bottom bar bg
BORDER     = (0.20, 0.23, 0.30, 1)      # card border colour
ALERT_WARN = (1.00, 0.72, 0.20, 1)      # amber warning
ALERT_CRIT = (0.95, 0.30, 0.30, 1)      # red critical

# Screen order direcetion
SCREEN_ORDER = ["dashboard", "scan", "profile"]

def rgba(color):
    return color

class Card(BoxLayout):
    bg_color = ListProperty(list(CARD_BG))
    radius = NumericProperty(dp(12))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, bg_color = self._draw)
        Clock.schedule_once(self._draw)
    
    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self.radius])

class DataArrow(Widget):
    #Up or down arrow to indicate the position of current data compared to overall trends
    direction = StringProperty("up")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, direction = self._draw)
        Clock.schedule_once(self._draw)
        
    def _draw (self, *_):
        self.canvas.clear()
        width, height = self.size
        nx, ny = self.x + width / 2, self.y + height / 2
        awidth = min(width, height) * 0.55
        aheight = min(width, height) * 0.65
        clr = UP_CLR if self.direction == "up" else DOWN_CLR
        with self.canvas:
            Color(*clr)
            if self.direction == "up":
                #Triangle pointing up
                Triangle(points=[
                    nx - awidth /2, ny - aheight /4,
                    nx + awidth /2, ny + aheight/4,
                    nx,             ny + aheight/2,
                ])
            else:
                #Triangle pointing down
                Triangle(points=[
                    nx - awidth / 2, ny + aheight / 4,
                    nx + awidth / 2, ny + aheight / 4,
                    nx,              ny - aheight / 2,
                ])

class DataCard(Card):
    def __init__(self, title, value, unit, direction, delta, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", [dp(10), dp(8)])
        kwargs.setdefault("spacing", dp(2))
        super().__init__(**kwargs)

        # Title
        lbl = Label(text=title, font_size=sp(11), color=DIM,
                    halign="center", valign="middle", size_hint_y=0.22)
        lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.add_widget(lbl)

        # Value
        row = FloatLayout(size_hint_y=0.45)
        val = Label(text=f"{value}", font_size=sp(22), color=NEUTRAL,
                    bold=True, halign="center", valign="middle",
                    size_hint=(1, 1), pos_hint={"x": 0, "y": -0.1})
        val.bind(size=lambda w, s: setattr(w, 'text_size', s))
        arrow = DataArrow(direction=direction,
                          size_hint=(None, None), size=(dp(24), dp(24)),
                          pos_hint={"right": 1, "center_y": 0.5})
        row.add_widget(val)
        row.add_widget(arrow)
        self.add_widget(row)
        
        # Unit + delta
        bottom = BoxLayout(size_hint_y=0.33, spacing=dp(6))
        delta_clr = UP_CLR if direction == "up" else DOWN_CLR
        unit_lbl = Label(text=unit, font_size=sp(10), color=DIM,
                         halign="center", valign="middle", size_hint_x=0.5)
        unit_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        delta_lbl = Label(text=delta, font_size=sp(10), color=delta_clr,
                          halign="center", valign="middle", size_hint_x=0.5)
        delta_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        bottom.add_widget(unit_lbl)
        bottom.add_widget(delta_lbl)
        self.add_widget(bottom)
#class ExpandableDataCard(BoxLayout):

#class LocationMap(Widget):
    #location map drawn with canvas

#class ExpandableLocationMap(BoxLayout):
    

#Alert Panel

SAMPLE_ALERTS = [
    {"level": "critical", "title": "Plant dying",
     "summary": "Water at 97%",
     "detail": "The plant is definitely dying"},
    {"level": "warning",  "title": "Pressure",
     "summary": "Water pressure crashing",
     "detail": "Tidal waves incoming"}
]
class AlertRow(BoxLayout):
    expanded = BooleanProperty(False)
 
    COLLAPSED_H = dp(52)
    EXPANDED_H  = dp(110)
 
    def __init__(self, alert, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
        self.alert = alert
        self.height = self.COLLAPSED_H
 
        clr = ALERT_CRIT if alert["level"] == "critical" else ALERT_WARN
 
        # Summary row
        row = BoxLayout(size_hint_y=None, height=self.COLLAPSED_H,
                        padding=[dp(12), 0], spacing=dp(10))
 
        # Colour dot
        dot = Widget(size_hint=(None, None), size=(dp(8), dp(8)))
        with dot.canvas:
            Color(*clr)
            Ellipse(pos=dot.pos, size=dot.size)
        dot.bind(pos=lambda w, p: w.canvas.clear() or
                 self._redraw_dot(w, p, clr))
        row.add_widget(dot)
 
        text_col = BoxLayout(orientation="vertical", spacing=dp(2))
        text_col.add_widget(Label(
            text=alert["title"], font_size=sp(12),
            color=NEUTRAL, bold=True, halign="left",
            text_size=(None, None)
        ))
        text_col.add_widget(Label(
            text=alert["summary"], font_size=sp(10),
            color=DIM, halign="left", text_size=(None, None)
        ))
        row.add_widget(text_col)
 
        self._chevron = Label(text="›", font_size=sp(20),
                              color=DIM, size_hint_x=None,
                              width=dp(24))
        row.add_widget(self._chevron)
        row.bind(on_touch_down=self._on_touch)
        self.add_widget(row)
 
        # Detail section
        self._detail = Label(
            text=alert["detail"], font_size=sp(11),
            color=DIM, halign="left", valign="top",
            text_size=(None, None),
            size_hint_y=None, height=0, opacity=0,
            padding=(dp(12), dp(4))
        )
        self.add_widget(self._detail)
 
        # Bottom separator
        sep = Widget(size_hint_y=None, height=dp(1))
        with sep.canvas:
            Color(*BORDER)
            rect = Rectangle(pos=sep.pos, size=sep.size)
        sep.bind(pos=lambda w, p: setattr(rect, 'pos', p),
                 size=lambda w, s: setattr(rect, 'size', s))
        self.add_widget(sep)
 
    def _redraw_dot(self, w, pos, clr):
        with w.canvas:
            Color(*clr)
            Ellipse(pos=pos, size=w.size)
 
    def _on_touch(self, widget, touch):
        if widget.collide_point(*touch.pos):
            self.toggle()
            return True
 
    def toggle(self):
        self.expanded = not self.expanded
        target_h = self.EXPANDED_H if self.expanded else self.COLLAPSED_H
        detail_h = (self.EXPANDED_H - self.COLLAPSED_H - dp(1)) \
                   if self.expanded else 0
        self._chevron.text = "▾" if self.expanded else "›"
        anim = Animation(height=target_h, duration=0.22, t="out_cubic")
        anim.start(self)
        anim2 = Animation(height=detail_h, opacity=int(self.expanded),
                          duration=0.22, t="out_cubic")
        anim2.start(self._detail)
 
 
class AlertsPanel(BoxLayout):
    expanded = BooleanProperty(True)
 
    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
 
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(44),
                           padding=[dp(14), 0])
        with header.canvas.before:
            Color(*SURFACE2)
            self._hdr_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self._upd_hdr, size=self._upd_hdr)
 
        badge = Label(
            text=f"  {len(SAMPLE_ALERTS)} Alerts",
            font_size=sp(13), color=NEUTRAL, bold=True,
            halign="left", size_hint_x=0.65
        )
        header.add_widget(badge)
        self._toggle_lbl = Label(
            text="Collapse ▲", font_size=sp(11),
            color=ACCENT, halign="right", size_hint_x=0.35
        )
        header.add_widget(self._toggle_lbl)
        header.bind(on_touch_down=self._on_touch)
        self.add_widget(header)
 
        with self.canvas.before:
            Color(*CARD_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd_bg, size=self._upd_bg)
 
        # Alert rows
        self._rows_box = BoxLayout(orientation="vertical",
                                   size_hint_y=None)
        self._rows_box.bind(minimum_height=self._rows_box.setter('height'))
        self._alert_rows = []
        for alert in SAMPLE_ALERTS:
            row = AlertRow(alert)
            self._alert_rows.append(row)
            self._rows_box.add_widget(row)
        self.add_widget(self._rows_box)
        self._update_height()
        self._rows_box.bind(height=lambda *_: self._update_height())
 
    def _upd_hdr(self, w, *_):
        self._hdr_rect.pos  = w.pos
        self._hdr_rect.size = w.size
 
    def _upd_bg(self, w, *_):
        self._bg.pos  = w.pos
        self._bg.size = w.size
 
    def _on_touch(self, widget, touch):
        if widget.collide_point(*touch.pos):
            self.toggle()
            return True
 
    def _update_height(self):
        rows_h = self._rows_box.height if self.expanded else 0
        self.height = dp(44) + rows_h
 
    def toggle(self):
        self.expanded = not self.expanded
        self._toggle_lbl.text = "Collapse ▲" if self.expanded else "Expand ▼"
        if self.expanded:
            self._rows_box.opacity = 1
            self._update_height()
        else:
            self._rows_box.opacity = 0
            self.height = dp(44)
 
 
#Bottom Navigation Bar
class NavBar(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(62))
        kwargs.setdefault("spacing", 0)
        super().__init__(**kwargs)
        self.sm = screen_manager
 
        with self.canvas.before:
            Color(*BAR_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(*BORDER)
            self._border = Rectangle(pos=self.pos,
                                     size=(self.width, dp(1)))
        self.bind(pos=self._upd, size=self._upd)
 
        self._btns = {}
        items = [
            ("dashboard", "⊞", "Dashboard"),
            ("scan", "◎", "Scan"),
            ("profile", "⚇", "Profile"),
        ]
        for name, icon, label in items:
            btn = self._make_btn(name, icon, label)
            self._btns[name] = btn
            self.add_widget(btn)
 
        self._set_active("dashboard")
 
    def _upd(self, w, *_):
        self._bg.pos  = w.pos
        self._bg.size = w.size
        self._border.pos  = w.pos
        self._border.size = (w.width, dp(1))
 
    def _make_btn(self, name, icon, label):
        btn = BoxLayout(orientation="vertical", spacing=dp(2),
                        padding=[0,dp(8)])
        btn.name = name
        btn._icon_lbl  = Label(text=icon, font_size=sp(20),
                               color=DIM, size_hint_y=0.55)
        btn._text_lbl  = Label(text=label, font_size=sp(9),
                               color=DIM, size_hint_y=0.45)
        btn.add_widget(btn._icon_lbl)
        btn.add_widget(btn._text_lbl)
        btn.bind(on_touch_down=lambda w, t: self._nav(w, t))
        return btn
 

    def _nav(self, widget, touch):
        if widget.collide_point(*touch.pos):
            current = self.sm.current
            target = widget.name
            ci = SCREEN_ORDER.index(current) if current in SCREEN_ORDER else 0
            ti = SCREEN_ORDER.index(target) if target in SCREEN_ORDER else 0
            direction = "left" if ti > ci else "right"
            self.sm.transition = SlideTransition(direction=direction, duration=0.25)
            self._set_active(target)
            self.sm.current = target
            return True
 
    def _set_active(self, name):
        for n, btn in self._btns.items():
            if n == name:
                btn._icon_lbl.color = ACCENT
                btn._text_lbl.color = ACCENT
            else:
                btn._icon_lbl.color = DIM
                btn._text_lbl.color = DIM


# Screens
def make_bg(widget):
    with widget.canvas.before:
        Color(*BG)
        rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda w, p: setattr(rect, 'pos', p),
                size=lambda w, s: setattr(rect, 'size', s))
 
 
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        make_bg(self)
 
        root = BoxLayout(orientation="vertical")
 
        # Scrollable Body
        scroll = ScrollView(size_hint=(1, 1),
                            do_scroll_x=False, do_scroll_y=True)
        body = BoxLayout(orientation="vertical",
                         size_hint_y=None, spacing=dp(10),
                         padding=[dp(12), dp(20), dp(12), dp(10)])
        body.bind(minimum_height=body.setter('height'))
 
        # 2 x 3 Data Cards
        grid = GridLayout(cols=2, rows=3, spacing=dp(10),
                        size_hint_y=None, height=dp(240))
        readings = [
            ("Temperature", "24.7", "°C",  "up",   "+1.2°"),
            ("Humidity",    "61",   "%",    "down", "−3%"),
            ("Pressure",    "1013", "hPa",  "up",   "+4 hPa"),
            ("Air Quality", "42",   "AQI",  "down", "−8"),
            ("Soil Quality", "23.4", "N/a", "down", "−2.0")
        ]
        for title, val, unit, direction, delta in readings:
            card = DataCard(title, val, unit, direction, delta,
                               bg_color=list(CARD_BG))
            grid.add_widget(card)
        body.add_widget(grid)
 
        # Expandable Location Map
        #locationmap = ExpandableLocationMap(size_hint_x=1)
        #body.add_widget(locationmap)
 
        # Alerts Panel
        alerts = AlertsPanel(size_hint_x=1)
        body.add_widget(alerts)
 
        # Spacer so last card isn't cut off by nav bar
        body.add_widget(Widget(size_hint_y=None, height=dp(10)))
 
        scroll.add_widget(body)
        root.add_widget(scroll)
        self.add_widget(root)
 
 
class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        make_bg(self)
        layout = BoxLayout(orientation="vertical",
                           padding=dp(24), spacing=dp(20))
 
        layout.add_widget(Label(
            text="Scan", font_size=sp(22), color=NEUTRAL,
            bold=True, size_hint_y=None, height=dp(40)
        ))
 
        # Fake viewfinder
        vf = Widget(size_hint=(1, 0.55))
        def draw_vf(*_):
            vf.canvas.clear()
            with vf.canvas:
                # Dark overlay
                Color(0, 0, 0, 0.6)
                Rectangle(pos=vf.pos, size=vf.size)
                # Corner brackets
                clr = ACCENT
                Color(*clr)
                m  = dp(40)
                bl = dp(24)
                lw = dp(3)
                corners = [
                    # bottom-left
                    (vf.x + m,      vf.y + m,
                     vf.x + m + bl, vf.y + m,
                     vf.x + m,      vf.y + m + bl),
                    # bottom-right
                    (vf.right - m,      vf.y + m,
                     vf.right - m - bl, vf.y + m,
                     vf.right - m,      vf.y + m + bl),
                    # top-left
                    (vf.x + m,      vf.top - m,
                     vf.x + m + bl, vf.top - m,
                     vf.x + m,      vf.top - m - bl),
                    # top-right
                    (vf.right - m,      vf.top - m,
                     vf.right - m - bl, vf.top - m,
                     vf.right - m,      vf.top - m - bl),
                ]
                for (x1,y1, x2,y2, x3,y3) in corners:
                    Line(points=[x1,y1, x2,y2], width=lw)
                    Line(points=[x1,y1, x3,y3], width=lw)
                # Scan line
                Color(*ACCENT2)
                Line(points=[vf.x + m, vf.center_y,
                             vf.right - m, vf.center_y], width=dp(1.5))
        vf.bind(pos=draw_vf, size=draw_vf)
        layout.add_widget(vf)
 
        layout.add_widget(Label(
            text="Point camera at QR code or device ID",
            font_size=sp(12), color=DIM, halign="center"
        ))
 
        scan_btn = Button(
            text="Start Scanning", font_size=sp(14),
            size_hint=(1, None), height=dp(48),
            background_color=(*ACCENT[:3], 1),
            color=NEUTRAL, bold=True
        )
        layout.add_widget(scan_btn)
        layout.add_widget(Widget())
        self.add_widget(layout)
 
 
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        make_bg(self)
        layout = BoxLayout(orientation="vertical",
                           padding=dp(24), spacing=dp(16))
 
        layout.add_widget(Label(
            text="Profile", font_size=sp(22), color=NEUTRAL,
            bold=True, size_hint_y=None, height=dp(40)
        ))
 
        # Avatar circle (drawn via canvas)
        av_box = BoxLayout(size_hint_y=None, height=dp(100))
        av = Widget(size_hint=(None, None), size=(dp(80), dp(80)))
        def draw_av(*_):
            av.canvas.clear()
            with av.canvas:
                Color(*ACCENT)
                Ellipse(pos=av.pos, size=av.size)
        av.bind(pos=draw_av, size=draw_av)
        av_box.add_widget(Widget())   # spacer
        av_box.add_widget(av)
        av_box.add_widget(Widget())
        layout.add_widget(av_box)
 
        layout.add_widget(Label(
            text="Alex Johnson", font_size=sp(18),
            color=NEUTRAL, bold=True, size_hint_y=None, height=dp(30)
        ))
        layout.add_widget(Label(
            text="alex.johnson@example.com", font_size=sp(12),
            color=DIM, size_hint_y=None, height=dp(24)
        ))
 
        # Info cards
        for (label, value) in [("Role", "Senior Engineer"),
                                ("Location", "Leeds, UK"),
                                ("Devices", "7 connected"),
                                ("Plan", "Pro")]:
            row = Card(orientation="horizontal",
                       bg_color=list(CARD_BG),
                       size_hint_y=None, height=dp(44),
                       padding=[dp(14), 0])
            row.add_widget(Label(text=label, font_size=sp(12),
                                 color=DIM, halign="left"))
            row.add_widget(Label(text=value, font_size=sp(12),
                                 color=NEUTRAL, halign="right"))
            layout.add_widget(row)
 
        layout.add_widget(Widget())
        self.add_widget(layout)
 
 
class DashboardHeader(BoxLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(56))
        kwargs.setdefault("padding", [dp(14), dp(6)])
        kwargs.setdefault("spacing", dp(10))
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*SURFACE2)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        title_box = BoxLayout(orientation="vertical")
        ov = Label(text="Overview", font_size=sp(14),
                   color=NEUTRAL, bold=True, halign="left", valign="bottom")
        ov.bind(size=lambda w, s: setattr(w, 'text_size', s))
        today = datetime.now().strftime("%A, %d %B %Y")
        dt = Label(text=today, font_size=sp(9),
                   color=DIM, halign="left", valign="top")
        dt.bind(size=lambda w, s: setattr(w, 'text_size', s))
        title_box.add_widget(ov)
        title_box.add_widget(dt)
        self.add_widget(title_box)

    def _upd(self, w, *_):
        self._bg.pos  = w.pos
        self._bg.size = w.size

# App Root
class DashboardApp(App):
    def build(self):
        self.title = "Dashboard"

        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(ScanScreen(name="scan"))
        sm.add_widget(ProfileScreen(name="profile"))

        nav = NavBar(screen_manager=sm)
        header = DashboardHeader()

        root = BoxLayout(orientation="vertical")
        root.add_widget(header)
        root.add_widget(sm)
        root.add_widget(nav)
        return root


if __name__ == "__main__":
    DashboardApp().run()