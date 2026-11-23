# -*- coding: utf-8 -*-
"""Shared UI pieces: preferences (language / theme / sound), widgets, helpers."""
import json
import os

from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from gamedata import ITEMS
from textfx import has_arabic, shape, wrap

BASE = os.path.dirname(os.path.abspath(__file__))


def asset(*parts):
    return os.path.join(BASE, "assets", *parts)


# DejaVu Sans carries Arabic presentation forms; replacing the default font makes
# every Label / TextInput / Popup in the app use it.
LabelBase.register(name="Roboto", fn_regular=asset("fonts", "DejaVuSans.ttf"),
                   fn_bold=asset("fonts", "DejaVuSans-Bold.ttf"))

THEMES = {
    "night": dict(bg=(.08, .08, .16, 1), card=(.14, .15, .27, 1), card2=(.22, .23, .40, 1),
                  text=(1, 1, 1, 1), muted=(.72, .74, .88, 1), primary=(.33, .45, .95, 1),
                  accent=(1, .78, .2, 1), good=(.2, .72, .42, 1), bad=(.9, .3, .32, 1),
                  btntext=(1, 1, 1, 1), inputbg=(.2, .21, .36, 1), goodtxt=(.4, .95, .6, 1),
                  badtxt=(1, .5, .5, 1)),
    "day": dict(bg=(.94, .95, .99, 1), card=(1, 1, 1, 1), card2=(.86, .88, .96, 1),
                text=(.1, .12, .2, 1), muted=(.4, .43, .55, 1), primary=(.25, .38, .9, 1),
                accent=(.95, .65, .05, 1), good=(.1, .62, .3, 1), bad=(.85, .2, .22, 1),
                btntext=(1, 1, 1, 1), inputbg=(.9, .92, .98, 1), goodtxt=(.05, .5, .2, 1),
                badtxt=(.8, .15, .15, 1)),
}


class Pref:
    lang = "ar"
    theme = "night"
    sound = True
    data = {}                      # other remembered values (names, budget, ...)
    path = None

    @classmethod
    def load(cls, folder):
        cls.path = os.path.join(folder, "prefs.json")
        try:
            with open(cls.path, encoding="utf-8") as f:
                d = json.load(f)
            cls.lang, cls.theme = d.get("lang", "ar"), d.get("theme", "night")
            cls.sound, cls.data = d.get("sound", True), d.get("data", {})
        except (OSError, ValueError):
            pass

    @classmethod
    def save(cls):
        try:
            with open(cls.path, "w", encoding="utf-8") as f:
                json.dump(dict(lang=cls.lang, theme=cls.theme, sound=cls.sound, data=cls.data), f,
                          ensure_ascii=False)
        except (OSError, TypeError):
            pass


def col(name):
    return THEMES[Pref.theme][name]


def L(ar, en):
    """Logical (unshaped) text in the current language."""
    return ar if Pref.lang == "ar" else en


def t(ar, en):
    """Display text in the current language (shaped when Arabic)."""
    return shape(ar) if Pref.lang == "ar" else en


def tw(ar, en, width=30):
    return wrap(ar, width) if Pref.lang == "ar" else wrap(en, width)


def iname(iid):
    """Logical item name."""
    it = ITEMS[iid]
    return it[1] if Pref.lang == "ar" else it[2]


def cat_name(cat):
    return cat["ar"] if Pref.lang == "ar" else cat["en"]


TAG_AR = dict(hall="قاعات", room="غرف", garden="حدائق", defense="دفاع", luxury="فخامة", outdoor="خارجي",
              tech="تقنية", comfort="راحة", kitchen="مطبخ", menu="قائمة الطعام", vibe="أجواء", fun="ترفيه",
              relax="استرخاء", food="طعام", safety="أمان", ride="ألعاب", kids="أطفال", show="عروض",
              GK="حارس مرمى", DEF="مدافع", MID="وسط", ATT="مهاجم", COACH="مدرب", strength="قوة",
              speed="سرعة", magic="سحر", mind="عقل", hero="بطل", villain="شرير", cosmic="كوني",
              cats="قطط", big="ضخمة", special="مميزة", birds="طيور", sea="بحرية", ship="سفن",
              lab="مختبر", power="طاقة", life="حياة", weapon="أسلحة", loot="غنائم", crew="طاقم",
              lucky="حظ", x="مقلب")


def tag_name(tag):
    return TAG_AR.get(tag, tag) if Pref.lang == "ar" else ("Prank" if tag == "x" else tag.capitalize())


def sign(n):
    return "+%d" % n if n > 0 else str(n)


# ---------------------------------------------------------------- sound
class Sfx:
    cache = {}

    @classmethod
    def play(cls, name):
        if not Pref.sound:
            return
        snd = cls.cache.get(name)
        if snd is None:
            try:
                snd = SoundLoader.load(asset("sounds", name + ".wav")) or False
            except Exception:                      # audio backend missing: stay silent
                snd = False
            cls.cache[name] = snd
        if snd:
            try:
                snd.stop()
                snd.play()
            except Exception:
                pass


# ---------------------------------------------------------------- widgets
class Page(BoxLayout):
    """Full-screen coloured background."""

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*col("bg"))
            self._r = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._u, size=self._u)

    def _u(self, *a):
        self._r.pos, self._r.size = self.pos, self.size


class Card(BoxLayout):
    def __init__(self, bg="card", radius=16, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self._c = Color(*col(bg))
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._u, size=self._u)

    def _u(self, *a):
        self._r.pos, self._r.size = self.pos, self.size


class TapCard(ButtonBehavior, Card):
    pass


class Lbl(Label):
    def __init__(self, text="", size=16, color="text", bold=False, halign="center", **kw):
        super().__init__(text=text, font_size=sp(size), color=col(color), bold=bold, halign=halign,
                         valign="middle", **kw)
        self.bind(size=self._ts)

    def _ts(self, *a):
        self.text_size = (self.width, self.height)


class Btn(ButtonBehavior, Label):
    def __init__(self, text="", kind="primary", on=None, size=17, **kw):
        dark = kind == "accent"
        txt = col("text") if kind == "card2" else ((.1, .1, .15, 1) if dark else col("btntext"))
        super().__init__(text=text, font_size=sp(size), bold=True, color=txt, halign="center",
                         valign="middle", **kw)
        self.kind, self.on = kind, on
        with self.canvas.before:
            self._c = Color(*col(kind))
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._u, size=self._u, state=self._st, disabled=self._dis)
        self.bind(on_release=self._rel)
        self._dis()

    def _u(self, *a):
        self._r.pos, self._r.size = self.pos, self.size
        self.text_size = self.size

    def _st(self, *a):
        base = col(self.kind)
        k = .75 if self.state == "down" else 1
        self._c.rgba = (base[0] * k, base[1] * k, base[2] * k, base[3])

    def _dis(self, *a):
        self.opacity = .4 if self.disabled else 1

    def _rel(self, *a):
        Sfx.play("click")
        if self.on:
            self.on()


class Inp(TextInput):
    """Text field that shows Arabic correctly.
    The real TextInput keeps the logical text (so .text is normal) but is drawn invisible;
    a Label on top shows the shaped text (joined letters, right direction)."""

    def __init__(self, text="", hint="", num=False, **kw):
        clear = (0, 0, 0, 0)
        super().__init__(text=text, hint_text="", multiline=False, write_tab=False,
                         input_filter="int" if num else None, font_size=sp(18),
                         background_normal="", background_active="", background_color=col("inputbg"),
                         foreground_color=clear, cursor_color=clear, selection_color=clear,
                         padding=[dp(12), dp(12), dp(12), dp(8)], **kw)
        self._hint = hint
        self._ov = Label(font_size=sp(18), color=col("text"), valign="middle", halign="left")
        self.add_widget(self._ov)
        self.bind(pos=self._lay, size=self._lay, text=self._upd, focus=self._upd)
        self._lay()
        self._upd()

    def _lay(self, *a):
        self._ov.pos = (self.x + dp(12), self.y)
        self._ov.size = (max(0, self.width - dp(24)), self.height)
        self._ov.text_size = self._ov.size

    def _upd(self, *a):
        if self.text:
            shown = shape(self.text) + ("  |" if self.focus and has_arabic(self.text) else "")
            if self.focus and not has_arabic(self.text):
                shown = self.text + "|"
            self._ov.text, self._ov.color = shown, col("text")
            self._ov.halign = "right" if has_arabic(self.text) else "left"
        else:
            self._ov.text = ("|" if self.focus else self._hint)
            self._ov.color = col("muted")
            self._ov.halign = "right" if has_arabic(self._hint) and not self.focus else "left"


def spacer(h=None):
    return BoxLayout(size_hint_y=None, height=dp(h)) if h else BoxLayout()


def header(title, back=None):
    row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
    if back:
        row.add_widget(Btn(t("رجوع", "Back"), kind="card2", on=back, size_hint_x=None, width=dp(90), size=15))
    row.add_widget(Lbl(title, size=20, bold=True))
    return row


def scroll_list(rows, row_h, spacing=6):
    """ScrollView with a vertical stack of fixed-height rows."""
    sv = ScrollView(do_scroll_x=False)
    box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(spacing))
    box.bind(minimum_height=box.setter("height"))
    for r in rows:
        r.size_hint_y = None
        if not r.height or r.height == 100:
            r.height = dp(row_h)
        box.add_widget(r)
    sv.add_widget(box)
    return sv


_toast = {"w": None}


def toast(msg):
    old = _toast["w"]
    if old is not None and old.parent:
        Window.remove_widget(old)
    w = Card(bg="card2", orientation="vertical", size_hint=(None, None), padding=dp(8),
             size=(Window.width * .9, dp(56)))
    w.add_widget(Lbl(msg, size=15))
    w.pos = ((Window.width - w.width) / 2, dp(110))
    Window.add_widget(w)
    _toast["w"] = w
    Clock.schedule_once(lambda dt: Window.remove_widget(w) if w.parent else None, 2.4)


def popup(title, rows, row_h=34, width=.92, height=.8):
    """Simple scrollable popup; rows = list of (text, colour-name)."""
    labels = [Lbl(txt, size=15, color=c, height=dp(row_h), size_hint_y=None) for txt, c in rows]
    box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
    box.add_widget(scroll_list(labels, row_h, 4))
    p = Popup(title=title, content=box, size_hint=(width, height), title_size=sp(18),
              separator_color=col("accent"), background_color=col("card"), title_color=col("text"))
    box.add_widget(Btn(t("إغلاق", "Close"), kind="primary", on=p.dismiss, size_hint_y=None, height=dp(48)))
    p.open()
    return p


def tf(ar, en, *args):
    """Format a sentence in the current language. Arabic: shape the whole sentence
    (names inside are re-ordered correctly). English: shape only the names (they may be Arabic)."""
    if Pref.lang == "ar":
        return shape(ar % args)
    return en % tuple(shape(a) if isinstance(a, str) else a for a in args)
