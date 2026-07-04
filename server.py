import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class DualStackServer(ThreadingHTTPServer):
    def server_bind(self):
        super().server_bind()

if __name__ == '__main__':
    port = 8000
    server_address = ('', port)
    handler = SimpleHTTPRequestHandler
    
    print(f"Starting multithreaded server on port {port}...")
    httpd = DualStackServer(server_address, handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
