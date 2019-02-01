#!/usr/bin/env python2

# -*- coding: utf-8 -*-

"""
Created on 27/10/17
Week 7 perceptron Algo
@author: Benoit Pinguet
 """
import numpy as np
# import matplotlib.pyplot as plt
# from time import sleep
import sys

data = np.genfromtxt(sys.argv[1], delimiter = ",")
fileName = sys.argv[2]
#data = np.genfromtxt('input1.csv', delimiter = ",")
Y = data[:,2]
X = np.array(data)
X[:,2] = 1
weights = np.zeros(3)
color = np.where(data[:,2] == 1, 'b', 'r')
xForPlot = np.array([data[:,0].min(),data[:,0].max()])
solution=np.array(weights)
while True:

    fY = ((np.sum(X * weights,axis=1)*Y) <= 0)
    if fY.any():
        weights += np.sum(X[fY]*np.vstack(Y[fY]),axis = 0)
    else:
        break
    solution=np.append(solution, weights)

# plt.scatter(data[:,0],data[:,1],c=color)
# xForPlot = np.array([data[:,0].min(),data[:,0].max()])
# plt.plot(xForPlot,-(weights[0]*xForPlot + weights[2])/weights[1])
# plt.show()
solution = solution.reshape(-1,3)
np.savetxt(fileName, solution, fmt='%d', delimiter=',') # write output to file




