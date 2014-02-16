import config
import json

def get_difficulty(obj, data):
    diff = config.db.find("coins", "all")
    if not diff:
        diff = []
    diff = len(diff)/50500 + 5
    if diff < 5:
        diff = 5
    obj.send(json.dumps({"difficulty":diff}))

