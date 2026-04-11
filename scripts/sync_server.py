#!/usr/bin/env python3
"""
EN Learning - 极简打分同步服务
只做一件事：接收网页的打分数据，写入 progress.json
端口：7755
"""
import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS = os.path.join(BASE_DIR, "progress.json")

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass  # 静默运行

    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200); self.cors(); self.end_headers()

    def do_GET(self):
        if self.path == "/ping":
            self.send_response(200); self.cors(); self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path != "/save":
            self.send_response(404); self.end_headers(); return
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n))
            with open(PROGRESS, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.send_response(200); self.cors(); self.end_headers()
            self.wfile.write(b"ok")
        except Exception as e:
            self.send_response(500); self.end_headers()
            self.wfile.write(str(e).encode())

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 7755), H)
    print("EN Learning 打分服务已启动 (port 7755)")
    server.serve_forever()
