#!/usr/bin/env python

"""
Serve all the mp3 and ogg files in the local directory and produce a playlist
as index.

Usage::

    $ playlistd.py
    Serving on http://0.0.0.0:6666/

On a remote machine:

    $ mplayer -playlist http://192.168.1.10:6666/
"""

import os
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import urllib
import cgi
import sys
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def is_music(filename):
    filename = filename.lower()
    for ext in ["mp3", "ogg", "flac", "mpa"]:
        if filename.endswith("."+ext):
            return True
    return False


class RequestHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        """Helper to produce a directory listing in the form of an m3u playlist

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        header = [
            "#EXTM3U",
            "#",
            "# generated by playlistd.py",
            "# https://github.com/tamentis/scripts/blob/master/playlistd.py",
            "#",
            "",
        ]
        f.write("\n".join(header))
        for name in [fn for fn in list if is_music(fn)]:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write("{}\n".format(linkname))
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "application/x-mpegurl; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f


server_address = ('', 6666)
RequestHandler.protocol_version = "HTTP/1.0"
httpd = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()
