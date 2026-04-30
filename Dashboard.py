'''Requirements:
pip install kivy
pip install bcrypt
pip install opencv-python'''


from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import (
    Color, Rectangle, RoundedRectangle, Line, Ellipse,
    Canvas, Triangle, InstructionGroup
)
from kivy.uix.camera import Camera
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty, StringProperty, NumericProperty, ListProperty
)
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.animation import Animation
from Code.Database.Queries.sign_in import sign_in_query
from Code.Database.Queries.sign_in import sign_up_query
import sqlite3
import bcrypt
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Code"))
from Code.bridge import Bridge
from datetime import datetime
import random
import math

DB_PATH = os.path.join(os.path.dirname(__file__), "Code", "Database", "Queries", "pest_control.db")
os.environ['KIVY_CAMERA'] = 'opencv'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

#Colour Palette
BG         = (0.06, 0.07, 0.10, 1)      # near-black page bg 
CARD_BG    = (0.11, 0.13, 0.18, 1)      # card bg
SURFACE2   = (0.15, 0.18, 0.24, 1)      # slightly lighter surface
ACCENT     = (0.22, 0.60, 0.95, 1)      # blue accent
ACCENT2    = (0.15, 0.82, 0.68, 1)      # teal
UP_CLR     = (0.20, 0.85, 0.50, 1)      # green = rising
DOWN_CLR   = (1.00, 0.55, 0.55, 1)      # red = falling
NEUTRAL    = (0.95, 0.95, 0.95, 1)      # neutral text
DIM        = (0.66, 0.70, 0.76, 1)      # secondary text
BAR_BG     = (0.08, 0.10, 0.14, 1)      # bottom bar bg
BORDER     = (0.20, 0.23, 0.30, 1)      # card border colour
ALERT_WARN = (1.00, 0.72, 0.20, 1)      # amber warning
ALERT_CRIT = (1.00, 0.50, 0.50, 1)      # red critical

# Screen order direcetion
SCREEN_ORDER = ["dashboard", "scan", "profile"]

def rgba(color):
    return color

def  make_label(text, font_size=18, color = NEUTRAL, bold = False, halign='left', height = dp(24)):
    label = Label(
        text = text,
        font_size = font_size,
        color = color,
        bold = bold,
        halign = halign, 
        valign = "middle",
        size_hint_y = None,
        height = height
    )
    label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
    return label

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
        self.bind(pos=self._draw, size=self._draw, direction=self._draw)
        Clock.schedule_once(self._draw)

    def _draw(self, *_):
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
                    nx - awidth / 2, ny - aheight / 4,
                    nx + awidth / 2, ny - aheight / 4,
                    nx,              ny + aheight / 2,
                ])
            else:
                #Triangle pointing down
                Triangle(points=[
                    nx - awidth / 2, ny + aheight / 4,
                    nx + awidth / 2, ny + aheight / 4,
                    nx,              ny - aheight / 2,
                ])

class RoundedCard(FloatLayout):
    """Rounded card widget"""

    def __init__(self, bg_color=CARD_BG, radius=dp(14), border_color=BORDER, **kwargs):
        super().__init__(**kwargs)
        self._bg = bg_color
        self._radius = radius
        self._border = border_color
        self.bind(pos = self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self._radius])
            Color(*self._border)
            Line(rounded_rectangle=[*self.pos, *self.size, self._radius],
                 width=1.2)
            
class ErrorLabel(Label):
    """Inline error message"""
    def __init__(self, **kwargs):
        super().__init__(
            text = '', font_size = sp(12), color = ALERT_CRIT,
            halign='left', valign='middle',
            size_hint=(1, None), height =0, opacity=0
        )
        self.bind(size = lambda w, s:setattr(w, 'text_size',s))
    
    def show(self, message):
        self.text = message
        self.height = dp(20)
        self.opacity = 1
    
    def hide(self):
        self.text = ''
        self.height = 0
        self.opacity = 0
            
class Input(TextInput):
    """Single line styled text input"""

    def __init__(self, hint='', password=False, **kwargs):

        passed_font_size = kwargs.pop('font_size', 22)
        super().__init__(
            hint_text=hint,
            password=password,
            multiline=False,
            background_normal="",
            background_active="",
            background_color=SURFACE2,
            foreground_color=NEUTRAL,
            hint_text_color=DIM,
            cursor_color=ACCENT,
            font_size=passed_font_size,
            padding = [dp(8), dp(10), dp(8), 0],
            size_hint=(1, None),
            height=dp(44),
            **kwargs,
        )

class InputField(BoxLayout):
    """Wrapper that draws the rounded border around an Input."""
    def __init__(self, hint='', password=False, font_size='18sp', **kwargs):
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(44))
        super().__init__(**kwargs)

        self._input = Input(hint=hint, password=password, font_size = font_size)
        self._input.bind(focus=self._on_focus)
        self.add_widget(self._input)

        self._border_group = InstructionGroup()
        self.canvas.after.add(self._border_group)
        self.bind(pos=self._redraw, size=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw())

    def _redraw(self, *_):
        self._border_group.clear()
        self._border_group.add(
            Color(*(ACCENT if self._input.focus else BORDER))
        )
        self._border_group.add(
            Line(rounded_rectangle=[*self.pos, *self.size, dp(8)], width=1.2)
        )

    def _on_focus(self, inst, focused):
        self._redraw()

    # Proxy .text so the panels can still do self.username.text
    @property
    def text(self):
        return self._input.text


class SignInButton(Button):
    """Blue sign in button"""
    def __init__(self, text="Sign In", **kwargs):
        super().__init__(
            text=text,
            background_color=CARD_BG,
            color=NEUTRAL,
            bold=True,
            font_size=30,
            size_hint=(1, None),
            height=dp(48),
            **kwargs,
        )
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*CARD_BG)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(8)])
            Color(*BORDER)
            Line(rounded_rectangle=[*self.pos, *self.size, dp(8)],
                 width=1.2)
            
    def on_press(self):
        self.color = ACCENT2
        with self.canvas.before:
            Color(*CARD_BG)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
            Color(*ACCENT2)
            Line(rounded_rectangle=[*self.pos, *self.size, dp(8)], width = 1.5)
    
    def on_release(self):
        self.color=DIM
        self._draw()

class SignUpButton(Button):
    def __init__(self, text="Sign Up", **kwargs):
        super().__init__(
            text=text,
            background_color=CARD_BG,
            color=NEUTRAL,
            bold=True,
            font_size=30,
            size_hint=(1, None),
            height=dp(48),
            **kwargs,
        )
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*CARD_BG)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(8)])
            Color(*BORDER)
            Line(rounded_rectangle=[*self.pos, *self.size, dp(8)],
                 width=1.2)
            
    def on_press(self):
        self.color = ACCENT2
        with self.canvas.before:
            Color(*CARD_BG)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
            Color(*ACCENT2)
            Line(rounded_rectangle=[*self.pos, *self.size, dp(8)], width = 1.5)

    def on_release(self):
        self.color=DIM
        self._draw()

class Divider(BoxLayout):
    """Line divided sign in and sign up buttons"""  
    def __init__(self, text='or', **kwargs):
        super().__init__(orientation='horizontal', size_hint=(1, None),
                         height=dp(24), spacing=dp(8), **kwargs)      
        for _ in range(2):
            line_holder = Widget(size_hint=(1, None), height=dp(1))
            line_holder.bind(pos=lambda w, *_: self._draw_line(w),
                             size=lambda w, *_: self._draw_line(w))
            self._line_holders = getattr(self, '_line_holders', [])
            self._line_holders.append(line_holder)
        label = make_label(text, font_size=20, color=BORDER, halign="center", height=dp(24))
        label.width=dp(30)

        self.add_widget(self._line_holders[0])
        self.add_widget(label)
        self.add_widget(self._line_holders[1])
    
    def _draw_line(self, widget):
        widget.canvas.before.clear()
        with widget.canvas:
            Color(*BORDER)
            Line(points=[widget.x, widget.center_y, widget.right, widget.center_y],
                 width=1)
            
class SignInHeader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', size_hint=(1, None),
                         height=dp(60), spacing=dp(10), **kwargs)

        name_box = BoxLayout(orientation='horizontal', spacing=0)
        name_box.add_widget(make_label('Application Name', font_size=32, color=NEUTRAL,
                                       bold=True,
                                       height=dp(40)))
        name_box.add_widget(Widget())
        self.add_widget(name_box)

class SignInPanel(BoxLayout):
    def __init__(self, switch_cb, success_cb, **kwargs):
        super().__init__(orientation = "vertical", spacing=dp(12), **kwargs)
        self.switch_cb = switch_cb
        self.success_cb = success_cb
        self._build()

    def _build(self):
        self.add_widget(make_label('Welcome', font_size=50,
                                   color=NEUTRAL, bold=True, height=dp(30)))
        self.add_widget(make_label('Sign in to your environmental dashboard',
                                   font_size=45, color=DIM, height=dp(22)))
        self.add_widget(Widget(size_hint=(1, None), height=dp(6)))
 
        self.add_widget(make_label('USERNAME', font_size=35, color=DIM,
                                   height=dp(18)))
        self.username = InputField(hint='e.g. j.farmer')
        self.add_widget(self.username)
 
        self.add_widget(make_label('PASSWORD', font_size=35, color=DIM,
                                   height=dp(18)))
        self.password = InputField(hint='••••••••', password=True)
        self.add_widget(self.password)

        self._error = ErrorLabel()
        self.add_widget(self._error)
 
        self.add_widget(Widget(size_hint=(1, None), height=dp(4)))
 
        sign_in = SignInButton(text='Sign in')
        sign_in.bind(on_release=self._on_sign_in)
        self.add_widget(sign_in)
 
        self.add_widget(Divider())
 
        signup_btn = SignUpButton(text='Create an account')
        signup_btn.bind(on_release=lambda *_: self.switch_cb('signup'))
        self.add_widget(signup_btn)
 
        self.add_widget(Widget())
    
    def _on_sign_in(self, *_):
        user = self.username.text.strip()
        pwd = self.password.text.strip()

        if not user or not pwd:
            self._error.show("Please enter your username and password")
            return

        role = sign_in_query(conn, cursor, user, pwd)
        if role:
            self._error.hide()
            self.success_cb(role)
        else:
            self._error.show("Incorrect username or password.")

class SignUpPanel(BoxLayout):
    def __init__(self, switch_cb, success_cb, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(12),
                         size_hint=(1, 1), **kwargs)
        self.switch_cb = switch_cb
        self.success_cb = success_cb
        self._selected_role = "Farmer" # default selected role
        self._build()

    def _build(self):
        self.add_widget(make_label('Start monitoring your crops today',
                                   font_size=24, color=DIM, height=dp(22)))
        self.add_widget(Widget(size_hint=(1, None), height=dp(6)))
 
        self.add_widget(make_label('FULL NAME', font_size=20, color=DIM,
                                   height=dp(18)))
        self.fullname = InputField(hint='e.g. John Farmer')
        self.add_widget(self.fullname)
 
        self.add_widget(make_label('USERNAME', font_size=20, color=DIM,
                                   height=dp(18)))
        self.username = InputField(hint='e.g. j.farmer')
        self.add_widget(self.username)
 
        self.add_widget(make_label('PASSWORD', font_size=20, color=DIM,
                                   height=dp(18)))
        self.password = InputField(hint='Min. 8 characters', password=True)
        self.add_widget(self.password)

        self.add_widget(make_label('I AM A', font_size=20, color=DIM, height=dp(18)))
        role_row = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint=(1, None), height=dp(40))
        self._farmer_btn = self._role_btn("Farmer")
        self._researcher_btn = self._role_btn("Researcher")
        role_row.add_widget(self._farmer_btn)
        role_row.add_widget(self._researcher_btn)
        self.add_widget(role_row)
        self._set_role("Farmer")

        self._error = ErrorLabel()
        self.add_widget(self._error)

        self.add_widget(Widget(size_hint=(1, None), height=dp(4)))

        sign_in = SignInButton(text='Sign Up')
        sign_in.bind(on_release=self._on_sign_up)
        self.add_widget(sign_in)

        self.add_widget(Divider())

        signup_btn = SignUpButton(text='Sign In Instead')
        signup_btn.bind(on_release=lambda *_: self.switch_cb('login'))
        self.add_widget(signup_btn)
 
        self.add_widget(Widget())
    
    def _role_btn(self, label):
        btn = Button(text=label, font_size=sp(13), bold=True, size_hint=(1, 1), background_normal='', background_color=(0, 0, 0, 0))
        btn.bind(on_release=lambda *_: self._set_role(label))
        btn.bind(pos=self._draw_role_btn, size=self._draw_role_btn)
        return btn

    def _draw_role_btn(self, btn, *_):
        btn.canvas.before.clear()
        with btn.canvas.before:
            if self._selected_role == btn.text:
                Color(*ACCENT)
                btn.color = NEUTRAL
            else:
                Color(*CARD_BG)
                btn.color = DIM
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(6)])
            if self._selected_role != btn.text:
                Color(*BORDER)
                Line(rounded_rectangle=[btn.x, btn.y, btn.width, btn.height, dp(6)], width=1)

    def _set_role(self, role):
        self._selected_role = role
        self._draw_role_btn(self._farmer_btn)
        self._draw_role_btn(self._researcher_btn)

    def _on_sign_up(self, *_):
        name = self.fullname.text.strip()
        user = self.username.text.strip()
        pwd = self.password.text.strip()

        if not name or not user or not pwd:
            self._error.show("All fields are required")
            return
        if len(pwd) < 8:
            self._error.show("Password must be longer than 8 characters")
            return

        success = sign_up_query(conn, cursor, name, user, pwd, name, self._selected_role)
        if success:
            self._error.hide()
            self.success_cb(self._selected_role)
        else:
            self._error.show("Username is taken. Please choose another.")
        


class DataCard(Card):
    def __init__(self, title, value, unit, direction, delta, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", [dp(12), dp(10)])
        kwargs.setdefault("spacing", dp(4))
        super().__init__(**kwargs)

        self.tap_callback = None
        self._direction = direction
        self._bar_color = UP_CLR if direction == "up" else DOWN_CLR
        self._unit = unit

        self.bind(pos=self._draw_top_bar, size=self._draw_top_bar, bg_color=self._draw_top_bar)
        Clock.schedule_once(self._draw_top_bar)

        # Title
        title_lbl = Label(
            text=title.upper(), font_size=sp(10), color=DIM,
            halign="left", valign="middle",
            size_hint_y=None, height=dp(18)
        )
        title_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.add_widget(title_lbl)

        # Value row — value+unit in markup, arrow right
        val_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=1,
            spacing=dp(4)
        )

        val = Label(
            text=self._fmt(value), font_size=sp(28), color=NEUTRAL,
            bold=True, halign="left", valign="middle",
            size_hint=(1, 1), markup=True
        )
        val.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self._value_lbl = val

        arrow = DataArrow(
            direction=direction,
            size_hint=(None, None), size=(dp(20), dp(20)),
            pos_hint={"center_y": 0.5}
        )
        self._arrow = arrow

        val_row.add_widget(val)
        val_row.add_widget(arrow)
        self.add_widget(val_row)

        # Delta row
        delta_clr = UP_CLR if direction == "up" else DOWN_CLR
        delta_lbl = Label(
            text=delta, font_size=sp(10), color=delta_clr,
            halign="right", valign="middle",
            size_hint_y=None, height=dp(18)
        )
        delta_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self._delta_lbl = delta_lbl
        self.add_widget(delta_lbl)

    def _fmt(self, value):
        if self._unit:
            return f"{value}[size={int(sp(13))}] {self._unit}[/size]"
        return f"{value}"

    def _draw_top_bar(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            Color(*self._bar_color)
            Rectangle(
                pos=(self.x + self.radius, self.top - dp(3)),
                size=(self.width - self.radius * 2, dp(3))
            )
            Color(*BORDER)
            Line(rounded_rectangle=[*self.pos, *self.size, self.radius], width=1.0)

    def update(self, value, direction, delta):
        self._direction = direction
        self._bar_color = UP_CLR if direction == "up" else DOWN_CLR
        self._draw_top_bar()
        self._value_lbl.text  = self._fmt(value)
        self._arrow.direction = direction
        self._delta_lbl.text  = delta
        self._delta_lbl.color = UP_CLR if direction == "up" else DOWN_CLR

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.ud[f"card_hit_{id(self)}"] = True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.ud.get(f"card_hit_{id(self)}"):
            if self.tap_callback:
                self.tap_callback()
            return True
        return super().on_touch_up(touch)
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
        dot_wrap = BoxLayout(size_hint=(None, None), size=(dp(20), dp(52)))
        dot = Widget(size_hint=(None, None), size=(dp(10), dp(10)),
                     pos_hint={"center_x": 0.5, "center_y": 0.5})
        with dot.canvas:
            Color(*clr)
            Ellipse(pos=dot.pos, size=dot.size)
        dot.bind(pos=lambda w, p: (w.canvas.clear(), self._redraw_dot(w, p, clr)))
        dot_wrap.add_widget(dot)
        row.add_widget(dot_wrap)

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
            self._hdr_rect = RoundedRectangle(pos=header.pos, size=header.size)
        header.bind(pos=self._upd_hdr, size=self._upd_hdr)

        self._badge = Label(
            text=f"  {len(SAMPLE_ALERTS)} Alerts",
            font_size=sp(13), color=NEUTRAL, bold=True,
            halign="left", size_hint_x=0.65
        )
        header.add_widget(self._badge)
        self._toggle_lbl = Label(
            text="Collapse ▲", font_size=sp(11),
            color=ACCENT, halign="right", size_hint_x=0.35
        )
        header.add_widget(self._toggle_lbl)
        header.bind(on_touch_down=self._on_touch)
        self.add_widget(header)

        with self.canvas.before:
            Color(*CARD_BG)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
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

    def update_alerts(self, alert_dicts):
        self._rows_box.clear_widgets()
        self._alert_rows = []
        for alert in alert_dicts:
            row = AlertRow(alert)
            self._alert_rows.append(row)
            self._rows_box.add_widget(row)
        self._badge.text = f"  {len(alert_dicts)} Alerts"
        self._update_height()


class GraphOverlay(FloatLayout):
    """
    Full-screen modal overlay that draws a line graph from historical data.

    Usage:
        overlay = GraphOverlay(
            title     = "Temperature",
            unit      = "°C",
            site      = "Maize",
            timestamps = [...],   # list of date strings
            values     = [...],   # list of floats
        )
        App.get_running_app().root.add_widget(overlay)

    Tapping the × button or outside the panel removes it.
    """

    # Rolling average window (number of data points)
    AVG_WINDOW = 20

    def __init__(self, title, unit, site, timestamps, values, **kwargs):
        # FloatLayout added to Window needs explicit size — size_hint doesn't work there
        kwargs.setdefault("size", Window.size)
        kwargs.setdefault("pos", (0, 0))
        super().__init__(**kwargs)

        self._title      = title
        self._unit       = unit
        self._site       = site
        self._timestamps = timestamps
        self._values     = values

        # Keep sized to window if it resizes
        Window.bind(size=lambda _, s: setattr(self, 'size', s))

        # ── dark scrim ────────────────────────────────────────────────
        scrim = Widget(size=self.size, pos=self.pos)
        with scrim.canvas:
            Color(0, 0, 0, 0.72)
            self._scrim_rect = Rectangle(pos=scrim.pos, size=scrim.size)
        self.bind(pos =lambda _, v: (setattr(scrim, 'pos',  v), setattr(self._scrim_rect, 'pos',  v)),
                  size=lambda _, v: (setattr(scrim, 'size', v), setattr(self._scrim_rect, 'size', v)))
        scrim.bind(on_touch_down=self._scrim_touch)
        self.add_widget(scrim)

        # ── panel card ────────────────────────────────────────────────
        pw = Window.width  * 0.94
        ph = Window.height * 0.72
        panel = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(pw, ph),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[dp(14), dp(12)],
            spacing=dp(8),
        )
        with panel.canvas.before:
            Color(*CARD_BG)
            self._panel_rect = RoundedRectangle(
                pos=panel.pos, size=panel.size, radius=[dp(16)])
        panel.bind(pos=self._upd_panel, size=self._upd_panel)

        # header row: title + close button
        hdr = BoxLayout(size_hint_y=None, height=dp(36))
        hdr.add_widget(Label(
            text=f"{title}  ·  {site.capitalize()}",
            font_size=sp(14), color=NEUTRAL, bold=True,
            halign="left", valign="middle",
        ))
        close_btn = Button(
            text="✕", font_size=sp(15), color=DIM,
            size_hint=(None, None), size=(dp(32), dp(32)),
            background_normal="", background_color=(0, 0, 0, 0),
        )
        close_btn.bind(on_release=lambda _: self._dismiss())
        hdr.add_widget(close_btn)
        panel.add_widget(hdr)

        # unit / range label
        self._info_lbl = Label(
            text="Loading…", font_size=sp(10), color=DIM,
            halign="left", valign="middle",
            size_hint_y=None, height=dp(18),
        )
        self._info_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        panel.add_widget(self._info_lbl)

        # graph canvas widget
        self._graph = Widget(size_hint=(1, 1))
        self._graph.bind(pos=self._draw_graph, size=self._draw_graph)
        panel.add_widget(self._graph)

        # legend row
        legend = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(16),
                           padding=[dp(4), 0])
        for clr, lbl_text in [(ACCENT, "Value"), (ACCENT2, f"{self.AVG_WINDOW}-pt avg")]:
            dot = Widget(size_hint=(None, 1), width=dp(12))
            with dot.canvas:
                Color(*clr)
                Ellipse(pos=(0, 0), size=(dp(8), dp(8)))
            dot.bind(pos=lambda w, p, c=clr: self._redraw_dot(w, p, c))
            legend.add_widget(dot)
            legend.add_widget(Label(
                text=lbl_text, font_size=sp(9), color=DIM,
                halign="left", size_hint_x=None, width=dp(70),
            ))
        legend.add_widget(Widget())   # spacer
        panel.add_widget(legend)

        self.add_widget(panel)

        # draw after two frames to ensure BoxLayout has distributed sizes
        Clock.schedule_once(self._draw_graph, 0.1)
        Clock.schedule_once(self._draw_graph, 0.3)

    # ── helpers ──────────────────────────────────────────────────────

    def _upd_panel(self, w, *_):
        self._panel_rect.pos  = w.pos
        self._panel_rect.size = w.size

    def _redraw_dot(self, w, pos, clr):
        w.canvas.clear()
        with w.canvas:
            Color(*clr)
            Ellipse(pos=(pos[0], pos[1] + dp(2)), size=(dp(8), dp(8)))

    def _scrim_touch(self, widget, touch):
        # dismiss if user taps the dark background (not the panel)
        self._dismiss()
        return True

    def _dismiss(self):
        Window.remove_widget(self)

    # ── rolling average ──────────────────────────────────────────────

    @staticmethod
    def _rolling_avg(values, window):
        out = []
        for i in range(len(values)):
            start = max(0, i - window + 1)
            chunk = values[start: i + 1]
            out.append(sum(chunk) / len(chunk))
        return out

    # ── graph drawing ────────────────────────────────────────────────

    def _draw_graph(self, *_):
        w = self._graph
        w.canvas.clear()

        # remove any old axis label widgets
        for child in list(w.children):
            w.remove_widget(child)

        values     = self._values
        timestamps = self._timestamps

        if not values:
            return

        v_min   = min(values)
        v_max   = max(values)
        v_range = v_max - v_min if v_max != v_min else 1.0

        # update info label regardless of size
        self._info_lbl.text = (
            f"{self._unit}  ·  min {v_min:.1f}  max {v_max:.1f}  ({len(values)} pts)"
        )

        if len(values) < 2:
            return

        # ── margins ──────────────────────────────────────────────────
        ml = dp(48)
        mr = dp(10)
        mt = dp(10)
        mb = dp(28)

        gx = w.x + ml
        gy = w.y + mb
        gw = w.width  - ml - mr
        gh = w.height - mb - mt

        if gw <= 0 or gh <= 0:
            return

        # ── value range ──────────────────────────────────────────────
        v_min = min(values)
        v_max = max(values)
        v_range = v_max - v_min if v_max != v_min else 1.0

        # update info label
        self._info_lbl.text = (
            f"{self._unit}  ·  min {v_min:.1f}  max {v_max:.1f}  "
            f"({len(values)} pts)"
        )

        def to_px(v):
            return gy + ((v - v_min) / v_range) * gh

        def to_x(i):
            return gx + (i / (len(values) - 1)) * gw

        # ── rolling average ──────────────────────────────────────────
        avg_values = self._rolling_avg(values, self.AVG_WINDOW)

        with w.canvas:

            # grid lines + Y labels (5 horizontal gridlines)
            N_GRID = 5
            for k in range(N_GRID + 1):
                frac  = k / N_GRID
                y_val = v_min + frac * v_range
                py    = gy + frac * gh

                # gridline
                Color(*BORDER)
                Line(points=[gx, py, gx + gw, py], width=dp(0.6))

                # Y label
                Color(*DIM)
                # We can't use Label in canvas so we'll skip text on canvas;
                # labels are placed via scheduled Label widgets below

            # X-axis baseline
            Color(*BORDER)
            Line(points=[gx, gy, gx + gw, gy], width=dp(0.8))

            # ── main value line ──────────────────────────────────────
            Color(*ACCENT)
            pts = []
            for i, v in enumerate(values):
                pts += [to_x(i), to_px(v)]
            Line(points=pts, width=dp(1.2))

            # ── rolling average line ─────────────────────────────────
            Color(*ACCENT2)
            avg_pts = []
            for i, v in enumerate(avg_values):
                avg_pts += [to_x(i), to_px(v)]
            Line(points=avg_pts, width=dp(1.5))

            # ── endpoint dot ─────────────────────────────────────────
            last_x = to_x(len(values) - 1)
            last_y = to_px(values[-1])
            Color(*ACCENT)
            Ellipse(pos=(last_x - dp(4), last_y - dp(4)),
                    size=(dp(8), dp(8)))

        # ── axis labels (via Label widgets added to graph widget) ────

        # Y labels
        N_GRID = 5
        for k in range(N_GRID + 1):
            frac  = k / N_GRID
            y_val = v_min + frac * v_range
            py    = gy + frac * gh
            lbl = Label(
                text=f"{y_val:.1f}",
                font_size=sp(8), color=DIM,
                size_hint=(None, None), size=(dp(42), dp(14)),
                halign="right", valign="middle",
            )
            lbl.text_size = lbl.size
            lbl.pos = (w.x + ml - dp(46), py - dp(7))
            w.add_widget(lbl)

        # X labels — show ~5 evenly-spaced date labels
        n = len(timestamps)
        x_indices = [int(i * (n - 1) / 4) for i in range(5)]
        for idx in x_indices:
            px = to_x(idx)
            # show Mon-YY format
            ts  = timestamps[idx]
            # ts is YYYY-MM-DD; show MM-YY
            parts = ts.split("-")
            short = f"{parts[1]}/{parts[0][2:]}" if len(parts) == 3 else ts
            lbl = Label(
                text=short,
                font_size=sp(7), color=DIM,
                size_hint=(None, None), size=(dp(36), dp(14)),
                halign="center", valign="top",
            )
            lbl.text_size = lbl.size
            lbl.pos = (px - dp(18), w.y + dp(2))
            w.add_widget(lbl)


class SiteSelectorBar(BoxLayout):
    """
    Horizontal pill-button bar for switching between the three monitoring sites.
    Call set_active(site_key) to highlight the chosen site.
    Fires on_select(site_key) when the user taps a button.
    """
    SITES = [
        ("maize",    "🌽  Maize"),
        ("brassica", "🥦  Brassica"),
        ("orchard",  "🍎  Orchard"),
    ]

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(44))
        kwargs.setdefault("spacing", dp(6))
        kwargs.setdefault("padding", [dp(12), dp(6)])
        super().__init__(**kwargs)

        self.on_select = None  # callback: fn(site_key)
        self._btns = {}

        with self.canvas.before:
            Color(*SURFACE2)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        for key, label in self.SITES:
            btn = Button(
                text=label,
                font_size=sp(11),
                size_hint_x=1,
                size_hint_y=1,
                background_normal="",
                background_color=(*CARD_BG[:3], 1),
                color=DIM,
                bold=False,
            )
            btn.site_key = key
            btn.bind(on_release=self._on_btn)
            self._btns[key] = btn
            self.add_widget(btn)

        self.set_active("maize")

    def _upd(self, w, *_):
        self._bg.pos  = w.pos
        self._bg.size = w.size

    def _on_btn(self, btn):
        if self.on_select:
            self.on_select(btn.site_key)
        self.set_active(btn.site_key)

    def set_active(self, site_key):
        for key, btn in self._btns.items():
            if key == site_key:
                btn.background_color = (*ACCENT[:3], 1)
                btn.color = (1, 1, 1, 1)
                btn.bold  = True
            else:
                btn.background_color = (*CARD_BG[:3], 1)
                btn.color = DIM
                btn.bold  = False


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
            ("scan",      "◎", "Scan"),
            ("profile",   "⚇", "Profile"),
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
                        padding=[0, dp(8)])
        btn.name = name
        btn._icon_lbl = Label(text=icon, font_size=sp(20),
                              color=DIM, size_hint_y=0.55)
        btn._text_lbl = Label(text=label, font_size=sp(9),
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
    
class SignInScreen(Screen):
    def __init__(self, on_authenticated, **kwargs):
        super().__init__(**kwargs)
        self._on_authenticated = on_authenticated
        root = FloatLayout()

        with root.canvas.before:
            Color(*BG)
            self._bg_rect = RoundedRectangle(pos = root.pos, size = root.size)

        root.bind(pos=lambda w, v: setattr(self._bg_rect, 'pos', v),
                  size=lambda w, v: setattr(self._bg_rect, 'size', v))
    
        card = RoundedCard(
            size = (0.9, 0.85),
            pos_hint = {"center_x": 0.5, "center_y": 0.5}
        )

        inner = BoxLayout(
            orientation='vertical',
            padding=[dp(28), dp(28)],
            spacing=dp(8),
            size_hint = (1,1),
        )

        card.bind(size = lambda w, s: setattr(inner, 'size', s),
                 pos = lambda w, p:setattr(inner, 'pos', p))

        inner.add_widget(SignInHeader())

        self.panel_holder = BoxLayout(orientation='vertical', size_hint = (1,1))
        self.current_panel = None
        self._show_panel('login')

        inner.add_widget(self.panel_holder)
        card.add_widget(inner)
        root.add_widget(card)
        self.add_widget(root)

    def _show_panel(self, name):
        self.panel_holder.clear_widgets()
        if name == 'login':
            panel = SignInPanel(switch_cb=self._show_panel, success_cb = self._on_authenticated)
        else:
            panel = SignUpPanel(switch_cb=self._show_panel, success_cb = self._on_authenticated)
        self.panel_holder.add_widget(panel)
        self._current_panel = name



class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        make_bg(self)

        # Active site key and latest data cache
        self._active_site = "maize"
        self._latest = {"maize": None, "brassica": None, "orchard": None}

        root = BoxLayout(orientation="vertical")

        # Site selector bar (sits above the scroll area)
        self._site_bar = SiteSelectorBar(size_hint_x=1)
        self._site_bar.on_select = self._on_site_selected
        root.add_widget(self._site_bar)

        # Scrollable Body
        scroll = ScrollView(size_hint=(1, 1),
                            do_scroll_x=False, do_scroll_y=True)
        body = BoxLayout(orientation="vertical",
                         size_hint_y=None, spacing=dp(10),
                         padding=[dp(12), dp(14), dp(12), dp(10)])
        body.bind(minimum_height=body.setter('height'))

        # 2 x 3 Data Cards — labels and units match bridge STAT_LABELS order:
        # [air_temp, humidity, leaf_wetness, light, vibration, pest_count]
        STAT_LABELS = ["Temperature", "Humidity", "Leaf Wetness", "Light", "Vibration", "Pest Count"]
        STAT_UNITS  = ["°C", "%", "", "lux", "", ""]

        self._grid = GridLayout(cols=2, rows=3, spacing=dp(12),
                                size_hint_y=None, height=dp(330))
        self._cards = []
        for i in range(6):
            card = DataCard(STAT_LABELS[i], "-", STAT_UNITS[i], "up", "",
                            bg_color=list(CARD_BG))
            # capture i in closure
            card.tap_callback = (lambda idx, lbl=STAT_LABELS[i], unit=STAT_UNITS[i]:
                           lambda: self._show_graph(idx, lbl, unit))(i)
            self._cards.append(card)
            self._grid.add_widget(card)
        body.add_widget(self._grid)

        # Expandable Location Map
        #locationmap = ExpandableLocationMap(size_hint_x=1)
        #body.add_widget(locationmap)

        # Alerts Panel
        self.alerts_panel = AlertsPanel(size_hint_x=1)
        body.add_widget(self.alerts_panel)

        # Spacer so last card isn't cut off by nav bar
        body.add_widget(Widget(size_hint_y=None, height=dp(10)))

        scroll.add_widget(body)
        root.add_widget(scroll)
        self.add_widget(root)

    def _show_graph(self, stat_index, stat_label, stat_unit):
        """Fetch history from bridge and display the graph overlay."""
        bridge = App.get_running_app().bridge
        timestamps, values = bridge.get_history(self._active_site, stat_index)

        if not values:
            return

        overlay = GraphOverlay(
            title      = stat_label,
            unit       = stat_unit,
            site       = self._active_site,
            timestamps = timestamps,
            values     = values,
        )
        Window.add_widget(overlay)

    def _on_site_selected(self, site_key):
        """Called when the user taps a site button; re-renders with cached data."""
        self._active_site = site_key
        data = self._latest.get(site_key)
        if data:
            self._render(data)

    def _render(self, site):
        stats  = site["stats"]
        flags  = site["flags"]
        deltas = site["deltas"]
        alerts = site["alerts"]

        for i, card in enumerate(self._cards):
            val       = f"{stats[i]:.1f}" if stats[i] is not None else "-"
            direction = "up" if flags[i] else "down"
            card.update(val, direction, deltas[i])

        self.alerts_panel.update_alerts(alerts)

    def on_bridge_tick(self, maize, brassica, orchard, timestamp):
        # Cache all three sites every tick
        self._latest["maize"]    = maize
        self._latest["brassica"] = brassica
        self._latest["orchard"]  = orchard

        # Render whichever site is currently selected
        self._render(self._latest[self._active_site])

        App.get_running_app().header.update_time(timestamp)


class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        make_bg(self)
        layout = BoxLayout(orientation="vertical",
                           padding=dp(24), spacing=dp(20))

        layout.add_widget(Label(
            text="Scan", font_size=sp(22), color=NEUTRAL,
            bold=True, size_hint=(1, None), height=dp(40)
        ))

        layout.add_widget(Label(
            text="Point camera at QR code or device ID",
            font_size=sp(12), color=DIM, halign="center",
            size_hint=(1, None), height = dp(20)
        ))

        self.camera = Camera(play=True, index = 0, size_hint = (1, 1)) #0 = rear camera 

        layout.add_widget(self.camera)

        scan_btn = Button(
            text="Start Scanning", font_size=sp(14),
            height=dp(48),
            background_color=(*ACCENT[:3], 1),
            color=NEUTRAL, bold=True, size_hint = (1, None)
        )
        scan_btn.bind(on_press=self.capture)

        layout.add_widget(scan_btn)
        self.add_widget(layout)

    def capture(self, instance):
        self.camera.export_to_png('scan.png')


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
        # CHANGED: role value left blank here; populated in on_enter once user is logged in
        self._role_value_lbl = None
        for (label, value) in [("Role", ""),
                                ("Location", "Leeds, UK"),
                                ("Devices", "7 connected"),
                                ("Plan", "Pro")]:
            row = Card(orientation="horizontal",
                       bg_color=list(CARD_BG),
                       size_hint_y=None, height=dp(44),
                       padding=[dp(14), 0])
            row.add_widget(Label(text=label, font_size=sp(12),
                                 color=DIM, halign="left"))
            val_lbl = Label(text=value, font_size=sp(12),
                            color=NEUTRAL, halign="right")
            row.add_widget(val_lbl)
            layout.add_widget(row)
            if label == "Role":
                self._role_value_lbl = val_lbl

        layout.add_widget(Widget())
        self.add_widget(layout)

    def on_enter(self, *_):
        # CHANGED: update the role label when the screen is shown (user is logged in by then)
        if self._role_value_lbl:
            self._role_value_lbl.text = App.get_running_app().user_role


class DashboardHeader(BoxLayout):
    # Define these as None initially if you want to be safe, 
    # but the order in __init__ is what matters most.
    date_lbl = None
    time_lbl = None

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(56))
        kwargs.setdefault("padding", [dp(14), dp(6)])
        kwargs.setdefault("spacing", dp(10))
        super().__init__(**kwargs)

        # 1. INITIALIZE ATTRIBUTES FIRST
        self.date_lbl = Label(
            text=datetime.now().strftime("%A, %d %B %Y"),
            font_size=sp(9), color=DIM, halign="left", valign="top"
        )
        self.time_lbl = Label(
            text="00:00", font_size=sp(16), color=ACCENT, 
            bold=True, halign="right", valign="middle", size_hint_x=0.4
        )

        # 2. SETUP CANVAS
        with self.canvas.before:
            Color(*SURFACE2)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        # 3. CONSTRUCT LAYOUT
        title_box = BoxLayout(orientation="vertical")
        ov = Label(text="Overview", font_size=sp(14),
                   color=NEUTRAL, bold=True, halign="left", valign="bottom")
        
        # Bind size AFTER labels are created
        ov.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.date_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.time_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))

        title_box.add_widget(ov)
        title_box.add_widget(self.date_lbl)
        
        self.add_widget(title_box)
        self.add_widget(self.time_lbl)

    def _upd(self, w, *_):
        self._bg.pos  = w.pos
        self._bg.size = w.size

    def update_time(self, dt_obj):
        # Now these attributes are guaranteed to exist
        if self.date_lbl and self.time_lbl:
            self.date_lbl.text = dt_obj.strftime("%A, %d %B %Y")
            self.time_lbl.text = dt_obj.strftime("%H:%M")


# App Root
class DashboardApp(App):
    def build(self):
        self.title = "Environmental App"

        self._root = BoxLayout(orientation = "vertical")

        self.sm = ScreenManager(transition = NoTransition())

        login_screen = SignInScreen(
            on_authenticated=self._on_login_success,
            name = 'login'
        )
        self.sm.add_widget(login_screen)


        self._dashboard = DashboardScreen(name="dashboard")
        self._app_sm = ScreenManager()
        self._app_sm.add_widget(self._dashboard)
        self._app_sm.add_widget(ScanScreen(name="scan"))
        self._app_sm.add_widget(ProfileScreen(name="profile"))

        self.bridge = Bridge(2022, 1, 1)
        self.bridge.on_tick = self._dashboard.on_bridge_tick
        self.bridge.start()

        self._nav = NavBar(screen_manager=self._app_sm)
        self.header = DashboardHeader()

        self._root.add_widget(self.sm)
        return self._root
    
    def _on_login_success(self, role):
        self.user_role = role
        self._root.clear_widgets()
        self._root.add_widget(self.header)
        self._root.add_widget(self._app_sm)
        self._root.add_widget(self._nav)


if __name__ == "__main__":
    DashboardApp().run()