from gasp import games # type: ignore
from gasp import boards # type: ignore
from gasp import color # type: ignore
import random
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('width', default = 15, type = int, nargs = '?')
parser.add_argument('height', default = 15, type = int, nargs = '?')
parser.add_argument('difficulty', default = 0.6, type = float, nargs = '?')
args = parser.parse_args()
WIDTH: int = args.width
HEIGHT: int = args.height
PADDING_RIGHT: int = 3
PADDING_BOTTOM: int = 3
MAXSIZE: int = max(2 * WIDTH - WIDTH // 2 + PADDING_RIGHT, 2 * HEIGHT - HEIGHT // 2 + PADDING_BOTTOM)
BOX_SIZE: int = 800 // MAXSIZE
MARGIN_LEFT: int = (WIDTH + 1) // 2 * BOX_SIZE
MARGIN_TOP: int = (HEIGHT + 1) // 2 * BOX_SIZE
MARGIN_RIGHT: int = BOX_SIZE * PADDING_RIGHT
MARGIN_BOTTOM: int = BOX_SIZE * PADDING_BOTTOM
FILL_PERCENT: float = args.difficulty
MAX_MISTAKES: int = 3
LARGE_OUTLINE_THICKNESS: int = 2
MAX_GENERATE_ATTEMPTS: int = 64
MAX_UNKNOWN_TOLERANCE: int = 8
DIFFICULTY_INCREMENT: float = 0.05
HEALTH_ICON: str = "X"
COLORS = {
    "UNKNOWN" : color.WHITE,
    "MINED" : color.BLUE,
    "FLAGGED" : color.LIGHTGRAY,
    "MISTAKE" : color.RED,
    "FLAG" : color.GRAY,
    "NUMS" : color.WHITE,
    "CROSSOUT" : color.GRAY,
    "WIN" : color.YELLOW,
    "LOSE" : color.RED,
    "GRID" : color.BLACK,
    "HEALTH" : color.RED,
    "PROGRESS" : color.GREEN,
    "SPECIAL" : color.YELLOW
}
STATES = {
    "UNKNOWN" : 0,
    "MINED" : 1,
    "FLAGGED" : -1
}
VISUALS: dict[int, str] = {
    STATES["UNKNOWN"]: "?",
    STATES["FLAGGED"]: "X",
    STATES["MINED"]: "O"
}

class Tile(boards.GameCell):
    
    def __init__(self, board: "Game", i: int, j: int, mineable: bool):
        self.board: Game = board
        self.i, self.j = i, j
        self.mineable: bool = mineable
        self.changeable: bool = True
        self.state: int = STATES["UNKNOWN"]
        self.init_gamecell(board, i, j)
        self.set_color(COLORS["UNKNOWN"])
        x, y = self.board.cell_to_coords(self.i, self.j)
        self.mark = games.Text(self.board, x + BOX_SIZE / 2, y + BOX_SIZE / 2, "", BOX_SIZE, COLORS["FLAG"], None, 1)
        
        
    def handleMistake(self) -> None:
        self.board.health -= 1
        if self.mineable:
            self.mine()
        else:
            self.flag()
        self.mark.set_color(COLORS["MISTAKE"])
        self.mark.set_text("X")
        self.changeable = False
        self.board.updateBoard()
        return
    
    
    def mine(self) -> None:
        # Handle unchangeable tiles
        if not self.changeable:
            return
        
        # Handle flagged tiles
        if self.state == STATES["FLAGGED"]:
            return
        
        # Handle mistake
        if not self.mineable:
            self.handleMistake()
            return
        
        # Mine this tile
        self.state = STATES["MINED"]
        self.changeable = False
        self.set_color(COLORS["MINED"])
        self.board.handleCrossouts(self.j, self.i)
        self.board.progress += 1
        self.board.updateBoard()
        return
        
    
    def flag(self) -> None:
        # Handle unchangeable tiles
        if not self.changeable:
            return
        
        # Handle mistake
        if self.mineable:
            self.handleMistake()
            return
        
        # Flag this tile
        self.state = STATES["FLAGGED"]
        self.changeable = False
        self.mark.set_text("X")
        self.set_color(COLORS["FLAGGED"])
        self.board.handleCrossouts(self.j, self.i)
        self.board.progress += 1
        self.board.updateBoard()
        return
    
    
    
class Number():
    def __init__(self, board: "Game", i: int, j: int, value: int):
        self.value = value
        self.board = board
        self.i, self.j = i, j
        x, y = self.board.cell_to_coords(self.i, self.j)
        self.text = games.Text(self.board, x + BOX_SIZE / 2, y + BOX_SIZE / 2, str(value), BOX_SIZE, COLORS["NUMS"])
        if (value == 0):
            self.crossout()
        
    def crossout(self) -> None:
        self.text.set_color(COLORS["CROSSOUT"])
        
        
    
    

class Game(boards.SingleBoard):
    
    def __init__(self):
        print("Loading...")
        self.validBoard = Game.generateBoard()
        self.health: int = MAX_MISTAKES
        self.progress: int = 0
        self.lines: list[games.Line] = []
        self.init_singleboard((MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM), WIDTH, HEIGHT, BOX_SIZE)
        self.draw_all_outlines()
        self.grid: list[list[Tile]]
        self.rowNums: list[list[Number]] = []
        self.colNums: list[list[Number]] = []
        self.previous_mouse_positions: set[tuple[int, int]] = set[tuple[int, int]]()
        x1, y1 = self.cell_to_coords(WIDTH - 1, HEIGHT + 2)
        x2, y2 = self.cell_to_coords(0, HEIGHT + 2)
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        self.game_over_text = games.Text(self, x + BOX_SIZE / 2, y + BOX_SIZE / 2, "", BOX_SIZE, COLORS["WIN"])
        x1, y1 = self.cell_to_coords(WIDTH - 1, HEIGHT)
        x2, y2 = self.cell_to_coords(0, HEIGHT)
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        self.hp_text = games.Text(self, x + BOX_SIZE / 2, y + BOX_SIZE / 2, " ".join([HEALTH_ICON] * self.health), BOX_SIZE, COLORS["HEALTH"])
        x1, y1 = self.cell_to_coords(WIDTH - 1, HEIGHT + 1)
        x2, y2 = self.cell_to_coords(0, HEIGHT + 1)
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        self.progress_text = games.Text(self, x + BOX_SIZE / 2, y + BOX_SIZE / 2, "Progress: 0%", BOX_SIZE, COLORS["PROGRESS"])
        self.createLargeOutlines()
        self.handleAllNums()
        
    def new_gamecell(self, i: int, j: int) -> Tile:
        mineable: bool = (self.validBoard[i][j] == STATES["MINED"])
        return Tile(self, i, j, mineable)
    
    def tick(self):
        buttons = self.mouse_buttons()
        digging = buttons[0] or self.is_pressed(32)
        flagging = buttons[2] or self.is_pressed(1073742049)
        button: int = 0
        if not digging and not flagging:
            self.previous_mouse_positions.clear()
            return
        if digging and flagging:
            return
        if flagging:
            button = 2
        x, y = self.mouse_position()
        i, j = self.coords_to_cell(x, y)
        assert isinstance(i, int) and isinstance(j, int)
        if not self.on_board(i, j):
            return
        if (i, j) in self.previous_mouse_positions:
            return
        self.previous_mouse_positions.add((i, j))
        # Left Click
        if button == 0:
            self.grid[i][j].mine()
            return
        
        # Right Click
        if button == 2:
            self.grid[i][j].flag()
            return
        return
    
    def createLargeOutlines(self) -> None:
        for i in range(5, WIDTH, 5):
            x1, y1 = self.cell_to_coords(i, 0)
            x2, y2 = self.cell_to_coords(i, HEIGHT)
            self.lines.append(games.Line(self, 0, 0, [(x1, y1), (x2, y2)], COLORS["GRID"], 0, LARGE_OUTLINE_THICKNESS))
        for j in range(5, HEIGHT, 5):
            x1, y1 = self.cell_to_coords(0, j)
            x2, y2 = self.cell_to_coords(WIDTH, j)
            self.lines.append(games.Line(self, 0, 0, [(x1, y1), (x2, y2)], COLORS["GRID"], 0, LARGE_OUTLINE_THICKNESS))
    
    def handleAllNums(self) -> None:
        for j in range(HEIGHT):
            self.rowNums.append([])
            rowNums = Game.getTileNums(self.getRow(j))
            n = len(rowNums)
            for i in range(n):
                self.rowNums[-1].append(Number(self, i - n, j, rowNums[i]))
                if rowNums[i] > WIDTH // 2:
                    self.rowNums[-1][-1].text.set_color(COLORS["SPECIAL"])
                
        for i in range(WIDTH):
            self.colNums.append([])
            colNums = Game.getTileNums(self.getCol(i))
            m = len(colNums)
            for j in range(m):
                self.colNums[-1].append(Number(self, i, j - m, colNums[j]))
                if colNums[j] > HEIGHT // 2:
                    self.colNums[-1][-1].text.set_color(COLORS["SPECIAL"])
                
        for j in range(HEIGHT):
            if self.rowNums[j][0].value == 0:
                self.grid[0][j].flag()
        for i in range(WIDTH):
            if self.colNums[i][0].value == 0:
                self.grid[i][0].flag()        
             
    def updateBoard(self):
        self.hp_text.set_text(" ".join([HEALTH_ICON] * self.health))
        self.progress_text.set_text(f"Progress: {100 * self.progress // (WIDTH * HEIGHT)}%")
        if self.health == 0:
            self.game_over_text.set_color(COLORS["LOSE"])
            self.game_over_text.set_text("YOU LOST!")
            for i in range(WIDTH):
                for j in range(HEIGHT):
                    self.grid[i][j].changeable = False
        elif self.progress == WIDTH * HEIGHT:
            self.game_over_text.set_text("YOU WIN!")
            
    @staticmethod        
    def solveRow(row: list[int], nums: list[int]) -> list[int]:
        if not Game.tilesAreValid(row, nums):
            raise Exception("Invalid nums for this row")
        
        if nums in [[], [0]]:
            return [STATES["FLAGGED"]] * len(row)
        
        if row[0] == STATES["FLAGGED"]:
            return [STATES["FLAGGED"]] + Game.solveRow(row[1:], nums)
        
        if len(row) == nums[0]:
            return [STATES["MINED"]] * nums[0]
        
        if row[0] == STATES["MINED"]:
            return [STATES["MINED"]] * nums[0] + [STATES["FLAGGED"]] + Game.solveRow(row[nums[0] + 1:], nums[1:])
        
        if not Game.tilesAreValid([STATES["FLAGGED"]] + row[1:], nums):
            return [STATES["MINED"]] * nums[0] + [STATES["FLAGGED"]] + Game.solveRow(row[nums[0] + 1:], nums[1:])
        
        if not Game.tilesAreValid([STATES["MINED"]] + row[1:], nums):
            return [STATES["FLAGGED"]] + Game.solveRow(row[1:], nums)
        
        outrow: list[int] = list()
        blockstr = Game.solveRow([STATES["FLAGGED"]] + row[1:], nums)
        fillstr = Game.solveRow([STATES["MINED"]] + row[1:], nums)
        for i in range(len(row)):
            if fillstr[i] == blockstr[i]:
                outrow.append(fillstr[i])
            else:
                outrow.append(STATES["UNKNOWN"])
        return outrow
            
    @staticmethod
    def tilesAreValid(tile_states: list[int], nums: list[int]) -> bool:
        if nums in [[], [0]]:
            return not STATES["MINED"] in tile_states
        
        if not STATES["UNKNOWN"] in tile_states:
            if not STATES["MINED"] in tile_states:
                return nums in [[], [0]]
            temp1 = tile_states.index(STATES["MINED"])
            if STATES["FLAGGED"] in tile_states[temp1:]:
                temp2 = tile_states.index(STATES["FLAGGED"], temp1)
            else:
                temp2 = len(tile_states)
            if temp2 - temp1 != nums[0]:
                return False
            return Game.tilesAreValid(tile_states[temp2:], nums[1:])
        
        if not STATES["MINED"] in tile_states:
            temp1 = tile_states.index(STATES["UNKNOWN"])
            if STATES["FLAGGED"] in tile_states[temp1:]:
                temp2 = tile_states.index(STATES["FLAGGED"], temp1)
            else:
                temp2 = len(tile_states)
            if temp2 >= temp1 + nums[0]:
                return Game.tilesAreValid(tile_states[temp1 + nums[0] + 1:], nums[1:])
            return Game.tilesAreValid(tile_states[temp2 + 1:], nums)
            
        if tile_states[0] == STATES["FLAGGED"]:
            return Game.tilesAreValid(tile_states[1:], nums)
        if tile_states[0] == STATES["MINED"]:
            if len(tile_states) > nums[0] and tile_states[nums[0]] == STATES["MINED"]:
                return False
            if STATES["FLAGGED"] in tile_states:
                temp = tile_states.index(STATES["FLAGGED"])
            else:
                temp = len(tile_states)
            if temp < nums[0]:
                return False
            return Game.tilesAreValid(tile_states[nums[0] + 1:], nums[1:])
        if len(tile_states) > nums[0] and tile_states[nums[0]] == STATES["MINED"]:
            return Game.tilesAreValid(tile_states[1:], nums)
        if STATES["FLAGGED"] in tile_states:
            temp = tile_states.index(STATES["FLAGGED"])
        else:
            temp = len(tile_states)
        if temp < nums[0]:
            return Game.tilesAreValid(tile_states[temp + 1:], nums)
        if Game.tilesAreValid(tile_states[nums[0] + 1:], nums[1:]):
            return True
        return Game.tilesAreValid(tile_states[1:], nums)
    
    @staticmethod
    def getTileNums(tiles: list[Tile]) -> list[int]:
        outnums: list[int] = []
        total: int = 0
        for tile in tiles:
            if tile.mineable:
                total += 1
            elif total > 0:
                outnums.append(total)
                total = 0
        if total > 0 or len(outnums) == 0:
            outnums.append(total)
        return outnums
    
    @staticmethod
    def getListNums(tiles: list[int]) -> list[int]:
        if STATES["UNKNOWN"] in tiles:
            raise Exception("Can't get list nums for a list with unknown tiles")
        outnums: list[int] = []
        total: int = 0
        for tile in tiles:
            if tile == STATES["MINED"]:
                total += 1
            elif total > 0:
                outnums.append(total)
                total = 0
        if total > 0 or len(outnums) == 0:
            outnums.append(total)
        return outnums
    
    @staticmethod
    def getTileStates(tiles: list[Tile]) -> list[int]:
        outnums: list[int] = []
        for tile in tiles:
            outnums.append(tile.state)
        return outnums
    
    @staticmethod
    def solveBoard(rowNums: list[list[int]], colNums: list[list[int]], board: list[list[int]] | None = None) -> list[list[int]]:
        newBoard: list[list[int]] = list()
        width = len(colNums)
        height = len(rowNums)
        originalBoard: list[list[int]]
        if board == None:
            originalBoard = list()
            for x in range(width):
                originalBoard.append(list())
                for y in range(height):
                    originalBoard[x].append(STATES["UNKNOWN"])
        else:
            originalBoard = board
        
        # Solve Columns
        for x in range(width):
            newBoard.append(Game.solveRow(originalBoard[x], colNums[x]))
            
        # Solve Rows
        for y in range(height):
            currRow: list[int] = list()
            for x in range(width):
                currRow.append(newBoard[x][y])
            newRow = Game.solveRow(currRow, rowNums[y])
            for x in range(width):
                newBoard[x][y] = newRow[x]
        
        # Repeat until more info needed
        if newBoard != originalBoard:
            return Game.solveBoard(rowNums, colNums, newBoard)
        
        # Manage hypotheticals
        total: int = 0
        qx: int = -1
        qy: int = -1
        for x in range(len(colNums)):
            for y in range(len(rowNums)):
                if board[x][y] == STATES["UNKNOWN"]:
                    total += 1
                    qx = x
                    qy = y
        if total > MAX_UNKNOWN_TOLERANCE or total == 0:
            return newBoard
        
        hypoMined: list[list[int]] = list()
        hypoFlagged: list[list[int]] = list()
        for x in range(width):
            hypoMined.append(list())
            hypoFlagged.append(list())
            for y in range(height):
                if (x, y) == (qx, qy):
                    hypoMined[x].append(STATES["MINED"])
                    hypoFlagged[x].append(STATES["FLAGGED"])
                else:
                    hypoMined[x].append(newBoard[x][y])
                    hypoFlagged[x].append(newBoard[x][y])
        if not Game.boardIsValid(rowNums, colNums, hypoMined):
            return Game.solveBoard(rowNums, colNums, hypoFlagged)
        if not Game.boardIsValid(rowNums, colNums, hypoFlagged):
            return Game.solveBoard(rowNums, colNums, hypoMined)
        return newBoard
    
    @staticmethod
    def printBoard(board: list[list[int]]):
        for y in range(len(board[0])):
            for x in range(len(board)):
                print(VISUALS[board[x][y]], end = "")
            print("")
        return
    
    @staticmethod
    def boardIsValid(rowNums: list[list[int]], colNums: list[list[int]], board: list[list[int]] | None = None) -> bool:
        try:
            Game.solveBoard(rowNums, colNums, board)
            return True
        except:
            return False
    
    @staticmethod
    def boardIsSolvable(rowNums: list[list[int]], colNums: list[list[int]], board: list[list[int]] | None = None) -> bool:
        try:
            for col in Game.solveBoard(rowNums, colNums, board):
                if STATES["UNKNOWN"] in col:
                    return False
        except:
            return False
        return True
    
    @staticmethod
    def generateBoard() -> list[list[int]]:
        attempts: int = 1
        currFillPercent: float = FILL_PERCENT
        new_board: list[list[int]] = []
        for i in range(WIDTH):
            new_board.append([])
            for j in range(HEIGHT):
                new_board[-1].append(STATES["MINED"] if random.random() <= currFillPercent else STATES["FLAGGED"])
        while not Game.boardIsSolvable(Game.getListRowNums(new_board), Game.getListColNums(new_board)):
            if attempts == MAX_GENERATE_ATTEMPTS:
                currFillPercent = 1.0 - (1.0 - DIFFICULTY_INCREMENT) * (1.0 - currFillPercent)
                attempts = 0
            attempts += 1
            for i in range(WIDTH):
                for j in range(HEIGHT):
                    new_board[i][j] = STATES["MINED"] if random.random() <= currFillPercent else STATES["FLAGGED"]
        return new_board
    
    @staticmethod
    def getListCol(board: list[list[int]], colIndex: int) -> list[int]:
        return board[colIndex]
    
    @staticmethod
    def getListRow(board: list[list[int]], rowIndex: int) -> list[int]:
        outRow: list[int] = list()
        for col in board:
            outRow.append(col[rowIndex])
        return outRow
    
    @staticmethod
    def getListRowNums(board: list[list[int]]) -> list[list[int]]:
        outList: list[list[int]] = list()
        for y in range(len(board[0])):
            outList.append(Game.getListNums(Game.getListRow(board, y)))
        return outList
    
    @staticmethod
    def getListColNums(board: list[list[int]]) -> list[list[int]]:
        outList: list[list[int]] = list()
        for x in range(len(board)):
            outList.append(Game.getListNums(Game.getListCol(board, x)))
        return outList
    
    def getRow(self, rowIndex: int) -> list[Tile]:
        outRow: list[Tile] = []
        for col in self.grid:
            outRow.append(col[rowIndex])
        return outRow
    
    def getCol(self, colIndex: int) -> list[Tile]:
        return self.grid[colIndex]
    
    def handleCrossouts(self, rowIndex: int, colIndex: int) -> None:
        k: int = 0
        total: int = 0
        for i in range(0, WIDTH, 1):
            if self.grid[i][rowIndex].state == STATES["UNKNOWN"]:
                break
            if self.grid[i][rowIndex].state == STATES["MINED"]:
                total += 1
                if total == self.rowNums[rowIndex][k].value:
                    if i + 1 < WIDTH:
                        self.grid[i + 1][rowIndex].flag()
                    self.rowNums[rowIndex][k].crossout()
                    k += 1
            if self.grid[i][rowIndex].state == STATES["FLAGGED"]:
                total = 0
                
        k: int = -1
        total: int = 0
        for i in range(WIDTH - 1, -1, -1):
            if self.grid[i][rowIndex].state == STATES["UNKNOWN"]:
                break
            if self.grid[i][rowIndex].state == STATES["MINED"]:
                total += 1
                if total == self.rowNums[rowIndex][k].value:
                    if i - 1 > -1:
                        self.grid[i - 1][rowIndex].flag()
                    self.rowNums[rowIndex][k].crossout()
                    k -= 1
            if self.grid[i][rowIndex].state == STATES["FLAGGED"]:
                total = 0
                
        k: int = 0
        total: int = 0
        for j in range(0, HEIGHT, 1):
            if self.grid[colIndex][j].state == STATES["UNKNOWN"]:
                break
            if self.grid[colIndex][j].state == STATES["MINED"]:
                total += 1
                if total == self.colNums[colIndex][k].value:
                    if j + 1 < HEIGHT:
                        self.grid[colIndex][j + 1].flag()
                    self.colNums[colIndex][k].crossout()
                    k += 1
            if self.grid[colIndex][j].state == STATES["FLAGGED"]:
                total = 0
                
        k: int = -1
        total: int = 0
        for j in range(HEIGHT - 1, -1, -1):
            if self.grid[colIndex][j].state == STATES["UNKNOWN"]:
                break
            if self.grid[colIndex][j].state == STATES["MINED"]:
                total += 1
                if total == self.colNums[colIndex][k].value:
                    if j - 1 < HEIGHT:
                        self.grid[colIndex][j - 1].flag()
                    self.colNums[colIndex][k].crossout()
                    k -= 1
            if self.grid[colIndex][j].state == STATES["FLAGGED"]:
                total = 0
                
        crossout_row: bool = True
        crossout_col: bool = True
        for i in range(WIDTH):
            if self.grid[i][rowIndex].mineable and not self.grid[i][rowIndex].state == STATES["MINED"]:
                crossout_row = False
        for j in range(HEIGHT):
            if self.grid[colIndex][j].mineable and not self.grid[colIndex][j].state == STATES["MINED"]:
                crossout_col = False
        if crossout_row:
            for i in range(WIDTH):
                self.grid[i][rowIndex].flag()
        if crossout_col:
            for j in range(HEIGHT):
                self.grid[colIndex][j].flag()
