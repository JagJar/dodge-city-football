import { aliases, articleIds, playerIds, canonicalPaths } from './routes.js';

// Resolve only documented historic URLs. Unknown content keeps its 404 status.
const routingKeys = ['option', 'view', 'id', 'sid', 'Itemid', 'task', 'layout', 'format', 'type', 'tmpl'];
const hasOwn = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
const knownPaths = new Set(canonicalPaths);

export function resolveLegacy(url) {
  let path = url.pathname;
  const params = url.searchParams;
  const controller = path === '/index.php' || path === '/' || path === '/index.html';
  if (controller && routingKeys.some(key => params.has(key))) {
    let destination;
    const id = (params.get('id') || '').split(':')[0];
    const sid = (params.get('sid') || '').split(':')[0];
    if (params.get('option') === 'com_content' && params.get('view') === 'article' && hasOwn(articleIds, id)) {
      destination = articleIds[id];
    } else if (params.get('option') === 'com_sobipro' && hasOwn(playerIds, sid)) {
      destination = playerIds[sid];
    } else if (params.get('format') === 'feed' && !params.has('option') && ['rss', 'atom', null].includes(params.get('type'))) {
      destination = '/feed.xml';
    } else {
      return { missing: true };
    }
    routingKeys.forEach(key => params.delete(key));
    return { destination };
  }
  // Joomla also exposed SEF paths with an index.php prefix.
  if (path.startsWith('/index.php/')) {
    const candidate = path.slice('/index.php'.length);
    if (knownPaths.has(candidate)) return { destination: candidate };
    if (hasOwn(aliases, candidate)) return { destination: aliases[candidate] };
  }
  if (hasOwn(aliases, path)) return { destination: aliases[path] };
  return {};
}

export default {
  async fetch(request, env) {
    if (!['GET', 'HEAD'].includes(request.method)) {
      return new Response('This historical archive is read-only.', {status: 405, headers: {'Allow': 'GET, HEAD'}});
    }
    const url = new URL(request.url);
    const route = resolveLegacy(url);
    const canonicalHost = url.hostname === 'www.dodgecityfootball.com';
    if (canonicalHost || route.destination) {
      if (canonicalHost) url.hostname = 'dodgecityfootball.com';
      if (route.destination) {
        const target = new URL(route.destination, url);
        url.pathname = target.pathname;
        url.hash = target.hash;
      }
      return new Response(null, {status: 301, headers: {'Location': url.toString(), 'Cache-Control': 'public, max-age=3600'}});
    }
    if (route.missing) {
      const page = await env.ASSETS.fetch(new Request(new URL('/404.html', url), request));
      const headers = new Headers(page.headers);
      headers.set('X-Robots-Tag', 'noindex');
      return new Response(request.method === 'HEAD' ? null : page.body, {status: 404, headers});
    }
    // html_handling: none preserves historic .html URLs; serve the root explicitly.
    if (url.pathname === '/') {
      url.pathname = '/index.html';
      return env.ASSETS.fetch(new Request(url, request));
    }
    return env.ASSETS.fetch(request);
  },
};
