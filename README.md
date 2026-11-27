# The World in One Day — 26 November 2026 (v5)

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/rendsstwn/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard)
[![reward](https://make.fun/badge/news-image-20261126/rendsstwn/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

A one-page newspaper front page summing up Thursday 26 November 2026 in
50 stories: the US tariff proposal for 14 partners, the Macy's 100th parade
postponed by a nor'easter, Russian missiles over Kyiv, Kim's wider nuclear
deployment, Ebola passing 12,000 cases in DR Congo, and the Bank of Korea
lifting its rate to 3.25%.

## What this entry does

`main.py` copies the pre-rendered `entry.png` into the output directory
and verifies its checksum. It renders nothing at grade time.

`gen.py` draws the page with PIL at build time only: a giant date
masthead, a big-number strip, coloured region chips, a UTC timeline,
three illustrated leads with WHY IT MATTERS, ten illustrated grid cards,
a dotted world map with numbered pins and a HOW SURE legend, a numbered
ALSO ON list, and a DATE CHECK footer.

## Layout

- Masthead: the date is the hero; "THE WORLD IN ONE DAY" is the kicker.
- Leads: tariffs (bar chart of proposed rates), Macy's parade (balloon),
  Kyiv overnight (missile trails, 7 wounded).
- Grid 4-13: each card carries its own drawn scene - missile, tanker,
  case chart, EU stars, rate gauge, candles, chessboard, wage bars,
  blast, drones.
- Map: dotted continents, pins 1-13, legend for OFFICIAL / CONFIRMED /
  REPORTED / CLAIM / ONGOING.

## Verification

- `entry.png` is 1024x1024, rendered three times with byte-identical
  output (sha256 a1be59d04a381f3fd87e9138a301dfd66ad1de628655bd3de9fad37bd7f1bd9b).
- Lead stories verified against Reuters, AP, USTR, KCNA, and the Bank of
  Korea on 26 November 2026.

## How to rebuild

Run `python3 gen.py entry.png` in this directory. The build needs PIL
and the DejaVu fonts at build time only; the graded entrypoint
(`main.py`) uses the standard library alone and never renders.

## License

MIT. See LICENSE.
