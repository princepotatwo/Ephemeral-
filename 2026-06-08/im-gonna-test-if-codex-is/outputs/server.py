#!/usr/bin/env python3
"""Simple HTTP server that adds ngrok-skip-browser-warning header to all responses."""
from http.server import SimpleHTTPRequestHandler, HTTPServer

class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("ngrok-skip-browser-warning", "true")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # silence logs

if __name__ == "__main__":
    server = HTTPServer(("", 8000), NoCacheHandler)
    print("Serving on http://localhost:8000")
    server.serve_forever()
