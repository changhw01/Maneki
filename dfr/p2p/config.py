import landerdb

relay = 1
seeds = [{"ip":"127.0.0.1", "port":1217}]
version = "0.0.1"
host = "127.0.0.1" # for relay mode
port = 1217 # for relay mode
nodes = landerdb.Connect("nodes.db")
wallet = landerdb.Connect("wallet.db")
db = landerdb.Connect("db.db")
