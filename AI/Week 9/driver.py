#!/usr/bin/env python2

# -*- coding: utf-8 -*-

"""
Created on 24/09/17
CSP solving algorithms
@author: Benoit Pinguet
 """
from collections import deque
import heapq
import copy
import sys
import time

def intialDomain(c):
    return {1,2,3,4,5,6,7,8,9} if c == '0' else set([int(c)])

def quadrant(x):
    return str(int(x[0]) // 3) + str(int(x[1]) // 3)

QUADRANTDICT = {str(x)+str(y): quadrant(str(x)+str(y)) for x in range(9) for y in range(9)}

QUADRANTNEIGHBOURS = dict()

def buildQuadrantNeighbours():
    for c in (QUADRANTDICT):
        q = QUADRANTDICT[c]
        if q in QUADRANTNEIGHBOURS:
            QUADRANTNEIGHBOURS[q].add(c)
        else:
            QUADRANTNEIGHBOURS[q] = set([c])

buildQuadrantNeighbours()

def neighbours(x):
    neighboursList = set()
    row = x[0]
    col = x[1]
    for i in range(9):
        neighboursList.add(str(i)+str(col))
        neighboursList.add(str(row)+str(i))
    neighboursList = neighboursList.union(QUADRANTNEIGHBOURS[QUADRANTDICT[x]])
    neighboursList.remove(x)
    return neighboursList

class sudoku(object):
    def __init__(self, s = None):
        if s != None:
            self.X = {str(row)+str(col): intialDomain(s[row*9 + col]) for row in range(9) for col in range(9)}
        else:
            self.X = None
        #s is a string with initial state of sudoku
        #initialize X and D
    
    def setX(self, X):
        self.X = dict(X)
    def setd(self,x,d):
        self.X[x]=set([d])

    def __str__(self):
        s = '    1   2   3   4   5   6   7   8   9\n'
        for row in range(9):
            s += chr(ord('A')+row) +' | '
            for col in range(9):
                d = self.X[str(row)+str(col)]
                if len(d) == 1:
                    s += str(next(iter(d)))
                else:
                    s += ' '
                if col % 3 == 2:
                    s+= ' | '
                else:
                    s+= '   '
            s+='\n'
            if row % 3 == 2:
                s+='---------------------------------------\n'
        return s

    def toString(self):
        s = ''
        for row in range(9):
            for col in range(9):
                s += str(next(iter(self.X[str(row) +str(col)])))
        return s

    def isDomainEmpty(self,x):
        return len(self.X[x])== 0

    def revise(self,x,y):
        for d in self.X[x]:
            if self.X[y] == set([d]):
                self.X[x].remove(d)
                return True
        return False

    def getAllArcs(self):
        arcList = deque()
        for x in self.X:
            for y in neighbours(x): 
                arcList.append((x,y))
        return arcList

    def solved(self):
        for x,d in self.X.iteritems():
            if len(d) <> 1:
                return False
        return True

    def solve(self):
        self.AC3()
        if self.solved():
          return self.toString() + " AC3"
        solvedSudoku =  self.BTS()
        if solvedSudoku == None:
            return "unsolved"
        return solvedSudoku.toString() + " BTS"

    # AC3 algorithm takes a csp problem as input and checks arc consistency of problem
    #returns false if an inconsistency is found and true otherwise
    def AC3(self,q = None):
        queue = self.getAllArcs() if q == None else q
        try:
            while True:
                x,y = queue.popleft()
                if self.revise(x, y):
                    if self.isDomainEmpty(x):
                        return False
                    for neighbour in neighbours(x):
                        if neighbour <> y:
                            queue.append((neighbour,x))
        except IndexError:
            return True
    
    def getUnassigned(self):
        unassigned = []
        for x ,d in self.X.iteritems():
            if len(d) > 1:
                heapq.heappush(unassigned,(len(d),x))
        return unassigned

    def selectUnassigned(self):
        return self.getUnassigned()[0][1]
    
    def getOrderedValues(self,x):
        return set(self.X[x])

    def BTS(self):
        if self.solved():
            return self
        var = self.selectUnassigned()
        values = self.getOrderedValues(var)
        try:
            while True:
                n = values.pop()
                child = copy.deepcopy(self)
                child.setd(var,n)        
                queue = deque()
                for y in neighbours(var):
                    queue.append((y,var))
                if child.AC3(queue):
                    result = child.BTS()
                    if result != None:
                        return result
        except KeyError:
            return None



s = sudoku(sys.argv[1])

with open("output.txt","w") as file:
    
    file.write(s.solve()+'\n')

