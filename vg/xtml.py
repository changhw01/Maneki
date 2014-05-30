
#import sys
import numpy as np
#import matplotlib.pyplot as plt
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import explained_variance_score
from sklearn.metrics import r2_score
import random
#from sklearn.svm import SVR
#from sklearn.externals import joblib
import cPickle
import time
import sys

n_trees = 100
feature_list = ["HR_G","Gender","Age", "BMI", "Height", "Weight", "HR_R", "HR_B"]

## populate current distribution of data
data_file = "dall_new_partial2.csv"
data = np.loadtxt(open(data_file, "rb"), delimiter=" ", skiprows=1)
trainset = np.loadtxt(open(data_file, "rb"), delimiter=" ", skiprows=1, usecols=range(2, 128))
bpset = np.array(np.loadtxt(open(data_file, "rb"), delimiter=" ", skiprows=1, usecols=(0, 1))) * 1.0

## split data
data_train, data_test, bp_train, bp_test = train_test_split(trainset, bpset, test_size=0.1, random_state=int(random.random() * 10))
print "train set shape", data_train.shape
print "test set shape", data_test.shape
print "----"
'''
## random forest
t0 = time.time()
clf_rf = RandomForestRegressor(n_jobs=-1, n_estimators=n_trees)
clf_rf.fit(X=data_train, y=bp_train)
rf_importances = clf_rf.feature_importances_

std = np.std([tree.feature_importances_ for tree in clf_rf.estimators_], axis=0)
indices = np.argsort(rf_importances)[::-1]

# Print the feature ranking
print "Random Forest Feature ranking:"
for f in xrange(12):
    if indices[f] < 8:
        print "%d. %s (%f)" % (f + 1, feature_list[indices[f]],rf_importances[indices[f]])
    else:
        print "%d. feature %d (%f)" % (f + 1, indices[f], rf_importances[indices[f]])

# Plot the feature importances of the forest
#import pylab as pl
#pl.figure()
#pl.title("Feature importances")
#pl.bar(xrange(10), rf_importances[indices][:10], color="r", yerr=std[indices][:10], align="center")
#pl.xticks(xrange(10), indices[:10])
#pl.xlim([-1, 10])
#pl.show()

with open('rf_all.pkl', 'wb') as f:
    cPickle.dump(clf_rf, f)

with open('rf_all.pkl', 'rb') as f:
    clf_rf = cPickle.load(f)

#joblib.dump(clf_rf, 'rf.pkl', compress=9)
#clf_rf = joblib.load('rf.pkl')
abs_err = np.abs(bp_test - clf_rf.predict(data_test))
t1 = time.time() - t0
print "rfr sbp mean: %.2f (sd: %.2f)" % (np.mean(abs_err[:, 0]), np.std(abs_err[:, 0])),
print "rfr dbp mean: %.2f (sd: %.2f)" % (np.mean(abs_err[:, 1]), np.std(abs_err[:, 1])), "took", round(t1, 2), "sec"
scores = cross_val_score(clf_rf, data_train, bp_train)
print "xv scores", scores.mean()
print "explained_variance_score (sbp)", explained_variance_score(bp_test[:, 0], clf_rf.predict(data_test)[:, 0])
print "explained_variance_score (dbp)", explained_variance_score(bp_test[:, 1], clf_rf.predict(data_test)[:, 1])
print "r2_score (sbp)", r2_score(bp_test[:, 0], clf_rf.predict(data_test)[:, 0])
print "r2_score (dbp)", r2_score(bp_test[:, 1], clf_rf.predict(data_test)[:, 1])
print "----"
'''
## extra tree regressor
t0 = time.time()
clf_xt = ExtraTreesRegressor(n_jobs=-1, n_estimators=n_trees)
clf_xt.fit(X=data_train, y=bp_train)
xt_importances = clf_xt.feature_importances_

std = np.std([tree.feature_importances_ for tree in clf_xt.estimators_], axis=0)
indices = np.argsort(xt_importances)[::-1]

# Print the feature ranking
print "Extra Tree Feature ranking:"
for f in xrange(12):
    if indices[f] < 8:
        print "%d. %s (%f)" % (f + 1, feature_list[indices[f]],xt_importances[indices[f]])
    else:
        print "%d. feature %d (%f)" % (f + 1, indices[f], xt_importances[indices[f]])

with open('xt_all.pkl', 'wb') as f:
    cPickle.dump(clf_xt, f)

with open('xt_all.pkl', 'rb') as f:
    clf_xt = cPickle.load(f)
#joblib.dump(clf_xt, 'xt.pkl', compress=9)
#clf_xt = joblib.load('xt.pkl')
abs_err = np.abs(bp_test - clf_xt.predict(data_test))
t1 = time.time() - t0
print "xtr sbp mean: %.2f (sd: %.2f)" % (np.mean(abs_err[:, 0]), np.std(abs_err[:, 0])),
print "xtr dbp mean: %.2f (sd: %.2f)" % (np.mean(abs_err[:, 1]), np.std(abs_err[:, 1])), "took", round(t1, 2), "sec"
scores = cross_val_score(clf_xt, data_train, bp_train)
print "xv scores", scores.mean()
print "explained_variance_score (sbp)", explained_variance_score(bp_test[:, 0], clf_xt.predict(data_test)[:, 0])
print "explained_variance_score (dbp)", explained_variance_score(bp_test[:, 1], clf_xt.predict(data_test)[:, 1])
print "r2_score (sbp)", r2_score(bp_test[:, 0], clf_xt.predict(data_test)[:, 0])
print "r2_score (dbp)", r2_score(bp_test[:, 1], clf_xt.predict(data_test)[:, 1])
print "----"
'''
## svr, need some fine tuning
t0 = time.time()
clf_svr = SVR(C=1.0, epsilon=0.4)
clf_svr.fit(X=data_train, y=bp_train[:, 0])
with open('svr_all.pkl', 'wb') as f:
    cPickle.dump(clf_svr, f)

with open('svr_all.pkl', 'rb') as f:
    clf_svr = cPickle.load(f)
#joblib.dump(clf_svr, 'svr.pkl', compress=9)
#clf_svr = joblib.load('svr.pkl')
abs_err = np.abs(bp_test[:, 0] - clf_svr.predict(data_test))
t1 = time.time() - t0
print "svr sbp mean: %.2f (sd: %.2f)" % (np.mean(abs_err), np.std(abs_err)), "took", round(t1, 2), "sec"
scores = cross_val_score(clf_svr, data_train, bp_train[:, 0])
print "xv scores", scores.mean()
print "explained_variance_score (sbp)", explained_variance_score(bp_test[:, 0], clf_svr.predict(data_test))
print "r2_score (sbp)", r2_score(bp_test[:, 0], clf_svr.predict(data_test))
print "----"
'''