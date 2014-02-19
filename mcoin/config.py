# test wallet 1: Z4n9k9PtyaJe2oMi7HCpN97dpX53Ol6kVC2F1ARYaKKvseOs4In

import landerdb

relay = 0
brokers = [{"ip":"192.168.1.121", "port":1217}, {"ip":"192.168.1.122", "port":1217}]
version = "0.0.1"
host = "0.0.0.0"
port = 1217
nodes = landerdb.Connect("nodes.db")
wallet = landerdb.Connect("wallet.db")
db = landerdb.Connect("db.db")
