#!/usr/bin/env python3
"""news-image-20261119: draws a newspaper front page summing up the world news
of Thursday 19 November 2026 and writes it to /output/entry.png.

Pure Python 3.13 standard library only (zlib, struct, os). No network, no
fonts, no image libraries: all text is drawn with an embedded 5x7 bitmap font
and all art is drawn with simple shapes, so the output is byte-identical on
every run. Output: 1024x1024 PNG, well under 1 MiB.

Stories (all verified against Reuters / AP / NPR / NASA reporting on
19 November 2026, early edition):
  1. Anthropic starts trading on Nasdaq as ANT after a record $81.3bn IPO
     priced at $83 a share (NPR/AP, 18 Nov; trading begins 19 Nov).
  2. Trump, Xi and Putin hold their first-ever trilateral meeting in
     Shenzhen on the sidelines of APEC (Reuters, 18 Nov; meeting 19 Nov).
  3. The ICJ delivers its judgment in The Gambia v. Myanmar, the Rohingya
     genocide case (Reuters; judgment due 19 Nov).
  4. Grand Theft Auto VI rolls out worldwide at midnight local time,
     13 years after GTA V (Reuters, 19 Nov).
  5. NASA marks Voyager 1 reaching one light-day from Earth with a
     briefing on 19 Nov (NASA/Reuters; crossing 18 Nov).
  6. Iran widens its attacks on US bases in the Gulf: a US air base in
     Kuwait and sites in Bahrain (AP/Reuters, 18 Nov).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (24, 24, 28)
RED = (176, 32, 40)
NAVY = (26, 42, 74)
GOLD = (176, 132, 40)
GREY = (120, 116, 104)
WHITE = (255, 255, 255)
LIGHT = (232, 226, 212)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '1' = ink. Uppercase, lowercase, digits and
# the punctuation this poster uses.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10001"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}

CHAR_W = 6  # glyph advance in font units (5 px + 1 px gap)


def text_width(text, scale):
    return max(0, len(text) * CHAR_W - 1) * scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def rect(self, x, y, w, h, color, t=2):
        self.hline(x, y, w, color, t)
        self.hline(x, y + h - t, w, color, t)
        self.vline(x, y, h, color, t)
        self.vline(x + w - t, y, h, color, t)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, t=2):
        for yy in range(cy - r - 1, cy + r + 2):
            for xx in range(cx - r - 1, cx + r + 2):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= t / 2.0:
                    self.set(xx, yy, color)

    def text(self, x, y, s, scale, color, bold=False):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += CHAR_W * scale
                continue
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == '1':
                        self.fill_rect(cx + gx * scale, y + gy * scale,
                                       scale, scale, color)
                        if bold:
                            self.fill_rect(cx + gx * scale + 1,
                                           y + gy * scale, scale, scale,
                                           color)
            cx += CHAR_W * scale
        return cx

    def text_center(self, cx, y, s, scale, color, bold=False):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color, bold)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns list of lines, each <= max_w px."""
        words = s.split(' ')
        lines, cur = [], ''
        for word in words:
            trial = word if not cur else cur + ' ' + word
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, max_w, scale, color, leading=None):
        lines = self.wrap(s, max_w, scale)
        lh = (leading if leading is not None else 9 * scale)
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, scale, color)
        return y + len(lines) * lh


def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack('>I', len(data)) + kind + data
        return c + struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)

    out = b'\x89PNG\r\n\x1a\n'
    out += chunk(b'IHDR', struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2,
                                      0, 0, 0))
    out += chunk(b'IDAT', comp)
    out += chunk(b'IEND', b'')
    return out


# ------------------------------------------------------------------- icons
def draw_bar_chart(c, x, y, w, h):
    """IPO bar chart: Anthropic $81.3bn, SpaceX $75bn, Aramco 2019 $25.6bn."""
    c.text(x, y, "LARGEST IPOS, $BN", 2, GREY)
    base = y + h - 30
    bars = [("ANTHROPIC", "", 81.3, RED), ("SPACEX", "", 75.0, NAVY),
            ("ARAMCO", "2019", 25.6, GREY)]
    bw, gap = 70, 40
    top = y + 44
    for i, (label, sub, val, color) in enumerate(bars):
        bx = x + i * (bw + gap)
        bh = int((base - top) * val / 81.3)
        c.fill_rect(bx, base - bh, bw, bh, color)
        c.text_center(bx + bw // 2, base - bh - 18, f"{val:g}", 2, INK,
                      bold=True)
        c.text_center(bx + bw // 2, base + 6, label, 2, INK)
        if sub:
            c.text_center(bx + bw // 2, base + 22, sub, 2, INK)
    c.hline(x, base, w, INK, 2)


def draw_globe(c, cx, cy, r):
    """Globe with three stars: the three leaders' meeting."""
    c.ring(cx, cy, r, NAVY, 3)
    c.fill_rect(cx - r, cy - 2, 2 * r, 3, NAVY)
    c.line(cx - r + 8, cy - r + 14, cx + r - 8, cy + r - 14, NAVY, 2)
    c.line(cx - r + 8, cy + r - 14, cx + r - 8, cy - r + 14, NAVY, 2)
    for dx, dy in ((-r - 14, -r + 8), (r + 10, -r - 4), (0, r + 12)):
        sx, sy = cx + dx, cy + dy
        for px, py in ((0, -7), (6, -2), (4, 6), (-4, 6), (-6, -2)):
            c.line(sx, sy, sx + px, sy + py, RED, 2)


def draw_scales(c, cx, cy, s):
    """Scales of justice for the ICJ story."""
    c.vline(cx, cy - 34, 68, INK, 3)
    c.hline(cx - 34, cy - 34, 68, INK, 3)
    c.text_center(cx, cy - 58, "ICJ", 2, NAVY, bold=True)
    for side in (-1, 1):
        px = cx + side * 34
        c.line(px, cy - 34, px - 14, cy - 8, INK, 2)
        c.line(px, cy - 34, px + 14, cy - 8, INK, 2)
        c.line(px - 14, cy - 8, px + 14, cy - 8, INK, 2)
        c.disc(px, cy - 4, 3, RED)
    c.fill_rect(cx - 22, cy + 34, 44, 4, INK)


def draw_controller(c, x, y, w, h):
    """Game controller for the GTA VI story, sized to its icon box."""
    cx, cy = x + w // 2, y + h // 2
    hw = w // 2 - 6  # half-width of the body
    c.fill_rect(cx - hw, cy - 18, 2 * hw, 36, NAVY)
    c.disc(cx - hw, cy, 18, NAVY)
    c.disc(cx + hw, cy, 18, NAVY)
    # d-pad
    c.fill_rect(cx - hw + 8, cy - 5, 7, 16, WHITE)
    c.fill_rect(cx - hw + 3, cy, 17, 7, WHITE)
    # buttons
    for bx, by in ((hw - 24, -8), (hw - 14, 2), (hw - 24, 10), (hw - 34, 2)):
        c.disc(cx + bx, cy + by, 4, RED)
    c.disc(cx + 2, cy + 7, 5, WHITE)


def draw_voyager(c, cx, cy, r):
    """Satellite with solar panels under a star field: Voyager 1."""
    for sx, sy, sr in ((cx - r - 6, cy - r + 8, 2), (cx + r - 4, cy - r - 2, 2),
                       (cx + r + 8, cy + 6, 3), (cx - r + 10, cy + r - 4, 2)):
        c.disc(sx, sy, sr, GOLD)
    # dotted trajectory arc
    for t in range(0, 61):
        a = math.radians(200 + t * 1.6)
        c.disc(int(cx + r * 1.15 * math.cos(a)) + 6,
               int(cy + r * 0.8 * math.sin(a)) - 4, 2, NAVY)
    # satellite: gold panels, navy body, red beacon
    c.fill_rect(cx - 44, cy - 8, 26, 16, GOLD)
    c.fill_rect(cx + 18, cy - 8, 26, 16, GOLD)
    c.vline(cx - 18, cy - 8, 16, NAVY, 2)
    c.vline(cx + 18, cy - 8, 16, NAVY, 2)
    c.fill_rect(cx - 18, cy - 10, 36, 20, NAVY)
    c.disc(cx, cy, 4, RED)
    c.line(cx + 14, cy - 10, cx + 30, cy - 26, NAVY, 2)
    c.disc(cx + 30, cy - 26, 3, RED)


def draw_gulf_map(c, x, y, w, h):
    """Stylised Gulf: sea, coastline, three markers (Kuwait, Bahrain, Qeshm)."""
    c.fill_rect(x, y, w, h, (214, 228, 238))
    c.fill_rect(x, y, w // 2, h, (233, 224, 196))  # land (west)
    c.line(x + w // 2, y, x + w // 2 + 26, y + h, INK, 2)
    c.text(x + 8, y + 8, "GULF", 2, NAVY, bold=True)
    marks = [("KUWAIT", 0.62, 0.30), ("BAHRAIN", 0.58, 0.55),
             ("QESHM", 0.72, 0.78)]
    for label, fx, fy in marks:
        mx, my = x + int(w * fx), y + int(h * fy)
        c.disc(mx, my, 6, RED)
        c.ring(mx, my, 10, RED, 2)
        c.text(mx + 14, my - 7, label, 2, INK, bold=True)


# ------------------------------------------------------------------ layout
def story_cell(c, x, y, w, h, kicker, headline, summary, draw_icon):
    c.fill_rect(x, y, w, h, WHITE)
    c.rect(x, y, w, h, INK, 2)
    tx = x + 16
    c.text(tx, y + 14, kicker, 2, RED, bold=True)
    icon_w = 120
    lines = c.wrap(headline, w - 32 - icon_w, 3)
    ly = y + 40
    for ln in lines:
        c.text(tx, ly, ln, 3, INK, bold=True)
        ly += 30
    c.para(tx, ly + 4, summary, w - 32, 2, INK, leading=18)
    # Icon lives in the top-right corner only, above the summary, so the
    # summary's full-width lines never run underneath it.
    draw_icon(c, x + w - icon_w + 8, y + 40, icon_w - 16, 76)


def build():
    c = Canvas(W, H, PAPER)
    # outer frame
    c.rect(10, 10, W - 20, H - 20, INK, 3)
    c.rect(16, 16, W - 32, H - 32, INK, 1)

    # ---- masthead
    c.text_center(W // 2, 34, "THE WORLD TODAY", 6, INK, bold=True)
    c.hline(28, 108, W - 56, INK, 3)
    c.hline(28, 114, W - 56, INK, 1)
    c.text_center(W // 2, 126, "THURSDAY 19 NOVEMBER 2026", 3, RED, bold=True)
    c.text_center(W // 2, 152, "EARLY EDITION - SIX STORIES THAT SUM UP THE DAY",
                  2, INK)

    # ---- lead story: Anthropic IPO debut
    lx, ly, lw, lh = 28, 176, W - 56, 208
    c.fill_rect(lx, ly, lw, lh, WHITE)
    c.rect(lx, ly, lw, lh, INK, 2)
    c.text(lx + 16, ly + 14, "MARKETS - RECORD IPO", 2, RED, bold=True)
    c.text(lx + 16, ly + 42, "ANTHROPIC DEBUTS ON", 4, INK, bold=True)
    c.text(lx + 16, ly + 82, "NASDAQ AFTER RECORD", 4, INK, bold=True)
    c.text(lx + 16, ly + 122, "$81.3BN IPO", 4, INK, bold=True)
    c.para(lx + 16, ly + 168, "Priced at $83 a share, the biggest IPO on record.",
           600, 2, INK, leading=18)
    draw_bar_chart(c, lx + 640, ly + 14, 300, 180)

    # ---- 2x2 grid
    gy, gh, gap = 400, 188, 16
    cw = (W - 56 - gap) // 2
    story_cell(c, 28, gy, cw, gh, "DIPLOMACY - SHENZHEN",
               "TRUMP, XI AND PUTIN MEET FOR FIRST TIME",
               "First-ever trilateral talks at APEC. Nuclear arms, Iran and trade on the agenda.",
               lambda cc, x, y, w, h: draw_globe(cc, x + w // 2, y + 40, 26))
    story_cell(c, 28 + cw + gap, gy, cw, gh, "JUSTICE - THE HAGUE",
               "WORLD COURT RULES ON ROHINGYA CASE TODAY",
               "Judges decide whether Myanmar committed genocide. A first if a state is found guilty.",
               lambda cc, x, y, w, h: draw_scales(cc, x + w // 2, y + 48, 1))
    story_cell(c, 28, gy + gh + gap, cw, gh, "CULTURE - GAMING",
               "GTA VI ROLLS OUT AROUND THE WORLD",
               "Rockstar's sequel unlocks at midnight, 13 years after GTA V. Pre-orders passed $1.5bn.",
               draw_controller)
    story_cell(c, 28 + cw + gap, gy + gh + gap, cw, gh, "SPACE - NASA",
               "VOYAGER 1, ONE LIGHT-DAY FROM EARTH",
               "NASA marks the 1977 probe's milestone today. A radio signal now takes a day to reach it.",
               lambda cc, x, y, w, h: draw_voyager(cc, x + w // 2, y + 42, 26))

    # ---- bottom band: Gulf escalation
    bx, by, bw, bh = 28, 800, W - 56, 140
    c.fill_rect(bx, by, bw, bh, WHITE)
    c.rect(bx, by, bw, bh, INK, 2)
    c.text(bx + 16, by + 12, "CONFLICT - THE GULF", 2, RED, bold=True)
    c.text(bx + 16, by + 38, "IRAN WIDENS ATTACKS ON US BASES", 3, INK, bold=True)
    c.text(bx + 16, by + 68, "IN THE GULF", 3, INK, bold=True)
    c.para(bx + 16, by + 98, "Tehran hit a US air base in Kuwait and sites in Bahrain after US jets struck Qeshm Island.",
           660, 2, INK, leading=18)
    draw_gulf_map(c, bx + 700, by + 14, 260, 112)

    # ---- footer strip
    c.hline(28, 952, W - 56, INK, 2)
    c.text_center(W // 2, 962,
                  "ALSO: EU PROPOSES A 45BN-EURO LOAN FOR UKRAINE",
                  2, NAVY, bold=True)
    c.text_center(W // 2, 984,
                  "SOURCES: REUTERS, AP, NPR, NASA - EARLY EDITION, 19 NOV 2026",
                  2, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)
    print(f"wrote {len(data)} bytes to {out_dir}/entry.png")


if __name__ == "__main__":
    main()
