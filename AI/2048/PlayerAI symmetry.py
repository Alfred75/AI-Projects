from Grid import Grid
import numpy as np
from sys import maxint
from threading import Timer
from BaseAI import BaseAI
import time
import argparse

defaultInitialTiles = 2
defaultProbability = 0.9
possibleNewTiles = [2,4]
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
        self.minEvalDepth = 0
        self.maxEvalDepth = 0
        self.minEval = self.eval()
        self.maxEval = self.minEval
        self.minMove = 2
        self.moveTransform = [0,1,2,3]
        self.maxMove = 0
        self.minChild = None
        self.maxChild = None
        self.playerChildren = None
        self.computerChildren = None

    def checkLeaf(self, type):
        if type == 'Player':
            moves = self.grid.getAvailableMoves()
        else:
            moves = self.grid.getAvailableCells()
        if moves == []: #leaf
            self.minEvalDepth = maxint
            self.maxEvalDepth = maxint
            self.minEval = self.npGrid.max()
            self.maxEval = self.minEval
            self.playerChildren = []
            self.computerChildren = []
        return moves

    
        x1 = a / self.grid.size
        x2 = b / self.grid.size
        y1 = a % self.grid.size
        y2 = b % self.grid.size
        return abs(x2-x1)+abs(y2-y1)

    def eval(self):
        maxTileValue = np.max(self.npGrid)
        e1 = 0
        b = self.npGrid.ravel()
        for i in [0,3,12,15]:
            if b[i] == maxTileValue:
                e1 = 2048
                maxCorner = i
        
        tileValues = b[np.flatnonzero(self.npGrid)]

        sigma = np.std(tileValues)
        average = np.average(self.npGrid)
        usedTiles = np.count_nonzero(self.npGrid)
        e2 = (float(usedTiles)/16)*self.grid.getMaxTile() + (1- float(usedTiles)/16) *2048
        
        return int(float(e1) + e2 + 200 * sigma/average)


class PlayerAI(BaseAI):
    def __init__(self, depth = maxint, timer = 0.2, debug = False):
        self.exploredNodes = dict()
        self.debug = debug
        self.maxIDSDepth = int(depth) if depth != None else maxint
        self.timerLength = float(timer) if timer != None else 0.2

    def stop(self):
        if self.debug:
            elapsed = time.time() - self.startTime
            print("fired at : %.2f" %elapsed)
            print(self.totalNodes)
        self.stopFlag = True

    def addNode(self, node):
        if node.score not in self.exploredNodes:
            self.exploredNodes[node.score] = {}
        if node.id in self.exploredNodes[node.score]:
            if type(self.exploredNodes[node.score][node.id]) == tuple:
                node.moveTransform = self.exploredNodes[node.score][node.id][0]
                newNodeID = self.exploredNodes[node.score][node.id][1]
                mNode = self.exploredNodes[node.score][newNodeID]
            else:
                mNode = self.exploredNodes[node.score][node.id]
            return mNode

        npGrid = node.npGrid.copy()

        for i in range(4):
            if i == 0:
                self.exploredNodes[node.score][node.id] = node
                transform = [0,1,2,3]
                # print('Node')
                # print(npGrid)
                # print(transform)
            if i > 0:
                npGrid = np.rot90(npGrid)
                newId= str(npGrid)
                transform = [transform[2],transform[3],transform[1],transform[0]]
                # print('rot90')
                # print(npGrid)
                # print(transform)
                if newId != node.id:
                    self.exploredNodes[node.score][newId] = (transform,node.id)
            
            newIdT = str(npGrid.T)
            Tvector = [2,3,0,1]
            transformT = [0,0,0,0]
            for i in range(4):
                transformT[i] = transform.index(Tvector[i])
            # print('transposed')
            # print(npGrid.T)
            # print(transformT)
            if newIdT != node.id:
                self.exploredNodes[node.score][newIdT] = (transformT,node.id)

        return self.exploredNodes[node.score][node.id]  

    def createPlayerChildren(self, node):
        moves = node.checkLeaf('Player')
        if moves == []:
            return []
        c = []
        for m in moves:
            g = node.grid.clone()
            g.move(m)
            n = self.addNode(Node(g))
            n.minEval = n.eval()
            c.append((n.minEval, n.minEvalDepth, m, n.id))
            
        c.sort(reverse=True)
        node.playerChildren = c
        node.maxEval = max(node.playerChildren)[0]
        node.maxEvalDepth = 1
        return node.playerChildren

    def createComputerChildren(self,node):
        available = node.checkLeaf('Computer')
        if available == []:
            return []
        
        c = []
        for cell in available:
            for cellValue in possibleNewTiles:
                g = node.grid.clone()
                g.setCellValue(cell, cellValue)
                n = self.addNode(Node(g))
                n.maxEval = n.eval()
                c.append((n.maxEval, n.maxEvalDepth, cellValue, n.id))
            
        c.sort()
        node.computerChildren = c
        node.minEval = min(node.computerChildren)[0]
        node.minEvalDepth = 1
        return node.computerChildren

    def getMove(self, grid):
        self.startTime = time.time()
        node = Node(grid)
        # garbage collection
        newExplored = dict()
        for score in self.exploredNodes:
            if score >= node.score:
                newExplored[score] = self.exploredNodes[score]
        self.exploredNodes = newExplored
        self.stopFlag = False
        if self.timerLength != 0:
            self.timer = Timer(self.timerLength, self.stop)
            self.timer.start()
        self.IDSDepth = 3
        self.totalNodes = 0
        self.totalLeaves = 0
        while not self.stopFlag and self.IDSDepth <= self.maxIDSDepth:
            (transform,maxNode) = self.maximize(node, 0, self.IDSDepth, -maxint, maxint)
            if self.debug:
                print("@ depth %d" %self.IDSDepth)
                s = 0
                for count in self.exploredNodes:
                    l = len(self.exploredNodes[count])
                    print("%d: %d" %(count,l))
                    s += l
                print("total :%s" %s)
            self.IDSDepth += 1
        
        if self.debug:
            elapsed = time.time() - self.startTime
            print("returned at : %.2f" %elapsed)
            print("transform : ")
            print(transform)
            for i, child in enumerate(maxNode.playerChildren):
                print("Child %d:" %i)
                print(child)

        return transform[maxNode.maxMove]

    def minimize(self, node, depth, maxDepth, alpha, beta):
        
        mNode = self.addNode(node) 
        if mNode.minEvalDepth >= maxDepth or self.stopFlag:
                return (node.moveTransform, mNode)
        # take node's children if already calculated otherwise create them
        # those children will be ordered if they exist
        if mNode.computerChildren == None:
            self.createComputerChildren(mNode)
        children = mNode.computerChildren
        # leaf nodes are identified by children = [] (None means not explored)
        if children == []:
            return (node.moveTransform, mNode)

        for i, child in enumerate(children):
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
            #     print i
            # print("\n")
            if not self.stopFlag or depth < maxDepth - 1 :
                # print("drilling with alpha = %d and beta = %d" %(alpha, beta))
                drillNode = self.exploredNodes[mNode.score+child[2]][child[3]]
                (_,maxNode) = self.maximize(drillNode, depth + 1, maxDepth, alpha, beta)
                children[i] = (maxNode.maxEval, maxNode.maxEvalDepth, child[2], child[3])
                if maxNode.maxEval <= alpha:
                    # print("pruning with alpha")
                    break
                if maxNode.maxEval < beta:
                    beta = maxNode.maxEval
            
        mNode.minEvalDepth =  min(children, key = lambda t: t[1])[1] + 1
        children.sort()
        mNode.minEval = children[0][0]
        mNode.minMove = children[0][2]
        mNode.minChild = self.exploredNodes[node.score+children[0][2]][children[0][3]]
        return (node.moveTransform, mNode)

    def maximize(self, node, depth, maxDepth, alpha, beta):
        
        mNode = self.addNode(node)
        if mNode.maxEvalDepth + depth >= maxDepth or self.stopFlag:
                return (node.moveTransform, mNode)   
        # take node's children if already calculated otherwise create them (getavailableMoves)
        # those children will be ordered if they exist
        if mNode.playerChildren == None:
            self.createPlayerChildren(mNode)
        children = mNode.playerChildren
        # leaf mNodes are identified by children = [] (None means not explored)
        if children == []:
            return (node.moveTransform, mNode)

        
        for i, child in enumerate(children):
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
            #     print i
            # print("\n")
            if not self.stopFlag or depth < maxDepth - 1 :
                # print("drilling with alpha = %d and beta = %d" %(alpha, beta))
                drillNode = self.exploredNodes[mNode.score][child[3]]
                (_,minNode) = self.minimize(drillNode, depth + 1, maxDepth, alpha, beta)
                children[i] = (minNode.minEval, minNode.minEvalDepth, child[2], child[3])
                if minNode.minEval >= beta:
                    # print("pruning with beta")
                    break
                if minNode.minEval > alpha:
                    alpha = minNode.minEval
            
        mNode.maxEvalDepth =  min(children, key = lambda t: t[1])[1] + 1
        children.sort(reverse = True)
        mNode.maxEval = children[0][0]
        mNode.maxMove = children[0][2]
        mNode.maxChild = self.exploredNodes[node.score][children[0][3]]
        return (node.moveTransform, mNode)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solves 2048 AI Test")
    parser.add_argument("depth", nargs='?')
    parser.add_argument('timer', nargs='?')
    args = parser.parse_args()
    sGrid = Grid()
    # sGrid.map[0] = [16, 8, 2, 2]
    # sGrid.map[1] = [4, 4, 0, 0]
    # sGrid.map[2] = [1024, 2, 0, 0]
    # sGrid.map[3] = [0, 0, 0, 512]
    sGrid.map[0] = [0, 0, 2, 4]
    sGrid.map[1] = [0, 0, 0, 16]
    sGrid.map[2] = [0, 0, 0, 0]
    sGrid.map[3] = [0, 0, 0, 0]

    checkGrid = Grid()
    checkGrid.map[0] = [16, 8, 4, 0]
    checkGrid.map[1] = [8, 0, 0, 0]
    checkGrid.map[2] = [1024, 2, 0, 0]
    checkGrid.map[3] = [512, 0, 0, 0]

    checkGrid2 = Grid()
    checkGrid2.map[0] = [16, 8, 4, 0]
    checkGrid2.map[1] = [8, 0, 0, 0]
    checkGrid2.map[2] = [1024, 2, 0, 0]
    checkGrid2.map[3] = [512, 0, 2, 0]

    for i in sGrid.map:
            print i
    print("\n")
    p = PlayerAI(depth = args.depth, timer = args.timer, debug = True)
    s = Node(sGrid)
    p.addNode(s)
    print(" eval: " + str(s.eval())+"\n")
    print(p.getMove(sGrid))
    sGrid.map[0] = [0, 0, 0, 0]
    sGrid.map[1] = [0, 0, 2, 2]
    sGrid.map[2] = [0, 0, 8, 4]
    sGrid.map[3] = [0, 16, 8, 4]
    s = Node(sGrid)
    p.addNode(s)
    print(" eval: " + str(s.eval())+"\n")
    print(p.getMove(sGrid))

    