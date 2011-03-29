#!/usr/bin/env python

"""
This is an autonomous mplayer http remote. It does not require any extra
dependencies and rely solely on the default library. Start the server
with the filename you want to play on the target device.

    usage: mplayer-remote.py my-movie.avi

At this point, you may access the web server from the defined port, start
the movie, pause, etc.
"""

import os
import sys
import time
import threading
import subprocess
import BaseHTTPServer

server_address = ('', 9955)
ififo = "/tmp/mplayer_input_fifo"

class MplayerRemoteHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def start(self):
        def run_mplayer():
            try:
                os.remove(ififo)
            except OSError:
                pass
            os.mkfifo(ififo)
            subprocess.call(["mplayer", "-really-quiet", "-fs", "-input",
                 "file=%s" % ififo, filename])
            os.remove(ififo)

        t = threading.Thread(group=None, target=run_mplayer)
        t.start()

    def send_cmd(self, cmd):
        with open(ififo, "w") as fp:
            fp.write(cmd + "\n")
    
    def pause(self):
        self.send_cmd("pause")

    def forward(self):
        self.send_cmd("seek +15")

    def backward(self):
        self.send_cmd("seek -15")

    def stop(self):
        self.send_cmd("quit")

    def shutdown(self):
        os.system("sudo halt")

    def do_GET(self):
        try:
            getattr(self, self.path[1:].split("?")[0])()
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return
        except:
            pass

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

        self.wfile.write("""
            <html>
                <head>
                    <style type="text/css">
                        body {
                            background-color: #222;
                            font-size: 450%%;
                            font-family: Verdana, sans, Arial;
                        }
                        h1 {
                            color: #eee;
                            font-size: 90%%;
                            text-align: center;
                            padding: 24px;
                            margin: 0px;
                            text-shadow: black 0.1em 0.1em 0.2em;
                        }
                        a {
                            color: #eee;
                            background-color: #555;
                            text-decoration: none;
                            font-weight: bold;
                            text-align: center;
                            border-radius: 10px;
                            border: 6px solid #777;
                            display: block;
                            padding: 24px;
                            margin: 32px;
                            text-shadow: black 0.1em 0.1em 0.2em;
                        }
                        a:hover {
                            background-color: white;
                        }
                    </style>
                </head>
                <body>
                    <h1>mplayer</h1>
                    <a href="/start?_t=%(now)s">Start</a>
                    <a href="/pause?_t=%(now)s">Play/Pause</a>
                    <a href="/forward?_t=%(now)s">&rarr; Forward &rarr;</a>
                    <a href="/backward?_t=%(now)s">&larr; Backward &larr;</a>
                    <a href="/stop?_t=%(now)s">Stop</a>
                    <a href="/shutdown?_t=%(now)s">Shutdown</a>
                </body>
            </html>
            """ % dict(now=time.time()))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(-1)

    filename = sys.argv[1]
    httpd = BaseHTTPServer.HTTPServer(server_address, MplayerRemoteHandler)
    print("Serving on port %d..." % server_address[1])
    httpd.serve_forever()

