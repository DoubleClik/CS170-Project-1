import heapq
import time

# ----- Helper Functions -----
def printLargeGap():
    for _ in range(50):
        print()

def printBar(barLength):
    output = ""
    for _ in range(barLength):
        output += "-"
    print(output)

def formatNumAndSpace(num, longestNumLen):
    numSpaces = longestNumLen - len(str(num))
    output = ""

    for _ in range(numSpaces):
        output += " "

    output += str(num)
    return output

def printGrid(state, barLength, n, longestNumLen):
    for row in state:
        printBar(barLength)
        output = "|"
        for i in range(0,n):
            if row[i] is None:
                for i in range(longestNumLen):
                    output += " "
            else:
                output += formatNumAndSpace(row[i], longestNumLen)
            output += "|"
        print(output)
    printBar(barLength)

def displayState(state):
    longestNumLen = len(str(state[0][0]))
    n = len(state)
    barLength = (n+1) + (longestNumLen*n)

    printGrid(state, barLength, n, longestNumLen)

def generateGoalState(n):
    if n <= 1:
        return None

    goal = []
    value = 1

    for rowIndex in range(n):
        row = []
        for colIndex in range(n):
            if rowIndex == n - 1 and colIndex == n - 1:
                row.append(0)
            else:
                row.append(value)
                value += 1
        goal.append(tuple(row))

    return tuple(goal)

# Returns hashable key for states already visited
# NOTE: State is stored as tuple-of-tuples
def stateKey(state):
    return state

# ----- Node Class -----
# herusticType: 0 - Misplaced Tile, 1 - Manhattan Distance, Other - None
class Node:
    def __init__(self, parent, state, depth, heuristicType, goalState):
        self.parent = parent
        self.state = state # Tuple-of-tuples
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
        for rowIndex, rowArr in enumerate(state):
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
    # ONLY USE AFTER HAVING CALLED _tryDirection
    # NOTE: arr is expected to be passed in as tuple-of-tuples; converted to mutable, then back to tuple-of-tuples at end to be returned
    def _moveEmptySquare(self, arr, direction):
        newArr = [list(row) for row in arr]
        rowIndex, colIndex = self._emptySquareCoords(newArr)

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

        return tuple(tuple(row) for row in newArr)

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

# ----- User Prompter -----


def promptUser():
    n = input("Enter Puzzle Dimensions [n by n]. n: ")

    n = int(n)
    longestNumLen = len(str(n*n-1))
    barLength = (n+1) + (longestNumLen*n)
    arr = [[None for _ in range(n)] for _ in range(n)]

    for rowIndex in range(0,n):
        for colIndex in range(0,n):
                printGrid(arr, barLength, n, longestNumLen)
                value = input(f'Enter Value for Row {rowIndex+1}, Column {colIndex+1}: ')
                arr[rowIndex][colIndex] = int(value)
                printLargeGap()
    
    initArr = tuple(tuple(row) for row in arr)
    goalArr = generateGoalState(n)

    return initArr, goalArr

#FIXME: promptUser() input validation, innitArr input validation, improve code readibility, write report, check code and report at office hours
# ----- Main -----
if __name__ == '__main__':

    initArr, goalArr = promptUser()
  
    problem = Problem(initArr, goalArr)

    start = time.time()
    
    # 1) Uniform Cost Search
    # goalNode = general_search(problem, heuristicType=-1)

    # 2) A* Misplaced
    # goalNode = general_search(problem, heuristicType=0)

    # 3) A* Manhattan
    goalNode = general_search(problem, heuristicType=1)

    # Calculate the end time and time taken
    end = time.time()
    length = end - start

    if goalNode is None:
        print("failure")
    else:
        path = reconstructPath(goalNode)
        i = 0
        for s in path:
            printLargeGap()
            displayState(s)
            print(f'Depth: {i}')
            i+=1
            time.sleep(.5)
        print(f"Solved in {len(path)-1} moves")

    print("Search took", length * 1000, "ms")
