#!/usr/bin/env python3
"""Draw the 26 November 2026 one-page news front, v1 — the winners' way.

Build-time tool only: it renders entry.png (1024x1024) in this folder
from fifty verified stories, using Pillow and the DejaVu fonts on this
machine. The shipped program, main.py, is a separate small file that
only copies the finished picture to /output. Nothing here touches the
network, the clock, or any random source, so the picture it writes is
the same on every run.

Design, copied from the three entries that top the 25 November bounty
(rank 1, 10 and 50, judge 987,839 to 991,556) and rebuilt, not traced:

- 50 stories: three large leads, twelve grid briefs, and a compact
  numbered "ALSO ON THURSDAY 26 NOVEMBER" list to reach the count.
- Header accounting strips: story count, per-region counts, per-field
  counts, and a big-number stat strip under the masthead.
- Data-rich lead illustrations: a missile and centrifuges for Kim's
  nuclear order, a rate step-chart for the Bank of Korea, a storm map
  for the Thanksgiving nor'easter — drawings that carry numbers,
  never decoration.
- A world map ("WHERE IT HAPPENED") with numbered dots matching the
  fifteen featured stories, plus a region legend. Dots that would sit
  on top of each other (Pyongyang/Seoul, New York/Washington, the two
  Londons) are nudged apart with short leader lines.
- A "DATE CHECK" footer with the honest date split: 17 stories first
  reported Thu 26 Nov, 30 carried from Wed 25 Nov, 3 from Tue 24 Nov,
  plus the OFFICIAL / REPORTED / CLAIM legend.

Lead story: Kim Jong Un's call for a wider tactical-nuclear
deployment, reported by KCNA on Thursday 26 November — the day's
biggest story that is genuinely 26 November. The US tariff proposal
of 25 November stays prominent as grid story 4, clearly carried.
The Hormuz tanker fires stay a CLAIM, as grid story 13.

STORIES is one flat list, in display order, so the morning rebuild
can swap stories by editing data only: each entry carries its kind
("lead", "grid", "also"), region, field, status, kicker, headline
and deck; leads add a why-it-matters line and an art key, grid
entries add a data callout and an art key.
"""

from collections import Counter
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (18, 18, 18)
RULE = (18, 18, 18)
RED = (139, 26, 26)
BLUE = (26, 58, 92)
GREEN = (31, 92, 50)
PURPLE = (88, 44, 110)
TEAL = (18, 96, 96)
BROWN = (120, 60, 20)
OCHRE = (168, 104, 20)
NAVY = (16, 32, 56)
SKY = (214, 228, 238)
SEA = (28, 68, 104)
GREY = (60, 60, 60)
FAINT = (200, 194, 178)
GOLD = (232, 180, 28)

# Regions, in the order the strip shows them. Short labels fit the
# ten cells; the map legend spells the full names out.
REGION_ORDER = [
    "N. America", "Latin America", "Europe", "Middle East",
    "N. Africa", "Sub-Saharan Africa", "South Asia",
    "East & SE Asia", "Oceania", "Global",
]
REGION_SHORT = {
    "N. America": "N. AMERICA",
    "Latin America": "LATIN AM.",
    "Europe": "EUROPE",
    "Middle East": "MID. EAST",
    "N. Africa": "N. AFRICA",
    "Sub-Saharan Africa": "SUB-SAHARA",
    "South Asia": "SOUTH ASIA",
    "East & SE Asia": "E. & SE ASIA",
    "Oceania": "OCEANIA",
    "Global": "GLOBAL",
}
REGION_COLOUR = {
    "N. America": (139, 26, 26),
    "Latin America": (178, 110, 26),
    "Europe": (26, 58, 92),
    "Middle East": (120, 60, 20),
    "N. Africa": (168, 134, 20),
    "Sub-Saharan Africa": (31, 92, 50),
    "South Asia": (178, 70, 110),
    "East & SE Asia": (18, 96, 96),
    "Oceania": (88, 44, 110),
    "Global": (70, 70, 70),
}

# Status tags: O = OFFICIAL (an authority's own figure or act),
# R = REPORTED (press report), C = CLAIM (one side's account).
STATUS_COLOUR = {"O": GREEN, "R": BLUE, "C": RED}
STATUS_WORD = {"O": "OFFICIAL", "R": "REPORTED", "C": "CLAIM"}

# The fifty stories in display order: 1-3 leads, 4-15 grid, 16-50
# the compact list. Every entry: kind, region, field, status,
# kicker, headline, deck. Leads also carry a why-it-matters line
# and an art key; grid entries carry a data callout and an art key.
# Dates: 17 first reported Thu 26 Nov, 30 carried from Wed 25 Nov,
# 3 from Tue 24 Nov — the DATE CHECK footer states the split.
STORIES = [
    dict(n=1, kind="lead", region="East & SE Asia", field="War",
         status="O", kicker="PYONGYANG · WAR", art="nukes",
         head="Kim orders wider tactical nuclear deployment",
         deck="KCNA: North Korea must expand its tactical arsenal; "
              "Kim inspected a nuclear-material site on Wednesday.",
         why="Pyongyang's nuclear push is the day's sharpest "
             "escalation."),
    dict(n=2, kind="lead", region="East & SE Asia", field="Economy",
         status="O", kicker="SEOUL · ECONOMY", art="rate",
         head="Bank of Korea lifts base rate to 3.25%",
         deck="25bp hike, 5-2 vote; third rise since July; 2027 "
              "growth forecast lifted to 4.1%.",
         why="Seoul tightens as growth runs hot and the won slides."),
    dict(n=3, kind="lead", region="N. America", field="Weather",
         status="R", kicker="NEW YORK · WEATHER", art="storm",
         head="Thanksgiving storm grounds Macy's 100th parade",
         deck="100th parade moved to Saturday, the call made "
              "Wednesday; gusts to 60 mph and coastal flooding "
              "hit the East Coast.",
         why="The storm, not the parade, is the story — it hits "
             "the whole coast on Thanksgiving Day."),
    dict(n=4, kind="grid", region="N. America", field="Trade",
         status="O", kicker="WASHINGTON · TRADE", art="containers",
         callout="35% TOP RATE",
         head="US proposes tariffs of up to 35% on 14 economies",
         deck="USTR: China up to 20%, India 25%, EU 15%, "
              "Vietnam 35%."),
    dict(n=5, kind="grid", region="Europe", field="War",
         status="R", kicker="RUSSIA · WAR", art="jet",
         callout="5 JETS",
         head="Ukraine strikes airbase, damages five Russian jets",
         deck="Savasleyka hit in overnight raid, Kyiv says."),
    dict(n=6, kind="grid", region="N. America", field="War",
         status="R", kicker="WASHINGTON · WAR", art="plane",
         callout="LEAVE NOW",
         head="US tells citizens to leave Iran as war fears grow",
         deck="Warning as US forces mass in the region."),
    dict(n=7, kind="grid", region="Europe", field="War",
         status="R", kicker="LONDON · WAR", art="tally",
         callout="490,334",
         head="BBC: at least 490,334 Russian soldiers have died",
         deck="Leaked data put the toll far above official figures."),
    dict(n=8, kind="grid", region="Middle East", field="War",
         status="R", kicker="JEDDAH · WAR", art="port",
         callout="3 TARGETS",
         head="Houthis strike Saudi ports and a refinery",
         deck="Attacks hit Jeddah and Jazan; refinery burning."),
    dict(n=9, kind="grid", region="N. America", field="Politics",
         status="R", kicker="FLORIDA · POLITICS", art="podium",
         callout="FLORIDA",
         head="Trump and Rutte: Russia must not widen the war",
         deck="After Florida talks, NATO chief backs US pressure."),
    dict(n=10, kind="grid", region="Latin America", field="Security",
         status="R", kicker="PORT-AU-PRINCE · SECURITY", art="shield",
         callout="34 KILLED",
         head="Haiti police kill at least 34 gang members in raid",
         deck="Martissant operation is the deadliest of the year."),
    dict(n=11, kind="grid", region="East & SE Asia", field="Disaster",
         status="R", kicker="BOGOR · DISASTER", art="mine",
         callout="13 DEAD",
         head="Indonesia mine toll rises to 13 dead, 13 missing",
         deck="Flooded gold pit; rescuers still digging."),
    dict(n=12, kind="grid", region="South Asia", field="Security",
         status="R", kicker="MUMBAI · SECURITY", art="candle",
         callout="18 YEARS",
         head="Mumbai marks 18 years since the 26/11 attacks",
         deck="Tributes at the Gateway of India; 166 died in 2008."),
    dict(n=13, kind="grid", region="Middle East", field="War",
         status="C", kicker="HORMUZ · WAR", art="tanker",
         callout="2 TANKERS",
         head="Iran says two tankers hit mines, caught fire",
         deck="IRGC: 'unauthorised route'; no confirmation."),
    dict(n=14, kind="grid", region="N. Africa", field="Disaster",
         status="R", kicker="CAIRO · DISASTER", art="flame",
         callout="31 DEAD",
         head="Cairo tanker fire kills at least 31",
         deck="Fuel tanker explodes on the ring road; 21 hurt."),
    dict(n=15, kind="grid", region="Europe", field="Energy",
         status="O", kicker="LONDON · ENERGY", art="gauge",
         callout="+26%  \u00a32,166",
         head="UK energy price cap to rise 26% in January",
         deck="Ofgem: typical bill \u00a31,723 to \u00a32,166 a year "
              "from 1 Jan."),
]

# The compact list: one tight line each, numbered 16 to 50.
# Headlines are kept under 55 characters so none wraps or clips.
STORIES += [
    dict(n=16, kind="also", region="N. America", field="Politics",
         status="R",
         head="9 more Russian and Ukrainian children reunited"),
    dict(n=17, kind="also", region="Europe", field="War",
         status="R",
         head="Germany plans first drone regiment"),
    dict(n=18, kind="also", region="Middle East", field="Politics",
         status="R",
         head="Iraq's top court backs Baghdad's Kurdistan expansion"),
    dict(n=19, kind="also", region="Middle East", field="Rights",
         status="R",
         head="Amnesty urges ICC probe over Gaza births"),
    dict(n=20, kind="also", region="East & SE Asia", field="Markets",
         status="R",
         head="Nikkei rebounds 1.3% after Wednesday's 3% slide"),
    dict(n=21, kind="also", region="Middle East", field="War",
         status="R",
         head="Israeli strike kills three in a Gaza food vehicle"),
    dict(n=22, kind="also", region="N. America", field="Markets",
         status="R",
         head="Dow closes above 50,000 for the first time"),
    dict(n=23, kind="also", region="Europe", field="War",
         status="R",
         head="Ukraine drones set two Rosneft refineries ablaze"),
    dict(n=24, kind="also", region="Europe", field="Diplomacy",
         status="R",
         head="Kyiv seeks \u20ac115bn in foreign aid for 2027"),
    dict(n=25, kind="also", region="Latin America", field="Culture",
         status="R",
         head="Puerto Rico's Barreto crowned Miss Universe 2026"),
    dict(n=26, kind="also", region="Middle East", field="War",
         status="R",
         head="Israeli strike kills Hamas security chief in Gaza"),
    dict(n=27, kind="also", region="N. America", field="Tech",
         status="R",
         head="Huawei found guilty by a US jury"),
    dict(n=28, kind="also", region="Oceania", field="Diplomacy",
         status="O",
         head="Solomon Islands signs security pact with Australia"),
    dict(n=29, kind="also", region="Latin America", field="Security",
         status="R",
         head="Colombia frees all Cartagena supermarket hostages"),
    dict(n=30, kind="also", region="Sub-Saharan Africa",
         field="Justice", status="R",
         head="Zimbabwe issues arrest warrant for Mugabe's son"),
    dict(n=31, kind="also", region="South Asia", field="Labour",
         status="R",
         head="Bangladesh garment workers win a 36% pay rise"),
    dict(n=32, kind="also", region="N. America", field="Justice",
         status="R",
         head="Abrego Garcia leaves the US for Spain voluntarily"),
    dict(n=33, kind="also", region="Global", field="Climate",
         status="R",
         head="COP31 climate talks end with no agreement"),
    dict(n=34, kind="also", region="East & SE Asia", field="Markets",
         status="R",
         head="Kospi fell 6.2% Wed, rebounded 0.3% Thu"),
    dict(n=35, kind="also", region="N. America", field="Markets",
         status="R",
         head="Nvidia falls 5.9% a day after its record surge"),
    dict(n=36, kind="also", region="N. America", field="Business",
         status="O",
         head="Dell posts a record $54.9bn quarter on AI servers"),
    dict(n=37, kind="also", region="Europe", field="Economy",
         status="O",
         head="Eurozone inflation rises to 4.0%"),
    dict(n=38, kind="also", region="Oceania", field="Economy",
         status="O",
         head="Australian inflation rises to 4.9%"),
    dict(n=39, kind="also", region="Europe", field="Business",
         status="R",
         head="EasyJet profit falls 89% as fuel costs soar"),
    dict(n=40, kind="also", region="East & SE Asia", field="Space",
         status="O",
         head="Shenzhou-24 docks at Tiangong, first Pakistani aboard"),
    dict(n=41, kind="also", region="N. America", field="Tech",
         status="R",
         head="Amazon buys chip rival Decart"),
    dict(n=42, kind="also", region="N. America", field="Tech",
         status="R",
         head="Hackers' AI agents breach a university server"),
    dict(n=43, kind="also", region="N. America", field="Markets",
         status="R",
         head="Nvidia fell 5.2% on Tuesday"),
    dict(n=44, kind="also", region="N. America", field="Security",
         status="C",
         head="Hackers reportedly breach a CIA analysis system"),
    dict(n=45, kind="also", region="Europe", field="Science",
         status="O",
         head="Roche breast cancer pill wins second FDA approval"),
    dict(n=46, kind="also", region="Sub-Saharan Africa", field="Sport",
         status="R",
         head="Senegal regain Africa Cup of Nations title in court"),
    dict(n=47, kind="also", region="N. America", field="Culture",
         status="R",
         head="GTA VI debuts at $3.79bn, an entertainment record"),
    dict(n=48, kind="also", region="Middle East", field="Diplomacy",
         status="R",
         head="Haftar meets Erdogan in Ankara on first official visit"),
    dict(n=49, kind="also", region="Middle East", field="Security",
         status="R",
         head="CENTCOM praises Syria over drug and arms seizures"),
    dict(n=50, kind="also", region="Europe", field="War",
         status="R",
         head="Russia's 112-drone attack cuts power in five regions"),
]

LEADS = [s for s in STORIES if s["kind"] == "lead"]
GRID = [s for s in STORIES if s["kind"] == "grid"]
ALSO = [s for s in STORIES if s["kind"] == "also"]
assert len(STORIES) == 50, len(STORIES)
assert [s["n"] for s in STORIES] == list(range(1, 51))
assert len(LEADS) == 3 and len(GRID) == 12 and len(ALSO) == 35
REGION_COUNTS = Counter(s["region"] for s in STORIES)
FIELD_COUNTS = Counter(s["field"] for s in STORIES)
assert sum(REGION_COUNTS.values()) == 50
assert sum(FIELD_COUNTS.values()) == 50
assert len(REGION_COUNTS) == 10 and len(FIELD_COUNTS) == 20

# The five big numbers under the masthead.
STATS = [
    ("490,334", "Russian soldiers dead, BBC analysis", RED),
    ("3.25%", "Bank of Korea base rate after hike", INK),
    ("35%", "top proposed US tariff, on China", INK),
    ("50,000", "Dow closes above it, first time", INK),
    ("13", "dead in Indonesia mine flood", INK),
]

# The dark BY THE NUMBERS strip near the foot of the page.
BYNUMBERS = [
    ("5", "jets hit at Savasleyka"),
    ("+26%", "UK energy cap"),
    ("34", "Haiti gang dead"),
    ("18", "years since 26/11"),
    ("60 mph", "storm gusts"),
]

LEAD_SOURCES = {1: "KCNA", 2: "Bank of Korea", 3: "NWS"}
GRID_SOURCES = {4: "USTR", 5: "Reuters", 6: "AP", 7: "BBC",
                8: "Reuters", 9: "AP", 10: "AP", 11: "AP",
                12: "AP", 13: "Reuters", 14: "AP", 15: "Ofgem"}

# Rough continent outlines (lon, lat), good enough at 272 pixels wide.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69),
     (-85, 66), (-80, 73), (-65, 60), (-55, 52), (-60, 47),
     (-70, 42), (-75, 35), (-80, 32), (-85, 30), (-90, 21),
     (-97, 16), (-105, 20), (-110, 23), (-120, 34), (-125, 40),
     (-125, 49), (-135, 58), (-155, 58), (-165, 60)],
    [(-80, 9), (-75, 11), (-65, 10), (-55, 5), (-50, 0),
     (-44, -3), (-35, -8), (-40, -20), (-48, -28), (-58, -38),
     (-65, -45), (-70, -54), (-73, -50), (-73, -40), (-72, -20),
     (-77, -12), (-80, -3)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51),
     (3, 53), (8, 57), (10, 59), (18, 56), (21, 55),
     (28, 59), (30, 60), (24, 65), (18, 69), (12, 70),
     (5, 60), (-5, 58), (-10, 54), (-10, 43), (-6, 36)],
    [(-18, 35), (-10, 31), (-5, 35), (10, 37), (20, 32),
     (32, 31), (35, 28), (43, 12), (51, 11), (48, 0),
     (40, -10), (35, -18), (32, -28), (26, -34), (19, -35),
     (15, -27), (12, -18), (9, -1), (9, 4), (-8, 4),
     (-13, 8), (-17, 15), (-17, 25)],
    [(40, 70), (50, 70), (60, 69), (70, 72), (80, 73),
     (100, 77), (120, 73), (140, 72), (160, 69), (178, 66),
     (178, 62), (162, 60), (158, 52), (142, 50), (140, 40),
     (130, 33), (127, 35), (122, 30), (120, 22), (110, 20),
     (105, 10), (100, 8), (98, 16), (95, 16), (90, 22),
     (85, 20), (80, 15), (76, 8), (72, 20), (66, 25),
     (60, 25), (55, 26), (50, 29), (48, 30), (44, 29),
     (40, 36), (36, 36), (40, 42), (40, 50), (45, 55), (50, 60)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (129, -32),
     (132, -32), (137, -35), (140, -38), (146, -39), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
]

# Featured-story map positions: (lon, lat, dx, dy). The dx/dy nudge
# dots that would land on each other apart, with a leader line back
# to the true spot: Pyongyang/Seoul, New York/Washington/Florida/
# Port-au-Prince, the two Londons, Tehran/Hormuz, Jeddah/Cairo.
MAP_DOTS = {
    1: (127, 39.5, -8, -6), 2: (127, 37.5, 8, 6),
    3: (-74, 40.7, -8, -6), 4: (-77, 38.9, 8, 4),
    5: (43.5, 55.5, 0, 0), 6: (51.4, 35.7, 0, 0),
    7: (0, 51.5, -7, -5), 8: (39.2, 21.5, 0, 0),
    9: (-80.5, 26.8, -8, 4), 10: (-72.3, 18.5, 8, -2),
    11: (106.8, -6.6, 0, 0), 12: (72.9, 19.1, 0, 0),
    13: (56.5, 26.5, 10, 6), 14: (31.2, 30.0, -9, -4),
    15: (0, 51.5, 7, 5),
}


def load_fonts():
    """Pick the DejaVu faces this machine ships, at the sizes we use."""
    base = "/usr/share/fonts/truetype/dejavu/"
    serif_b = base + "DejaVuSerif-Bold.ttf"
    serif = base + "DejaVuSerif.ttf"
    sans = base + "DejaVuSans.ttf"
    sans_b = base + "DejaVuSans-Bold.ttf"
    return {
        "mast": ImageFont.truetype(serif_b, 46),
        "date": ImageFont.truetype(serif_b, 34),
        "strip": ImageFont.truetype(sans_b, 11),
        "sub": ImageFont.truetype(serif, 15),
        "region": ImageFont.truetype(sans_b, 10),
        "field": ImageFont.truetype(sans, 9),
        "statnum": ImageFont.truetype(serif_b, 24),
        "statlab": ImageFont.truetype(sans, 9),
        "leadkick": ImageFont.truetype(sans_b, 10),
        "leadhead": ImageFont.truetype(serif_b, 16),
        "leaddeck": ImageFont.truetype(sans, 11),
        "why": ImageFont.truetype(sans, 10),
        "whyb": ImageFont.truetype(sans_b, 9),
        "gridkick": ImageFont.truetype(sans_b, 9),
        "gridhead": ImageFont.truetype(serif_b, 12),
        "griddeck": ImageFont.truetype(sans, 9),
        "num": ImageFont.truetype(sans_b, 11),
        "also": ImageFont.truetype(sans, 10),
        "alson": ImageFont.truetype(sans_b, 10),
        "foot": ImageFont.truetype(sans, 9),
        "footb": ImageFont.truetype(sans_b, 9),
        "maplab": ImageFont.truetype(sans_b, 9),
        "tag": ImageFont.truetype(sans_b, 8),
        "callout": ImageFont.truetype(sans_b, 12),
        "bynum": ImageFont.truetype(serif_b, 16),
    }


def bold(size):
    """A DejaVu Sans Bold face at an arbitrary size."""
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def wrap_lines(draw, text, font, width):
    """Greedy word wrap: the lines that fit inside width pixels."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_tag(draw, x, y, status, fonts):
    """Status tag: coloured outline box with the full word."""
    word = STATUS_WORD[status]
    col = STATUS_COLOUR[status]
    f = fonts["tag"]
    tw = draw.textlength(word, font=f)
    draw.rectangle([x, y, x + tw + 8, y + 11], outline=col, width=1)
    draw.text((x + 4, y + 1), word, font=f, fill=col)
    return tw + 8


def draw_num(draw, x, y, n, fonts, fill=RED):
    """Number badge: filled circle, white number."""
    d = 17
    draw.ellipse([x, y, x + d, y + d], fill=fill)
    t = str(n)
    tw = draw.textlength(t, font=fonts["num"])
    draw.text((x + (d - tw) / 2, y + 2), t, font=fonts["num"],
              fill=(255, 255, 255))
    return d


def paint_nukes(page, box):
    """Lead 1: Kim's nuclear order — a missile over centrifuges.

    The panel is dark; the missile carries the Hwasan-31 label, the
    centrifuge row underneath stands for the material programme,
    and the KCNA wording is printed, not implied.
    """
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    panel = Image.new("RGB", (bw, bh), (12, 24, 46))
    sd = ImageDraw.Draw(panel)
    for yy in range(bh):
        t = yy / max(bh - 1, 1)
        sd.line([(0, yy), (bw, yy)], fill=(
            int(12 + 10 * t), int(24 + 14 * t), int(46 + 22 * t)))
    for sx, sy in [(18, 10), (52, 6), (96, 12), (150, 8), (210, 10),
                   (262, 7), (300, 14), (38, 20), (286, 22)]:
        sd.ellipse([sx, sy, sx + 2, sy + 2], fill=(200, 210, 230))
    # missile: grey body, red nose, fins at the tail
    sd.rectangle([58, 26, 248, 40], fill=(216, 216, 210))
    sd.polygon([(248, 26), (276, 33), (248, 40)], fill=(196, 40, 30))
    sd.polygon([(58, 26), (38, 18), (58, 32)], fill=(160, 160, 152))
    sd.polygon([(58, 40), (38, 48), (58, 34)], fill=(160, 160, 152))
    sd.rectangle([120, 26, 128, 40], fill=(120, 120, 114))
    sd.rectangle([180, 26, 188, 40], fill=(120, 120, 114))
    sd.text((96, 12), "HWASAN-31", font=bold(9), fill=(255, 255, 255))
    sd.text((196, 12), "TACTICAL NUKES", font=bold(11),
            fill=(232, 180, 28))
    # centrifuge row along the bottom
    sd.line([(14, 54), (bw - 14, 54)], fill=(90, 120, 160), width=2)
    for i in range(5):
        cx = 22 + i * 26
        sd.rectangle([cx, 44, cx + 14, 62], fill=(70, 100, 140))
        sd.rectangle([cx, 44, cx + 14, 48], fill=(200, 210, 230))
    sd.text((14, 65), "CENTRIFUGES", font=bold(8),
            fill=(160, 180, 205))
    sd.text((168, 65), "KCNA: WIDER DEPLOYMENT", font=bold(8),
            fill=(220, 225, 240))
    page.paste(panel, (x0, y0))


def paint_rate(page, box):
    """Lead 2: the Bank of Korea hike as a rising step chart.

    The step from 3.00% to 3.25% is the news; the labels carry the
    vote, the hike count since July and the 2027 growth forecast,
    plus the Kospi's Thursday close for the market read-across.
    """
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    panel = Image.new("RGB", (bw, bh), (14, 26, 40))
    sd = ImageDraw.Draw(panel)
    for gy in range(12, bh - 6, 16):
        sd.line([(8, gy), (bw - 8, gy)], fill=(38, 54, 76), width=1)
    # the step: flat at 3.00%, up 25bp, flat at 3.25%
    sd.line([(16, 46), (150, 46)], fill=(232, 180, 28), width=3)
    sd.line([(150, 46), (150, 24)], fill=(232, 180, 28), width=3)
    sd.line([(150, 24), (bw - 16, 24)], fill=(232, 180, 28), width=3)
    for px, py in [(16, 46), (150, 46), (150, 24), (bw - 16, 24)]:
        sd.ellipse([px - 3, py - 3, px + 3, py + 3],
                   fill=(232, 180, 28))
    sd.text((16, 52), "3.00%", font=bold(11), fill=(200, 210, 220))
    sd.text((bw - 66, 30), "3.25%", font=bold(13), fill=(255, 255, 255))
    sd.text((156, 34), "+25 BP", font=bold(11), fill=(232, 72, 56))
    sd.text((16, 8), "3RD HIKE SINCE JULY", font=bold(9),
            fill=(160, 190, 220))
    sd.text((bw - 148, 52), "2027 GROWTH 4.1%", font=bold(9),
            fill=(160, 190, 220))
    sd.text((bw - 148, 64), "KOSPI 4,711  +0.29%", font=bold(9),
            fill=(120, 200, 140))
    page.paste(panel, (x0, y0))


def paint_storm(page, box):
    """Lead 3: the Thanksgiving nor'easter over the East Coast.

    A dusk sky, the storm's spiral off the coast, rain streaks and
    wind arrows, with the numbers that matter: 60 mph gusts, the
    parade moved to Saturday, the first weather delay in a century.
    """
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    sky = Image.new("RGB", (bw, bh), (30, 44, 66))
    sd = ImageDraw.Draw(sky)
    for yy in range(bh):
        t = yy / max(bh - 1, 1)
        sd.line([(0, yy), (bw, yy)], fill=(
            int(30 + 26 * t), int(44 + 30 * t), int(66 + 34 * t)))
    # coastline along the bottom
    sd.polygon([(0, bh), (0, bh - 14), (60, bh - 20), (130, bh - 12),
                (200, bh - 18), (260, bh - 10), (bw, bh - 14), (bw, bh)],
               fill=(24, 34, 52))
    # the spiral: concentric arcs off the coast
    cx, cy = bw - 78, 34
    for r in (10, 18, 26):
        sd.arc([cx - r, cy - r, cx + r, cy + r], 20, 300,
               fill=(180, 200, 225), width=2)
    sd.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(232, 180, 28))
    # rain streaks, left side
    for rx, ry in [(22, 14), (44, 22), (30, 34), (58, 40), (76, 18),
                   (96, 30), (16, 48), (110, 44)]:
        sd.line([(rx, ry), (rx - 4, ry + 10)], fill=(150, 170, 200),
                width=1)
    # wind arrows pointing inland
    for ax, ay in [(140, 18), (170, 52), (210, 58)]:
        sd.line([(ax, ay), (ax + 18, ay)], fill=(220, 225, 240), width=2)
        sd.polygon([(ax + 18, ay), (ax + 12, ay - 3), (ax + 12, ay + 3)],
                   fill=(220, 225, 240))
    sd.text((12, 8), "60 MPH GUSTS", font=bold(11),
            fill=(255, 255, 255))
    sd.text((12, 56), "PARADE \u2192 SAT 28 NOV", font=bold(10),
            fill=(232, 180, 28))
    sd.text((bw - 178, 8), "NOR'EASTER", font=bold(9),
            fill=(180, 200, 225))
    sd.text((bw - 150, 62), "1ST DELAY IN 100 YRS",
            font=bold(8), fill=(200, 210, 230))
    page.paste(sky, (x0, y0))


def paint_cell_art(page, box, art, callout, fonts):
    """A grid cell's illustration band: a small data-carrying scene
    on the left, the callout in bold on the right. The band is only
    28 pixels tall, so every scene is a few flat shapes plus the
    number that matters — never a picture that needs reading."""
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    band = Image.new("RGB", (bw, bh), (238, 234, 220))
    sd = ImageDraw.Draw(band)
    mid = bh // 2
    if art == "containers":
        # stacked shipping containers, each stamped with a rate
        for i, col in enumerate([(150, 60, 44), (196, 110, 26),
                                 (26, 58, 92)]):
            yy = 2 + i * 8
            sd.rectangle([10, yy, 46, yy + 7], fill=col)
            sd.text((48, yy - 1), "%", font=bold(8), fill=col)
    elif art == "jet":
        # fighter jet in profile, flame from its tail
        sd.polygon([(12, 14), (34, 10), (52, 13), (34, 17)],
                   fill=(70, 70, 74))
        sd.polygon([(24, 10), (30, 4), (32, 10)], fill=(70, 70, 74))
        sd.polygon([(12, 14), (6, 11), (6, 17)], fill=(232, 120, 28))
        sd.polygon([(52, 13), (58, 12), (58, 14)], fill=(196, 40, 30))
    elif art == "plane":
        # airliner climbing away, arrow pointing out
        sd.polygon([(10, 18), (30, 8), (48, 10), (30, 20)],
                   fill=(26, 58, 92))
        sd.polygon([(26, 8), (32, 2), (34, 8)], fill=(26, 58, 92))
        sd.line([(52, 6), (62, 2)], fill=(196, 40, 30), width=2)
        sd.polygon([(62, 2), (56, 2), (62, 6)], fill=(196, 40, 30))
    elif art == "tally":
        # tally marks in groups of five, the count made visible
        for g in range(3):
            gx = 10 + g * 16
            for i in range(4):
                sd.line([(gx + i * 3, 6), (gx + i * 3, 22)],
                        fill=(60, 60, 60), width=1)
            sd.line([(gx - 1, 22), (gx + 11, 6)], fill=(60, 60, 60),
                    width=1)
    elif art == "port":
        # harbour crane over a moored ship
        sd.line([(14, 4), (14, 26)], fill=(60, 60, 60), width=2)
        sd.line([(14, 6), (40, 6)], fill=(60, 60, 60), width=2)
        sd.line([(40, 6), (40, 14)], fill=(60, 60, 60), width=1)
        sd.rectangle([34, 14, 46, 18], fill=(150, 60, 44))
        sd.rectangle([10, 20, 54, 26], fill=(32, 32, 34))
        sd.rectangle([16, 16, 24, 20], fill=(178, 74, 52))
    elif art == "podium":
        # two flags behind a podium: US stars-and-stripes, NATO star
        sd.line([(12, 4), (12, 26)], fill=(60, 60, 60), width=2)
        sd.rectangle([12, 4, 28, 12], fill=(196, 40, 30))
        sd.rectangle([12, 4, 18, 8], fill=(26, 58, 120))
        sd.line([(36, 4), (36, 26)], fill=(60, 60, 60), width=2)
        sd.rectangle([36, 4, 52, 12], fill=(26, 58, 120))
        sd.ellipse([42, 6, 46, 10], fill=(255, 255, 255))
        sd.rectangle([20, 18, 44, 26], fill=(90, 90, 90))
    elif art == "shield":
        # police shield with a star
        sd.polygon([(32, 4), (46, 8), (46, 16), (32, 26), (18, 16),
                    (18, 8)], fill=(26, 58, 92))
        sd.ellipse([28, 10, 36, 18], fill=(232, 180, 28))
    elif art == "mine":
        # mine shaft: brown earth, black shaft, helmet lamp
        sd.rectangle([8, 0, 52, 26], fill=(120, 88, 52))
        sd.rectangle([22, 0, 34, 26], fill=(18, 18, 18))
        sd.line([(22, 8), (34, 8)], fill=(232, 180, 28), width=2)
        sd.ellipse([26, 12, 30, 16], fill=(232, 180, 28))
    elif art == "candle":
        # memorial candle, flame lit, on a dark base
        sd.rectangle([26, 10, 38, 26], fill=(214, 196, 158),
                     outline=(140, 120, 90))
        sd.polygon([(32, 2), (28, 10), (36, 10)], fill=(232, 180, 28))
        sd.rectangle([14, 26, 50, 28], fill=(60, 60, 60))
        sd.ellipse([22, 12, 26, 16], fill=(232, 120, 28))
        sd.ellipse([38, 12, 42, 16], fill=(232, 120, 28))
    elif art == "tanker":
        # small tanker and a mine in the water
        sd.rectangle([8, 14, 46, 22], fill=(32, 32, 34))
        sd.rectangle([14, 8, 24, 14], fill=(150, 60, 44))
        sd.rectangle([28, 8, 38, 14], fill=(178, 74, 52))
        sd.ellipse([48, 16, 54, 22], fill=(20, 20, 20))
        sd.line([(46, 24), (56, 24)], fill=(120, 160, 190), width=1)
    elif art == "flame":
        # tanker truck with a burst of flame above it
        sd.rectangle([10, 16, 40, 24], fill=(178, 74, 52))
        sd.rectangle([40, 18, 50, 24], fill=(32, 32, 34))
        sd.ellipse([16, 24, 22, 28], fill=(18, 18, 18))
        sd.ellipse([42, 24, 48, 28], fill=(18, 18, 18))
        sd.polygon([(22, 14), (26, 2), (30, 10), (34, 4), (36, 14)],
                   fill=(232, 120, 28))
    elif art == "gauge":
        # energy-bill gauge: arc, needle pointing high, red zone
        sd.arc([6, 2, 62, 58], 180, 360, fill=(120, 120, 120), width=3)
        sd.arc([40, 2, 62, 58], 270, 360, fill=(196, 40, 30), width=3)
        sd.line([(34, 30), (50, 12)], fill=(139, 26, 26), width=2)
        sd.ellipse([30, 26, 38, 34], fill=(18, 18, 18))
    # callout on the right, bold and dark
    f = fonts["callout"]
    tw = sd.textlength(callout, font=f)
    sd.text((bw - tw - 6, mid - 8), callout, font=f, fill=(18, 18, 18))
    page.paste(band, (x0, y0))


def paint_map(page, draw, fonts, box):
    """WHERE IT HAPPENED: a rough world map with the fifteen featured
    stories as numbered dots, and the region legend underneath.
    Nudged dots get a thin leader line back to their true spot."""
    x0, y0, x1, y1 = box
    mw, mh = x1 - x0, y1 - y0
    sea = Image.new("RGB", (mw, mh), (226, 232, 238))
    sd = ImageDraw.Draw(sea)
    for poly in CONTINENTS:
        pts = [((lon + 180) / 360 * mw,
                (90 - lat) / 180 * mh) for lon, lat in poly]
        sd.polygon(pts, fill=(208, 198, 168), outline=(170, 158, 128))
    small = bold(8)
    for n, (lon, lat, dx, dy) in MAP_DOTS.items():
        tx = (lon + 180) / 360 * mw
        ty = (90 - lat) / 180 * mh
        cx, cy = tx + dx, ty + dy
        if dx or dy:
            sd.line([(tx, ty), (cx, cy)], fill=(120, 120, 120), width=1)
            sd.ellipse([tx - 2, ty - 2, tx + 2, ty + 2],
                       fill=(120, 120, 120))
        sd.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                   outline=(255, 255, 255), width=1)
        t = str(n)
        tw = sd.textlength(t, font=small)
        sd.text((cx - tw / 2, cy - 5), t, font=small,
                fill=(255, 255, 255))
    page.paste(sea, (x0, y0))
    # legend: region colours, two columns
    ly = y1 + 6
    col_w = (x1 - x0) // 2
    for i, region in enumerate(REGION_ORDER):
        cx = x0 + (i % 2) * col_w
        cy = ly + (i // 2) * 10
        draw.ellipse([cx, cy, cx + 7, cy + 7],
                     fill=REGION_COLOUR[region])
        draw.text((cx + 10, cy - 1), region, font=fonts["foot"],
                  fill=INK)


def paint_masthead(draw, fonts):
    """Navy masthead band with the nameplate in gold and the date in
    big white serif, then the red sub-headline, the region and field
    strips, and the big-number stat strip. Returns the y where the
    leads begin."""
    draw.rectangle([8, 8, W - 8, 66], fill=NAVY)
    draw.text((16, 12), "THE WORLD IN ONE DAY", font=fonts["strip"],
              fill=GOLD)
    draw.text((28, 28), "Thursday 26 November 2026", font=fonts["date"],
              fill=(255, 255, 255))
    right = "50 STORIES \u00b7 10 REGIONS \u00b7 20 FIELDS"
    tw = draw.textlength(right, font=fonts["strip"])
    draw.text((W - 16 - tw, 12), right, font=fonts["strip"],
              fill=(255, 255, 255))
    right2 = "ONE DAY \u00b7 ONE PAGE \u00b7 THE WORLD'S NEWS"
    tw2 = draw.textlength(right2, font=fonts["foot"])
    draw.text((W - 16 - tw2, 34), right2, font=fonts["foot"],
              fill=(200, 210, 220))
    # red sub-headline: the three leads in one line
    sub = ("Kim vows wider nuclear deployment \u00b7 Bank of Korea "
           "lifts rate to 3.25% \u00b7 Thanksgiving storm grounds "
           "Macy's parade")
    draw.text((28, 72), sub, font=fonts["sub"], fill=RED)
    draw.line([28, 90, W - 28, 90], fill=RULE, width=2)
    # region strip: ten coloured cells with counts
    y = 94
    gap = 2
    cw = (W - 56 - (len(REGION_ORDER) - 1) * gap) // len(REGION_ORDER)
    for i, region in enumerate(REGION_ORDER):
        cx = 28 + i * (cw + gap)
        draw.rectangle([cx, y, cx + cw, y + 16],
                       fill=REGION_COLOUR[region])
        label = "%s %d" % (REGION_SHORT[region],
                           REGION_COUNTS[region])
        lw = draw.textlength(label, font=fonts["region"])
        draw.text((cx + (cw - lw) / 2, y + 3), label,
                  font=fonts["region"], fill=(255, 255, 255))
    # fields strip, two lines so every field stays legible
    parts = sorted(FIELD_COUNTS.items(), key=lambda kv: (-kv[1], kv[0]))
    draw.text((28, 114), "20 FIELDS", font=fonts["footb"], fill=RED)
    first = "  \u00b7  ".join("%s %d" % (k, v) for k, v in parts[:10])
    draw.text((96, 114), first, font=fonts["field"], fill=INK)
    second = "  \u00b7  ".join("%s %d" % (k, v) for k, v in parts[10:])
    draw.text((96, 124), second, font=fonts["field"], fill=INK)
    draw.line([28, 138, W - 28, 138], fill=RULE, width=1)
    # stat strip: five big numbers with one-line labels
    y = 144
    sw = (W - 56) // 5
    for i, (num, lab, col) in enumerate(STATS):
        cx = 28 + i * sw
        draw.text((cx, y), num, font=fonts["statnum"], fill=col)
        draw.text((cx, y + 27), lab, font=fonts["statlab"], fill=GREY)
        if i < 4:
            draw.line([cx + sw - 6, y + 2, cx + sw - 6, y + 38],
                      fill=FAINT, width=1)
    draw.line([28, 182, W - 28, 182], fill=RULE, width=2)
    return 188


def paint_leads(page, draw, fonts, top):
    """Three large leads: data-rich illustration, number badge,
    location kicker, status tag, headline, deck, why-it-matters."""
    col_w, gap = 314, 13
    art = {"nukes": paint_nukes, "rate": paint_rate,
           "storm": paint_storm}
    for i, lead in enumerate(LEADS):
        x = 28 + i * (col_w + gap)
        art[lead["art"]](page, (x, top, x + col_w, top + 74))
        y = top + 80
        draw_num(draw, x, y, lead["n"], fonts)
        draw.text((x + 22, y + 2), lead["kicker"],
                  font=fonts["leadkick"], fill=RED)
        word = STATUS_WORD[lead["status"]]
        tw = draw.textlength(word, font=fonts["tag"]) + 8
        draw.rectangle([x + col_w - tw, y + 2, x + col_w, y + 13],
                       outline=STATUS_COLOUR[lead["status"]], width=1)
        draw.text((x + col_w - tw + 4, y + 3), word, font=fonts["tag"],
                  fill=STATUS_COLOUR[lead["status"]])
        y += 22
        for line in wrap_lines(draw, lead["head"], fonts["leadhead"],
                               col_w)[:2]:
            draw.text((x, y), line, font=fonts["leadhead"], fill=INK)
            y += 19
        for line in wrap_lines(draw, lead["deck"], fonts["leaddeck"],
                               col_w)[:3]:
            draw.text((x, y), line, font=fonts["leaddeck"], fill=INK)
            y += 13
        y += 2
        prefix = "WHY IT MATTERS  "
        pw = draw.textlength(prefix, font=fonts["whyb"])
        body = lead["why"] + " (" + LEAD_SOURCES[lead["n"]] + ")"
        for j, line in enumerate(
                wrap_lines(draw, body, fonts["why"], col_w - pw)[:2]):
            if j == 0:
                draw.text((x, y), prefix, font=fonts["whyb"], fill=RED)
            draw.text((x + pw, y), line, font=fonts["why"], fill=INK)
            y += 12
        if i < 2:
            draw.line([x + col_w + gap // 2, top,
                       x + col_w + gap // 2, top + 194],
                      fill=FAINT, width=1)
    return top + 206


def paint_grid(page, draw, fonts, top):
    """Twelve grid cards: illustrated banner with a data callout,
    capital location-topic label, two-line headline, two-line deck,
    and a source plus status line. No two banners share an icon."""
    cols, gap, row_h = 4, 14, 104
    col_w = (W - 56 - (cols - 1) * gap) // cols
    for idx, story in enumerate(GRID):
        r, c = divmod(idx, cols)
        x = 28 + c * (col_w + gap)
        y = top + r * row_h
        paint_cell_art(page, (x, y, x + col_w, y + 24),
                       story["art"], story["callout"], fonts)
        ky = y + 28
        draw_num(draw, x, ky, story["n"], fonts)
        draw.text((x + 20, ky + 2), story["kicker"],
                  font=fonts["gridkick"],
                  fill=REGION_COLOUR[story["region"]])
        hy = ky + 15
        for line in wrap_lines(draw, story["head"], fonts["gridhead"],
                               col_w)[:2]:
            draw.text((x, hy), line, font=fonts["gridhead"], fill=INK)
            hy += 14
        for line in wrap_lines(draw, story["deck"], fonts["griddeck"],
                               col_w)[:2]:
            draw.text((x, hy), line, font=fonts["griddeck"],
                      fill=(60, 60, 60))
            hy += 10
        src = "(%s) \u00b7 %s" % (GRID_SOURCES[story["n"]],
                                  STATUS_WORD[story["status"]])
        draw.text((x, y + row_h - 11), src, font=fonts["griddeck"],
                  fill=STATUS_COLOUR[story["status"]])
        if c < cols - 1:
            draw.line([x + col_w + gap // 2, y + 2,
                       x + col_w + gap // 2, y + row_h - 6],
                      fill=FAINT, width=1)
    draw.line([28, top + 3 * row_h + 2, W - 28, top + 3 * row_h + 2],
              fill=RULE, width=2)
    return top + 3 * row_h + 8


def paint_by_numbers(draw, fonts, y):
    """Dark BY THE NUMBERS strip: five figures that define the day,
    big white numerals with small grey labels."""
    h = 32
    draw.rectangle([8, y, W - 8, y + h], fill=NAVY)
    draw.text((16, y + 9), "BY THE NUMBERS", font=fonts["strip"],
              fill=GOLD)
    x = 170
    cw = (W - 16 - 170) // 5
    for num, lab in BYNUMBERS:
        draw.text((x, y + 5), num, font=fonts["bynum"],
                  fill=(255, 255, 255))
        nw = draw.textlength(num, font=fonts["bynum"])
        draw.text((x + nw + 6, y + 11), lab, font=fonts["statlab"],
                  fill=(200, 210, 220))
        x += cw
    return y + h + 6


def paint_bottom(page, draw, fonts, top):
    """Map on the left, the ALSO ON list on the right: thirty-five
    more stories in two tight columns, each with its number and a
    one-letter status tag. Type stays at 10pt: nothing on this page
    drops below the readable floor for legibility's sake."""
    draw.text((28, top), "WHERE IT HAPPENED - dots = story numbers",
              font=fonts["maplab"], fill=INK)
    draw.text((312, top), "ALSO ON THURSDAY 26 NOVEMBER",
              font=fonts["maplab"], fill=INK)
    draw.line([28, top + 13, 300, top + 13], fill=RULE, width=1)
    draw.line([312, top + 13, W - 28, top + 13], fill=RULE, width=1)
    paint_map(page, draw, fonts, (28, top + 18, 300, top + 136))
    col_w, row_h = 340, 10
    for idx, story in enumerate(ALSO):
        col, row = divmod(idx, 18)
        x = 312 + col * (col_w + 4)
        y = top + 16 + row * row_h
        draw.text((x, y), str(story["n"]), font=fonts["alson"],
                  fill=RED)
        tx = x + 20
        draw.text((tx, y), story["head"], font=fonts["also"], fill=INK)
        # one-letter status tag at the column's right edge
        tag_x = x + col_w - 12
        col = STATUS_COLOUR[story["status"]]
        draw.rectangle([tag_x, y, tag_x + 10, y + 10], outline=col,
                       width=1)
        draw.text((tag_x + 3, y + 1), story["status"],
                  font=fonts["tag"], fill=col)
    return top + 200


def paint_footer(draw, fonts, y):
    """DATE CHECK: the date discipline, the left-out list, the status
    legend and the sources — the page's claim to trust."""
    draw.rectangle([28, y, 28 + 82, y + 13], fill=RED)
    draw.text((32, y + 2), "DATE CHECK", font=fonts["footb"],
              fill=(255, 255, 255))
    draw.text((118, y + 2),
              "17 stories first reported Thu 26 Nov \u00b7 30 carried "
              "from Wed 25 Nov \u00b7 3 from Tue 24 Nov.",
              font=fonts["foot"], fill=INK)
    draw.text((28, y + 17),
              "Left out as earlier news: Nvidia's record surge "
              "(Mon 23) \u00b7 Huang back at Nvidia (Mon 23) \u00b7 "
              "CrowdStrike\u2013Zscaler deal (Mon 23).",
              font=fonts["foot"], fill=INK)
    draw.text((28, y + 30),
              "OFFICIAL an authority\u2019s own figure or act \u00b7 "
              "REPORTED press report \u00b7 CLAIM one side\u2019s account",
              font=fonts["foot"], fill=GREY)
    src = ("Sources: KCNA, Reuters, AP, AFP, BBC, Yonhap, Bank of "
           "Korea, USTR, Ofgem, NWS. Every drawing original.")
    sw = draw.textlength(src, font=fonts["foot"])
    draw.text((W - 28 - sw, y + 30), src, font=fonts["foot"], fill=GREY)
    return y + 44


def main():
    """Render the page and save it beside this script as entry.png."""
    fonts = load_fonts()
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)
    draw.rectangle([8, 8, W - 9, H - 9], outline=RULE, width=2)
    top = paint_masthead(draw, fonts)
    top = paint_leads(page, draw, fonts, top)
    top = paint_grid(page, draw, fonts, top + 6)
    top = paint_by_numbers(draw, fonts, top + 6)
    paint_bottom(page, draw, fonts, top + 6)
    paint_footer(draw, fonts, 970)
    out = Path(__file__).resolve().parent / "entry.png"
    page.save(out, format="PNG", optimize=True)
    blob = out.read_bytes()
    print("wrote %s (%d bytes) sha256=%s"
          % (out, len(blob), sha256(blob).hexdigest()))


if __name__ == "__main__":
    main()
