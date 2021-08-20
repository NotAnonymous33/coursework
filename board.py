# import pygame
from constants import *
from aenum import Enum
from aenum import NoAlias
from copy import copy, deepcopy

pygame.init()


class PieceColor(Enum):
    BLACK = -1
    WHITE = 1
    EMPTY = 0


class PieceType(Enum):
    _settings_ = NoAlias
    EMPTY = 0
    PAWN = 1
    ROOK = 5
    BISHOP = 3
    KNIGHT = 3
    QUEEN = 9
    KING = 999999


pieces_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
pieces_order_char = ["R", "N", "B", "Q", "K", "B", "N", "R"]


class Piece:
    def __init__(self, x, y):
        # sorting out color of piece
        if y < 3:
            self.color = PieceColor.BLACK
            img = "b"
        else:
            self.color = PieceColor.WHITE
            img = "w"

        # type of piece
        if y == 0 or y == 7:
            self.piece_type = pieces_order[x]
            img += pieces_order_char[x]
        else:
            self.piece_type = PieceType.PAWN
            img += "p"

        # image of piece
        self.image = IMAGES[img]
        self.moved = False

    def draw(self, x, y):
        WIN.blit(self.image, (x * CLENGTH, y * CLENGTH))

    def __repr__(self):
        return f"{self.color} {self.piece_type}"


class Cell:
    def __init__(self, x, y):
        self.xcoor = x * CLENGTH
        self.ycoor = y * CLENGTH
        self.color = [LCOLOR, RCOLOR][(x + y) % 2]

    def draw(self):
        pygame.draw.rect(WIN, self.color, [self.xcoor, self.ycoor, CLENGTH, CLENGTH])

    def __repr__(self):
        return f"({self.xcoor}, {self.ycoor})"


class Empty:
    def __init__(self):
        self.color = PieceColor.EMPTY
        self.piece_type = PieceType.EMPTY

    def __repr__(self):
        return "empty"

    def draw(self, *args, **kwargs):
        pass


class Board:
    def __init__(self):
        self.cells = [[Cell(col, row) for col in range(NUM_ROWS)] for row in range(NUM_ROWS)]
        self.pieces = [
            [Piece(i, 0) for i in range(NUM_ROWS)],
            [Piece(i, 1) for i in range(NUM_ROWS)],
            [Empty() for _ in range(NUM_ROWS)],
            [Empty() for _ in range(NUM_ROWS)],
            [Empty() for _ in range(NUM_ROWS)],
            [Empty() for _ in range(NUM_ROWS)],
            [Piece(i, 6) for i in range(NUM_ROWS)],
            [Piece(i, 7) for i in range(NUM_ROWS)]
        ]
        self.source_coord = (-1, -1)
        self.turn = 1
        self.highlighted_cells = set([])
        self.check = False
        self.quit = False

    def draw(self):
        # draw the squares of the board
        for row in self.cells:
            for cell in row:
                cell.draw()

        # draw highlighted squares
        for coord in self.highlighted_cells:
            color = HLCOLOR
            if (coord[0] + coord[1]) % 2: color = HDCOLOR
            pygame.draw.rect(WIN, color, [coord[0] * CLENGTH, coord[1] * CLENGTH, CLENGTH, CLENGTH])

        # draw selected square
        pygame.draw.rect(WIN, SCOLOR,
                         [self.source_coord[0] * CLENGTH, self.source_coord[1] * CLENGTH, CLENGTH, CLENGTH])

        # draw pieces
        for row_num in range(NUM_ROWS):
            for col_num in range(NUM_ROWS):
                self.pieces[row_num][col_num].draw(col_num, row_num)

    def click(self, xpos, ypos):
        xc = xpos // CLENGTH
        yc = ypos // CLENGTH

        # if the click is outside the board, reset the pieces
        if not (0 <= xc <= 7 and 0 <= yc <= 7):  # de morgans law moment
            self.reset_source()
            return

        # if there isn't a source cell
        if self.source_coord == (-1, -1):
            if self.pieces[yc][xc].color.value == self.turn:  # if a cell with a piece is clicked
                self.source_coord = (xc, yc)  # set the clicked piece as the source piece
                self.highlight_cells(True)
                '''
                For each highlighted cell, make move
                If after move, still in check
                Remove move
                '''
            else:
                self.reset_source()
            return

        # there is a source cell
        if (xc, yc) in self.highlighted_cells:
            self.move_piece(xc, yc, True)
        self.reset_source()

    def highlight_cells(self, recur=False):
        self.highlighted_cells = set([])
        x, y = self.source_coord  # really do be wishing python 3.10 were here
        if self.pieces[y][x].piece_type == PieceType.PAWN:
            self.highlight_pawn()
        elif self.pieces[y][x].piece_type == PieceType.BISHOP:
            self.highlight_bishop()
        elif self.pieces[y][x].piece_type == PieceType.KNIGHT:
            self.highlight_knight()
        elif self.pieces[y][x].piece_type == PieceType.ROOK:
            self.highlight_rook()
        elif self.pieces[y][x].piece_type == PieceType.QUEEN:
            self.highlight_queen()
        elif self.pieces[y][x].piece_type == PieceType.KING:
            self.highlight_king()

        if recur:
            new_moves = set([])
            for move in self.highlighted_cells:
                new_board = copy(self)
                new_board.pieces = [row[:] for row in self.pieces]
                new_board.highlighted_cells = deepcopy(self.highlighted_cells)
                new_board.move_piece(*move)
                # self.turn *= -1
                if not new_board.is_check():
                    new_moves.add(move)
            self.highlighted_cells = new_moves

        self.highlighted_cells.discard((x, y))


    def highlight_pawn(self):
        x, y = self.source_coord
        # if the piece in front is empty add that cell
        if self.pieces[y - self.turn][x].color.value == 0:
            self.highlighted_cells.add((x, y - self.turn))

        # if the pawn hasn't moved, let it move 2 moves forward
        if not self.pieces[y][x].moved and self.pieces[y - 2 * self.turn][x].color.value == self.pieces[y - self.turn][
            x].color.value == 0:
            self.highlighted_cells.add((x, y - 2 * self.turn))

        # if the piece to the left and right corner are opposite color, add them to highlighted piece
        # left hand side
        if x != 0:
            if self.pieces[y - self.turn][x - 1].color.value == self.turn * -1:
                self.highlighted_cells.add((x - 1, y - self.turn))

        # right hand side
        if x != 7:
            if self.pieces[y - self.turn][x + 1].color.value == self.turn * -1:
                self.highlighted_cells.add((x + 1, y - self.turn))

    def highlight_bishop(self):
        # top right
        self.check_bishop(1, -1)
        # top left
        self.check_bishop(-1, -1)
        # bottom right
        self.check_bishop(1, 1)
        # bottom left
        self.check_bishop(-1, 1)

    def check_bishop(self, d2x, d2y):
        x, y = self.source_coord
        dx, dy = d2x, d2y
        stop = False
        while 0 <= x + dx <= 7 and 0 <= y + dy <= 7 and not stop:
            if self.pieces[y + dy][x + dx].color.value == self.turn * -1:
                stop = True
                self.highlighted_cells.add((x + dx, y + dy))
            elif self.pieces[y + dy][x + dx].color.value == self.turn:
                stop = True
            else:
                self.highlighted_cells.add((x + dx, y + dy))
            dy += d2y
            dx += d2x

    def highlight_knight(self):
        # 2 right 1 up
        self.check_knight(2, -1)
        # 2 right 1 down
        self.check_knight(2, 1)
        # 1 right 2 up
        self.check_knight(1, -2)
        # 1 right 2 down
        self.check_knight(1, 2)
        # 2 left 1 up
        self.check_knight(-2, -1)
        # 2 left 1 down
        self.check_knight(-2, 1)
        # 1 left 2 up
        self.check_knight(-1, -2)
        # 1 left 2 down
        self.check_knight(-1, 2)

    def check_knight(self, dx, dy):
        x, y = self.source_coord
        if not (0 <= x + dx <= 7): return
        if not (0 <= y + dy <= 7): return
        if self.pieces[y + dy][x + dx].color.value != self.turn:  # 2 right 1 up
            self.highlighted_cells.add((x + dx, y + dy))

    def highlight_queen(self):
        self.highlight_rook()
        self.highlight_bishop()

    def highlight_rook(self):
        self.check_rook(1, 0)  # look right
        self.check_rook(-1, 0)  # look left
        self.check_rook(0, 1)  # look down
        self.check_rook(0, -1)  # look up

    def check_rook(self, d2x, d2y):
        condition = True
        dx = d2x
        dy = d2y
        x, y = self.source_coord
        while True:
            if not (0 <= x + dx <= 7 and 0 <= y +  dy <= 7):
                return
            if self.pieces[y + dy][x + dx].color.value == self.turn * -1:
                self.highlighted_cells.add((x + dx, y + dy))
                return
            elif self.pieces[y + dy][x + dx].color.value == self.turn:
                return
            else:
                self.highlighted_cells.add((x + dx, y + dy))
                dx += d2x
                dy += d2y

    def highlight_king(self):
        # check up
        self.check_king(0, -1)
        # check down
        self.check_king(0, 1)
        # check left
        self.check_king(-1, 0)
        # check right
        self.check_king(1, 0)
        # check up right
        self.check_king(1, -1)
        # check up left
        self.check_king(-1, -1)
        # check down right
        self.check_king(1, 1)
        # check down left
        self.check_king(-1, 1)

    def check_king(self, dx, dy):
        x, y = self.source_coord
        if not (0 <= y + dy <= 7 and 0 <= x + dx <= 7):
            return
        if self.pieces[y + dy][x + dx].color.value != self.turn:
            self.highlighted_cells.add((x + dx, y + dy))

    def check_quit(self):
        return self.quit

    def reset_source(self):
        self.source_coord = (-1, -1)
        self.highlighted_cells = set([])

    def move_piece(self, x, y, first=False):
        self.pieces[y][x] = self.pieces[self.source_coord[1]][self.source_coord[0]]
        self.pieces[y][x].moved = True
        self.pieces[self.source_coord[1]][self.source_coord[0]] = Empty()  # set the source piece to 0

        self.check = self.is_check()

        self.turn *= -1

        if self.check and first:
            self.check_checkmate()



        '''
        If king is under attack, check
        For each piece
            Select piece
            If king is in highlighted cells
                check = True
                break 
        For each move opponent can make
            Make move
            If not in check anymore:
                break
        else:
            checkmate, end the game
        
        '''

    def check_checkmate(self):
        for row_num in range(NUM_ROWS):
            for col_num in range(NUM_ROWS):
                if self.pieces[row_num][col_num].color.value != self.turn: continue
                self.source_coord = (col_num, row_num)
                self.highlight_cells(True)
                if self.highlighted_cells != set([]): return
        print("chekmate noob")
        self.quit = True



    def is_check(self):
        for row_num in range(NUM_ROWS):
            for col_num in range(NUM_ROWS):
                if self.pieces[row_num][col_num].color.value != self.turn:
                    continue
                self.source_coord = (col_num, row_num)
                self.highlight_cells()
                for coord in self.highlighted_cells:
                    x, y = coord
                    if self.pieces[y][x].piece_type == PieceType.KING and self.pieces[y][x].color.value != self.turn:
                        return True
        return False

    def opponent_check(self):
        self.turn *= -1
        for row_num in range(NUM_ROWS):
            for col_num in range(NUM_ROWS):
                if self.pieces[row_num][col_num].color.value != self.turn:
                    continue
                self.reset_source()
                self.source_coord = (col_num, row_num)
                self.highlight_cells()
                for coord in self.highlighted_cells:
                    x, y = coord
                    if self.pieces[y][x].piece_type == PieceType.KING and self.pieces[y][x].color.value != self.turn:
                        self.turn *= -1
                        return True
        self.turn *= -1
        return False

    def evaluate(self):
        e = 0
        for row in self.pieces:
            e += sum(map(lambda x : x.color.value * x.piece_type.value, row))
            # e += piece.color.value * piece.piece_type.value
        return e
