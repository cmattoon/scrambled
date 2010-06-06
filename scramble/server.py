import optparse
import os
import sys

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from scramble import __version__

# HTML templates
HEADER = """<html><head><title>{title}</title></head><body><h1>{title}</h1>"""
ITEM   = """<a href="../../package/{package}">{package}</a><br/>"""
FOOTER = """</body></html>"""

class PyPIHandler(SimpleHTTPRequestHandler):
    server_version = "scrambled/{version}".format(version=__version__)

    def do_GET(self):
        if self.path.startswith("/simple/"):
            return self.search()
        elif self.path.startswith("/package/"):
            self.path = self.path[9:] # snip prefix
            return SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            self.wfile.write("Not Found")

    def search(self):
        if self.path[-1] != '/':
            self.send_response(301)
            self.send_header("Location", self.path + "/")
            self.end_headers()
            return
        else:
            pkgname  = self.path[8:-1]

        packages = filter(lambda f: f.startswith(pkgname), os.listdir(self.server.pkgdir))
        if not packages:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            self.wfile.write("Not Found")
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(HEADER.format(title="Links for " + pkgname))
            for pkg in packages:
                self.wfile.write(ITEM.format(package=pkg))
            self.wfile.write(FOOTER)


def run():
    parser = optparse.OptionParser(usage="usage: %prog [options] package_directory",
                                   version="%prog {version}".format(version=__version__))

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
        sys.stderr.write("starting scrambled... [{0}:{1}]\n".format(opt.bind, opt.port))
        server = HTTPServer((opt.bind, opt.port), PyPIHandler)
        server.pkgdir = arg[0]

        os.chdir(server.pkgdir)
        server.serve_forever()

    except KeyboardInterrupt:
        sys.stderr.write("scrambled shutting down...\n")
        server.socket.close()

