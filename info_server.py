#!/usr/bin/python3

from http.server import SimpleHTTPRequestHandler, HTTPServer
import sys, socket
import threading


port = 80


class ReqHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
            #self.path = '$HOME/weather_info/index.html'
            #self.path = 'weather_info/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def run():
    server_address = ('', port)
    server = HTTPServer(server_address, ReqHandler)

    # get current ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("9.9.9.9", 80))
    ipaddr = s.getsockname()[0]
    s.close()

    def run_httpd():
        server.serve_forever()

    # start server thread
    print(f"[ INFO ] starting server thread", flush=True)
    t = threading.Thread(target=run_httpd, daemon=True)
    t.start()
    print(f"[ INFO ] Server running at {ipaddr}:{port}", flush=True)

    # listen for commands
    for line in sys.stdin:
        if line.strip().lower() == "terminate":
            server.shutdown()
            break
    print("TERMINATED", flush=True)


if __name__ == "__main__":
    run()
