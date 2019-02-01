import numpy as np
import sys

lambda_input = int(sys.argv[1])
sigma2_input = float(sys.argv[2])
X_train = np.genfromtxt(sys.argv[3], delimiter = ",")
y_train = np.genfromtxt(sys.argv[4])
X_test = np.genfromtxt(sys.argv[5], delimiter = ",")

## Solution for Part 1
# wRR = (lambda.I + T(X)X)^(-1).T(X)y.
def part1(lambda_, X, y):
    ## Input : Arguments to the function
    ## Return : wRR, Final list of values to write in the file
    return np.linalg.inv(lambda_ * np.eye(X.shape[1]) + np.dot(X.T, X)).dot(X.T.dot(y))

wRR = part1(lambda_input, X_train, y_train)
print(wRR)
 # Assuming wRR is returned from the function
np.savetxt("wRR_" + str(lambda_input) + ".csv", wRR, delimiter="\n") # write output to file


## Solution for Part 2
def part2(lambda_, sigma2, Xin, Yin, Xtest):

    dim = Xin.shape[1]
    n = Xtest.shape[0]
    XtX = np.dot(Xin.T, Xin)
    active = []

    for k in range(10):
        bigSigma = np.linalg.inv(lambda_ * np.eye(dim) + (1/sigma2)*XtX)
        #mu = np.linalg.inv(lambda_ * sigma2 * np.eye(dim) + XtX)).dot(XtY)
        nMax = 0
        for i in range(n):
            p = np.dot(Xtest[i].T,bigSigma.dot(Xtest[i]))
            if p > nMax and not (i+1) in active:
                nMax = p
                nMaxIndex = i
        XtX += np.outer(Xtest[nMaxIndex],Xtest[nMaxIndex].T)
        active.append(nMaxIndex + 1)

    return np.array(active).reshape(1,10)

active = part2(lambda_input, sigma2_input, X_train,y_train,X_test)
print(active)  # Assuming active is returned from the function
np.savetxt("active_" + str(lambda_input) + "_" + str(int(sigma2_input)) + ".csv", active, fmt='%d', delimiter=',') # write output to file
