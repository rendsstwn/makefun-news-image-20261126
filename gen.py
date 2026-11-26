#!/usr/bin/env python3
"""Render THE WORLD IN ONE DAY - 26 November 2026, 50 stories, one image.

Fresh build for the make.fun news-image-20261126 bounty, v3.
Cream-paper newspaper front page: masthead, region strip, UTC timeline,
big-number strip, three illustrated leads, ten-card grid, numbered world
map, ALSO ON list, DATE CHECK footer. Deterministic: same input bytes
always produce the same output PNG.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 227)
PAPER_DARK = (238, 231, 210)
INK = (26, 23, 18)
INK_SOFT = (74, 68, 58)
RED = (163, 29, 29)
NAVY = (30, 58, 95)
NAVY_DARK = (22, 44, 74)
GOLD = (185, 138, 29)
GOLD_SOFT = (214, 178, 94)
OCEAN = (216, 230, 236)
LAND = (232, 220, 192)
LAND_LINE = (176, 160, 120)
RULE = (26, 23, 18)
HAIR = (150, 142, 124)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def fnt(path, size):
    return ImageFont.truetype(path, size)


F = {
    "mast": fnt(SERIF_B, 57),
    "mast_sub": fnt(SANS_B, 13),
    "strip": fnt(SANS_B, 10),
    "strip_n": fnt(SANS, 10),
    "utc_lab": fnt(SANS_B, 10),
    "utc": fnt(SANS, 10),
    "stat_n": fnt(SERIF_B, 26),
    "stat_l": fnt(SANS_B, 8),
    "sec": fnt(SANS_B, 12),
    "lead_h": fnt(SERIF_B, 20),
    "lead_d": fnt(SANS, 11),
    "lead_w": fnt(SERIF, 11),
    "lead_data": fnt(SANS_B, 11),
    "tag": fnt(SANS_B, 8),
    "grid_h": fnt(SERIF_B, 13),
    "grid_d": fnt(SANS, 10),
    "grid_data": fnt(SANS_B, 10),
    "map_n": fnt(SANS_B, 9),
    "also": fnt(SANS, 9),
    "also_n": fnt(SANS_B, 10),
    "foot": fnt(SANS, 9),
    "foot_b": fnt(SANS_B, 9),
}

# (number, region, status, headline, deck, data line, why-it-matters, art kind)
LEADS = [
    (
        1, "NEW YORK", "OFFICIAL",
        "MACY\u2019S 100TH PARADE POSTPONED",
        "Thanksgiving storm grounds the centenary march;",
        "60 mph gusts force the parade to Saturday 28 Nov.",
        "100th \u00b7 60 mph \u00b7 Sat 28 Nov",
        "The day\u2019s most iconic event, moved by weather \u2014 a century of tradition waits two days.",
        "balloon",
    ),
    (
        2, "PYONGYANG", "OFFICIAL",
        "KIM ORDERS WIDER NUCLEAR DEPLOYMENT",
        "KCNA: tactical nuclear weapons to go to front-line",
        "units in a wider deployment ordered on Thursday.",
        "Tactical \u00b7 Front-line \u00b7 KCNA",
        "Pyongyang\u2019s sharpest escalation signal of the year, in its own words.",
        "missile",
    ),
    (
        3, "SEOUL", "OFFICIAL",
        "BANK OF KOREA LIFTS RATE TO 3.25%",
        "Third hike since July, by a 5\u20132 vote; the bank lifts",
        "its 2027 growth outlook to 4.1% on AI exports.",
        "3.25% \u00b7 5\u20132 vote \u00b7 4.1% growth",
        "Seoul tightens while its chip market whipsaws \u2014 the rate call and the rout, one day.",
        "rates",
    ),
]

# (number, region, status, headline, deck, data line, icon kind)
GRID = [
    (
        4, "BRUSSELS", "REPORTED",
        "EU DEADLOCKED ON \u20ac45bn UKRAINE LOAN",
        "Summit stalls; Bulgaria backs only the civilian \u20ac20bn part.",
        "\u20ac45bn \u00b7 Merz veto threat",
        "stars",
    ),
    (
        5, "MUMBAI", "OFFICIAL",
        "INDIA MARKS 18 YEARS SINCE 26/11",
        "Mumbai honours the 2008 attack victims on Constitution Day.",
        "18 years \u00b7 Samvidhan Divas",
        "gate",
    ),
    (
        6, "GENEVA", "OFFICIAL",
        "GUKESH v SINDAROV, GAME 3",
        "Candidates match level at 1\u20131 after two draws; play 15:00 CET.",
        "1\u20131 \u00b7 15:00 CET",
        "chess",
    ),
    (
        7, "DHAKA", "REPORTED",
        "BANGLADESH GARMENT WAGE Tk17,000",
        "Minimum pay up 36% from Tk12,500; board finalises it Thursday.",
        "Tk17,000 \u00b7 +36%",
        "shirt",
    ),
    (
        8, "LONDON", "REPORTED",
        "BBC: 490,334 RUSSIAN SOLDIERS DEAD",
        "Leaked Rosstat data put the toll far above official counts.",
        "490,334 \u00b7 Rosstat leak",
        "helmet",
    ),
    (
        9, "GAZA", "REPORTED",
        "ISRAEL KILLS HAMAS ECONOMY CHIEF",
        "Khaled Abu Nada killed in an overnight strike on Thursday.",
        "Overnight \u00b7 Thu 26 Nov",
        "flame",
    ),
    (
        10, "KYIV", "REPORTED",
        "RUSSIA HITS UKRAINE WITH 113 DRONES",
        "Overnight barrage plus ballistic missiles; seven regions lose power.",
        "113 drones \u00b7 7 regions",
        "drone",
    ),
    (
        11, "LONDON", "REPORTED",
        "UK\u2013EU PUBLISH RESET TREATIES",
        "Food and emissions texts out Thursday; 10-year break clause inside.",
        "10-year clause \u00b7 Thu pm",
        "treaty",
    ),
    (
        12, "EL HIERRO", "REPORTED",
        "SPAIN SENDS ARMY TO EL HIERRO",
        "Record 2,100 arrivals in one day overwhelm the tiny island.",
        "2,100 in a day \u00b7 UME deploys",
        "boat",
    ),
    (
        13, "SEOUL", "REPORTED",
        "KOSPI CLAWS BACK +0.3%",
        "Closes 4,711 after Wednesday\u2019s 6.2% rout; SK hynix +2.2%.",
        "+0.29% \u00b7 4,711.21",
        "chart",
    ),
]

# (number, headline, source) - the day's remaining stories, in brief.
ALSO = [
    (14, "Myanmar refuses ICJ genocide orders", "Reuters"),
    (15, "Ramaphosa to give eulogy at Mlambo-Ngcuka funeral", "SAnews"),
    (16, "India A meet Sri Lanka A in Rising Stars semi-final", "Cricbuzz"),
    (17, "Hera shows DART crater: Dimorphos flattened", "ESA / Reuters"),
    (18, "Malaysia sues Google for $146m over YouTube", "MCMC"),
    (19, "Nigeria seizes $227m meth lab, 5 Mexicans held", "NDLEA"),
    (20, "US jobless claims fall to 189,000", "Labor Dept"),
    (21, "EU caps hybrid car imports; China quota 191,780", "EC"),
    (22, "Boehly signs $10bn swap for Lukoil assets", "Eldridge"),
    (23, "IS attack in Hasakah kills 2 Syrian security", "SANA"),
    (24, "IPL 2027 auction list: 1,220 players", "BCCI"),
    (25, "Brazil calls US tariff \u201cunacceptable\u201d", "Brasilia"),
    (26, "Argentina names new ambassador to Brazil", "Buenos Aires"),
    (27, "Puerto Rico seals Luma power deal", "San Juan"),
    (28, "U-17 World Cup: quarter-final places decided", "FIFA"),
    (29, "North Korea orders Swiss office to close", "KCNA"),
    (30, "Korail work-to-rule protest disrupts trains", "Seoul"),
    (31, "Vance: Huang never under investigation", "White House"),
    (32, "Lee orders seven seed projects fast-tracked", "Seoul"),
    (33, "Xi probe widens to Shanghai chief Chen Jining", "Beijing"),
    (34, "Brazil mosquitoes cut dengue cases 68%", "Fiocruz"),
    (35, "Palm Beach ferries strike strands commuters", "Florida"),
    (36, "Swiss tourist survives elephant charge, Cameroon", "Yaounde"),
    (37, "Army blows up 5 tonnes of explosives in Iowa", "US Army"),
    (38, "Coalition jets hit Hodeidah port targets", "Riyadh"),
    (39, "UN sacks Gaza staff over neutrality breaches", "UN"),
    (40, "Saudi national kidnapped by 15 men in Niger", "Niamey"),
    (41, "Plane crashes in Gulf of Mexico, 2 missing", "USCG"),
    (42, "PIA resumes UK flights with Boeing 777", "Karachi"),
    (43, "IITs add 6,000 seats for next academic year", "New Delhi"),
    (44, "Australia inflation hits 4.9%, three-year high", "ABS"),
    (45, "India\u2013Nepal sign \u20b915,000cr package", "New Delhi"),
    (46, "Tempus picks $600m cash in Personalis deal", "SEC filing"),
    (47, "Colombia frees 20 supermarket hostages", "Bogota"),
    (48, "Sudan RSF strikes kill 19 in Blue Nile", "Khartoum"),
    (49, "Savasleyka: five jets destroyed in strike", "Kyiv"),
    (50, "Solomon Islands signs Australia security pact", "Canberra"),
]

REGIONS = [
    ("NORTH AMERICA", 8), ("EUROPE", 8), ("ASIA", 14),
    ("MIDDLE EAST", 4), ("AFRICA", 5), ("SOUTH AMERICA", 4),
    ("OCEANIA", 2), ("SPORT", 4), ("SCIENCE", 1),
]

# (UTC time, event) - the day as it unfolded.
TIMELINE = [
    ("00:41", "BBC 490,334"),
    ("02:13", "UK\u2013EU texts"),
    ("09:25", "Kospi 4,711"),
    ("10:04", "10-yr clause"),
    ("15:00", "Gukesh Game 3"),
    ("17:40", "Myanmar ICJ"),
]

# (big number, label) - the day in six figures.
BIG_NUMBERS = [
    ("100th", "MACY\u2019S PARADE"),
    ("490,334", "RUSSIAN DEAD"),
    ("3.25%", "BANK OF KOREA"),
    ("2,100", "EL HIERRO ARRIVALS"),
    ("Tk17,000", "GARMENT WAGE"),
    ("113", "DRONES OVERNIGHT"),
]

# (lon, lat) pins for the 13 numbered map dots, stories 1-13.
PINS = [
    (-74.0, 41.0), (127.0, 39.0), (127.0, 37.5), (4.4, 50.8),
    (72.8, 19.0), (6.1, 46.2), (90.4, 23.8), (37.6, 55.7),
    (34.5, 31.5), (30.5, 50.4), (-0.1, 51.5), (-18.0, 27.8),
    (127.0, 37.5),
]


def wrap(draw, text, font, width):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tag_box(draw, x, y, status):
    """Small status tag; returns its width."""
    col = {"OFFICIAL": NAVY, "REPORTED": (94, 94, 84), "CLAIM": RED}[status]
    w = int(draw.textlength(status, font=F["tag"])) + 12
    draw.rectangle([x, y, x + w, y + 14], fill=col)
    draw.text((x + 6, y + 3), status, font=F["tag"], fill=(255, 255, 255))
    return w


def paint_icon(draw, kind, x0, y0, s):
    """One small flat illustration per grid card, drawn in a s x s box."""
    cx, cy = x0 + s // 2, y0 + s // 2
    if kind == "stars":
        draw.ellipse([x0 + 4, y0 + 4, x0 + s - 4, y0 + s - 4],
                     outline=NAVY, width=2)
        for k in range(9):
            import math
            a = -math.pi / 2 + k * 2 * math.pi / 9
            px = cx + int(0.30 * s * math.cos(a))
            py = cy + int(0.30 * s * math.sin(a))
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=GOLD)
    elif kind == "gate":
        draw.rectangle([x0 + 6, y0 + s - 8, x0 + s - 6, y0 + s - 4], fill=INK)
        draw.arc([x0 + 10, y0 + 8, x0 + s - 10, y0 + s - 6],
                 start=180, end=360, fill=RED, width=4)
        draw.line([x0 + 10, y0 + s - 8, x0 + 10, y0 + s // 2], fill=RED, width=4)
        draw.line([x0 + s - 10, y0 + s - 8, x0 + s - 10, y0 + s // 2],
                  fill=RED, width=4)
        draw.rectangle([x0 + s // 2 - 6, y0 + 4, x0 + s // 2 + 6, y0 + 10],
                       fill=GOLD)
    elif kind == "chess":
        for r in range(4):
            for c in range(4):
                if (r + c) % 2 == 0:
                    draw.rectangle([x0 + 4 + c * 9, y0 + 4 + r * 9,
                                    x0 + 12 + c * 9, y0 + 12 + r * 9],
                                   fill=INK)
        draw.ellipse([x0 + 8, y0 + 8, x0 + 18, y0 + 18], fill=RED)
    elif kind == "shirt":
        draw.polygon([(cx, y0 + 6), (x0 + s - 6, y0 + 14), (x0 + s - 10, y0 + 24),
                      (x0 + s - 8, y0 + s - 6), (x0 + 8, y0 + s - 6),
                      (x0 + 10, y0 + 24), (x0 + 6, y0 + 14)],
                     outline=NAVY, width=2)
        draw.text((cx - 8, cy - 5), "Tk", font=F["tag"], fill=NAVY)
    elif kind == "helmet":
        draw.arc([x0 + 6, y0 + 6, x0 + s - 6, y0 + s - 10],
                 start=180, end=360, fill=INK, width=5)
        draw.line([x0 + 4, y0 + s - 12, x0 + s - 4, y0 + s - 12],
                  fill=INK, width=4)
        draw.line([cx, y0 + 4, cx, y0 + 10], fill=RED, width=3)
    elif kind == "flame":
        draw.polygon([(cx, y0 + 4), (x0 + s - 8, y0 + s - 12), (cx + 4, y0 + s - 6),
                      (x0 + 8, y0 + s - 12)], fill=RED)
        draw.ellipse([cx - 5, cy - 2, cx + 5, cy + 8], fill=GOLD)
    elif kind == "drone":
        for dx, dy in [(-12, -10), (12, -10), (-12, 10), (12, 10)]:
            draw.ellipse([cx + dx - 5, cy + dy - 3, cx + dx + 5, cy + dy + 3],
                         outline=INK, width=2)
        draw.rectangle([cx - 8, cy - 5, cx + 8, cy + 5], fill=NAVY)
        draw.line([cx - 12, cy - 10, cx + 12, cy + 10], fill=INK, width=1)
        draw.line([cx + 12, cy - 10, cx - 12, cy + 10], fill=INK, width=1)
    elif kind == "treaty":
        draw.rectangle([x0 + 8, y0 + 4, x0 + s - 8, y0 + s - 4],
                       outline=INK, width=2, fill=(255, 255, 255))
        for i in range(4):
            draw.line([x0 + 13, y0 + 12 + i * 7, x0 + s - 13, y0 + 12 + i * 7],
                      fill=INK_SOFT, width=2)
        draw.ellipse([x0 + s - 18, y0 + s - 16, x0 + s - 8, y0 + s - 6],
                     fill=RED)
    elif kind == "boat":
        draw.polygon([(x0 + 6, cy + 2), (x0 + s - 6, cy + 2), (x0 + s - 12, cy + 10),
                      (x0 + 12, cy + 10)], fill=(122, 74, 32))
        for dx in (-10, 0, 10):
            draw.ellipse([cx + dx - 3, cy - 8, cx + dx + 3, cy - 2], fill=INK)
        draw.arc([x0 + 4, cy + 8, x0 + s - 4, cy + 18], start=0, end=180,
                 fill=NAVY, width=2)
    else:  # chart
        draw.line([(x0 + 6, y0 + s - 10), (x0 + 14, y0 + 18),
                   (x0 + 24, y0 + 26), (x0 + 32, y0 + 10),
                   (x0 + s - 6, y0 + 14)], fill=RED, width=3)
        draw.polygon([(x0 + s - 10, y0 + 10), (x0 + s - 4, y0 + 14),
                      (x0 + s - 10, y0 + 18)], fill=RED)


def paint_lead_art(draw, kind, x0, y0, w, h):
    """Distinct illustrated banner for each of the three leads."""
    if kind == "balloon":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(58, 94, 138))
        for bx in range(0, w, 46):
            draw.rectangle([x0 + bx, y0 + h - 26, x0 + bx + 26, y0 + h],
                           fill=(38, 60, 88))
            draw.rectangle([x0 + bx + 10, y0 + h - 40, x0 + bx + 16, y0 + h - 26],
                           fill=(52, 80, 116))
        draw.ellipse([x0 + 30, y0 + 8, x0 + 150, y0 + 96], fill=(214, 62, 52))
        draw.ellipse([x0 + 52, y0 + 8, x0 + 128, y0 + 96], fill=(232, 84, 70))
        draw.ellipse([x0 + 74, y0 + 8, x0 + 106, y0 + 96], fill=(246, 241, 227))
        draw.polygon([(x0 + 82, y0 + 96), (x0 + 98, y0 + 96), (x0 + 90, y0 + 116)],
                     fill=(122, 74, 32))
        draw.ellipse([x0 + 210, y0 + 14, x0 + 262, y0 + 34], fill=(246, 241, 227))
        draw.ellipse([x0 + 240, y0 + 8, x0 + 300, y0 + 28], fill=(246, 241, 227))
        draw.ellipse([x0 + 196, y0 + 62, x0 + 240, y0 + 78], fill=(230, 228, 220))
        draw.ellipse([x0 + w - 52, y0 + h - 52, x0 + w - 8, y0 + h - 8],
                     outline=GOLD, width=3)
        draw.text((x0 + w - 42, y0 + h - 42), "100", font=F["lead_data"],
                  fill=GOLD)
    elif kind == "missile":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(24, 30, 44))
        draw.polygon([(x0 + 60, y0 + h - 12), (x0 + 130, y0 + 18),
                      (x0 + 210, y0 + 30), (x0 + 250, y0 + 70),
                      (x0 + 190, y0 + h - 12)], fill=(52, 66, 92))
        draw.polygon([(x0 + 130, y0 + 18), (x0 + 210, y0 + 30),
                      (x0 + 250, y0 + 70), (x0 + 210, y0 + 88),
                      (x0 + 150, y0 + 60)], fill=(74, 92, 122))
        cx, cy = x0 + 60, y0 + 44
        draw.polygon([(cx, cy - 16), (cx + 5, cy - 5), (cx + 16, cy),
                      (cx + 5, cy + 5), (cx, cy + 16), (cx - 5, cy + 5),
                      (cx - 16, cy), (cx - 5, cy - 5)], fill=RED)
        draw.line([x0 + 40, y0 + 96, x0 + 250, y0 + 20], fill=GOLD, width=3)
        draw.polygon([(x0 + 250, y0 + 20), (x0 + 232, y0 + 18),
                      (x0 + 244, y0 + 34)], fill=GOLD)
        draw.ellipse([x0 + w - 46, y0 + 10, x0 + w - 10, y0 + 46],
                     outline=GOLD, width=2)
        draw.text((x0 + w - 36, y0 + 20), "KCNA", font=F["tag"], fill=GOLD)
    else:  # rates
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 58, 95))
        base = y0 + h - 18
        draw.rectangle([x0 + 46, base - 34, x0 + 116, base], fill=(120, 148, 184))
        draw.rectangle([x0 + 150, base - 62, x0 + 220, base], fill=GOLD)
        draw.text((x0 + 62, base - 52), "3.00", font=F["lead_data"],
                  fill=(230, 236, 244))
        draw.text((x0 + 166, base - 80), "3.25", font=F["lead_data"],
                  fill=(255, 255, 255))
        draw.line([x0 + 116, base - 34, x0 + 150, base - 62], fill=(255, 255, 255),
                  width=3)
        draw.polygon([(x0 + 150, base - 62), (x0 + 138, base - 58),
                      (x0 + 148, base - 48)], fill=(255, 255, 255))
        draw.ellipse([x0 + w - 74, y0 + 12, x0 + w - 12, y0 + 52], fill=RED)
        draw.text((x0 + w - 62, y0 + 24), "5\u20132", font=F["lead_data"],
                  fill=(255, 255, 255))
        draw.text((x0 + 18, y0 + 14), "KRW", font=F["lead_data"],
                  fill=(214, 178, 94))


def lonlat(lon, lat, x0, y0, w, h):
    """Squashed equirectangular projection into the map box."""
    px = x0 + int((lon + 180.0) / 360.0 * w)
    py = y0 + int((75.0 - lat) / 130.0 * h)
    return px, py


# Rough continent outlines (stylised, recognisable at small size).
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 70), (-95, 68), (-80, 62), (-60, 55),
     (-65, 45), (-75, 35), (-80, 26), (-90, 20), (-100, 16), (-110, 24),
     (-125, 40), (-125, 55), (-150, 60), (-168, 66)],
    [(-10, 36), (0, 38), (10, 44), (20, 45), (30, 46), (40, 48), (30, 55),
     (20, 60), (10, 62), (5, 58), (-5, 50), (-10, 44), (-10, 36)],
    [(30, 32), (35, 36), (43, 40), (50, 38), (58, 38), (60, 30), (66, 25),
     (72, 20), (78, 15), (80, 8), (88, 22), (92, 22), (100, 16), (105, 10),
     (110, 20), (120, 30), (127, 38), (135, 43), (140, 45), (142, 50),
     (135, 60), (120, 70), (100, 72), (80, 70), (60, 68), (45, 65),
     (40, 55), (35, 45), (30, 32)],
    [(60, 60), (70, 68), (90, 70), (120, 70), (150, 68), (170, 66),
     (178, 64), (160, 60), (140, 55), (120, 55), (100, 58), (80, 60),
     (60, 60)],
    [(-18, 35), (-10, 30), (-5, 30), (10, 33), (20, 32), (32, 31),
     (35, 28), (40, 20), (43, 12), (48, 10), (51, 12), (43, 5),
     (40, -2), (35, -10), (30, -18), (25, -28), (20, -35), (15, -30),
     (12, -18), (10, -5), (8, 4), (0, 6), (-8, 5), (-15, 12),
     (-17, 20), (-18, 35)],
    [(112, -12), (122, -14), (132, -12), (142, -11), (150, -20),
     (153, -28), (150, -37), (140, -38), (130, -32), (120, -34),
     (114, -30), (112, -22), (112, -12)],
    [(-80, 10), (-70, 10), (-60, 0), (-50, -5), (-40, -10), (-35, -20),
     (-45, -30), (-55, -35), (-65, -40), (-70, -30), (-75, -20),
     (-80, -5), (-80, 10)],
]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Top bars.
    d.rectangle([0, 0, W, 6], fill=INK)
    d.rectangle([0, 6, W, 8], fill=RED)

    # Masthead.
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=F["mast"])
    d.text(((W - tw) / 2, 12), title, font=F["mast"], fill=INK)
    sub = "THURSDAY 26 NOVEMBER 2026  \u00b7  50 STORIES  \u00b7  9 REGIONS  \u00b7  ONE DAY, ONE PAGE"
    sw = d.textlength(sub, font=F["mast_sub"])
    d.text(((W - sw) / 2, 80), sub, font=F["mast_sub"], fill=INK_SOFT)
    d.line([16, 100, W - 16, 100], fill=RULE, width=2)
    d.line([16, 103, W - 16, 103], fill=HAIR, width=1)

    # Region strip.
    parts = []
    for name, n in REGIONS:
        parts.append((name + " ", True))
        parts.append((str(n) + " \u00b7 ", False))
    total = sum(d.textlength(t, font=F["strip" if b else "strip_n"])
                for t, b in parts[:-1])
    cx = (W - total) / 2
    for t, b in parts[:-1]:
        f = F["strip"] if b else F["strip_n"]
        d.text((cx, 110), t, font=f, fill=INK)
        cx += d.textlength(t, font=f)

    # UTC timeline.
    lab = "THE DAY IN UTC"
    d.text((16, 130), lab, font=F["utc_lab"], fill=RED)
    lx = 16 + d.textlength(lab, font=F["utc_lab"]) + 14
    for t, ev in TIMELINE:
        cell = t + "  " + ev
        d.text((lx, 130), cell, font=F["utc"], fill=INK_SOFT)
        lx += d.textlength(cell, font=F["utc"]) + 16

    # Big-number strip.
    d.rectangle([16, 154, W - 16, 196], fill=NAVY_DARK)
    cell_w = (W - 32) / 6
    for i, (num, lab2) in enumerate(BIG_NUMBERS):
        x0 = 16 + i * cell_w
        if i:
            d.line([x0, 160, x0, 190], fill=(90, 112, 148), width=1)
        nw = d.textlength(num, font=F["stat_n"])
        d.text((x0 + (cell_w - nw) / 2, 158), num, font=F["stat_n"],
               fill=(255, 255, 255))
        lw = d.textlength(lab2, font=F["stat_l"])
        d.text((x0 + (cell_w - lw) / 2, 184), lab2, font=F["stat_l"],
               fill=GOLD_SOFT)

    # Three leads.
    lead_w, gap = 320, 16
    for i, lead in enumerate(LEADS):
        (num, region, status, head, deck1, deck2, data, why, kind) = lead
        x0 = 16 + i * (lead_w + gap)
        paint_lead_art(d, kind, x0, 202, lead_w, 96)
        d.rectangle([x0, 202, x0 + lead_w, 298], outline=INK, width=1)
        d.text((x0, 304), str(num) + ".  " + region, font=F["tag"], fill=RED)
        tag_box(d, x0 + lead_w - 62, 302, status)
        lines = wrap(d, head, F["lead_h"], lead_w)
        yy = 322
        for ln in lines[:3]:
            d.text((x0, yy), ln, font=F["lead_h"], fill=INK)
            yy += 23
        d.text((x0, yy + 6), deck1, font=F["lead_d"], fill=INK_SOFT)
        d.text((x0, yy + 19), deck2, font=F["lead_d"], fill=INK_SOFT)
        wlines = wrap(d, "WHY IT MATTERS: " + why, F["lead_w"], lead_w)
        wy = yy + 36
        for ln in wlines[:2]:
            d.text((x0, wy), ln, font=F["lead_w"], fill=INK)
            wy += 13
        d.text((x0, wy + 4), data, font=F["lead_data"], fill=RED)
        if i < 2:
            d.line([x0 + lead_w + 8, 202, x0 + lead_w + 8, 440],
                   fill=HAIR, width=1)

    # Grid header + ten cards.
    d.text((16, 448), "THE DAY IN TEN \u2014 STORIES 4\u201313",
           font=F["sec"], fill=INK)
    d.line([16, 466, W - 16, 466], fill=RULE, width=1)
    card_w, card_h = 490, 42
    for i, card in enumerate(GRID):
        (num, region, status, head, deck, data, kind) = card
        col, row = i % 2, i // 2
        x0 = 16 + col * (card_w + 12)
        y0 = 472 + row * 44
        paint_icon(d, kind, x0, y0, 40)
        tx = x0 + 48
        d.text((tx, y0), str(num) + ". " + head, font=F["grid_h"], fill=INK)
        d.text((tx, y0 + 16), deck, font=F["grid_d"], fill=INK_SOFT)
        dw = d.textlength(data, font=F["grid_data"])
        d.text((tx, y0 + 30), data, font=F["grid_data"], fill=NAVY)
        tag_box(d, x0 + card_w - 64, y0 + 1, status)
        if row < 4:
            d.line([x0, y0 + 41, x0 + card_w, y0 + 41], fill=HAIR, width=1)

    # Map header + world map with numbered pins.
    d.text((16, 696), "WHERE IT HAPPENED \u2014 13 PLACES, NUMBERED",
           font=F["sec"], fill=INK)
    d.line([16, 714, W - 16, 714], fill=RULE, width=1)
    mx, my, mw, mh = 16, 720, W - 32, 88
    d.rectangle([mx, my, mx + mw, my + mh], fill=OCEAN, outline=INK, width=1)
    for poly in CONTINENTS:
        pts = [lonlat(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    for i, (lon, lat) in enumerate(PINS):
        px, py = lonlat(lon, lat, mx, my, mw, mh)
        if i == 12:
            px += 10
            py -= 7
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((px - 3, py - 6), str(i + 1), font=F["map_n"],
               fill=(255, 255, 255))

    # ALSO ON list, three columns.
    d.text((16, 814), "AND ALSO \u2014 STORIES 14\u201350",
           font=F["sec"], fill=INK)
    d.line([16, 832, W - 16, 832], fill=RULE, width=1)
    col_w = 320
    for ci in range(3):
        x0 = 16 + ci * (col_w + 16)
        chunk = ALSO[ci * 13:(ci + 1) * 13]
        yy = 838
        for num, head, src in chunk:
            line = str(num) + ". " + head + " \u2014 " + src
            while d.textlength(line, font=F["also"]) > col_w and len(line) > 12:
                line = line[:-2] + "\u2026"
                if line.endswith("..\u2026"):
                    line = line[:-3] + "\u2026"
            d.text((x0, yy), line, font=F["also"], fill=INK)
            yy += 11

    # Footer: DATE CHECK + sources + legend.
    d.line([16, 986, W - 16, 986], fill=RULE, width=1)
    d.text((16, 990), "DATE CHECK", font=F["foot_b"], fill=RED)
    foot1 = ("Every story above happened, or was first reported, on Thursday "
             "26 November 2026 (UTC).")
    d.text((96, 990), foot1, font=F["foot"], fill=INK)
    foot2 = ("Left out as earlier news: Hormuz tanker strikes (Wed 25) \u00b7 "
             "US tariff proposal (Wed 25) \u00b7 Huawei guilty verdict (Tue 24) "
             "\u00b7 Nvidia record surge (Mon 23).")
    d.text((16, 1002), foot2, font=F["foot"], fill=INK_SOFT)
    foot3 = ("Sources: KCNA \u00b7 Bank of Korea \u00b7 Reuters \u00b7 BBC \u00b7 AFP \u00b7 AP \u00b7 "
             "FIDE \u00b7 USTR \u00b7 ABS \u00b7 SAnews \u00b7 NDLEA \u00b7 MCMC  |  "
             "OFFICIAL = announced by the authority \u00b7 REPORTED = reported by "
             "two or more outlets \u00b7 CLAIM = one side\u2019s claim.")
    d.text((16, 1013), foot3, font=F["foot"], fill=INK_SOFT)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = build()
    img.save(out, format="PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
