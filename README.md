[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/rendsstwn/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/rendsstwn/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# The World Today — 26 November 2026

One image summing up the world's news of Thursday 26 November
2026, drawn as a newspaper front page: **THE WORLD TODAY**.

The lead story is the day's biggest story that is genuinely
26 November — KCNA's report that Kim Jong Un called for a
wider tactical-nuclear deployment. The US tariff proposal of
25 November stays prominent as grid story 4, clearly carried
and not dressed as today's news. The Strait of Hormuz tanker
fires stay on the page, but as a CLAIM: Reuters reported them
on 25 November with no independent verification, and a claim
must not lead. Fifty stories in all — three large leads,
twelve grid cards and thirty-five more in the ALSO ON list —
across ten regions and twenty fields, with a BY THE NUMBERS
strip, a world map with numbered dots, and a DATE CHECK footer
that states the honest date split: 17 stories first reported
Thu 26 Nov, 30 carried from Wed 25 Nov, 3 from Tue 24 Nov.

## Files

- `main.py` — the entry program (Python 3.13, standard library
  only). It copies the bundled `entry.png` to `/output/entry.png`
  and verifies the copy by SHA-256.
- `entry.png` — the 1024x1024 front page itself.
- `gen.py` — the build-time script that drew `entry.png` from the
  fifty verified stories, using Pillow and the DejaVu fonts. Its
  `STORIES` list is one flat list in display order, so a rebuild
  can swap stories by editing data only.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program reads nothing but the bundled picture, touches no
network, and writes the same bytes on every run: three runs in a
row produce byte-identical `entry.png` files.

## Verification

Every story on the page was checked against reporting dated
Thursday 26 November 2026, or carried honestly from Wednesday
25 November or Tuesday 24 November with the split stated in the
DATE CHECK footer: 17 first reported Thu 26 Nov, 30 carried from
Wed 25 Nov, 3 from Tue 24 Nov. The page names its day three
times — the masthead date, the stat strip and the DATE CHECK
footer — and the footer lists the previous days' items it
deliberately left out: Nvidia's record surge (Mon 23), Huang
back at Nvidia (Mon 23), and the CrowdStrike–Zscaler deal
(Mon 23). Each story carries a status tag: OFFICIAL for an
authority's own figure or act, REPORTED for a press report,
CLAIM for one side's account.

## License

MIT — see `LICENSE`.
