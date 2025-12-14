import math
import time
from board import Board
from itertools import combinations
import traceback

def heuristics1(board, player, opponent):
    """
    Offensive Heuristic:
        - Player's potential winning lines
        - Blocking immediate threats lightly
        - Positional advantage (center control)
    """
    board_size = len(board)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # vertical, horizontal, diagonals
    score = 0

    # Counts consecutive pieces in both directions and checks for open ends
    def count_consecutive(row, col, dr, dc, target):
        count = 1  # count the starting stone
        open_ends = 0

        # Forward direction
        r, c = row + dr, col + dc
        while 0 <= r < board_size and 0 <= c < board_size:
            if board[r][c] == target:
                count += 1
                r += dr
                c += dc
            elif board[r][c] == 0:
                open_ends += 1
                break
            else:
                break

        # Backward direction
        r, c = row - dr, col - dc
        while 0 <= r < board_size and 0 <= c < board_size:
            if board[r][c] == target:
                count += 1
                r -= dr
                c -= dc
            elif board[r][c] == 0:
                open_ends += 1
                break
            else:
                break

        return count, open_ends

    # Positional weight: favor the center
    def positional_weight(row, col):
        center = board_size // 2
        return (center - abs(center - row)) + (center - abs(center - col))

    # Evaluate the board
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col] != 0:
                current_player = board[row][col]

                for dr, dc in directions:
                    count, open_ends = count_consecutive(row, col, dr, dc, current_player)

                    # Winning or losing patterns
                    if count >= 6:
                        if current_player == player:
                            return 100000  # immediate win
                        else:
                            return -100000  # immediate loss

                    # Offensive scoring for player
                    if current_player == player:
                        if count == 5:
                            score += 10000 * open_ends
                        elif count == 4:
                            score += 1000 * open_ends
                        elif count == 3:
                            score += 100 * open_ends
                        elif count == 2:
                            score += 10 * open_ends

                    # Lightly consider opponent patterns
                    elif current_player == opponent:
                        if count == 5:
                            score -= 5000 * open_ends
                        elif count == 4:
                            score -= 500 * open_ends
                        elif count == 3:
                            score -= 50 * open_ends
                        elif count == 2:
                            score -= 5 * open_ends

            # Add positional weight
            if board[row][col] == player:
                score += positional_weight(row, col)
            elif board[row][col] == opponent:
                score -= positional_weight(row, col)

    return score


def heuristics2(board, player, opponent):
    """
    Defensive Heuristic:
        - Prioritizes blocking opponent streaks
        - Secondary consideration for player's potential moves
        - Includes basic positional advantage
    """
    board_size = len(board)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    score = 0

    # Count consecutive stones in both directions and check open ends
    def count_consecutive(row, col, dr, dc, target):
        count = 1  # include the starting stone
        open_ends = 0

        # Forward
        r, c = row + dr, col + dc
        while 0 <= r < board_size and 0 <= c < board_size:
            if board[r][c] == target:
                count += 1
                r += dr
                c += dc
            elif board[r][c] == 0:
                open_ends += 1
                break
            else:
                break

        # Backward
        r, c = row - dr, col - dc
        while 0 <= r < board_size and 0 <= c < board_size:
            if board[r][c] == target:
                count += 1
                r -= dr
                c -= dc
            elif board[r][c] == 0:
                open_ends += 1
                break
            else:
                break

        return count, open_ends

    # Positional weight: weaker influence
    def positional_weight(row, col):
        center = board_size // 2
        return ((center - abs(center - row)) + (center - abs(center - col)))

    for row in range(board_size):
        for col in range(board_size):
            if board[row][col] != 0:
                current_player = board[row][col]

                for dr, dc in directions:
                    count, open_ends = count_consecutive(row, col, dr, dc, current_player)

                    # Terminal positions
                    if count >= 6:
                        if current_player == player:
                            return 100000  # immediate win
                        else:
                            return -100000  # immediate loss

                    # Defensive scoring: opponent threats prioritized
                    if current_player == opponent:
                        if count == 5:
                            score -= 10000 * open_ends  # big threat
                        elif count == 4:
                            score -= 2000 * open_ends
                        elif count == 3:
                            score -= 500 * open_ends
                        elif count == 2:
                            score -= 100 * open_ends
                    elif current_player == player:
                        if count == 5:
                            score += 5000 * open_ends  # secondary
                        elif count == 4:
                            score += 500 * open_ends
                        elif count == 3:
                            score += 100 * open_ends
                        elif count == 2:
                            score += 50 * open_ends

            # Add weak positional weight
            if board[row][col] == player:
                score += positional_weight(row, col)
            elif board[row][col] == opponent:
                score -= positional_weight(row, col)

    return score

heuristic_map = {
    "heuristics1": heuristics1,
    "heuristics2": heuristics2,
}

def get_possible_moves(board):
    """Return all empty positions as (row, col)."""
    board_size = len(board)
    return [(r, c) for r in range(board_size) for c in range(board_size) if board[r][c] == 0]

# Allow heuristic to be either function or string key
def resolve_heuristic(heuristic):
    if callable(heuristic):
        return heuristic
    # fallback to global map lookup
    return heuristic_map.get(heuristic)

def get_top_single_moves(board, possible_moves, player, opponent, heuristic_func, top_k=8):
    """
    Quickly score single moves (place a temporary stone, evaluate heuristic),
    return top_k moves sorted by score descending (best for maximizing player).
    """
    scored = []
    for (r, c) in possible_moves:
        # place temporarily as player's move to evaluate
        orig = board[r][c]
        board[r][c] = player
        try:
            s = heuristic_func(board, player, opponent)
        except Exception:
            s = -math.inf
        board[r][c] = orig
        scored.append(((r, c), s))
    # sort descending and keep top_k
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, _ in scored[:top_k]]

def minimax_connect6(board, depth, is_maximizing, current_player, opponent,alpha, beta, heuristic, top_k=8, use_alpha_beta=True):
    """
    Safer minimax:
      - heuristic: function or string key (resolved)
      - top_k: limit single-move candidates to form pairs (reduces branching)
    """
    heuristic_func = resolve_heuristic(heuristic)
    if heuristic_func is None:
        raise ValueError("Unknown heuristic: {}".format(heuristic))

    possible_moves = get_possible_moves(board)  # returns list of (r,c)

    # Terminal conditions
    if depth == 0 or not possible_moves:
        return heuristic_func(board, current_player, opponent), None

    # Choose top single-move candidates to limit branching
    # If few empties, just use them all
    if len(possible_moves) <= top_k:
        single_candidates = possible_moves
    else:
        single_candidates = get_top_single_moves(board, possible_moves, current_player if is_maximizing else opponent, opponent if is_maximizing else current_player, heuristic_func, top_k=top_k)

    # Form combinations of two stones among chosen candidates
    # if only one candidate available, fallback to single moves
    move_combinations_iter = combinations(single_candidates, 2)
    # If only single candidate or no pairs, we'll handle below
    pair_list = list(move_combinations_iter)
    if not pair_list:
        pair_list = [(m,) for m in single_candidates]

    best_score = -math.inf if is_maximizing else math.inf
    best_move = None

    for moves in pair_list:
        # Place stones: if is_maximizing -> place current_player, else place opponent
        placed = []
        try:
            for r, c in moves:
                placed.append((r, c, board[r][c]))
                board[r][c] = current_player if is_maximizing else opponent

            score = minimax_connect6(
                board, depth - 1, not is_maximizing, current_player, opponent, alpha, beta, heuristic, top_k
            )[0]

        finally:
            # Undo moves robustly even if something fails
            for r, c, orig in placed:
                board[r][c] = orig

        # Maximize or minimize
        if is_maximizing:
            if score > best_score:
                best_score = score
                best_move = moves
            alpha = max(alpha, best_score)
        else:
            if score < best_score:
                best_score = score
                best_move = moves
            beta = min(beta, best_score)

        if use_alpha_beta and beta <= alpha:
            break

    return best_score, best_move


def heuristic_move(board, heuristic, use_alpha_beta):
    _, best_move = minimax_connect6(
        board.board,
        depth=2,
        is_maximizing=True,
        current_player=2,
        opponent=1,
        alpha=-math.inf,
        beta=math.inf,
        heuristic=heuristic,
        use_alpha_beta=use_alpha_beta
    )
    return best_move