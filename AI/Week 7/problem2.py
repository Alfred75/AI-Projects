#!/usr/bin/env python2

# -*- coding: utf-8 -*-

"""
Created on 27/10/17
Week 7 gradient descent Algo
@author: Benoit Pinguet
 """
import numpy as np
import sys
data = np.genfromtxt(sys.argv[1], delimiter = ",")
# data = np.genfromtxt('input2.csv', delimiter = ",")
fileName = sys.argv[2]

X = np.array(data[:,:2])
Y = data[:,2]
muX = np.mean(X,axis=0)
sigmaX = np.std(X,axis=0)
X = (X - muX)/sigmaX
X= np.insert(X,0,1,axis=1)
learningRates = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 0.9]
iterations = 100
solution = np.ones((len(learningRates),5))*iterations
error = np.zeros((len(learningRates),iterations))
index = 0

for l in learningRates:
    weights = np.zeros(3)
    for i in range(iterations):
        f = np.dot(X,weights)
        loss = np.mean((f- Y)**2.0)/2.0
        error[index,i] = loss
        weights -= l * np.mean((f-Y).reshape(-1,1)*X,axis = 0)

    solution[index,0] = l
    solution[index,2:] = weights
    # solution[index,2] = sigmaY * (weights[0] - np.sum(weights[1:] * muX / sigmaX))
    # solution[index,3:] = sigmaY * (weights[1:]*sigmaX)
    index += 1
    

np.savetxt(fileName, solution, fmt='%0.8f', delimiter=',') # write output to file




