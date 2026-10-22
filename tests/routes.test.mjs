import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import worker from '../worker.js';
import { aliases, articleIds, playerIds, canonicalPaths } from '../routes.js';
import { assets } from '../scripts/asset-server.mjs';
const fetch = (path, method='GET') => worker.fetch(new Request(new URL(path, 'https://dodgecityfootball.com'), {method}), {ASSETS:assets});

test('all canonical pages and legacy aliases resolve without redirect loops', async () => {
  for (const path of canonicalPaths) {
    const response = await fetch(path);
    assert.equal(response.status, 200, path);
    if (path !== '/feed.xml') assert.match(await response.text(), /Historical archive/, path);
  }
  for (const [path, target] of Object.entries(aliases)) {
    const response = await fetch(path);
    assert.equal(response.status, 301, path);
    assert.equal(new URL(response.headers.get('location')).pathname, target.split('#')[0], path);
    assert.equal((await fetch(target)).status, 200, `${path} → ${target}`);
  }
});

test('index.php, www and Joomla links reach specific content in one redirect', async () => {
  const root = await fetch('https://www.dodgecityfootball.com/index.php?utm_source=archive');
  assert.equal(root.headers.get('location'), 'https://dodgecityfootball.com/?utm_source=archive');
  for (const [id, path] of Object.entries(articleIds)) {
    const response = await fetch(`/index.php?option=com_content&view=article&id=${id}:old-title&Itemid=40&utm_source=old`);
    assert.equal(response.headers.get('location'), `https://dodgecityfootball.com${path}?utm_source=old`);
    assert.equal((await fetch('/index.php'+path)).headers.get('location'), 'https://dodgecityfootball.com'+path);
  }
  const [id, path] = Object.entries(playerIds)[0];
  assert.equal((await fetch(`/?option=com_sobipro&sid=${id}&Itemid=101`)).headers.get('location'), 'https://dodgecityfootball.com'+path);
  assert.equal((await fetch('/index.php?format=feed&type=rss')).headers.get('location'), 'https://dodgecityfootball.com/feed.xml');
});

test('unknown content and spam stay real 404s, including nested and controller URLs', async () => {
  for (const path of ['/not-a-page','/team/unknown.html','/01_dodge_manual.pdf','/index.php?option=com_content&view=article&id=999999','/index.php?option=com_unknown','/index.php/unknown.html']) {
    const response=await fetch(path);
    assert.equal(response.status,404,path);
    const html=await response.text();
    assert.match(html,/page not found/); assert.match(html,/href="\/"/); assert.match(html,/name="robots" content="noindex/);
  }
});

test('HEAD keeps status and headers with an empty body; submissions are closed', async () => {
  for (const path of ['/','/team/roster.html','/missing','/index.php','/index.php?option=missing']) {
    const head=await fetch(path,'HEAD'), get=await fetch(path);
    assert.equal(head.status,get.status,path); assert.equal(await head.text(),'');
    assert.equal(head.headers.get('location'),get.headers.get('location'));
  }
  const post=await fetch('/','POST'); assert.equal(post.status,405); assert.equal(post.headers.get('allow'),'GET, HEAD');
});

test('asset binding is configured and local images, CSS, JS and fonts are served', async () => {
  const config=JSON.parse((await readFile(new URL('../wrangler.jsonc', import.meta.url),'utf8')).replace(/^\s*\/\/.*$/gm,''));
  assert.equal(config.assets.binding,'ASSETS'); assert.equal(config.assets.html_handling,'none');
  assert.ok(config.assets.run_worker_first.includes('/*'));
  for (const path of ['/images/dodge-city-law-logo.png','/assets/css/style.css','/assets/js/site.js','/favicon.ico']) {
    const response=await fetch(path); assert.equal(response.status,200,path); assert.ok((await response.arrayBuffer()).byteLength>0);
  }
  const home=await (await fetch('/')).text(); assert.match(home,/class="hero"/); assert.doesNotMatch(home,/http-equiv="refresh"/);
});
