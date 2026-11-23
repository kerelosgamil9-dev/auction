# -*- coding: utf-8 -*-
"""Pure-Python Arabic text shaping for Kivy (joins letters and fixes direction).
Kivy's SDL2 text provider does not shape Arabic, so every Arabic string shown in a
Label goes through shape() first. Keep the *logical* text everywhere else
(network, storage, TextInput) and shape only at display time."""
import textwrap

# letter -> (first presentation form, number of forms)
#   4 forms: isolated, final, initial, medial   2 forms: isolated, final   1: isolated only
_T = {0x621: (0xFE80, 1), 0x622: (0xFE81, 2), 0x623: (0xFE83, 2), 0x624: (0xFE85, 2),
      0x625: (0xFE87, 2), 0x626: (0xFE89, 4), 0x627: (0xFE8D, 2), 0x628: (0xFE8F, 4),
      0x629: (0xFE93, 2), 0x62A: (0xFE95, 4), 0x62B: (0xFE99, 4), 0x62C: (0xFE9D, 4),
      0x62D: (0xFEA1, 4), 0x62E: (0xFEA5, 4), 0x62F: (0xFEA9, 2), 0x630: (0xFEAB, 2),
      0x631: (0xFEAD, 2), 0x632: (0xFEAF, 2), 0x633: (0xFEB1, 4), 0x634: (0xFEB5, 4),
      0x635: (0xFEB9, 4), 0x636: (0xFEBD, 4), 0x637: (0xFEC1, 4), 0x638: (0xFEC5, 4),
      0x639: (0xFEC9, 4), 0x63A: (0xFECD, 4), 0x641: (0xFED1, 4), 0x642: (0xFED5, 4),
      0x643: (0xFED9, 4), 0x644: (0xFEDD, 4), 0x645: (0xFEE1, 4), 0x646: (0xFEE5, 4),
      0x647: (0xFEE9, 4), 0x648: (0xFEED, 2), 0x649: (0xFEEF, 2), 0x64A: (0xFEF1, 4)}
# lam + alef ligatures: alef code -> (isolated, final)
_LIG = {0x622: (0xFEF5, 0xFEF6), 0x623: (0xFEF7, 0xFEF8), 0x625: (0xFEF9, 0xFEFA), 0x627: (0xFEFB, 0xFEFC)}
_MIRROR = {"(": ")", ")": "(", "[": "]", "]": "[", "<": ">", ">": "<", "{": "}", "}": "{"}


def has_arabic(s):
    return any(0x600 <= ord(c) <= 0x6FF for c in s)


def reshape(s):
    s = "".join(c for c in s if not (0x64B <= ord(c) <= 0x65F or ord(c) == 0x640))
    out, i, n, prev_join = [], 0, len(s), False
    while i < n:
        c = s[i]
        o = ord(c)
        if o not in _T:
            out.append(c)
            prev_join = False
            i += 1
            continue
        if o == 0x644 and i + 1 < n and ord(s[i + 1]) in _LIG:          # lam-alef
            iso, fin = _LIG[ord(s[i + 1])]
            out.append(chr(fin if prev_join else iso))
            prev_join = False
            i += 2
            continue
        base, k = _T[o]
        nxt = i + 1 < n and ord(s[i + 1]) in _T and _T[ord(s[i + 1])][1] >= 2
        if k == 1:
            g = base
        elif k == 2:
            g = base + (1 if prev_join else 0)
        elif prev_join and nxt:
            g = base + 3
        elif prev_join:
            g = base + 1
        elif nxt:
            g = base + 2
        else:
            g = base
        out.append(chr(g))
        prev_join = (k == 4 and nxt)
        i += 1
    return "".join(out)


def _cls(c):
    o = ord(c)
    if 0x590 <= o <= 0x8FF or 0xFB1D <= o <= 0xFDFF or 0xFE70 <= o <= 0xFEFF:
        return "R"
    return "L" if c.isalnum() else "N"


def visual(s):
    """Logical -> visual order for a right-to-left paragraph."""
    cl = [_cls(c) for c in s]
    n, i = len(s), 0
    while i < n:                       # neutrals take the direction of their neighbours
        if cl[i] == "N":
            j = i
            while j < n and cl[j] == "N":
                j += 1
            left = cl[i - 1] if i > 0 else "R"
            right = cl[j] if j < n else "R"
            v = "L" if (left == "L" and right == "L") else "R"
            for k in range(i, j):
                cl[k] = v
            i = j
        else:
            i += 1
    runs = []
    for c, t in zip(s, cl):
        if runs and runs[-1][0] == t:
            runs[-1][1].append(c)
        else:
            runs.append([t, [c]])
    out = []
    for t, chars in reversed(runs):
        out.extend([_MIRROR.get(c, c) for c in reversed(chars)] if t == "R" else chars)
    return "".join(out)


def shape(text):
    """Return text ready for display (no-op for text without Arabic letters)."""
    if not text or not has_arabic(text):
        return text
    return "\n".join(visual(reshape(line)) for line in text.split("\n"))


def wrap(text, width):
    """Wrap the logical text first, then shape each line (so wrapped lines stay in order)."""
    if not has_arabic(text):
        return "\n".join(textwrap.wrap(text, width)) if width else text
    return "\n".join(shape(line) for line in textwrap.wrap(text, width))
