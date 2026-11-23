# -*- coding: utf-8 -*-
"""Offline multiplayer over Wi-Fi / phone hotspot (no internet needed).

* Host phone runs a TCP server (PORT) and announces the room by UDP broadcast (DISC_PORT).
* Clients find rooms through the broadcast, or type the host IP by hand.
* All threads only push tuples into a queue.Queue; the Kivy main thread drains it,
  so game state is never touched from two threads.
* Messages are JSON lines. A client keeps a token so it can reconnect to the same seat.
"""
import json
import queue
import socket
import threading
import time

PORT = 52345
DISC_PORT = 52346
MAGIC = "AUCTION_LAN_V1"


def local_ip():
    """Best guess of this phone's LAN / hotspot address (works with no internet).
    Also works on the phone that *creates* the hotspot (it has no default route)."""
    targets = ("192.168.43.255", "192.168.49.255", "192.168.137.255", "172.20.10.255", "192.168.1.255",
               "192.168.0.255", "192.168.2.255", "10.0.0.255", "10.255.255.255", "172.16.255.255", "8.8.8.8")
    for target in targets:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.connect((target, 1))
            ip = s.getsockname()[0]
            if ip and not ip.startswith(("127.", "0.")):
                return ip
        except OSError:
            pass
        finally:
            s.close()
    return "127.0.0.1"


def _kill(sock):
    """Close a socket right away even if another thread is blocked in recv()."""
    for fn in (lambda: sock.shutdown(socket.SHUT_RDWR), sock.close):
        try:
            fn()
        except OSError:
            pass


def _send(sock, obj):
    sock.sendall((json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8"))


def _lines(sock, stop):
    """Yield decoded JSON objects from a socket until it closes."""
    buf = b""
    sock.settimeout(1.0)
    while not stop.is_set():
        try:
            data = sock.recv(65536)
        except socket.timeout:
            continue
        except OSError:
            return
        if not data:
            return
        buf += data
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            if line.strip():
                try:
                    yield json.loads(line.decode("utf-8"))
                except ValueError:
                    pass


class HostServer:
    """Events put into self.q:  ("join", cid, msg) ("msg", cid, msg) ("drop", cid)"""

    def __init__(self, room_name):
        self.q = queue.Queue()
        self.room_name = room_name
        self.stop = threading.Event()
        self.clients = {}            # cid -> socket
        self.lock = threading.Lock()
        self.next_cid = 1
        self.players = 1
        self.srv = None

    def start(self):
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind(("", PORT))
        self.srv.listen(8)
        self.srv.settimeout(1.0)
        threading.Thread(target=self._accept, daemon=True).start()
        threading.Thread(target=self._announce, daemon=True).start()

    def _accept(self):
        while not self.stop.is_set():
            try:
                conn, _addr = self.srv.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            with self.lock:
                cid = self.next_cid
                self.next_cid += 1
                self.clients[cid] = conn
            threading.Thread(target=self._reader, args=(cid, conn), daemon=True).start()

    def _reader(self, cid, conn):
        for msg in _lines(conn, self.stop):
            self.q.put(("join" if msg.get("t") == "join" else "msg", cid, msg))
        self._close(cid)
        self.q.put(("drop", cid))

    def _close(self, cid):
        with self.lock:
            conn = self.clients.pop(cid, None)
        if conn:
            _kill(conn)

    def _announce(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while not self.stop.is_set():
            data = json.dumps({"magic": MAGIC, "name": self.room_name, "port": PORT,
                               "players": self.players}, ensure_ascii=False).encode("utf-8")
            ip = local_ip()
            subnet = ip.rsplit(".", 1)[0] + ".255"      # directed broadcast reaches the hotspot interface
            for addr in ("255.255.255.255", subnet):
                try:
                    s.sendto(data, (addr, DISC_PORT))
                except OSError:
                    pass
            time.sleep(1.0)
        s.close()

    def send(self, cid, obj):
        with self.lock:
            conn = self.clients.get(cid)
        if conn:
            try:
                conn.settimeout(2.0)
                _send(conn, obj)
            except OSError:
                self._close(cid)
                self.q.put(("drop", cid))

    def broadcast(self, obj, cids):
        for cid in list(cids):
            self.send(cid, obj)

    def shutdown(self):
        self.stop.set()
        for cid in list(self.clients):
            self._close(cid)
        if self.srv:
            _kill(self.srv)


class ClientLink:
    """Events put into self.q: ("msg", msg) ("status", "up"|"down"|"fail")
    Reconnects by itself (same token => same seat) once the first join succeeded."""

    def __init__(self, ip, name, token):
        self.q = queue.Queue()
        self.ip, self.name, self.token = ip, name, token
        self.stop = threading.Event()
        self.sock = None
        self.joined = False

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while not self.stop.is_set():
            try:
                s = socket.create_connection((self.ip, PORT), timeout=4)
                self.sock = s
                _send(s, {"t": "join", "name": self.name, "token": self.token})
                self.q.put(("status", "up"))
                for msg in _lines(s, self.stop):
                    if msg.get("t") == "welcome":
                        self.joined = True
                    self.q.put(("msg", msg))
                self.q.put(("status", "down"))
            except OSError:
                if not self.joined:
                    self.q.put(("status", "fail"))
                    return
                self.q.put(("status", "down"))
            self.sock = None
            if not self.joined:
                return
            for _ in range(20):                # wait 2 s, then retry
                if self.stop.is_set():
                    return
                time.sleep(0.1)

    def send(self, obj):
        s = self.sock
        if s:
            try:
                s.settimeout(2.0)
                _send(s, obj)
            except OSError:
                pass

    def shutdown(self):
        self.stop.set()
        if self.sock:
            _kill(self.sock)


class Discovery:
    """Listens for room announcements. Events: ("found", ip, info)"""

    def __init__(self):
        self.q = queue.Queue()
        self.stop = threading.Event()

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", DISC_PORT))
        except OSError:
            return
        s.settimeout(1.0)
        while not self.stop.is_set():
            try:
                data, addr = s.recvfrom(2048)
                info = json.loads(data.decode("utf-8"))
                if info.get("magic") == MAGIC:
                    self.q.put(("found", addr[0], info))
            except (socket.timeout, ValueError):
                continue
            except OSError:
                break
        s.close()

    def shutdown(self):
        self.stop.set()
