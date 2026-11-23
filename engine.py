# -*- coding: utf-8 -*-
"""Auction game rules. Pure Python so it can run on the host phone,
in pass-and-play mode, and be unit-tested without Kivy."""
import random

from gamedata import ITEMS, CAT, GEN_GOOD, GEN_PRANK

MAX_PLAYERS = 8
PRANK_CHANCE = 0.35


class Engine:
    def __init__(self):
        self.reset()

    def reset(self):
        self.phase = "lobby"          # lobby | bidding | roundend | final
        self.players = []
        self.cfg = {"budget": 1000, "rounds": 8, "cat": "palace"}
        self.round = 0
        self.rounds = 0
        self.deck = []
        self.item = None
        self.high = 0
        self.high_by = None
        self.passed = set()
        self.result = None
        self.used = set()

    # ---------------------------------------------------------- players
    def add_player(self, name, token=None):
        """Returns player id, or None when the room is full / game started."""
        if token:
            for p in self.players:
                if p["token"] == token:          # reconnecting player
                    p["connected"] = True
                    return p["id"]
        if self.phase != "lobby" or len(self.players) >= MAX_PLAYERS:
            return None
        pid = max([p["id"] for p in self.players] + [-1]) + 1
        name = (name or "").strip()[:16] or "P%d" % (pid + 1)
        self.players.append(dict(id=pid, name=name, budget=self.cfg["budget"], items=[],
                                 connected=True, token=token))
        return pid

    def remove_player(self, pid):
        if self.phase == "lobby":
            self.players = [p for p in self.players if p["id"] != pid]

    def player(self, pid):
        for p in self.players:
            if p["id"] == pid:
                return p
        return None

    def set_connected(self, pid, flag):
        p = self.player(pid)
        if p:
            p["connected"] = flag
            if self.phase == "bidding":
                self._check_auto()

    def configure(self, budget=None, rounds=None, cat=None):
        if budget is not None:
            self.cfg["budget"] = max(1, int(budget))
        if rounds is not None:
            self.cfg["rounds"] = max(1, min(30, int(rounds)))
        if cat in CAT:
            self.cfg["cat"] = cat

    # ---------------------------------------------------------- flow
    def start(self):
        if self.phase != "lobby" or len(self.players) < 2:
            return False
        cat = CAT[self.cfg["cat"]]
        self.deck = list(cat["good"])
        random.shuffle(self.deck)
        self.rounds = min(self.cfg["rounds"], len(self.deck))
        self.round = 0
        self.used = set()
        for p in self.players:
            p["budget"] = self.cfg["budget"]
            p["items"] = []
        self._next_round()
        return True

    def back_to_lobby(self):
        self.phase = "lobby"
        self.item = None
        self.result = None
        self.round = 0
        for p in self.players:
            p["items"] = []
            p["budget"] = self.cfg["budget"]

    def _next_round(self):
        self.round += 1
        self.item = self.deck.pop()
        self.used.add(self.item)
        self.high, self.high_by, self.passed, self.result = 0, None, set(), None
        self.phase = "bidding"
        self._check_auto()

    def next_round(self):
        if self.phase != "roundend":
            return False
        if self.round >= self.rounds:
            self.phase = "final"
        else:
            self._next_round()
        return True

    # ---------------------------------------------------------- bidding
    def eligible(self, p):
        return p["connected"] and p["budget"] > 0 and p["id"] not in self.passed

    def bid(self, pid, amount):
        """Returns None on success or an error code string."""
        if self.phase != "bidding":
            return "phase"
        p = self.player(pid)
        if p is None:
            return "phase"
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return "number"
        if p["budget"] <= 0:
            return "zero"
        if pid in self.passed:
            return "passed"
        if amount <= self.high:
            return "low"
        if amount > p["budget"]:
            return "budget"
        self.high, self.high_by = amount, pid
        self._check_auto()
        return None

    def pass_turn(self, pid):
        if self.phase != "bidding" or self.player(pid) is None:
            return "phase"
        if pid == self.high_by:
            return "leader"
        self.passed.add(pid)
        self._check_auto()
        return None

    def _check_auto(self):
        """Round ends by itself when nobody except the leader can still bid."""
        if self.phase != "bidding":
            return
        others = [p for p in self.players if p["id"] != self.high_by and self.eligible(p)]
        if not others:
            self.end_round()

    def end_round(self):
        if self.phase != "bidding":
            return False
        res = {"item": self.item, "winner": None, "amount": 0, "randoms": {}}
        winner = self.player(self.high_by) if self.high_by is not None else None
        if winner:
            winner["budget"] -= self.high
            winner["items"].append(self.item)
            res["winner"], res["amount"] = winner["id"], self.high
        for p in self.players:
            if winner and p["id"] == winner["id"]:
                continue
            iid = self._random_item()
            p["items"].append(iid)
            res["randoms"][str(p["id"])] = iid
        self.result = res
        self.phase = "roundend"
        return True

    def _random_item(self):
        cat = CAT[self.cfg["cat"]]
        for _ in range(2):
            prank = random.random() < PRANK_CHANCE
            pool = (cat["prank"] + GEN_PRANK) if prank else (cat["good"] + GEN_GOOD)
            free = [i for i in pool if i not in self.used]
            if free:
                choice = random.choice(free)
                self.used.add(choice)
                return choice
            # the pool is exhausted: allow repeats instead of failing
            self.used -= set(pool)
        return random.choice(cat["good"] + GEN_GOOD)

    # ---------------------------------------------------------- scoring
    def score(self, items):
        power = pranks = 0
        tags = {}
        for iid in items:
            tag, _ar, _en, pw, _c = ITEMS[iid]
            if pw < 0:
                pranks += pw
                continue
            power += pw
            if tag != "lucky":
                tags[tag] = tags.get(tag, 0) + 1
        combo = sum((n - 1) * 2 for n in tags.values() if n > 1)
        if len(tags) >= 3:
            combo += 5
        if all(t in tags for t in CAT[self.cfg["cat"]]["tags"]):
            combo += 10
        return {"power": power, "combo": combo, "pranks": pranks, "total": power + combo + pranks}

    def ranking(self):
        rows = []
        for p in self.players:
            s = self.score(p["items"])
            rows.append(dict(id=p["id"], name=p["name"], budget=p["budget"], items=list(p["items"]), **s))
        rows.sort(key=lambda r: (r["total"], r["budget"]), reverse=True)
        return rows

    # ---------------------------------------------------------- snapshot
    def snapshot(self):
        players = []
        for p in self.players:
            s = self.score(p["items"])
            players.append(dict(id=p["id"], name=p["name"], budget=p["budget"], items=list(p["items"]),
                                connected=p["connected"], passed=p["id"] in self.passed,
                                score=s["total"]))
        return {"phase": self.phase, "cfg": dict(self.cfg), "round": self.round, "rounds": self.rounds,
                "item": self.item, "high": self.high, "high_by": self.high_by, "players": players,
                "result": self.result, "ranking": self.ranking() if self.phase == "final" else None}
