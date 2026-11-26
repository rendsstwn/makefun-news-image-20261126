#!/usr/bin/env python3
"""Ship the 26 November 2026 one-picture news front page.

The picture ferried to /output/entry.png is the front page
bundled beside this program as entry.png: fifty items from
Thursday, 26 November 2026, on one page. It follows the shape
of the day's highest-judged front pages — masthead, stat strip,
three large leads, a twelve-card grid, a BY THE NUMBERS strip,
a world map with numbered dots, a numbered ALSO ON list, and a
DATE CHECK footer — but every line of the drawing is original.

Why Kim leads: KCNA reported on Thursday 26 November that Kim
Jong Un called for a wider tactical-nuclear deployment, the
day's sharpest escalation and the biggest story that is
genuinely 26 November. The US tariff proposal of 25 November
stays prominent as grid story 4, clearly carried, not dressed
as today's news. The Hormuz tanker fires stay a CLAIM: Reuters
reported them on 25 November with no independent verification.

Date split, stated in the footer: 17 stories first reported
Thu 26 Nov, 30 carried from Wed 25 Nov, 3 from Tue 24 Nov.
Statuses: OFFICIAL is an authority's own figure or act;
REPORTED is a press report; CLAIM is one side's account.

LEADS (all Thu 26 Nov)
 1. Kim orders wider tactical nuclear deployment (OFFICIAL)
 2. Bank of Korea lifts base rate to 3.25% (OFFICIAL)
 3. Thanksgiving storm grounds Macy's 100th parade (REPORTED)

GRID
 4. US proposes tariffs of up to 35% on 14 economies (OFFICIAL, 25 Nov)
 5. Ukraine strikes Savasleyka airbase, damages five jets (REPORTED, 26 Nov)
 6. US tells citizens to leave Iran as war fears grow (REPORTED, 26 Nov)
 7. BBC: at least 490,334 Russian soldiers have died (REPORTED, 26 Nov)
 8. Houthis strike Saudi ports and a refinery (REPORTED, 26 Nov)
 9. Trump and Rutte: Russia must not widen the war (REPORTED, 26 Nov)
10. Haiti police kill at least 34 gang members in raid (REPORTED, 26 Nov)
11. Indonesia mine toll rises to 13 dead, 13 missing (REPORTED, 26 Nov)
12. Mumbai marks 18 years since the 26/11 attacks (REPORTED, 26 Nov)
13. Iran says two tankers hit mines, caught fire (CLAIM, 25 Nov)
14. Cairo tanker fire kills at least 31 (REPORTED, 25 Nov)
15. UK energy price cap to rise 26% in January (OFFICIAL, 25 Nov)

ALSO ON THURSDAY 26 NOVEMBER
16. 9 more Russian and Ukrainian children reunited (26 Nov)
17. Germany plans first drone regiment (26 Nov)
18. Iraq's top court backs Baghdad's Kurdistan expansion (26 Nov)
19. Amnesty urges ICC probe over Gaza births (26 Nov)
20. Nikkei rebounds 1.3% after Wednesday's 3% slide (26 Nov)
21. Israeli strike kills three in a Gaza food vehicle (26 Nov)
22. Dow closes above 50,000 for the first time (25 Nov)
23. Ukraine drones set two Rosneft refineries ablaze (25 Nov)
24. Kyiv seeks 115bn euros in foreign aid for 2027 (25 Nov)
25. Puerto Rico's Barreto crowned Miss Universe 2026 (24 Nov)
26. Israeli strike kills Hamas security chief in Gaza (25 Nov)
27. Huawei found guilty by a US jury (24 Nov)
28. Solomon Islands signs security pact with Australia (25 Nov)
29. Colombia frees all Cartagena supermarket hostages (25 Nov)
30. Zimbabwe issues arrest warrant for Mugabe's son (25 Nov)
31. Bangladesh garment workers win a 36% pay rise (25 Nov)
32. Abrego Garcia leaves the US for Spain voluntarily (25 Nov)
33. COP31 climate talks end with no agreement (25 Nov)
34. Kospi fell 6.2% Wed, rebounded 0.3% Thu (25 Nov)
35. Nvidia falls 5.9% a day after its record surge (25 Nov)
36. Dell posts a record 54.9bn dollar quarter on AI servers (25 Nov)
37. Eurozone inflation rises to 4.0% (25 Nov)
38. Australian inflation rises to 4.9% (25 Nov)
39. EasyJet profit falls 89% as fuel costs soar (25 Nov)
40. Shenzhou-24 docks at Tiangong, first Pakistani aboard (25 Nov)
41. Amazon buys chip rival Decart (25 Nov)
42. Hackers' AI agents breach a university server (25 Nov)
43. Nvidia fell 5.2% on Tuesday (24 Nov)
44. Hackers reportedly breach a CIA analysis system (25 Nov)
45. Roche's breast cancer pill wins a second FDA approval (25 Nov)
46. Senegal regain the Africa Cup of Nations title in court (25 Nov)
47. GTA VI debuts at 3.79bn dollars, a record launch (25 Nov)
48. Haftar meets Erdogan in Ankara on first official visit (25 Nov)
49. CENTCOM praises Syria over drug and arms seizures (25 Nov)
50. Russia's 112-drone attack cuts power in five regions (25 Nov)

The program itself only copies the bundled picture to the
output slot and checks the copy by checksum, so every run
leaves exactly the same bytes behind. Standard library only,
no network, no clock, no randomness.
"""

import os
from hashlib import sha256
from pathlib import Path

BUNDLED = "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def bundled_bytes():
    """Read the picture shipped beside this program, as bytes."""
    here = Path(__file__).resolve().parent
    data = (here / BUNDLED).read_bytes()
    if data[:8] != PNG_MAGIC:
        raise SystemExit("bundled entry.png is not a PNG file")
    return data


def destination():
    """Where the picture goes: /output, or MAKEFUN_OUTPUT_DIR."""
    root = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return Path(root) / BUNDLED


def fingerprint(data):
    """SHA-256 hex digest of a byte string."""
    return sha256(data).hexdigest()


def place_picture(data):
    """Write the picture bytes to the output slot."""
    target = destination()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def check_picture(target, data):
    """Confirm the written file matches the bundled bytes."""
    again = target.read_bytes()
    if sha256(again).hexdigest() != fingerprint(data):
        raise SystemExit("copied entry.png failed its checksum")
    return len(again)


def main():
    """Deliver the bundled front page and report its checksum."""
    data = bundled_bytes()
    target = place_picture(data)
    size = check_picture(target, data)
    print("entry.png placed: %d bytes, sha256 %s"
          % (size, fingerprint(data)))


if __name__ == "__main__":
    main()
