# Dodge City Law historical website restoration

A static restoration of **dodgecityfootball.com**, based on the original 2017
Joomla/Sportson site. Hosted by the existing Cloudflare Worker and Static Assets
configuration in `wrangler.jsonc`. Repository: `JagJar/dodge-city-football`.

The restoration restores the 1170px desktop composition, Titillium Web fonts,
team photographs, navigation artwork, standings and historical page URLs. It
adds responsive navigation, keyboard controls, roster filtering, and clear
source/recovery notes. No live team services or hotlinked media are included.

The 2017 sponsor ads have been removed until new ads replace them;
`research/ad-placements.md` records where each one was. The one third-party
script is the ad library (`//acscdn.com/script/aclib.js`), loaded in every
page's `<head>`; its AutoTag zone (`nvly1c3coi`) runs at the end of each
page's `<body>`.

## Build and preview

The generated `public/` files and `routes.js` are checked in, so serving the
site needs no build or downloads. Use Node 20+ for the Worker-aware preview:

```sh
npm run dev
# http://127.0.0.1:8000
```

To regenerate after editing the templates or preserved sources, use Python
3.9+ with Pillow (`python3 -m pip install -r requirements.txt`):

```sh
npm run build
npm test
```

Edit `scripts/build.py` for content and templates, `public/assets/css/style.css`
for styling, `public/assets/js/site.js` for progressive enhancements, and
`worker.js` for legacy URL handling. Do not hand-edit generated HTML or
`routes.js`.

A basic static server also works (`python3 -m http.server 8000 --directory
public`), but only the Worker-aware preview exercises PHP/Joomla redirects and
custom 404 status handling. Pages use root-relative URLs; opening an individual
HTML file directly is not a complete preview.

## What is restored

- Homepage composition and 14-team standings from June 2, 2017.
- All 24 roster listings and individual player URLs, reconstructed from roster
  fields. These are signed listings, not a verified game-day active roster.
- Six historical headline URLs: four recovered announcements, one surviving
  excerpt, and an attributed newspaper summary.
- Staff/coaches, full-size seating-chart image, original ticket-pricing artwork,
  and 13 recorded game results. Full box-score statistics have
  not been recovered; game-result pages say so.
- Historical navigation destinations, with explicit partial records where
  content is missing. `/archive-index.html` lists recovery status.
- `/index.php`, the old `/roster.html`, headline aliases, extensionless paths,
  documented Joomla article/player parameters, and `index.php/` prefixes.
- Root-relative themed 404 pages, a historical RSS feed, and a canonical sitemap.

`research/restoration-pages.json` inventories 89 pages. `research/legacy-routes.json`
lists 207 aliases and the supported query IDs. Counts include archive utility
pages and labeled partial reconstructions; they do not imply complete recovery
of every original page.

## Provenance and gaps

See `research/provenance.md`, `research/sitemap.md`, and the public
`/about-this-archive.html` page. The resource manifest records actual Wayback
response dates and SHA-256 hashes. Raw captures and original CSS are kept only
in `research/`; they are never deployed.

The page background slideshow, some fan/team sections, original ticket and
seating PDFs, individual player biographies, and detailed box scores remain
unrecovered. Missing material is labeled rather than invented. The recovered
schedule includes June results later than the homepage snapshot; its earlier
retrieval did not retain an exact response timestamp.

## Validation

`npm test` checks all canonical routes and aliases, Joomla parameters, combined
www/path redirects, HEAD behavior, read-only method handling, and genuine 404s.
The offline crawler checks generated HTML, local resources, CSS font/image
references, anchors, duplicate IDs, and coverage of original homepage paths.

The restoration was visually checked in Safari at desktop and 390px widths;
mobile menu/submenu navigation and roster search were exercised. Cloudflare's
Wrangler 4.83.0 deployment dry run passed with `env.ASSETS` bound correctly.
The execution environment blocked listening on localhost, so visual QA used a
temporary file-based copy while route tests called the Worker directly.

## Release

The asset binding is required: `worker.js` calls `env.ASSETS.fetch`. Explicit
`html_handling: none` preserves historical `.html` URLs, and the Worker serves
`/index.html` for `/` without a redirect loop. Unknown content and unrelated
parked-domain PDFs remain genuine 404 responses, never redirects to the home
page. Original asset folders bypass Worker routing.

From an environment with Cloudflare network access and the existing account:

```sh
npm run build
npm test
npx wrangler@4.83.0 deploy --dry-run
npx wrangler@4.83.0 deploy --keep-vars
```

Before a production release, retain the current Cloudflare deployment version.
After release, verify `/`, `/index.php`, `/team/roster.html`, a headline, a nested
missing URL, and their www variants. Confirm that `/index.php` redirects once to
`/`, old article links reach the specific article, and unknown paths return 404.
Watch request/status counts and Worker errors after rollout. Roll back to the
previous Cloudflare deployment version if those checks fail.

The production Worker is connected to `JagJar/dodge-city-football` on GitHub.
Changes merged to `main` trigger Cloudflare's deployment pipeline. Generated
assets and `routes.js` must be committed together with Worker changes so the
deployment is self-contained. Preserve the static asset binding on every release.

### Production runtime hotfix

Live Cloudflare logs subsequently confirmed that the earlier production version
`255a91f6` threw `Cannot read properties of undefined (reading 'fetch')` at
`worker.js:9:23`. Its configuration omitted `assets.binding`, while the Worker
called `env.ASSETS.fetch`. Existing static assets bypassed the Worker; missing
paths, including unrelated PDF crawler traffic, invoked the broken handler.

The one-line `"binding": "ASSETS"` correction was committed through GitHub's UI
as `60ef2a9aa69a320fb29bf3d7dc5fd102cea1fcb2`. Cloudflare's connected build succeeded
and deployed version `a371be61-647e-4f56-9730-c4feb3da835b`. Fresh live-log samples
from that version show `outcome: "ok"` with an empty exceptions list for the
same class of missing-PDF requests. The live homepage also loads successfully.
The rolling 24-hour error total still includes the earlier failures.
That hotfix changed only the production binding. The full restoration retains
the correction and adds the legacy routing and recovered static assets.
