# Restoration provenance — 2026-10-22

The visual reference is the June 2, 2017 homepage:
https://web.archive.org/web/20170602095555/http://dodgecityfootball.com/

A July 12, 2017 homepage replay supplies surviving assets. The importer records
the **actual resource response timestamp**, which can differ from the page's
requested date. For example, the homepage photograph resolves to a later 2017
capture. The restoration is therefore a documented reconstruction using nearby
captures, not a claim that every byte existed in the June 2 snapshot.

## Evidence inventory

- `baseline-20170602.html`: original homepage structure, menus, headline dates,
  news excerpts, image maps, and North/South standings.
- `roster.html`: 24 readable listings, all preserved. Matched to the July 12,
  2017 roster replay (`20170712052125`). Individual profile pages reproduce
  these fields and do not claim recovery of the original biographies.
- `schedule-2017.html`: 13 recorded games, including the June 10 playoff.
  Earlier retrieval did not retain the exact response timestamp. The schedule
  is explicitly distinguished from the June 2 standings snapshot.
- `news-731.html`: Kiowa County Signal article; public page uses an attributed
  editorial summary, with a link to the archived original.
- `recovered/`: eight newly preserved main documents: July homepage, four full
  team releases, staff/coaches, seating chart, and ticket pricing.
- `recovered-assets.json`: 76 resources, including 49 image/icon files, two
  Titillium Web fonts, 17 reference stylesheets, and eight HTML captures.
  Each record has original URL, actual capture timestamp, replay URL, local
  path, MIME type, size, and SHA-256. Derived copies such as `/favicon.ico`
  come from the recorded original asset.
- `original-css/`: the original template CSS for design reference only.
- `restoration-pages.json` and `legacy-routes.json`: generated page and URL maps.

## Recovery method

Wayback pages were opened in Safari and saved as Web Archives. The local
`scripts/import_webarchive.py` importer extracts original response URLs from
Safari's saved response metadata. It accepts own-domain images, PDFs, CSS and
main HTML, plus the original Titillium Web fonts. Scripts, external widgets,
tracking resources and all captures dated January 1, 2018 or later are excluded.
Normal page views load only local resources. Explicit source links open Wayback.
The build is offline and reproducible from this repository.

## Known limitations

- The original background slide `dodge2.jpg` resolved to an October 25, 2018
  capture when requested on either hostname. It was excluded under the cutoff;
  the white backdrop visible in the accessible 2017 replay is retained.
- The full former-Chiefs article (727) was not returned from either tested
  hostname. Its verified headline and surviving homepage excerpt remain.
- Ticket artwork is reused under both pricing headings in the original March
  16, 2017 capture; its filename contains “2015.” That behavior is documented,
  not silently treated as independently verified 2017 prices.
- Seating-chart and season-ticket PDFs remain missing. The recovered seating
  JPEG is available at full resolution; the former PDF URL leads to that
  explanation, not an invented download.
- Missing fan/team text, original photo-gallery organization, box-score detail,
  and player biographies are identified on the corresponding pages.
- The mid-season standings and later schedule results have different dates;
  historical disciplinary adjustments are not reconstructed from game scores.

Original design credit: Trey Braid. Original imagery, logos, fonts and text
remain attributable to their creators; recovery does not establish a new
license or ownership claim. The public site identifies itself as an unofficial
historical archive and does not accept purchases, registrations or requests.
