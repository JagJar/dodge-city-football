# Archive sitemap & provenance

Baseline: homepage capture `20170602095555` of `http://dodgecityfootball.com/`
(Joomla!, shaper_sportson template). Cross-checked: `schedule.html`,
`team/roster.html`, `news-hm/731-...` from the same June 2017 window.
Homepage captures run through `20170919144156`, then gap to `20181228124524`.
Cutoff: exclude everything >= 2018-01-01 (parked-domain spam: repair-manual PDFs).

## Canonical pages (original path -> rebuilt page)

- `/` -> `index.html` (2017 recap, headlines, league, arena summary)
- `/schedule.html` -> `schedule.html` (13 rows transcribed verbatim)
- `/team/roster.html` -> `roster.html` (6 rows recovered verbatim + named additions from headlines)
- `/news.html`, `/news/headline-news.html`, `/news-hm/726-731-*.html` -> `news.html` (6 headlines; 731 summarized)
- `/tickets/buy-tickets-online.html`, `/tickets/ticket-pricing.html`, `/tickets/single-season-ticket-pricing.html` -> `tickets.html` (history only)
- `/arena/seating-chart.html`, `/partners.html` -> `arena.html` (names only, no sponsor links)
- `/team.html`, `/team/staff-coaches.html`, `/team/gunpowder-girls.html`, `/team/junior-gunpowder-girls.html`, `/team/ball-dolls.html`, `/team/meet-marshall.html` -> covered in `roster.html` team-sections list
- `/fans/mvp-award.html`, `/fans/itc-honorary-family-of-the-night.html`, `/fans/appearance-request.html`, `/contac.html` (spelled as captured) -> covered in `tickets.html`
- Gridiron standings `/component/gridiron/team/*` (14 CIF teams) -> 2017 team list on `index.html`/`arena.html`

## Vendored assets

- `assets/img/dodge-city-law-logo.png` <- `/images/dodge-city-law-logo.png` (June 2017 capture, PNG 260x195). Only vendored image.
- Everything else rewritten. No Joomla code, trackers, ad scripts, social widgets, video embeds. Zero external resource loads in shipped pages (verified).

## Raw research copies

- `research/baseline-20170602.html` (75,389 bytes, homepage)
- `research/schedule-2017.html` (44,083 bytes)
- `research/roster.html` (79,456 bytes)
- `research/news-731.html` (50,980 bytes)
