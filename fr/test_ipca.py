import sys
import os
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils import array2d, as_float_array
from sklearn.decomposition import PCA
import cv2
import time
import pickle


class CCIPCA(BaseEstimator, TransformerMixin):

    """Candid covariance-free incremental principal component analysis (CCIPCA)

    Linear dimensionality reduction using an online incremental PCA algorithm.
    CCIPCA computes the principal components incrementally without
    estimating the covariance matrix. This algorithm was designed for high
    dimensional data and converges quickly.

    This implementation only works for dense arrays. However it should scale
    well to large data. Time Complexity: per iteration 3 dot products and 2 
    additions over 'n' where 'n' is the number of features (n_features).

    Implementation of:
        author={Juyang Weng and Yilu Zhang and Wey-Shiuan Hwang}
        journal={Pattern Analysis and Machine Intelligence, IEEE Transactions}
        title={Candid covariance-free incremental principal component analysis}
        year={2003}
        month={aug}
        volume={25}
        number={8}
        pages={1034-1040}

    Parameters
    ----------
    n_components : int
        Number of components to keep.
        Must be set

    amnesia : float
        A parameter that weights the present more strongly than the
        past. amnesia=1 makes the present count the same as anything else.

    copy : bool
        If False, data passed to fit are overwritten

    Attributes
    ----------
    `components_` : array, [n_components, n_features]
        Components.

    `explained_variance_ratio_` : array, [n_components]
        Percentage of variance explained by each of the selected components.

    Notes
    -----
    Calling fit(X) multiple times will update the components_ etc.

    Examples
    --------

    >>> import numpy as np
    >>> from sklearn.decomposition import CCIPCA
    >>> X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
    >>> ccipca = CCIPCA(n_components=2)
    >>> ccipca.fit(X)
    CCIPCA(amnesic=2.0, copy=True, n_components=2)
    >>> print(ccipca.explained_variance_ratio_)
    [ 0.97074203  0.02925797]

    See also
    --------
    PCA
    ProbabilisticPCA
    RandomizedPCA
    KernelPCA
    SparsePCA
    IPCA
    """

    def __init__(self, n_components=2, amnesic=2.0, copy=True):
        self.n_components = n_components
        if self.n_components < 2:
            raise ValueError("must specifiy n_components for CCIPCA")

        self.copy = copy
        self.amnesic = amnesic
        self.iteration = 0

    def fit(self, X, y=None, **params):
        """Fit the model with X.

        Parameters
        ----------
        X: array-like, shape (n_samples, n_features)
            Training data, where n_samples in the number of samples
            and n_features is the number of features.

        Returns
        -------
        self : object
            Returns the instance itself.

        Notes
        -----
        Calling multiple times will update the components
        """

        X = array2d(X)
        n_samples, n_features = X.shape
        X = as_float_array(X, copy=self.copy)

        # init
        if self.iteration == 0:
            self.mean_ = np.zeros([n_features], np.float)
            self.components_ = np.zeros([self.n_components, n_features], 
                                        np.float)
        else:
            if n_features != self.components_.shape[1]:
                raise ValueError('The dimensionality does not match')

        # incrementally fit the model
        for i in range(0, X.shape[0]):
            self.partial_fit(X[i, :])

        # update explained_variance_ratio_
        self.explained_variance_ratio_ = np.sqrt(np.sum(self.components_ ** 2, 
                                                        axis=1))

        # sort by explained_variance_ratio_
        idx = np.argsort(-self.explained_variance_ratio_)
        self.explained_variance_ratio_ = self.explained_variance_ratio_[idx]
        self.components_ = self.components_[idx, :]

        # re-normalize
        self.explained_variance_ratio_ = (self.explained_variance_ratio_ / self.explained_variance_ratio_.sum())

        for r in range(0, self.components_.shape[0]):
            self.components_[r, :] /= np.sqrt(np.dot(self.components_[r, :], self.components_[r, :]))

        return self

    def partial_fit(self, u):
        """ Updates the mean and components to account for a new vector.

        Parameters
        ----------
        _u : array [1, n_features]
            a single new data sample
        """

        n = float(self.iteration)
        V = self.components_

        # amnesic learning params
        if n <= int(self.amnesic):
            w1 = float(n + 2 - 1) / float(n + 2)
            w2 = float(1) / float(n + 2)
        else:
            w1 = float(n + 2 - self.amnesic) / float(n + 2)
            w2 = float(1 + self.amnesic) / float(n + 2)

        # update mean
        self.mean_ = w1 * self.mean_ + w2 * u

        # mean center u
        u = u - self.mean_

        # update components
        for j in range(0, self.n_components):

            if j > n:
                # the component has already been init to a zerovec
                pass

            elif j == n:
                # set the component to u
                V[j, :] = u
            else:
                # update the components
                V[j, :] = w1 * V[j, :] + w2 * np.dot(u, V[j, :]) * u / np.linalg.norm(V[j, :])

                normedV = V[j, :] / np.linalg.norm(V[j, :])

                u = u - np.dot(np.dot(u.T, normedV), normedV)

        self.iteration += 1
        self.components_ = V

        return

    def transform(self, X):
        """Apply the dimensionality reduction on X.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            New data, where n_samples in the number of samples
            and n_features is the number of features.

        Returns
        -------
        X_new : array-like, shape (n_samples, n_components)

        """
        X = array2d(X)
        X_transformed = X - self.mean_
        X_transformed = np.dot(X_transformed, self.components_.T)
        return X_transformed

    def inverse_transform(self, X):
        """Transform data back to its original space, i.e.,
        return an input X_original whose transform would be X

        Parameters
        ----------
        X : array-like, shape (n_samples, n_components)
            New data, where n_samples in the number of samples
            and n_components is the number of components.

        Returns
        -------
        X_original array-like, shape (n_samples, n_features)
        """
        return np.dot(X, self.components_) + self.mean_


def read_cvimages(path, sz=None):
    c = 0
    X = []
    y, z = [], []
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            subject_path = os.path.join(dirname, subdirname)
            for filename in os.listdir(subject_path):
                try:
                    if filename[-3:] == "png":
                        im = cv2.imread(os.path.join(subject_path, filename))
                        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                        im = cv2.resize(im, 
                                        (128, 128), 
                                        interpolation=cv2.INTER_CUBIC)
                        im = cv2.equalizeHist(im)
                        X.append(im.flatten("C").copy())  # flatten 2D to 1D
                        #X.append(im.flatten().astype(np.float32, copy=False))
                        y.append(c)
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise
            z.append(subdirname)
            c = c + 1
    return [X, y, z]


def project(W, X, mu=None):
    if mu is None:
        return np.dot(X, W)
    return np.dot(X - mu, W)


def EuclideanDistance(p, q):
    p = np.asarray(p).flatten()
    q = np.asarray(q).flatten()
    return np.sqrt(np.sum(np.power((p - q), 2)))


def CosineDistance(p, q):
    p = np.asarray(p).flatten()
    q = np.asarray(q).flatten()
    return -np.dot(p.T, q) / (np.sqrt(np.dot(p, p.T) * np.dot(q, q.T)))


def predict(Xin, W, mu, projections, y, z, labels):
    minDist = -.1,
    print "min dist: %f" % minDist
    minClass = -1
    Q = project(W, Xin.reshape(1, -1), mu)
    for i in xrange(len(projections)):
        dist = CosineDistance(projections[i], Q)
        #print y[i], dist
        if dist < minDist:
            minDist = dist
            print "found min dist: %f (%s)" % (minDist, labels[z[y[i]]])
            minClass = y[i]
        else:
            #print "dist: %f (%s)"%(dist, z[y[i]])
            pass
    return minClass, minDist


def asRowMatrix(X):
    if len(X) == 0:
        return np.array([])
    mat = np.empty((0, X[0].size), dtype=X[0].dtype)
    for row in X:
        mat = np.vstack((mat, np.asarray(row).reshape(1, -1)))
    return mat


if __name__ == "__main__":

    # read labels
    indata = open("labels.bin", "rb")
    labels = pickle.load(indata)

    # read images
    [X, y, z] = read_cvimages("raw")
    X = np.vstack(X)

    print "X. total pixel per face", X.shape
    print "y. numbers of samples", np.array(y).shape
    print "z. numbers of labels", np.array(z).shape

    # PCA
    k = len(z)
    print "principal component no: ", k
    pca_m = PCA(n_components=k).fit(X)
    W_pca = pca_m.components_.T
    pca_projections = []  # build pca projection model
    for xi in X:
        pca_projections.append(project(W_pca, xi.reshape(1, -1), mu=pca_m.mean_))

    # CCIPCA
    sample_no = len(y) - 2
    ccipca_m = CCIPCA(n_components=k, amnesic=1.0).fit(X[:sample_no, :])
    W_ipca = ccipca_m.components_.T
    ccipca_projections = []  # build pca projection model
    for xi in X[:sample_no, :]:
        ccipca_projections.append(project(W_ipca, xi.reshape(1, -1), mu=ccipca_m.mean_))

    ### testing phase
    test_img = cv2.imread(sys.argv[1])
    test_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
    test_img = cv2.resize(test_img, (128, 128), interpolation=cv2.INTER_CUBIC)
    test_img = cv2.equalizeHist(test_img)
    test_img = test_img.flatten("C").copy()

    print ""
    print "pca-based prediction result"
    t0 = time.time()
    [output_label, score] = predict(
        test_img, W_pca, pca_m.mean_, pca_projections, y, z, labels)
    print "took", "%f" % ((time.time() - t0) * 1000.), "ms"
    if output_label > -1:
        print "Label:", labels[z[output_label]], score
    else:
        print "no suitable label found"

    print ""
    print "ccipca-based prediction result (%d samples)" % sample_no
    t0 = time.time()
    [output_label, score] = predict(test_img, W_ipca, ccipca_m.mean_, ccipca_projections, y[:sample_no], z, labels)
    print "took", "%f" % ((time.time() - t0) * 1000.), "ms"
    if output_label > -1:
        print "Label:", labels[z[output_label]], score
    else:
        print "no suitable label found"

    print ""
    print "add more samles"
    add_no_files = 4
    ccipca_m.fit(X[sample_no:(sample_no + add_no_files), :])
    W_ipca2 = ccipca_m.components_.T
    for xi in X[sample_no:(sample_no + add_no_files), :]:
        ccipca_projections.append(
            project(W_ipca2, xi.reshape(1, -1), mu=ccipca_m.mean_))

    print "ccipca-based prediction result (%d samples)" % (sample_no + add_no_files)
    t0 = time.time()
    [output_label, score] = predict(test_img, W_ipca2, ccipca_m.mean_, ccipca_projections, y[:(sample_no + add_no_files)], z, labels)
    print "took", "%f" % ((time.time() - t0) * 1000.), "ms"
    if output_label > -1:
        print "Label:", labels[z[output_label]], score
    else:
        print "no suitable label found"
