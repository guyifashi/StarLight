import http from 'node:http';
import worker from './cloudflare_worker.js';

const PORT = 3000;

const server = http.createServer(async (req, res) => {
  try {
    const url = `http://${req.headers.host || `localhost:${PORT}`}${req.url}`;
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const body = ['GET', 'HEAD'].includes(req.method) ? undefined : Buffer.concat(chunks);

    const webReq = new Request(url, {
      method: req.method,
      headers: req.headers,
      body: body && body.length > 0 ? body : undefined,
    });

    const webRes = await worker.fetch(webReq, {}, {});

    res.statusCode = webRes.status;
    webRes.headers.forEach((val, key) => res.setHeader(key, val));
    const resBuf = Buffer.from(await webRes.arrayBuffer());
    res.end(resBuf);
  } catch (err) {
    res.statusCode = 500;
    res.end(`Internal Server Error: ${err.message}`);
  }
});

server.listen(PORT, () => {
  console.log(`🚀 本地预览已就绪: http://localhost:${PORT}`);
});
