#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os
import tornado.websocket
import base64
import urllib2
import time
import sys

tornado.options.define("port", default=8080, help="run on the given port", type=int)

class WSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "ws opened"
        self.dir_name = "%.0f"%(time.time()*1000.0)
        self.userresponse = 0
        self.emotion = ""

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True
    
    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        d = urllib2.unquote(parsed["base64Data"])
        fname = "%.0f"%(time.time()*1000.0)
        if not os.path.exists("data//"+self.dir_name):
            os.makedirs("data//"+self.dir_name)
        
        with open("data//%s//%s.png"%(self.dir_name,fname),"wb") as f:
            f.write(base64.b64decode(d.split(',')[1]))
            print "saved to %s.png"%fname
    
    def on_close(self):
        print "ws closed"


class CapturePageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("face.html")

def main():
    settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True)
    
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", CapturePageHandler),
        (r"/ws",WSocketHandler),

    ],**settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(tornado.options.options.port)
    print "open your chrome at http://localhost:8080"
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
