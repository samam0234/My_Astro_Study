import { createServer } from 'node:http';
import { WebSocketServer } from 'ws';
import { getStore } from '../src/lib/store.mjs';
import { authenticate } from '../src/lib/auth.mjs';
import { settings } from '../src/lib/config.mjs';

const store = await getStore(), site = settings().site;
const server = createServer((_req, res) => { res.writeHead(404); res.end(); });
const sockets = new WebSocketServer({ noServer: true, maxPayload: 4096 });
server.on('upgrade', async (request, socket, head) => {
  try {
    if (request.url !== '/events' || request.headers.origin !== new URL(site).origin) throw new Error('origin/path');
    const token = request.headers.cookie?.split(';').map(c => c.trim()).find(c => c.startsWith('desk_session='))?.slice(13);
    const user = await authenticate(store, token); if (!user) throw new Error('auth');
    sockets.handleUpgrade(request, socket, head, ws => {
      ws.send(JSON.stringify({ type: 'ready', nickname: user.nickname }));
      ws.on('message', async () => {
        try {
          if (!(await authenticate(store, token))) { ws.close(1008, 'session expired'); return; }
          ws.send(JSON.stringify({ type: 'pong', at: new Date().toISOString() }));
        } catch { ws.close(1011, 'server error'); }
      });
      const expiry = setTimeout(() => ws.close(1008, 'reauthenticate'), 60000);
      ws.on('close', () => clearTimeout(expiry));
    });
  } catch { socket.write('HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\n'); socket.destroy(); }
});
server.listen(Number(process.env.WS_PORT || 4324), '127.0.0.1');
