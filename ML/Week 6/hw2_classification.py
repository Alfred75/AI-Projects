from __future__ import division
import numpy as np
from math import sqrt, exp
import sys

np.set_printoptions(precision=3)
X_train = np.genfromtxt(sys.argv[1], delimiter=",")
y_train = np.genfromtxt(sys.argv[2])
X_test = np.genfromtxt(sys.argv[3], delimiter=",")
# X_train = np.genfromtxt('X_train.csv', delimiter=",")
# y_train = np.genfromtxt('y_train.csv')
# X_test = np.genfromtxt('X_test.csv', delimiter=",")
# X_train = np.array([[1,2,3],
#             [1,3,4],
#             [1,2,-5],
#             [1,-2,3],
#             [-1,-4,5],
#             [0,0,1],
#             [1,-4,1],
#             [2,6,5],
#             [-2,2,1],
#             [8,0,1]],dtype=np.float64)
# y_train = np.array([0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0])
# X_test = np.array([[1,4,7],
        # [3,6,2]])

## can make more functions if required
def calibrate(x,y):
  n = float(y.size)
  yCount = np.bincount(y.astype(dtype=np.int64)).astype(dtype=np.float64)
  piPrior = yCount / n

  mu = np.zeros((piPrior.size, x.shape[1]))
  sigma = np.zeros((piPrior.size, x.shape[1], x.shape[1]))
  det = np.zeros((piPrior.size, x.shape[1]))

  for i in range(piPrior.size):
    Xy = x[y==i]
    mu[i] = np.average(Xy, axis=0)
    sigma[i] = np.cov(Xy, rowvar= False)

  invDet = np.reciprocal(np.sqrt(np.linalg.det(sigma)))
  invSigma = np.linalg.inv(sigma)

  return(piPrior, mu, invSigma, invDet)

def pluginClassifier(X_train, y_train, X_test):
  # this function returns the required output
  piPrior, mu, invSigma, invDet = calibrate(X_train,y_train)
  
  r = np.zeros((X_test.shape[0],piPrior.size))
  for i in range(X_test.shape[0]):
    for j in range(piPrior.size):
      r[i,j] = piPrior[j] *invDet[j] * exp(-(X_test[i]-mu[j]).dot(invSigma[j].dot(X_test[i]-mu[j]))/2)

  r = r / r.sum(axis=1).reshape(-1,1)
  return r 

final_outputs = pluginClassifier(X_train, y_train, X_test) # assuming final_outputs is returned from function

np.savetxt("probs_test.csv", final_outputs,fmt = '%0.3f', delimiter=",") # write output to file