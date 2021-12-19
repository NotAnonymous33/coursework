from copy import copy, deepcopy
from pieces import *
from ai import AI
from functools import lru_cache
import pickle


pygame.init()

pieces_order = [PieceType.Rook, PieceType.Knight, PieceType.Bishop, PieceType.Queen,
                PieceType.King, PieceType.Bishop, PieceType.Knight, PieceType.Rook]
pieces_order_char = ["R", "N", "B", "Q", "K", "B", "N", "R"]

pawn_table = [[0, 0, 0, 0, 0, 0, 0, 0],
              [50, 50, 50, 50, 50, 50, 50, 50],
              [10, 10, 20, 30, 30, 20, 10, 10],
              [5, 5, 10, 25, 25, 10, 5, 5],
              [0, 0, 0, 20, 20, 0, 0, 0],
              [5, -5, -10, 0, 0, -10, -5, 5],
              [5, 10, 10, -20, -20, 10, 10, 5],
              [0, 0, 0, 0, 0, 0, 0, 0]]

knight_table = [[-50, -40, -30, -30, -30, -30, -40, -50],
                [-40, -20, 0, 0, 0, 0, -20, -40],
                [-30, 0, 10, 15, 15, 10, 0, -30],
                [-30, 5, 15, 20, 20, 15, 5, -30],
                [-30, 0, 15, 20, 20, 15, 0, -30],
                [-30, 5, 10, 15, 15, 10, 5, -30],
                [-40, -20, 0, 5, 5, 0, -20, -40],
                [-50, -40, -30, -30, -30, -30, -40, -50]]

bishop_table = [[-20, -10, -10, -10, -10, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 5, 10, 10, 5, 0, -10],
                [-10, 5, 5, 10, 10, 5, 5, -10],
                [-10, 0, 10, 10, 10, 10, 0, -10],
                [-10, 10, 10, 10, 10, 10, 10, -10],
                [-10, 5, 0, 0, 0, 0, 5, -10],
                [-20, -10, -10, -10, -10, -10, -10, -20, ]]

rook_table = [[0, 0, 0, 0, 0, 0, 0, 0, ],
              [5, 10, 10, 10, 10, 10, 10, 5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [0, 0, 0, 5, 5, 0, 0, 0]]

queen_table = [[-20, -10, -10, -5, -5, -10, -10, -20],
               [-10, 0, 0, 0, 0, 0, 0, -10],
               [-10, 0, 5, 5, 5, 5, 0, -10],
               [-5, 0, 5, 5, 5, 5, 0, -5],
               [0, 0, 5, 5, 5, 5, 0, -5],
               [-10, 5, 5, 5, 5, 5, 0, -10],
               [-10, 0, 5, 0, 0, 0, 0, -10],
               [-20, -10, -10, -5, -5, -10, -10, -20]]

empty_table = [[0 for i in range(8)] for j in range(8)]

tables = {
    PieceColor.White: {PieceType.Pawn: pawn_table, PieceType.Knight: knight_table, PieceType.Bishop: bishop_table,
                       PieceType.Rook: rook_table, PieceType.Queen: queen_table, PieceType.Empty: empty_table,
                       PieceType.King: empty_table},
    PieceColor.Black: {PieceType.Pawn: pawn_table[::-1], PieceType.Knight: knight_table, PieceType.Bishop: bishop_table[::-1],
                       PieceType.Rook: rook_table[::-1], PieceType.Queen: [row[::-1] for row in queen_table[::-1]], PieceType.Empty: empty_table,
                       PieceType.King: empty_table},
    PieceColor.Empty: {PieceType.Pawn: pawn_table, PieceType.Knight: knight_table, PieceType.Bishop: bishop_table,
                       PieceType.Rook: rook_table, PieceType.Queen: queen_table, PieceType.Empty: empty_table,
                       PieceType.King: empty_table}
}


class Board:
    def __init__(self):
        self.pieces = [
            [Piece(i, 0) for i in range(NUM_ROWS)],
            [Piece(i, 1) for i in range(NUM_ROWS)],
            [Piece() for _ in range(NUM_ROWS)],
            [Piece() for _ in range(NUM_ROWS)],
            [Piece() for _ in range(NUM_ROWS)],
            [Piece() for _ in range(NUM_ROWS)],
            [Piece(i, 6) for i in range(NUM_ROWS)],
            [Piece(i, 7) for i in range(NUM_ROWS)]
        ]
        self.source_coord = (-1, -1)
        self.moved_to = (-1, -1)
        self.turn = 1
        self.highlighted_cells = set([])
        self.check = False
        self.quit = False
        self.promote = False
        self.ai = AI(DEPTH)

    def click(self, xpos, ypos):
        xc = xpos // CLENGTH
        yc = ypos // CLENGTH

        # if the click is outside the board, reset the pieces
        if not (0 <= xc <= 7 and 0 <= yc <= 7 + self.promote):  # de morgans law moment
            self.reset_source()
            return

        x, y = self.source_coord
        if y % 7 == 0 and self.pieces[y][x].piece_type == PieceType.Pawn:
            self.highlight_cells(True)
            self.move_piece(xc, yc, True)
            self.ai.move(self)
            self.reset_source()
            return

        # if there isn't a source cell
        if self.source_coord == (-1, -1):
            if self.pieces[yc][xc].color.value is self.turn:  # if a cell with a piece is clicked
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
        if not self.promote and (xc, yc) in self.highlighted_cells:
            self.move_piece(xc, yc, True)
            self.ai.move(self)

        if not self.promote:
            self.reset_source()

    def highlight_cells(self, recur=False):
        if self.promote:
            self.highlighted_cells = set([(i, 8) for i in range(4)])
            return
        self.highlighted_cells = set([])
        x, y = self.source_coord  # really do be wishing python 3.10 were here
        if self.pieces[y][x].piece_type is PieceType.Pawn:
            self.highlight_pawn()
        elif self.pieces[y][x].piece_type is PieceType.Bishop:
            self.highlight_bishop()
        elif self.pieces[y][x].piece_type is PieceType.Knight:
            self.highlight_knight()
        elif self.pieces[y][x].piece_type is PieceType.Rook:
            self.highlight_rook()
        elif self.pieces[y][x].piece_type is PieceType.Queen:
            self.highlight_queen()
        elif self.pieces[y][x].piece_type is PieceType.King:
            self.highlight_king()

        if recur:
            new_moves = set([])
            for move in self.highlighted_cells:
                new_board = self.copyboard()
                new_board.move_piece(*move)
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
        self.check_bishop(1, -1)  # top right
        self.check_bishop(-1, -1)  # top left
        self.check_bishop(1, 1)  # bottom right
        self.check_bishop(-1, 1)  # bottom left

    def check_bishop(self, d2x, d2y):
        x, y = self.source_coord
        dx, dy = d2x, d2y
        stop = False
        while 0 <= x + dx <= 7 and 0 <= y + dy <= 7 and not stop:
            if self.pieces[y + dy][x + dx].color.value is self.turn * -1:
                stop = True
                self.highlighted_cells.add((x + dx, y + dy))
            elif self.pieces[y + dy][x + dx].color.value is self.turn:
                stop = True
            else:
                self.highlighted_cells.add((x + dx, y + dy))
            dy += d2y
            dx += d2x

    def highlight_knight(self):
        self.check_knight(2, -1)  # 2 right 1 up
        self.check_knight(2, 1)  # 2 right 1 down
        self.check_knight(1, -2)  # 1 right 2 up
        self.check_knight(1, 2)  # 1 right 2 down
        self.check_knight(-2, -1)  # 2 left 1 up
        self.check_knight(-2, 1)  # 2 left 1 down
        self.check_knight(-1, -2)  # 1 left 2 up
        self.check_knight(-1, 2)  # 1 left 2 down

    def check_knight(self, dx, dy):
        x, y = self.source_coord
        if not (0 <= x + dx <= 7): return
        if not (0 <= y + dy <= 7): return
        if self.pieces[y + dy][x + dx].color.value is not self.turn:  # 2 right 1 up
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
        dx = d2x
        dy = d2y
        x, y = self.source_coord
        while True:
            if not (0 <= x + dx <= 7 and 0 <= y + dy <= 7):
                return
            if self.pieces[y + dy][x + dx].color.value is self.turn * -1:
                self.highlighted_cells.add((x + dx, y + dy))
                return
            elif self.pieces[y + dy][x + dx].color.value is self.turn:
                return
            else:
                self.highlighted_cells.add((x + dx, y + dy))
                dx += d2x
                dy += d2y

    def highlight_king(self):
        self.check_king(0, -1)  # check up
        self.check_king(0, 1)  # check down
        self.check_king(-1, 0)  # check left
        self.check_king(1, 0)  # check right
        self.check_king(1, -1)  # check up right
        self.check_king(-1, -1)  # check up left
        self.check_king(1, 1)  # check down right
        self.check_king(-1, 1)  # check down left

        x, y = self.source_coord
        # add castling to right
        if self.check:  # no castling allowed if in check
            return
        if self.pieces[y][x].moved: return  # no castling allowed if king has moved
        if not self.pieces[y][7].color.value: return

        if not self.pieces[y][7].moved and (
                self.pieces[y][x + 1].color.value == self.pieces[y][x + 2].color.value == 0):
            self.highlighted_cells.add((x + 2, y))

        if not self.pieces[y][7].moved and (
                self.pieces[y][x - 1].color.value == self.pieces[y][x - 2].color.value == self.pieces[y][
            x - 3].color.value == 0):
            self.highlighted_cells.add((x - 2, y))
            self.highlighted_cells.add((x - 3, y))

    def check_king(self, dx, dy):
        x, y = self.source_coord
        if not (0 <= y + dy <= 7 and 0 <= x + dx <= 7):
            return
        if self.pieces[y + dy][x + dx].color.value is not self.turn:
            self.highlighted_cells.add((x + dx, y + dy))

    def check_quit(self):
        return self.quit

    def reset_source(self):
        self.source_coord = (-1, -1)
        self.highlighted_cells = set([])

    def move_piece(self, x, y, first=False):
        self.moved_to = (x, y)

        px, py = self.source_coord

        if self.promote:
            self.pieces[py][px] = Piece(x, 7 * self.turn)
            self.pieces[py][px].moved = False
            self.promote = False
            print("false")
        elif self.pieces[py][px].piece_type == PieceType.Pawn and y % 7 == 0:
            # wait for input from user asking which piece to turn into
            self.pieces[y][x] = self.pieces[py][px]
            self.pieces[py][px] = Piece()
            self.source_coord = (x, y)
            self.promote = True
            self.highlight_cells(True)
            return
            # get input
            # turn the piece into whatever type it should be
        else:
            # castling
            if self.pieces[py][px].piece_type == PieceType.King:
                if abs((d := x - px)) == 2:
                    d //= 2
                    rookx = max([0, d]) * 7
                    self.pieces[y][px + d] = self.pieces[y][rookx]
                    self.pieces[y][px + d].moved = True
                    self.pieces[y][rookx] = Piece()

                if px - x == 3:
                    self.pieces[y][2] = self.pieces[y][0]
                    self.pieces[y][2].moved = True
                    self.pieces[y][0] = Piece()

            self.pieces[y][x] = self.pieces[py][px]
            self.pieces[y][x].moved = True
            self.pieces[py][px] = Piece()  # set the source piece to 0

        current = self.source_coord
        self.check = self.is_check()
        self.source_coord = current

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
                if self.pieces[row_num][col_num].color.value is not self.turn: continue
                self.source_coord = (col_num, row_num)
                self.highlight_cells(True)
                if self.highlighted_cells != set([]): return
        print("checkmate noob")
        self.quit = True
        pygame.quit()

    def is_check(self):
        for row_num in range(NUM_ROWS):
            for col_num in range(NUM_ROWS):
                if self.pieces[row_num][col_num].color.value is not self.turn:
                    continue
                self.source_coord = (col_num, row_num)
                self.highlight_cells()
                for coord in self.highlighted_cells:
                    x, y = coord
                    if not self.promote and self.pieces[y][x].piece_type is PieceType.King and self.pieces[y][
                        x].color.value is not self.turn:
                        return True
        return False

    def opponent_check(self):
        self.turn *= -1
        for row_num in range(NUM_ROWS):
            for col_num in range(NUM_ROWS):
                if self.pieces[row_num][col_num].color.value is not self.turn:
                    continue
                self.reset_source()
                self.source_coord = (col_num, row_num)
                self.highlight_cells()
                for coord in self.highlighted_cells:
                    x, y = coord
                    if self.pieces[y][x].piece_type is PieceType.King and self.pieces[y][x].color.value is not self.turn:
                        self.turn *= -1
                        return True
        self.turn *= -1
        return False

    #@lru_cache(maxsize=None)
    def evaluate(self):
        if self.quit:
            print("quit")
            return self.turn * 99999999

        # add enumerate here
        e = 0
        for y, row in enumerate(self.pieces):
            for x, piece in enumerate(row):
                weight = tables[piece.color][piece.piece_type][y][x]
                e += piece.color.value * (piece.piece_type.value + weight)
                # e += piece.color.value * piece.piece_type.value
        return e

    def copyboard(self):
        # new_board = deepcopy(self)
        # new_board.pieces = [[piece.copyp() for piece in row] for row in self.pieces]
        # new_board.highlighted_cells = deepcopy(self.highlighted_cells)
        # add copy stuff

        return pickle.loads(pickle.dumps(self, -1))



