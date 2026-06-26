#!/usr/bin/env python3
"""Simple HTTP server that adds ngrok-skip-browser-warning header to all responses."""
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socket

class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("ngrok-skip-browser-warning", "true")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # silence logs

def get_local_ip():
    try:
        # Create a socket and connect to an external address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

if __name__ == "__main__":
    port = 8000
    server = HTTPServer(("0.0.0.0", port), NoCacheHandler)
    local_ip = get_local_ip()
    print("==================================================")
    print(f"Game Server started successfully!")
    print(f"Local Access:   http://localhost:{port}")
    if local_ip:
        print(f"Network Access: http://{local_ip}:{port}")
        print("Use the Network Access URL to open the game on other")
        print("devices connected to the same Wi-Fi network.")
    print("==================================================")
    server.serve_forever()
