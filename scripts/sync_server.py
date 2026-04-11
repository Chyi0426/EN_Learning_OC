#!/usr/bin/env python3
"""
EN Learning - 本地同步服务器
接收网页打分数据 → 写入 progress.json → git push 到 GitHub
运行后在 http://localhost:7755 提供服务
"""

import json
import os
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")
PORT = 7755


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(data):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def git_push():
    """后台静默推送到 GitHub"""
    try:
        subprocess.run(["git", "add", "progress.json"],
                       cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "commit", "-m",
                        f"sync: review progress {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                       cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "push"],
                       cwd=BASE_DIR, capture_output=True)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 打分记录已同步到 GitHub")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 同步失败：{e}")


def git_pull():
    """从 GitHub 拉取最新打分记录"""
    try:
        subprocess.run(["git", "pull", "--rebase"],
                       cwd=BASE_DIR, capture_output=True)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 已拉取最新打分记录")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 拉取失败：{e}")


class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # 关闭默认日志，减少终端噪音

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/progress":
            # 返回当前打分记录
            data = load_progress()
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors()
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/pull":
            # 从 GitHub 拉取最新
            git_pull()
            data = load_progress()
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors()
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/ping":
            self.send_response(200)
            self.send_cors()
            self.end_headers()
            self.wfile.write(b"pong")

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/progress":
            # 接收打分数据并合并保存
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                incoming = json.loads(raw.decode("utf-8"))
                progress = load_progress()

                # 合并：新数据覆盖旧数据，但保留旧数据中新数据没有的条目
                for item_id, item_data in incoming.items():
                    progress[item_id] = item_data

                save_progress(progress)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 收到打分数据，共 {len(incoming)} 条，已保存")

                # 后台推送，不阻塞响应
                threading.Thread(target=git_push, daemon=True).start()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode())

            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 处理打分数据出错：{e}")
                self.send_response(500)
                self.send_cors()
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    # 启动时先拉取最新数据
    print(f"EN Learning 同步服务器启动中...")
    git_pull()

    # 监听 0.0.0.0，局域网内所有设备都能访问
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"✅ 服务器运行在 http://0.0.0.0:{PORT}")
    print(f"   本机访问：http://localhost:{PORT}")
    print(f"   局域网访问：http://192.168.100.12:{PORT}")
    print(f"   打分记录文件：{PROGRESS_FILE}")
    print(f"   按 Ctrl+C 停止")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
