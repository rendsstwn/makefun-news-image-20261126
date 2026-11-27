#!/usr/bin/env python3
"""Render the 26 November 2026 world-news front page (v5).

One 1024x1024 PNG. Everything is drawn with PIL primitives on a cream
newsprint background: a giant date masthead, a big-number strip, coloured
region chips, a UTC timeline, three illustrated leads, ten illustrated grid
cards, a dotted world map with numbered pins, a numbered ALSO ON list, and
a DATE CHECK footer. No network, no clock, no randomness: the same input
always produces the same bytes.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (26, 26, 26)
MUTED = (90, 84, 72)
RULE = (150, 30, 30)
NAVY = (24, 42, 78)
GOLD = (176, 132, 24)
TEAL = (14, 110, 110)
CRIMSON = (178, 34, 34)
SKY = (70, 130, 180)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"

STATUS_FILL = {
    "OFFICIAL": (18, 90, 60),
    "CONFIRMED": (24, 42, 78),
    "REPORTED": (120, 90, 10),
    "CLAIM": (150, 60, 10),
    "ONGOING": (90, 60, 120),
}

REGION_FILL = {
    "EUROPE": (52, 84, 160),
    "N. AMERICA": (178, 34, 34),
    "MIDDLE EAST": (150, 90, 20),
    "S. ASIA": (20, 120, 90),
    "E. ASIA": (120, 40, 110),
    "AFRICA": (110, 110, 20),
    "S. AMERICA": (20, 130, 130),
    "SE ASIA": (200, 120, 20),
    "OCEANIA": (60, 140, 90),
    "WORLD": (100, 100, 100),
}

# (number, region, status, place, topic, headline, deck, why, source)
LEADS = [
    (1, "N. AMERICA", "OFFICIAL", "WASHINGTON", "TRADE",
     "Trump unveils tariffs on 14 partners",
     "Section 301 duties proposed on 14 economies: China 20%, India 25%, "
     "Vietnam up to 35%, EU 15%.",
     "WHY IT MATTERS - The biggest trade move of the year - but nothing "
     "is in force; comments due 5 Jan.",
     "USTR - REUTERS"),
    (2, "N. AMERICA", "REPORTED", "NEW YORK", "WEATHER",
     "Macy's 100th parade postponed",
     "A nor'easter brings 60 mph gusts to New York; the parade moves to "
     "Saturday, a first in 100 years.",
     "WHY IT MATTERS - The day's most iconic event, grounded by weather; "
     "250,000 lose power on the coast.",
     "AP"),
    (3, "EUROPE", "CONFIRMED", "KYIV", "WAR",
     "Russia's missiles pound Kyiv overnight",
     "Ballistic missiles hit a shopping centre and two buildings; seven "
     "wounded, two seriously.",
     "WHY IT MATTERS - Moscow vows more strikes in reply; 113 drones "
     "launched across Ukraine overnight.",
     "MAYOR'S OFFICE - REUTERS"),
]

# (number, region, status, place, topic, headline, deck, source, scene)
GRID = [
    (4, "E. ASIA", "OFFICIAL", "PYONGYANG", "NUCLEAR",
     "Kim orders wider nuclear deployment",
     "KCNA: tactical nukes forward.",
     "KCNA - YONHAP", "missile"),
    (5, "MIDDLE EAST", "REPORTED", "HORMUZ", "MARITIME",
     "Two tankers hit naval mines in the Strait",
     "Mines strike vessels off Dubai.",
     "US OFFICIALS - UKMTO", "tanker"),
    (6, "AFRICA", "OFFICIAL", "DR CONGO", "HEALTH",
     "Congo Ebola cases pass 12,000",
     "12,021 confirmed, 5,904 dead.",
     "HEALTH MINISTRY - REUTERS", "chart"),
    (7, "EUROPE", "CONFIRMED", "BRUSSELS", "SUMMIT",
     "EU deadlocked on \u20ac45bn Ukraine loan",
     "Leaders meet for two days.",
     "EURONEWS - COUNCIL", "stars"),
    (8, "E. ASIA", "OFFICIAL", "SEOUL", "ECONOMY",
     "Bank of Korea lifts rate to 3.25%",
     "Third hike since July, 5-2 vote.",
     "BOK - REUTERS", "gauge"),
    (9, "S. ASIA", "CONFIRMED", "MUMBAI", "ANNIVERSARY",
     "India marks 18 years since 26/11",
     "Mumbai honours 2008 victims.",
     "PTI", "candles"),
    (10, "EUROPE", "ONGOING", "GENEVA", "CHESS",
     "Gukesh v Sindarov, Game 3",
     "Candidates level at 1-1.",
     "FIDE", "chess"),
    (11, "S. ASIA", "CONFIRMED", "DHAKA", "LABOUR",
     "Bangladesh garment wage Tk17,000",
     "Minimum pay up 36% Thursday.",
     "AFP", "wage"),
    (12, "MIDDLE EAST", "REPORTED", "GAZA", "WAR",
     "Israel kills Hamas economy chief",
     "Khaled Abu Nada dies Thursday.",
     "IDF", "blast"),
    (13, "EUROPE", "REPORTED", "KYIV", "WAR",
     "Russia hits Ukraine with 113 drones",
     "Seven regions lose power.",
     "KYIV POST", "drones"),
]

# (number, region, headline, source)
ALSO = [
    (14, "SE ASIA", "Myanmar faces ICJ genocide order", "ICJ"),
    (15, "AFRICA", "Ramaphosa gives eulogy at Mlambo-Ngcuka funeral", "SABC"),
    (16, "S. ASIA", "India A meet Sri Lanka A in semi-final", "Cricbuzz"),
    (17, "WORLD", "Hera shows DART crater on Dimorphos", "ESA"),
    (18, "SE ASIA", "Malaysia sues Google for $146m over YouTube", "Reuters"),
    (19, "AFRICA", "Nigeria busts $227m meth lab", "NDLEA"),
    (20, "N. AMERICA", "US jobless claims fall to 189,000", "Labor Dept"),
    (21, "EUROPE", "EU caps hybrid car imports from China", "EC"),
    (22, "EUROPE", "Boehly signs $10bn swap for Lukoil assets", "Eldridge"),
    (23, "MIDDLE EAST", "IS attack in Hasakah kills 29 in Syria", "SANA"),
    (24, "S. ASIA", "IPL 2027 auction lists 1,220 players", "BCCI"),
    (25, "S. AMERICA", "Brazil calls US tariff 'unacceptable'", "Brasilia"),
    (26, "S. AMERICA", "Argentina names ambassador to Brazil", "Buenos Aires"),
    (27, "N. AMERICA", "Puerto Rico seals Luma power deal", "San Juan"),
    (28, "MIDDLE EAST", "U-17 World Cup quarter-final places decided", "FIFA"),
    (29, "EUROPE", "North Korea opens Swiss office - to close", "KCNA"),
    (30, "N. AMERICA", "Vance meets Huang; chip curbs on table", "White House"),
    (31, "E. ASIA", "Lee orders seed projects fast-tracked", "Seoul"),
    (32, "E. ASIA", "Xi probe widens to Shanghai chief Chen Jining", "Beijing"),
    (33, "S. AMERICA", "Brazil dengue down 68% on vaccine push", "Fiocruz"),
    (34, "OCEANIA", "Solomon Islands signs pact with Australia", "Canberra"),
    (35, "MIDDLE EAST", "Coalition hits Hodeidah port targets", "Riyadh"),
    (36, "MIDDLE EAST", "UN sacks Gaza staff over unproven claims", "The Guardian"),
    (37, "AFRICA", "Saudi national kidnapped by 15 men in Niger", "Niamey"),
    (38, "N. AMERICA", "Plane crashes in Gulf of Mexico, 2 missing", "USCG"),
    (39, "EUROPE", "PIA resumes UK flights with Boeing 777", "Karachi"),
    (40, "S. ASIA", "IITs add 6,000 seats for next academic year", "New Delhi"),
    (41, "OCEANIA", "Australia inflation at 4.9%", "ABS"),
    (42, "S. ASIA", "India-Nepal sign \u20b915,000cr package", "New Delhi"),
    (43, "N. AMERICA", "Tempus pays $600m cash in Personalus deal", "SEC filing"),
    (44, "S. AMERICA", "Colombia frees 20 supermarket hostages", "Bogota"),
    (45, "AFRICA", "Sudan RSF strikes kill 19 in Blue Nile", "Khartoum"),
    (46, "EUROPE", "Savasleyka jets scrambled; five hit", "Kyiv"),
    (47, "EUROPE", "UK-EU publish reset treaties", "London"),
    (48, "EUROPE", "Spain sends army to El Hierro", "Madrid"),
    (49, "E. ASIA", "Kospi claws back +0.3%", "KRX"),
    (50, "EUROPE", "BBC: 490,334 Russian soldiers dead", "BBC"),
]

BIG_NUMBERS = [
    ("14", "economies in US tariff plan"),
    ("\u20ac45bn", "EU aid proposed for Ukraine"),
    ("12,021", "Ebola cases in DR Congo"),
    ("3.25%", "Bank of Korea's new rate"),
    ("100th", "Macy's parade"),
    ("490,334", "Russian soldiers dead, BBC"),
]

REGIONS = [
    ("EUROPE", 12), ("N. AMERICA", 7), ("MIDDLE EAST", 6),
    ("S. ASIA", 6), ("E. ASIA", 5), ("AFRICA", 5),
    ("S. AMERICA", 4), ("SE ASIA", 2), ("OCEANIA", 2), ("WORLD", 1),
]

UTC_ITEMS = [
    ("00:41", "BBC 490,334"),
    ("02:13", "UK-EU texts"),
    ("09:25", "Kospi 4,711"),
    ("10:04", "10-yr clause"),
    ("15:00", "Gukesh Game 3"),
    ("17:40", "Myanmar ICJ"),
]


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit in width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def status_tag(draw, x, y, label):
    """Right-aligned status pill; returns its left edge."""
    fnt = font(SANS_B, 10)
    w = int(draw.textlength(label, font=fnt)) + 12
    fill = STATUS_FILL[label]
    draw.rounded_rectangle([x - w, y, x, y + 14], radius=3, fill=fill)
    draw.text((x - w + 6, y + 2), label, font=fnt, fill=(255, 255, 255))
    return x - w


def num_badge(draw, cx, cy, n):
    """Numbered circle badge centred at (cx, cy)."""
    r = 11
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RULE,
                 outline=(255, 255, 255), width=1)
    fnt = font(SANS_B, 11)
    txt = str(n)
    tw = draw.textlength(txt, font=fnt)
    draw.text((cx - tw / 2, cy - 8), txt, font=fnt, fill=(255, 255, 255))

# ---------------------------------------------------------------------------
# Illustrations. Every scene is drawn from primitives so the page stays
# self-contained and deterministic. Each takes (draw, x, y, w, h).
# ---------------------------------------------------------------------------

def scene_tariff(draw, x, y, w, h):
    """Bar chart of proposed tariff rates by economy."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 240, 244))
    draw.rectangle([x, y, x + w, y + 18], fill=NAVY)
    fnt = font(SANS_B, 11)
    draw.text((x + 8, y + 3), "14 PARTNERS", font=fnt, fill=(255, 255, 255))
    bars = [("CHINA", 20, (178, 34, 34)), ("INDIA", 25, (200, 110, 20)),
            ("EU", 15, (52, 84, 160)), ("JAPAN", 15, (20, 120, 90))]
    bw = (w - 40) // 4
    base = y + h - 22
    for i, (name, rate, col) in enumerate(bars):
        bx = x + 14 + i * bw
        bh = int((h - 52) * rate / 25.0)
        draw.rectangle([bx, base - bh, bx + bw - 12, base], fill=col)
        lf = font(SANS_B, 12)
        lab = "%d%%" % rate
        draw.text((bx + (bw - 12) / 2 - draw.textlength(lab, font=lf) / 2,
                   base - bh - 15), lab, font=lf, fill=INK)
        sf = font(SANS, 9)
        draw.text((bx, base + 4), name, font=sf, fill=MUTED)


def scene_balloon(draw, x, y, w, h):
    """Night skyline with a big parade balloon and rain."""
    draw.rectangle([x, y, x + w, y + h], fill=(28, 38, 74))
    for bx, bh in [(0, 42), (46, 58), (92, 36), (140, 62), (188, 44),
                   (236, 56), (282, 40)]:
        draw.rectangle([x + bx, y + h - bh, x + bx + 42, y + h],
                       fill=(16, 24, 52))
        for wy in range(y + h - bh + 8, y + h - 4, 12):
            draw.rectangle([x + bx + 6, wy, x + bx + 12, wy + 6],
                           fill=(240, 200, 80))
    for rx in range(x + 10, x + w - 6, 26):
        draw.line([rx, y + 12, rx - 6, y + 30], fill=(160, 180, 220), width=1)
    cx, cy = x + w // 2, y + h // 2 - 6
    draw.ellipse([cx - 52, cy - 34, cx + 52, cy + 34], fill=(214, 48, 49))
    draw.ellipse([cx - 38, cy - 28, cx - 18, cy - 8], fill=(240, 120, 120))
    draw.line([cx - 52, cy + 34, cx - 30, cy + 58], fill=(120, 40, 40), width=2)
    draw.line([cx + 52, cy + 34, cx + 30, cy + 58], fill=(120, 40, 40), width=2)
    draw.ellipse([x + w - 52, y + 8, x + w - 12, y + 48], fill=(240, 200, 80))
    bf = font(SANS_B, 20)
    draw.text((x + w - 42, y + 16), "100", font=bf, fill=(26, 26, 26))


def scene_kyiv(draw, x, y, w, h):
    """Night skyline with missile trails and a casualty callout."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 20, 34))
    for sx, sy in [(20, 14), (70, 26), (130, 10), (190, 22), (250, 12),
                   (290, 28), (110, 34), (230, 36)]:
        draw.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3],
                     fill=(255, 255, 255))
    for bx, bh in [(0, 46), (52, 66), (104, 52), (156, 74), (210, 48),
                   (262, 60), (300, 42)]:
        draw.rectangle([x + bx, y + h - bh, x + bx + 44, y + h],
                       fill=(8, 10, 22))
    draw.arc([x + 30, y + 8, x + 180, y + 88], start=200, end=330,
             fill=(255, 180, 60), width=3)
    draw.arc([x + 120, y + 2, x + 300, y + 96], start=210, end=320,
             fill=(255, 120, 40), width=3)
    draw.ellipse([x + 168, y + 26, x + 178, y + 36], fill=(255, 200, 90))
    draw.ellipse([x + 288, y + 18, x + 298, y + 28], fill=(255, 200, 90))
    draw.rectangle([x + w - 96, y + 10, x + w - 8, y + 32], fill=CRIMSON)
    wf = font(SANS_B, 13)
    draw.text((x + w - 90, y + 14), "7 WOUNDED", font=wf,
              fill=(255, 255, 255))


def scene_missile(draw, x, y, w, h):
    """Missile launcher silhouette against a dusk sky."""
    draw.rectangle([x, y, x + w, y + h], fill=(52, 58, 74))
    draw.rectangle([x, y + h - 14, x + w, y + h], fill=(30, 32, 40))
    draw.rectangle([x + 18, y + h - 30, x + 92, y + h - 14], fill=(20, 22, 30))
    for wx in (28, 48, 68):
        draw.rectangle([x + wx, y + h - 12, x + wx + 12, y + h - 4],
                       fill=(60, 64, 78))
    draw.line([x + 110, y + h - 26, x + w - 30, y + 22], fill=(200, 200, 210),
              width=6)
    draw.polygon([(x + w - 30, y + 22), (x + w - 14, y + 30),
                  (x + w - 26, y + 38)], fill=(200, 60, 40))
    draw.ellipse([x + w - 56, y + 6, x + w - 24, y + 38], fill=(240, 200, 80))
    kf = font(SANS_B, 11)
    draw.text((x + w - 50, y + 16), "HW-31", font=kf, fill=(26, 26, 26))
    draw.ellipse([x + 14, y + 10, x + 20, y + 16], fill=(255, 220, 120))
    draw.ellipse([x + 40, y + 22, x + 44, y + 26], fill=(255, 220, 120))


def scene_tanker(draw, x, y, w, h):
    """Oil tanker on the sea with a mine, drawn inside its band."""
    draw.rectangle([x, y, x + w, y + h], fill=(150, 190, 210))
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(40, 90, 130))
    for wx in range(x + 8, x + w - 8, 30):
        draw.line([wx, y + h - 8, wx + 16, y + h - 8],
                  fill=(120, 170, 200), width=2)
    draw.rectangle([x + 16, y + 14, x + w - 52, y + h - 10],
                   fill=(140, 40, 40))
    draw.rectangle([x + w - 46, y + 6, x + w - 30, y + 14],
                   fill=(200, 200, 200))
    draw.rectangle([x + w - 42, y + 2, x + w - 34, y + 6],
                   fill=(120, 120, 120))
    draw.ellipse([x + w - 26, y + 6, x + w - 8, y + 24], fill=(60, 60, 60))
    import math
    for ang in range(0, 360, 45):
        dx = math.cos(math.radians(ang)) * 9
        dy = math.sin(math.radians(ang)) * 9
        draw.line([x + w - 17 + dx * 0.5, y + 15 + dy * 0.5,
                   x + w - 17 + dx, y + 15 + dy], fill=(60, 60, 60), width=2)
    draw.polygon([(x + 26, y + 14), (x + 34, y + 2), (x + 42, y + 14)],
                 fill=(255, 160, 40))

def scene_chart(draw, x, y, w, h):
    """Rising case bars for the Ebola count."""
    draw.rectangle([x, y, x + w, y + h], fill=(240, 236, 224))
    vals = [0.25, 0.4, 0.55, 0.75, 1.0]
    bw = (w - 24) // 5
    base = y + h - 10
    for i, v in enumerate(vals):
        bx = x + 10 + i * bw
        bh = int((h - 26) * v)
        col = (200, 60, 40) if i == 4 else (120, 120, 120)
        draw.rectangle([bx, base - bh, bx + bw - 6, base], fill=col)
    cf = font(SANS_B, 12)
    draw.text((x + 8, y + 4), "12,021", font=cf, fill=CRIMSON)


def scene_stars(draw, x, y, w, h):
    """Circle of EU stars over a bar chart."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 42, 78))
    cx, cy = x + w // 2, y + h // 2
    import math
    for k in range(12):
        ang = math.radians(k * 30 - 90)
        sx = cx + int(math.cos(ang) * 34)
        sy = cy + int(math.sin(ang) * 26)
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(240, 200, 80))
    draw.rectangle([cx - 34, cy - 8, cx + 34, cy + 8], fill=(240, 200, 80))
    sf = font(SANS_B, 11)
    draw.text((cx - 26, cy - 7), "\u20ac45bn", font=sf, fill=NAVY)


def scene_gauge(draw, x, y, w, h):
    """Rate steps climbing to 3.25%."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 240, 244))
    pts = [(x + 12, y + h - 16), (x + w // 3, y + h - 26),
           (x + 2 * w // 3, y + h - 36), (x + w - 14, y + h - 52)]
    draw.line(pts, fill=(24, 42, 78), width=3)
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=CRIMSON)
    gf = font(SANS_B, 13)
    draw.text((x + w - 62, y + 4), "3.25%", font=gf, fill=CRIMSON)
    sf = font(SANS, 9)
    draw.text((x + 8, y + h - 14), "3.00", font=sf, fill=MUTED)


def scene_candles(draw, x, y, w, h):
    """Row of memorial candles with flames."""
    draw.rectangle([x, y, x + w, y + h], fill=(40, 34, 30))
    for i in range(5):
        cx = x + 18 + i * ((w - 36) // 4)
        draw.rectangle([cx - 6, y + h - 26, cx + 6, y + h - 8],
                       fill=(240, 230, 200))
        draw.ellipse([cx - 4, y + h - 36, cx + 4, y + h - 26],
                     fill=(255, 180, 60))
    draw.rectangle([x + w - 52, y + 6, x + w - 8, y + 24], fill=(240, 200, 80))
    nf = font(SANS_B, 11)
    draw.text((x + w - 48, y + 9), "18 YRS", font=nf, fill=(26, 26, 26))


def scene_chess(draw, x, y, w, h):
    """Chessboard with two clocks at 1:32 each."""
    draw.rectangle([x, y, x + w, y + h], fill=(30, 50, 40))
    sq = (h - 16) // 4
    ox, oy = x + 10, y + 8
    for r in range(4):
        for c in range(4):
            col = (240, 235, 220) if (r + c) % 2 == 0 else (60, 70, 60)
            draw.rectangle([ox + c * sq, oy + r * sq,
                            ox + (c + 1) * sq, oy + (r + 1) * sq], fill=col)
    draw.ellipse([ox + sq + 1, oy + sq + 1, ox + 2 * sq - 1, oy + 2 * sq - 1],
                 fill=(20, 20, 20))
    draw.ellipse([ox + 2 * sq + 1, oy + 2 * sq + 1,
                  ox + 3 * sq - 1, oy + 3 * sq - 1], fill=(245, 245, 245))
    draw.rectangle([x + w - 96, y + 6, x + w - 8, y + 26], fill=(240, 240, 240))
    tf = font(SANS_B, 11)
    draw.text((x + w - 90, y + 10), "1:32  1:32", font=tf, fill=INK)


def scene_wage(draw, x, y, w, h):
    """Wage bars: old pay vs new pay."""
    draw.rectangle([x, y, x + w, y + h], fill=(240, 238, 228))
    draw.rectangle([x + 14, y + h - 22, x + 74, y + h - 10], fill=(150, 150, 150))
    draw.rectangle([x + 14, y + 12, x + 74, y + h - 10], fill=(20, 120, 90))
    wf = font(SANS_B, 12)
    draw.text((x + 82, y + 8), "Tk17,000", font=wf, fill=(20, 120, 90))
    draw.text((x + 82, y + 24), "+36%", font=wf, fill=CRIMSON)


def scene_blast(draw, x, y, w, h):
    """Explosion flash over a dark street."""
    draw.rectangle([x, y, x + w, y + h], fill=(30, 28, 34))
    cx, cy = x + w // 2, y + h // 2
    for rr, col in [(17, (255, 120, 40)), (12, (255, 180, 60)),
                    (7, (255, 240, 160))]:
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    for bx, bh in [(0, 26), (60, 36), (130, 24)]:
        draw.rectangle([x + bx, y + h - bh, x + bx + 56, y + h],
                       fill=(12, 12, 16))


def scene_drones(draw, x, y, w, h):
    """Drone silhouettes crossing a pale sky, one downed."""
    draw.rectangle([x, y, x + w, y + h], fill=(200, 215, 225))
    for dx, dy in [(16, 14), (70, 26), (120, 12)]:
        draw.line([x + dx, y + dy, x + dx + 26, y + dy], fill=(40, 40, 40),
                  width=3)
        draw.line([x + dx + 13, y + dy - 6, x + dx + 13, y + dy + 6],
                  fill=(40, 40, 40), width=3)
    draw.line([x + w - 60, y + 16, x + w - 30, y + h - 20], fill=(150, 60, 40),
              width=2)
    draw.ellipse([x + w - 44, y + h - 26, x + w - 28, y + h - 10],
                 fill=(150, 60, 40))
    df = font(SANS_B, 12)
    draw.text((x + 8, y + h - 18), "113", font=df, fill=CRIMSON)


SCENES = {
    "tariff": scene_tariff, "balloon": scene_balloon, "kyiv": scene_kyiv,
    "missile": scene_missile, "tanker": scene_tanker, "chart": scene_chart,
    "stars": scene_stars, "gauge": scene_gauge, "candles": scene_candles,
    "chess": scene_chess, "wage": scene_wage, "blast": scene_blast,
    "drones": scene_drones,
}

LEAD_SCENES = ["tariff", "balloon", "kyiv"]

# ---------------------------------------------------------------------------
# Dotted world map. Land is a hand-drawn 72x18 dot grid; pins are placed
# by (col, row) coordinates on that grid.
# ---------------------------------------------------------------------------

MAP_ROWS = [
    "                 ##                  ###############               ",
    "  #############  ##       ####      ##################             ",
    "  #############         #######     ###################   #        ",
    "  ##########           ########     #################    #        ",
    "  ########            ##########    ##############               ",
    "  ######        ##   ##########  ##########  ########             ",
    "  ####            #############  ###  #############               ",
    "   ###             ############  ###   ##########                 ",
    "    ##             ###########        #######  ####               ",
    "     ######        ##########          ###                       ",
    "     ######        #########                                     ",
    "     #####         ########           #########                  ",
    "      ####          ######            #########                  ",
    "      ###           #####             ########                   ",
    "      ##                                                     ",
    "      ##                                                     ",
    "      #                                                      ",
    "                                                             ",
]

# (story number, map col, map row)
PINS = [
    (1, 9, 5), (2, 12, 5), (3, 38, 3), (4, 62, 4), (5, 45, 6),
    (6, 38, 9), (7, 34, 3), (8, 64, 6), (9, 54, 7), (10, 36, 5),
    (11, 56, 7), (12, 43, 6), (13, 40, 3),
]


def draw_map(draw, x, y, w, h):
    """Dotted continents with numbered red pins for stories 1-13."""
    cols = max(len(r) for r in MAP_ROWS)
    rows = len(MAP_ROWS)
    step_x = w / cols
    step_y = h / rows
    dot = (150, 148, 138)
    for ry, row in enumerate(MAP_ROWS):
        for cx, ch in enumerate(row):
            if ch == "#":
                px = x + cx * step_x + step_x / 2
                py = y + ry * step_y + step_y / 2
                draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=dot)
    for n, col, row in PINS:
        px = x + col * step_x + step_x / 2
        py = y + row * step_y + step_y / 2
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=CRIMSON,
                     outline=(255, 255, 255), width=1)
        fnt = font(SANS_B, 9)
        txt = str(n)
        tw = draw.textlength(txt, font=fnt)
        draw.text((px - tw / 2, py - 6), txt, font=fnt, fill=(255, 255, 255))


def draw_masthead(draw):
    """Kicker line, giant date, sub-deck, big numbers, regions, UTC."""
    draw.rectangle([0, 0, W, 4], fill=RULE)
    kf = font(SANS_B, 11)
    draw.text((14, 8), "THE WORLD IN ONE DAY", font=kf, fill=INK)
    rt = "50 STORIES  \u00b7  10 REGIONS  \u00b7  THURSDAY 26 NOVEMBER 2026"
    draw.text((W - 14 - draw.textlength(rt, font=kf), 8), rt, font=kf,
              fill=MUTED)
    df = font(SERIF_B, 48)
    date = "Thursday 26 November 2026"
    draw.text(((W - draw.textlength(date, font=df)) / 2, 26), date, font=df,
              fill=INK)
    sf = font(SERIF, 15)
    deck = ("Trump unveils tariffs on 14 partners  \u00b7  Russia's missiles "
            "hit Kyiv  \u00b7  Macy's 100th parade postponed")
    draw.text(((W - draw.textlength(deck, font=sf)) / 2, 82), deck, font=sf,
              fill=MUTED)
    # Big-number strip.
    y0, y1 = 100, 138
    cw = (W - 28) / 6
    bf = font(SERIF_B, 26)
    lf = font(SANS, 9)
    for i, (num, lab) in enumerate(BIG_NUMBERS):
        cx = 14 + i * cw
        if i:
            draw.line([cx, y0 + 4, cx, y1 - 4], fill=(200, 192, 172), width=1)
        draw.text((cx + (cw - draw.textlength(num, font=bf)) / 2, y0 + 2),
                  num, font=bf, fill=CRIMSON if i in (0, 2, 3, 5) else INK)
        draw.text((cx + (cw - draw.textlength(lab, font=lf)) / 2, y0 + 32),
                  lab, font=lf, fill=MUTED)
    draw.line([14, y1, W - 14, y1], fill=INK, width=1)
    # Region chips.
    y = 144
    rx = 14
    rf = font(SANS_B, 10)
    for name, count in REGIONS:
        label = "%s %d" % (name, count)
        tw = draw.textlength(label, font=rf) + 14
        draw.rounded_rectangle([rx, y, rx + tw, y + 18], radius=3,
                               fill=REGION_FILL[name])
        draw.text((rx + 7, y + 3), label, font=rf, fill=(255, 255, 255))
        rx += tw + 5
    # UTC strip.
    y = 164
    draw.rectangle([0, y, W, y + 18], fill=NAVY)
    uf = font(SANS_B, 11)
    draw.text((14, y + 4), "THE DAY IN UTC", font=uf, fill=(240, 200, 80))
    parts = ["%s %s" % item for item in UTC_ITEMS]
    ux = 150
    for part in parts:
        draw.text((ux, y + 4), part, font=uf, fill=(255, 255, 255))
        ux += draw.textlength(part, font=uf) + 26

def draw_leads(draw):
    """Three illustrated lead cards."""
    y0, y1 = 192, 428
    cw = (W - 28 - 16) // 3
    for i, lead in enumerate(LEADS):
        n, region, status, place, topic, head, deck, why, src = lead
        x = 14 + i * (cw + 8)
        draw.rectangle([x, y0, x + cw, y1], outline=(190, 182, 164), width=1)
        SCENES[LEAD_SCENES[i]](draw, x + 1, y0 + 1, cw - 2, 96)
        num_badge(draw, x + 16, y0 + 110, n)
        tf = font(SANS_B, 10)
        draw.text((x + 32, y0 + 102), "%s \u00b7 %s" % (place, topic),
                  font=tf, fill=REGION_FILL[region])
        status_tag(draw, x + cw - 8, y0 + 102, status)
        hf = font(SERIF_B, 19)
        ly = y0 + 122
        for line in wrap(draw, head, hf, cw - 16)[:2]:
            draw.text((x + 8, ly), line, font=hf, fill=INK)
            ly += 22
        df = font(SANS, 11)
        ly = y0 + 168
        for line in wrap(draw, deck, df, cw - 16)[:2]:
            draw.text((x + 8, ly), line, font=df, fill=(60, 56, 48))
            ly += 14
        wf = font(SANS_B, 10)
        ly = y0 + 196
        for line in wrap(draw, why, wf, cw - 16)[:2]:
            draw.text((x + 8, ly), line, font=wf, fill=CRIMSON)
            ly += 13
        sf = font(SANS, 9)
        draw.text((x + 8, y1 - 13), src, font=sf, fill=MUTED)


def draw_grid(draw):
    """Ten illustrated grid cards in two rows of five."""
    y0 = 436
    rows = [GRID[:5], GRID[5:]]
    cw = (W - 28 - 32) // 5
    ch = 100
    for ri, row in enumerate(rows):
        y = y0 + ri * (ch + 8)
        for ci, card in enumerate(row):
            n, region, status, place, topic, head, deck, src, scene = card
            x = 14 + ci * (cw + 8)
            draw.rectangle([x, y, x + cw, y + ch],
                           outline=(190, 182, 164), width=1)
            SCENES[scene](draw, x + 1, y + 1, cw - 2, 40)
            num_badge(draw, x + 13, y + 52, n)
            tf = font(SANS_B, 8)
            draw.text((x + 26, y + 46), "%s \u00b7 %s" % (place, topic),
                      font=tf, fill=REGION_FILL[region])
            status_tag(draw, x + cw - 6, y + 46, status)
            hf = font(SERIF_B, 12)
            for li, line in enumerate(wrap(draw, head, hf, cw - 12)[:2]):
                draw.text((x + 6, y + 60 + li * 14), line, font=hf, fill=INK)
            df = font(SANS, 9)
            dlines = wrap(draw, deck, df, cw - 12)
            if dlines:
                draw.text((x + 6, y + 88), dlines[0], font=df,
                          fill=(60, 56, 48))


def draw_map_section(draw):
    """Where it happened: dotted map plus the HOW SURE legend."""
    y = 652
    hf = font(SANS_B, 11)
    draw.text((14, y), "WHERE IT HAPPENED \u2014 PINS 1\u201313",
              font=hf, fill=INK)
    draw.line([14, y + 16, W - 14, y + 16], fill=INK, width=1)
    draw_map(draw, 14, y + 22, 640, 70)
    lx = 676
    draw.text((lx, y + 22), "HOW SURE", font=hf, fill=INK)
    legend = [
        ("OFFICIAL", "an authority's own word"),
        ("CONFIRMED", "two or more major outlets"),
        ("REPORTED", "one outlet so far"),
        ("CLAIM", "one side's account, unverified"),
        ("ONGOING", "still unfolding"),
    ]
    lf = font(SANS, 9)
    ly = y + 40
    for label, desc in legend:
        draw.rectangle([lx, ly, lx + 62, ly + 11], fill=STATUS_FILL[label])
        bf = font(SANS_B, 8)
        draw.text((lx + 4, ly + 1), label, font=bf, fill=(255, 255, 255))
        draw.text((lx + 68, ly + 1), desc, font=lf, fill=MUTED)
        ly += 14


def draw_also(draw):
    """Numbered ALSO ON list, three columns."""
    y = 750
    hf = font(SANS_B, 11)
    draw.text((14, y), "AND ALSO \u2014 STORIES 14\u201350",
              font=hf, fill=INK)
    draw.line([14, y + 16, W - 14, y + 16], fill=INK, width=1)
    cols = [ALSO[:13], ALSO[13:25], ALSO[25:]]
    cw = (W - 28 - 24) / 3
    af = font(SANS, 10)
    nf = font(SANS_B, 10)
    for ci, col in enumerate(cols):
        x = 14 + ci * (cw + 12)
        for ri, (n, region, head, src) in enumerate(col):
            yy = y + 24 + ri * 15
            draw.text((x, yy), str(n), font=nf, fill=REGION_FILL[region])
            draw.text((x + 22, yy), head, font=af, fill=INK)
            sw = draw.textlength(" \u2014 " + src, font=af)
            draw.text((x + cw - sw, yy), " \u2014 " + src, font=af,
                      fill=MUTED)


def draw_footer(draw):
    """DATE CHECK box and the sources line."""
    y = 972
    draw.rectangle([14, y, W - 14, y + 30], outline=RULE, width=2)
    bf = font(SANS_B, 10)
    draw.text((22, y + 3), "DATE CHECK", font=bf, fill=RULE)
    ff = font(SANS, 10)
    line1 = ("Every story above happened, or was first reported, on "
             "Thursday 26 November 2026 (UTC).")
    draw.text((22, y + 16), line1, font=ff, fill=INK)
    line2 = ("Left out as earlier news: Huawei guilty verdict (Tue 24 Nov) "
             "\u00b7 Nvidia record surge (Mon 23 Nov) \u00b7 Shenzhou-24 "
             "docking at Tiangong (25 Nov).")
    draw.text((W - 14 - draw.textlength(line2, font=ff), y + 3), line2,
              font=ff, fill=MUTED)
    sf = font(SANS, 8)
    srcs = ("Sources: USTR, Reuters, AP, AFP, BBC, KCNA, BOK, FIDE, PTI, "
            "Euronews, Yonhap. Scenes are drawn illustrations, not "
            "photographs.")
    draw.text((14, 1008), srcs, font=sf, fill=MUTED)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_leads(draw)
    draw_grid(draw)
    draw_map_section(draw)
    draw_also(draw)
    draw_footer(draw)
    return img


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build().save(out, "PNG")
