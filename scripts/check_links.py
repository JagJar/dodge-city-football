#!/usr/bin/env python3
"""Check generated pages and route coverage without making network requests."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote
from html_utils import Tree
ROOT=Path(__file__).resolve().parents[1]; PUBLIC=ROOT/'public'
routes=json.loads((ROOT/'research/legacy-routes.json').read_text()); aliases=routes['aliases']
# Third-party resources loaded on purpose; any other external resource is an error.
ALLOWED_EXTERNAL={'//acscdn.com/script/aclib.js'}
errors=[]; documents={}; resources=0; links=0
for file in PUBLIC.rglob('*.html'):
    path='/'+str(file.relative_to(PUBLIC)); tree=Tree(file.read_text()).root
    ids=[n.attrs['id'] for n in tree.walk() if 'id' in n.attrs]
    if len(ids)!=len(set(ids)): errors.append(f'{path}: duplicate element IDs')
    documents[path]=(tree,set(ids))

def check(value, source, resource=False):
    global links,resources
    if not value: return
    url=urlsplit(value)
    if url.scheme or url.netloc:
        if resource and value not in ALLOWED_EXTERNAL:errors.append(f'{source}: external resource {value}')
        return
    if not value.startswith(('/', '#')):errors.append(f'{source}: relative URL {value}');return
    path=unquote(url.path) or source
    target=urlsplit(aliases.get(path,path))
    path=target.path
    filename='/index.html' if path=='/' else path
    if not (PUBLIC/filename.lstrip('/')).is_file():errors.append(f'{source}: missing {value}')
    fragment=target.fragment or url.fragment
    if fragment and filename in documents and unquote(fragment) not in documents[filename][1]:errors.append(f'{source}: missing anchor {value}')
    if resource:resources+=1
    else:links+=1
for path,(tree,ids) in documents.items():
    for n in tree.walk():
        if n.tag in {'img','script','iframe','source'}:check(n.attrs.get('src',''),path,True)
        if n.tag=='img' and 'alt' not in n.attrs:errors.append(f'{path}: image without alt text')
        if n.tag=='a':check(n.attrs.get('href',''),path)
        if n.tag=='link' and n.attrs.get('rel') in {'stylesheet','icon','preload'}:check(n.attrs.get('href',''),path,True)
        if n.tag in {'iframe','form'}:errors.append(f'{path}: live embed/form')
for file in (PUBLIC/'assets').rglob('*.css'):
    for value in re.findall(r'url\([\'"]?([^\)\'\"]+)',file.read_text()):check(value,str(file.relative_to(PUBLIC)),True)
# The original home linked to these sections; each needs a local page or explicit alias.
original=Tree((ROOT/'research/baseline-20170602.html').read_text()).root
original_paths=set()
for a in original.walk('a'):
    href=a.attrs.get('href','');u=urlsplit(href)
    if href.startswith('/') and not href.startswith('//') and u.path and u.path not in {'/index.php'}:
        original_paths.add(u.path)
for path in original_paths:
    target=aliases.get(path,path);filename='index.html' if target=='/' else target.lstrip('/')
    if not (PUBLIC/filename).is_file():errors.append(f'Original homepage: no restoration route for {path}')
if errors:
    print('\n'.join(sorted(set(errors))));sys.exit(1)
print(f'PASS: {len(documents)} HTML files, {links} internal links, {resources} resources; {len(original_paths)} original homepage paths covered.')
