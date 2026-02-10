import heapq

# ----- Some Random Leftover Helper Functions that I Might Want to Use Later, Delete Later if not -----
def display2DArray(arr):
    for row in arr:
        print(row)

def distanceBetween(rowIndex1, colIndex1, rowIndex2, colIndex2): #Moved as a helper function in Node Class for Manhattan Distance calc function to use
    return abs(rowIndex1 - rowIndex2) + abs(colIndex1 - colIndex2)

# ----- Node Class -----
# parent node of child (set to None for Root node)
# state is a 2D array: [[ 1,  2,  3 ],
                    #   [ 4,  5,  6 ],
                    #   [ 7,  8,  0 ]]
# depth is how the number of moves needed to reach this node
# fn = depth (gn) + heuristic (hn)
# herusticType: 0 - Misplaced Tile, 1 - Manhattan Distance, Other - None
class Node:
    def __init__(self, parent, state, depth, heuristicType, goalState):
        self.parent = parent
        self.state = state
        self.depth = depth
        self.heuristicType = heuristicType
        self.goalState = goalState

        self.hn = self._calculateHn()
        self.fn = self.depth + self.hn

    # Misplaced Tiles Heuristic: Number of tiles not in their goal positions
    def _getMisplacedTileCount(self):
        heuristicValue = 0
        for rowIndex in range(len(self.state)):
            for colIndex in range(len(self.state[0])):
                value = self.state[rowIndex][colIndex]
                if value != 0 and value != self.goalState[rowIndex][colIndex]:
                    heuristicValue += 1
        return heuristicValue
    
    # Manhattan Distance Heuristic: Summation of distance of each tile's position from their goal positions
    def _getManhattanDistance(self):
        goalPos = {}
        for rowIndex in range(len(self.goalState)):
            for colIndex in range(len(self.goalState[0])):
                goalPos[self.goalState[rowIndex][colIndex]] = (rowIndex, colIndex)

        heuristicValue = 0
        for rowIndex in range(len(self.state)):
            for colIndex in range(len(self.state[0])):
                value = self.state[rowIndex][colIndex]
                if value == 0:
                    continue
                goalRowIndex, goalColIndex = goalPos[value]
                heuristicValue += abs(rowIndex - goalRowIndex) + abs(colIndex - goalColIndex)
        return heuristicValue

    # Calculate Hn using the correct heuristic method requested
    def _calculateHn(self):
        if self.heuristicType == -1:
            return 0
        elif self.heuristicType == 0:
            return self._getMisplacedTileCount()
        elif self.heuristicType == 1:
            return self._getManhattanDistance()
        else:
            return 0

    # Returns where 0 is in a state (defaults to self.state)
    def _emptySquareCoords(self, state=None):
        if state is None:
            state = self.state
        for rowIndex, rowArr in enumerate(self.state):
            for colIndex, colVal in enumerate(rowArr):
                if colVal == 0:
                    return rowIndex, colIndex
        raise ValueError("No 0 found in state")

    # Helper function to check if a move in a chosen direction is allowed (0 - Up, 1 - Right, 2 - Down, 3 - Left)
    def _tryDirection(self, direction):
        zeroRowIndex, zeroColIndex = self._emptySquareCoords()
        rowCount, colCount = len(self.state), len(self.state[0])
        if direction == 0:
            return zeroRowIndex != 0 #Can it go further [ Up ] from upmost row?
        elif direction == 1:
            return zeroColIndex != (colCount-1) #Can it go further [ Right ] from rightmost column?
        elif direction == 2:
            return zeroRowIndex != (rowCount-1) #Can it go further [ Down ] from downmost row?
        elif direction == 3:
            return zeroColIndex != 0 #Can it go further [ Left ] from leftmost column?
        else:
            raise ValueError("direction must be 0..3")
        
    # Swaps the values of squares 
    def _swapSquares(self, arr, rowIndex1, colIndex1, rowIndex2, colIndex2):
        saveNum = arr[rowIndex1][colIndex1]
        arr[rowIndex1][colIndex1] = arr[rowIndex2][colIndex2]
        arr[rowIndex2][colIndex2] = saveNum
    
    # Helper function to move empty square in a chosen direction (0 - Up, 1 - Right, 2 - Down, 3 - Left)
    # Returns a new Array/State
    # ONLY USE AFTER HAVING CALLED _tryDirection
    def _moveEmptySquare(self, arr, direction):
        newArr = [row[:] for row in arr]
        rowIndex, colIndex = self._emptySquareCoords()

        if direction == 0: #Up
            self._swapSquares(newArr, rowIndex, colIndex, rowIndex-1, colIndex)
        elif direction == 1: #Right
            self._swapSquares(newArr, rowIndex, colIndex, rowIndex, colIndex+1)
        elif direction == 2: #Down
            self._swapSquares(newArr, rowIndex, colIndex, rowIndex+1, colIndex)
        elif direction == 3: #Left
            self._swapSquares(newArr, rowIndex, colIndex, rowIndex, colIndex-1)
        else:
            raise ValueError("direction must be 0..3")
        return newArr

    #Try moving node in each direction, return array of possible children
    def generateChildren(self):
        children = []
        #Generate child nodes of each possible state (max 4, min 2) that can derive from parent.
        for direction in [0, 1, 2, 3]:
            if self._tryDirection(direction):
                childState = self._moveEmptySquare(self.state, direction)
                child = Node(
                    parent=self,
                    state=childState,
                    depth=self.depth + 1,
                    heuristicType=self.heuristicType,
                    goalState=self.goalState
                )
                children.append(child)
        return children
    
# ----- Problem Class -----
class Problem:
    def __init__(self, initialState, goalState):
        self.INITIAL_STATE = initialState
        self.GOAL_STATE = goalState
        self.OPERATORS = [0, 1, 2, 3]  # Up, Right, Down, Left

    def GOAL_TEST(self, state):
        return state == self.GOAL_STATE


# ----- Main -----
if __name__ == '__main__':
    
