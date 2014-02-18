import sys
from tinyfacerec.util import read_cvimages
from tinyfacerec.model import EigenfacesModel
from tinyfacerec.model import FisherfacesModel
from tinyfacerec.distance import CosineDistance
import pickle
import time
import hashlib

def sha256_for_file(path, block_size=256*128, hr=False):
    sha256 = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            sha256.update(chunk)
            if sha256.hexdigest().startswith("00"):
                print sha256.hexdigest()
    if hr:
        return sha256.hexdigest()
    return sha256.digest()

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "USAGE: train.py data/raw/"
        sys.exit()

    ## read images
    t = time.time()
    [X,y,z] = read_cvimages(sys.argv[1])

    ## save to matrix data
    #scipy.io.savemat("x4.mat", mdict={'X': X, 'y':y, 'z':z}, oned_as='row')
    with open('data//processed//mat.data', 'wb') as output:
        pickle.dump({'X': X, 'y':y, 'z':z}, output, pickle.HIGHEST_PROTOCOL)

    with open('data//processed//mat.data', 'rb') as input:
        matdata = pickle.load(input)
    print matdata['z']

    # compute model as pow
    #print "doing PoW compute models..."
    t = time.time()
    model_eigen = EigenfacesModel(matdata['X'][1:], matdata['y'][1:], dist_metric = CosineDistance())
    model_fisher = FisherfacesModel(matdata['X'][1:], matdata['y'][1:], dist_metric = CosineDistance())

    with open('data//model//data.bin', 'wb') as output:
        pickle.dump(dict(eigen=model_eigen, fisher=model_fisher), output, pickle.HIGHEST_PROTOCOL)

    print "model computed and saved. took %.3f ms"%((time.time()-t)*1000.)

    # hashing model
    t = time.time()
    print "model hashing: %s took %.3f ms"%(sha256_for_file('data//model//data.bin',hr=True),(time.time()-t)*1000.)

    with open('data//model//data.bin', 'rb') as input:
        mmodel = pickle.load(input)

    # get a prediction for the first observation
    # predict based on global model/local model/O(N)-based model
    print "predicting..."

    ## test w. cv2
    #import cv2
    #test_img = cv2.imread("test.png")
    #test_img  = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)

    t = time.time()
    output_name, min_dist =  mmodel["eigen"].predict(matdata['X'][0],-.5)
    print "predicted (eigen)= %s (%f). took %.3f ms"%(matdata["z"][output_name], min_dist,(time.time()-t)*1000.)
    t = time.time()
    output_name, min_dist =  mmodel["fisher"].predict(matdata['X'][0],-.5)
    print "predicted (fisher)= %s (%f). took %.3f ms"%(matdata["z"][output_name], min_dist,(time.time()-t)*1000.)

    # reward: acccurate labels (more good labels) should get more reward
