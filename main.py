import heapq

# ----- Helper Functions -----
def display2DArray(arr):
    for row in arr:
        print(row)

# Returns hashable key for states already visited
def stateKey(state):
    return tuple(tuple(row) for row in state)

# ----- Node Class -----
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

# ----- Queue Helpers -----
def MAKE_QUEUE(rootNode):
    nodes = []
    tie = 0
    heapq.heappush(nodes, (rootNode.fn, tie, rootNode))
    return nodes, tie

def EMPTY(nodes):
    return len(nodes) == 0

def REMOVE_FRONT(nodes):
    return heapq.heappop(nodes)[2]

# QUEUEING_FUNCTION: insert newNodes into heap
def QUEUEING_FUNCTION(nodes, tieCounter, newNodes):
    for n in newNodes:
        tieCounter += 1
        heapq.heappush(nodes, (n.fn, tieCounter, n))
    return nodes, tieCounter

# ----- General Search Algorithm -----
def general_search(problem, heuristicType):
    # nodes = MAKE-QUEUE(MAKE-NODE(problem.INITIAL-STATE))
    root = Node(None, problem.INITIAL_STATE, 0, heuristicType, problem.GOAL_STATE)
    nodes, tieCounter = MAKE_QUEUE(root)

    visited = set()  # avoid re-expanding previously explored states

    # loop do
    while True:
        # if EMPTY(nodes) then return "failure"
        if EMPTY(nodes):
            return None
        
        # node = REMOVE-FRONT(nodes)
        node = REMOVE_FRONT(nodes)

        # if problem.GOAL-TEST(node.STATE) succeeds then return node
        if problem.GOAL_TEST(node.state):
            return node

        k = stateKey(node.state)
        if k in visited:
            continue
        visited.add(k)

        # nodes = QUEUEING-FUNCTION(nodes, EXPAND(node, problem.OPERATORS))
        children = node.generateChildren()
        nodes, tieCounter = QUEUEING_FUNCTION(nodes, tieCounter, children)

# ----- Path reconstruction -----
def reconstructPath(goalNode):
    path = []
    currentNode = goalNode
    while currentNode is not None:
        path.append(currentNode.state)
        currentNode = currentNode.parent
    return list(reversed(path))


#FIXME: Needs better result display, initial and goal state inputs, validation for those inputs, timers and comparisons (maybe multiple trials, averages, ect. make it experimental kind of), bugfix anything ig, improve code readibility, write report, check code and report at office hours
# ----- Main -----
if __name__ == '__main__':
    #FIXME: Enter Initial State Function (Hardcoded for now)
    initArr = ([[0, 7, 2],
                [4, 6, 1],
                [3, 5, 8,]])
        
    #FIXME: Enter Goal State Function (Hardcoded for now)
    goalArr = ([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 0,]])
    
    problem = Problem(initArr, goalArr)
    
    # 1) Uniform Cost Search
    # goalNode = general_search(problem, heuristicType=-1)

    # 2) A* Misplaced
    # goalNode = general_search(problem, heuristicType=0)

    # 3) A* Manhattan
    goalNode = general_search(problem, heuristicType=1)

    if goalNode is None:
        print("failure")
    else:
        path = reconstructPath(goalNode)
        for s in path:
            display2DArray(s)
            print()
        print(f"Solved in {len(path)-1} moves")