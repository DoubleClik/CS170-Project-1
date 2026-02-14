import heapq
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ----- Helper Functions -----
def printLargeGap():
    # for _ in range(50):
    #     print()
    output = ""

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
    # Find largest number for formatting width
    largest = 0
    for row in state:
        for value in row:
            if value > largest:
                largest = value

    longestNumLen = len(str(largest))
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

# CREDIT: https://www.geeksforgeeks.org/dsa/check-instance-8-puzzle-solvable/
    # For the idea to count inversions to prove/disprove solvability
    # And this really good statement: "It is not possible to solve an instance of 8 puzzle if number of inversions is odd in the input state."
    # My implementation of isSolvable is a heavily modified version of geeksforgeeks'. (Used geeksforgeeks' isSolvable function as a starting point,
    # after which I modified it to work for any n by n sized puzzle state)
def isSolvable(n, state):
    flatList = []
    blankRowIndex = 0

    # Flatten state into a list (ignore 0)
    for rowIndex in range(n):
        for colIndex in range(n):
            value = state[rowIndex][colIndex]
            if value == 0:
                blankRowIndex = rowIndex
            else:
                flatList.append(value)

    # Count inversions
    inversionCount = 0
    for firstIndex in range(len(flatList)):
        for secondIndex in range(firstIndex + 1, len(flatList)):
            if flatList[firstIndex] > flatList[secondIndex]:
                inversionCount += 1

    # Row counting from bottom (1-based)
    blankRowFromBottom = n - blankRowIndex

    if n % 2 == 1:
        return inversionCount % 2 == 0
    else:
        return (inversionCount + blankRowFromBottom) % 2 == 1


def validateInitialState(n, initState):

    # Check dimensions
    if len(initState) != n:
        print("Invalid: Incorrect number of rows.")
        return False

    for row in initState:
        if len(row) != n:
            print("Invalid: Incorrect number of columns.")
            return False

    flatList = []
    for rowIndex in range(n):
        for colIndex in range(n):
            value = initState[rowIndex][colIndex]

            if not isinstance(value, int):
                print("Invalid: All entries must be integers.")
                return False

            flatList.append(value)

    validValues = set(range(n * n))

    if set(flatList) != validValues:
        print("Invalid: Must contain all values from 0 to", n*n - 1, "exactly once.")
        return False

    if not isSolvable(n, initState):
        print("Invalid: Puzzle is not solvable.")
        return False

    return True

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
    nodesExpanded = 0

    # loop do
    while True:
        # if EMPTY(nodes) then return "failure"
        if EMPTY(nodes):
            return None, nodesExpanded
        
        # node = REMOVE-FRONT(nodes)
        node = REMOVE_FRONT(nodes)

        # if problem.GOAL-TEST(node.STATE) succeeds then return node
        if problem.GOAL_TEST(node.state):
            return node, nodesExpanded

        k = stateKey(node.state)
        if k in visited:
            continue
        visited.add(k)

        # This node is being expanded now
        nodesExpanded += 1

        # nodes = QUEUEING-FUNCTION(nodes, EXPAND(node, problem.OPERATORS))
        children = node.generateChildren()
        nodes, tieCounter = QUEUEING_FUNCTION(nodes, tieCounter, children)

# ----- Path reconstruction -----
def reconstructPath(goalNode):
    path = []
    currentNode = goalNode
    while currentNode is not None:
        path.append(currentNode)   # store the node itself
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
    printGrid(arr, barLength, n, longestNumLen)

    initArr = tuple(tuple(row) for row in arr)
    if not validateInitialState(n, initArr):
        raise ValueError("Invalid initial state entered, please try again.")
    
    heuristicType = int(input("Which heuristic would you like to use: Misplaced Tile [0], Manhattan Distance [1], or None [2]: "))
    goalArr = generateGoalState(n)

    return initArr, goalArr, heuristicType

# ----- Run Test Cases -----
def buildRuntimeVsDepthData():
    # Goal state (standard 3 by 3)
    goalArr = (
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 0)
    )

    # Test cases taken from instructions
    testCases = [
        (0,  ((1, 2, 3),
              (4, 5, 6),
              (7, 8, 0))),

        (2,  ((1, 2, 3),
              (4, 5, 6),
              (0, 7, 8))),

        (4,  ((1, 2, 3),
              (5, 0, 6),
              (4, 7, 8))),

        (8,  ((1, 3, 6),
              (5, 0, 2),
              (4, 7, 8))),

        (12, ((1, 3, 6),
              (5, 0, 7),
              (4, 8, 2))),

        (16, ((1, 6, 7),
              (5, 0, 3),
              (4, 8, 2))),

        (20, ((7, 1, 2),
              (4, 8, 5),
              (6, 3, 0))),

        (24, ((0, 7, 2),
              (4, 6, 1),
              (3, 5, 8))),
    ]

    algorithmConfigs = [
        ("UCS", -1),
        ("A* Misplaced", 0),
        ("A* Manhattan", 1),
    ]

    rows = []

    for (knownDepth, initArr) in testCases:
        problem = Problem(initArr, goalArr)

        for (algorithmName, heuristicType) in algorithmConfigs:
            start = time.perf_counter()
            goalNode, nodesExpanded = general_search(problem, heuristicType)
            end = time.perf_counter()

            runtimeMs = (end - start) * 1000.0

            # If something goes wrong, don't crash the whole experiment
            if goalNode is None:
                rows.append({
                    "solutionDepth": knownDepth,
                    "runtimeMs": runtimeMs,
                    "nodesExpanded": nodesExpanded,
                    "algorithm": algorithmName,
                    "solved": False
                })
            else:
                rows.append({
                    "solutionDepth": knownDepth,
                    "runtimeMs": runtimeMs,
                    "nodesExpanded": nodesExpanded,
                    "algorithm": algorithmName,
                    "solved": True
                })

    return pd.DataFrame(rows)

# ----- Main -----
if __name__ == '__main__':
    choice = int(input("Would you like to [0] Solve a Puzzle or [1] Generate Test Figures: "))
    if choice == 0:
        initArr, goalArr, heuristicType = promptUser()
  
        problem = Problem(initArr, goalArr)

        start = time.time()

        # A* Misplaced Tile [0], A* Manhattan Distance [1], or Uniform Cost Search or No Heustic [2]
        goalNode, nodesExpanded = general_search(problem, heuristicType)
        # Calculate the end time and time taken
        end = time.time()
        length = end - start

        if goalNode is None:
            print("Inputted Puzzle Arrangement is Invalid")
        else:
            path = reconstructPath(goalNode)
            for node in path:
                printLargeGap()
                displayState(node.state)

                # g(n) is depth, h(n) is the heuristic value stored on the node
                print(f"g(n) = {node.depth} | h(n) = {node.hn} | f(n) = {node.fn}")

                time.sleep(.25)

        print("Nodes Expanded:", nodesExpanded)
        print("Search took", round(length * 1000, 2), "ms")
    elif choice == 1:
        df = buildRuntimeVsDepthData()

        # Optional: filter out failures if any
        df = df[df["solved"] == True]

        # ----- Table 1: Runtime vs Solution Depth -----
        runtimeTable = (
            df.pivot_table(
                index="solutionDepth",
                columns="algorithm",
                values="runtimeMs",
                aggfunc="mean"
            )
            .sort_index()
            .round(3)
        )

        print("\n----- Runtime (ms) vs Solution Depth -----")
        print(runtimeTable.to_string())

        # ----- Table 2: Nodes Expanded vs Solution Depth -----
        nodesExpandedTable = (
            df.pivot_table(
                index="solutionDepth",
                columns="algorithm",
                values="nodesExpanded",
                aggfunc="mean"
            )
            .sort_index()
        )

        print("\n----- Nodes Expanded vs Solution Depth -----")
        print(nodesExpandedTable.to_string())

        # ----- Figure 1: Runtime vs Solution Depth -----
        plt.figure()
        sns.lineplot(data=df, x="solutionDepth", y="runtimeMs", hue="algorithm", marker="o")
        plt.xlabel("Solution Depth")
        plt.ylabel("Runtime (ms)")
        plt.title("Runtime vs Solution Depth (8-Puzzle)")
        plt.show()

        # ----- Figure 2: Nodes Expanded vs Solution Depth -----
        plt.figure()
        sns.lineplot(data=df, x="solutionDepth", y="nodesExpanded", hue="algorithm", marker="o")
        plt.xlabel("Solution Depth")
        plt.ylabel("Nodes Expanded")
        plt.title("Nodes Expanded vs Solution Depth (8-Puzzle)")
        plt.show()

    else:
        print("Sorry, that choice was invalid.")
