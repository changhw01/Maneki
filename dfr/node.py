#!/usr/bin/env python

## face server
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
import json

## p2p node
import string
import random
import thread
import socket
import p2p.config
import p2p.get_db
import p2p.get_version
import p2p.get_nodes
import p2p.register
import rsa
import p2p.send_command

class p2pNode:
    def __init__(self):
        self.cmds = {
            
            "get_db":p2p.get_db.get_db,
            "get_nodes":p2p.get_nodes.get_nodes,
            "get_version":p2p.get_version.get_version,
            "register":p2p.register.register,
            "get_nodes_count":p2p.get_nodes.count,
            "p2p":self.runp2p
        }
    def runp2p(self,obj,data):
        obj.send(json.dumps({"p2p":"hello world!"}))
    
    def firstrun(self):
        print "Generating address and public/private keys"
        pub, priv = rsa.newkeys(1024)
        address = "D"+''.join([random.choice(string.uppercase+string.lowercase+string.digits) for x in range(50)])
        print "My DFR wallet address: "+address
        print "Getting nodes from network"
        p2p.get_nodes.send(True)
        check = p2p.config.nodes.find("nodes", "all")
        if not check:
            print "Seed node (aka no other nodes online)"
            p2p.config.nodes.insert("nodes", {"public":str(pub), "address":address, "ip":p2p.config.host, "relay":p2p.config.relay, "port":p2p.config.port})
            p2p.config.nodes.save()
            p2p.config.db.save()
        p2p.config.wallet.insert("data", {"public":str(pub), "address":address, "private":str(priv)})
        p2p.config.wallet.save()
        print "Registering..."
        p2p.register.send()
        print "Getting db..."
        p2p.get_db.send()
        print "Done!"
    
    def relay(self):
        # relay mode
        p2p.get_nodes.send()
        p2p.register.send()
        p2p.get_db.send()
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((p2p.config.host, p2p.config.port))
        sock.listen(5)
        while True:
            obj, conn = sock.accept()
            thread.start_new_thread(self.handle, (obj, conn[0]))
    
    def handle(self, obj, ip):
        data = obj.recv(10240)
        if data:
            try:
                data = json.loads(data)
            except:
                obj.close()
                return
            else:
                if "cmd" in data:
                    if data['cmd'] in self.cmds:
                        data['ip'] = ip
                        print data
                        self.cmds[data['cmd']](obj, data)
                        obj.close()
    
    def normal(self):
        # normal mode
        if not p2p.config.relay:
            p2p.get_db.send()
            p2p.register.send()
        while True:
            #coin_count.send()
            p2p.get_nodes.count_send()
            time.sleep(60)

def run():
    pn = p2pNode()
    check = p2p.config.nodes.find("nodes", "all")
    if not check:
        pn.firstrun()
    if p2p.config.relay:
        thread.start_new_thread(pn.normal, ())
        thread.start_new_thread(pn.relay, ())
        print "DFR started as a relay node."
    else:
        thread.start_new_thread(pn.normal, ())
        print "DFR started as a normal node."


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
        if not os.path.exists("data//raw//"+self.dir_name):
            os.makedirs("data//raw//"+self.dir_name)
        
        with open("data//raw//%s//%s.png"%(self.dir_name,fname),"wb") as f:
            f.write(base64.b64decode(d.split(',')[1]))
            print "saved to %s.png"%fname
    
    def on_close(self):
        print "ws closed"


class CapturePageHandler(tornado.web.RequestHandler):
    def get(self):
        p2p.send_command.send({"cmd":"p2p"})
        self.render("face.html")

def main():
    run()
    settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=False)
    
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
