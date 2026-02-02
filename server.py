import http.server
import socketserver
import json
import os
import subprocess
import time

# 配置区域
PORT = 8000
DATA_FILE = "etf_data.json"
GIT_REMOTE = "origin"
GIT_BRANCH = "main"

def git_pull():
    """启动时拉取最新数据"""
    if not os.path.exists(".git"):
        print("⚠️ 未检测到 Git 仓库，跳过同步功能")
        return
    
    print("🔄 正在从 GitHub 拉取最新数据...")
    try:
        # 尝试拉取，如果失败也不要崩溃
        subprocess.call(["git", "pull", GIT_REMOTE, GIT_BRANCH], shell=True)
        print("✅ 拉取完成")
    except Exception as e:
        print(f"❌ 拉取失败: {e} (可能是离线状态)")

def git_push():
    """保存后自动推送"""
    if not os.path.exists(".git"):
        return

    print("☁️ 正在同步至 GitHub...")
    try:
        # 1. Add
        subprocess.call(["git", "add", DATA_FILE], shell=True)
        # 2. Commit
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        subprocess.call(["git", "commit", "-m", f"Auto-sync: {timestamp}"], shell=True)
        # 3. Push
        subprocess.call(["git", "push", GIT_REMOTE, GIT_BRANCH], shell=True)
        print("✅ 同步成功")
    except Exception as e:
        print(f"❌ 同步失败: {e}")

class ETFRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        self.wfile.write(f.read().encode('utf-8'))
                except:
                    self.wfile.write(b'{}')
            else:
                self.wfile.write(b'{}')
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/save':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # 1. 写入本地
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    f.write(post_data.decode('utf-8'))
                
                # 2. 触发 Git 同步 (这是关键新增)
                git_push()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            except Exception as e:
                print("错误:", e)
                self.send_error(500, str(e))
            return

if __name__ == "__main__":
    print("------------------------------------------")
    print("🚀 ETF云同步版启动 (Python 3.6)")
    print(f"🔗 地址: http://localhost:{PORT}")
    
    # 启动时先拉取一次
    git_pull()
    
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), ETFRequestHandler) as httpd:
            httpd.serve_forever()
    except OSError:
        print(f"端口 {PORT} 被占用")
    except KeyboardInterrupt:
        print("\n已停止")