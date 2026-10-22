# Ad placements

The historical 2017 sponsor ads were removed on 2026-10-22 to make room for new
ads. This note records where each one was, its size, and the code in
`scripts/build.py` that produced it, so new ads can go back in the same spots.

- The image files are still in `public/images/league/ads/` and
  `public/images/league/partners/`. No page links to them now.
- The CSS for every slot is still in `public/assets/css/style.css`. A new ad
  that uses the same markup and class names picks up the original styling,
  including the smaller sizes on tablet and phone.
- The previous/next carousel script in `public/assets/js/site.js` is still
  there. It does nothing on pages without a `.sponsor-rotation` section.

## Ad library

Every page built by `layout()` in `scripts/build.py` loads the ad network's
library in its `<head>`:

```html
<script id="aclib" type="text/javascript" src="//acscdn.com/script/aclib.js"></script>
```

`scripts/check_links.py` allows this one external script through
`ALLOWED_EXTERNAL`. Any other external resource still fails the check.

The AutoTag zone runs at the end of every page's `<body>`, after the footer:

```html
<script type="text/javascript">aclib.runAutoTag({zoneId: 'nvly1c3coi'});</script>
```

AutoTag is site-wide. The ad network picks the ad formats and where they
appear, using the zone's settings in its dashboard. It does not fill the
slots listed below. Ads in those exact spots would need a banner zone for
each one.

## Summary

| # | Slot | Page | Where | Original image size | Sponsor |
|---|------|------|-------|---------------------|---------|
| 1 | Title sponsor banner | Every page (89) | Full width, directly above the footer | 1170 × 120 | Western Plains Medical Complex |
| 2 | Hero sidebar tile | Home | Bottom of the Team News / League News column, right of the hero photo | 520 × 400, shown 145px wide | Freddy's Frozen Custard & Steakburgers |
| 3 | Full-width banner | Home | Directly below the hero | 1170 × 200 | G&G and McDonald's |
| 4 | Sponsor carousel | Home | Below slot 3, above the "2017 season archive" strip | 1170 × 90 per slide, 3 slides | AB Creative, Cargill, United Wireless Arena |
| 5 | Secondary links banner | Home | Below the CIF standings, above the news cards | 1170 × 160 | The Dodge House, Z98 |
| 6 | Partner gallery | `/partners.html` | Page body | All of the above | All of the above |

The homepage used to run in this order (ad slots in bold):

1. Top navigation banner (social icons, ticket links, ticket phone line)
2. Hero photo with the news column, **with the Freddy's tile (slot 2)** at the bottom
3. **G&G / McDonald's banner (slot 3)**
4. **Sponsor carousel (slot 4)**
5. "2017 season archive" strip
6. Quick links (seating chart, schedule, partner with the Law, tickets)
7. Headline news ticker
8. Champions Indoor Football standings
9. **Secondary links banner (slot 5)**
10. News cards
11. **Title sponsor banner (slot 1)**, then the footer

## Slot details

### 1. Title sponsor banner (every page)

- Image: `/images/league/ads/title-sponsor.jpg` (1170 × 120)
- Alt text: "Western Plains Medical Complex — archived title sponsor"
- Linked to `/partners.html`
- CSS: `.sponsor-title` (white background, image full width; hidden when
  printing)
- Code: the start of the string returned by `footer()`:

```python
'<div class="container sponsor-title"><a href="/partners.html">'+img('/images/league/ads/title-sponsor.jpg','Western Plains Medical Complex — archived title sponsor')+'</a></div><footer>...
```

### 2. Hero sidebar tile (home)

- Image: `/images/league/partners/freddys.jpg` (520 × 400)
- Alt text: "Freddy’s — archived team partner"
- Linked to `/partners.html`
- CSS: `.freddys`. It is 145px wide on desktop, 115px at 901–1200px and 110px
  at 601–900px. At 600px and below it sits in its own 100px column beside the
  headlines.
- Code: in `hero`, the last element inside `<div class="hero-news">`, after the
  League News panel:

```python
'<a class="freddys" href="/partners.html">'+img('/images/league/partners/freddys.jpg',"Freddy’s — archived team partner")+'</a>'
```

### 3. Full-width banner (home)

- Image: `/images/league/ads/lia-gg-mcdonalds-banner.jpg` (1170 × 200)
- Alt text: "Archived G&G and McDonald’s sponsor artwork — historical offers"
- Linked to `/partners.html`
- CSS: `.banner`
- Code: in `homebody`, right after `hero`:

```python
'<a class="banner" href="/partners.html">'+img('/images/league/ads/lia-gg-mcdonalds-banner.jpg','Archived G&G and McDonald’s sponsor artwork — historical offers')+'</a>'
```

### 4. Sponsor carousel (home)

- Images, one shown at a time, each 1170 × 90:
  - `/images/league/ads/ab1.jpg`: AB Creative
  - `/images/league/ads/cargill.jpg`: Cargill
  - `/images/league/ads/united-wireless.jpg`: United Wireless Arena
- Each slide linked to `/partners.html`
- Has a "2017 partners" label and ‹ › buttons in the bottom-right corner. The
  label hides at 600px and below. The buttons are driven by `manualCarousel`
  in `site.js` through `data-sponsor`.
- CSS: `.sponsor-rotation`
- Code: the `sponsor` variable, used in `homebody` right after slot 3:

```python
sponsor='<section class="sponsor-rotation" aria-label="Historical sponsor banners">'+''.join('<a href="/partners.html"'+(' hidden' if i else '')+'>'+img('/images/league/ads/'+file,label)+'</a>' for i,(file,label) in enumerate([('ab1.jpg','AB Creative'),('cargill.jpg','Cargill'),('united-wireless.jpg','United Wireless Arena')]))+'<div><span>2017 partners</span><button data-sponsor="-1" aria-label="Previous sponsor">‹</button><button data-sponsor="1" aria-label="Next sponsor">›</button></div></section>'
```

### 5. Secondary links banner (home)

- Image: `/images/league/ads/secondary-links-banner.jpg` (1170 × 160)
- A single graphic with clickable areas recreated from the original image map
  `m_secondarylinksbanner`. The top strip is a row of links: Watch Law Games,
  Buy Tickets Online, Single and Season Tickets, Schedule, Partners, Seating
  Chart and United Wireless Arena. Below it are three panels: a Dodge House
  Hotel & Convention Center ad ("Exclusive housing provider of the Dodge City
  Law"), a corporate sponsorship contact box, and a Z98 radio ad ("Listen to
  Law games on…").
- CSS: `.image-map`
- Code: in `homebody`, between the standings section and `cards`:

```python
banner_map('m_secondarylinksbanner','/images/league/ads/secondary-links-banner.jpg')
```

### 6. Partner gallery (`/partners.html`)

- Intro text: "Original sponsor artwork recovered from the 2017 site. Offers,
  contact details, and sponsorships shown in these images are historical."
- Each image appeared as a captioned figure, followed by the Freddy's image
  (shown up to 260px wide). In order:
  1. Western Plains Medical Complex (`title-sponsor.jpg`)
  2. AB Creative (`ab1.jpg`)
  3. Cargill (`cargill.jpg`)
  4. United Wireless Arena (`united-wireless.jpg`)
  5. G&G and McDonald’s (`lia-gg-mcdonalds-banner.jpg`)
  6. The Dodge House and Z98 (`secondary-links-banner.jpg`)
  7. Freddy’s Frozen Custard & Steakburgers (`partners/freddys.jpg`)
- CSS: `.partner-banners`
- Code: the original `layout('/partners.html', ...)` call:

```python
layout('/partners.html','Partners','<p>Original sponsor artwork recovered from the 2017 site. Offers, contact details, and sponsorships shown in these images are historical.</p><div class="partner-banners">'+''.join('<figure>'+img('/images/league/ads/'+file,name)+'<figcaption>'+e(name)+'</figcaption></figure>' for file,name in [('title-sponsor.jpg','Western Plains Medical Complex'),('ab1.jpg','AB Creative'),('cargill.jpg','Cargill'),('united-wireless.jpg','United Wireless Arena'),('lia-gg-mcdonalds-banner.jpg','G&G and McDonald’s'),('secondary-links-banner.jpg','The Dodge House and Z98')])+img('/images/league/partners/freddys.jpg',"Freddy’s Frozen Custard & Steakburgers")+'</div>'+source_note(HOME_SOURCE),source=HOME_SOURCE)
```

## Left in place

These use sponsor-related artwork but are not third-party ad slots, so they
were kept:

- **Top navigation banner** on the home page
  (`/images/league/ads/top-secondary-links.png`). It holds the team's own
  social icons, ticket links and the "Contact the Law for tickets" phone line.
- **"Partner with the Law" quick link** on the home page
  (`/images/league/pix/shop-banner.jpg`). This was the team's own call for
  sponsors, and it links to `/partners.html`.
- **United Wireless Arena banner on `/arena.html`**. It is the same image as
  carousel slide 3, used here as the arena page's header.

Three images in `public/images/league/ads/` were never used by the rebuild:
`baden-vidswap-banner.jpg`, `cif-mobile.jpg` and
`scorestream-horizontal-banner.jpg`.
