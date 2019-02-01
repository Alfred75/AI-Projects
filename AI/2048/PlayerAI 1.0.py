from BaseAI import BaseAI
from Grid import Grid
from sys import maxint
from threading import Timer
import time

defaultInitialTiles = 2
defaultProbability = 0.9

# Time Limit Before Losing
timeLimit = 0.2
allowance = 0.05
positionValues = [ 16 , 12, 12, 9 ,8, 8, 6, 6, 4, 4 , 4, 3, 3, 2 , 2, 1]

class State(object):
    def __init__(self, grid, move = None, depth = 0):
        self.grid = grid
        self.move = move
        self.depth = depth

    def analyze(self):
        size = self.grid.size
        map = self.grid.map
        empty = 0
        score = 0
        tiles=[]
        weightedScore = [0,0,0,0]
        maxTile = 0
        maxweightedscore = 0
        
        for x in xrange(size):
            for y in xrange(size):
                if map[x][y] > maxTile:
                    maxTile = map[x][y]
                    (maxTileX,maxTileY) = (x,y)
                score += map[x][y]
                weightedScore[0] += (size - x) * (size - y)* map[x][y] #top left corner
                weightedScore[1] += (size - x) * (y + 1 ) * map[x][y] #top right corner
                weightedScore[2] += (size - y) * (x + 1 )* map[x][y] #bottom left corner
                weightedScore[3] += (x +1) *(y + 1)* map[x][y] #bottom right corner
                if map[x][y] == 0:
                    empty += 1
                else:
                    tiles.append((map[x][y], (x,y)))

        tiles.sort(reverse=True)
        l = len(tiles)
        if l > 1:
            (x1,y1) = tiles[0][1]
            (x2,y2) = tiles[1][1]
            tileDist = tiles[1][0] * max(0,2-(abs(x2-x1)+abs(y2-y1)))
        

        Zscore = 0 #longest max path
        for t in tiles:
            if t[0] == maxTile:
                corner = t[1] == (0,0) or t[1] == (size-1,0) or t[1] == (0, size -1) or t[1] == (size-1,size-1)
                if corner:
                    Zscore = max(Zscore, self.getMaxPath(t[1][0],t[1][1],set()))
        

        binaryTilesDistance = empty + bin(score).count("1") #number of tiles used vs minimum
        weightedScore = max(weightedScore) #score weighted by distance to a corner
        # maxTileCornerDist: importance of maximum tile (2 - how many moves to get to a corner: 0, 1, 2)
        maxTileCornerDist = 1 *((maxTileX == 0) or (maxTileX == size -1)) + 1 *((maxTileY == 0) or (maxTileY == size -1))
        return (score, Zscore, tileDist, maxTile, maxTileCornerDist, binaryTilesDistance)

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
        (score, Zscore, tileDist, maxTile, maxTileCornerDist, binaryTilesDistance) = self.analyze()
        w1 = 1
        w2 = 0 #maxTile / 4
        w3 = 1
        w4 = 50
        wh = 1
        heuristic = w1 * Zscore + int(w2 * (2 + maxTileCornerDist)) + (w3 * tileDist) + (w4 * binaryTilesDistance)
        k = min(score/4096,1)
        e = k * maxTile + (1-k) * heuristic * wh
        if printH:
            a=[0,0,0,0]
            a[0] = (w1 * Zscore)
            a[1] = int(w2 * (2 + maxTileCornerDist)) 
            a[2] = (w3 * tileDist)
            a[3] = w4 * binaryTilesDistance
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
            # c.append(State(g4, move = self.move, depth = self.depth +1))
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
        self.timer.start()
        self.IDSDepth = 3
        self.totalNodes = 0
        self.totalLeaves = 0
        self.maxSuperChild = None
        while not self.stopFlag:
            self.numberOfNodes = 0
            self.numberOfLeaves = 0
            self.maxChild = None
            self.maxUtility = -maxint
            self.maximize0(State(grid), self.IDSDepth)
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
        # print("returned at : %.2f" %elapsed)
        return self.maxSuperChild.move

    def minimize(self, state, maxDepth, alpha, beta):
        available = state.grid.getAvailableCells()
        if available == []:
            self.numberOfLeaves += 1
            return (None, state.grid.getMaxTile())
        
        (minChild, minUtility) = (None, maxint)
        for child in state.childrenComputer(available):
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | " + str(child.analyze()) +" eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
                # print i
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
                # print("pruning with alpha")
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
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | " + str(child.analyze()) +" eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
                # print i
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

    def maximize0(self, state, maxDepth):
        moves = state.grid.getAvailableMoves()
        if moves == []:
            self.numberOfLeaves += 1
            return

        for child in state.childrenPlayer(moves):
            # print("exploring move %d" %child.move)
            # print("depth :" + str(child.depth) +" move :" + str(child.move) +" | " + str(child.analyze()) +" eval: " + str(child.eval(True))+"\n")
            # for i in child.grid.map:
                # print i
            # print("\n")
            self.numberOfNodes +=1
            if child.depth == maxDepth:
                utility = child.eval()
            else:
                # print("drilling with alpha = %d and beta = %d" %(self.maxUtility, maxint))
                (_, utility) = self.minimize(child, maxDepth, self.maxUtility, maxint)
            if utility > self.maxUtility:
                # print("new depth %d move found with Utility: %d" %(state.depth, utility))
                (self.maxChild, self.maxUtility) = (child, utility)
            if self.stopFlag:
                break
        
if __name__ == '__main__':
    sGrid = Grid()

    sGrid.map[0] = [0, 2, 8, 16]
    sGrid.map[1] = [0, 0, 4, 2]
    sGrid.map[2] = [0, 2, 2, 4]
    sGrid.map[3] = [0, 0, 0, 0]


    for i in sGrid.map:
            print i
    print("\n")
    p = PlayerAI()
    s = State(sGrid)
    print(str(s.analyze()) +" eval: " + str(s.eval(True))+"\n")
    print(p.getMove(sGrid))
    visited = set()
    print(State(sGrid).getMaxPath(0,3,visited))