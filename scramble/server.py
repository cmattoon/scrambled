import optparse
import os
import sys

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from scramble import __version__

# HTML templates
HEADER = """<html><head><title>Links for %(package)s</title></head><body><h1>Links for %(package)s</h1>"""
ITEM   = """<a href="%(prefix)s/%(package)s">%(package)s</a><br/>"""
FOOTER = """</body></html>"""

class PyPIHandler(SimpleHTTPRequestHandler):
    server_version = "scrambled/" + __version__

    def do_GET(self):
        if self.path.startswith("/simple/"):
            return self.search(self.path[8:], "../../package")

        elif self.path.startswith("/package/"):
            self.path = self.path[9:]

            if not self.path:
                return self.search(self.path, ".")
            else:
                return SimpleHTTPRequestHandler.do_GET(self)

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            self.wfile.write("Not Found")

    def search(self, name, prefix):
        if name.endswith('/'):
            pkgname  = name[:-1]
            packages = filter(lambda f: f.startswith(pkgname), os.listdir(self.server.pkgdir))
        elif name == '':
            pkgname  = 'All Packages'
            packages = os.listdir(self.server.pkgdir)
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            self.wfile.write("Bad Request")
            return

        if packages:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(HEADER % {'package':pkgname})
            for pkg in packages:
                self.wfile.write(ITEM % {'prefix':prefix, 'package':pkg})
            self.wfile.write(FOOTER)
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            if name:
                self.wfile.write("Not Found (%(package)s does not have any releases)" % {'package': pkgname})
            else:
                self.wfile.write("Not Found")


def run():
    parser = optparse.OptionParser(usage="usage: %prog [options] package_directory",
                                   version="%prog " + __version__)

    parser.add_option("-b", "--bind", dest="bind", default="0.0.0.0", type="str",
                      help="address to bind to (default: %default)")
    parser.add_option("-p", "--port", dest="port", default=8000, type="int",
                      help="port to listen on  (default: %default)")

    opt, arg = parser.parse_args()
    if len(arg) != 1:
        parser.error("incorrect number of arguments")
    if not os.path.exists(os.path.join(arg[0], ".")):
        parser.error("invalid package_dir")

    try:
        sys.stderr.write("starting scrambled... [%s:%s]\n" % (opt.bind, opt.port,))
        server = HTTPServer((opt.bind, opt.port), PyPIHandler)
        server.pkgdir = arg[0]

        os.chdir(server.pkgdir)
        server.serve_forever()

    except KeyboardInterrupt:
        sys.stderr.write("scrambled shutting down...\n")
        server.socket.close()

