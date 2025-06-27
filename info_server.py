#!/usr/bin/python3

from http.server import SimpleHTTPRequestHandler, HTTPServer


class ReqHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
            #self.path = '$HOME/weather_info/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)


def run():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ReqHandler)

    print(f"[!] Server running at ...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
