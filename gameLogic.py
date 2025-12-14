import random
from board import Board
from algorithms import heuristic_move

class GameLogic:
    def __init__(self, mode, user_board_size):
        self.board_size = user_board_size
        self.board = Board(board_size=self.board_size)
        self.mode = mode.lower()
        self.current_player = 1
        self.moves_made = 0  # counts moves in current turn
        self.max_moves_per_turn = 2
        self.turn = 0
        self.vsai = self.mode != "pvp"

    def is_valid_move(self, row, col):
        return 0 <= row < self.board.board_size and 0 <= col < self.board.board_size and self.board.board[row][col] == 0

    def place_piece(self, row, col):
        if self.is_valid_move(row, col):
            self.board.board[row][col] = self.current_player
            self.moves_made += 1
            self.turn += 1
            print(f"Player {self.current_player} played ({row}, {col})")

    def switch_player(self):
        if self.moves_made >= self.max_moves_per_turn:
            self.current_player = 3 - self.current_player
            self.moves_made = 0

    def ai_plays(self):
        # Map UI mode to algorithm calls. We have three AI variants:
        # - minimax with heuristics1
        # - minimax with heuristics2
        # - minimax with heuristics1 + alphabeta
        # - minimax with heuristics2 + alphabeta

        if self.mode == "heuristics1":
            best_move = heuristic_move(self.board, "heuristics1", False)

        elif self.mode == "heuristics2":
            best_move = heuristic_move(self.board, "heuristics2", False)

        elif self.mode == "alphabeta1":
            best_move = heuristic_move(self.board, "heuristics1", True)

        elif self.mode == "alphabeta2":
            best_move = heuristic_move(self.board, "heuristics2", True)

        else:
            best_move = None

        # Fallback: no best move
        if not best_move:
            empty = [(r, c) for r in range(self.board_size) for c in range(self.board_size)
                    if self.board.board[r][c] == 0]
            if empty:
                return [random.choice(empty)]   # return list of 1 move
            return []

        # best_move is tuple of tuples → convert to list
        move_list = list(best_move)

        # Validate only
        valid_moves = []
        for r, c in move_list:
            if self.is_valid_move(r, c):
                valid_moves.append((r, c))

        return valid_moves


    def check_win(self, row, col):
        directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]
        return any(self.count_in_direction(row, col, dr, dc) >= 6 for dr, dc in directions)
    
    def check_draw(self):
        return all(self.board.board[r][c] != 0 for r in range(self.board_size) for c in range(self.board_size))

    def count_in_direction(self, row, col, dr, dc):
        count = 1  # Include the current piece
        for step in (-1, 1):
            r, c = row + step * dr, col + step * dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board.board[r][c] == self.current_player:
                count += 1
                r += step * dr
                c += step * dc
        return count