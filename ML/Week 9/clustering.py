#!/usr/bin/env python2

# -*- coding: utf-8 -*-

"""
Created on 24/09/17
Clustering algorithms for EDX ML course
@author: Benoit Pinguet
 """

import numpy as np
from scipy.stats import multivariate_normal as mvNormal
import sys

np.set_printoptions(precision=3)
X = np.genfromtxt(sys.argv[1], delimiter=",")
# X = np.genfromtxt('X.csv', delimiter=",")

def cluster(X, Niter, K):
    #initialize centers
    n = X.shape[0]
    u = np.random.randint(0, high = n, size =K)
    C = X[u]
    distances2 = np.zeros((n,K))

    for iteration in range(Niter):
        #update c
        for i in range(K):
            distances2[:,i] = np.sum((X-C[i])**2,axis=1)
    
        clusters = np.argmin(distances2,axis = 1)
        #update mu
        for i in range(K):
            data = X[clusters == i]
            C[i] = np.average(data,axis=0)
        #save results
        np.savetxt("centroids-%d.csv" %iteration, C,fmt = '%0.3f', delimiter=",") # write output to file
        
def  EMGMM(X, Niter, K):
    #initialize centers
    n = X.shape[0]
    u = np.random.randint(0, high = n, size =K)
    C = X[u]
    p = np.ones(K) / K
    sigma = np.empty((K,X.shape[1],X.shape[1]))
    for i in range(K):
        sigma[i]= np.identity(X.shape[1])
    # sigma = np.repeat(np.identity(X.shape[1])[np.newaxis,...],K,axis=0)

    for iteration in range(Niter):
        #E step
        phi = np.empty((n,K))
        for i in range(K):
            phi[:,i] = mvNormal.pdf(X,mean = C[i], cov=sigma[i])
        phi = phi / np.sum(phi,axis =1).reshape(-1,1)
        phi = phi*p
        #M step
        nk = np.sum(phi,axis=0)
        p = nk / n
        for i in range(K):
            C[i] = np.sum(X * phi[:,i, None],axis=0) / nk[i]
            diff = X-C[i]
            sigma[i] = np.sum( (diff[...,np.newaxis] * diff[:,np.newaxis]) * phi[:,i,None,None],axis = 0)  / nk[i]
        #save results
        np.savetxt("pi-%d.csv" %iteration, p,fmt = '%0.3f', delimiter=",") # write output to file
        np.savetxt("mu-%d.csv" %iteration, C,fmt = '%0.3f', delimiter=",") # write output to file
        for i in range(K):
            np.savetxt("Sigma-%d-%d.csv" %(i,iteration), sigma[i],fmt = '%0.3f', delimiter=",") # write output to file

cluster(X, 10, 5)
EMGMM(X, 10, 5)
