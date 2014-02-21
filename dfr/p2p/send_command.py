import socket
import json
import config
import random

def send(cmd, out=False, god=False):
    
    if god:
        nodes = config.seeds # connect to seed nodes
    else:
        nodes = config.nodes.find("nodes", {"relay":1}) # connect to relay nodes (every node should be relaying lo)
        #print nodes
        random.shuffle(nodes) # randomize nodes (need to remove connecting self)
    if not nodes:
        nodes = config.seeds
    for x in nodes:
        s = socket.socket()
        try:
            s.connect((x['ip'], x['port']))
        except:
            s.close()
            continue
        else:
            s.send(json.dumps({"cmd":"get_version"}))
            data = s.recv(1024)
            print data # get node's version
            if data == config.version:
                s.close()
                s = socket.socket()
                try:
                    s.connect((x['ip'], x['port']))
                except:
                    s.close()
                    continue
                else:
                    s.send(json.dumps(cmd))
                    out = ""
                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        out = out + data
                    s.close()
                    if out:
                        return out
            else:
                s.close()

