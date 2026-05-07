"""
File: Dashboard.py
Author: Holly, Ashwin, Liam, Sara, Izzy
Created: 20/03/26
Last modified: 05/05/26

Description: This file creates all of the visuals seen on the application and 
             performs AI functionalities and API connection

Dependencies:
- kivy
- bcrypt
- opencv-python
- kivymd
- sqlite3
- sys
- os
- datetime
- numpy
- tensorflow
- PIL
- threading
"""

#All imports and dependencies
from kivymd.app import MDApp
from kivy.uix.screenmanager import (ScreenManager, Screen,
                                    SlideTransition, NoTransition)
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import (
    Color,
    Rectangle,
    RoundedRectangle,
    Line,
    Ellipse,
    Triangle,
    InstructionGroup,
)

try:
    from kivy.graphics.boxshadow import BoxShadow
except Exception:
    BoxShadow = None
from kivy.uix.camera import Camera
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    StringProperty,
    NumericProperty,
    ListProperty,
)
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from Code.Database.Queries.sign_in import sign_in_query, sign_up_query
import sqlite3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Code"))
from Code.bridge import Bridge, DATASET_START
from datetime import datetime
import numpy as np
import tensorflow as tf
from PIL import Image as PILImage
import threading
from kivymd.uix.label import MDIcon
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.relativelayout import RelativeLayout

# Fonts
FONT_NAME = "Roboto"
try:
    for _fp in (
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ):
        if os.path.exists(_fp):
            LabelBase.register(name="AppMono", fn_regular=_fp)
            FONT_NAME = "AppMono"
            break
except Exception:
    FONT_NAME = "Roboto"

#Creating a database connection
DB_PATH = os.path.join(
    os.path.dirname(__file__), "Code", "Database", "Queries", "pest_control.db"
)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

#Creating camera connection
os.environ["KIVY_CAMERA"] = "opencv"

#Loading Sequential model into application
print("Loading model")
model = tf.keras.models.load_model('crop_disease_model.keras', safe_mode=False)
with open ("class_names.txt") as f:
    CLASS_NAMES = f.read().splitlines()
SAVE_DIR = "captured_crops"
os.makedirs(SAVE_DIR, exist_ok = True)

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
# Theme
APP_NAME = "Environmental Dashboard"

BG = (0.039, 0.039, 0.039, 1)
Window.clearcolor = BG
SURFACE = (0.078, 0.078, 0.078, 1)
INPUT_BG = (0.102, 0.102, 0.102, 1)

CARD_BG = SURFACE
BAR_BG = SURFACE
BORDER = (0.165, 0.165, 0.165, 1)

ACCENT = (0.267, 1.000, 0.533, 1)
ACCENT2 = (0.231, 0.510, 0.965, 1)
UP_CLR = ACCENT
DOWN_CLR = (1.000, 0.267, 0.267, 1)
ALERT_WARN = (1.000, 0.667, 0.000, 1)
ALERT_CRIT = DOWN_CLR

NEUTRAL = (0.910, 0.910, 0.910, 1)
DIM = (1, 1, 1, 1)

OVERLAY_SUBTLE = (1, 1, 1, 0.03)
OVERLAY_LIGHT = (1, 1, 1, 0.05)

RADIUS_SM = dp(6)
RADIUS_MD = dp(10)
RADIUS_LG = dp(14)
ELEV_Y = dp(1)
SHADOW_CLR = (0, 0, 0, 0.50)

# Prevents white flash on startup
Window.clearcolor = BG

# Screen slide direction order
SCREEN_ORDER = ["dashboard", "scan", "profile"]

def predict_image(img_path):
    '''
    Takes captured image and runs it through model to predict crop type, disease and confidence level.

    Parameters
    ----------
    img_path (string):
        Path to captured image

    Returns
    -------
    label (string):
        Name of crop type and predicted disease
    confidence (float):
        Percentage confidence of prediction outcome

    '''
    img = PILImage.open(img_path).convert("RGB").resize((128, 128))
    arr = np.array(img, dtype=np.float32)
    print(f"Image mean pixel value: {arr.mean():.2f}")  
    if arr.mean() < 5.0:
        return "Error: black image captured - try again", 0.0
    arr = np.expand_dims(arr, axis = 0)
    prediction = model.predict(arr)
    top_index = int(np.argmax(prediction[0]))
    confidence = float(prediction[0][top_index]) * 100
    label = CLASS_NAMES[top_index].replace("___", " - ").replace("_", " ")
    return label, confidence

def with_alpha(color, a):
    '''
    Returns a new RGBA colour tuple with the specified alpha value

    Parameters
    ----------
    color (tuple):
        A 4-tuple representing a RGBA color(r, g, b, a), original alpha value is ignored
    a (float or int):
        The new alpha value
    
    Returns
    -------
    tuple: A new RGBA tuple with an updated alpha value
    '''
    r, g, b, _ = color
    return (r, g, b, a)


def shade(color, factor):
    '''
    Returns a shaded version of an RGBA colour by scaling its RGB components
    The RGB values are multipled by the given factor.

    Parameters
    ----------
    color (tuple): A 4-tuple representing an RGBA colour (r, g, b, a)

    factor (float): The shading factor used to scale the RGB components

    Returns
    -------
    tuple: A new RGBA colour tuple with adjusted RGB values and an unchanged alpha

    '''
    r, g, b, a = color
    return (min(1.0, r * factor), min(1.0, g * factor),
            min(1.0, b * factor), a)


def make_label(
    text,
    font_size=sp(12),
    color=NEUTRAL,
    bold=False,
    halign="left",
    height=dp(24),
    **kwargs,
    ):
    '''
    Creates and returns a configures Kivy Label widget with standardised styling

    Parameters
    ----------
    text (string):
        The text to be displayed in the label
    font_size (int or float, optional):
        Font size of the label text
    color (tuple, optional):
        RGBA colour tuple for the text
    bold (boolean, optional):
        Whether the text should be bold
    halign (int or float, optional):
        Fixed height of the label
    **kwargs: 
        Additional keyword arguments passed directly into Kivy Label

    Returns
    -------
    Label: A configured Kivy label instance
    '''
    kwargs.setdefault("text", text)
    kwargs.setdefault("font_name", FONT_NAME)
    kwargs.setdefault("font_size", font_size)
    kwargs.setdefault("color", color)
    kwargs.setdefault("bold", bold)
    kwargs.setdefault("halign", halign)
    kwargs.setdefault("valign", "middle")
    if "size_hint" not in kwargs and "size_hint_y" not in kwargs:
        kwargs.setdefault("size_hint_y", None)
    kwargs.setdefault("height", height)
    lbl = Label(**kwargs)
    lbl.bind(size=lambda w, s: setattr(w, "text_size", (s[0], None)))
    return lbl


# Card class
class Card(BoxLayout):
    '''
    A UI container widget styled as a card with rounded corners, background colour, border, and a top highlight

    Class extends Kivy's BoxLayout and provides a custom-drawn panel using canvas instructions

    Attributes:
        bg_color (ListProperty): Background RGBA colour of the card
        radius (NumericProperty): Corner radius for rounded edges
        draw_panel (BooleanProperty): Enables or disables custom drawing
    
    Methods:
        _draw(*args): Redraws the card's canvas elements when properties change
    '''
    bg_color = ListProperty(list(CARD_BG))
    radius = NumericProperty(RADIUS_MD)
    draw_panel = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.draw_panel:
            self.bind(pos=self._draw, size=self._draw, bg_color=self._draw)
            Clock.schedule_once(self._draw)

    def _draw(self, *_):
        if not self.draw_panel:
            return
        self.canvas.before.clear()
        x, y = self.pos
        w, h = self.size
        r = float(self.radius)
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(*OVERLAY_SUBTLE)
            Rectangle(pos=(x + dp(1), y + h - dp(1)),
                      size=(max(0, w - dp(2)), dp(1)))
            Color(*BORDER)
            Line(rounded_rectangle=[x, y, w, h, r], width=1.0)


class DataArrow(Widget):
    '''
    A custom Kivy widget extending Kivy Widget class that displays an arrow indicating data trend direction

    Arrow visually represents whether a value is above or below trend with an upward or downward pointing triangle

    Attributes:
        direction (StringProperty): Direction of the arrow, "up" or "down"
    
    Methods:
        _draw(*args): Renders the arrow shape on the canvas based on size and direction
    '''
    direction = StringProperty("up")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, direction=self._draw)

    def _draw(self, *_):
        self.canvas.clear()
        nx, ny = self.x + self.width / 2, self.y + self.height / 2
        aw = min(self.width, self.height) * 0.55
        ah = min(self.width, self.height) * 0.65

        # Determine Color and Shape
        if self.direction == "up":
            clr = (0, 1, 0, 1) # Green
        elif self.direction == "down":
            clr = (1, 0, 0, 1) # Red
        else:
            clr = (1, 1, 1, 1) # White for "stable"[cite: 3]

        with self.canvas:
            Color(*clr)
            if self.direction == "up":
                Triangle(points=[nx-aw/2, ny-ah/4, nx+aw/2, ny-ah/4, nx, ny+ah/2])
            elif self.direction == "down":
                Triangle(points=[nx-aw/2, ny+ah/4, nx+aw/2, ny+ah/4, nx, ny-ah/2])
            elif self.direction == "stable":
                # White horizontal dash for no change
                Line(points=[nx - aw/2, ny, nx + aw/2, ny], width=dp(1.5))
            else:
                Line(points=[nx - aw/2, ny, nx + aw/2, ny], width=dp(1.5))

                
# Used for modal/auth containers
class RoundedCard(FloatLayout):
    '''
    A custom container widget extending Kivy's FloatLayout that renders a rounded card with background, border, highlight, and optional shadow/elevation

    Attributes:
        _bg (tuple): Background RGBA colour of the card
        _radius (int or float): Corner radius for rounded edges
        _border (tuple): Border RGBA colour

    Methods:
        _redraw(*args): Re-renders the card whenever position or size changes
    '''
    def __init__(
        self, bg_color=CARD_BG, radius=RADIUS_LG, border_color=BORDER, **kwargs
    ):
        super().__init__(**kwargs)
        self._bg = bg_color
        self._radius = radius
        self._border = border_color
        self.bind(pos=self._redraw, size=self._redraw)
        Clock.schedule_once(self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        x, y = self.pos
        w, h = self.size
        r = float(self._radius)
        with self.canvas.before:
            Color(*SHADOW_CLR)
            if BoxShadow is not None:
                BoxShadow(
                    pos=(x, y),
                    size=(w, h),
                    offset=(0, -dp(8)),
                    blur_radius=dp(32),
                    spread_radius=(-dp(12), -dp(12)),
                    border_radius=(r, r, r, r),
                )
            else:
                RoundedRectangle(pos=(x, y - ELEV_Y),
                                 size=(w, h + ELEV_Y), radius=[r])
            Color(*self._bg)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(*OVERLAY_LIGHT)
            Rectangle(pos=(x + dp(1), y + h - dp(1)),
                      size=(max(0, w - dp(2)), dp(1)))
            Color(*self._border)
            Line(rounded_rectangle=[x, y, w, h, r], width=1.0)


# Inline error label (hidden by default)
class ErrorLabel(Label):
    '''
    An inline error message label extending Kivy Label for displaying validation or UI feedback messages, hidden by default

    Methods:
        show(message): Displays the provided error message and makes the label visible
        hide(): Clears the message and hides the label

    '''
    def __init__(self, **kwargs):
        super().__init__(
            text="",
            font_name=FONT_NAME,
            font_size=sp(12),
            color=ALERT_CRIT,
            halign="left",
            valign="middle",
            size_hint=(1, None),
            height=0,
            opacity=0,
        )
        self.bind(size=lambda w, s: setattr(w, "text_size", s))

    def show(self, message):
        self.text = message
        self.height = dp(20)
        self.opacity = 1

    def hide(self):
        self.text = ""
        self.height = 0
        self.opacity = 0


# Inputs


# Text input
class Input(TextInput):
    '''
    A custom style single-line text input extending Kivy's TextInput

    Parameters:
        hint(str): Placeholder text shown when input is empty
        password(bool): If true, masks input characters for password entry
        font_size (int or float, optional): Font size of the input text
    '''
    def __init__(self, hint="", password=False, **kwargs):
        passed_font_size = kwargs.pop("font_size", sp(13))
        super().__init__(
            hint_text=hint,
            password=password,
            multiline=False,
            font_name=FONT_NAME,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=NEUTRAL,
            hint_text_color=DIM,
            cursor_color=ACCENT,
            font_size=passed_font_size,
            padding=[dp(12), dp(13), dp(12), dp(11)],
            size_hint=(1, None),
            height=dp(46),
            write_tab=False,
            **kwargs,
        )


class InputField(BoxLayout):
    '''
    Styled input container extending Kivy's BoxLayout that wraps a custom Input widget

    Attributes:
        _input(Input): The internal text input widget
        _bg (RoundedRectangle): Background shape
        _border_group(InstructionGroup): Canvas group for dynamic border

    Methods:
        _redraw(*args): Updates the background and border styling
        _on_focus(instance, focused): Triggered when the input gains or loses focus - updates border styling
        text(str): Proxy property that returns the internal input's text

    Parameters:
        hint(str): Placeholder text shown when input is empty
        password(bool): If true, masks input characters for password entry
        font_size (int or float, optional): Font size of the input text
    
        
    '''
    def __init__(self, hint="", password=False, font_size=sp(13), **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(46))
        super().__init__(**kwargs)

        self._input = Input(hint=hint, password=password, font_size=font_size)
        self._input.bind(focus=self._on_focus)
        self.add_widget(self._input)

        with self.canvas.before:
            Color(*INPUT_BG)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[RADIUS_SM]
            )

        self._border_group = InstructionGroup()
        self.canvas.after.add(self._border_group)
        self.bind(pos=self._redraw, size=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw())

    def _redraw(self, *_):
        if hasattr(self, "_bg"):
            self._bg.pos = self.pos
            self._bg.size = self.size
        self._border_group.clear()
        self._border_group.add(Color(*(ACCENT if self._input.focus
                                       else BORDER)))
        self._border_group.add(
            Line(rounded_rectangle=[*self.pos, *self.size,
                                    float(RADIUS_SM)], width=1.0)
        )

    def _on_focus(self, inst, focused):
        self._redraw()

    # Proxy .text so the panels can still do self.username.text
    @property
    def text(self):
        return self._input.text


class SignInButton(Button):
    '''
    A custom styled button used for signing by extending Kivy's Button

    Methods: 
        _draw(*args): Renders the button background and border based on size and and interaction state
        on_focus(instance, value): Handles focus changes and updates styling when the button gains or loses keyboard focus
    '''
    def __init__(self, text="Sign In", **kwargs):
        super().__init__(
            text=text,
            font_name=FONT_NAME,
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=BG,
            bold=True,
            font_size=sp(14),
            size_hint=(1, None),
            height=dp(50),
            **kwargs,
        )
        self.bind(pos=self._draw, size=self._draw, state=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        x, y = self.pos
        w, h = self.size
        r = float(RADIUS_SM)
        fill = shade(ACCENT, 0.82) if self.state == "down" else ACCENT
        with self.canvas.before:
            Color(*fill)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(*with_alpha((0, 0, 0, 1), 0.12))
            Line(rounded_rectangle=[x, y, w, h, r], width=1.0)

    def on_focus(self, instance, value):
        if value:
            self.bg_color = ACCENT  # Highlight the button when tabbed onto
        else:
            self.bg_color = SURFACE  # Return to normal when focus leaves


# Secondary button
class SignUpButton(Button):
    '''
    A custom styled button used for signing up actions by extending Kivy's Button

    Methods
    -------
        _draw(*args): Renders the button background and border based on size and and interaction state
    '''
    def __init__(self, text="Sign Up", **kwargs):
        super().__init__(
            text=text,
            font_name=FONT_NAME,
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=ACCENT,
            bold=True,
            font_size=sp(14),
            size_hint=(1, None),
            height=dp(50),
            **kwargs,
        )
        self.bind(pos=self._draw, size=self._draw, state=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        x, y = self.pos
        w, h = self.size
        r = float(RADIUS_SM)
        stroke = (
            with_alpha(ACCENT, 0.60)
            if self.state == "down"
            else with_alpha(BORDER, 1.0)
        )
        self.color = ACCENT
        with self.canvas.before:
            Color(
                *(
                    with_alpha(ACCENT, 0.08)
                    if self.state == "down"
                    else with_alpha(CARD_BG, 0.0)
                )
            )
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(*stroke)
            Line(rounded_rectangle=[x, y, w, h, r], width=1.0)


# Divider row
class Divider(BoxLayout):
    """
    A horizontal divider widget with optional centered text, used to separate sections

    Attributes
    ----------
    _line_holders(list): Internal widgets used to render the divider lines

    Methods
    -------
    _draw_line(widget): Draws a horizontal line across the given widget

    """

    def __init__(self, text="or", **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(24),
            spacing=dp(8),
            **kwargs,
        )

        self._line_holders = []
        for _ in range(2):
            lh = Widget(size_hint=(1, None), height=dp(1))
            lh.bind(
                pos=lambda w, *_: self._draw_line(w),
                size=lambda w, *_: self._draw_line(w),
            )
            self._line_holders.append(lh)

        label = make_label(
            text, font_size=sp(12), color=DIM, halign="center", height=dp(18)
        )
        label.width = dp(30)

        self.add_widget(self._line_holders[0])
        self.add_widget(label)
        self.add_widget(self._line_holders[1])

    def _draw_line(self, widget):
        widget.canvas.before.clear()
        with widget.canvas:
            Color(*BORDER)
            Line(
                points=[widget.x, widget.center_y,
                        widget.right, widget.center_y],
                width=1,
            )


class SignInPanel(BoxLayout):
    '''
    A UI panel for user sign-in, containing user input fields, buttons, and validation feedback
    Extends Kivy's BoxLayout

    Parameters
    ----------
    switch_cb(callable): Callback function to switch to another panel
    success_cb(callable): Callback function executed on successful sign-in, receiving user information as an argument

    Attributes
    ----------
    username (InputField): Input field for the username
    password (InputField): Input field for the password
    _error (ErrorLabel): Label used to display validation or login errors

    Methods
    -------
    _build(): Constructs and lays out all UI components
    _on_sign_in(*args): Handles sign-in logic, validates input, and triggers success or error feedback
    '''
    def __init__(self, switch_cb, success_cb, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(12), **kwargs)
        self.switch_cb = switch_cb
        self.success_cb = success_cb
        self._build()

    def _build(self):
        self.add_widget(
            make_label(
                "Welcome", font_size=sp(28),
                color=NEUTRAL, bold=True, height=dp(34)
            )
        )
        self.add_widget(
            make_label(
                "Sign in to your environmental dashboard",
                font_size=sp(14),
                color=DIM,
                height=dp(22),
            )
        )
        self.add_widget(Widget(size_hint=(1, None), height=dp(10)))

        self.add_widget(
            make_label("USERNAME", font_size=sp(11), color=DIM, height=dp(16))
        )
        self.username = InputField(hint="e.g. j.farmer")
        self.add_widget(self.username)

        self.add_widget(
            make_label("PASSWORD", font_size=sp(11), color=DIM, height=dp(16))
        )
        self.password = InputField(hint="••••••••", password=True)
        self.add_widget(self.password)

        self.username._input.focus_next = self.password._input
        self._error = ErrorLabel()
        self.add_widget(self._error)

        self.add_widget(Widget(size_hint=(1, None), height=dp(4)))

        sign_in = SignInButton(text="Sign In")
        sign_in.bind(on_release=self._on_sign_in)
        self.add_widget(sign_in)

        self.add_widget(Divider())

        signup_btn = SignUpButton(text="Create an account")
        signup_btn.bind(on_release=lambda *_: self.switch_cb("signup"))
        self.add_widget(signup_btn)

        self.add_widget(Widget())

    def _on_sign_in(self, *_):
        user = self.username.text.strip()
        pwd = self.password.text.strip()

        if not user or not pwd:
            self._error.show("Please enter your username and password")
            return

        user_info = sign_in_query(conn, cursor, user, pwd)
        if user_info:
            self._error.hide()
            self.success_cb(user_info)
        else:
            self._error.show("Incorrect username or password.")


class SignUpPanel(BoxLayout):
    '''
    A UI panel for user sign-up, containing user input fields, buttons, and validation feedback
    Extends Kivy's BoxLayout

    Parameters
    ----------
    switch_cb(callable): Callback function to switch to another panel
    success_cb(callable): Callback function executed on successful sign-in, receiving user information as an argument

    Attributes
    ----------
    username (InputField): Input field for the username
    password (InputField): Input field for the password
    fullname (InputField): Input field for the fullname of the user
    _selected_role (str): Currently selected user role ("Farmer" or "Researcher")
    _farmer_btn (Button):  Button for selecting the "Farmer" role
    _researcher_btn (Button): Button for selecting the "Researcher" role
    _error (ErrorLabel): Label used to display validation or login errors

    Methods
    -------
    _build(): Constructs and lays out all UI components
    _role_btn(label): Creates a selectable role button
    _draw_role_btn(btn, *args): Draws and styles a role button based on selection state
    _set_role(role): Updates the selected role and refreshes button styles
    _on_sign_up(*args): Handles sign-up logic, validates input, and triggers success or error feedback
    '''
    def __init__(self, switch_cb, success_cb, **kwargs):
        super().__init__(
            orientation="vertical", spacing=dp(10), size_hint=(1, 1), **kwargs
        )
        self.switch_cb = switch_cb
        self.success_cb = success_cb
        self._selected_role = "Farmer"
        self._build()

    def _build(self):
        self.add_widget(
            make_label(
                "Create account",
                font_size=sp(24),
                color=NEUTRAL,
                bold=True,
                height=dp(30),
            )
        )
        self.add_widget(
            make_label(
                "Start monitoring your crops today",
                font_size=sp(14),
                color=DIM,
                height=dp(22),
            )
        )
        self.add_widget(Widget(size_hint=(1, None), height=dp(8)))

        self.add_widget(
            make_label("FULL NAME", font_size=sp(11), color=DIM, height=dp(16))
        )
        self.fullname = InputField(hint="e.g. John Farmer")
        self.add_widget(self.fullname)

        self.add_widget(
            make_label("USERNAME", font_size=sp(11), color=DIM, height=dp(16))
        )
        self.username = InputField(hint="e.g. j.farmer")
        self.add_widget(self.username)

        self.add_widget(
            make_label("PASSWORD", font_size=sp(11), color=DIM, height=dp(16))
        )
        self.password = InputField(hint="Min. 8 characters", password=True)
        self.add_widget(self.password)

        self.add_widget(
            make_label("I AM A", font_size=sp(11), color=DIM, height=dp(16))
        )
        role_row = BoxLayout(
            orientation="horizontal", spacing=dp(8),
            size_hint=(1, None), height=dp(42)
        )

        self._farmer_btn = self._role_btn("Farmer")
        self._researcher_btn = self._role_btn("Researcher")
        role_row.add_widget(self._farmer_btn)
        role_row.add_widget(self._researcher_btn)
        self.add_widget(role_row)
        self._set_role("Farmer")

        self._error = ErrorLabel()
        self.add_widget(self._error)

        self.add_widget(Widget(size_hint=(1, None), height=dp(4)))

        sign_up = SignInButton(text="Sign Up")
        sign_up.bind(on_release=self._on_sign_up)
        self.add_widget(sign_up)

        self.add_widget(Divider())

        signup_btn = SignUpButton(text="Sign In Instead")
        signup_btn.bind(on_release=lambda *_: self.switch_cb("login"))
        self.add_widget(signup_btn)

        self.add_widget(Widget())

    def _role_btn(self, label):
        btn = Button(
            text=label,
            font_name=FONT_NAME,
            font_size=sp(12),
            bold=True,
            size_hint=(1, 1),
            background_normal="",
            background_color=(0, 0, 0, 0),
        )
        btn.bind(on_release=lambda *_: self._set_role(label))
        btn.bind(pos=self._draw_role_btn, size=self._draw_role_btn)
        return btn

    def _draw_role_btn(self, btn, *_):
        btn.canvas.before.clear()
        with btn.canvas.before:
            r = float(RADIUS_SM)
            selected = self._selected_role == btn.text
            if selected:
                Color(*with_alpha(ACCENT, 0.12))
                btn.color = ACCENT
                border = with_alpha(ACCENT, 0.35)
            else:
                Color(*OVERLAY_SUBTLE)
                btn.color = DIM
                border = BORDER
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[r])
            Color(*border)
            Line(rounded_rectangle=[btn.x, btn.y,
                                    btn.width, btn.height, r], width=1.0)

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
            self._error.show("Password must be at least 8 characters")
            return

        success = sign_up_query(
            conn, cursor, name, user, pwd, name, self._selected_role
        )
        if success:
            self._error.hide()
            self.success_cb({"role": self._selected_role, "fullname": name, "username": user})
        else:
            self._error.show("Username is taken. Please choose another.")


# Data cards


# Stat card
class DataCard(Card):
    '''
    A compact data display card uses to display a metric, its value, trend direction, and change indictator

    Extends Kivy's Card and includes:
    - Title label
    - Main value display (optional unit formatting)
    - A directional arrow indicating relation to average
    - Delta label showing change from average
    - Coloured bar showing change for average (red/green)

    Parameters
    ----------
    title(str): the title fo the data metric
    value (str/int/float): main value to display
    unit(str): unit of measurement
    direction(str): direction of arrow
    delta(str): change from average

    Attributes
    ----------
    _direction(str): Above/below average
    _bar_color (tuple): Colour of the indicator bar
    _unit (str): Unit for value formatting
    _value_lbl (Label): Label for displaying main value
    _arrow (DataArrow): Widget indicating above/below average
    _delta_lbl (Label): Label displaying the delta/change
    tap_callback (callable): Optional callback triggered when card is tapped

    Methods
    -------
    _fmt(value): Formats the value with unit (if provided)
    _draw_top_bar(*args): Draws the card background, border, and trend bar
    update(value, direction, delta): Updates displayed data and styling
    on_touch_down(touch): Tracks touch interaction for tap detection
    on_touch_up(touch): Handles tap release and triggers callback if set
    '''
    def __init__(self, title, value, unit, direction, delta, **kwargs):
        # We use FloatLayout as the root so the button can float in the corner
        kwargs.setdefault("draw_panel", False)
        super().__init__(**kwargs)

        self.tap_callback = None
        self._direction = direction
        self._bar_color = UP_CLR if direction == "up" else DOWN_CLR
        self._unit = unit

        # 1. Main container is now a RelativeLayout so children 
        # position relative to this card's boundaries
        self.container = RelativeLayout()
        
        # 2. THE BUTTON (Visual only)
        # We anchor it to top-right with a small offset (padding)
        self.graph_btn_visual = Label(
            text="CLICK FOR GRAPH",
            font_name=FONT_NAME,
            font_size=sp(10),
            bold=True,
            color=ACCENT,
            size_hint=(None, None),
            size=(dp(90), dp(23)),
            pos_hint={'top': 0.95, 'right': 0.95}
        )

        with self.graph_btn_visual.canvas.before:
            Color(*with_alpha(ACCENT, 0.1))
            self.btn_bg = RoundedRectangle(radius=[dp(4)])
            Color(*with_alpha(ACCENT, 0.3))
            self.btn_border = Line(width=1.0)

        self.graph_btn_visual.bind(pos=self._update_btn_ui, size=self._update_btn_ui)
        
        # 3. THE DATA CONTENT
        # We wrap this in a BoxLayout and give it padding so it stays 
        # away from the top-right corner where the button lives
        self.content = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(10), dp(12), dp(10)],
            spacing=dp(4)
        )

        self.content.add_widget(
            make_label(
                title.upper(),
                font_size=sp(18),
                color=DIM,
                bold=True,
                height=dp(16),
                shorten=True,
                shorten_from="right",
            )
        )

        val_row = BoxLayout(orientation="horizontal", size_hint_y=1, spacing=dp(4))
        self._value_lbl = make_label(
            self._fmt(value),
            font_size=sp(32),
            color=NEUTRAL,
            bold=True,
            halign="left",
            size_hint=(1, 1),
            markup=True,
        )

        self._arrow = DataArrow(
            direction=direction,
            size_hint=(None, None),
            size=(dp(20), dp(20)),
            pos_hint={"center_y": 0.5},
        )

        val_row.add_widget(self._value_lbl)
        val_row.add_widget(self._arrow)
        self.content.add_widget(val_row)

        if direction == "up":
            delta_color = (0, 1, 0, 1)    # Green (UP_CLR)
        elif direction == "down":
            delta_color = (1, 0, 0, 1)    # Red (DOWN_CLR)
        else:
            delta_color = (1, 1, 1, 1)    # White for "stable" or None

        self._delta_lbl = make_label(
            delta,
            font_size=sp(9),
            color=delta_color,  # Use the dynamic color variable
            halign="right",
            height=dp(16),
        )
        self.content.add_widget(self._delta_lbl)

        # Add both to the RelativeLayout
        self.container.add_widget(self.content)
        self.container.add_widget(self.graph_btn_visual)
        self.add_widget(self.container)

        self.bind(pos=self._draw_top_bar, size=self._draw_top_bar, bg_color=self._draw_top_bar)
        Clock.schedule_once(self._draw_top_bar)

    def _update_btn_ui(self, instance, value):
        self.btn_bg.pos = instance.pos
        self.btn_bg.size = instance.size
        self.btn_border.rounded_rectangle = [instance.x, instance.y, instance.width, instance.height, dp(4)]

    def _fmt(self, value):
        if self._unit:
            return f"{value}[size={int(sp(11))}] {self._unit}[/size]"
        return f"{value}"

    def _draw_top_bar(self, *_):
        self.canvas.before.clear()
        x, y = self.pos
        w, h = self.size
        r = float(self.radius)
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(*self._bar_color)
            RoundedRectangle(pos=(x + dp(12), y + dp(2)), size=(max(0, w - dp(24)), dp(2)), radius=[dp(1)])
            Color(*OVERLAY_SUBTLE)
            Rectangle(pos=(x + dp(1), y + h - dp(1)), size=(max(0, w - dp(2)), dp(1)))
            Color(*BORDER)
            Line(rounded_rectangle=[x, y, w, h, r], width=1.0)

    def update(self, value, direction, delta):
        self._direction = direction
        
        # 1. Update the card's top accent bar color
        if direction == "up":
            self._bar_color = UP_CLR
        elif direction == "down":
            self._bar_color = DOWN_CLR
        elif direction == "stable":
            self._delta_lbl.color = (1, 1, 1, 1) # White for stable
        else:
            self._delta_lbl.color = (1, 1, 1, 1) # White for stable
            
        self._draw_top_bar()
        self._value_lbl.text = self._fmt(value)
        self._arrow.direction = direction
        self._delta_lbl.text = delta
        
        # 2. Update the text color of the delta string
        if direction == "up":
            self._delta_lbl.color = UP_CLR
        elif direction == "down":
            self._delta_lbl.color = DOWN_CLR
        elif direction == "stable":
            self._delta_lbl.color = (1, 1, 1, 1) # White for stable
        else:
            self._delta_lbl.color = (1, 1, 1, 1) # White for stable

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
    def _fmt(self, value):
        if self._unit:
            return f"{value}[size={int(sp(11))}] {self._unit}[/size]"
        return f"{value}"

    def _draw_top_bar(self, *_):
        self.canvas.before.clear()
        x, y = self.pos
        w, h = self.size
        r = float(self.radius)
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(*self._bar_color)
            RoundedRectangle(
                pos=(x + dp(12), y + dp(2)),
                size=(max(0, w - dp(24)), dp(2)),
                radius=[dp(1)],
            )
            Color(*OVERLAY_SUBTLE)
            Rectangle(pos=(x + dp(1), y + h - dp(1)),
                      size=(max(0, w - dp(2)), dp(1)))
            Color(*BORDER)
            Line(rounded_rectangle=[x, y, w, h, r], width=1.0)

    def update(self, value, direction, delta):
        self._direction = direction
        if direction == "up":
            self._bar_color = UP_CLR
        elif direction == "down":
            self._bar_color = DOWN_CLR
        else:
            self._bar_color = (1, 1 , 1 ,1)
        self._draw_top_bar()
        self._value_lbl.text = self._fmt(value)
        self._arrow.direction = direction
        self._delta_lbl.text = delta
        if direction == "up":
            self._delta_lbl.color = UP_CLR
        elif direction == "down":
            self._delta_lbl.color = DOWN_CLR
        else:
            self._delta_lbl.color = (1, 1 , 1 ,1)

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


# Sample tests for testing purposes
SAMPLE_ALERTS = [
    {
        "level": "critical",
        "title": "Plant dying",
        "summary": "Water at 97%",
        "detail": "The plant is definitely dying",
    },
    {
        "level": "warning",
        "title": "Pressure",
        "summary": "Water pressure crashing",
        "detail": "Tidal waves incoming",
    },
]


class AlertRow(BoxLayout):
    '''
    Collapsible alert row widget used to display information about alerts.
    Expands Kivy's BoxLayout - it is collapsed into a summary by default and can be expanded for additional information

    Attributes
    ----------
    alert (dict): Dictionary containing alert data with keys such as
        "title", "summary", "detail", and "level"
    expanded (BooleanProperty): Indicates whether the row is expanded
    COLLAPSED_H (int): Height of the row when collapsed
    EXPANDED_H (int): Height of the row when expanded
    _detail (Label): Label containing the detailed alert text
    _chevron (Label): Indicator showing expand/collapse state

    Methods
    -------
    _redraw_dot(widget, pos, clr): Redraws the severity indicator dot
    _on_touch(widget, touch): Handles touch input and triggers toggle
    toggle(): Expands or collapses the row with animation
    _refresh_parent(): Forces parent layout update during animations
    '''
    expanded = BooleanProperty(False)

    COLLAPSED_H = dp(48)
    EXPANDED_H = dp(106)

    def __init__(self, alert, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
        self.alert = alert
        self.height = self.COLLAPSED_H

        # Defaults to white if status is 'all clear' or 
        # anything other than critical/warning
        if alert["level"] == "critical":
            clr = ALERT_CRIT
        elif alert["level"] == "warning":
            clr = ALERT_WARN
        else:
            clr = (1, 1, 1, 1)  # Pure White for 'all clear'

        # Summary row
        row = BoxLayout(
            size_hint_y=None,
            height=self.COLLAPSED_H,
            padding=[dp(12), 0],
            spacing=dp(10),
        )

        dot_wrap = BoxLayout(size_hint=(None, None), size=(dp(20), dp(48)))
        dot = Widget(
            size_hint=(None, None),
            size=(dp(10), dp(10)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        with dot.canvas:
            Color(*clr)
            Ellipse(pos=dot.pos, size=dot.size)
        dot.bind(pos=lambda w, p: (w.canvas.clear(),
                                   self._redraw_dot(w, p, clr)))
        dot_wrap.add_widget(dot)
        row.add_widget(dot_wrap)

        text_col = BoxLayout(orientation="vertical", spacing=dp(2))
        title_lbl = make_label(
            alert["title"],
            font_size=sp(12),
            color=NEUTRAL,
            bold=True,
            height=dp(18),
            shorten=True,
            shorten_from="right",
        )
        summary_lbl = make_label(
            alert["summary"],
            font_size=sp(10),
            color=DIM,
            height=dp(16),
            shorten=True,
            shorten_from="right",
        )
        text_col.add_widget(title_lbl)
        text_col.add_widget(summary_lbl)
        row.add_widget(text_col)

        self._chevron = make_label(
            "›",
            font_size=sp(18),
            color=DIM,
            halign="center",
            size_hint=(None, 1),
            width=dp(24),
        )
        row.add_widget(self._chevron)
        row.bind(on_touch_down=self._on_touch)
        self.add_widget(row)

        # Detail section
        self._detail = make_label(
            alert["detail"],
            font_size=sp(11),
            color=DIM,
            halign="left",
            valign="top",
            size_hint_y=None,
            height=0,
            opacity=0,
            padding=(dp(12), dp(4)),
        )
        self.add_widget(self._detail)

        # Bottom separator
        sep = Widget(size_hint_y=None, height=dp(1))
        with sep.canvas:
            Color(*BORDER)
            rect = Rectangle(pos=sep.pos, size=sep.size)
        sep.bind(
            pos=lambda w, p: setattr(rect, "pos", p),
            size=lambda w, s: setattr(rect, "size", s),
        )
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
        detail_h = (self.EXPANDED_H - self.COLLAPSED_H
                    - dp(1))if self.expanded else 0
        self._chevron.text = "▾" if self.expanded else "›"

        anim = Animation(height=target_h, duration=0.22, t="out_cubic")
        anim.bind(on_progress=lambda *args: self._refresh_parent())
        anim.start(self)
        Animation(
            height=detail_h, opacity=int(self.expanded),
            duration=0.22, t="out_cubic"
        ).start(self._detail)

    def _refresh_parent(self):
        if self.parent:
            self.parent.do_layout()


class AlertsPanel(BoxLayout):
    '''
    Collapsible panel that displats a list of alert rows with a header
    Extends Kivy's BoxLayout to provide a container tfor multiple AlertRow components

    Attributes
    ----------
    expanded (BooleanProperty): Indicates whether the panel is expanded
    HEADER_H (int): Fixed height of the header section
    _alerts (list): List of alert dictionaries used to populate rows
    _rows_box (BoxLayout): Container holding AlertRow widgets
    _badge (Label): Label displaying the number of alerts
    _chev (Label): Chevron indicator for expand/collapse state

    Methods
    -------
    _upd_hdr(widget, *args): Updates the header background position and size
    _upd_bg(widget, *args): Updates the panel background and border
    _badge_text(): Returns formatted text showing number of alerts
    _on_header_touch(widget, touch): Handles header tap to toggle panel
    _update_height(*args): Adjusts panel height based on expansion state
    toggle(): Expands or collapses the panel and updates layout
    update_alerts(alert_dicts): Updates the alert list and refreshes UI
    _render_rows(): Creates AlertRow widgets from alert data
    '''
    expanded = BooleanProperty(True)
    HEADER_H = dp(36)

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)

        self._alerts = list(SAMPLE_ALERTS)

        with self.canvas.before:
            Color(*CARD_BG)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[RADIUS_MD]
            )
            Color(*BORDER)
            self._border = Line(
                rounded_rectangle=[*self.pos, *self.size,
                                   float(RADIUS_MD)], width=1.0
            )
        self.bind(pos=self._upd_bg, size=self._upd_bg)

        # Header
        header = BoxLayout(
            size_hint_y=None,
            height=self.HEADER_H,
            padding=[dp(14), 0, dp(12), 0],
            spacing=dp(8),
        )
        with header.canvas.before:
            Color(*SURFACE)
            self._hdr_rect = RoundedRectangle(
                pos=header.pos,
                size=header.size,
                radius=[RADIUS_MD, RADIUS_MD, 0, 0],
            )
        header.bind(pos=self._upd_hdr, size=self._upd_hdr)
        header.bind(on_touch_down=self._on_header_touch)

        header.add_widget(
            make_label(
                "ALERTS",
                font_size=sp(11),
                color=NEUTRAL,
                bold=True,
                halign="left",
                size_hint=(None, 1),
                width=dp(72),
            )
        )

        badge_pill = BoxLayout(
            size_hint=(None, None), size=(dp(78), dp(20)), padding=[dp(10), 0]
        )
        with badge_pill.canvas.before:
            Color(*with_alpha((1, 1, 1, 1), 0.03))
            badge_pill._bg = RoundedRectangle(
                pos=badge_pill.pos, size=badge_pill.size, radius=[RADIUS_SM]
            )
            Color(*with_alpha(BORDER, 1.0))
            badge_pill._bd = Line(
                rounded_rectangle=[*badge_pill.pos, *badge_pill.size,
                                   float(RADIUS_SM)],
                width=1.0,
            )
        badge_pill.bind(
            pos=lambda w, p: (
                setattr(w._bg, "pos", p),
                setattr(
                    w._bd,
                    "rounded_rectangle",
                    [p[0], p[1], w.width, w.height, float(RADIUS_SM)],
                ),
            ),
            size=lambda w, s: (
                setattr(w._bg, "size", s),
                setattr(
                    w._bd, "rounded_rectangle",
                    [w.x, w.y, s[0], s[1], float(RADIUS_SM)]
                ),
            ),
        )

        self._badge = make_label(
            self._badge_text(),
            font_size=sp(10),
            color=DIM,
            bold=True,
            halign="center",
            size_hint=(1, 1),
        )
        badge_pill.add_widget(self._badge)
        header.add_widget(badge_pill)
        header.add_widget(Widget())

        self._chev = make_label(
            "▾",
            font_size=sp(18),
            color=DIM,
            halign="right",
            size_hint=(None, 1),
            width=dp(24),
        )
        header.add_widget(self._chev)
        self.add_widget(header)

        self._rows_box = BoxLayout(orientation="vertical", size_hint_y=None)
        self._rows_box.bind(minimum_height=self._rows_box.setter("height"))
        self.add_widget(self._rows_box)
        self.update_alerts(self._alerts)
        self._rows_box.bind(height=lambda *_: self._update_height())

    def _upd_hdr(self, w, *_):
        self._hdr_rect.pos = w.pos
        self._hdr_rect.size = w.size

    def _upd_bg(self, w, *_):
        self._bg.pos = w.pos
        self._bg.size = w.size
        self._border.rounded_rectangle = [w.x, w.y, w.width,
                                          w.height, float(RADIUS_MD)]

    def _badge_text(self):
        n = len(self._alerts)
        return f"{n} alert" if n == 1 else f"{n} alerts"

    def _on_header_touch(self, widget, touch):
        if widget.collide_point(*touch.pos):
            self.toggle()
            return True

    def _update_height(self, *args):
        rows_h = self._rows_box.height if self.expanded else 0
        self.height = self.HEADER_H + rows_h
        if self.parent:
            self.parent.do_layout()

    def toggle(self):
        self.expanded = not self.expanded
        self._chev.text = "▾" if self.expanded else "▸"
        # Detach rows so layout shrinks when collapsed
        if self.expanded and not self._rows_box.children:
            self._render_rows()
        elif not self.expanded and self._rows_box.children:
            self._rows_box.clear_widgets()
        self._update_height()
        if self.parent:
            self.parent.do_layout()

    def update_alerts(self, alert_dicts):
        self._alerts = list(alert_dicts)
        self._badge.text = self._badge_text()
        if self.expanded:
            self._render_rows()
        self._update_height()

    def _render_rows(self):
        self._rows_box.clear_widgets()
        for alert in self._alerts:
            self._rows_box.add_widget(AlertRow(alert))


# Full-screen modal graph
class GraphOverlay(FloatLayout):
    '''
    Full-screen overlay widget that displays an interactive time-series graph for a selected metric, with optional filtering
    Extends Kivy's FloatLayout

    Parameters
    ----------
    title (str): Name of the metric being displayed
    unit (str): Unit of measurement for the data values
    site (str): Name of the data site
    timestamps (list): List of timestamp strings corresponding to values
    values (list): List of numerical values to plot
    stat_index (int): Index identifying the metric

    Attributes
    ----------
    _title (str): Graph title
    _unit (str): Measurement unit
    _site (str): Site name
    _site_key (str): Lowercase site identifier
    _stat_index (int): Dataset index for queries
    _timestamps (list): Current timestamps displayed
    _values (list): Current values displayed
    _panel (BoxLayout): Main container for graph UI
    _graph (Widget): Canvas area for drawing the graph
    _info_lbl (Label): Displays summary statistics (min, max, count)
    _from_input (TextInput): Start date filter input (researcher mode)
    _to_input (TextInput): End date filter input (researcher mode)
    _filter_err (ErrorLabel): Displays filtering validation errors

    Methods
    -------
    _build_researcher_ui(panel): Adds filtering UI for researcher users
    _apply_filter(*args): Validates and applies date filtering to dataset
    _draw_small_btn(btn, *args): Draws styled button for filter controls
    _upd_panel(widget, *args): Updates panel position, size, and styling
    _redraw_dot(widget, pos, clr): Redraws legend indicator dots
    _scrim_touch(widget, touch): Dismisses overlay when clicking outside panel
    _dismiss(): Removes overlay from the window
    _rolling_avg(values, window): Computes rolling average of values
    _draw_graph(*args): Renders the graph, axes, labels, and data lines
    '''
    AVG_WINDOW = 20
    _COMPARE_COLORS = [(1.0, 0.27, 0.27, 1), (1.0, 0.85, 0.20, 1)]

    def __init__(self, title, unit, site, timestamps,
                 values, stat_index=0, **kwargs):
        kwargs.setdefault("size", Window.size)
        kwargs.setdefault("pos", (0, 0))
        super().__init__(**kwargs)

        self._title = title
        self._unit = unit
        self._site = site
        self._site_key = site.lower()
        self._stat_index = stat_index
        self._timestamps = timestamps
        self._values = values
        self._compare_sites = {}

        is_researcher = (
            getattr(MDApp.get_running_app(), "user_role",
                    "Farmer") == "Researcher"
        )

        Window.bind(size=lambda _, s: setattr(self, "size", s))

        scrim = Widget(size=self.size, pos=self.pos)
        with scrim.canvas:
            Color(0, 0, 0, 0.72)
            self._scrim_rect = Rectangle(pos=scrim.pos, size=scrim.size)
        self.bind(
            pos=lambda _, v: (
                setattr(scrim, "pos", v),
                setattr(self._scrim_rect, "pos", v),
            ),
            size=lambda _, v: (
                setattr(scrim, "size", v),
                setattr(self._scrim_rect, "size", v),
            ),
        )
        scrim.bind(on_touch_down=self._scrim_touch)
        self.add_widget(scrim)

        pw = Window.width * 0.94
        ph = Window.height * (0.82 if is_researcher else 0.72)
        panel = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(pw, ph),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[dp(14), dp(12)],
            spacing=dp(8),
        )
        self._panel = panel
        with panel.canvas.before:
            r = float(RADIUS_LG)
            Color(*SHADOW_CLR)
            if BoxShadow is not None:
                self._panel_shadow = BoxShadow(
                    pos=panel.pos,
                    size=panel.size,
                    offset=(0, -dp(12)),
                    blur_radius=dp(32),
                    spread_radius=(-dp(14), -dp(14)),
                    border_radius=(r, r, r, r),
                )
            else:
                self._panel_shadow = RoundedRectangle(
                    pos=(panel.x, panel.y - ELEV_Y),
                    size=(panel.width, panel.height + ELEV_Y),
                    radius=[r],
                )
            Color(*CARD_BG)
            self._panel_rect = RoundedRectangle(
                pos=panel.pos, size=panel.size, radius=[r]
            )
            Color(*BORDER)
            self._panel_border = Line(
                rounded_rectangle=[panel.x, panel.y,
                                   panel.width, panel.height, r],
                width=1.0,
            )
        panel.bind(pos=self._upd_panel, size=self._upd_panel)

        # Header row
        hdr = BoxLayout(size_hint_y=None, height=dp(36))
        hdr.add_widget(
            make_label(
                f"{title.upper()}  /  {site.upper()}",
                font_size=sp(12),
                color=NEUTRAL,
                bold=True,
                halign="left",
                shorten=True,
                shorten_from="right",
                size_hint=(1, 1),
            )
        )
        close_btn = Button(
            text="X",
            font_name=FONT_NAME,
            font_size=sp(14),
            color=DIM,
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            background_normal="",
            background_color=(0, 0, 0, 0),
        )
        close_btn.bind(on_release=lambda _: self._dismiss())
        hdr.add_widget(close_btn)
        panel.add_widget(hdr)

        self._info_lbl = make_label(
            "Loading...", font_size=sp(10), color=DIM,
            halign="left", height=dp(18)
        )
        panel.add_widget(self._info_lbl)

        # Graph canvas
        self._graph = Widget(size_hint=(1, 1))
        self._graph.bind(pos=self._draw_graph, size=self._draw_graph)
        panel.add_widget(self._graph)

        # Legend
        legend = BoxLayout(
            size_hint_y=None, height=dp(20), spacing=dp(16), padding=[dp(4), 0]
        )
        for clr, lbl_text in [
            (ACCENT, "Value"),
            (ACCENT2, f"{self.AVG_WINDOW}-pt avg"),
        ]:
            dot = Widget(size_hint=(None, 1), width=dp(12))
            with dot.canvas:
                Color(*clr)
                Ellipse(pos=(0, 0), size=(dp(8), dp(8)))
            dot.bind(pos=lambda w, p, c=clr: self._redraw_dot(w, p, c))
            legend.add_widget(dot)
            legend.add_widget(
                Label(
                    text=lbl_text,
                    font_size=sp(9),
                    color=DIM,
                    halign="left",
                    size_hint_x=None,
                    width=dp(70),
                )
            )
        legend.add_widget(Widget())
        panel.add_widget(legend)

        if is_researcher:
            self._build_researcher_ui(panel)

        self.add_widget(panel)

        Clock.schedule_once(self._draw_graph, 0.1)

    def _build_researcher_ui(self, panel):  # additional UI for researchers
        filter_row = BoxLayout(
            orientation="horizontal", size_hint_y=None,
            height=dp(32), spacing=dp(6)
        )
        filter_row.add_widget(
            Label(
                text="From", font_size=sp(10), color=DIM,
                size_hint_x=None, width=dp(30)
            )
        )
        self._from_input = TextInput(
            hint_text="YYYY-MM-DD",
            multiline=False,
            background_color=SURFACE,
            foreground_color=NEUTRAL,
            hint_text_color=DIM,
            cursor_color=ACCENT,
            font_size=sp(11),
            size_hint_x=1,
        )
        filter_row.add_widget(self._from_input)
        filter_row.add_widget(
            Label(
                text="To", font_size=sp(10), color=DIM,
                size_hint_x=None, width=dp(20)
            )
        )
        self._to_input = TextInput(
            hint_text="YYYY-MM-DD",
            multiline=False,
            background_color=SURFACE,
            foreground_color=NEUTRAL,
            hint_text_color=DIM,
            cursor_color=ACCENT,
            font_size=sp(11),
            size_hint_x=1,
        )
        filter_row.add_widget(self._to_input)
        apply_btn = Button(
            text="Apply",
            font_size=sp(11),
            color=NEUTRAL,
            bold=True,
            size_hint_x=None,
            width=dp(52),
            background_normal="",
            background_color=(0, 0, 0, 0),
        )
        apply_btn.bind(on_release=self._apply_filter)
        apply_btn.bind(pos=self._draw_small_btn, size=self._draw_small_btn)
        filter_row.add_widget(apply_btn)
        panel.add_widget(filter_row)

        self._filter_err = ErrorLabel()
        panel.add_widget(self._filter_err)

        compare_row = BoxLayout( # buttons to add/remove other sites for comparison
            orientation="horizontal", size_hint_y=None,
            height=dp(32), spacing=dp(6)
        )
        compare_row.add_widget(
            Label(
                text="Compare", font_size=sp(10), color=DIM,
                size_hint_x=None, width=dp(58)
            )
        )
        self._compare_btns = {} # site_key: btn for access in toggle and draw
        for key in ("maize", "brassica", "orchard"):
            btn = Button(
                text=key.capitalize(),
                font_name=FONT_NAME,
                font_size=sp(11),
                color=NEUTRAL,
                size_hint_x=1,
                background_normal="",
                background_color=(0, 0, 0, 0),
            )
            btn._site_key = key
            if key != self._site_key:
                btn.bind(on_release=lambda b, k=key: self._toggle_compare_site(k))
            btn.bind(pos=self._draw_compare_btn, size=self._draw_compare_btn)
            self._compare_btns[key] = btn
            compare_row.add_widget(btn)
        panel.add_widget(compare_row)

    def _toggle_compare_site(self, site_key): # add/remove a site to compare against
        bridge = MDApp.get_running_app().bridge
        start = self._from_input.text.strip() or None
        end = self._to_input.text.strip() or None
        if site_key in self._compare_sites:
            del self._compare_sites[site_key]
        else:
            ts, vs = bridge.get_history(
                site_key, self._stat_index, start_date=start, end_date=end
            )
            if vs:
                self._compare_sites[site_key] = (ts, vs)
        for btn in self._compare_btns.values():
            self._draw_compare_btn(btn) # accent fill when active (current site or toggled on), grey outline when inactive
        self._draw_graph()

    def _draw_compare_btn(self, btn, *_):
        active = (
            btn._site_key == self._site_key or
            btn._site_key in self._compare_sites
        )
        btn.canvas.before.clear()
        with btn.canvas.before:
            if active:
                Color(*with_alpha(ACCENT, 0.15))
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(6)])
                Color(*with_alpha(ACCENT, 0.5))
            else:
                Color(*OVERLAY_SUBTLE)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(6)])
                Color(*BORDER)
            Line(
                rounded_rectangle=[btn.x, btn.y, btn.width, btn.height, dp(6)],
                width=1,
            )

    def _apply_filter(self, *_):
        start = self._from_input.text.strip() or None
        end = self._to_input.text.strip() or None
        bridge = MDApp.get_running_app().bridge
        sim_date = bridge.timestamp.date()

        for val, label in ((start, "From"), (end, "To")):
            if val:
                try:
                    d = datetime.strptime(val, "%Y-%m-%d").date()
                    if d > sim_date:
                        self._filter_err.show(f"{label} date is in the future")
                        return
                    if d < DATASET_START:
                        self._filter_err.show(f"{label} date is before the dataset")
                        return
                except ValueError:
                    self._filter_err.show(f"{label} date must be YYYY-MM-DD")
                    return

        self._filter_err.hide()
        timestamps, values = bridge.get_history(
            self._site_key, self._stat_index, start_date=start, end_date=end
        )
        if not values:
            return
        self._timestamps = timestamps
        self._values = values
        for sk in list(self._compare_sites): # refresh compare sites with same date filter, remove if no data in range
            ts, vs = bridge.get_history(
                sk, self._stat_index, start_date=start, end_date=end
            )
            if vs:
                self._compare_sites[sk] = (ts, vs)
        self._draw_graph()

    def _draw_small_btn(self, btn, *_):
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(*CARD_BG)
            RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(6)])
            Color(*BORDER)
            Line(
                rounded_rectangle=[btn.x, btn.y, btn.width,
                                   btn.height, dp(6)], width=1
            )

    def _upd_panel(self, w, *_):
        self._panel_rect.pos = w.pos
        self._panel_rect.size = w.size
        if hasattr(self, "_panel_shadow"):
            self._panel_shadow.pos = (
                w.pos if BoxShadow is not None else (w.x, w.y - ELEV_Y)
            )
            self._panel_shadow.size = (
                w.size if BoxShadow is not None else (w.width,
                                                      w.height + ELEV_Y)
            )
        if hasattr(self, "_panel_border"):
            self._panel_border.rounded_rectangle = [
                w.x,
                w.y,
                w.width,
                w.height,
                float(RADIUS_LG),
            ]

    def _redraw_dot(self, w, pos, clr):
        w.canvas.clear()
        with w.canvas:
            Color(*clr)
            Ellipse(pos=(pos[0], pos[1] + dp(2)), size=(dp(8), dp(8)))

    # Dismiss when tapping outside the panel
    def _scrim_touch(self, widget, touch):
        if getattr(self, "_panel", None) and self._panel.collide_point(*touch.pos):
            return False
        self._dismiss()
        return True

    def _dismiss(self):
        if hasattr(self, "_win_size_cb"):
            Window.unbind(size=self._win_size_cb)
        Window.remove_widget(self)

    @staticmethod
    def _rolling_avg(values, window):
        out = []
        for i in range(len(values)):
            start = max(0, i - window + 1)
            chunk = values[start: i + 1]
            out.append(sum(chunk) / len(chunk))
        return out

    def _draw_graph(self, *_):
        w = self._graph
        w.canvas.clear()
        for child in list(w.children):
            w.remove_widget(child)

        values = self._values
        timestamps = self._timestamps

        if not values:
            return

        all_vals = list(values)
        for _, vs in self._compare_sites.values():
            all_vals.extend(vs)
        v_min = min(all_vals)
        v_max = max(all_vals)
        v_range = v_max - v_min if v_max != v_min else 1.0

        self._info_lbl.text = (
            f"{self._unit}  ·  min {v_min:.1f}  max {v_max:.1f}  ({len(values)} pts)"
        )

        if len(values) < 2:
            return

        # Layout margins
        ml = dp(48)
        mr = dp(10)
        mt = dp(10)
        mb = dp(28)

        gx = w.x + ml
        gy = w.y + mb
        gw = w.width - ml - mr
        gh = w.height - mb - mt

        if gw <= 0 or gh <= 0:
            return

        avg_values = self._rolling_avg(values, self.AVG_WINDOW)

        def to_px(v):
            return gy + ((v - v_min) / v_range) * gh

        def to_x(i, total):
            return gx + (i / (total - 1)) * gw

        with w.canvas:
            # Grid lines
            N_GRID = 5
            for k in range(N_GRID + 1):
                py = gy + (k / N_GRID) * gh
                Color(*BORDER)
                Line(points=[gx, py, gx + gw, py], width=dp(0.6))

            # X-axis baseline
            Color(*BORDER)
            Line(points=[gx, gy, gx + gw, gy], width=dp(0.8))

            # Value line
            Color(*ACCENT)
            pts = []
            for i, v in enumerate(values):
                pts += [to_x(i, len(values)), to_px(v)]
            Line(points=pts, width=dp(1.2))

            # Average line
            Color(*ACCENT2)
            avg_pts = []
            for i, v in enumerate(avg_values):
                avg_pts += [to_x(i, len(avg_values)), to_px(v)]
            Line(points=avg_pts, width=dp(1.5))

            # Endpoint dot
            Color(*ACCENT)
            Ellipse(
                pos=(to_x(len(values) - 1, len(values)) - dp(4), to_px(values[-1]) - dp(4)),
                size=(dp(8), dp(8)),
            )

            # compare site lines
            for ci, (_, (_, series_vals)) in enumerate(self._compare_sites.items()):
                if len(series_vals) < 2:
                    continue
                Color(*self._COMPARE_COLORS[ci % len(self._COMPARE_COLORS)])
                cpts = []
                for i, v in enumerate(series_vals):
                    cpts += [to_x(i, len(series_vals)), to_px(v)]
                Line(points=cpts, width=dp(1.2))

        # Y labels
        N_GRID = 5
        for k in range(N_GRID + 1):
            frac = k / N_GRID
            y_val = v_min + frac * v_range
            py = gy + frac * gh
            lbl = Label(
                text=f"{y_val:.1f}",
                font_name=FONT_NAME,
                font_size=sp(8),
                color=DIM,
                size_hint=(None, None),
                size=(dp(42), dp(14)),
                halign="right",
                valign="middle",
            )
            lbl.text_size = lbl.size
            lbl.pos = (w.x + ml - dp(46), py - dp(7))
            w.add_widget(lbl)

        # X labels
        n = len(timestamps)
        x_indices = [int(i * (n - 1) / 4) for i in range(5)]
        for idx in x_indices:
            px = to_x(idx, n)
            parts = timestamps[idx].split("-")
            short = f"{parts[1]}/{parts[0][2:]}" if len(parts) == 3 else timestamps[idx]
            lbl = Label(
                text=short,
                font_name=FONT_NAME,
                font_size=sp(7),
                color=DIM,
                size_hint=(None, None),
                size=(dp(36), dp(14)),
                halign="center",
                valign="top",
            )
            lbl.text_size = lbl.size
            lbl.pos = (px - dp(18), w.y + dp(2))
            w.add_widget(lbl)


# Site tab button
class SiteButton(ButtonBehavior, BoxLayout):
    '''
    UI button representing a site, combining an icon and label
    Extends Kivy's ButtonBehavior and BoxLayout

    Parameters
    ----------
    site_key(str): Unique identifier for the site
    icon_name(str): Name of the icon to display
    label_text(str): Text label shown below the icon

    Attributes
    ----------
    site_key (str): Identifier associated with the button
    icon_widget (MDIcon): Icon displayed at the top
    label_widget (Label): Text label displayed below the icon
    _bg_rect (RoundedRectangle): Background highlight rectangle
    _ind_rect (RoundedRectangle): Bottom indicator (underline)
    _bg_clr (Color): Background colour instruction
    _ind_clr (Color): Indicator colour instruction

    Methods
    -------
    _upd(*args): Updates background and indicator positions/sizes
    set_active(active): Updates styling based on whether the button is active
    '''
    def __init__(self, site_key, icon_name, label_text, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("spacing", dp(3))
        kwargs.setdefault("padding", [dp(8), dp(8), dp(8), dp(4)])
        super().__init__(**kwargs)
        self.site_key = site_key

        self.icon_widget = MDIcon(
            icon=icon_name,
            font_size=sp(18),
            theme_text_color="Custom",
            text_color=DIM,
            halign="center",
            valign="middle",
            size_hint=(1, None),
            height=dp(22),
        )
        self.label_widget = make_label(
            label_text, font_size=sp(18), color=DIM,
            halign="center", height=dp(14)
        )

        self.add_widget(self.icon_widget)
        self.add_widget(self.label_widget)

        with self.canvas.before:
            self._bg_clr = Color(*with_alpha(ACCENT, 0.0))
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[RADIUS_SM]
            )
        with self.canvas.after:
            # Active underline (hidden by default)
            self._ind_clr = Color(*with_alpha(ACCENT, 0.0))
            self._ind_rect = RoundedRectangle(
                pos=(self.x, self.y),
                size=(self.width, dp(3)), radius=[dp(1.5)]
            )
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._ind_rect.pos = (self.x, self.y)
        self._ind_rect.size = (self.width, dp(3))

    def set_active(self, active):
        if active:
            self._bg_clr.rgba = with_alpha(ACCENT, 0.08)
            self._ind_clr.rgba = with_alpha(ACCENT, 1.0)
            self.icon_widget.text_color = ACCENT
            self.label_widget.color = NEUTRAL
            self.label_widget.bold = True
        else:
            self._bg_clr.rgba = with_alpha(ACCENT, 0.0)
            self._ind_clr.rgba = with_alpha(ACCENT, 0.0)
            self.icon_widget.text_color = DIM
            self.label_widget.color = DIM
            self.label_widget.bold = False


class SiteSelectorBar(BoxLayout):
    '''
    Horizontal navigation bar for selecting different sites.
    Extends Kivy's BoxLayout to create a row of SiteButton components

    Attributes
    ----------
    SITES (list): List of tuples defining available sites in the form
        (site_key, icon_name, label_text)
    on_select (callable): Callback triggered when a site is selected,
        receiving the selected site_key
    _btns (dict): Dictionary mapping site keys to SiteButton instances
    _bg (Rectangle): Background rectangle of the bar
    _line (Line): Bottom border line

    Methods
    -------
    _upd(widget, *args): Updates background and border positions/sizes
    _on_btn(button): Handles button press events and triggers selection callback
    set_active(site_key): Updates active state styling for all buttons

    '''
    SITES = [
        ("maize", "leaf-circle-outline", "Maize"),
        ("brassica", "sprout-outline", "Brassica"),
        ("orchard", "tree-outline", "Orchard"),
    ]

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(58))
        kwargs.setdefault("spacing", dp(0))
        kwargs.setdefault("padding", [dp(12), dp(0), dp(12), dp(0)])
        super().__init__(**kwargs)

        self.on_select = None
        self._btns = {}

        with self.canvas.before:
            Color(*SURFACE)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(*BORDER)
            self._line = Line(points=[self.x, self.y,
                                      self.right, self.y], width=1.0)
        self.bind(pos=self._upd, size=self._upd)

        for key, icon_name, label in self.SITES:
            btn = SiteButton(site_key=key, icon_name=icon_name,
                             label_text=label)
            btn.bind(on_release=self._on_btn)
            self._btns[key] = btn
            self.add_widget(btn)

        self.set_active("maize")

    def _upd(self, w, *_):
        self._bg.pos = w.pos
        self._bg.size = w.size
        self._line.points = [w.x, w.y, w.right, w.y]

    def _on_btn(self, btn):
        if self.on_select:
            self.on_select(btn.site_key)
        self.set_active(btn.site_key)

    def set_active(self, site_key):
        for key, btn in self._btns.items():
            btn.set_active(key == site_key)


# Bottom Navigation Bar
class NavBar(BoxLayout):
    '''
    Bottom navigation bar that controls screen switching
    Extends Kivy's BoxLayout to create a widget for navigating between three screens (Dashboard, Scan and Profile) using a ScreenManager
    Visually highlights the currently active tab

    Properties
    ----------
    screen_manager (ScreenManager): Kivy ScreenManager instance used to switch between screens

    Attributes
    ----------
    sm (ScreenManager): Reference to the app's screen manager
    _btns (dict): Mapping of screen names to navigation button widgets
    _bg (Rectangle): Background rectangle of the navigation bar
    _border (Rectangle): Top border line of the navigation bar

    Methods
    -------
    _upd(*args): Updates the background and border positions/sizes when
        the widget is resized or moved
    _make_btn(name, icon_name, label): Creates a navigation button with icon
        and label
    _nav(widget, touch): Handles navigation logic and screen transitions
        when a button is tapped
    _set_active(name): Updates visual state of navigation buttons
    '''
    def __init__(self, screen_manager, **kwargs):
        # 1. FORCE size_hint_x to 1 so it fills the parent width automatically
        kwargs.setdefault("size_hint", (1, None))
        kwargs.setdefault("height", dp(62))
        kwargs.setdefault("spacing", 0)
        super().__init__(**kwargs)
        self.sm = screen_manager

        with self.canvas.before:
            Color(*BAR_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(*BORDER)
            self._border = Rectangle(pos=self.pos, size=(self.width, dp(1)))
        self.bind(pos=self._upd, size=self._upd)

        self._btns = {}
        items = [
            ("dashboard", "view-dashboard", "Dashboard"),
            ("scan", "qrcode-scan", "Scan"),
            ("profile", "account-circle", "Profile"),
        ]
        for name, icon, label in items:
            btn = self._make_btn(name, icon, label)
            # 2. Divide space equally (33.3% each)
            btn.size_hint_x = 1.0 / len(items)
            self._btns[name] = btn
            self.add_widget(btn)

        self._set_active("dashboard")

    def _upd(self, *args):
        """Update the background and border
        position/size when the widget changes."""
        if hasattr(self, "_bg"):
            self._bg.pos = self.pos
            self._bg.size = self.size
        if hasattr(self, "_border"):
            # Keeps the 1dp border at the very top of the bar
            self._border.pos = (self.x, self.y + self.height - dp(1))
            self._border.size = (self.width, dp(1))

    def _make_btn(self, name, icon_name, label):
        # Ensure the button container itself fills its allocated width
        btn = BoxLayout(
            orientation="vertical", spacing=0,
            padding=[0, dp(8)], size_hint_x=1
        )
        btn.name = name

        btn._icon_lbl = MDIcon(
            icon=icon_name,
            font_size=sp(24),
            theme_text_color="Custom",
            text_color=DIM,
            # FIX STARTS HERE
            halign="center",  # Horizontal alignment
            valign="middle",  # Vertical alignment
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
            # FIX ENDS HERE
        )

        btn._text_lbl = Label(
            text=label,
            font_size=sp(10),
            color=DIM,
            halign="center",
            valign="top",
            size_hint=(1, 0.4),
        )

        # 3. FIX: Bind text_size to width so halign='center' actually works
        btn._text_lbl.bind(
            size=lambda inst, val: setattr(inst, "text_size", (val[0], None))
        )

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
            self.sm.transition = SlideTransition(direction=direction,
                                                 duration=0.25)
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
    '''
    Applies a solid background colour to a Kivy widget

    Properties
    ----------
    widget(Widget): The Kivy widget to apply the background to
    '''
    with widget.canvas.before:
        Color(*BG)
        rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(
        pos=lambda w, p: setattr(rect, "pos", p),
        size=lambda w, s: setattr(rect, "size", s),
    )


class SignInScreen(Screen):
    '''
    Authetication screen that manages the sign-in and sign-up panels
    Extends Kivy's Screen to provide a container for user authentication panels

    Properties
    ----------
    on_authenticated(callable): Callback function triggered when authentication succeeds

    Attributes
    ----------
    _on_authenticated (callable): Stored authentication success callback
    panel_holder (BoxLayout): Container that holds the active panel
    current_panel (str): Tracks whether 'login' or 'signup' is displayed

    Methods
    -------
    _show_panel(name): Switches between login and signup panels
    '''
    def __init__(self, on_authenticated, **kwargs):
        super().__init__(**kwargs)
        make_bg(self)
        self._on_authenticated = on_authenticated
        root = FloatLayout()

        card = RoundedCard(
            size_hint=(None, None), pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        def _resize_card(*_):
            # Keeps auth card readable at any window size
            w, h = Window.size
            cw = min(dp(520), w - dp(64))
            ch = min(dp(740), h - dp(80))
            card.size = (max(dp(320), cw), max(dp(500), ch))

        Window.bind(size=lambda *_: _resize_card())
        Clock.schedule_once(lambda *_: _resize_card())

        inner = BoxLayout(
            orientation="vertical",
            padding=[dp(28), dp(24)],
            spacing=dp(8),
            size_hint=(1, 1),
        )
        card.bind(
            size=lambda w, s: setattr(inner, "size", s),
            pos=lambda w, p: setattr(inner, "pos", p),
        )

        self.panel_holder = BoxLayout(orientation="vertical", size_hint=(1, 1))
        self._current_panel = None
        self._show_panel("login")

        inner.add_widget(self.panel_holder)
        card.add_widget(inner)
        root.add_widget(card)
        self.add_widget(root)

    def _show_panel(self, name):
        self.panel_holder.clear_widgets()
        if name == "login":
            panel = SignInPanel(
                switch_cb=self._show_panel, success_cb=self._on_authenticated
            )
        else:
            panel = SignUpPanel(
                switch_cb=self._show_panel, success_cb=self._on_authenticated
            )
        self.panel_holder.add_widget(panel)
        self._current_panel = name


class DashboardScreen(Screen):
    '''
    Main dashboard screen displaying real-time environmental data
    Extends Kivy's Screen

    Attributes
    ----------
    _active_site (str): Currently selected site
    _latest (dict): Cached latest data for all supported sites
    _site_bar (SiteSelectorBar): UI component for switching sites
    _grid (GridLayout): Container holding statistical data cards
    _cards (list): List of DataCard widgets displaying metrics
    alerts_panel (AlertsPanel): Displays system alerts for the site
    _body_bg (Rectangle): Background rectangle for scrollable content

    Methods
    -------
     _show_graph(stat_index, stat_label, stat_unit):
        Opens a GraphOverlay for a selected statistic
    _on_site_selected(site_key):
        Handles switching between different agricultural sites
    _render(site):
        Updates all UI components with the latest site data
    on_bridge_tick(maize, brassica, orchard, timestamp):
        Receives real-time updates from the data bridge and refreshes UI
    _update_body_bg(instance, value):
        Keeps the scrollable body background aligned with layout changes
    '''
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
        body = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(10),
            padding=[dp(12), dp(14), dp(12), dp(10)],
        )
        body.bind(minimum_height=body.setter("height"))

        with body.canvas.before:
            from kivy.graphics import (
                Color,
                Rectangle,
            )  # Ensure these are imported at top of file

            Color(0.12, 0.14, 0.16, 1)  # This matches your dark theme
            self._body_bg = Rectangle(pos=body.pos, size=body.size)

        # This keeps the background size in sync with the body
        body.bind(pos=self._update_body_bg, size=self._update_body_bg)

        # 2 x 3 Data Cards — labels and units match bridge STAT_LABELS order:
        # [air_temp, humidity, leaf_wetness, light, vibration, pest_count]
        STAT_LABELS = [
            "Temperature",
            "Humidity",
            "Leaf Wetness",
            "Light",
            "Vibration",
            "Pest Count",
        ]
        STAT_UNITS = ["°C", "%", "", "lux", "", ""]

        self._grid = GridLayout(
            cols=2, rows=3, spacing=dp(12), size_hint_y=None, height=dp(330)
        )
        self._cards = []
        for i in range(6):
            card = DataCard(
                STAT_LABELS[i], "-", STAT_UNITS[i], "up", "",
                bg_color=list(CARD_BG)
            )
            # capture i in closure
            card.tap_callback = (
                lambda idx, lbl=STAT_LABELS[i], unit=STAT_UNITS[
                    i
                ]: lambda: self._show_graph(idx, lbl, unit)
            )(i)
            self._cards.append(card)
            self._grid.add_widget(card)
        body.add_widget(self._grid)

        # Expandable Location Map
        # locationmap = ExpandableLocationMap(size_hint_x=1)
        # body.add_widget(locationmap)

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
        bridge = MDApp.get_running_app().bridge
        timestamps, values = bridge.get_history(self._active_site, stat_index)

        if not values:
            return

        overlay = GraphOverlay(
            title=stat_label,
            unit=stat_unit,
            site=self._active_site,
            timestamps=timestamps,
            values=values,
            stat_index=stat_index,
        )
        Window.add_widget(overlay)

    def _on_site_selected(self, site_key):
        """Called when the user taps a site button;
        re-renders with cached data."""
        self._active_site = site_key
        data = self._latest.get(site_key)
        if data:
            self._render(data)

    # main.py inside class DashboardScreen
    def _render(self, site):
        stats = site["stats"]
        flags = site["flags"]
        deltas = site["deltas"]
        alerts = site["alerts"]

        for i, card in enumerate(self._cards):
            val = f"{stats[i]:.1f}" if stats[i] is not None else "-"
            
            # Ensure 'stable' is lowercase so DataArrow detects it
            direction = str(flags[i]).lower() 
                
            card.update(val, direction, deltas[i])
        
        self.alerts_panel.update_alerts(alerts)

    def on_bridge_tick(self, maize, brassica, orchard, timestamp):
        # Cache all three sites every tick
        self._latest["maize"] = maize
        self._latest["brassica"] = brassica
        self._latest["orchard"] = orchard

        # Render whichever site is currently selected
        self._render(self._latest[self._active_site])

        MDApp.get_running_app().header.update_time(timestamp)

    def _update_body_bg(self, instance, value):
        self._body_bg.pos = instance.pos
        self._body_bg.size = instance.size


class ScanScreen(Screen):
    '''
    Camera-based plant scanning screen that captures images, performs basic validation, and runs a model to detect plant type and health
    Screen provides a simple workflow: capture image -> validate image -> run ML prediciton -> display result

    Attributes
    ----------
    camera (Camera): Live camera feed used for image capture
    result_label (Label): Displays analysis status and results
    scan_btn (Button): Button used to trigger image capture

    Methods
    -------
    capture(instance): Disables UI and starts delayed capture process
    _do_capture(dt): Captures image from camera, saves it, validates it, and
        triggers analysis
    analyse(filename): Runs inference in a background thread to avoid blocking UI
    show_result(label, confidence): Displays prediction results and re-enables UI controls
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        make_bg(self)
        layout = BoxLayout(orientation="vertical",
                           padding=dp(24), spacing=dp(20))

        layout.add_widget(
            Label(
                text="Scan",
                font_size=sp(22),
                color=NEUTRAL,
                bold=True,
                size_hint=(1, None),
                height=dp(40),
            )
        )

        layout.add_widget(Label(
            text="Point camera at crop leaf and press Capture",
            font_size=sp(12), color=DIM, halign="center",
            size_hint=(1, None), height = dp(20)
        ))

        self.camera = Camera(play=True, index=0,
                             size_hint=(1, 1))  # 0 = rear camera

        layout.add_widget(self.camera)

        self.result_label = Label(
            text="",
            font_size=sp(14),
            color=NEUTRAL,
            halign="center",
            markup=True,
            size_hint=(1, None),
            height=dp(60)
        )

        layout.add_widget(self.result_label)

        self.scan_btn = Button(
            text="Capture", font_size=sp(14),
            height=dp(48),
            background_color=(*ACCENT[:3], 1),
            color=NEUTRAL,
            bold=True,
            size_hint=(1, None),
        )
        self.scan_btn.bind(on_press=self.capture)

        layout.add_widget(self.scan_btn)
        self.add_widget(layout)

    def capture(self, instance):
        self.scan_btn.disabled = True
        self.result_label.text = "Analysing plant..."
        Clock.schedule_once(self._do_capture, 2.0)
        

    def _do_capture(self, dt):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SAVE_DIR, f"crop_{timestamp}.png")
        self.camera.export_to_png(filename)
        check = PILImage.open(filename)
        check_arr = np.array(check)
        print(f"Saved PNG mean: {check_arr.mean():.2f}")
    
        if check_arr.mean() < 5.0:
            self.result_label.text = "Black image captured - please try again"
            self.scan_btn.disabled = False
            self.scan_btn.text = "Capture"
            return  # don't run inference on a black image
    
        self.analyse(filename)
    
    def analyse(self, filename):
        def do_inference():
            label, confidence = predict_image(filename)
            Clock.schedule_once(
                lambda dt: self.show_result(label, confidence), 0
            )
    
        threading.Thread(target=do_inference, daemon = True).start()

    def show_result(self, label, confidence):
        self.result_label.text =  (
            f"[b]{label}[/b]\n"
            f"Confidence: {confidence:.1f}%"
        )
        self.result_label.text_size = (self.result_label.width, None)
        self.scan_btn.disabled = False
        self.scan_btn.text = "Scan Again"

class ProfileScreen(Screen):
    '''
    User profile screen displaying account information

    Attributes
    -----------
    app (MDApp): Reference to the running application instance
    name_lbl (Label): Displays the user's full name
    user_lbl (Label): Displays the user's username handle
    _role_value_lbl (Label): Reference to the role value label in info cards

    Methods
    -------
    on_enter(*args): Refreshes displayed user information when the screen becomes active
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        make_bg(self)
        self.app = MDApp.get_running_app()

        layout = BoxLayout(orientation="vertical",
                           padding=dp(24), spacing=dp(16))

        layout.add_widget(
            Label(
                text="Profile",
                font_size=sp(22),
                color=NEUTRAL,
                bold=True,
                size_hint_y=None,
                height=dp(40),
            )
        )

        # Avatar circle (drawn via canvas)
        av_box = BoxLayout(size_hint_y=None, height=dp(100))
        av = Widget(size_hint=(None, None), size=(dp(80), dp(80)))

        def draw_av(*_):
            av.canvas.clear()
            with av.canvas:
                Color(*ACCENT)
                Ellipse(pos=av.pos, size=av.size)

        av.bind(pos=draw_av, size=draw_av)
        av_box.add_widget(Widget())  # spacer
        av_box.add_widget(av)
        av_box.add_widget(Widget())
        layout.add_widget(av_box)

        # NAME LABEL
        self.name_lbl = Label(
            text=self.app.user_fullname,  # Use app property
            font_size=sp(18),
            color=NEUTRAL,
            bold=True,
            size_hint_y=None,
            height=dp(30),
        )
        layout.add_widget(self.name_lbl)

        # USERNAME LABEL
        self.user_lbl = Label(
            text=f"@{self.app.user_username}",  # Use app property
            font_size=sp(12),
            color=DIM,
            size_hint_y=None,
            height=dp(24),
        )
        layout.add_widget(self.user_lbl)

        # Info cards
        self._role_value_lbl = None
        for label, value in [
            ("Role", self.app.user_role),
            ("Location", "Leeds, UK"),
            ("Devices", "7 connected"),
            ("Plan", "Pro"),
        ]:
            row = Card(
                orientation="horizontal",
                bg_color=list(CARD_BG),
                size_hint_y=None,
                height=dp(44),
                padding=[dp(14), 0],
            )
            row.add_widget(
                Label(text=label, font_size=sp(12), color=DIM, halign="left")
            )
            val_lbl = Label(text=value, font_size=sp(12),
                            color=NEUTRAL, halign="right")
            row.add_widget(val_lbl)
            layout.add_widget(row)
            if label == "Role":
                            self._role_value_lbl = val_lbl
        layout.add_widget(Widget())  # spacer pushes button to bottom
            
        sign_out_btn = Button(
            text="Sign Out",
            font_size=sp(14),
            bold=True,
            color=DOWN_CLR,
            background_normal="",
            background_color=(0, 0, 0, 0),
            size_hint=(1, None),
            height=dp(50),
        )

        self.add_widget(layout)

        def _draw_signout_btn(btn, *_):
            btn.canvas.before.clear()
            with btn.canvas.before:
                r = float(RADIUS_SM)
                fill = with_alpha(DOWN_CLR, 0.08) if btn.state == "down" else with_alpha(DOWN_CLR, 0.0)
                Color(*fill)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[r])
                Color(*with_alpha(DOWN_CLR, 0.45))
                Line(rounded_rectangle=[btn.x, btn.y, btn.width, btn.height, r], width=1.0)

        sign_out_btn.bind(pos=_draw_signout_btn, size=_draw_signout_btn, state=_draw_signout_btn)
        sign_out_btn.bind(on_release=lambda *_: MDApp.get_running_app().sign_out())
        layout.add_widget(sign_out_btn)

    def on_enter(self, *_):
        """Refresh labels whenever the screen is viewed"""
        self.name_lbl.text = self.app.user_fullname
        self.user_lbl.text = f"@{self.app.user_username}"
        if self._role_value_lbl:
            self._role_value_lbl.text = self.app.user_role


class DashboardHeader(BoxLayout):
    '''
    A top header displaying current date and time. 

    Attributes
    ----------
    date_lbl (Label): Displays the formatted current date
    time_lbl (Label): Displays the current time
    _bg (Rectangle): Background rectangle for styling the header

    Methods
    -------
    _upd(widget, *args): Updates the background position and size when layout changes

    update_time(dt_obj): Updates the displayed date and time based on a datetime object
    '''
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
            font_size=sp(9),
            color=DIM,
            halign="left",
            valign="top",
        )
        self.time_lbl = Label(
            text="00:00",
            font_size=sp(16),
            color=ACCENT,
            bold=True,
            halign="right",
            valign="middle",
            size_hint_x=0.4,
        )

        # 2. SETUP CANVAS
        with self.canvas.before:
            Color(*SURFACE)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        # 3. CONSTRUCT LAYOUT
        title_box = BoxLayout(orientation="vertical")
        ov = Label(
            text="Overview",
            font_size=sp(14),
            color=NEUTRAL,
            bold=True,
            halign="left",
            valign="bottom",
        )

        # Bind size AFTER labels are created
        ov.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.date_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.time_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))

        title_box.add_widget(ov)
        title_box.add_widget(self.date_lbl)

        self.add_widget(title_box)
        self.add_widget(self.time_lbl)

    def _upd(self, w, *_):
        self._bg.pos = w.pos
        self._bg.size = w.size

    def update_time(self, dt_obj):
        # Now these attributes are guaranteed to exist
        if self.date_lbl and self.time_lbl:
            self.date_lbl.text = dt_obj.strftime("%A, %d %B %Y")
            self.time_lbl.text = dt_obj.strftime("%H:%M")


# App Root
class DashboardApp(MDApp):
    '''
    Main application class that initialises the environmental monitoring system
    Extends Kivy's MDApp and handles:
    - User authentication state
    - Screen management
    - Live data bridge integration
    - Global UI componenets

    Attributes
    ----------
    user_fullname (str): Full name of the authenticated user
    user_username (str): Username of the authenticated user
    user_role (str): Role of the user (Farmer or Researcher)
    bridge (Bridge): Real-time data provider for environmental metrics
    sm (ScreenManager): Manages authentication screen flow
    _app_sm (ScreenManager): Manages main application screens
    _dashboard (DashboardScreen): Main dashboard screen instance
    _nav (NavBar): Bottom navigation bar for screen switching
    header (DashboardHeader): Top header displaying time/date

    Methods
    -------
    build():Constructs the application UI, initialises screens, and starts
        the data bridge
    _on_keyboard_down(instance, keyboard, keycode, text, modifiers): Handles global keyboard input events
    _on_login_success(user_info): Handles successful authentication, stores user data, and
        switches from login screen to main application interface

    '''
    user_fullname = StringProperty("Guest")
    user_username = StringProperty("guest.user")
    user_role = StringProperty("Farmer")

    def build(self):
        Window.bind(on_key_down=self._on_keyboard_down)
        self.title = "Environmental App"

        self._root = BoxLayout(orientation="vertical")

        self.sm = ScreenManager(transition=NoTransition())

        login_screen = SignInScreen(
            on_authenticated=self._on_login_success, name="login"
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

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 9:  # 9 is the 'Tab' key
            # This logic triggers Kivy's internal focus shift
            return False

    def _on_login_success(self, user_info):
        self.user_role = user_info["role"]
        self.user_fullname = user_info["fullname"]
        self.user_username = user_info["username"]

        self._root.clear_widgets()

        # Manually paint the root background dark
        with self._root.canvas.before:
            Color(0.039, 0.039, 0.039, 1)  # Match your BG variable
            self._bg_rect = Rectangle(pos=self._root.pos, size=self._root.size)

        # Update background size if the window resizes
        self._root.bind(
            pos=lambda w, p: setattr(self._bg_rect, "pos", p),
            size=lambda w, s: setattr(self._bg_rect, "size", s),
        )

        self._root.add_widget(self.header)

        self._root.add_widget(self._app_sm)

        self._root.add_widget(self._nav)

    def sign_out(self):
        self._app_sm.transition = NoTransition()
        self._app_sm.current = "dashboard"
        self._nav._set_active("dashboard")
        self._root.clear_widgets()
        self._root.add_widget(self.sm)
        self.sm.current = "login"


if __name__ == "__main__":
    DashboardApp().run()
