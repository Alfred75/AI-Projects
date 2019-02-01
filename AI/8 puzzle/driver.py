#!/usr/bin/env python2

# -*- coding: utf-8 -*-

"""
Created on 24/09/17
8 Puzzle solving algorithms for EDX AI course
@author: Benoit Pinguet
 """

import argparse
from sys import exit
import time
from collections import deque
import heapq
from resource import getrusage, RUSAGE_SELF

# list of implemented algos
ALGOS = {"dfs", "bfs", "ast"}
#list of test cases
TEST_CASES = [
    ["dfs", [3,1,2,0,4,6,5,7,8]],
    ["dfs", [1,2,5,3,4,0,6,7,8]],
    ["ast", [1,2,5,3,4,0,6,7,8]],
    ["bfs", [3,1,2,0,4,6,5,7,8]],
    ["dfs", [3,1,2,0,4,6,5,7,8]],
    ["ast", [3,1,2,0,4,6,5,7,8]],
    ["bfs", [6,1,8,4,0,2,7,3,5]],
    ["dfs", [6,1,8,4,0,2,7,3,5]],
    ["ast", [6,1,8,4,0,2,7,3,5]],
    ["bfs", [8,6,4,2,1,3,5,7,0]],
    ["dfs", [8,6,4,2,1,3,5,7,0]],
    ["ast", [8,6,4,2,1,3,5,7,0]],
]

# goal test function
def goalTest(state):
        return state == [0,1,2,3,4,5,6,7,8]

#Node is the combination of a state and a parent node (None if this is initial state)
class Node(object):
    def __init__(self, state, manhattanSize = 0, parent = None):
        self.parent = parent
        self.state = state
        self.depth = 0 if self.parent == None else self.parent.depth + 1
        #no need to calculate if not used. not sure about perf impact (guess not huge)
        self.f = (self.depth + self.manhattan(manhattanSize)) if manhattanSize > 0 else 0
        self.id = ''.join(map(str,self.state))

    # this function calculated the manahttan distance for that node
    def manhattan(self, size):
        dist = 0
        for index in range(size ** 2):
            if not self.state[index] == 0:
                dist += abs((index // size) - (self.state[index] // size)) #add vertical distance
                dist += abs((index % size) - (self.state[index] % size)) #add horizontal distance
                
        return dist
        
    #return the description of the action used to go from Parent to Node
    def action(self, size):
        position = self.state.index(0)
        parentPosition = self.parent.state.index(0)
        if position == parentPosition - size:
            return "Up"
        elif position == parentPosition + size:
            return "Down"
        elif position == parentPosition - 1:
            return "Left"
        elif position == parentPosition + 1:
            return "Right"
    
    #get path information from nodes
    def getPath(self, size):
        currentNode = self
        path = []
        while currentNode.parent != None:
            path.append(currentNode.action(size))
            currentNode = currentNode.parent
    
        path.reverse()
        return path

class Frontier(object):
    def __init__(self, size):
        self.size = size
        self.manhattanSize = 0
        self.queue = []
        self.queueId = set()
        self.queueSize = 0
    
    def isEmpty(self):
        return self.queueSize == 0
    
    def pop(self):
        return self.queue.pop()

    def append(self, node):
        self.queue.append(node)

    def getNext(self):
        nextNode = self.pop()
        self.queueId.remove(nextNode.id)
        self.queueSize -= 1
        return nextNode

    def add(self, node):
        self.append(node)
        self.queueId.add(node.id)
        self.queueSize += 1

    # function that returns the possible moves given position of the blank and size of the problem
    # returns a list of possible destination for the blank
    # this function is part of the Frontier class and not Node because the output order is dependant on the choosen algo
    def possibleMoves(self, node):
        position = node.state.index(0)
        moves = []
        if position >= self.size: 
            moves.append(position - self.size) # "up"
        if position < self.size * (self.size - 1):
            moves.append(position + self.size) # "down"
        if position % self.size > 0:
            moves.append(position -1) # "left"
        if (position+1) % self.size > 0:
            moves.append(position +1) # "right"
        
        return moves

    # returns a List of the neighbor Nodes
    def neighbors(self, node):
        position = node.state.index(0)
        neighborsList = []
        for target in self.possibleMoves(node):
            newPosition = list(node.state)
            newPosition[position] = node.state[target]
            newPosition[target] = 0
            neighborsList.append(Node(newPosition, self.manhattanSize, node))
        
        return neighborsList

class FrontierBFS(Frontier):
    #implement a double-ended queue instead of a list to achieve the BFS algo
    def __init__(self, size):
        super(FrontierBFS, self).__init__(size)
        self.queue = deque()

    def pop(self):
        return self.queue.popleft()
    
class FrontierDFS(Frontier):
    #override possibleMoves function to change the order
    def possibleMoves(self, node):
        position = node.state.index(0)
        moves = []
        if (position +1) % self.size > 0:
            moves.append( position +1) # "right"
        if position % self.size > 0:
            moves.append( position -1) # "left"
        if position < self.size * (self.size - 1):
            moves.append( position + self.size) # "down"
        if position >= self.size: 
            moves.append(position - self.size) # "up"
        
        return moves

class FrontierAST(Frontier):
    #enables manhattan distance calculation in nodes
    def __init__(self, size):
        super(FrontierAST, self).__init__(size)
        self.manhattanSize = size
    
    def pop(self):
        return heapq.heappop(self.queue)[1]

    def append(self, node):
        heapq.heappush(self.queue,(node.f,node))

class TreeSearchAlgorithm(object):

    def __init__(self, algo, size, initialPositions):
        self.size = size
        if algo == "bfs":     
            self.frontier = FrontierBFS(size)
        elif algo == "dfs":
            self.frontier = FrontierDFS(size)
        elif algo == "ast":
            self.frontier = FrontierAST(size)

        self.frontier.add(Node(initialPositions, self.frontier.manhattanSize, None))
        
    def treeSearch(self):
        
        self.startTime = time.time()
        self.expanded = 0
        self.maxDepth = 0
        explored = set()

        while not self.frontier.isEmpty():
            print('%d, %d' %(len(self.frontier.queue),len(explored)))
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
        print('returning')
        print('frontier : %d' %len(self.frontier.queue)) 
        return None
     
def run(algo, size, initialPositions, file, verbose = True):
    searchAlgo = TreeSearchAlgorithm(algo, size, initialPositions)
    goal = searchAlgo.treeSearch()
    path = goal.getPath(size)
    running_time = searchAlgo.endTime - searchAlgo.startTime 
    memory = float(getrusage(RUSAGE_SELF).ru_maxrss) / 1000000
    
    if goal.depth > 30 and not verbose:
        file.write("path_to_goal: " + str(path[:10]) + " ... " + str(path[-10:]) + "\n")
    else:
        file.write("path_to_goal: " + str(path) + "\n")
    file.write("cost_of_path: " + str(goal.depth) + "\n")
    file.write("nodes_expanded: " + str(searchAlgo.expanded) + "\n")
    file.write("search_depth: " + str(goal.depth) + "\n")
    file.write("max_search_depth: " + str(searchAlgo.maxDepth) + "\n")
    file.write("running_time: " + str(running_time) + "\n")
    file.write("max_ram_usage: " + str(memory) + "\n")

if __name__ == '__main__':
    #create parser
    parser = argparse.ArgumentParser(description="Solves 8 Puzzle with different tree search algorithms")
    parser.add_argument("method", nargs = '?', default = "bfs", help = "this is the search method to use to solve the puzzle. Implemented : bfs,dfs")
    parser.add_argument('initialState',metavar='init', type=str, nargs = '?',
                    help='list of 9 integers representing the initial state of the game. Use 0 for the blank')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    # run all test cases
    if True:#args.test:
        with open("test_results.txt","w") as file:
            pass
        with open("test_results.txt","a") as file:
            for game in TEST_CASES:
                print ("Running: %s [%s]" %(game[0],str(game[1])))
                file.write("GAME: "+ game[0] + " " + str(game[1])+"\n")
                run(game[0],3,game[1],file, verbose = False)
            exit(0)
    
    #test if method is known or implemented
    if args.method not in ALGOS:
        print ("unknown method %s" %args.method)
        exit(1)
    #test whether initial state argument is correct or not
    initialPositions = map(int,args.initialState.split(','))
    if len(initialPositions) != 9:
        print "wrong number or arguments. the initial sequence must be numbers a list of 9 unique ints between 0 and 8"
        exit(1)
    testSet = set()
    for i in initialPositions:
        if i<0 or i>8:
            print("wrong number %s the initial sequence must be numbers a list of 9 unique ints between 0 and 8" %i)
            exit(2)
        if i in testSet:
            print("duplicate %s the initial sequence must be numbers a list of 9 unique ints between 0 and 8" %i)
            exit(3)
        testSet.add(i)
    with open("output.txt","w") as file:
        run(args.method,3,initialPositions,file, verbose = True)
    