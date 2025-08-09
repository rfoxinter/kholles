from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from mimetypes import guess_type
from os import _exit, chdir
from os.path import exists, join
from socket import gethostbyname, gethostname
from threading import Thread
from urllib.parse import unquote

parser = ArgumentParser()
parser.add_argument('--path', type=str, required=False)

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
            _exit(0)
        else:
            super().do_GET()


def main_httpserver(path: str = ".") -> None:
    ip = gethostbyname(gethostname())
    print('IP : ' + ip)
    try:
        chdir(path)
    except TypeError:
        print('Using default folder')
        path = "."
    print('\nServer running from ' + path + "\n")
    server = Thread(target=ThreadingHTTPServer(('', 80), CORSRequestHandler).serve_forever)
    server.daemon = True
    server.start()
    while server.is_alive():
        if input('\nStop server with "S"\n').upper() == 'S':
            exit()
