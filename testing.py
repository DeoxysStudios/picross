from gameobjects import Game, STATES
import unittest

TESTBOARD: list[list[int]] = [
    [0, 0,  0,  0],
    [0, 0,  0,  0],
    [0, 0,  0,  0],
    [0, 0,  0,  0]
]
TESTROWNUMS: list[list[int]] = [
    [1, 1],
    [2],
    [1],
    [3]
]
TESTCOLNUMS: list[list[int]] = [
    [1, 1],
    [1, 1],
    [3],
    [1]
]
VISUALS: dict[int, str] = {
    STATES["UNKNOWN"]: "?",
    STATES["FLAGGED"]: "X",
    STATES["MINED"]: "O"
}

def printBoard(board: list[list[int]]):
    for y in range(len(board[0])):
        for x in range(len(board)):
            print(VISUALS[board[x][y]], end = "")
        print("")
        
newBoard = Game.solveBoard(TESTBOARD, TESTROWNUMS, TESTCOLNUMS)
printBoard(newBoard)
print(Game.fillRow([0, 0, 0, -1, 0], [2, 1]))