# The World in One Day — 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/rendsstwn/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard)
[![reward](https://make.fun/badge/news-image-20261126/rendsstwn/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

A one-page newspaper front page that sums up **Thursday 26 November 2026**
in a single image: 50 stories, 9 regions, one day. Cream paper, black serif
masthead, three illustrated leads, a ten-card grid, a numbered world map,
an ALSO ON list, and a DATE CHECK footer.

## The three leads

1. **Macy's 100th parade postponed** (New York, OFFICIAL) — the Thanksgiving
   storm grounds the centenary march; 60 mph gusts push it to Saturday 28 Nov.
2. **Kim orders wider nuclear deployment** (Pyongyang, OFFICIAL) — KCNA
   reports tactical nuclear weapons going to front-line units on Thursday.
3. **Bank of Korea lifts rate to 3.25%** (Seoul, OFFICIAL) — third hike since
   July, 5–2 vote; 2027 growth outlook raised to 4.1% on AI exports.

## The day in ten (stories 4–13)

4. EU deadlocked on €45bn Ukraine loan (Brussels, REPORTED)
5. India marks 18 years since 26/11 (Mumbai, OFFICIAL)
6. Gukesh v Sindarov, Game 3 (Geneva, OFFICIAL)
7. Bangladesh garment wage Tk17,000 (Dhaka, REPORTED)
8. BBC: 490,334 Russian soldiers dead (London, REPORTED)
9. Israel kills Hamas economy chief (Gaza, REPORTED)
10. Russia hits Ukraine with 113 drones (Kyiv, REPORTED)
11. UK–EU publish reset treaties (London, REPORTED)
12. Spain sends army to El Hierro (El Hierro, REPORTED)
13. Kospi claws back +0.3% (Seoul, REPORTED)

## And also (stories 14–50)

Myanmar refuses ICJ orders · Ramaphosa eulogy for Mlambo-Ngcuka · India A v
Sri Lanka A semi-final · Hera shows the DART crater · Malaysia sues Google
$146m · Nigeria seizes $227m meth lab · US jobless claims 189,000 · EU caps
hybrid car imports · Boehly's $10bn Lukoil swap · IS attack in Hasakah ·
IPL 2027 auction: 1,220 players · Brazil tariff "unacceptable" · Argentina
names Brazil ambassador · Puerto Rico Luma deal · U-17 World Cup · North
Korea orders Swiss office shut · Korail work-to-rule · Vance on Huang ·
Lee's seven seed projects · Xi probe reaches Chen Jining · Brazil dengue
down 68% · Palm Beach ferries strike · Swiss tourist, Cameroon elephants ·
Iowa explosives disposal · Coalition hits Hodeidah · UN sacks Gaza staff ·
Saudi kidnapped in Niger · Gulf of Mexico plane crash · PIA resumes UK
flights · IITs add 6,000 seats · Australia inflation 4.9% · India–Nepal
₹15,000cr package · Tempus $600m cash election · Colombia hostages freed ·
Sudan RSF strikes · Savasleyka jets · Solomon Islands–Australia pact.

## Build

```sh
python3 main.py        # writes /output/entry.png (1024x1024, deterministic)
python3 gen.py entry.png
```

The renderer uses only Pillow and the DejaVu fonts shipped with the system.
No network access, no random seeds: running it three times produces
byte-identical PNGs.

## Sources

KCNA, Bank of Korea, Reuters, BBC, AFP, AP, FIDE, USTR, ABS, SAnews,
NDLEA, MCMC. Status tags: OFFICIAL = announced by the authority;
REPORTED = reported by two or more outlets; CLAIM = one side's claim.

## License

MIT — see LICENSE.
