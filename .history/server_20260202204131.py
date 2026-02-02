import http.server
import socketserver
import json
import os

# 设置端口和数据文件名
PORT = 8000
DATA_FILE = "etf_data.json"

class ETFRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 接口：获取数据
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if os.path.exists(DATA_FILE):
                try:
                    # Python 3.6 必须显式指定编码读取
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.wfile.write(content.encode('utf-8'))
                except Exception as e:
                    print("读取文件出错:", e)
                    self.wfile.write(b'{}')
            else:
                self.wfile.write(b'{}')
            return
        
        # 默认行为：提供静态文件服务（服务同目录下的 index.html）
        return super().do_GET()

    def do_POST(self):
        # 接口：保存数据
        if self.path == '/api/save':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # 将接收到的 JSON 数据写入本地
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    f.write(post_data.decode('utf-8'))

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            except Exception as e:
                print("写入错误:", e)
                self.send_error(500, str(e))
            return

if __name__ == "__main__":
    # 打印启动信息
    print("------------------------------------------")
    print("✅ ETF本地服务启动成功 (Python 3.6 兼容版)")
    print("🔗 浏览器访问地址: http://localhost:8000")
    print("📂 数据将实时保存至: " + os.path.abspath(DATA_FILE))
    print("------------------------------------------")
    print("按 Ctrl+C 停止服务")
    
    # 允许地址重用，防止频繁重启报端口占用错误
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), ETFRequestHandler) as httpd:
            httpd.serve_forever()
    except OSError:
        print("❌ 错误: 端口 8000 已被占用，请检查是否已有程序在运行。")
    except KeyboardInterrupt:
        print("\n🛑 服务已停止。")