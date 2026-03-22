from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from mimetypes import guess_type
from os import chdir
from os.path import exists, join
from socket import gethostbyname, gethostname
from threading import Thread
from urllib.parse import unquote

global http_server
global server

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        path = unquote(self.path)
        mimetype = guess_type(path)[0]
        if mimetype is None and path[-1] == '/' or not exists('.' + join('.', path)):
            mimetype = 'text/html'
        elif mimetype is None:
            mimetype = 'text/plain'
        self.send_header('Content-type', mimetype + '; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        return super(CORSRequestHandler, self).end_headers()
    def do_GET(self):
        path = unquote(self.path)
        if path == "/EXIT_SERVER":
            global http_server
            global server
            self.send_response(200)
            self.end_headers()
            http_server.shutdown()
        else:
            super().do_GET()


def main_httpserver(path: str = ".") -> None:
    global http_server
    global server
    ip = gethostbyname(gethostname())
    print('IP : ' + ip)
    try:
        chdir(path)
    except TypeError:
        print('Using default folder.')
        path = "."
    print('\nServer running from “' + path + "”.\n")
    http_server = ThreadingHTTPServer(('', 8000), CORSRequestHandler)
    server = Thread(target=http_server.serve_forever)
    server.daemon = True
    server.start()
    server.join()

if __name__ == "__main__":
    main_httpserver()
