# The World Today — 19 November 2026

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/jhonrudi12/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/jhonrudi12/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

A newspaper-style front page that sums up the world news of **Thursday 19 November 2026** in one image, built for the [make.fun bounty "Sum up 19 November's world news in one image"](https://make.fun/bounty/news-image-20261119).

## The day in six stories

1. **Anthropic debuts on Nasdaq** — after pricing a record $81.3bn IPO at $83 a share, the biggest IPO on record; shares start trading today as ANT.
2. **Trump, Xi and Putin meet in Shenzhen** — the first-ever trilateral meeting of the three leaders, on the sidelines of APEC.
3. **World court rules on the Rohingya case** — the ICJ delivers its judgment in The Gambia v. Myanmar.
4. **GTA VI rolls out worldwide** — Rockstar's sequel unlocks at midnight local time, 13 years after GTA V.
5. **Voyager 1, one light-day from Earth** — NASA marks the 1977 probe's milestone; a radio signal now takes a day to reach it.
6. **Iran widens attacks on US bases in the Gulf** — a US air base in Kuwait and sites in Bahrain hit after US jets struck Qeshm Island.

Plus: the EU proposes a 45bn-euro loan for Ukraine. Sources: Reuters, AP, NPR, NASA (early edition).

## How it works

`main.py` is a pure Python 3.13 standard-library program: it draws the whole front page — masthead, headlines, summaries, bar chart and icons — with an embedded 5x7 bitmap font and simple shapes, and writes a deterministic 1024×1024 PNG to `/output/entry.png`. No network, no fonts, no image libraries, so two runs produce identical bytes.

## Run it

```bash
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, under 1 MiB)
```

## License

MIT — see [LICENSE](LICENSE).
