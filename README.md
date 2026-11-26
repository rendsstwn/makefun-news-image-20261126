[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/rendsstwn/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard)
[![reward](https://make.fun/badge/news-image-20261126/rendsstwn/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

# The World Today — Thursday 26 November 2026

A single 1024×1024 picture that sums up one day of world news
as a newspaper front page: **THE WORLD TODAY**.

The front page leads with what is genuinely new on Thursday
26 November and big enough to carry the day — KCNA reporting
that Kim Jong Un ordered a wider tactical-nuclear deployment.
The American tariff proposal, first reported on Wednesday
25 November, stays near the top of the grid, labelled as
carried rather than dressed up as today's news. The two tankers
ablaze in the Strait of Hormuz stay on the page as a CLAIM:
Reuters reported them on 25 November with no independent
confirmation, so a claim must not lead the page.

Fifty stories in all: three large leads, twelve grid cards and
thirty-five more in the numbered ALSO ON list, across ten
regions and twenty fields. A strip of headline figures sits
under the nameplate, a dark BY THE NUMBERS strip sits near the
foot, and a small world map marks the fifteen featured stories
with numbered dots. The DATE CHECK footer prints the honest
split — 17 stories first reported Thu 26 Nov, 30 carried from
Wed 25 Nov, 3 from Tue 24 Nov — and names the earlier items
deliberately left out.

## What is in here

- `main.py` — the entry program, Python 3.13 with the standard
  library only. It ferries the bundled `entry.png` to
  `/output/entry.png` and checks the copy by SHA-256.
- `entry.png` — the front page itself, 1024×1024.
- `gen.py` — the build-time script that painted `entry.png`
  from the fifty verified stories, using Pillow and the DejaVu
  faces. Its story table is one flat list in display order, so
  a rebuild for another day means editing data only.

## Running it

Run `MAKEFUN_OUTPUT_DIR=out python3 main.py` — the program
creates the output folder itself if it is missing.

It reads nothing but the bundled picture, touches no network,
and writes the same bytes on every run — run it three times
and the output is byte-identical every time.

## How the stories were checked

Each story was checked against reporting dated Thursday
26 November 2026, or carried honestly from Wednesday 25 November
or Tuesday 24 November, with the split stated in the DATE CHECK
footer: 17 first reported Thu 26 Nov, 30 carried from Wed
25 Nov, 3 from Tue 24 Nov. The page names its day three times —
the nameplate date, the stat strip and the DATE CHECK footer —
and the footer lists what it left out on purpose: Nvidia's
record surge (Mon 23), Huang back at Nvidia (Mon 23), and the
CrowdStrike–Zscaler deal (Mon 23). Every story carries a status
word: OFFICIAL for an authority's own figure or act, REPORTED
for a press report, CLAIM for one side's account.

Licensed under the MIT license — see `LICENSE`.
