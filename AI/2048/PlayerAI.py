from Grid import Grid
import numpy as np
from sys import maxint
from threading import Timer
from BaseAI import BaseAI
import time
import argparse

possibleNewTiles = [2,4]
OptimizedVecIndex = [1, 3, 2, 0]
# Time Limit Before Losing
timeLimit = 0.2
allowance = 0.05

class Node(object):
    def __init__(self, grid):
        self.grid = grid
        self.npGrid = np.array(grid.map)
        self.id = str(self.npGrid)
        self.score = np.sum(self.npGrid)
        #how many steps further is this node eval
        self.minEvalDepth = -1 # -1 means not evaluated yet
        self.maxEvalDepth = -1
        self.evalScore = None
        self.minEval = 0
        self.maxEval = 0
        self.minChild = None
        self.maxChild = None
        self.playerChildren = None
        self.computerChildren = None
        self.playerLeaf = False
        self.computerLeaf = False

class PlayerAI(BaseAI):
    def __init__(self, depth = maxint, timer = 0.2, debug = False):
        self.exploredNodes = dict()
        self.debug = debug
        self.maxIDSDepth = int(depth) if depth != None else maxint
        self.timerLength = float(timer) if timer != None else 0.2
        self.createEvalMatrix()

    def createEvalMatrix(self):

        bottomDistance=np.array([[0,0,0,0],
                                [0,0,0,0],
                                [1,1,1,1],
                                [3,3,3,3]])
        self.bottomWeight = 4 ** bottomDistance
        snakeBase = np.array([3,2,1,0,4,5,6,7,11,10,9,8,12,13,14,15])
        self.snakeWeight = (4 ** snakeBase).reshape(4,4)
        
    def eval(self, node):
        if node.evalScore != None:
            return node.evalScore
        
        tile3 = node.npGrid[3][3]
        tile2 = node.npGrid[2][0]
        filled3 = 0
        filled2 = 0
        for i in range(3):
            if node.npGrid[3][2-i] <= node.npGrid[3][3-i]:
                filled3 += 1 
            if node.npGrid[2][i+1] <= node.npGrid[2][i]:
                filled2 += 1 
        if tile2 >= node.npGrid[3][0]:
            filled2 = 0
        filled3 = 4 ** filled3
        filled2 = 2 ** filled2
        filled = np.array([1,1,filled2,filled3])
        
        wB = 1
        wS = 1
        evalBottom = np.sum(node.npGrid * self.bottomWeight)
        evalSnake = np.sum(node.npGrid * self.snakeWeight,axis=1)
        evalSnake = np.sum(evalSnake * filled)

        node.evalScore = wB*evalBottom + wS*evalSnake
        # if this is the first time that eval is run, save score and set depth to 0
        if node.minEvalDepth < 0:
            node.minEval = node.evalScore
            node.minEvalDepth = 0
        if node.maxEvalDepth < 0:
            node.maxEval = node.evalScore    
            node.maxEvalDepth = 0
        
        return node.evalScore

    def checkLeaf(self, node, type):
        if type == 'Player':
            if node.playerLeaf:
                return []
            moves = node.grid.getAvailableMoves(dirs = OptimizedVecIndex)
            if moves == []:
                node.maxEvalDepth = maxint
                node.playerLeaf = True
                node.playerChildren = []
                node.maxEval = self.eval(node)
        else:
            if node.computerLeaf:
                return []
            moves = node.grid.getAvailableCells()
            if moves == []:
                node.minEvalDepth = maxint
                node.computerLeaf = True
                node.computerChildren = []
                node.minEval = self.eval(node)
        return moves

    def addNode(self, node):
        if node.score not in self.exploredNodes:
            self.exploredNodes[node.score] = {}
        if node.id not in self.exploredNodes[node.score]:
            self.exploredNodes[node.score][node.id] = node       
        return self.exploredNodes[node.score][node.id]

    def createPlayerChildren(self, node):
        moves = self.checkLeaf(node,'Player')
        if moves == []:
            return []
        c = []
        for m in moves:
            g = node.grid.clone()
            g.move(m)
            n = self.addNode(Node(g))
            c.append((0,-1,m,n)) #eval, depth, move, node

        node.playerChildren = c
        return c

    def createComputerChildren(self,node):
        available = self.checkLeaf(node,'Computer')
        if available == []:
            return []
        c = []
        for cell in available:
            for cellValue in possibleNewTiles:
                g = node.grid.clone()
                g.setCellValue(cell, cellValue)
                n = self.addNode(Node(g))
                c.append((0,-1,cellValue,n)) #eval, depth, move, node
           
        node.computerChildren = c
        return node.computerChildren

    def getMove(self, grid):
        node = Node(grid)
        self.testTime = time.time() + self.timerLength
        # garbage collection
        newExplored = dict()
        for score in self.exploredNodes:
            if score >= node.score:
                newExplored[score] = self.exploredNodes[score]
        self.exploredNodes = newExplored
       
        # start 
        self.IDSDepth = 1
        self.totalNodes = 0
        self.totalLeaves = 0
        while time.time() < self.testTime and self.IDSDepth <= self.maxIDSDepth:
            (maxChild, utility, evalDepth) = self.maximize(node, 0, self.IDSDepth, -maxint, maxint)
            if self.debug:
                print("@ depth %d" %self.IDSDepth)
                s = 0
                for count in self.exploredNodes:
                    l = len(self.exploredNodes[count])
                    print("%d: %d" %(count,l))
                    s += l
                print("total :%s" %s)
            self.IDSDepth += 2
        
        if self.debug:
            elapsed = time.time() - self.startTime
            print("returned at : %.2f" %elapsed)
            for i, child in enumerate(self.exploredNodes[node.score][node.id].playerChildren):
                print("Child %d:" %i)
                print(child)
        return self.exploredNodes[node.score][node.id].maxMove

    def minimize(self, node, depth, maxDepth, alpha, beta):
        
        mNode = self.addNode(node) 
        if time.time() >= self.testTime:
            if mNode.minEvalDepth < 0:
                return (None, self.eval(mNode), 0)
            else:
                
                return (mNode.minChild, mNode.minEval, mNode.minEvalDepth)

        if mNode.minEvalDepth + depth >= maxDepth:
                return (mNode.minChild, mNode.minEval, mNode.minEvalDepth)
        # take node's children if already calculated otherwise create them
        # those children will be ordered if they exist
        if mNode.computerChildren == None:
            self.createComputerChildren(mNode)
        children = mNode.computerChildren
        # leaf nodes are identified by children = [] (None means not explored)
        # in this case eval is MaxTile
        if children == []:
            return (None, mNode.minEval, maxint)
        
        # if depth is reached and children not empty (othterwise caught above):
        # eval and return
        if depth == maxDepth:
            return (None, self.eval(mNode), 0)

        for i, child in enumerate(children):
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
            #     print i
            # print("\n")
            # print("drilling with alpha = %d and beta = %d" %(alpha, beta))
            (_,utility, exploredDepth) = self.maximize(child[3], depth + 1, maxDepth, alpha, beta)
            if time.time() >= self.testTime:
                return (None, mNode.minEval, mNode.minEvalDepth)
            children[i] = (utility, exploredDepth, child[2], child[3])
            if utility <= alpha:
                # print("pruning with alpha")
                break
            if utility < beta:
                beta = utility
            
        mNode.minEvalDepth =  min(children, key = lambda t: t[1])[1] + 1
        children.sort()
        mNode.minEval = children[0][0]
        mNode.minMove = children[0][2]
        mNode.minChild = children[0][3]
        return (mNode.minChild, mNode.minEval, mNode.minEvalDepth)

    def maximize(self, node, depth, maxDepth, alpha, beta):
        
        mNode = self.addNode(node)
        if time.time() >= self.testTime:
            if mNode.maxEvalDepth < 0:
                return (None, self.eval(mNode), 0)
            else:
                return (mNode.maxChild, mNode.maxEval, mNode.maxEvalDepth)

        if mNode.maxEvalDepth + depth >= maxDepth:
                return (mNode.maxChild, mNode.maxEval, mNode.maxEvalDepth)
        # take node's children if already calculated otherwise create them
        # those children will be ordered if they exist
        if mNode.playerChildren == None:
            self.createPlayerChildren(mNode)
        children = mNode.playerChildren
        # leaf nodes are identified by children = [] (None means not explored)
        # in this case eval is MaxTile
        if children == []:
            return (None, mNode.maxEval, maxint)
        
        # if depth is reached and children not empty (othterwise caught above):
        # eval and return
        if depth == maxDepth:
            return (None, self.eval(mNode), 0) 
        
        for i, child in enumerate(children):
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
            #     print i
            # print("\n")
            # print("drilling with alpha = %d and beta = %d" %(alpha, beta))
            (_,utility, exploredDepth) = self.minimize(child[3], depth + 1, maxDepth, alpha, beta)
            if time.time() >= self.testTime:
                return (None, mNode.maxEval, mNode.maxEvalDepth)
            children[i] = (utility, exploredDepth, child[2], child[3])
            if utility >= beta:
                # print("pruning with alpha")
                break
            if utility > alpha:
                alpha = utility
            
        mNode.maxEvalDepth =  min(children, key = lambda t: t[1])[1] + 1
        children.sort(reverse = True)
        mNode.maxEval = children[0][0]
        mNode.maxMove = children[0][2]
        mNode.maxChild = children[0][3]
        if depth == 0:
            pass
        return (mNode.maxChild, mNode.maxEval, mNode.maxEvalDepth)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solves 2048 AI Test")
    parser.add_argument("depth", nargs='?')
    parser.add_argument('timer', nargs='?')
    args = parser.parse_args()
    sGrid = Grid()
    sGrid.map[0] = [16, 8, 2, 2]
    sGrid.map[1] = [4, 4, 0, 0]
    sGrid.map[2] = [1024, 2, 0, 0]
    sGrid.map[3] = [0, 0, 0, 512]
    # sGrid.map[0] = [0, 0, 2, 4]
    # sGrid.map[1] = [0, 0, 0, 16]
    # sGrid.map[2] = [0, 0, 0, 0]
    # sGrid.map[3] = [0, 0, 0, 0]

    checkGrid = Grid()
    checkGrid.map[0] = [0, 0, 0, 0]
    checkGrid.map[1] = [4, 8, 0, 0]
    checkGrid.map[2] = [16, 8, 32, 0]
    checkGrid.map[3] = [8, 64, 256, 0]

    checkGrid2 = Grid()
    checkGrid2.map[0] = [0, 0, 0, 0]
    checkGrid2.map[1] = [0, 0, 4, 8]
    checkGrid2.map[2] = [0, 16, 8, 32]
    checkGrid2.map[3] = [0, 8, 64, 256]

    for i in sGrid.map:
            print i
    print("\n")
    p = PlayerAI(depth = args.depth, timer = args.timer, debug = True)
    # p = PlayerAI(depth = 1, timer = 0, debug = True)
    s = Node(sGrid)
    print(" eval: " + str(p.eval(s))+"\n")
    print(p.getMove(sGrid))
    m = p.createEvalMatrix()
    print(m)
    print(p.eval(Node(checkGrid)))
    print(p.eval(Node(checkGrid2)))
    