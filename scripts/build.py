#!/usr/bin/env python3
"""Build the static restoration from preserved captures. No network required."""
import json
import re
import shutil
from pathlib import Path
from html import escape as e
from urllib.parse import urlsplit
from html_utils import Tree, content_blocks

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
RESEARCH = ROOT / 'research'
BASE = 'https://dodgecityfootball.com'
HOME_SOURCE = 'https://web.archive.org/web/20170602095555/http://dodgecityfootball.com/'
ROSTER_SOURCE = 'https://web.archive.org/web/20170712052125/http://www.dodgecityfootball.com/team/roster.html'
assets = json.loads((RESEARCH / 'recovered-assets.json').read_text())
home = Tree((RESEARCH / 'baseline-20170602.html').read_text()).root
pages = {}
aliases = {'/index.html': '/', '/index.php': '/', '/roster.html': '/team/roster.html',
           '/schedules.html': '/schedule.html', '/news/headline-news.html': '/news.html',
           '/news-hm.html': '/news.html', '/contac.html': '/contact.html',
           '/tickets/single-season-ticket-pricing.html': '/tickets/ticket-pricing.html',
           '/tickets/tickets-pricing.html': '/tickets/ticket-pricing.html',
           '/appearance-request.html': '/fans/appearance-request.html',
           '/images/league/flyers/dodge-seating-chart.pdf': '/arena/seating-chart.html#original-pdf',
           '/itc-honorary-family-of-the-night.html': '/fans/itc-honorary-family-of-the-night.html'}

def wayback(path, stamp='20170712'):
    return f'https://web.archive.org/web/{stamp}/http://www.dodgecityfootball.com{path}'

def recovered(path):
    matches = [r for r in assets if r['mime'] == 'text/html' and urlsplit(r['original_url']).path == path]
    return sorted(matches, key=lambda r: r['capture'])[0] if matches else None

def original_url(value):
    m = re.search(r'/web/\d+[a-z_]*/(https?://.*)', value)
    return m[1] if m else value

def local_link(value):
    value = original_url(value)
    if value.startswith(('mailto:', 'tel:')): return '/contact.html'
    if value.startswith('#'): return value
    u = urlsplit(value)
    if not u.netloc or u.hostname in ('dodgecityfootball.com','www.dodgecityfootball.com'):
        path = u.path or '/'
        return aliases.get(path, path) + ('#' + u.fragment if u.fragment else '')
    return 'https://web.archive.org/web/20170602/' + value

def img(path, alt='', cls='', eager=False):
    if not (PUBLIC / path.lstrip('/')).exists(): return ''
    from PIL import Image
    try:
        with Image.open(PUBLIC / path.lstrip('/')) as im: w,h=im.size
    except Exception: w,h=0,0
    dimensions = f' width="{w}" height="{h}"' if w else ''
    return f'<img src="{e(path)}" alt="{e(alt)}" class="{cls}"{dimensions} loading="{"eager" if eager else "lazy"}" decoding="async">'

def source_note(url, label='Original capture', detail=''):
    return f'<p class="source-note">{e(detail)} <a href="{e(url)}" rel="noopener">{e(label)} ↗</a></p>'

def sanitize(n):
    if isinstance(n,str): return e(n)
    classes=n.attrs.get('class','')
    if n.tag in {'script','style','iframe','form','input','button','noscript'} or any(x in classes for x in ('fastsocial','al_comments','al_social','al_btn','fb_','twitter','pinterest')) or n.attrs.get('id','') in {'fb-root'}:
        return ''
    inside=''.join(sanitize(c) for c in n.children)
    if n.tag=='img':
        u=urlsplit(original_url(n.attrs.get('src','')))
        return img(u.path, n.attrs.get('alt','Archived team image'))
    if n.tag=='a':
        href=local_link(n.attrs.get('href',''))
        identifier=n.attrs.get('id') or n.attrs.get('name')
        anchor=f' id="{e(identifier)}"' if identifier else ''
        if not n.attrs.get('href'): return f'<span{anchor}>{inside}</span>'
        if href.startswith(('javascript:', 'data:')): return inside
        return f'<a href="{e(href)}"{anchor}>{inside}</a>'
    if n.tag not in {'p','h2','h3','h4','ul','ol','li','strong','b','em','i','br','table','thead','tbody','tr','th','td','div','span','blockquote','hr'}: return inside
    attrs=''
    if n.attrs.get('id'): attrs+=f' id="{e(n.attrs["id"])}"'
    for key in ('colspan','rowspan'):
        if n.attrs.get(key,'').isdigit(): attrs+=f' {key}="{n.attrs[key]}"'
    if n.tag=='table': attrs+=' class="historical-table"'
    return f'<{n.tag}{attrs}>' + ('' if n.tag in {'br','hr'} else inside+f'</{n.tag}>')

def recovered_body(path):
    record=recovered(path)
    if not record: return None
    root=Tree((ROOT/record['local_path']).read_text()).root
    content=next(root.walk(cls='entry-content'),None)
    return (sanitize(content), record['replay_url']) if content else None

news_specs=[
 (731,'2017-04-24','law-set-for-big-season','Law set for big season','law-set-for-big-season'),
 (730,'2016-12-13','dodge-city-law-sign-4-new-receivers','Dodge City Law sign 4 new Receivers','receivers'),
 (729,'2016-11-16','law-sign-qb-s-rudy-johnson-winston-salem-state-teejay-gordon-college-of-idaho',"Law sign QB’s Rudy Johnson (Winston-Salem State) & Teejay Gordon (College of Idaho)",'qbs'),
 (728,'2016-11-04','dodge-city-law-add-more-nfl-talent','Dodge City Law Add More NFL Talent','nfl-talent'),
 (727,'2016-10-27','law-sign-former-chiefs-tank-tyler-and-donnell-alexander','Law sign Former Chiefs Tank Tyler and Donnell Alexander','tank-tyler'),
 (726,'2016-10-05','the-dodge-city-law-announce-coaching-addition-for-the-2017-season','The Dodge City Law Announce Coaching Addition for the 2017 Season','coaching'),
]
thumbs=list((PUBLIC/'cache/mod_bt_contentslider').glob('*.jpg'))
def thumb(kind): return '/'+str(next(p for p in thumbs if kind in p.name).relative_to(PUBLIC))
news=[]
for ident,date,slug,title,anchor in news_specs:
    path=f'/news-hm/{ident}-{slug}.html'
    rec=recovered(path)
    news.append(dict(id=ident,date=date,title=title,path=path,anchor=anchor,source=rec['replay_url'] if rec else HOME_SOURCE,
                     image=thumb('rjohnson' if ident==729 else 'various' if ident==728 else 'no-image')))

team_sections=[('Team Roster','/team/roster.html'),('Staff & Coaches','/team/staff-coaches.html'),('Gunpowder Girls','/team/gunpowder-girls.html'),('Jr. Gunpowder Girls','/team/junior-gunpowder-girls.html'),('Ball Dolls','/team/ball-dolls.html'),('Meet Marshall','/team/meet-marshall.html')]
fan_sections=[('Photo Gallery','/gallery.html'),('Watch & Listen','/watch-games.html'),('H.S. MVP Award','/fans/mvp-award.html'),('ITC Honorary Family','/fans/itc-honorary-family-of-the-night.html'),('Appearance Request','/fans/appearance-request.html'),('Social Archive','/fans/social.html')]
nav_items=[('The LAW','/',[]),('Team','/team.html',team_sections),('Schedule','/schedule.html',[]),('Tickets','/tickets.html',[('Buy Tickets Online','/tickets/buy-tickets-online.html'),('Ticket Pricing','/tickets/ticket-pricing.html'),('Season Ticket Form','/tickets/season-ticket-form.html')]),('News','/news.html',[('Headline News','/news.html'),('RSS Feed','/news/subscribe-to-rss-feeds.html')]),('Arena','/arena.html',[('United Wireless Arena','/arena.html'),('Seating Chart','/arena/seating-chart.html')]),('Partners','/partners.html',[]),('Stats','/stats.html',[]),('Fans','/fans.html',fan_sections),('Contact','/contact.html',[]),('The CIF','/league.html',[])]

def links(items): return '<ul>'+''.join(f'<li><a href="{p}">{e(t)}</a></li>' for t,p in items)+'</ul>'

def navigation(path):
    out='<nav class="main-nav" aria-label="Main navigation"><button class="menu-toggle" aria-expanded="false" aria-controls="nav-list">Menu <span aria-hidden="true">☰</span></button><ul id="nav-list">'
    for index,(title,p,children) in enumerate(nav_items):
        current=' aria-current="page"' if path==p else ''
        out+=f'<li><a href="{p}"{current}>{e(title)}</a>'
        if children: out+=f'<button class="submenu-toggle" aria-expanded="false" aria-controls="submenu-{index}" aria-label="Show {e(title)} menu">▾</button><ul class="submenu" id="submenu-{index}">'+''.join(f'<li><a href="{q}">{e(t)}</a></li>' for t,q in children)+'</ul>'
        out+='</li>'
    return out+'</ul></nav>'

def footer():
    teamlogos=[('venom','Amarillo Venom'),('bucks','Bismarck Bucks'),('centex','Centex Cavalry'),('dclaw','Dodge City Law'),('edge','Bloomington Edge'),('gladiators','Duke City Gladiators'),('mesquite','Dallas Marshals'),('kansas-city-phantoms-2','Kansas City Phantoms'),('omaha-beef','Omaha Beef'),('liberty','Salina Liberty'),('scbandits','Sioux City Bandits'),('texas-revs','Texas Revolution'),('west-michigan-ironmen','West Michigan Ironmen'),('wichita-force','Wichita Force')]
    return '<footer><div class="footer-grid container"><div><h2>The LAW</h2>'+links(team_sections[:2]+[('2017 Schedule','/schedule.html'),('Headline News','/news.html'),('Seating Chart','/arena/seating-chart.html')])+'</div><div><h2>Fans & archive</h2>'+links([('Ticket History','/tickets.html'),('Partners','/partners.html'),('Photo Gallery','/gallery.html'),('About This Archive','/about-this-archive.html'),('Archive Index','/archive-index.html')])+'</div><div><h2>Champions Indoor Football · 2017</h2><ul class="league-links">'+''.join(f'<li><a href="/league.html">{img("/images/stories/"+logo+".png","")}{name}</a></li>' for logo,name in teamlogos)+'</ul></div><div><h2>Dodge City Law</h2><p>United Wireless Arena<br>4100 W Comanche St.<br>Dodge City, KS 67801</p><p class="small">Historical address · 2014–2017<br>Phone (archived): (620) 371-7390</p></div></div><div class="copyright"><div class="container">Historical archive. Team ceased operations in 2017. Original site: Trey Braid. <a href="/about-this-archive.html">Sources & restoration notes</a><a class="to-top" href="#top">Back to top ↑</a></div></div></footer>'

def layout(path,title,body,description='',full=False,partial=False,source=None):
    canonical=BASE+path
    body=body.replace('<div class="table-scroll">','<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable historical table">')
    metadata=f'<meta name="description" content="{e(description or title+" — Dodge City Law historical archive, 2014–2017.")}">'
    if partial: metadata+='<meta name="robots" content="noindex,follow">'
    document=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">{metadata}<title>{e(title)} | Dodge City Law Archive</title><link rel="canonical" href="{canonical}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="Dodge City Law · Historical football archive, 2014–2017"><meta property="og:image" content="{BASE}/images/dodge-city-law-logo.png"><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/css/style.css"><link rel="alternate" type="application/rss+xml" title="Dodge City Law archival news" href="/feed.xml"><script src="/assets/js/site.js" defer></script><script id="aclib" type="text/javascript" src="//acscdn.com/script/aclib.js"></script></head><body id="top"><a class="skip-link" href="#main">Skip to content</a><div class="archive-bar"><div class="container"><strong>Historical archive · 2014–2017</strong><span>The team is no longer active. <a href="/about-this-archive.html">About this restoration</a></span></div></div><header class="site-header"><div class="container header-inner"><a class="brand" href="/" aria-label="Dodge City Law home">{img('/images/dodge-city-law-logo.png','Dodge City Law football logo',eager=True)}</a>{navigation(path)}</div></header><div class="masthead" aria-hidden="true"></div><main id="main" class="container {'home' if full else 'interior'}">{body if full else '<div class="page-heading"><p>DODGE CITY LAW · HISTORICAL ARCHIVE</p><h1>'+e(title)+'</h1></div><div class="page-content">'+body+'</div>'}</main>{footer()}<script type="text/javascript">aclib.runAutoTag({{zoneId: 'nvly1c3coi'}});</script></body></html>'''
    destination=PUBLIC/('index.html' if path=='/' else path.lstrip('/'))
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(document)
    pages[path]={'title':title,'status':'partial' if partial else 'restored','source':source,'file':str(destination.relative_to(ROOT))}

def news_links(): return '<ul class="headline-list">'+''.join(f'<li><a href="{n["path"]}">{e(n["title"])}</a></li>' for n in news)+'</ul>'

def banner_map(name,imagepath):
    node=next(n for n in home.walk('map') if n.attrs.get('name')==name)
    out='<div class="image-map">'+img(imagepath,'Original 2017 navigation and sponsor artwork',eager=True)
    for area in node.walk('area'):
        values=[int(v) for v in area.attrs['coords'].split(',')];xs=values[0::2];ys=values[1::2]
        target=local_link(area.attrs['href']);label=area.attrs.get('alt','Archive link')
        if 'feedburner' in target: target='/news.html'
        elif 'facebook' in target or 'twitter' in target: target='/fans/social.html'
        elif 'securenetsystems' in target: target='/watch-games.html'
        elif 'unitedwirelessarena' in target: target='/arena.html'
        elif target=='#': target='/partners.html'
        elif target.endswith('.pdf') and not (PUBLIC/target.lstrip('/')).exists(): target='/tickets/season-ticket-form.html'
        if min(ys)>=96 and name=='m_topsecondarylinks':target='/tickets.html';label='Archived ticket information — no tickets are on sale'
        out+=f'<a href="{e(target)}" aria-label="{e(label)}" title="{e(label)}" style="left:{min(xs)/11.7:.3f}%;top:{min(ys)/1.6:.3f}%;width:{(max(xs)-min(xs))/11.7:.3f}%;height:{(max(ys)-min(ys))/1.6:.3f}%"></a>'
    return out+'</div>'

# All 24 signed-listing records are in the preserved capture, without JavaScript.
roster=[]
tree=Tree((RESEARCH/'roster.html').read_text()).root
for n in tree.walk(cls='vc_title'):
    a=next(n.walk('a'),None)
    if not a:continue
    roster.append({'name':a.text(),'path':a.attrs['href'],'fields':[x.text() for x in n.walk(cls='vc_roster')]})
assert len(roster)==24

# Preserve the actual mid-season standings, rather than mixing them with final results.
standings=[]
for index,table in enumerate(home.walk('table')):
    for tr in table.walk('tr'):
        a=next((a for a in tr.walk('a') if '/component/gridiron/team/' in a.attrs.get('href','')),None)
        if not a:continue
        td=list(tr.walk('td'))
        name=next((x.text() for x in td[0].walk('a') if x.text()),'')
        standings.append({'name':name,'path':a.attrs['href'],'values':[x.text() for x in td[1:]],'division':'North' if len(standings)<7 else 'South'})
assert len(standings)==14

def standings_table(division):
    rows=[s for s in standings if s['division']==division]
    return f'<div class="table-scroll"><table class="standings"><caption>{division} Division</caption><thead><tr><th scope="col">Team</th>'+''.join(f'<th scope="col">{x}</th>' for x in ['W','L','Pct.','GP','PF','PA'])+'</tr></thead><tbody>'+''.join('<tr'+(' class="law-row"' if s['name']=='Dodge' else '')+'><th scope="row"><a href="'+s['path']+'">'+e(s['name'])+'</a></th>'+''.join('<td>'+e(v)+'</td>' for v in s['values'])+'</tr>' for s in rows)+'</tbody></table></div>'

# Six original headline URLs, with four recovered releases, one excerpt, one attributed summary.
for n in news:
    rec=recovered(n['path']); body='';partial=False
    if rec:
        root=Tree((ROOT/rec['local_path']).read_text()).root
        author=next(root.walk(cls='by-author'),None)
        byline=author.text() if author else 'Written by Dodge City Law'
        blocks=content_blocks((ROOT/rec['local_path']).read_text())
        body=''.join(f'<{tag}>{e(text)}</{tag}>' for tag,text in blocks if text!=n['title'])
    elif n['id']==731:
        byline='Kiowa County Signal · Timothy Everson'
        body='<p class="notice">Editorial summary of the archived newspaper article. The byline and original source are preserved.</p><p>At 6–1, the Law were aiming for a franchise-best season and a home playoff game under head coach Sean Ponder. The offense ranked fifth in the CIF in points per game and third in yards per game. Rookie quarterback Rudy Johnson had thrown 25 touchdown passes against six interceptions and led the team with 232 rushing yards. Ponder credited the offensive line’s protection as a foundation of the offense.</p>'
        n['source']=wayback(n['path'])
    else:
        byline='Dodge City Law · archived homepage excerpt';partial=True
        body='<p>Former Kansas City Chief players, Demarcus Lamon “Tank” Tyler and Donnell Alexander have…</p><p class="notice">The headline and opening excerpt survive on the homepage. The complete article was not recovered from either archived hostname during this restoration.</p>'
    n['excerpt']=re.sub('<[^>]+>',' ',body)[:180].strip()
    layout(n['path'],n['title'],f'<article class="article"><p class="article-meta"><time datetime="{n["date"]}">{n["date"]}</time> · {e(byline)}</p>{body}{source_note(n["source"],detail="Historical text reflects the source at the time of publication.")}<p><a href="/news.html">← All headline news</a></p></article>',partial=partial,source=n['source'])

cards='<div class="news-grid">'+''.join(f'<article id="{n["anchor"]}"><a href="{n["path"]}">{img(n["image"],"Archived football photograph")}<h2>{e(n["title"])}</h2></a><time datetime="{n["date"]}">{n["date"]}</time><p><a href="{n["path"]}">Read article →</a></p></article>' for n in reversed(news))+'</div>'
layout('/news.html','Headline News',cards+source_note(HOME_SOURCE),source=HOME_SOURCE)

league_feed=next(home.walk(cls='srfrList'))
league_headlines='<ul class="headline-list">'+''.join(f'<li><a href="{e(local_link(a.attrs["href"]))}">{e(a.text())} ↗</a></li>' for a in list(league_feed.walk('a'))[:6])+'</ul>'
hero=banner_map('m_topsecondarylinks','/images/league/ads/top-secondary-links.png')+'<h1 class="sr-only">The Dodge City Law — 2017 website restoration</h1><section class="hero"><div class="hero-photo">'+img('/images/league/pix/fp-spacer.jpg','Dodge City Law players on the field in the original homepage photograph',eager=True)+'</div><div class="hero-news"><div class="tab-buttons" role="tablist" aria-label="Archived headlines"><button id="team-tab" role="tab" aria-selected="true" aria-controls="team-panel" tabindex="0">Team News</button><button id="league-tab" role="tab" aria-selected="false" aria-controls="league-panel" tabindex="-1">League News</button></div><div id="team-panel" role="tabpanel" aria-labelledby="team-tab">'+news_links()+'</div><div id="league-panel" role="tabpanel" aria-labelledby="league-tab" hidden>'+league_headlines+'<p class="small">Archived June 2, 2017. Links open Wayback.</p></div></div></section>'
quick='<nav class="quick-links" aria-label="Team shortcuts">'+''.join(f'<a href="{path}">{img("/images/league/pix/"+asset,label)}</a>' for asset,path,label in [('arena-seating-chart.jpg','/arena/seating-chart.html','Arena seating chart'),('schedule-banner.jpg','/schedule.html','Schedule'),('shop-banner.jpg','/partners.html','Partner with the Law — historical sponsors'),('tickets-banner.jpg','/tickets/ticket-pricing.html','Ticket pricing — historical only')])+'</nav>'
ticker='<section class="ticker" aria-label="Headline news"><strong>Headline News</strong><div aria-live="polite">'+''.join(f'<a href="{n["path"]}"'+(' hidden' if i else '')+f'>{e(n["title"])}</a>' for i,n in enumerate(news))+'</div><button data-ticker="-1" aria-label="Previous headline">‹</button><button data-ticker="1" aria-label="Next headline">›</button></section>'
# Historical sponsor ads were removed pending new ones; research/ad-placements.md records each slot.
homebody=hero+'<div class="season-strip"><strong>2017 season archive</strong><a href="/schedule.html">Schedule & recorded results →</a></div>'+quick+ticker+'<section class="standings-section"><h2>Champions Indoor Football</h2><p>Standings as displayed June 2, 2017 · historical snapshot</p><div class="standings-grid">'+standings_table('North')+standings_table('South')+'</div></section>'+cards
layout('/','The Official Website of the Dodge City Law — Archived',homebody,full=True,source=HOME_SOURCE)

roster_table='<div class="roster-tools"><label for="roster-search">Find a player</label><input id="roster-search" type="search" placeholder="Name, position, or college" autocomplete="off"><p id="roster-count" role="status">24 archived player entries</p></div><div class="table-scroll"><table id="roster-table"><caption>Signed listings preserved in the July 12, 2017 capture</caption><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in ['Player','No.','Position','Height','Weight','School','Experience','Status','Signed'])+'</tr></thead><tbody>'
for r in roster:
    roster_table+='<tr><th scope="row"><a href="'+r['path']+'">'+e(r['name'])+'</a></th>'+''.join('<td>'+e(v)+'</td>' for v in r['fields'])+'</tr>'
    labels=['Number','Position','Height','Weight (lb)','School','Experience','Status','Signed']
    body='<p>Player information transcribed from the archived team roster.</p><dl class="player-details">'+''.join('<div><dt>'+label+'</dt><dd>'+e(value)+'</dd></div>' for label,value in zip(labels,r['fields']))+'</dl><p class="small">This profile reconstructs the surviving roster entry; an individual biography has not been recovered.</p>'+source_note(ROSTER_SOURCE)+'<p><a href="/team/roster.html">← Full team roster</a></p>'
    layout(r['path'],r['name'],body,source=ROSTER_SOURCE)
roster_table+='</tbody></table></div><p id="roster-empty" hidden>No matching players. Try another name or position.</p><p class="notice">All 24 entries in the surviving capture are included. These are signed listings, not a verified game-day active roster. Duplicate jersey numbers and historical spellings are preserved.</p>'+source_note(ROSTER_SOURCE)
layout('/team/roster.html','Team Roster',roster_table,source=ROSTER_SOURCE)
layout('/team.html','The Team','<p>The Dodge City Law played professional indoor football at United Wireless Arena. Explore the original team sections.</p>'+links(team_sections)+source_note(HOME_SOURCE),source=HOME_SOURCE)

# Transcribe the recorded schedule from its preserved source, not from a new database.
schedule_tree=Tree((RESEARCH/'schedule-2017.html').read_text()).root
# The original schedule is an editorial HTML table; retain its first content table.
entry=next(schedule_tree.walk(cls='entry-content'),None)
schedule_table=next(entry.walk('table'),None) if entry else None
if schedule_table is None:
    schedule_table=next((t for t in schedule_tree.walk('table') if 'Tingley' in t.text()),None)
assert schedule_table is not None, 'Schedule source table not found'
for tr in schedule_table.walk('tr'):
    score_link=next((a for a in tr.walk('a') if '/schedule/boxscore/' in a.attrs.get('href','')),None)
    if not score_link: continue
    fields=[td.text() for td in tr.walk('td')]
    labels=['Game date','Opponent','Location','Time as published','Recorded result']
    gamebody='<dl class="player-details">'+''.join('<div><dt>'+label+'</dt><dd>'+e(value)+'</dd></div>' for label,value in zip(labels,fields))+'</dl><p class="notice">Result recovered from the team schedule. Quarter-by-quarter scoring and individual game statistics have not been recovered.</p><p><a href="/schedule.html">← Full 2017 schedule</a></p>'+source_note(wayback('/schedule.html'))
    layout(score_link.attrs['href'],fields[1].split(' / ')[0]+' · Game Result',gamebody,partial=True,source='research/schedule-2017.html (exact response timestamp not retained)')
layout('/schedule.html','2017 Schedule & Results','<p>Recorded game results from the surviving team schedule. The listed regular-season scores total 9–3, followed by a playoff game. This is the site’s game-results record; it is not a reconstruction of disciplinary adjustments to league standings.</p><div class="table-scroll">'+sanitize(schedule_table)+'</div><p class="notice">This schedule includes June 10 results and therefore represents a later state than the June 2 homepage. The original retrieval did not retain its exact response timestamp; that provenance gap is recorded.</p>'+source_note(wayback('/schedule.html'),label='Browse archived schedule captures'),source='research/schedule-2017.html (exact response timestamp not retained)')

layout('/league.html','Champions Indoor Football · 2017','<p>North and South Division standings preserved on the June 2, 2017 homepage. These are mid-season figures, not the final standings.</p><div class="standings-grid">'+standings_table('North')+standings_table('South')+'</div>'+source_note(HOME_SOURCE),source=HOME_SOURCE)
for s in standings:
    body=f'<p>{e(s["division"])} Division · June 2, 2017 snapshot</p><dl class="player-details">'+''.join('<div><dt>'+label+'</dt><dd>'+e(v)+'</dd></div>' for label,v in zip(['Wins','Losses','Percentage','Games played','Points for','Points against'],s['values']))+'</dl><p>The original team-detail URL now preserves the standings entry recovered from the homepage.</p>'+source_note(HOME_SOURCE)+'<p><a href="/league.html">All 2017 teams →</a></p>'
    layout(s['path'],s['name']+' · Archived Standings',body,source=HOME_SOURCE)

layout('/partners.html','Partners','<p>Partner information is being updated.</p>',source=HOME_SOURCE)
layout('/arena.html','United Wireless Arena','<p>The Law’s home arena was United Wireless Arena, 4100 W Comanche St., Dodge City, Kansas 67801.</p>'+img('/images/league/ads/united-wireless.jpg','United Wireless Arena — original banner')+'<p><a class="button" href="/arena/seating-chart.html">View the archived seating chart →</a></p>'+source_note(HOME_SOURCE),source=HOME_SOURCE)
ticket_notice='<p class="notice"><strong>Historical information only.</strong> The team ceased operations in 2017. Ticket sales, registration, and appearance requests are closed. Archived telephone numbers and offers are not current.</p>'
layout('/tickets.html','Tickets · Historical',ticket_notice+links([('Archived Ticket Pricing','/tickets/ticket-pricing.html'),('Seating Chart','/arena/seating-chart.html'),('Season Ticket Form','/tickets/season-ticket-form.html')])+source_note(HOME_SOURCE),source=HOME_SOURCE)
layout('/tickets/buy-tickets-online.html','Buy Tickets Online · Archived',ticket_notice+'<p>This was the original online ticket entry point. The archive preserves its place in the navigation.</p><p><a href="/tickets/ticket-pricing.html">See historical ticket information</a></p>'+source_note(HOME_SOURCE),source=HOME_SOURCE)

# Prefer recovered editorial content; otherwise provide a specific, honest archive record.
fallbacks={
 '/team/staff-coaches.html':('Staff & Coaches','<h2>Sean Ponder</h2><p>Head coach in the 2017 season.</p><h2>Heron O’Neal</h2><p>Announced as assistant head coach and director of player personnel for 2017.</p><p><a href="'+news[-1]['path']+'">Read the recovered coaching announcement</a></p>'),
 '/team/gunpowder-girls.html':('Gunpowder Girls','<p>The original team navigation included the Gunpowder Girls dance team. The complete page content has not yet been recovered.</p>'),
 '/team/junior-gunpowder-girls.html':('Jr. Gunpowder Girls','<p>The original site linked to Jr. Gunpowder Girls registration. Registration is closed; the original form has not been recovered.</p>'),
 '/team/ball-dolls.html':('Ball Dolls','<p>Ball Dolls was a team section linked from the original navigation. Its complete page content has not yet been recovered.</p>'),
 '/team/meet-marshall.html':('Meet Marshall','<p>Marshall was featured in the original mascot section. The page text and mascot image have not yet been recovered.</p>'),
 '/arena/seating-chart.html':('Arena Seating Chart',img('/images/league/pix/arena-seating-chart.jpg','Original arena seating-chart thumbnail')+'<p>The homepage seating graphic is preserved above. A larger chart has not yet been recovered.</p>'),
 '/tickets/ticket-pricing.html':('Ticket Pricing · Historical',img('/images/league/pix/tickets-banner.jpg','Original season and game-day ticket pricing graphic')+'<p>The original pricing graphic is preserved. Prices are historical; amounts that are not clearly legible have not been retyped.</p>'),
 '/contact.html':('Contact · Historical','<p>Dodge City Law<br>United Wireless Arena<br>4100 W Comanche St.<br>Dodge City, KS 67801</p><p>Archived phone: (620) 371-7390</p><p>This is a historical contact record. The archive does not receive requests for the former team.</p>'),
 '/fans/mvp-award.html':('H.S. MVP Award','<p>The H.S. MVP Award was linked in the original Fans menu. Its program details have not yet been recovered.</p>'),
 '/fans/itc-honorary-family-of-the-night.html':('ITC Honorary Family of the Night','<p>The original site featured an ITC Honorary Family program. Its full page has not yet been recovered.</p>'),
 '/fans/appearance-request.html':('Appearance Request · Historical','<p>The original site accepted appearance requests. This archive preserves the page location; it does not accept submissions.</p>'),
}
for path,(title,fallback) in fallbacks.items():
    recovered_content=recovered_body(path)
    body,url=recovered_content if recovered_content else (fallback,HOME_SOURCE)
    partial=not bool(recovered_content) and path not in ['/team/staff-coaches.html','/contact.html']
    if path.startswith('/tickets/') or 'request' in path or 'junior' in path:body=ticket_notice+body
    if path=='/arena/seating-chart.html':body+='<div id="original-pdf"><p class="notice">The original PDF download has not been recovered. The full-size chart image is preserved above.</p><p><a href="/images/league/flyers/dodge-seating-chart.jpg">Open the recovered chart image</a></p></div>'
    if path=='/tickets/ticket-pricing.html' and recovered_content:body+='<p class="small">The March 16, 2017 capture uses the same pricing artwork for both sections, with “2015” in the original image filename. That source behavior is preserved here.</p>'
    if partial:body+='<p class="notice">Partial restoration. The page’s existence is documented in the original navigation; missing content has not been invented.</p>'
    layout(path,title,'<div class="archived-content">'+body+'</div>'+source_note(url),partial=partial,source=url)

pdf='/images/league/pdfs/DodgeCitySeasonTicketForm.pdf'
if (PUBLIC/pdf.lstrip('/')).exists():
    formbody=f'<p><a href="{pdf}">Download the original season ticket form (PDF)</a></p>'
else:
    formbody='<p>The original site linked a season-ticket PDF. The file has not yet been recovered; no replacement form has been fabricated.</p>'
    aliases[pdf]='/tickets/season-ticket-form.html'
layout('/tickets/season-ticket-form.html','Season Ticket Form · Historical',ticket_notice+formbody+source_note(HOME_SOURCE),partial=not (PUBLIC/pdf.lstrip('/')).exists(),source=HOME_SOURCE)
layout('/fans.html','Fans',links(fan_sections)+source_note(HOME_SOURCE),source=HOME_SOURCE)
layout('/fans/social.html','Social Archive','<p>The original site linked to the Dodge City Law accounts below. These links open historical Wayback views.</p>'+links([('Facebook archive','https://web.archive.org/web/2017/https://www.facebook.com/DodgeCityLaw'),('Twitter archive','https://web.archive.org/web/2017/http://www.twitter.com/dodgecitylaw')])+source_note(HOME_SOURCE),source=HOME_SOURCE)
layout('/watch-games.html','Watch & Listen · Historical','<p>The original fan menu linked to CIF games on Eversport and radio coverage on Z98 (KSKZ). Live streams are not available through this archive.</p>'+links([('Archived Eversport listing','https://web.archive.org/web/2017/http://eversport.tv/indoor-football/cif'),('Archived Z98 player','https://web.archive.org/web/2017/http://streamdb5web.securenetsystems.net/v5/KSKZ')])+source_note(HOME_SOURCE),source=HOME_SOURCE)
layout('/stats.html','Statistics Archive','<p>The original navigation linked to the league’s 2015 and 2016 statistics. The external tables are not mirrored here; these links open their archived locations.</p>'+links([('2016 CIF statistics','https://web.archive.org/web/2017/http://stats.gocif.net/2016stats/confstat.htm'),('2015 CIF statistics','https://web.archive.org/web/2017/http://stats.gocif.net/2015stats/confstat.htm'),('2017 standings snapshot','/league.html'),('2017 game results','/schedule.html')])+source_note(HOME_SOURCE),source=HOME_SOURCE)
layout('/transactions.html','Transactions Archive','<p>The original footer linked to a transactions page. The transaction log has not been recovered. The signed dates in the surviving team roster remain available.</p><p><a href="/team/roster.html">View signed player listings →</a></p>'+source_note(HOME_SOURCE),partial=True,source=HOME_SOURCE)
gallery='<p>A selection of photographs recovered from the original site. This collection does not reproduce the unrecovered original gallery.</p><div class="gallery">'+''.join('<figure>'+img(p,alt)+'<figcaption>'+alt+'</figcaption></figure>' for p,alt in [('/images/league/pix/fp-spacer.jpg','Original homepage football photograph'),('/images/league/mobile-slides/catch.jpg','Original mobile artwork'),(thumb('various'),'Players pictured in the NFL talent announcement'),(thumb('rjohnson'),'Original quarterback article thumbnail')])+'</div>'+source_note(HOME_SOURCE)
layout('/gallery.html','Recovered Photographs',gallery,source=HOME_SOURCE)

# Explicit source dates and recovery status for readers and future maintainers.
source_rows=''.join(f'<tr><td>{e(r["original_url"].split(".com")[-1])}</td><td>{r["capture"][:4]}-{r["capture"][4:6]}-{r["capture"][6:8]}</td><td><a href="{e(r["replay_url"])}">Wayback capture ↗</a></td></tr>' for r in assets if r['local_path'].startswith('public/images/') or r['mime']=='text/html')
about='<p>This is an unofficial historical restoration of the Dodge City Law’s website. The team played from 2014 through 2017. This archive is not affiliated with the former team, ownership, league, or sponsors.</p><h2>Restoration reference</h2><p>The desktop layout follows the June 2, 2017 homepage: a 1170-pixel layout, Titillium Web typography, overlapping team logo, yellow navigation, and photographic panels. Nearby 2017 captures supply missing assets and article text. Mobile layouts have been adapted for readability and keyboard access.</p><h2>What the dates mean</h2><p>The homepage standings are the June 2 snapshot. The 24-player roster is preserved in the July 12 capture. News dates are publication dates taken from the original headline list; capture dates can be later. The schedule contains later June results and is labeled separately. Where the earlier rebuild did not preserve an exact response timestamp, we say so.</p><h2>Recovered and incomplete material</h2><p>Four team announcements are restored from complete captures; the former-Chiefs announcement has a surviving excerpt. The Kiowa County Signal article is presented as an attributed summary. Player detail pages reconstruct the captured roster fields, not unverified biographies. Pages with missing text are marked partial.</p><h2>Historical services</h2><p>Ticket offers, telephone numbers, registrations, and requests belong to the historical record. This site accepts no purchases or submissions. Old social widgets and score services have been replaced with local content or labeled archive links.</p><h2>Source inventory</h2><p>Only pre-2018 captures are included. Known later parked-domain material is excluded. Images and fonts are served locally; visiting an explicit source link opens the Internet Archive.</p><div class="table-scroll"><table><thead><tr><th>Original resource</th><th>Actual capture date</th><th>Source</th></tr></thead><tbody>'+source_rows+'</tbody></table></div><p>Original site design credit: Trey Braid. Original photographs, logos, and text remain attributed to their respective creators.</p>'
layout('/about-this-archive.html','About This Archive',about,source=HOME_SOURCE)
layout('/news/subscribe-to-rss-feeds.html','Archived News Feed','<p>This feed contains the six recovered historical headlines. It is an archive feed, not current team news.</p><p><a href="/feed.xml">Subscribe to the archival RSS feed</a></p>',source=HOME_SOURCE)
feed='<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Dodge City Law — Historical News</title><link>'+BASE+'/news.html</link><description>Archived 2016–2017 headlines. The team is no longer active.</description>'+''.join('<item><title>'+e(n['title'])+'</title><link>'+BASE+n['path']+'</link><guid>'+BASE+n['path']+'</guid><description>Historical article published '+n['date']+'.</description></item>' for n in news)+'</channel></rss>'
(PUBLIC/'feed.xml').write_text(feed)
layout('/archive-index.html','Archive Index','<p>Browse restored pages and documented gaps in the historical record.</p><div class="table-scroll"><table><thead><tr><th>Page</th><th>Recovery status</th></tr></thead><tbody>'+''.join(f'<tr><td><a href="{p}">{e(v["title"])}</a></td><td>{v["status"]}</td></tr>' for p,v in sorted(pages.items()))+'</tbody></table></div>',source=HOME_SOURCE)
layout('/404.html','Fourth and long — page not found','<p>This address does not match a recovered page. Some old links belong to material that was never captured or to the domain’s later unrelated use.</p>'+links([('Home','/'),('Archive Index','/archive-index.html'),('Team Roster','/team/roster.html'),('2017 Schedule','/schedule.html'),('News','/news.html')]),partial=True)

for path in list(pages):
    if path.endswith('.html') and path not in ('/index.html','/404.html'):
        aliases.setdefault(path[:-5],path)
        aliases.setdefault(path[:-5]+'/',path)
for path,target in list(aliases.items()):
    if path.endswith('.html'):
        aliases.setdefault(path[:-5],target)
        aliases.setdefault(path[:-5]+'/',target)
# Keep direct-file previews and old relative URLs readable as well as edge aliases.
for path,target in aliases.items():
    if path.endswith('.html') and path != '/index.html' and path not in pages:
        filename=PUBLIC/path.lstrip('/');filename.parent.mkdir(parents=True,exist_ok=True)
        filename.write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url={target}"><title>Archived page moved</title><p><a href="{target}">Continue to the archived page</a></p></html>')
routes={'aliases':aliases,'articleIds':{str(n['id']):n['path'] for n in news},'playerIds':{re.search(r'/(\d+)-',r['path'])[1]:r['path'] for r in roster},'canonicalPaths':list(pages)+['/feed.xml']}
(ROOT/'routes.js').write_text('// Generated by scripts/build.py. Do not edit by hand.\n'+''.join('export const '+k+' = '+json.dumps(v,indent=2)+';\n' for k,v in routes.items()))
(RESEARCH/'restoration-pages.json').write_text(json.dumps(pages,indent=2)+'\n')
(RESEARCH/'legacy-routes.json').write_text(json.dumps(routes,indent=2)+'\n')
(PUBLIC/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+p+'</loc></url>' for p,v in pages.items() if v['status']=='restored')+'</urlset>')
(PUBLIC/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
shutil.copyfile(PUBLIC/'templates/shaper_sportson/favicon.ico',PUBLIC/'favicon.ico')
print(f'Built {len(pages)} pages, {len(aliases)} legacy aliases, {len(roster)} player entries.')
