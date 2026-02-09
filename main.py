import heapq

# ----- Some Random Leftover Helper Functions that I Might Want to Use Later, Delete Later if not -----
def display2DArray(arr):
    for row in arr:
        print(row)

def distanceBetween(rowIndex1, colIndex1, rowIndex2, colIndex2): #Moved as a helper function in Node Class for Manhattan Distance calc function to use
    return abs(rowIndex1 - rowIndex2) + abs(colIndex1 - colIndex2)

# parent node of child (set to None for Root node)
# state is a 2D array: [[ 1,  2,  3 ],
                    #   [ 4,  5,  6 ],
                    #   [ 7,  8,  0 ]]
# depth is how the number of moves needed to reach this node
# fn = depth (gn) + heuristic (hn)
# herusticType: 0 - Misplaced Tile, 1 - Manhattan Distance, Other - None
class Node:
    def __init__(self, parent, state, depth, heuristicType):
        self.parent = parent
        self.state = state
        self.depth = depth
        self.heuristicType = heuristicType
        self.fn = self._calculateFn(heuristicType)

    #FIXME/WARN: Only works if goal state has all the numbers ascending from left to right, top to bottom, with 0 at the end. Change if other goal states are wanted
    def _getMisplacedTileCount(self, arr):
        heuristic = (len(arr) * len(arr[0])) - 1 # (RowCount * ColCount) - 1 or Num tiles excluding 0
        idealValue = 1

        for rowIndex, rowArr in enumerate(arr):
            for colIndex, colVal in enumerate(rowArr):
                if( colVal != 0 and colVal == idealValue ):
                    heuristic -= 1
                idealValue += 1
        return heuristic
    
    def _distanceBetween(self, rowIndex1, colIndex1, rowIndex2, colIndex2):
        return abs(rowIndex1 - rowIndex2) + abs(colIndex1 - colIndex2)

    #FIXME: Hardcoded to 3 by 3, find a way to dynamically give provide goalState coords
    def _getManhattanDistance(self,arr):
        heuristic = 0

        for rowIndex, rowArr in enumerate(arr):
            for colIndex, colVal in enumerate(rowArr):
                if( colVal == 1 ):
                    heuristic += self._distanceBetween(rowIndex, colIndex, 0, 0)
                elif( colVal == 2 ):
                    heuristic += self._distanceBetween(rowIndex, colIndex, 1, 0)
                elif( colVal == 3 ):
                    heuristic += self._distanceBetween(rowIndex, colIndex, 2, 0)
                elif( colVal == 4 ):
                    heuristic += self._distanceBetween(rowIndex, colIndex, 0, 1)
                elif( colVal == 5 ):
                    heuristic += self._distanceBetween(rowIndex, colIndex, 1, 1)
                elif( colVal == 6 ):
                    heuristic += self._distanceBetween(rowIndex, colIndex, 2, 1)
                elif( colVal == 7 ):
                    heuristic += self._distanceBetween(rowIndex, colIndex, 0, 2)
                elif( colVal == 8 ):
                    heuristic += self._distanceBetween(rowIndex, colIndex, 1, 2)
            return heuristic

    def _calculateFn(self, heuristicType):
        if heuristicType == 0:
            return self.depth + self._getMisplacedTileCount(self.state)
        elif heuristicType == 1:
            return self.depth + self._getManhattanDistance(self.state)
        else:
            return self.depth

    #Returns where 0 is in state
    def _emptySquareCoords(self):
        for rowIndex, rowArr in enumerate(self.state):
            for colIndex, colVal in enumerate(rowArr):
                if colVal == 0:
                    return rowIndex, colIndex

    #Helper function to check if a move in a chosen direction is allowed (0 - Up, 1 - Right, 2 - Down, 3 - Left)
    def _tryDirection(self, direction):
        zeroRowIndex, zeroColIndex = self._emptySquareCoords()
        if direction == 0:
            return zeroRowIndex != 0 #Can it go further Up from upmost row?
        elif direction == 1:
            return zeroColIndex != (len(self.state[zeroRowIndex])-1) #Can it go further Right from rightmost column?
        elif direction == 2:
            return zeroRowIndex != (len(self.state)-1) #Can it go further Down from downmost row?
        elif direction == 3:
            return zeroColIndex != 0 #Can it go further Left from leftmost column?
        else:
            raise ValueError("direction must be 0..3")
        
    #Swaps the values of squares 
    def _swapSquares(self, arr, rowIndex1, colIndex1, rowIndex2, colIndex2):
        saveNum = arr[rowIndex1][colIndex1]
        arr[rowIndex1][colIndex1] = arr[rowIndex2][colIndex2]
        arr[rowIndex2][colIndex2] = saveNum
    
    #Helper function to move empty square in a chosen direction (0 - Up, 1 - Right, 2 - Down, 3 - Left)
    #ONLY USE AFTER HAVING CALLED _tryDirection
    def _moveEmptySquare(self, arr, direction):
        rowIndex, colIndex = self._emptySquareCoords()
        if direction == 0: #Up
            self._swapSquares(arr, rowIndex, colIndex, rowIndex-1, colIndex)
        elif direction == 1: #Right
            self._swapSquares(arr, rowIndex, colIndex, rowIndex, colIndex+1)
        elif direction == 2: #Down
            self._swapSquares(arr, rowIndex, colIndex, rowIndex+1, colIndex)
        elif direction == 3: #Left
            self._swapSquares(arr, rowIndex, colIndex, rowIndex, colIndex-1)
        else:
            raise ValueError("direction must be 0..3")

    #Try moving node in each direction, return array of possible children
    def generateChildren(self):
        children = []
        i = 0
        #Generate child nodes of each possible state (max 4, min 2) that can derive from parent.
        while i < 4:
            if self._tryDirection(i):
                newState = self.state
                self._moveEmptySquare(newState, i)
                child = Node(newState, self, self.depth + 1, self.heuristicType)
                children.append(child)
            i += 1
        
        return children

# ----- Main -----
if __name__ == '__main__':
    arr = ([[0, 7, 2],
            [4, 6, 1],
            [3, 5, 8,]])
    
