# installation mac 10.9
$ sudo port install opencv +python27

# run stand-alone node (not p2p yet)
$ python node.py

# train dataset (should be integrated into node.py)
$ python train.py

# use zcoin as p2p network (soon to be integrated)
$ mcoin/python zcoin.py

# open chrome at http://localhost:8080/

# TO-DO:
# - [easy] limit snapshot frequency
# - [need more p2p knowledge] p2p sync dataset and remove duplicates
# - [architecture problem] label management
# - [architecture problem] integrate face recog into node