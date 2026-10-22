import { readFile, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = fileURLToPath(new URL('../public/', import.meta.url));
const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.xml':'application/xml; charset=utf-8','.txt':'text/plain; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.gif':'image/gif','.ico':'image/x-icon','.ttf':'font/ttf','.woff':'font/woff','.woff2':'font/woff2','.pdf':'application/pdf'};
// Local adapter for Worker tests/preview; production uses Cloudflare Static Assets.
export const assets = {
  async fetch(request) {
    let filename;
    try { filename = path.resolve(root, '.' + decodeURIComponent(new URL(request.url).pathname)); }
    catch { return new Response('Bad URL', {status:400}); }
    if (!filename.startsWith(root)) return new Response('Not found', {status:404});
    let status = 200;
    try { if (!(await stat(filename)).isFile()) throw new Error('Not a file'); }
    catch { filename = path.join(root, '404.html'); status = 404; }
    const body = request.method === 'HEAD' ? null : await readFile(filename);
    return new Response(body, {status, headers:{'Content-Type':types[path.extname(filename)] || 'application/octet-stream'}});
  }
};
