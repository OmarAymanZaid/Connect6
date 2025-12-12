"""Experiment runner: pairwise comparisons between heuristics with plotting."""
import time
import random
import matplotlib.pyplot as plt
from board import Board
from algorithms import minimax_connect6
import math

# The algorithms to compare: (algo_type, heuristic_name)
# algo_type: "minimax" or "alphabeta"
ALGOS = [("minimax", "heuristics1"), ("minimax", "heuristics2"), ("alphabeta", "heuristics3")]


def count_in_direction(board, row, col, dr, dc, player):
    board_size = len(board)
    count = 1
    for step in (1, -1):
        r, c = row + step * dr, col + step * dc
        while 0 <= r < board_size and 0 <= c < board_size and board[r][c] == player:
            count += 1
            r += step * dr
            c += step * dc
    return count


def check_win(board, player, last_row, last_col):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dr, dc in directions:
        if count_in_direction(board, last_row, last_col, dr, dc, player) >= 6:
            return True
    return False


def get_empty_cells(board):
    return [(r, c) for r in range(len(board)) for c in range(len(board)) if board[r][c] == 0]


def run_single_game(alg_a, heur_a, alg_b, heur_b, board_size=9, depth=2, starting_player=1):
    board = [[0] * board_size for _ in range(board_size)]
    current_player = starting_player
    # mapping for algorithms and heuristics
    alg_map = {1: (alg_a, heur_a), 2: (alg_b, heur_b)}
    times = {1: 0.0, 2: 0.0}
    moves = 0

    while True:
        alg_type, heuristic = alg_map[current_player]
        use_ab = True if alg_type == "alphabeta" else False
        start = time.perf_counter()
        score, best_move = minimax_connect6(
            board,
            depth=depth,
            is_maximizing=True,
            current_player=current_player,
            opponent=3 - current_player,
            alpha=-math.inf,
            beta=math.inf,
            heuristic=heuristic,
            use_alpha_beta=use_ab,
        )
        elapsed = time.perf_counter() - start
        times[current_player] += elapsed

        # best_move may be None, a tuple of one move, or a tuple of two moves
        if not best_move:
            empties = get_empty_cells(board)
            if not empties:
                return {"winner": 0, "times": times, "moves": moves}  # draw
            chosen = random.choice(empties)
            candidates = [chosen]
        else:
            candidates = list(best_move)

        for (r, c) in candidates:
            if board[r][c] == 0:
                board[r][c] = current_player
                moves += 1
                if check_win(board, current_player, r, c):
                    return {"winner": current_player, "times": times, "moves": moves}
                if not get_empty_cells(board):
                    return {"winner": 0, "times": times, "moves": moves}

        # switch player
        current_player = 3 - current_player


def run_match(alg_a, heur_a, alg_b, heur_b, games=6, board_size=9, depth=2):
    label_a = f"{alg_a}({heur_a})"
    label_b = f"{alg_b}({heur_b})"
    stats = {label_a: 0, label_b: 0, "draws": 0}
    total_times = {label_a: 0.0, label_b: 0.0}
    total_moves = []

    for i in range(games):
        starting = 1 if i % 2 == 0 else 2
        result = run_single_game(alg_a, heur_a, alg_b, heur_b, board_size=board_size, depth=depth, starting_player=starting)
        winner = result["winner"]
        if winner == 0:
            stats["draws"] += 1
        else:
            winner_label = label_a if winner == 1 else label_b
            stats[winner_label] += 1

        total_times[label_a] += result["times"][1]
        total_times[label_b] += result["times"][2]
        total_moves.append(result["moves"])

    avg_time = {label_a: total_times[label_a] / games, label_b: total_times[label_b] / games}
    avg_moves = sum(total_moves) / len(total_moves) if total_moves else 0

    return {"stats": stats, "avg_time": avg_time, "avg_moves": avg_moves}


def plot_results(comparisons):
    # comparisons: list of (label, result)
    n = len(comparisons)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]

    for ax, (label, res) in zip(axes, comparisons):
        heur_a, heur_b = label.split(" vs ")
        vals = [res["stats"][heur_a], res["stats"][heur_b], res["stats"]["draws"]]
        names = [heur_a, heur_b, "draws"]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
        ax.bar(names, vals, color=colors)
        ax.set_title(label)
        for i, v in enumerate(vals):
            ax.text(i, v + 0.05, str(v), ha='center')

    plt.tight_layout()
    plt.savefig("experiment_results.png")
    plt.show()


def run_all_pairwise(games=6, board_size=9, depth=2):
    # pair indices for the three algos
    pairs = [(0, 1), (0, 2), (1, 2)]
    comparisons = []
    for i, j in pairs:
        alg_a, heur_a = ALGOS[i]
        alg_b, heur_b = ALGOS[j]
        label = f"{alg_a}({heur_a}) vs {alg_b}({heur_b})"
        print(f"Running: {label} — {games} games")
        res = run_match(alg_a, heur_a, alg_b, heur_b, games=games, board_size=board_size, depth=depth)
        print(f"  Results: {res['stats']}, avg_moves={res['avg_moves']:.1f}, avg_time={res['avg_time']}")
        comparisons.append((label, res))

    plot_results(comparisons)


if __name__ == "__main__":
    # Quick test run: small number of games to verify plotting
    # Reduced board size/depth/games for reasonable runtime during tests
    run_all_pairwise(games=4, board_size=7, depth=1)
