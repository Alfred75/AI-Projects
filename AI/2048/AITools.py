#!/usr/bin/env python2

# -*- coding: utf-8 -*-

"""
Created on 24/09/17
Minmax implementation
@author: Benoit Pinguet
 """
import time

#Node is the combination of a state and a parent node (None if this is initial state)
class Node(object):
    def __init__(self, grid, parent = None):
        self.parent = parent
        self.grid = grid
        self.depth = 0 if self.parent == None else self.parent.depth + 1

class FrontierDFS(object):
    def __init__(self, size):
        self.size = size
        self.queue = []
        self.queueId = set()
        self.queueSize = 0
    
    def isEmpty(self):
        return self.queueSize == 0
    
    def getNext(self):
        nextNode = self.queue.pop()
        self.queueId.remove(nextNode.id)
        self.queueSize -= 1
        return nextNode

    def add(self, node):
        self.queue.append(node)
        self.queueId.add(node.id)
        self.queueSize += 1

class TreeSearchAlgorithm(object):

    def __init__(self, algo, size, initialPositions):
        self.size = size
        self.frontier = FrontierDFS(size)
        self.frontier.add(Node(initialPositions, self.frontier.manhattanSize, None))
        
    def treeSearch(self):
        self.expanded = 0
        self.maxDepth = 0
        explored = set()

        while not self.frontier.isEmpty():
            node = self.frontier.getNext()
            explored.add(node.id)

            if goalTest(node.state):
                self.endTime = time.time()
                return node
            
            self.expanded += 1
            for neighbor in self.frontier.neighbors(node):
                if not (neighbor.id in explored or neighbor.id in self.frontier.queueId):
                    self.frontier.add(neighbor)
                    if neighbor.depth > self.maxDepth:
                        self.maxDepth = neighbor.depth

        self.endTime = time.time()   
        return None
     
def run(algo, size, initialPositions, filename, mode, verbose = True):
    searchAlgo = TreeSearchAlgorithm(algo, size, initialPositions)
    goal = searchAlgo.treeSearch()
    path = goal.getPath(size)
    running_time = searchAlgo.endTime - searchAlgo.startTime 
   