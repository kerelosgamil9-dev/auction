# -*- coding: utf-8 -*-
"""Session = one object the UI talks to, whatever the mode is:
  local  : pass & play on one device (engine runs here)
  host   : engine runs here and is pushed to the clients over the LAN
  client : state comes from the host, actions are sent to the host
No Kivy imports here, so it can be tested without a window."""
import uuid

import netplay
from engine import Engine


class Session:
    def __init__(self, on_state, on_event):
        self.on_state = on_state          # on_state(snapshot_dict)
        self.on_event = on_event          # on_event(kind, data): "error" | "link" | "found"
        self.token = uuid.uuid4().hex
        self.mode = "local"
        self.eng = Engine()
        self.state = None
        self.my_pid = 0
        self.host = self.link = self.disc = None
        self.conn_pid = {}

    # ------------------------------------------------------------ properties
    @property
    def is_admin(self):
        """Who may end a round / go to the next one / start the game."""
        return self.mode in ("local", "host")

    # ------------------------------------------------------------ setup
    def start_local(self, names, cfg):
        self.close()
        self.mode, self.my_pid = "local", 0
        self.eng = Engine()
        self.eng.configure(**cfg)
        for n in names:
            self.eng.add_player(n)
        self.eng.start()
        self._push()

    def start_host(self, name, cfg):
        self.close()
        self.mode, self.my_pid = "host", 0
        self.eng = Engine()
        self.eng.configure(**cfg)
        self.eng.add_player(name, self.token)
        self.host = netplay.HostServer(name)
        try:
            self.host.start()
        except OSError:
            self.host = None
            self.on_event("error", "port")
            return False
        self._push()
        return True

    def host_start_game(self):
        if not self.eng.start():
            self.on_event("error", "players")
            return
        self._push()

    def back_to_lobby(self):
        if self.mode == "local":
            self.eng.back_to_lobby()
            self.eng.start()
        else:
            self.eng.back_to_lobby()
        self._push()

    def search(self):
        if self.disc is None:
            self.disc = netplay.Discovery()
            self.disc.start()

    def join(self, ip, name):
        self.close()
        self.mode = "client"
        self.state = None
        self.link = netplay.ClientLink(ip.strip(), name.strip() or "Player", self.token)
        self.link.start()

    def close(self):
        for obj in (self.host, self.link, self.disc):
            if obj:
                obj.shutdown()
        self.host = self.link = self.disc = None
        self.conn_pid = {}
        self.state = None

    # ------------------------------------------------------------ actions
    def act(self, action, pid=None, **kw):
        if self.mode == "client":
            if self.link:
                self.link.send(dict(t="act", a=action, **kw))
            return
        err = self._apply(self.my_pid if pid is None else pid, action, kw)
        if err:
            self.on_event("error", err)
        self._push()

    def _apply(self, pid, action, kw):
        e = self.eng
        if action == "bid":
            return e.bid(pid, kw.get("amount"))
        if action == "pass":
            return e.pass_turn(pid)
        admin = self.mode == "local" or pid == 0
        if action in ("end", "next", "restart") and not admin:
            return "admin"
        if action == "end":
            return None if e.end_round() else "phase"
        if action == "next":
            return None if e.next_round() else "phase"
        if action == "restart":
            self.back_to_lobby()
        return None

    def _push(self):
        self.state = self.eng.snapshot()
        if self.host:
            self.host.players = len(self.eng.players)
            for cid in list(self.conn_pid):
                self.host.send(cid, {"t": "state", "s": self.state})
        self.on_state(self.state)

    # ------------------------------------------------------------ polling (main thread)
    def poll(self):
        if self.host:
            self._poll_host()
        if self.link:
            self._poll_client()
        if self.disc:
            while not self.disc.q.empty():
                _k, ip, info = self.disc.q.get()
                self.on_event("found", (ip, info))

    def _poll_host(self):
        changed = False
        while not self.host.q.empty():
            kind, cid, *rest = self.host.q.get()
            if kind == "join":
                msg = rest[0]
                pid = self.eng.add_player(msg.get("name", ""), msg.get("token"))
                if pid is None:
                    self.host.send(cid, {"t": "err", "m": "full"})
                    continue
                for old, p in list(self.conn_pid.items()):      # stale connection of same seat
                    if p == pid and old != cid:
                        del self.conn_pid[old]
                        self.host._close(old)
                self.conn_pid[cid] = pid
                self.eng.set_connected(pid, True)
                self.host.send(cid, {"t": "welcome", "pid": pid})
                changed = True
            elif kind == "msg":
                pid = self.conn_pid.get(cid)
                msg = rest[0]
                if pid is not None and msg.get("t") == "act":
                    err = self._apply(pid, msg.get("a"), msg)
                    if err:
                        self.host.send(cid, {"t": "err", "m": err})
                    changed = True
            elif kind == "drop":
                pid = self.conn_pid.pop(cid, None)
                if pid is not None:
                    self.eng.set_connected(pid, False)
                    changed = True
        if changed:
            self._push()

    def _poll_client(self):
        while self.link and not self.link.q.empty():
            item = self.link.q.get()
            if item[0] == "status":
                self.on_event("link", item[1])
                continue
            msg = item[1]
            t = msg.get("t")
            if t == "welcome":
                self.my_pid = msg["pid"]
            elif t == "state":
                self.state = msg["s"]
                self.on_state(self.state)
            elif t == "err":
                self.on_event("error", msg.get("m"))
                if msg.get("m") == "full":
                    self.link.shutdown()
