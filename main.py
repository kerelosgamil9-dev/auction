# -*- coding: utf-8 -*-
"""Grand Auction (المزاد الكبير) - multiplayer auction game, Kivy.
Screens: menu -> setup -> categories -> (lobby) -> game -> final.  join -> lobby -> game."""
import math

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager

import netplay
from gamedata import CAT, CATEGORIES, ITEMS
from session import Session
from textfx import shape, wrap
from ui import (Btn, Card, Inp, Lbl, Page, Pref, Sfx, TapCard, asset, cat_name, col, header, iname,
                L, popup, scroll_list, sign, spacer, t, tag_name, tf, toast, tw)

ERRORS = {
    "low": ("يجب أن تزيد على أعلى مزايدة حالية", "Your bid must beat the highest bid"),
    "budget": ("رصيدك لا يكفي", "Not enough budget"),
    "zero": ("رصيدك صفر، لا يمكنك المزايدة", "Your budget is 0, you cannot bid"),
    "passed": ("لقد مرّرت في هذه الجولة", "You passed this round"),
    "number": ("أدخل مبلغاً صحيحاً", "Enter a valid amount"),
    "leader": ("أنت صاحب أعلى مزايدة", "You are the highest bidder"),
    "admin": ("هذا الزر للمضيف فقط", "Only the host can do this"),
    "players": ("تحتاج لاعبين اثنين على الأقل", "You need at least 2 players"),
    "full": ("الغرفة ممتلئة أو اللعبة بدأت", "Room is full or the game already started"),
    "port": ("تعذّر فتح الغرفة، أغلق أي لعبة أخرى وحاول ثانية", "Could not open the room, try again"),
}

RULES_AR = [
    "في كل جولة يُعرض عنصر للمزاد، ويزايد اللاعبون عليه بأي مبلغ يريدونه ما دام رصيدهم أكبر من صفر.",
    "صاحب أعلى مزايدة يفوز بالعنصر ويُخصم مبلغه من رصيده هو فقط.",
    "باقي اللاعبين لا يخسرون شيئاً، ويحصل كل منهم على عنصر عشوائي قد يكون مفيداً أو مقلباً.",
    "من يصل رصيده إلى صفر لا يستطيع المزايدة، لكنه يكمل اللعب ويأخذ عنصره العشوائي.",
    "تنتهي الجولة عندما يمرّر الجميع، أو عندما يضغط المضيف على حسم المزاد.",
    "في النهاية: مجموع قوة العناصر + نقاط التكامل (عناصر من نفس النوع، تنوع الأنواع، اكتمال كل الأنواع) - خسارة المقالب. الأعلى يفوز، والتعادل يُحسم بالرصيد المتبقي.",
]
RULES_EN = [
    "Each round an item is auctioned. Players bid any amount they like as long as their budget is above 0.",
    "The highest bidder wins the item and only that player pays the bid.",
    "Everyone else pays nothing and gets a random item - it may be a gift or a prank.",
    "A player at 0 budget cannot bid but keeps playing and gets the random item.",
    "A round ends when everyone passes, or when the host presses End Bidding.",
    "Final score = item power + combo points (same type, variety, complete set) - prank penalties. Highest wins; ties go to the larger remaining budget.",
]


def A():
    return App.get_running_app()


class Base(Screen):
    """Screens rebuild their widgets every time they are shown (language/theme changes apply)."""

    def on_pre_enter(self, *args):
        self.rebuild()

    def rebuild(self):
        self.clear_widgets()
        self.page = Page(orientation="vertical", padding=dp(12), spacing=dp(10))
        self.add_widget(self.page)
        self.build(self.page)

    def build(self, page):
        pass


# ===================================================================== menu
class MenuScreen(Base):
    def build(self, page):
        a = A()
        page.add_widget(Image(source=asset("icon.png"), size_hint_y=None, height=dp(130)))
        page.add_widget(Lbl(t("المزاد الكبير", "Grand Auction"), size=32, bold=True, color="accent",
                            size_hint_y=None, height=dp(48)))
        page.add_widget(Lbl(t("زايد، اجمع، وابنِ الأقوى!", "Bid, collect and build the strongest!"), size=15,
                            color="muted", size_hint_y=None, height=dp(28)))
        page.add_widget(spacer())
        for text, kind, fn in (
                (t("لعب على جهاز واحد", "Pass & Play (one device)"), "primary", lambda: a.go_setup("local")),
                (t("إنشاء غرفة (Wi-Fi / Hotspot)", "Host a Room (Wi-Fi / Hotspot)"), "good", lambda: a.go_setup("host")),
                (t("الانضمام لغرفة", "Join a Room"), "accent", lambda: a.goto("join")),
                (t("طريقة اللعب", "How to Play"), "card2", self.rules)):
            page.add_widget(Btn(text, kind=kind, on=fn, size_hint_y=None, height=dp(58)))
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        row.add_widget(Btn("English" if Pref.lang == "ar" else shape("العربية"),
                           kind="card2", on=lambda: a.toggle("lang"), size=15))
        row.add_widget(Btn(t("الوضع النهاري", "Day mode") if Pref.theme == "night" else t("الوضع الليلي", "Night mode"),
                           kind="card2", on=lambda: a.toggle("theme"), size=15))
        row.add_widget(Btn(t("الصوت: تشغيل", "Sound: ON") if Pref.sound else t("الصوت: كتم", "Sound: OFF"),
                           kind="card2", on=lambda: a.toggle("sound"), size=15))
        page.add_widget(row)

    def rules(self):
        src = RULES_AR if Pref.lang == "ar" else RULES_EN
        rows = []
        for i, line in enumerate(src, 1):
            txt = wrap("%d. %s" % (i, line), 30)
            n = txt.count("\n") + 1
            rows.append((txt, "text", n))
        labels = [Lbl(txt, size=15, halign="right" if Pref.lang == "ar" else "left",
                      size_hint_y=None, height=dp(22 * n + 14)) for txt, _c, n in rows]
        box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        box.add_widget(scroll_list(labels, 40, 6))
        from kivy.uix.popup import Popup
        p = Popup(title=t("طريقة اللعب", "How to Play"), content=box, size_hint=(.94, .85), title_size=sp(18),
                  separator_color=col("accent"), background_color=col("card"), title_color=col("text"))
        box.add_widget(Btn(t("إغلاق", "Close"), on=p.dismiss, size_hint_y=None, height=dp(48)))
        p.open()


# ===================================================================== setup
class SetupScreen(Base):
    def grab(self):
        a = A()
        a.f_budget, a.f_rounds = self.i_budget.text, self.i_rounds.text
        if a.mode == "local":
            for i, inp in enumerate(self.i_names):
                a.f_names[i] = inp.text
        else:
            a.f_host = self.i_host.text

    def build(self, page):
        a = A()
        page.add_widget(header(t("إعدادات اللعبة", "Game Settings"), back=lambda: a.goto("menu")))
        sv = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0, 0, 0, dp(10)])
        box.bind(minimum_height=box.setter("height"))

        def field(label, inp):
            box.add_widget(Lbl(label, size=15, color="muted", size_hint_y=None, height=dp(26)))
            inp.size_hint_y, inp.height = None, dp(48)
            box.add_widget(inp)

        self.i_budget = Inp(a.f_budget, num=True)
        self.i_rounds = Inp(a.f_rounds, num=True)
        field(t("الميزانية الابتدائية لكل لاعب", "Starting budget per player"), self.i_budget)
        field(t("عدد جولات المزاد (العناصر)", "Number of auction rounds"), self.i_rounds)
        if a.mode == "local":
            box.add_widget(Lbl(t("عدد اللاعبين", "Number of players"), size=15, color="muted",
                                size_hint_y=None, height=dp(26)))
            row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
            row.add_widget(Btn("-", kind="card2", on=lambda: self.step(-1), size_hint_x=None, width=dp(60), size=24))
            row.add_widget(Lbl(str(a.nplayers), size=24, bold=True, color="accent"))
            row.add_widget(Btn("+", kind="card2", on=lambda: self.step(1), size_hint_x=None, width=dp(60), size=24))
            box.add_widget(row)
            self.i_names = []
            for i in range(a.nplayers):
                inp = Inp(a.f_names[i], hint=tf("لاعب %d", "Player %d", i + 1))
                self.i_names.append(inp)
                field(tf("اسم اللاعب %d", "Player %d name", i + 1), inp)
        else:
            self.i_host = Inp(a.f_host, hint=t("اسمك", "Your name"))
            field(t("اسمك (المضيف)", "Your name (host)"), self.i_host)
        sv.add_widget(box)
        page.add_widget(sv)
        page.add_widget(Btn(t("التالي: اختيار الفئة", "Next: choose category"), kind="good", on=self.go,
                            size_hint_y=None, height=dp(56)))

    def step(self, d):
        a = A()
        self.grab()
        a.nplayers = max(2, min(8, a.nplayers + d))
        self.rebuild()

    def go(self):
        a = A()
        self.grab()
        try:
            budget, rounds = int(a.f_budget), int(a.f_rounds)
        except ValueError:
            return toast(t("أدخل أرقاماً صحيحة", "Enter valid numbers"))
        if budget < 1 or rounds < 1:
            return toast(t("الميزانية والجولات يجب أن تكون 1 أو أكثر", "Budget and rounds must be 1 or more"))
        a.cfg = dict(budget=budget, rounds=min(rounds, 30))
        if a.mode == "local":
            a.names = [(a.f_names[i].strip() or L("لاعب %d", "Player %d") % (i + 1)) for i in range(a.nplayers)]
        else:
            a.host_name = a.f_host.strip() or L("المضيف", "Host")
        a.remember()
        a.goto("cats")


# ===================================================================== categories
class CategoryScreen(Base):
    def build(self, page):
        a = A()
        page.add_widget(header(t("اختر فئة اللعب", "Choose a Category"), back=lambda: a.goto("setup")))
        sv = ScrollView(do_scroll_x=False)
        grid = GridLayout(cols=2, spacing=dp(10), padding=dp(2), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for c in CATEGORIES:
            tile = TapCard(orientation="vertical", padding=dp(6), spacing=dp(2), size_hint_y=None, height=dp(180))
            tile.add_widget(Image(source=asset("icons", c["id"] + ".png")))
            tile.add_widget(Lbl(tw(c["ar"], c["en"], 16), size=14, bold=True, size_hint_y=None, height=dp(44)))
            tile.bind(on_release=lambda w, cid=c["id"]: (Sfx.play("click"), a.choose_cat(cid)))
            grid.add_widget(tile)
        sv.add_widget(grid)
        page.add_widget(sv)


# ===================================================================== lobby
class LobbyScreen(Base):
    def build(self, page):
        a = A()
        s = a.sess
        st = s.state
        page.add_widget(header(t("غرفة اللعب", "Game Room"), back=a.leave))
        if st is None:
            page.add_widget(Lbl(t("جاري الاتصال...", "Connecting...")))
            return
        cat = CAT[st["cfg"]["cat"]]
        info = Card(orientation="vertical", padding=dp(8), size_hint_y=None, height=dp(86))
        info.add_widget(Lbl(tw(cat["ar"], cat["en"], 30).replace("\n", " "), size=20, bold=True, color="accent"))
        info.add_widget(Lbl(tf("الميزانية %d  •  الجولات %d", "Budget %d  •  Rounds %d",
                               st["cfg"]["budget"], st["cfg"]["rounds"]), size=15, color="muted"))
        page.add_widget(info)
        if s.mode == "host":
            ip = netplay.local_ip()
            box = Card(bg="card2", orientation="vertical", padding=dp(8), size_hint_y=None, height=dp(110))
            box.add_widget(Lbl(t("عنوان الغرفة", "Room address"), size=14, color="muted"))
            box.add_widget(Lbl(ip, size=28, bold=True))
            box.add_widget(Lbl(t("يظهر تلقائياً عند اللاعبين على نفس الشبكة", "Shows up automatically for players on the same network"),
                               size=12, color="muted"))
            page.add_widget(box)
        rows = []
        for p in st["players"]:
            r = Card(orientation="horizontal", padding=dp(10), height=dp(48))
            label = tf("%s  (أنت)", "%s  (you)", p["name"]) if p["id"] == s.my_pid else shape(p["name"])
            r.add_widget(Lbl(label, size=17, bold=True))
            r.add_widget(Lbl(t("متصل", "Online") if p["connected"] else t("غير متصل", "Offline"), size=14,
                             color="goodtxt" if p["connected"] else "badtxt", size_hint_x=None, width=dp(90)))
            rows.append(r)
        page.add_widget(scroll_list(rows, 48))
        if s.mode == "host":
            page.add_widget(Btn(t("ابدأ اللعبة", "Start Game"), kind="good", on=s.host_start_game,
                                size_hint_y=None, height=dp(58), disabled=len(st["players"]) < 2))
        else:
            page.add_widget(Lbl(t("في انتظار المضيف ليبدأ اللعبة...", "Waiting for the host to start..."),
                                color="muted", size_hint_y=None, height=dp(40)))


# ===================================================================== join
class JoinScreen(Base):
    def on_pre_enter(self, *args):
        A().sess.search()
        super().on_pre_enter()

    def build(self, page):
        a = A()
        page.add_widget(header(t("الانضمام لغرفة", "Join a Room"), back=a.leave))
        self.i_name = Inp(Pref.data.get("join_name", ""), hint=t("اسمك", "Your name"), size_hint_y=None, height=dp(48))
        page.add_widget(Lbl(t("اسمك", "Your name"), size=15, color="muted", size_hint_y=None, height=dp(24)))
        page.add_widget(self.i_name)
        page.add_widget(Lbl(t("الغرف المتاحة (اضغط للاختيار)", "Rooms found (tap to pick)"), size=15, color="muted",
                            size_hint_y=None, height=dp(24)))
        self.holder = BoxLayout(size_hint_y=None, height=dp(150))
        page.add_widget(self.holder)
        self.fill_found()
        page.add_widget(Lbl(t("أو اكتب عنوان المضيف يدوياً", "Or type the host address"), size=15, color="muted",
                             size_hint_y=None, height=dp(24)))
        self.ip = Inp("", hint="192.168.x.x", size_hint_y=None, height=dp(48))
        page.add_widget(self.ip)
        self.status = Lbl("", size=15, color="accent", size_hint_y=None, height=dp(30))
        page.add_widget(self.status)
        page.add_widget(spacer())
        page.add_widget(Btn(t("اتصال", "Connect"), kind="good", on=self.connect, size_hint_y=None, height=dp(56)))

    def fill_found(self):
        a = A()
        self.holder.clear_widgets()
        if not a.found:
            self.holder.add_widget(Lbl(t("جاري البحث... تأكد أن الجميع على نفس الواي فاي/الهوت سبوت",
                                         "Searching... make sure everyone is on the same Wi-Fi/hotspot"),
                                       size=14, color="muted"))
            return
        rows = [Btn(tf("%s  -  %s", "%s  -  %s", info.get("name", "?"), ip), kind="card2",
                    on=lambda ip=ip: setattr(self.ip, "text", ip), size=15) for ip, info in a.found.items()]
        self.holder.add_widget(scroll_list(rows, 44))

    def set_status(self, text):
        if getattr(self, "status", None):
            self.status.text = text

    def connect(self):
        a = A()
        ip = self.ip.text.strip()
        if not ip:
            return toast(t("اختر غرفة أو اكتب العنوان", "Pick a room or type the address"))
        name = self.i_name.text.strip() or L("لاعب", "Player")
        Pref.data["join_name"] = name
        Pref.save()
        self.set_status(t("جاري الاتصال...", "Connecting..."))
        a.sess.join(ip, name)


# ===================================================================== game
class GameScreen(Base):
    actor = 0

    def on_pre_enter(self, *args):
        s = A().sess
        self._key = None
        self.amount = None
        self.amount_text = ""
        if s.mode != "local":
            self.actor = s.my_pid
        elif s.state and self.actor >= len(s.state["players"]):
            self.actor = 0
        super().on_pre_enter()

    def build(self, page):
        self.top = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self.plist = BoxLayout()
        self.panel = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        for w in (self.top, self.plist, self.panel):
            page.add_widget(w)
        if A().sess.state:
            self.update(A().sess.state)

    def update(self, st):
        self.fill_top(st)
        self.fill_list(st)
        self.fill_panel(st)

    # ---- top: round, item, highest bid
    def fill_top(self, st):
        a = A()
        cat = CAT[st["cfg"]["cat"]]
        top = self.top
        top.clear_widgets()
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        row.add_widget(Lbl(tf("الجولة %d من %d", "Round %d of %d", st["round"], st["rounds"]), size=17, bold=True))
        row.add_widget(Btn(t("خروج", "Exit"), kind="card2", on=a.leave, size_hint_x=None, width=dp(80), size=15))
        top.add_widget(row)
        card = Card(orientation="horizontal", padding=dp(8), spacing=dp(10), size_hint_y=None, height=dp(88))
        card.add_widget(Image(source=asset("icons", cat["id"] + ".png"), size_hint_x=None, width=dp(72)))
        info = BoxLayout(orientation="vertical")
        it = ITEMS[st["item"]]
        info.add_widget(Lbl(t(it[1], it[2]), size=22, bold=True,
                            color="accent"))
        info.add_widget(Lbl(tf("القوة %d  •  %s", "Power %d  •  %s", it[3], tag_name(it[0])), size=14, color="muted"))
        card.add_widget(info)
        top.add_widget(card)
        hb = None
        if st["high_by"] is None:
            txt = t("لا توجد مزايدة بعد", "No bids yet")
        else:
            who = [p for p in st["players"] if p["id"] == st["high_by"]][0]["name"]
            txt = tf("أعلى مزايدة: %d  بواسطة %s", "Highest bid: %d by %s", st["high"], who)
            hb = "accent"
        top.add_widget(Lbl(txt, size=17, bold=True, color=hb or "muted", size_hint_y=None, height=dp(30)))
        n = 3
        if a.sess.mode == "client" and a.link_down:
            top.add_widget(Lbl(t("انقطع الاتصال... جاري إعادة المحاولة", "Connection lost... retrying"), size=14,
                                color="badtxt", size_hint_y=None, height=dp(24)))
            n = 4
        top.height = dp(44 + 88 + 30 + (24 if n == 4 else 0)) + dp(6) * n

    # ---- players list
    def fill_list(self, st):
        a = A()
        self.plist.clear_widgets()
        rows = []
        for p in st["players"]:
            row = TapCard(orientation="horizontal", padding=dp(8), spacing=dp(4), height=dp(58))
            tags = []
            if p["id"] == st["high_by"]:
                tags.append(t("الأعلى", "Leader"))
            if p["passed"]:
                tags.append(t("مرّر", "Passed"))
            if not p["connected"]:
                tags.append(t("غير متصل", "Offline"))
            if p["budget"] <= 0:
                tags.append(t("رصيد 0", "Broke"))
            if a.sess.mode != "local" and p["id"] == a.sess.my_pid:
                tags.append(t("أنت", "You"))
            nm = BoxLayout(orientation="vertical", size_hint_x=.4)
            nm.add_widget(Lbl(shape(p["name"]), size=16, bold=True))
            nm.add_widget(Lbl(" • ".join(tags), size=11, color="accent" if p["id"] == st["high_by"] else "muted"))
            row.add_widget(nm)
            row.add_widget(Lbl(tf("رصيد\n%d", "Budget\n%d", p["budget"]), size=13))
            row.add_widget(Lbl(tf("عناصر\n%d", "Items\n%d", len(p["items"])), size=13))
            row.add_widget(Lbl(tf("نقاط\n%d", "Score\n%d", p["score"]), size=13, bold=True, color="accent"))
            row.bind(on_release=lambda w, p=p: self.show_items(p))
            rows.append(row)
        self.plist.add_widget(scroll_list(rows, 58))

    def show_items(self, p):
        a = A()
        eng = a.sess.eng
        cfgcat = a.sess.state["cfg"]["cat"]
        sc = _score(p["items"], cfgcat)
        rows = [(tf("قوة %d + تكامل %d + مقالب %d = %d", "Power %d + Combo %d + Pranks %d = %d",
                    sc["power"], sc["combo"], sc["pranks"], sc["total"]), "accent")]
        if not p["items"]:
            rows.append((t("لا يملك عناصر بعد", "No items yet"), "muted"))
        for iid in sorted(p["items"], key=lambda i: -ITEMS[i][3]):
            it = ITEMS[iid]
            rows.append((tf("%s   [%s]   %s", "%s   [%s]   %s", iname(iid), tag_name(it[0]), sign(it[3])),
                         "goodtxt" if it[3] > 0 else "badtxt"))
        popup(shape(p["name"]), rows)

    # ---- bottom panel
    def fill_panel(self, st):
        a = A()
        s = a.sess
        me = [p for p in st["players"] if p["id"] == self.actor]
        me = me[0] if me else st["players"][0]
        admin = s.is_admin
        key = (st["phase"], st["round"], me["id"], me["passed"], me["budget"] > 0, st["high_by"] == me["id"], admin)
        if key == self._key:
            return
        if self._key is None or key[:2] != self._key[:2]:
            self.amount_text = ""
        elif self.amount is not None:
            self.amount_text = self.amount.text
        self._key = key
        self.amount = None
        box = self.panel
        box.clear_widgets()
        h = 0
        if st["phase"] == "roundend":
            h = self.panel_result(st, admin)
        else:
            h = self.panel_bidding(st, me, admin)
        box.height = h + dp(6) * (len(box.children) - 1 if box.children else 0)

    def panel_bidding(self, st, me, admin):
        a = A()
        s = a.sess
        box = self.panel
        h = 0
        if s.mode == "local":
            sv = ScrollView(do_scroll_y=False, size_hint_y=None, height=dp(46))
            strip = BoxLayout(size_hint_x=None, spacing=dp(6))
            strip.bind(minimum_width=strip.setter("width"))
            for p in st["players"]:
                strip.add_widget(Btn(shape(p["name"]), kind="accent" if p["id"] == me["id"] else "card2",
                                     on=lambda pid=p["id"]: self.pick(pid), size_hint_x=None, width=dp(104), size=15))
            sv.add_widget(strip)
            box.add_widget(sv)
            h += dp(46)
        box.add_widget(Lbl(tf("رصيد %s: %d", "%s's budget: %d", me["name"], me["budget"]), size=15, color="muted",
                           size_hint_y=None, height=dp(26)))
        h += dp(26)
        if me["budget"] <= 0:
            box.add_widget(Lbl(t("رصيدك صفر: لا مزايدة، وستحصل على عنصر عشوائي", "Budget 0: no bidding, you still get a random item"),
                               size=14, color="badtxt", size_hint_y=None, height=dp(38)))
            h += dp(38)
        elif me["passed"]:
            box.add_widget(Lbl(t("لقد مرّرت في هذه الجولة", "You passed this round"), size=15, color="muted",
                               size_hint_y=None, height=dp(34)))
            h += dp(34)
        else:
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
            self.amount = Inp(self.amount_text, hint=t("مبلغ المزايدة", "Bid amount"), num=True)
            row.add_widget(self.amount)
            row.add_widget(Btn(t("زايد", "Bid"), kind="good", on=self.do_bid, size_hint_x=None, width=dp(110)))
            box.add_widget(row)
            quick = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
            for inc in (10, 50, 100):
                quick.add_widget(Btn("+%d" % inc, kind="card2", size=14, on=lambda inc=inc: self.quick(inc)))
            quick.add_widget(Btn(t("كل الرصيد", "All-in"), kind="card2", size=14, on=lambda: self.quick(None)))
            box.add_widget(quick)
            h += dp(50 + 40)
        row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        if me["budget"] > 0 and not me["passed"]:
            row.add_widget(Btn(t("تمرير", "Pass"), kind="card2", on=lambda: self.do_pass(me["id"]),
                               disabled=st["high_by"] == me["id"]))
        if admin:
            row.add_widget(Btn(t("حسم المزاد", "End Bidding"), kind="accent", on=lambda: a.sess.act("end")))
        if row.children:
            box.add_widget(row)
            h += dp(50)
        return h

    def panel_result(self, st, admin):
        a = A()
        s = a.sess
        res = st["result"]
        box = self.panel
        names = {p["id"]: p["name"] for p in st["players"]}
        lines = []
        if res["winner"] is None:
            lines.append((t("لم يزايد أحد: لا فائز بالعنصر", "Nobody bid: the item is discarded"), "muted"))
        else:
            lines.append((tf("فاز %s بـ %s مقابل %d", "%s won %s for %d", names[res["winner"]], iname(res["item"]),
                             res["amount"]), "accent"))
        for pid, iid in res["randoms"].items():
            pw = ITEMS[iid][3]
            lines.append((tf("%s ← %s (%s)", "%s ← %s (%s)", names[int(pid)], iname(iid), sign(pw)),
                          "goodtxt" if pw > 0 else "badtxt"))
        labels = [Lbl(txt, size=15, color=c, bold=(i == 0), size_hint_y=None, height=dp(30))
                  for i, (txt, c) in enumerate(lines)]
        card = Card(orientation="vertical", padding=dp(6), size_hint_y=None, height=dp(min(30 * len(labels) + 12, 200)))
        card.add_widget(scroll_list(labels, 30, 2))
        box.add_widget(card)
        h = card.height
        if admin:
            last = st["round"] >= st["rounds"]
            box.add_widget(Btn(t("عرض النتيجة النهائية", "Show final results") if last else t("الجولة التالية", "Next round"),
                               kind="good", on=lambda: s.act("next"), size_hint_y=None, height=dp(54)))
        else:
            box.add_widget(Lbl(t("في انتظار المضيف...", "Waiting for the host..."), color="muted",
                               size_hint_y=None, height=dp(54)))
        return h + dp(54)

    # ---- actions
    def pick(self, pid):
        self.actor = pid
        self.fill_panel(A().sess.state)

    def quick(self, inc):
        st = A().sess.state
        me = [p for p in st["players"] if p["id"] == self.actor][0]
        v = me["budget"] if inc is None else min(me["budget"], st["high"] + inc)
        if self.amount is not None:
            self.amount.text = str(v)

    def do_bid(self):
        if self.amount is None:
            return
        txt = self.amount.text.strip()
        if not txt:
            return toast(t(*ERRORS["number"]))
        self.amount.text = ""
        self.amount_text = ""
        A().sess.act("bid", pid=self.actor, amount=txt)

    def do_pass(self, pid):
        Sfx.play("pass")
        A().sess.act("pass", pid=pid)


def _score(items, cat_id):
    from engine import Engine
    e = Engine()
    e.cfg["cat"] = cat_id
    return e.score(items)


# ===================================================================== final
class FinalScreen(Base):
    def build(self, page):
        a = A()
        s = a.sess
        st = s.state
        page.add_widget(header(t("النتيجة النهائية", "Final Results")))
        if not st or not st.get("ranking"):
            return
        rk = st["ranking"]
        tied = [r for r in rk if r["total"] == rk[0]["total"] and r["budget"] == rk[0]["budget"]]
        if len(tied) > 1:
            banner = tf("تعادل بين: %s", "Tie between: %s", " - ".join(r["name"] for r in tied))
        else:
            banner = tf("الفائز: %s", "Winner: %s", rk[0]["name"])
        b = Card(bg="accent", orientation="vertical", padding=dp(8), size_hint_y=None, height=dp(70))
        lb = Lbl(banner, size=24, bold=True)
        lb.color = (.1, .1, .15, 1)
        b.add_widget(lb)
        page.add_widget(b)
        rows = []
        for i, r in enumerate(rk, 1):
            ar_items = "، ".join(ITEMS[x][1] for x in r["items"]) or "لا شيء"
            en_items = ", ".join(ITEMS[x][2] for x in r["items"]) or "None"
            txt = tw(ar_items, en_items, 34)
            n = txt.count("\n") + 1
            card = Card(orientation="vertical", padding=dp(8), spacing=dp(2), height=dp(36 + 24 + 20 * n + 12))
            top = BoxLayout(size_hint_y=None, height=dp(34))
            top.add_widget(Lbl("%d. %s" % (i, shape(r["name"])), size=19, bold=True, color="accent" if i == 1 else "text"))
            top.add_widget(Lbl(tf("%d نقطة", "%d pts", r["total"]), size=19, bold=True, size_hint_x=None, width=dp(100)))
            card.add_widget(top)
            card.add_widget(Lbl(tf("قوة %d  تكامل %+d  مقالب %+d  رصيد %d", "Power %d  Combo %+d  Pranks %+d  Budget %d",
                                   r["power"], r["combo"], r["pranks"], r["budget"]), size=12, color="muted",
                                size_hint_y=None, height=dp(22)))
            card.add_widget(Lbl(txt, size=13, size_hint_y=None, height=dp(20 * n)))
            rows.append(card)
        page.add_widget(scroll_list(rows, 100))
        if s.is_admin:
            page.add_widget(Btn(t("العب مرة أخرى", "Play again"), kind="good", on=lambda: s.act("restart"),
                                size_hint_y=None, height=dp(52)))
        page.add_widget(Btn(t("القائمة الرئيسية", "Main menu"), kind="card2", on=a.leave, size_hint_y=None, height=dp(52)))


# ===================================================================== app
class AuctionApp(App):
    title = "Grand Auction"

    def build(self):
        self.icon = asset("icon.png")
        Pref.load(self.user_data_dir)
        d = Pref.data
        self.mode = "local"
        self.cfg = {}
        self.names = []
        self.host_name = ""
        self.nplayers = d.get("n", 3)
        self.f_budget, self.f_rounds = str(d.get("budget", 1000)), str(d.get("rounds", 8))
        self.f_names = (d.get("names", []) + [""] * 8)[:8]
        self.f_host = d.get("host", "")
        self.found = {}
        self.link_down = False
        self._prev = {}
        self.sess = Session(self.on_state, self.on_event)
        Window.clearcolor = col("bg")
        try:
            Window.softinput_mode = "below_target"
        except Exception:
            pass
        self.sm = ScreenManager(transition=NoTransition())
        for name, cls in (("menu", MenuScreen), ("setup", SetupScreen), ("cats", CategoryScreen),
                          ("lobby", LobbyScreen), ("join", JoinScreen), ("game", GameScreen),
                          ("final", FinalScreen)):
            self.sm.add_widget(cls(name=name))
        Clock.schedule_interval(lambda dt: self.sess.poll(), 0.1)
        Window.bind(on_keyboard=self.on_key)
        return self.sm

    # ---- navigation / prefs
    def goto(self, name):
        self.sm.current = name

    def go_setup(self, mode):
        self.mode = mode
        self.goto("setup")

    def leave(self):
        self.sess.close()
        self.found = {}
        self.link_down = False
        self._prev = {}
        self.goto("menu")

    def remember(self):
        Pref.data.update(n=self.nplayers, budget=self.cfg.get("budget", 1000), rounds=self.cfg.get("rounds", 8),
                         names=self.f_names, host=self.f_host)
        Pref.save()

    def toggle(self, what):
        if what == "lang":
            Pref.lang = "en" if Pref.lang == "ar" else "ar"
        elif what == "theme":
            Pref.theme = "day" if Pref.theme == "night" else "night"
        else:
            Pref.sound = not Pref.sound
        Pref.save()
        Window.clearcolor = col("bg")
        self.sm.current_screen.rebuild()

    def on_key(self, window, key, *args):
        if key == 27:                                  # Android back button
            if self.sm.current == "menu":
                return False
            if self.sm.current in ("setup", "join"):
                self.leave()
            elif self.sm.current == "cats":
                self.goto("setup")
            else:
                self.leave()
            return True
        return False

    def on_pause(self):
        return True

    def on_stop(self):
        self.sess.close()

    # ---- starting
    def choose_cat(self, cid):
        self.cfg["cat"] = cid
        if self.mode == "local":
            self.sess.start_local(self.names, self.cfg)
        else:
            self.sess.start_host(self.host_name, self.cfg)

    # ---- session callbacks
    def on_state(self, st):
        cur = self.sm.current
        ph = st["phase"]
        if ph == "lobby":
            if cur == "lobby":
                self.sm.current_screen.rebuild()
            else:
                self.goto("lobby")
        elif ph in ("bidding", "roundend"):
            if cur != "game":
                self.goto("game")
            else:
                self.sm.current_screen.update(st)
        elif ph == "final" and cur != "final":
            self.goto("final")
        self.sounds(st)

    def sounds(self, st):
        pv, s = self._prev, self.sess
        if st["phase"] == "bidding" and st["round"] == pv.get("round") and st["high"] > pv.get("high", 0):
            Sfx.play("bid")
        if st["phase"] == "roundend" and pv.get("phase") != "roundend":
            res = st["result"]
            Sfx.play("win" if res["winner"] is not None else "pass")
            ids = [i for k, i in res["randoms"].items() if s.mode == "local" or int(k) == s.my_pid]
            if ids:
                bad = any(ITEMS[i][3] < 0 for i in ids)
                Clock.schedule_once(lambda dt: Sfx.play("prank" if bad else "lucky"), .7)
        if st["phase"] == "final" and pv.get("phase") != "final":
            Sfx.play("end")
        self._prev = dict(round=st["round"], high=st["high"], phase=st["phase"])

    def on_event(self, kind, data):
        cur = self.sm.current_screen
        if kind == "error":
            msg = ERRORS.get(data)
            if msg:
                toast(t(*msg))
            if data == "full" and self.sm.current == "join":
                cur.set_status(t(*msg))
        elif kind == "link":
            self.link_down = data == "down"
            if data == "fail" and self.sm.current == "join":
                cur.set_status(t("تعذّر الاتصال بالمضيف", "Could not reach the host"))
            elif data == "up" and self.sm.current == "join":
                cur.set_status(t("تم الاتصال، جاري الدخول...", "Connected, joining..."))
            elif self.sm.current == "game" and self.sess.state:
                cur.fill_top(self.sess.state)
        elif kind == "found":
            ip, info = data
            self.found[ip] = info
            if self.sm.current == "join":
                cur.fill_found()


if __name__ == "__main__":
    AuctionApp().run()
