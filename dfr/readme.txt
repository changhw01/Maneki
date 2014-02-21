# installation mac 10.9
$ sudo port install opencv +python27

# run p2p node (not fully functioning yet)
$ python node.py

# face recog training (should be integrated into node.py)
$ python train.py

# open chrome at http://localhost:8080/

# TO-DO:
# - [easy] limit snapshot frequency
# - [need more p2p knowledge] p2p sync dataset and remove duplicates
# - [architecture problem] label management
# - [architecture problem] integrate face recog into node