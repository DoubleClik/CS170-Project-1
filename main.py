class ProblemSpace(object):
    #FIXME: Goal state is hard-coded, make it dynamic to match the size of initial state later (currently expects a 3 by 3 2D array). Also add bad-input handling
    def __init__(self, initialState):
        self.currentState = initialState
        self.rowMax = 2 #(highest array row index)
        self.colMax = 2 #(highest array col index)
        self.goalState = [[ 1,  2,  3 ], #Hardcoded, change later
                          [ 4,  5,  6 ],
                          [ 7,  8,  0 ]]
    
    #Returns where 0 is in currentState
    def _emptySquareCoords(self):
        for rowIndex, rowArr in enumerate(self.currentState):
            for colIndex, colVal in enumerate(rowArr):
                if colVal == 0:
                    return rowIndex, colIndex
    
    #Swaps the values of squares 
    def _swapSquares(self, rowIndex1, colIndex1, rowIndex2, colIndex2):
        saveNum = self.currentState[rowIndex1][colIndex1]
        self.currentState[rowIndex1][colIndex1] = self.currentState[rowIndex2][colIndex2]
        self.currentState[rowIndex2][colIndex2] = saveNum
    
    def moveEmptySquareLeft(self):
        rowIndex, colIndex = self._emptySquareCoords()
        if colIndex == 0:
            print("Cannot move empty square left.")
            return False
        
        self._swapSquares(rowIndex, colIndex, rowIndex, colIndex-1)
        return True

def display2DArray(arr):
    for row in arr:
        print(row)

def distanceBetween(rowIndex1, colIndex1, rowIndex2, colIndex2):
    return abs(rowIndex1 - rowIndex2) + abs(colIndex1 - colIndex2)

#FIXME: Hardcoded to 3 by 3, find a way to dynamically give provide goalState coords
def getManhattanDistance(arr):
    heuristic = 0

    for rowIndex, rowArr in enumerate(arr):
        for colIndex, colVal in enumerate(rowArr):
            if( colVal == 0 ):
                heuristic += distanceBetween(rowIndex, colIndex, 2, 2)
            elif( colVal == 1 ):
                heuristic += distanceBetween(rowIndex, colIndex, 0, 0)
            elif( colVal == 2 ):
                heuristic += distanceBetween(rowIndex, colIndex, 1, 0)
            elif( colVal == 3 ):
                heuristic += distanceBetween(rowIndex, colIndex, 2, 0)
            elif( colVal == 4 ):
                heuristic += distanceBetween(rowIndex, colIndex, 0, 1)
            elif( colVal == 5 ):
                heuristic += distanceBetween(rowIndex, colIndex, 1, 1)
            elif( colVal == 6 ):
                heuristic += distanceBetween(rowIndex, colIndex, 2, 1)
            elif( colVal == 7 ):
                heuristic += distanceBetween(rowIndex, colIndex, 0, 2)
            elif( colVal == 8 ):
                heuristic += distanceBetween(rowIndex, colIndex, 1, 2)

    return heuristic

# ----- Main -----
if __name__ == '__main__':
    arr = ([[0, 7, 2],
            [4, 6, 1],
            [3, 5, 8,]])
    
    problemSpace = ProblemSpace(arr)
    
    print("Display arr and try to move it left (should fail)")
    display2DArray(problemSpace.currentState)
    problemSpace.moveEmptySquareLeft()

    print("Swap the top left and bottom middle")
    problemSpace._swapSquares(0,0,2,1)
    display2DArray(problemSpace.currentState)

    print("Print where the empty square is, move the empty square to the left, should swap 0 and 3")
    row, col = problemSpace._emptySquareCoords()
    print(f"Row: {row}, Col: {col}")
    problemSpace.moveEmptySquareLeft()
    display2DArray(problemSpace.currentState)

    row, col = problemSpace._emptySquareCoords()
    print(f"Row: {row}, Col: {col}")
