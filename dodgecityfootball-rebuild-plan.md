## Goal

Rebuild dodgecityfootball.com as a static archival-tribute website for the defunct Dodge City Law indoor football team (folded ~2017), reconstructed from Internet Archive Wayback Machine captures, hosted as code in https://github.com/JagJar/dodgecityfootball-rebuild.

## Success Criteria

- The repo contains a complete static site that reproduces the structure and content of the pre-shutdown site (home, schedule/results, roster, news, tickets/sponsors-history, contact) as observed in 2016–2017 captures, with no dependency on live third-party servers from the original site.
- Every page, image, and stylesheet is either rebuilt source or a locally vendored archive asset with provenance noted; no hotlinking to `web.archive.org` remains in shipped pages.
- Post-shutdown domain-spam URLs (e.g. the 2018–2019 `*_manual*.pdf` captures) are explicitly excluded from the rebuild.
- The site builds/serves with zero backend: open `index.html` or one static-server command renders the full site locally.
- A reader can tell within 10 seconds that this is an unofficial historical archive of a team that ceased operations in 2017.

## Context And Current Facts

- Workspace `/Users/stephenarmstrong/Desktop/dodgecitylaw-rebuild` is empty and is not a git repo (`ls -la` shows only `.`/`..`; `git status` reports "not a git repository"). There is no existing code, spec, or plan convention to follow.
- Target repo `https://github.com/JagJar/dodgecityfootball-rebuild` (user-provided) is not publicly reachable at plan time: `curl https://api.github.com/repos/JagJar/dodgecityfootball-rebuild` returns `{"message": "Not Found"}`. Assumption: it is private, renamed, or not yet created; repo bootstrap is part of the work.
- Wayback CDX evidence (inspected via `curl` this run):
  - Broad query returns continuous `200 text/html` captures from `20131003060151` onward, confirming a multi-year capture history exists.
  - Homepage query `from=2016&to=2018` returns uninterrupted `200` captures through `20170919144156`, then a gap to `20181228124524`, consistent with a mid/late-2017 shutdown followed by domain repurposing.
  - `curl -w "%{http_code}" https://web.archive.org/web/20170602095555/http://dodgecityfootball.com/` returns `200`, so mid-2017 replay is directly viewable and is a good rebuild baseline.
  - A `collapse=urlkey` sample shows post-2017 captures are spam PDFs (`01_dodge_2500_repair_manual_download.pdf`, `03_toyota_matrix_manual_radio_wiring_pdf.pdf`, etc.), which must be blocklisted.
- Team background (user statement plus background search): Dodge City Law, Dodge City KS indoor football, inaugural 2014 season, played in CPIFL then CIF, last activity/penalty controversy 2017 season. Treat league details and win/loss records as content to verify against the archive captures themselves, not as plan-time facts.

## Constraints And Non-goals

- Total rebuild from archive only: do not copy any post-2017 parked-domain content; do not present the site as the live/official team.
- No backend, no CMS, no database, no build-time network fetches. The shipped site must work as plain static files.
- Do not clone trackers, ad scripts, or social widgets from captures; replace contact/ticket/purchase flows with clearly historical, non-functional equivalents.
- Non-goals: reviving e-commerce or ticket sales; exact pixel-clone of every historical season; recovering the original server stack; SEO takeover of the old domain.

## Key Decisions

- **Baseline snapshot: mid-2017 homepage capture `20170602095555`, cross-checked against late-2017 `20170919` captures.** Why: it is the newest verified-good replay before the capture gap; earlier 2016 captures fill gaps. Rejected: earliest (2013) baseline (too stale) and anything dated 2018+ (parked/spam era).
- **Rebuild, don't mirror.** Recreate pages as clean static source following the archive's information architecture, vendoring images/CSS assets locally, instead of saving raw Wayback HTML with rewritten URLs. Why: raw mirrors carry dead scripts, tracker cruft, and Wayback toolbar artifacts; rebuild is maintainable and honest about being a tribute. Rejected: byte-for-byte mirror.
- **Archive-cutoff rule: exclude every capture dated 2018-01-01 or later.** Why: CDX evidence shows the post-2017 namespace is polluted with manual-PDF spam. Rejected: "import everything under the domain."
- **Legal framing as unofficial historical archive with disclaimer on every template.** Why: team is defunct, but logos/photos may retain third-party rights; a persistent footer disclaimer plus a provenance page is the smallest safe framing. Rejected: presenting as the official club site.
- **Repo bootstrap is Phase 0 because the target is currently unreachable (API 404).** Why: no work can be reviewed until `git init` + remote + initial push path is settled. Default: initialize locally and wire to the user-provided URL once the owner confirms visibility.

## Recommended Approach

1. Inventory the archive via CDX for the `dodgecityfootball.com/` and `www.dodgecityfootball.com/` hostnames, capped at 2017-12-31, producing a URL manifest grouped by page type (home, schedule, roster, news, tickets, sponsors, contact) and asset type (images, stylesheets).
2. Render the baseline captures through Wayback replay, transcribe structure and copy into fresh static pages, and download only content assets (photos, logos, stylesheets-as-reference) into a local `assets/` tree with a provenance log (source capture timestamp + original URL).
3. Bootstrap the repo, commit the manifest + provenance log first, then the rebuilt static site, so reviewers can audit "what the archive said" separately from "what we rebuilt."
4. Ship responsive, accessible plain static files with a site-wide 2017-shutdown banner, historical-results tables, and a `/about-this-archive.html` provenance page; validate with a local static server and a link crawl before any publish step.

## Work Plan

- **Phase 0 — Repo bootstrap (blocks everything).**
  - `git init`, create layout (`index.html`, `schedule.html`, `roster.html`, `news/`, `assets/`, `about-this-archive.html`, `README.md`), wire remote to `https://github.com/JagJar/dodgecityfootball-rebuild` once owner confirms create/private-vs-public.
  - Validation: `git status --short --branch` and `git remote -v` show the expected remote; `git log --oneline` shows the bootstrap commit.
- **Phase 1 — Archive inventory.**
  - Run the two CDX queries in Sources (broad + 2016–2018 homepage) plus a per-section listing capped `--to 20171231`; save raw JSON as `research/cdx-manifest-*.json`.
  - Produce `research/sitemap.md`: canonical page list, chosen capture timestamp per page, excluded spam URLs with reason.
  - Validation: manifest files exist; every shipped page traces to one listed capture; zero `2018+` URLs in manifest.
- **Phase 2 — Asset triage and provenance.**
  - From replayed pages, download content images/logos; record each in `research/provenance.md` (original URL, capture timestamp, local path, license/owner unknown flag).
  - Blocklist: trackers, ad iframes, social widgets, post-2017 PDFs.
  - Validation: `grep -ri "web.archive.org" --include="*.html" .` returns nothing in shipped pages; all `<img src>` resolve to local `assets/`.
- **Phase 3 — Static rebuild.**
  - Rebuild templates: header/nav, footer with "Unofficial historical archive — team ceased operations 2017" disclaimer, home, schedule/results (2014–2017 tables as captured), roster, news index, tickets/sponsors-as-history, contact-as-history, 404 page.
  - Validation: `python3 -m http.server 8000` serves the whole site; manual pass over nav on desktop + mobile widths.
- **Phase 4 — QA and handoff.**
  - Dead-link crawl of the local server, image-404 check, readability/proof pass against baseline replays, README with run instructions and archive notes.
  - Validation: link-crawl report clean; README documents one-command local serve; working tree clean except intended files.

## Validation Plan

- Archive evidence: re-run the CDX queries in Sources and confirm the 2017 cutoff story still holds; expected evidence is the same `20170919` last-good / `20181228` gap pattern.
- Local serve: `python3 -m http.server 8000` from repo root, then browse `/`, `/schedule.html`, `/roster.html`, `/about-this-archive.html`; expected evidence is full render with no external requests (browser devtools network tab shows same-origin only).
- Link integrity: crawl the local server for dead internal links and missing images; expected evidence is zero 404s in the crawl log.
- History check: `git log --oneline` and `git status` confirm manifest, provenance, and site commits are separated as planned.

## Risks / Rollback

- Target repo stays unreachable (private/missing): keep all work on local `main` until the remote is confirmed; rollback is simply "do not push."
- Sparse captures for subpages (common with image-heavy schedule/roster pages): fall back to nearest-earlier capture and mark the page "partial — nearest capture YYYYMMDD"; never backfill from fan wikis.
- Rights uncertainty on logos/photos: mitigated by tribute framing, no merchandise/commerce, and provenance log; if the owner requests removal, delete the flagged asset and ship a text placeholder (rollback per-asset).
- Scope creep into pixel-perfect cloning: capped by the cutoff rule and the "rebuild, don't mirror" decision; any extra season added only with a listed capture timestamp.

## Open Questions

- Is `https://github.com/JagJar/dodgecityfootball-rebuild` private or yet-to-be-created, and should history start fresh (`git init`) or attach to an existing remote? Default: init locally now, wire remote on your confirmation.
- Faithful-clone styling vs. clean tribute styling under the same sitemap? Default: same sitemap and copy, clean modern CSS, original look referenced but not pixel-cloned.
- None beyond these: workspace facts were established by direct inspection above.

## Sources

- https://web.archive.org/cdx/search/cdx?url=dodgecityfootball.com/*&output=json&filter=statuscode:200&filter=mimetype:text/html&fl=timestamp,original,statuscode,digest&collapse=digest&limit=50
- https://web.archive.org/cdx/search/cdx?url=dodgecityfootball.com/&output=json&fl=timestamp,original,statuscode,digest&filter=statuscode:200&from=2016&to=2018&limit=30
- https://web.archive.org/web/20170602095555/http://dodgecityfootball.com/
