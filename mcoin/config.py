import landerdb

relay = 1
brokers = [{"ip":"192.168.0.1", "port":6565}, {"ip":"127.0.0.1", "port":6565}]
version = "0.0.1"
host = "0.0.0.0"
port = 6565
nodes = landerdb.Connect("nodes.db")
wallet = landerdb.Connect("wallet.db")
db = landerdb.Connect("db.db")
