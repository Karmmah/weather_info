#!/usr/bin/python3

from http.server import SimpleHTTPRequestHandler, HTTPServer
import sys, socket


port = 8000


class ReqHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
            #self.path = '$HOME/weather_info/index.html'
            #self.path = 'weather_info/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)


def run():
    server_address = ('', port)
    httpd = HTTPServer(server_address, ReqHandler)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("9.9.9.9", 80))
    ipaddr = s.getsockname()[0]
    s.close()

    print(f"[ INFO ] Server running at {ipaddr}:{port}", flush=True)
    #httpd.serve_forever()
    httpd.handle_request()
    for line in sys.stdin:
        print(f"line:{line}", flush=True) #debug
        if line == "terminate\n":
            break
        httpd.handle_request()
    print("[ INFO ] stopped", flush=True)


if __name__ == "__main__":
    run()
