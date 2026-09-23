# Dodge City Law — Unofficial Historical Archive

Total static rebuild of **dodgecityfootball.com** (Dodge City Law indoor
football, 2014–2017, folded 2017) from Internet Archive Wayback Machine
captures. No backend, no build step, no external requests.

## Run it

```sh
python3 -m http.server 8000
# browse http://localhost:8000/
```

Or open `index.html` directly — all links, CSS and images are relative
and local.

## What's here

- `index.html` — home / 2017 season recap (baseline: June 2017 capture)
- `schedule.html` — full 2017 schedule & results, 9–3 + playoff, transcribed
- `roster.html` — archived 2017 signings + original team sections
- `news.html` — six headlines Oct 2016–Apr 2017, one with article summary
- `tickets.html` — ticket/fan sections as history (nothing for sale)
- `arena.html` — United Wireless Arena, partners (names only), 2017 CIF teams
- `about-this-archive.html` — provenance, baseline, cutoff, citations
- `404.html` — archive-themed not-found page
- `assets/css/style.css` — all styling (local, no frameworks)
- `assets/img/dodge-city-law-logo.png` — only vendored image, from the
  June 2017 capture of `/images/dodge-city-law-logo.png`
- `research/` — raw baseline captures kept for audit
- `dodgecityfootball-rebuild-plan.md` — the build plan

## Archive rules followed

- Baseline `20170602095555`, cross-checked to `20170919`; cutoff excludes
  everything ≥ 2018-01-01 (parked-domain spam era).
- No hotlinking to `web.archive.org`; no trackers, ads, or social widgets.
- Persistent “unofficial historical archive, ceased operations 2017”
  framing on every page.

## GitHub

Target repo `https://github.com/JagJar/dodgecityfootball-rebuild`
(per owner: new repo, wired later — this tree is ready to `git init`,
commit, and push when you are).
