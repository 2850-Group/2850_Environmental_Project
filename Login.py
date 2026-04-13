"""
Login In Screen

Requirements: pip install kivy
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock

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

def  make_label(text, font_size=14, color = NEUTRAL, bold = False, halign='left', height = dp(24)):
    label = Label(
        text = text,
        font_size = font_size,
        color = color,
        bold = bold,
        halign = halign, 
        valign = "middle",
        height = height
    )
    label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
    return label

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
            
class Input(TextInput):
    """Single line styled text input"""

    def __init__(self, hint='', password=False, **kwargs):
        super().__init__(
            hint_text=hint,
            password=password,
            multiline=False,
            background_color=BG,
            foreground_color=NEUTRAL,
            hint_text_color=BORDER,
            cursor_color=ACCENT,
            font_name='RobotoMono-Regular' if False else 'Roboto',
            font_size=14,
            padding=[dp(12), dp(10)],
            size_hint=(1, None),
            height=dp(44),
            **kwargs,
        )
        self._draw_bg()
        self.bind(focus = self._on_focus, pos = self._draw_bg, size = self._draw_bg)

    def _draw_bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*SURFACE2)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(8)])
            Color(*(ACCENT if self.focus else BORDER))
            Line(rounded_rectangle=[*self.pos, *self.size, dp(8)],
                 width=1.2)
            
    def _on_focus(self, inst, focused):
        self._draw_bg()

class SignInButton(Button):
    """Blue sign in button"""
    def __init__(self, text="Sign In", **kwargs):
        super().__init__(
            text=text,
            background_color=BG,
            color=NEUTRAL,
            bold=True,
            font_size=14,
            size_hint=(1, None),
            height=dp(48),
            **kwargs,
        )
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*ACCENT)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(8)])
            
    def on_press(self):
        with self.canvas.before:
            Color(*ACCENT)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])

    def on_release(self):
        self._draw

class SignUpButton(Button):
    def __init__(self, text="Sign Up", **kwargs):
        super().__init__(
            text=text,
            background_color=BG,
            color=NEUTRAL,
            bold=True,
            font_size=14,
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
        self._draw

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
        label = make_label(text, font_size=11, color=BORDER, halign="center", height=dp(24))
        label.width=dp(30)

        self.add_widget(self._line_holders[0])
        self.add_widget(label)
        self.add_widget(self._line_holders[1])
    
    def _draw_line(self, widget):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BORDER)
            Line(points=[widget.x, widget.center_y, widget.right, widget.center_y],
                 width=1)
            
class Header(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', size_hint=(1, None),
                         height=dp(44), spacing=dp(10), **kwargs)

        name_box = BoxLayout(orientation='horizontal', spacing=0)
        name_box.add_widget(make_label('Application Name', font_size=18, color=NEUTRAL,
                                       bold=True,
                                       height=dp(44)))
        name_box.add_widget(Widget())
        self.add_widget(name_box)

class SignInPanel(BoxLayout):
    def __init__(self, switch_cb, **kwargs):
        super().__init__(orientation = "vertical", spacing=dp(12), **kwargs)
        self.switch_cb = switch_cb
        self._build()

    def _build(self):
        self.add_widget(make_label('Welcome', font_size=20,
                                   color=NEUTRAL, bold=True, height=dp(30)))
        self.add_widget(make_label('Sign in to your environmental dashboard',
                                   font_size=13, color=DIM, height=dp(22)))
        self.add_widget(Widget(size_hint=(1, None), height=dp(6)))
 
        self.add_widget(make_label('USERNAME', font_size=11, color=DIM,
                                   height=dp(18)))
        self.username = Input(hint='e.g. j.farmer')
        self.add_widget(self.username)
 
        self.add_widget(make_label('PASSWORD', font_size=11, color=DIM,
                                   height=dp(18)))
        self.password = Input(hint='••••••••', password=True)
        self.add_widget(self.password)
 
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

class SignUpPanel(BoxLayout):
    def __init__(self, switch_cb, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(12),
                         size_hint=(1, 1), **kwargs)
        self.switch_cb = switch_cb
        self._build()

    def _build(self):
        self.add_widget(make_label('Create account', font_size=20,
                                   color=NEUTRAL, bold=True, height=dp(30)))
        self.add_widget(make_label('Start monitoring your crops today',
                                   font_size=13, color=DIM, height=dp(22)))
        self.add_widget(Widget(size_hint=(1, None), height=dp(6)))
 
        self.add_widget(make_label('FULL NAME', font_size=11, color=DIM,
                                   height=dp(18)))
        self.fullname = Input(hint='e.g. John Farmer')
        self.add_widget(self.fullname)
 
        self.add_widget(make_label('USERNAME', font_size=11, color=DIM,
                                   height=dp(18)))
        self.username = Input(hint='e.g. j.farmer')
        self.add_widget(self.username)
 
        self.add_widget(make_label('PASSWORD', font_size=11, color=DIM,
                                   height=dp(18)))
        self.password = Input(hint='Min. 8 characters', password=True)
        self.add_widget(self.password)
 
        self.add_widget(Widget(size_hint=(1, None), height=dp(4)))
 
        create_btn = Button(text='Create account')
        create_btn.bind(on_release=self._on_create)
        self.add_widget(create_btn)
 
        self.add_widget(Divider())
 
        signin_btn = Button(text='Sign in instead')
        signin_btn.bind(on_release=lambda *_: self.switch_cb('login'))
        self.add_widget(signin_btn)
 
        self.add_widget(Widget())

    def _on_create(self, *_):
        name = self.fullname.text.strip()
        user = self.username.text.strip()
        pwd = self.password.text.strip()

class SignInScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()

        with root.canvas.before:
            Color(*BG)
            self._bg_rect = RoundedRectangle(pos = root.pos, size = root.pos, radius = [0])

        root.bind(pos=lambda w, v: setattr(self._bg_rect, 'pos', v),
                  size=lambda w, v: setattr(self._bg_rect, 'size', v))
    
        card = RoundedCard(
            size = (dp(360), dp(560)),
        )

        inner = BoxLayout(
            orientation='vertical',
            padding=[dp(28), dp(28)],
            spacing=dp(0)
        )

        inner.add_widget(Header())

        self.panel_holder = BoxLayout(orientation='vertical')
        self.current_panel = None
        self._show_panel('login')

        inner.add_widget(self.panel_holder)
        card.add_widget(inner)
        root.add_widget(card)
        self.add_widget(root)

    def _show_panel(self, name):
        self.panel_holder.clear_widgets()
        if name == 'login':
            panel = SignInPanel(switch_cb=self._show_panel)
        else:
            panel = SignUpPanel(switch_cb=self._show_panel)
        self.panel_holder.add_widget(panel)
        self._current_panel = name

class EnvironmentalApp(App):
    def build(self):
        screen = ScreenManager(transition = NoTransition())
        screen.add_widget(SignInScreen(name = 'login'))
        return screen
    

if __name__ == '__main__':
    EnvironmentalApp().run()