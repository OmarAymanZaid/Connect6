class Board:
    def __init__(self, board_size = 19):
        self.board_size = board_size
        self.board      = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]

    def print_board(self):
        for row in self.board:
            print(" ".join(str(cell) for cell in row))