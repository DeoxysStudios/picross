from gameobjects import Game, STATES
import unittest

TESTBOARD = [
    [-1, -1, 0, -1, 0],
    [-1, -1, 1, -1, 1],
    [-1, -1, 0, 1, 0],
    [0, -1, 0, -1, -1],
    [0, -1, 0, -1, -1]
]

SOLUTION = [
    [-1, -1, 0, -1, 0],
    [-1, -1, 1, -1, 1],
    [-1, -1, 0, 1, 0],
    [0, -1, 0, -1, -1],
    [0, -1, 1, -1, -1]
]

COUNTERBOARD = [
    [-1, -1, 0, -1, 0],
    [-1, -1, 1, -1, 1],
    [-1, -1, 0, 1, 0],
    [0, -1, 0, -1, -1],
    [0, -1, -1, -1, -1]
]

TESTROWS = [
    [1],
    [0],
    [2, 1],
    [1],
    [2]
]

TESTCOLS = [
    [1],
    [1, 1],
    [2],
    [1],
    [1]
]


board1 = Game.solveBoard(TESTROWS, TESTCOLS, SOLUTION)
board2 = Game.solveBoard(TESTROWS, TESTCOLS, COUNTERBOARD)
Game.printBoard(board1)
print("-----")
Game.printBoard(board2)
print(Game.boardIsSolvable(TESTROWS, TESTCOLS, COUNTERBOARD))