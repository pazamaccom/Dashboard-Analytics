#!/usr/bin/env python3
"""Independent, read-only P | ANALYTICS portal. Python standard library only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
from threading import Lock
import time
from urllib.request import build_opener, ProxyHandler

ROOT = Path(__file__).resolve().parent
DASHBOARDS = json.loads((ROOT / 'dashboards.json').read_text())
CACHE = {'expires': 0, 'states': []}
LOCK = Lock()
OPENER = build_opener(ProxyHandler({}))


def probe(item):
    try:
        with OPENER.open(item['url'], timeout=2) as response:
            online = 200 <= response.status < 400
    except Exception:
        online = False
    return {'id': item['id'], 'url': item['url'], 'online': online}


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'")
        super().end_headers()

    def do_GET(self):
        if self.path.split('?')[0] == '/api/status':
            with LOCK:
                if time.monotonic() >= CACHE['expires']:
                    with ThreadPoolExecutor(max_workers=7) as pool:
                        CACHE['states'] = list(pool.map(probe, DASHBOARDS))
                    CACHE['expires'] = time.monotonic() + 15
                data = json.dumps(CACHE['states']).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            super().do_GET()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='100.127.41.102')
    parser.add_argument('--port', type=int, default=8087)
    args = parser.parse_args()
    if args.host in ('0.0.0.0', '::'):
        parser.error('Use a specific private or loopback address.')
    server = ThreadingHTTPServer((args.host, args.port), partial(Handler, directory=str(ROOT / 'public')))
    print(f'P | ANALYTICS listening on http://{args.host}:{args.port}', flush=True)
    server.serve_forever()
