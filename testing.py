from gameobjects import Game, STATES
import unittest

TESTROWNUMS: list[list[int]] = [
    [2],
    [1, 2],
    [3],
    [3],
    [1, 2]
]
TESTCOLNUMS: list[list[int]] = [
    [2, 1],
    [1, 1],
    [1, 3],
    [1, 2],
    [1, 1]
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
    return

newBoard = Game.solveBoard(TESTROWNUMS, TESTCOLNUMS)
printBoard(newBoard)
print(f"is valid: {Game.validateBoard(TESTROWNUMS, TESTCOLNUMS)}")
printBoard(Game.generateBoard())