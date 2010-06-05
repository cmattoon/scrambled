import mimetypes
import optparse
import os
import re
import sys

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from scramble import __version__

class PyPIHandler(BaseHTTPRequestHandler):
    server_version = "scrambled/{version}".format(version=__version__)

    def do_GET(self):
        if self.path.startswith("/simple/"):
            return self.search()
        elif self.path.startswith("/package/"):
            return self.fetch()
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            self.wfile.write("Not Found")

    def search(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        self.wfile.write("searching...")

    def fetch(self):
        m = re.match(r"[\./]*([^/]+)$", self.path[9:])
        if not m:
            self.send_response(406)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("Invalid Request")
            return

        pkg = os.path.join(self.server.pkgdir, m.group(1))
        if not os.path.exists(pkg):
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("Not Found")
            return

        self.send_response(200)
        self.send_header("Content-type", mimetypes.guess_type(pkg)[0] or 'application/octet-stream')
        self.send_header("Content-length", os.path.getsize(pkg))
        self.end_headers()

        self.wfile.write(file(pkg).read())





def run():
    parser = optparse.OptionParser(usage="usage: %prog [options] package_directory",
                                   version="%prog {version}".format(version=__version__))

    parser.add_option("-b", "--bind", dest="bind", default="0.0.0.0", type="str",
                      help="address to bind to (default: %default)")
    parser.add_option("-p", "--port", dest="port", default=8000, type="int",
                      help="port to listen on  (default: %default)")

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    if not os.path.exists(os.path.join(args[0], ".")):
        parser.error("invalid package_dir")

    try:
        mimetypes.add_type('application/zip', 'egg')
        server = HTTPServer((options.bind, options.port), PyPIHandler)
        server.pkgdir = args[0]
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("scrambled shutting down...\n")
        server.socket.close()

