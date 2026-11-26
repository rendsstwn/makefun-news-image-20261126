#!/usr/bin/python3
"""Render the Thursday 26 November 2026 front page as a PNG.

This script runs at build time only. It takes the fifty verified
stories for the day and paints them onto one 1024 by 1024 page in
the style of a printed newspaper: a navy nameplate, a strip of
headline figures, three big illustrated leads, a dozen short cards,
a dark figures strip, a small world map and a numbered list that
brings the count to fifty, then a footer that owns up to which
stories were first reported today and which were carried over.

Nothing here reads the network, the clock or a random source, so
running it again produces the same bytes. The entry program in
main.py is separate: it only ferries the finished picture into
/output. Pillow and the DejaVu faces installed on this machine do
all the drawing.

How the day is laid out
------------------------
The three leads are the stories that are genuinely new on the 26th
and big enough to carry the page: Kim Jong Un's nuclear order
(KCNA), the Bank of Korea's rate rise, and the storm that grounded
the Macy's parade. The tariff proposal from the 25th stays near
the top of the grid, labelled as carried, and the Hormuz tanker
fires stay a CLAIM because no independent confirmation exists.

Every story carries a status word. OFFICIAL means the figure or
the act comes from the authority itself; REPORTED means a press
outlet reported it; CLAIM means it is one side's account only.
The footer prints the split out loud: 17 stories first reported
on Thursday 26 November, 30 carried from Wednesday 25 November,
3 from Tuesday 24 November.

The story table below is one flat list in display order. Each row
holds the number, the slot it fills, its region and topic, its
status mark, the place line, the picture key, the shout line, the
headline, the deck, and the why-it-matters line. Leads use the
picture and the why line; grid cards use the picture and the shout
line; list items use the headline only. Rebuilding for a new day
means editing this table and nothing else."""

import collections
import hashlib
import pathlib

from PIL import Image, ImageDraw, ImageFont

SHEET_W, SHEET_H = 1024, 1024
PAGE_TINT = (248, 244, 233)
TEXT_INK = (18, 18, 18)
LINE_INK = (18, 18, 18)
CRIMSON = (139, 26, 26)
OCEAN = (26, 58, 92)
LEAF = (31, 92, 50)
MIDNIGHT = (16, 32, 56)
SLATE = (60, 60, 60)
HAIRLINE = (200, 194, 178)
BRASS = (232, 180, 28)

# Ten zones, in strip order. Each row: full name, short strip label,
# and the colour the strip cell and the map legend both use.
ZONES = [
    ("N. America", "N. AMERICA", (139, 26, 26)),
    ("Latin America", "LATIN AM.", (178, 110, 26)),
    ("Europe", "EUROPE", (26, 58, 92)),
    ("Middle East", "MID. EAST", (120, 60, 20)),
    ("N. Africa", "N. AFRICA", (168, 134, 20)),
    ("Sub-Saharan Africa", "SUB-SAHARA", (31, 92, 50)),
    ("South Asia", "SOUTH ASIA", (178, 70, 110)),
    ("East & SE Asia", "E. & SE ASIA", (18, 96, 96)),
    ("Oceania", "OCEANIA", (88, 44, 110)),
    ("Global", "GLOBAL", (70, 70, 70)),
]  # ten zones
ZONE_NAMES = [row[0] for row in ZONES]
ZONE_SHORT = {row[0]: row[1] for row in ZONES}
ZONE_TINT = {row[0]: row[2] for row in ZONES}

# One-letter status marks, each with its word and its tint.
MARKS = {
    "O": ("OFFICIAL", LEAF),
    "R": ("REPORTED", OCEAN),
    "C": ("CLAIM", CRIMSON),
}  # status marks

# The fifty stories, in display order. Row shape:
# (number, slot, zone, topic, mark, place, picture, shout,
#  headline, deck, why). Slot is "lead", "grid" or "also".
RAW_ITEMS = [
    (1, "lead", "East & SE Asia", "War", "O",
     "PYONGYANG · WAR", "nukes", "",
     "Kim orders wider tactical nuclear deployment",
     "KCNA: North Korea must expand its tactical arsenal; Kim inspected a nuclear-material site on Wednesday.",
     "Pyongyang's nuclear push is the day's sharpest escalation."),
    (2, "lead", "East & SE Asia", "Economy", "O",
     "SEOUL · ECONOMY", "rate", "",
     "Bank of Korea lifts base rate to 3.25%",
     "25bp hike, 5-2 vote; third rise since July; 2027 growth "
     "forecast lifted to 4.1%.",
     "Seoul tightens as growth runs hot and the won slides."),
    (3, "lead", "N. America", "Weather", "R",
     "NEW YORK · WEATHER", "storm", "",
     "Thanksgiving storm grounds Macy's 100th parade",
     "100th parade moved to Saturday, the call made Wednesday; "
     "gusts to 60 mph and coastal flooding hit the East Coast.",
     "The storm, not the parade, is the story — it hits the "
     "whole coast on Thanksgiving Day."),
    (4, "grid", "N. America", "Trade", "O",
     "WASHINGTON · TRADE", "containers", "35% TOP RATE",
     "US proposes tariffs of up to 35% on 14 economies",
     "USTR: China up to 20%, India 25%, EU 15%, Vietnam 35%.", ""),
    (5, "grid", "Europe", "War", "R",
     "RUSSIA · WAR", "jet", "5 JETS",
     "Ukraine strikes airbase, damages five Russian jets",
     "Savasleyka hit in overnight raid, Kyiv says.", ""),
    (6, "grid", "N. America", "War", "R",
     "WASHINGTON · WAR", "plane", "LEAVE NOW",
     "US tells citizens to leave Iran as war fears grow",
     "Warning as US forces mass in the region.", ""),
    (7, "grid", "Europe", "War", "R",
     "LONDON · WAR", "tally", "490,334",
     "BBC: at least 490,334 Russian soldiers have died",
     "Leaked data put the toll far above official figures.", ""),
    (8, "grid", "Middle East", "War", "R",
     "JEDDAH · WAR", "port", "3 TARGETS",
     "Houthis strike Saudi ports and a refinery",
     "Attacks hit Jeddah and Jazan; refinery burning.", ""),
    (9, "grid", "N. America", "Politics", "R",
     "FLORIDA · POLITICS", "podium", "FLORIDA",
     "Trump and Rutte: Russia must not widen the war",
     "After Florida talks, NATO chief backs US pressure.", ""),
    (10, "grid", "Latin America", "Security", "R",
     "PORT-AU-PRINCE · SECURITY", "shield", "34 KILLED",
     "Haiti police kill at least 34 gang members in raid",
     "Martissant operation is the deadliest of the year.", ""),
    (11, "grid", "East & SE Asia", "Disaster", "R",
     "BOGOR · DISASTER", "mine", "13 DEAD",
     "Indonesia mine toll rises to 13 dead, 13 missing",
     "Flooded gold pit; rescuers still digging.", ""),
    (12, "grid", "South Asia", "Security", "R",
     "MUMBAI · SECURITY", "candle", "18 YEARS",
     "Mumbai marks 18 years since the 26/11 attacks",
     "Tributes at the Gateway of India; 166 died in 2008.", ""),
    (13, "grid", "Middle East", "War", "C",
     "HORMUZ · WAR", "tanker", "2 TANKERS",
     "Iran says two tankers hit mines, caught fire",
     "IRGC: 'unauthorised route'; no confirmation.", ""),
    (14, "grid", "N. Africa", "Disaster", "R",
     "CAIRO · DISASTER", "flame", "31 DEAD",
     "Cairo tanker fire kills at least 31",
     "Fuel tanker explodes on the ring road; 21 hurt.", ""),
    (15, "grid", "Europe", "Energy", "O",
     "LONDON · ENERGY", "gauge", "+26%  £2,166",
     "UK energy price cap to rise 26% in January",
     "Ofgem: typical bill £1,723 to £2,166 a year from 1 Jan.", ""),
]  # leads and grid done

# The compact list, stories 16 to 50: one tight line each.
RAW_ITEMS += [
    (16, "also", "N. America", "Politics", "R", "", "", "",
     "9 more Russian and Ukrainian children reunited", "", ""),
    (17, "also", "Europe", "War", "R", "", "", "",
     "Germany plans first drone regiment", "", ""),
    (18, "also", "Middle East", "Politics", "R", "", "", "",
     "Iraq's top court backs Baghdad's Kurdistan expansion", "", ""),
    (19, "also", "Middle East", "Rights", "R", "", "", "",
     "Amnesty urges ICC probe over Gaza births", "", ""),
    (20, "also", "East & SE Asia", "Markets", "R", "", "", "",
     "Nikkei rebounds 1.3% after Wednesday's 3% slide", "", ""),
    (21, "also", "Middle East", "War", "R", "", "", "",
     "Israeli strike kills three in a Gaza food vehicle", "", ""),
    (22, "also", "N. America", "Markets", "R", "", "", "",
     "Dow closes above 50,000 for the first time", "", ""),
    (23, "also", "Europe", "War", "R", "", "", "",
     "Ukraine drones set two Rosneft refineries ablaze", "", ""),
    (24, "also", "Europe", "Diplomacy", "R", "", "", "",
     "Kyiv seeks €115bn in foreign aid for 2027", "", ""),
    (25, "also", "Latin America", "Culture", "R", "", "", "",
     "Puerto Rico's Barreto crowned Miss Universe 2026", "", ""),
    (26, "also", "Middle East", "War", "R", "", "", "",
     "Israeli strike kills Hamas security chief in Gaza", "", ""),
    (27, "also", "N. America", "Tech", "R", "", "", "",
     "Huawei found guilty by a US jury", "", ""),
    (28, "also", "Oceania", "Diplomacy", "O", "", "", "",
     "Solomon Islands signs security pact with Australia", "", ""),
    (29, "also", "Latin America", "Security", "R", "", "", "",
     "Colombia frees all Cartagena supermarket hostages", "", ""),
    (30, "also", "Sub-Saharan Africa", "Justice", "R", "", "", "",
     "Zimbabwe issues arrest warrant for Mugabe's son", "", ""),
    (31, "also", "South Asia", "Labour", "R", "", "", "",
     "Bangladesh garment workers win a 36% pay rise", "", ""),
    (32, "also", "N. America", "Justice", "R", "", "", "",
     "Abrego Garcia leaves the US for Spain voluntarily", "", ""),
    (33, "also", "Global", "Climate", "R", "", "", "",
     "COP31 climate talks end with no agreement", "", ""),
    (34, "also", "East & SE Asia", "Markets", "R", "", "", "",
     "Kospi fell 6.2% Wed, rebounded 0.3% Thu", "", ""),
    (35, "also", "N. America", "Markets", "R", "", "", "",
     "Nvidia falls 5.9% a day after its record surge", "", ""),
]  # stories 16 to 35

RAW_ITEMS += [
    (36, "also", "N. America", "Business", "O", "", "", "",
     "Dell posts a record $54.9bn quarter on AI servers", "", ""),
    (37, "also", "Europe", "Economy", "O", "", "", "",
     "Eurozone inflation rises to 4.0%", "", ""),
    (38, "also", "Oceania", "Economy", "O", "", "", "",
     "Australian inflation rises to 4.9%", "", ""),
    (39, "also", "Europe", "Business", "R", "", "", "",
     "EasyJet profit falls 89% as fuel costs soar", "", ""),
    (40, "also", "East & SE Asia", "Space", "O", "", "", "",
     "Shenzhou-24 docks at Tiangong, first Pakistani aboard", "", ""),
    (41, "also", "N. America", "Tech", "R", "", "", "",
     "Amazon buys chip rival Decart", "", ""),
    (42, "also", "N. America", "Tech", "R", "", "", "",
     "Hackers' AI agents breach a university server", "", ""),
    (43, "also", "N. America", "Markets", "R", "", "", "",
     "Nvidia fell 5.2% on Tuesday", "", ""),
    (44, "also", "N. America", "Security", "C", "", "", "",
     "Hackers reportedly breach a CIA analysis system", "", ""),
    (45, "also", "Europe", "Science", "O", "", "", "",
     "Roche breast cancer pill wins second FDA approval", "", ""),
    (46, "also", "Sub-Saharan Africa", "Sport", "R", "", "", "",
     "Senegal regain Africa Cup of Nations title in court", "", ""),
    (47, "also", "N. America", "Culture", "R", "", "", "",
     "GTA VI debuts at $3.79bn, an entertainment record", "", ""),
    (48, "also", "Middle East", "Diplomacy", "R", "", "", "",
     "Haftar meets Erdogan in Ankara on first official visit", "", ""),
    (49, "also", "Middle East", "Security", "R", "", "", "",
     "CENTCOM praises Syria over drug and arms seizures", "", ""),
    (50, "also", "Europe", "War", "R", "", "", "",
     "Russia's 112-drone attack cuts power in five regions", "", ""),
]  # stories 36 to 50


def _to_record(row):
    """Turn one story row into a named record the painters use."""
    (no, form, zone, topic, mark, place, picture, shout,
     title, body, point) = row
    return {"no": no, "form": form, "zone": zone, "topic": topic,
            "mark": mark, "place": place, "picture": picture,
            "shout": shout, "title": title, "body": body,
            "point": point}


ITEMS = [_to_record(row) for row in RAW_ITEMS]
TOP_ITEMS = [it for it in ITEMS if it["form"] == "lead"]
CARD_ITEMS = [it for it in ITEMS if it["form"] == "grid"]
LIST_ITEMS = [it for it in ITEMS if it["form"] == "also"]
assert len(ITEMS) == 50, len(ITEMS)
assert [it["no"] for it in ITEMS] == list(range(1, 51))
assert len(TOP_ITEMS) == 3 and len(CARD_ITEMS) == 12
assert len(LIST_ITEMS) == 35
ZONE_TALLY = collections.Counter(it["zone"] for it in ITEMS)
TOPIC_TALLY = collections.Counter(it["topic"] for it in ITEMS)
assert sum(ZONE_TALLY.values()) == 50
assert sum(TOPIC_TALLY.values()) == 50
assert len(ZONE_TALLY) == 10 and len(TOPIC_TALLY) == 20

# The five headline figures under the nameplate.
HEADLINE_NUMBERS = [
    ("490,334", "Russian soldiers dead, BBC analysis", CRIMSON),
    ("3.25%", "Bank of Korea base rate after hike", TEXT_INK),
    ("35%", "top proposed US tariff, on China", TEXT_INK),
    ("50,000", "Dow closes above it, first time", TEXT_INK),
    ("13", "dead in Indonesia mine flood", TEXT_INK),
]  # five figures

# The dark figures strip near the foot of the page.
DAY_NUMBERS = [
    ("5", "jets hit at Savasleyka"),  # overnight raid on the airbase
    ("+26%", "UK energy cap"),  # Ofgem's January cap rise
    ("34", "Haiti gang dead"),  # the Martissant raid
    ("18", "years since 26/11"),  # the Mumbai anniversary
    ("60 mph", "storm gusts"),  # the nor'easter's gusts
]  # five more figures

TOP_CREDIT = {1: "KCNA", 2: "Bank of Korea", 3: "NWS"}
CARD_CREDIT = {
    4: "USTR", 5: "Reuters", 6: "AP", 7: "BBC", 8: "Reuters",
    9: "AP", 10: "AP", 11: "AP", 12: "AP", 13: "Reuters",
    14: "AP", 15: "Ofgem",
}  # grid credits

# Rough continent outlines as (lon, lat) pairs, good enough at
# 272 pixels wide. Six shapes, in the same order the map draws them.
LAND_SHAPES = [
    [(-168, 66), (-140, 70), (-125, 72),
     (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 52),
     (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 21),
     (-97, 16), (-105, 20), (-110, 23),
     (-120, 34), (-125, 40), (-125, 49),
     (-135, 58), (-155, 58), (-165, 60)],
    [(-80, 9), (-75, 11), (-65, 10),
     (-55, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28),
     (-58, -38), (-65, -45), (-70, -54),
     (-73, -50), (-73, -40),
     (-72, -20), (-77, -12), (-80, -3)],
    [(-10, 36), (-9, 43), (-2, 48),
     (-4, 50), (0, 51), (3, 53),
     (8, 57), (10, 59), (18, 56),
     (21, 55), (28, 59), (30, 60),
     (24, 65), (18, 69), (12, 70),
     (5, 60), (-5, 58), (-10, 54),
     (-10, 43), (-6, 36)],
    [(-18, 35), (-10, 31), (-5, 35),
     (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11),
     (48, 0), (40, -10), (35, -18),
     (32, -28), (26, -34), (19, -35),
     (15, -27), (12, -18), (9, -1),
     (9, 4), (-8, 4), (-13, 8),
     (-17, 15), (-17, 25)],
    [(40, 70), (50, 70), (60, 69),
     (70, 72), (80, 73), (100, 77),
     (120, 73), (140, 72), (160, 69),
     (178, 66), (178, 62), (162, 60),
     (158, 52), (142, 50), (140, 40),
     (130, 33), (127, 35), (122, 30),
     (120, 22), (110, 20), (105, 10),
     (100, 8), (98, 16), (95, 16),
     (90, 22), (85, 20), (80, 15),
     (76, 8), (72, 20), (66, 25),
     (60, 25), (55, 26), (50, 29),
     (48, 30), (44, 29), (40, 36),
     (36, 36), (40, 42), (40, 50),
     (45, 55), (50, 60)],
    [(113, -22), (114, -30), (115, -35),
     (124, -33), (129, -32), (132, -32),
     (137, -35), (140, -38), (146, -39),
     (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
]  # six shapes

# Featured-story map spots: (story, lon, lat, nudge x, nudge y).
# The nudge moves dots that would land on each other apart, with a
# leader line back to the true spot: Pyongyang/Seoul, New
# York/Washington/Florida/Port-au-Prince, the two Londons,
# Tehran/Hormuz, Jeddah/Cairo.
PIN_SPOTS = [
    (1, 127, 39.5, -8, -6),
    (2, 127, 37.5, 8, 6),
    (3, -74, 40.7, -8, -6),
    (4, -77, 38.9, 8, 4),
    (5, 43.5, 55.5, 0, 0),
    (6, 51.4, 35.7, 0, 0),
    (7, 0, 51.5, -7, -5),
    (8, 39.2, 21.5, 0, 0),
    (9, -80.5, 26.8, -8, 4),
    (10, -72.3, 18.5, 8, -2),
    (11, 106.8, -6.6, 0, 0),
    (12, 72.9, 19.1, 0, 0),
    (13, 56.5, 26.5, 10, 6),
    (14, 31.2, 30.0, -9, -4),
    (15, 0, 51.5, 7, 5),
]  # fifteen pins

def fetch_typefaces():
    """Load the DejaVu faces this machine ships, at the sizes used."""
    folder = "/usr/share/fonts/truetype/dejavu/"
    serif_heavy = folder + "DejaVuSerif-Bold.ttf"
    serif_plain = folder + "DejaVuSerif.ttf"
    sans_plain = folder + "DejaVuSans.ttf"
    sans_heavy = folder + "DejaVuSans-Bold.ttf"
    faces = {
        "title": ImageFont.truetype(serif_heavy, 46),
        "dateline": ImageFont.truetype(serif_heavy, 34),
        "ribbon": ImageFont.truetype(sans_heavy, 11),
        "tagline": ImageFont.truetype(serif_plain, 15),
        "zonelabel": ImageFont.truetype(sans_heavy, 10),
        "fieldlabel": ImageFont.truetype(sans_plain, 9),
        "bignum": ImageFont.truetype(serif_heavy, 24),
        "biglab": ImageFont.truetype(sans_plain, 9),
        "leadplace": ImageFont.truetype(sans_heavy, 10),
        "leadtitle": ImageFont.truetype(serif_heavy, 16),
        "leadbody": ImageFont.truetype(sans_plain, 11),
        "whybody": ImageFont.truetype(sans_plain, 10),
        "whylabel": ImageFont.truetype(sans_heavy, 9),
        "cardplace": ImageFont.truetype(sans_heavy, 9),
        "cardtitle": ImageFont.truetype(serif_heavy, 12),
        "cardbody": ImageFont.truetype(sans_plain, 9),
        "badge": ImageFont.truetype(sans_heavy, 11),
        "listitem": ImageFont.truetype(sans_plain, 10),
        "listnum": ImageFont.truetype(sans_heavy, 10),
        "foottext": ImageFont.truetype(sans_plain, 9),
        "footbold": ImageFont.truetype(sans_heavy, 9),
        "maphead": ImageFont.truetype(sans_heavy, 9),
        "status": ImageFont.truetype(sans_heavy, 8),
        "shout": ImageFont.truetype(sans_heavy, 12),
        "bynumber": ImageFont.truetype(serif_heavy, 16),
    }  # faces ready
    return faces


def heavy(size):
    """Bold DejaVu Sans, sized on demand."""
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(path, size)


def fold_text(draw, text, font, width):
    """Split text into lines no wider than the given pixel width."""
    pieces = text.split()
    out, current = [], ""
    for piece in pieces:
        attempt = piece if not current else current + " " + piece
        if draw.textlength(attempt, font=font) <= width:
            current = attempt
            continue
        if current:
            out.append(current)
        current = piece
    if current:
        out.append(current)
    return out


def paint_status(draw, x, y, mark, faces):
    """Draw the status word in a thin coloured frame."""
    word, tint = MARKS[mark]
    face = faces["status"]
    wide = draw.textlength(word, font=face)
    draw.rectangle([x, y, x + wide + 8, y + 11], outline=tint, width=1)
    draw.text((x + 4, y + 1), word, font=face, fill=tint)
    return wide + 8


def paint_badge(draw, x, y, number, faces, fill=CRIMSON):
    """A filled disc with the story number in white."""
    span = 17
    draw.ellipse([x, y, x + span, y + span], fill=fill)
    label = str(number)
    wide = draw.textlength(label, font=faces["badge"])
    draw.text((x + (span - wide) / 2, y + 2), label, font=faces["badge"], fill=(255, 255, 255))
    return span

def scene_missiles(page, box):
    """Lead 1: a missile above centrifuges, for Kim's nuclear order.

    The panel stays dark; the missile wears the Hwasan-31 label,
    the centrifuge row below it stands for the material programme,
    and the KCNA wording is spelled out, never hinted at."""
    (x0, y0, x1, y1) = box
    wide, tall = x1 - x0, y1 - y0
    slab = Image.new("RGB", (wide, tall), (12, 24, 46))
    pen = ImageDraw.Draw(slab)
    for yy in range(tall):
        frac = yy / max(tall - 1, 1)
        pen.line([(0, yy), (wide, yy)], fill=(
            int(12 + 10 * frac), int(24 + 14 * frac),
            int(46 + 22 * frac)))
    for sx, sy in [(18, 10), (52, 6), (96, 12), (150, 8),
                   (210, 10), (262, 7), (300, 14), (38, 20), (286, 22)]:
        pen.ellipse([sx, sy, sx + 2, sy + 2], fill=(200, 210, 230))
    # the missile: grey body, red nose, tail fins
    pen.rectangle([58, 26, 248, 40], fill=(216, 216, 210))
    pen.polygon([(248, 26), (276, 33), (248, 40)], fill=(196, 40, 30))
    pen.polygon([(58, 26), (38, 18), (58, 32)], fill=(160, 160, 152))
    pen.polygon([(58, 40), (38, 48), (58, 34)], fill=(160, 160, 152))
    pen.rectangle([120, 26, 128, 40], fill=(120, 120, 114))
    pen.rectangle([180, 26, 188, 40], fill=(120, 120, 114))
    pen.text((96, 12), "HWASAN-31", font=heavy(9), fill=(255, 255, 255))
    pen.text((196, 12), "TACTICAL NUKES", font=heavy(11), fill=(232, 180, 28))
    # a row of centrifuges along the bottom
    pen.line([(14, 54), (wide - 14, 54)], fill=(90, 120, 160), width=2)
    for slot in range(5):
        cx = 22 + slot * 26
        pen.rectangle([cx, 44, cx + 14, 62], fill=(70, 100, 140))
        pen.rectangle([cx, 44, cx + 14, 48], fill=(200, 210, 230))
    pen.text((14, 65), "CENTRIFUGES", font=heavy(8), fill=(160, 180, 205))
    pen.text((168, 65), "KCNA: WIDER DEPLOYMENT", font=heavy(8), fill=(220, 225, 240))
    page.paste(slab, (x0, y0))


def scene_rates(page, box):
    """Lead 2: the Bank of Korea rise drawn as a step chart.

    The step itself, 3.00% to 3.25%, is the news; the labels add
    the vote split, how many hikes since July, the 2027 growth
    outlook, and the Kospi's Thursday close for context."""
    (x0, y0, x1, y1) = box
    wide, tall = x1 - x0, y1 - y0
    slab = Image.new("RGB", (wide, tall), (14, 26, 40))
    pen = ImageDraw.Draw(slab)
    for gy in range(12, tall - 6, 16):
        pen.line([(8, gy), (wide - 8, gy)], fill=(38, 54, 76), width=1)
    # the step itself: flat at 3.00%, up 25bp, flat at 3.25%
    pen.line([(16, 46), (150, 46)], fill=(232, 180, 28), width=3)
    pen.line([(150, 46), (150, 24)], fill=(232, 180, 28), width=3)
    pen.line([(150, 24), (wide - 16, 24)], fill=(232, 180, 28), width=3)
    for px, py in [(16, 46), (150, 46), (150, 24), (wide - 16, 24)]:
        pen.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(232, 180, 28))
    pen.text((16, 52), "3.00%", font=heavy(11), fill=(200, 210, 220))
    pen.text((wide - 66, 30), "3.25%", font=heavy(13), fill=(255, 255, 255))
    pen.text((156, 34), "+25 BP", font=heavy(11), fill=(232, 72, 56))
    pen.text((16, 8), "3RD HIKE SINCE JULY", font=heavy(9), fill=(160, 190, 220))
    pen.text((wide - 148, 52), "2027 GROWTH 4.1%", font=heavy(9), fill=(160, 190, 220))
    pen.text((wide - 148, 64), "KOSPI 4,711  +0.29%", font=heavy(9), fill=(120, 200, 140))
    page.paste(slab, (x0, y0))


def scene_storm(page, box):
    """Lead 3: the Thanksgiving nor'easter above the East Coast.

    A dusk sky holds the storm's spiral off the shore, rain
    streaks and wind arrows, plus the figures that count: gusts
    of 60 mph, the parade shifted to Saturday, the first such
    weather delay in a hundred years."""
    (x0, y0, x1, y1) = box
    wide, tall = x1 - x0, y1 - y0
    sky = Image.new("RGB", (wide, tall), (30, 44, 66))
    pen = ImageDraw.Draw(sky)
    for yy in range(tall):
        frac = yy / max(tall - 1, 1)
        pen.line([(0, yy), (wide, yy)], fill=(
            int(30 + 26 * frac), int(44 + 30 * frac),
            int(66 + 34 * frac)))
    # the coastline runs along the bottom
    pen.polygon([(0, tall), (0, tall - 14), (60, tall - 20),
                 (130, tall - 12), (200, tall - 18), (260, tall - 10),
                 (wide, tall - 14), (wide, tall)], fill=(24, 34, 52))
    # the spiral: rings off the coast
    cx, cy = wide - 78, 34
    for ring in (10, 18, 26):
        pen.arc([cx - ring, cy - ring, cx + ring, cy + ring],
                20, 300, fill=(180, 200, 225), width=2)
    pen.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(232, 180, 28))
    # rain streaks down the left side
    for rx, ry in [(22, 14), (44, 22), (30, 34), (58, 40),
                   (76, 18), (96, 30), (16, 48), (110, 44)]:
        pen.line([(rx, ry), (rx - 4, ry + 10)], fill=(150, 170, 200), width=1)
    # wind arrows blowing inland
    for wx, wy in [(140, 18), (170, 52), (210, 58)]:
        pen.line([(wx, wy), (wx + 18, wy)], fill=(220, 225, 240),
                 width=2)
        pen.polygon([(wx + 18, wy), (wx + 12, wy - 3), (wx + 12, wy + 3)], fill=(220, 225, 240))
    pen.text((12, 8), "60 MPH GUSTS", font=heavy(11), fill=(255, 255, 255))
    pen.text((12, 56), "PARADE → SAT 28 NOV", font=heavy(10), fill=(232, 180, 28))
    pen.text((wide - 178, 8), "NOR'EASTER", font=heavy(9), fill=(180, 200, 225))
    pen.text((wide - 150, 62), "1ST DELAY IN 100 YRS",
             font=heavy(8), fill=(200, 210, 230))
    page.paste(sky, (x0, y0))  # storm panel placed

def scene_card(page, box, motif, shout, faces):
    """A grid cell's picture band: a small data-carrying scene on
    the left, the shout line in bold on the right. The band is
    only 28 pixels tall, so each scene is a few flat shapes and
    the one number that matters — never a picture that asks to
    be studied."""
    (x0, y0, x1, y1) = box
    wide, tall = x1 - x0, y1 - y0
    strip = Image.new("RGB", (wide, tall), (238, 234, 220))
    pen = ImageDraw.Draw(strip)
    mid = tall // 2
    if motif == "containers":
        # piled shipping containers, each stamped with a rate
        box_cols = [(150, 60, 44), (196, 110, 26), (26, 58, 92)]
        for row, tint in enumerate(box_cols):
            yy = 2 + row * 8
            pen.rectangle([10, yy, 46, yy + 7], fill=tint)
            pen.text((48, yy - 1), "%", font=heavy(8), fill=tint)
    elif motif == "jet":
        # a fighter jet in profile, flame from its tail
        pen.polygon([(12, 14), (34, 10), (52, 13), (34, 17)], fill=(70, 70, 74))
        pen.polygon([(24, 10), (30, 4), (32, 10)], fill=(70, 70, 74))
        pen.polygon([(12, 14), (6, 11), (6, 17)], fill=(232, 120, 28))
        pen.polygon([(52, 13), (58, 12), (58, 14)], fill=(196, 40, 30))
    elif motif == "plane":
        # an airliner climbing away, arrow pointing out
        pen.polygon([(10, 18), (30, 8), (48, 10), (30, 20)], fill=(26, 58, 92))
        pen.polygon([(26, 8), (32, 2), (34, 8)], fill=(26, 58, 92))
        pen.line([(52, 6), (62, 2)], fill=(196, 40, 30), width=2)
        pen.polygon([(62, 2), (56, 2), (62, 6)], fill=(196, 40, 30))
    elif motif == "tally":
        # tally marks grouped in fives, the count made visible
        for group in range(3):
            gx = 10 + group * 16
            for mark in range(4):
                pen.line([(gx + mark * 3, 6), (gx + mark * 3, 22)], fill=(60, 60, 60), width=1)
            pen.line([(gx - 1, 22), (gx + 11, 6)], fill=(60, 60, 60), width=1)
    elif motif == "port":
        # a harbour crane above a moored ship
        pen.line([(14, 4), (14, 26)], fill=(60, 60, 60), width=2)
        pen.line([(14, 6), (40, 6)], fill=(60, 60, 60), width=2)
        pen.line([(40, 6), (40, 14)], fill=(60, 60, 60), width=1)
        pen.rectangle([34, 14, 46, 18], fill=(150, 60, 44))
        pen.rectangle([10, 20, 54, 26], fill=(32, 32, 34))
        pen.rectangle([16, 16, 24, 20], fill=(178, 74, 52))
    elif motif == "podium":
        # two flags behind a podium: US stripes, NATO star
        pen.line([(12, 4), (12, 26)], fill=(60, 60, 60), width=2)
        pen.rectangle([12, 4, 28, 12], fill=(196, 40, 30))
        pen.rectangle([12, 4, 18, 8], fill=(26, 58, 120))
        pen.line([(36, 4), (36, 26)], fill=(60, 60, 60), width=2)
        pen.rectangle([36, 4, 52, 12], fill=(26, 58, 120))
        pen.ellipse([42, 6, 46, 10], fill=(255, 255, 255))
        pen.rectangle([20, 18, 44, 26], fill=(90, 90, 90))
    elif motif == "shield":
        # a police shield carrying a star
        pen.polygon([(32, 4), (46, 8), (46, 16), (32, 26), (18, 16), (18, 8)], fill=(26, 58, 92))
        pen.ellipse([28, 10, 36, 18], fill=(232, 180, 28))
    elif motif == "mine":
        # a mine shaft: brown earth, black hole, helmet lamp
        pen.rectangle([8, 0, 52, 26], fill=(120, 88, 52))
        pen.rectangle([22, 0, 34, 26], fill=(18, 18, 18))
        pen.line([(22, 8), (34, 8)], fill=(232, 180, 28), width=2)
        pen.ellipse([26, 12, 30, 16], fill=(232, 180, 28))
    elif motif == "candle":
        # a memorial candle, flame lit, on a dark base
        pen.rectangle([26, 10, 38, 26], fill=(214, 196, 158), outline=(140, 120, 90))
        pen.polygon([(32, 2), (28, 10), (36, 10)], fill=(232, 180, 28))
        pen.rectangle([14, 26, 50, 28], fill=(60, 60, 60))
        pen.ellipse([22, 12, 26, 16], fill=(232, 120, 28))
        pen.ellipse([38, 12, 42, 16], fill=(232, 120, 28))
    elif motif == "tanker":
        # a small tanker and a mine in the water
        pen.rectangle([8, 14, 46, 22], fill=(32, 32, 34))
        pen.rectangle([14, 8, 24, 14], fill=(150, 60, 44))
        pen.rectangle([28, 8, 38, 14], fill=(178, 74, 52))
        pen.ellipse([48, 16, 54, 22], fill=(20, 20, 20))
        pen.line([(46, 24), (56, 24)], fill=(120, 160, 190), width=1)
    elif motif == "flame":
        # a tanker truck with flame bursting above it
        pen.rectangle([10, 16, 40, 24], fill=(178, 74, 52))
        pen.rectangle([40, 18, 50, 24], fill=(32, 32, 34))
        pen.ellipse([16, 24, 22, 28], fill=(18, 18, 18))
        pen.ellipse([42, 24, 48, 28], fill=(18, 18, 18))
        pen.polygon([(22, 14), (26, 2), (30, 10), (34, 4), (36, 14)], fill=(232, 120, 28))
    elif motif == "gauge":
        # an energy-bill gauge: arc, needle high, red zone
        pen.arc([6, 2, 62, 58], 180, 360, fill=(120, 120, 120), width=3)
        pen.arc([40, 2, 62, 58], 270, 360, fill=(196, 40, 30), width=3)
        pen.line([(34, 30), (50, 12)], fill=(139, 26, 26), width=2)
        pen.ellipse([30, 26, 38, 34], fill=(18, 18, 18))
    # shout line on the right, bold and dark
    face = faces["shout"]
    shout_w = pen.textlength(shout, font=face)
    pen.text((wide - shout_w - 6, mid - 8), shout, font=face,
             fill=(18, 18, 18))
    page.paste(strip, (x0, y0))

def scene_map(page, draw, faces, box):
    """WHERE IT HAPPENED: a rough world map with the fifteen
    featured stories as numbered dots, and the region legend
    underneath. Nudged dots get a thin leader line back to their
    true spot."""
    (x0, y0, x1, y1) = box
    mwide, mtall = x1 - x0, y1 - y0
    ocean = Image.new("RGB", (mwide, mtall), (226, 232, 238))
    pen = ImageDraw.Draw(ocean)
    for shape in LAND_SHAPES:
        pts = [((lon + 180) / 360 * mwide,
                (90 - lat) / 180 * mtall) for lon, lat in shape]
        pen.polygon(pts, fill=(208, 198, 168), outline=(170, 158, 128))
    tiny = heavy(8)
    for number, lon, lat, dx, dy in PIN_SPOTS:
        tx = (lon + 180) / 360 * mwide
        ty = (90 - lat) / 180 * mtall
        cx, cy = tx + dx, ty + dy  # nudged dot
        if (dx, dy) != (0, 0):
            pen.line([(tx, ty), (cx, cy)], fill=(120, 120, 120), width=1)
            pen.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(120, 120, 120))
        pen.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=CRIMSON, outline=(255, 255, 255), width=1)
        label = str(number)
        wide = pen.textlength(label, font=tiny)
        pen.text((cx - wide / 2, cy - 5), label, font=tiny, fill=(255, 255, 255))
    page.paste(ocean, (x0, y0))
    # the legend: region colours in two columns
    top_y = y1 + 6
    half = (x1 - x0) // 2
    for pos, zone in enumerate(ZONE_NAMES):
        lx = x0 + (pos % 2) * half
        ly = top_y + (pos // 2) * 10
        draw.ellipse([lx, ly, lx + 7, ly + 7], fill=ZONE_TINT[zone])
        draw.text((lx + 10, ly - 1), zone, font=faces["foottext"],
                  fill=TEXT_INK)

def scene_masthead(draw, faces):
    """Navy nameplate band with the paper's name in gold and the
    date in big white serif, then the red sub-headline, the region
    and field strips, and the big-number stat strip. Returns the y
    where the leads begin."""
    draw.rectangle([8, 8, SHEET_W - 8, 66], fill=MIDNIGHT)
    draw.text((16, 12), "THE WORLD IN ONE DAY", font=faces["ribbon"],
              fill=BRASS)
    draw.text((28, 28), "Thursday 26 November 2026", font=faces["dateline"], fill=(255, 255, 255))
    right = "50 STORIES · 10 REGIONS · 20 FIELDS"
    tw = draw.textlength(right, font=faces["ribbon"])
    draw.text((SHEET_W - 16 - tw, 12), right, font=faces["ribbon"], fill=(255, 255, 255))
    right2 = "ONE DAY · ONE PAGE · THE WORLD'S NEWS"
    tw2 = draw.textlength(right2, font=faces["foottext"])
    draw.text((SHEET_W - 16 - tw2, 34), right2, font=faces["foottext"], fill=(200, 210, 220))
    # a red sub-headline: the three leads in one line
    sub = ("Kim vows wider nuclear deployment · Bank of Korea lifts "
           "rate to 3.25% · Thanksgiving storm grounds Macy's parade")
    draw.text((28, 72), sub, font=faces["tagline"], fill=CRIMSON)
    draw.line([28, 90, SHEET_W - 28, 90], fill=LINE_INK, width=2)
    # the region strip: ten coloured cells with counts
    band_y = 94
    cell_gap = 2
    cell = (SHEET_W - 56 - (len(ZONE_NAMES) - 1) * cell_gap)
    cell = cell // len(ZONE_NAMES)
    for pos, zone in enumerate(ZONE_NAMES):
        cx = 28 + pos * (cell + cell_gap)
        draw.rectangle([cx, band_y, cx + cell, band_y + 16],
                       fill=ZONE_TINT[zone])
        tag = "%s %d" % (ZONE_SHORT[zone], ZONE_TALLY[zone])
        lw = draw.textlength(tag, font=faces["zonelabel"])
        draw.text((cx + (cell - lw) / 2, band_y + 3), tag,
                  font=faces["zonelabel"], fill=(255, 255, 255))
    # the fields strip, on two lines so every field stays legible
    ranked = sorted(TOPIC_TALLY.items(), key=lambda kv: (-kv[1], kv[0]))
    draw.text((28, 114), "20 FIELDS", font=faces["footbold"],
              fill=CRIMSON)
    top_row = "  ·  ".join("%s %d" % (k, v) for k, v in ranked[:10])
    draw.text((96, 114), top_row, font=faces["fieldlabel"], fill=TEXT_INK)
    bot_row = "  ·  ".join("%s %d" % (k, v) for k, v in ranked[10:])
    draw.text((96, 124), bot_row, font=faces["fieldlabel"], fill=TEXT_INK)
    draw.line([28, 138, SHEET_W - 28, 138], fill=LINE_INK, width=1)
    # the stat strip: five big numbers with one-line labels
    stat_y = 144
    span = (SHEET_W - 56) // 5
    for pos, (num, lab, tint) in enumerate(HEADLINE_NUMBERS):
        cx = 28 + pos * span
        draw.text((cx, stat_y), num, font=faces["bignum"], fill=tint)
        draw.text((cx, stat_y + 27), lab, font=faces["biglab"],
                  fill=SLATE)
        if pos < 4:
            draw.line([cx + span - 6, stat_y + 2, cx + span - 6,
                       stat_y + 38], fill=HAIRLINE, width=1)
    draw.line([28, 182, SHEET_W - 28, 182], fill=LINE_INK, width=2)
    return 188  # leads start here


def scene_leads(page, draw, faces, top):
    """Three large leads: data-rich picture, number badge, place
    line, status tag, headline, deck, why-it-matters."""
    width, gap = 314, 13
    scenes = {"nukes": scene_missiles, "rate": scene_rates,
              "storm": scene_storm}
    for pos, lead in enumerate(TOP_ITEMS):
        x = 28 + pos * (width + gap)
        scenes[lead["picture"]](page, (x, top, x + width, top + 74))
        cursor = top + 80
        paint_badge(draw, x, cursor, lead["no"], faces)
        draw.text((x + 22, cursor + 2), lead["place"],
                  font=faces["leadplace"], fill=CRIMSON)
        word, tint = MARKS[lead["mark"]]
        wide = draw.textlength(word, font=faces["status"]) + 8
        draw.rectangle([x + width - wide, cursor + 2, x + width,
                        cursor + 13], outline=tint, width=1)
        draw.text((x + width - wide + 4, cursor + 3), word,
                  font=faces["status"], fill=tint)
        cursor += 22
        for line in fold_text(draw, lead["title"], faces["leadtitle"],
                              width)[:2]:
            draw.text((x, cursor), line, font=faces["leadtitle"],
                      fill=TEXT_INK)
            cursor += 19
        for line in fold_text(draw, lead["body"], faces["leadbody"],
                              width)[:3]:
            draw.text((x, cursor), line, font=faces["leadbody"],
                      fill=TEXT_INK)
            cursor += 13
        cursor += 2
        head = "WHY IT MATTERS  "
        pw = draw.textlength(head, font=faces["whylabel"])
        body = lead["point"] + " (" + TOP_CREDIT[lead["no"]] + ")"
        why_lines = fold_text(draw, body, faces["whybody"],
                              width - pw)[:2]
        for k, line in enumerate(why_lines):
            if k == 0:
                draw.text((x, cursor), head, font=faces["whylabel"],
                          fill=CRIMSON)
            draw.text((x + pw, cursor), line, font=faces["whybody"],
                      fill=TEXT_INK)
            cursor += 12
        if pos < 2:
            draw.line([x + width + gap // 2, top,
                       x + width + gap // 2, top + 194],
                      fill=HAIRLINE, width=1)
    return top + 206  # grid starts below


def scene_grid(page, draw, faces, top):
    """Twelve grid cards: picture band with a data shout, capital
    place-topic label, two-line headline, two-line deck, and a
    source plus status line. No two bands share a picture."""
    cols = 4
    gap = 14
    row_h = 104
    width = (SHEET_W - 56 - (cols - 1) * gap) // cols
    for idx, story in enumerate(CARD_ITEMS):
        row, col = divmod(idx, cols)
        x = 28 + col * (width + gap)
        y = top + row * row_h
        scene_card(page, (x, y, x + width, y + 24),
                   story["picture"], story["shout"], faces)
        kick_y = y + 28
        paint_badge(draw, x, kick_y, story["no"], faces)
        draw.text((x + 20, kick_y + 2), story["place"],
                  font=faces["cardplace"],
                  fill=ZONE_TINT[story["zone"]])
        head_y = kick_y + 15
        for line in fold_text(draw, story["title"], faces["cardtitle"],
                              width)[:2]:
            draw.text((x, head_y), line, font=faces["cardtitle"],
                      fill=TEXT_INK)
            head_y += 14
        for line in fold_text(draw, story["body"], faces["cardbody"],
                              width)[:2]:
            draw.text((x, head_y), line, font=faces["cardbody"], fill=(60, 60, 60))
            head_y += 10
        src = "(%s) · %s" % (CARD_CREDIT[story["no"]],
                             MARKS[story["mark"]][0])
        draw.text((x, y + row_h - 11), src, font=faces["cardbody"],
                  fill=MARKS[story["mark"]][1])
        if col < cols - 1:
            draw.line([x + width + gap // 2, y + 2,
                       x + width + gap // 2, y + row_h - 6],
                      fill=HAIRLINE, width=1)
    draw.line([28, top + 3 * row_h + 2, SHEET_W - 28,
               top + 3 * row_h + 2], fill=LINE_INK, width=2)
    return top + 3 * row_h + 8  # figures strip follows

def scene_numbers(draw, faces, y):
    """The dark BY THE NUMBERS strip: five figures that sum up
    the day, big white numerals with small grey labels."""
    tall = 32
    draw.rectangle([8, y, SHEET_W - 8, y + tall], fill=MIDNIGHT)
    draw.text((16, y + 9), "BY THE NUMBERS", font=faces["ribbon"],
              fill=BRASS)
    x = 170  # after the label
    step = (SHEET_W - 16 - 170) // 5
    for num, lab in DAY_NUMBERS:
        draw.text((x, y + 5), num, font=faces["bynumber"], fill=(255, 255, 255))
        nw = draw.textlength(num, font=faces["bynumber"])
        draw.text((x + nw + 6, y + 11), lab, font=faces["biglab"], fill=(200, 210, 220))
        x += step
    return y + tall + 6


def scene_bottom(page, draw, faces, top):
    """Map on the left, ALSO ON list on the right: thirty-five
    more stories in two tight columns, each with its number and
    a one-letter status tag. Type stays at 10pt: nothing on this
    page drops below the readable floor, for legibility's sake."""
    draw.text((28, top), "WHERE IT HAPPENED - dots = story numbers", font=faces["maphead"], fill=TEXT_INK)
    draw.text((312, top), "ALSO ON THURSDAY 26 NOVEMBER", font=faces["maphead"], fill=TEXT_INK)
    draw.line([28, top + 13, 300, top + 13], fill=LINE_INK, width=1)
    draw.line([312, top + 13, SHEET_W - 28, top + 13], fill=LINE_INK, width=1)
    scene_map(page, draw, faces, (28, top + 18, 300, top + 136))
    col_w = 340
    row_h = 10
    for idx, story in enumerate(LIST_ITEMS):
        slot, row = divmod(idx, 18)
        x = 312 + slot * (col_w + 4)
        yy = top + 16 + row * row_h
        draw.text((x, yy), str(story["no"]), font=faces["listnum"],
                  fill=CRIMSON)
        tx = x + 20  # headline starts here
        draw.text((tx, yy), story["title"], font=faces["listitem"],
                  fill=TEXT_INK)
        # a one-letter status tag at the column's right edge
        mark_x = x + col_w - 12
        tint = MARKS[story["mark"]][1]
        draw.rectangle([mark_x, yy, mark_x + 10, yy + 10], outline=tint, width=1)
        draw.text((mark_x + 3, yy + 1), story["mark"],
                  font=faces["status"], fill=tint)
    return top + 200  # footer follows


def scene_footer(draw, faces, y):
    """DATE CHECK: the date discipline, the left-out list, the
    status legend and the sources — the page's claim to trust."""
    draw.rectangle([28, y, 28 + 82, y + 13], fill=CRIMSON)
    draw.text((32, y + 2), "DATE CHECK", font=faces["footbold"], fill=(255, 255, 255))
    draw.text((118, y + 2), "17 stories first reported Thu 26 Nov · 30 carried from Wed 25 Nov · 3 from Tue 24 Nov.", font=faces["foottext"], fill=TEXT_INK)
    draw.text((28, y + 17), "Left out as earlier news: Nvidia's record surge (Mon 23) · Huang back at Nvidia (Mon 23) · CrowdStrike–Zscaler deal (Mon 23).", font=faces["foottext"], fill=TEXT_INK)
    draw.text((28, y + 30), "OFFICIAL an authority’s own figure or act · REPORTED press report · CLAIM one side’s account", font=faces["foottext"], fill=SLATE)
    src = ("Sources: KCNA, Reuters, AP, AFP, BBC, Yonhap, Bank of Korea, "
           "USTR, Ofgem, NWS. Every drawing original.")
    sw = draw.textlength(src, font=faces["foottext"])
    draw.text((SHEET_W - 28 - sw, y + 30), src, font=faces["foottext"],
              fill=SLATE)
    return y + 44  # page done


def main():  # entry point: draw the page and save entry.png
    """Draw the whole front page and write it out as entry.png."""
    faces = fetch_typefaces()
    sheet = Image.new("RGB", (SHEET_W, SHEET_H), PAGE_TINT)
    draw = ImageDraw.Draw(sheet)
    draw.rectangle([8, 8, SHEET_W - 9, SHEET_H - 9], outline=LINE_INK,
                   width=2)
    cursor = scene_masthead(draw, faces)
    cursor = scene_leads(sheet, draw, faces, cursor)
    cursor = scene_grid(sheet, draw, faces, cursor + 6)
    cursor = scene_numbers(draw, faces, cursor + 6)
    scene_bottom(sheet, draw, faces, cursor + 6)
    scene_footer(draw, faces, 970)
    out = pathlib.Path(__file__).resolve().parent / "entry.png"
    sheet.save(out, format="PNG", optimize=True)
    saved = out.read_bytes()
    print("entry.png written: %d bytes, sha256 %s"
          % (len(saved), hashlib.sha256(saved).hexdigest()))


if __name__ == "__main__":  # run when executed directly
    main()  # go
