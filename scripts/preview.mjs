import http from 'node:http';
import worker from '../worker.js';
import { assets } from './asset-server.mjs';
const port = Number(process.env.PORT || 8000);
const server = http.createServer(async (req, res) => {
  try {
    const request = new Request(`http://${req.headers.host}${req.url}`, {method:req.method});
    const response = await worker.fetch(request, {ASSETS:assets});
    res.writeHead(response.status, Object.fromEntries(response.headers));
    res.end(Buffer.from(await response.arrayBuffer()));
  } catch (error) {
    console.error(error.message); res.writeHead(500); res.end('Preview error');
  }
});
server.listen(port, '127.0.0.1', () => console.log(`Restoration preview: http://127.0.0.1:${port}`));
