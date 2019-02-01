from Grid import Grid
from sys import maxint
from threading import Timer
from BaseAI import BaseAI
from math import log
import time

defaultInitialTiles = 2
defaultProbability = 0.9

# Time Limit Before Losing
timeLimit = 0.2
allowance = 0.05
positionValues = [16 , 12, 12, 9 ,8, 8, 6, 6, 4, 4 , 4, 3, 3, 2 , 2, 1]

class State(object):
    def __init__(self, grid, move = None, depth = 0):
        self.grid = grid
        self.move = move
        self.depth = depth      

    def getPath(self, a,b, visited, cellValue):
        if not self.grid.crossBound((a, b)):
            if (not (a,b) in visited):
                if (self.grid.map[a][b] == cellValue) or  (self.grid.map[a][b] == cellValue/ 2):
                    v = set(visited)
                    v.add((a,b))
                    return self.getMaxPath(a, b, v)
        return 0

    def getMaxPath(self, x, y, visited):
        cellValue = self.grid.map[x][y]
        visited.add((x,y))
        maxPath = 0
        a = x
        b = y-1
        maxPath = max(maxPath, cellValue + self.getPath(a,b, visited, cellValue))
        a = x
        b = y+1
        maxPath = max(maxPath, cellValue + self.getPath(a,b, visited, cellValue))
        a = x+1
        b = y
        maxPath = max(maxPath, cellValue + self.getPath(a,b, visited, cellValue))
        a = x-1
        b = y
        maxPath = max(maxPath, cellValue + self.getPath(a,b, visited, cellValue))
        return maxPath

    def eval(self,printH = False):
        size = self.grid.size
        map = self.grid.map
        empty = 0
        score = 0
        score2 = 0
        tiles=[]
        maxTile = 0
        
        for x in xrange(size):
            for y in xrange(size):
                if map[x][y] > maxTile:
                    maxTile = map[x][y]
                    (maxTileX,maxTileY) = (x,y)
                score += map[x][y]
                score2 += map[x][y] ** 2
                if map[x][y] == 0:
                    empty += 1
                else:
                    tiles.append((map[x][y], (x,y)))

        tiles.sort(reverse=True)
        l = len(tiles)
        tileDist = 0
        if l > 1:
            i = 0
            while i+1 < l:
                best = tiles[i][0]
                j = i+1
                while j < l and tiles[j][0] >= best /2:
                    (x1,y1) = tiles[i][1]
                    (x2,y2) = tiles[j][1]
                    tileDist += max(0,(2-(abs(x2-x1)+abs(y2-y1))))
                    j += 1
                i += 1

        maxTileCornerDist = 0
        for t in tiles:
            if t[0] == maxTile:
                TileCornerDist = 1 *((t[1][0] == 0) or (t[1][0] == size -1)) + 1 *((t[1][1] == 0) or (t[1][1] == size -1))
                maxTileCornerDist = max(TileCornerDist, maxTileCornerDist)
                
        #number of tiles used on top of minimum
        binaryTilesDistance = (size * size - empty - bin(score).count("1")) 
        
        # maxTileCornerDist: importance of maximum tile (2 in a corner 1 on a side)
        
        w0 = 2048 / maxTile
        w1 = 1024
        w2 = 1024 / (size * size - empty)
        w3 = -float(score)/(size * size - empty)
        heuristic = int(w0*float(score2-score)/score) + int(w1*maxTileCornerDist) + int(w2* tileDist) + int(w3 * binaryTilesDistance)
        wh = min(1.0,float(score)/4096)
        e = wh*maxTile + (1-wh)*heuristic
        if printH:
            a=[0,0,0,0]
            a[0] = int(w0*float(score2-score)/score) 
            a[1] = int(w1*maxTileCornerDist)
            a[2] = int(w2 * tileDist)
            a[3] = int(w3 * binaryTilesDistance)
            return (a,e)
        else:
            return e 
    
    def childrenPlayer(self,moves):
        c = []
        #we assume that there are some available moves (i.e. isTerminal has been called before)
        for m in moves:
            g = self.grid.clone()
            g.move(m)
            c.append(State(g, m, self.depth +1))      
        return c

    def childrenComputer(self,cells):
        c = []
        #we assume that there are some available moves (i.e. isTerminal has been called before)
        for cell in cells:
            g2 = self.grid.clone()
            g4 = self.grid.clone()
            g2.setCellValue(cell, 2)
            g4.setCellValue(cell, 4)
            c.append(State(g2, move = None, depth = self.depth +1))
            c.append(State(g4, move = self.move, depth = self.depth +1))
        return c

class PlayerAI(BaseAI):
    def __init__(self):
        pass

    def stop(self):
        elapsed = time.time() - self.start
        # print("fired at : %.2f" %elapsed)
        self.stopFlag = True

    def getMove(self, grid):
        explored =[]
        self.start = time.time()
        self.stopFlag = False
        self.timer = Timer(0.2, self.stop)
        #self.timer.start()
        self.IDSDepth = 3
        self.totalNodes = 0
        self.totalLeaves = 0
        self.maxSuperChild = None
        self.order = [0,1,2,3]
        while not self.stopFlag and self.IDSDepth < 6:
            self.numberOfNodes = 0
            self.numberOfLeaves = 0
            self.maxChild = None
            self.maxUtility = -maxint
            self.order = self.maximize0(State(grid), self.IDSDepth, self.order)
            explored.append((self.IDSDepth,self.numberOfNodes,self.numberOfLeaves))
            self.totalLeaves += self.numberOfLeaves
            self.totalNodes += self.numberOfNodes
            if not self.stopFlag:
                self.maxSuperChild = self.maxChild
            # print ("depth : %d best move is: %d" %(self.IDSDepth,self.maxSuperChild.move))
            self.IDSDepth += 2
        
        elapsed = time.time() - self.start
        print("\nexplored: " + str(explored))
        print("\n total nodes %d and %d leaves explored" %(self.totalNodes, self.totalLeaves))
        print("returned at : %.2f" %elapsed)
        return self.maxSuperChild.move

    def minimize(self, state, maxDepth, alpha, beta):
        available = state.grid.getAvailableCells()
        if available == []:
            self.numberOfLeaves += 1
            return (None, state.grid.getMaxTile())
        
        (minChild, minUtility) = (None, maxint)
        for child in state.childrenComputer(available):
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
            #     print i
            # print("\n")
            self.numberOfNodes +=1 
            if self.stopFlag:
                return (minChild, minUtility)
            if child.depth == maxDepth:
                # print("leaf")
                utility = child.eval()
            else:
                # print("drilling with alpha = %d and beta = %d" %(alpha, beta))
                (_, utility) = self.maximize(child, maxDepth, alpha, beta)
            if utility < minUtility:
                
                # print("new min depth %d move found with Utility: %d" %(state.depth, utility))
                (minChild, minUtility) = (child, utility)
            if minUtility <= alpha:
                # print("pruning as min < alpha")
                break
            if minUtility < beta:
                beta = minUtility
        return (minChild, minUtility)

    def maximize(self, state, maxDepth, alpha, beta):
        moves = state.grid.getAvailableMoves()
        if moves == []:
            self.numberOfLeaves += 1
            return (None, state.grid.getMaxTile())

        (maxChild, maxUtility) = (None, -maxint)
        for child in state.childrenPlayer(moves):
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
            #     print i
            # print("\n")
            self.numberOfNodes +=1
            if self.stopFlag:
                return (maxChild, maxUtility)
            if child.depth == maxDepth:
                # print("leaf")
                utility = child.eval()
            else:
                # print("drilling with alpha = %d and beta = %d" %(alpha, beta))
                (_, utility) = self.minimize(child, maxDepth, alpha, beta)
            if utility > maxUtility:
                # print("new max depth %d move found with Utility: %d" %(state.depth, utility))
                (maxChild, maxUtility) = (child, utility)
            if maxUtility >= beta:
                # print("pruning with beta")
                break
            if maxUtility > alpha:
                alpha = maxUtility
        return (maxChild, maxUtility)

    def maximize0(self, state, maxDepth, order):
        moves = state.grid.getAvailableMoves(order)
        if moves == []:
            self.numberOfLeaves += 1
            return
        theoreticalMoves = set([0,1,2,3])
        moveUtilities = []
        for child in state.childrenPlayer(moves):
            # print("exploring move %d" %child.move)
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
                # print i
            # print("\n")
            self.numberOfNodes +=1
            if child.depth == maxDepth:
                utility = child.eval()
            else:
                # print("drilling with alpha = %d and beta = %d" %(self.maxUtility, maxint))
                (_, utility) = self.minimize(child, maxDepth, self.maxUtility, maxint)
                moveUtilities.append((utility,child.move))
                theoreticalMoves.remove(child.move)
            if utility > self.maxUtility:
                # print("new depth %d move found with Utility: %d" %(state.depth, utility))
                (self.maxChild, self.maxUtility) = (child, utility)
            if self.stopFlag:
                break
        moveUtilities.sort(reverse=True)
        newOrder = []
        for o in moveUtilities:
            newOrder.append(o[1])
        for m in theoreticalMoves:
            newOrder.append(m)
        return newOrder
        

if __name__ == '__main__':
    sGrid = Grid()

    sGrid.map[0] = [16, 8, 2, 2]
    sGrid.map[1] = [4, 4, 0, 0]
    sGrid.map[2] = [2, 2, 0, 0]
    sGrid.map[3] = [0, 0, 0, 0]


    for i in sGrid.map:
            print i
    print("\n")
    p = PlayerAI()
    s = State(sGrid)
    print(" eval: " + str(s.eval(True))+"\n")
    print(p.getMove(sGrid))
    visited = set()
    print(State(sGrid).getMaxPath(0,3,visited))