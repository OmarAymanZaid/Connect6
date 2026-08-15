"""Experiment runner: pairwise comparisons between heuristics with plotting."""
import time
import random
import matplotlib.pyplot as plt
from board import Board
from algorithms import minimax_connect6, resolve_heuristic, heuristic_map
from itertools import combinations
import math
import numpy as np
from matplotlib.ticker import MaxNLocator

# experiment compares search strategies as well as heuristic functions.
ALGOS = []
for h in heuristic_map.keys():
    ALGOS.append(("minimax", h))
    ALGOS.append(("alphabeta", h))


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
    if board_size <= 5:
        raise ValueError("board_size must be greater than 5")

    # Verify heuristics exist before starting
    if resolve_heuristic(heur_a) is None:
        raise ValueError(f"Unknown heuristic: {heur_a}")
    if resolve_heuristic(heur_b) is None:
        raise ValueError(f"Unknown heuristic: {heur_b}")

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
    if board_size <= 5:
        raise ValueError("board_size must be greater than 5")

    # Validate heuristics at match level as well
    if resolve_heuristic(heur_a) is None:
        raise ValueError(f"Unknown heuristic: {heur_a}")
    if resolve_heuristic(heur_b) is None:
        raise ValueError(f"Unknown heuristic: {heur_b}")

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
    if not comparisons:
        print("No comparison data to plot")
        return

    labels = [lbl for lbl, _ in comparisons]
    wins_a = []
    wins_b = []
    draws = []

    for label, res in comparisons:
        try:
            left, right = label.split(" vs ")
        except ValueError:
            # fallback to first two keys
            keys = [k for k in res["stats"].keys() if k != "draws"]
            left, right = (keys + [None, None])[:2]

        wins_a.append(res["stats"].get(left, 0))
        wins_b.append(res["stats"].get(right, 0))
        draws.append(res["stats"].get("draws", 0))

    x = np.arange(len(labels))
    # dynamic width so bars remain visible for many comparisons
    width = min(0.25, 0.8 / max(3, len(labels)))

    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 2), 6))
    rects1 = ax.bar(x - width, wins_a, width, label='A wins', color='#1f77b4')
    rects2 = ax.bar(x, wins_b, width, label='B wins', color='#ff7f0e')
    rects3 = ax.bar(x + width, draws, width, label='Draws', color='#2ca02c')

    # replace ' vs ' with newline for clearer multi-line labels
    display_labels = [l.replace(' vs ', '\nvs\n') for l in labels]
    ax.set_xticks(x)
    ax.set_xticklabels(display_labels, rotation=30, ha='right')
    ax.set_ylabel('Number of games')
    ax.set_title('Pairwise comparison results')
    ax.legend()

    # grid and integer y ticks for clarity
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)

    # annotate bars
    def autolabel(rects):
        for rect in rects:
            h = rect.get_height()
            ax.annotate(str(int(h)), xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=8)

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    ymax = max(wins_a + wins_b + draws) if (wins_a + wins_b + draws) else 0
    ax.set_ylim(0, ymax + max(1, int(ymax * 0.15)))

    plt.tight_layout()
    plt.savefig("experiment_results.png", dpi=200)
    plt.show()


# -------------------------------------------------------------------------------
# Instrumentation: node counter 
# --------------------------------------------------------------------------------
nodes_expanded = 0

def reset_node_counter():
    global nodes_expanded
    nodes_expanded = 0

def get_node_count():
    return nodes_expanded

def run_search_once(board_obj, depth=2, heuristic=None, use_alpha_beta=True, is_maximizing=True):
    """
    Runs one search on a board (Board instance) and returns:
  
    """
    # default to a valid heuristic if none provided
    if heuristic is None or resolve_heuristic(heuristic) is None:
        heuristic = next(iter(heuristic_map.keys()))

    reset_node_counter()
    start = time.perf_counter()

    score, move = minimax_connect6(
        board_obj.board,
        depth=depth,
        is_maximizing=is_maximizing,
        current_player=2 if is_maximizing else 1,
        opponent=1 if is_maximizing else 2,
        alpha=-float("inf"),
        beta=float("inf"),
        heuristic=heuristic,
        use_alpha_beta=use_alpha_beta
    )

    elapsed = time.perf_counter() - start
    nodes = get_node_count()
    return {"score": score, "move": move, "nodes": nodes, "time": elapsed}



def run_all_pairwise(games=6, board_size=9, depth=2, pair_mode='full'):
    """Run pairwise experiments."""
    if board_size <= 5:
        raise ValueError("board_size must be greater than 5")

    heuristics = list(heuristic_map.keys())
    if len(heuristics) < 2:
        print("Not enough heuristics available for pairwise experiments.")
        return

    comparisons = []

    if pair_mode == 'four':
        
        h1, h2 = heuristics[0], heuristics[1]
        pairs = [
            (("minimax", h1), ("minimax", h2)),
            (("alphabeta", h1), ("alphabeta", h2)),
            (("minimax", h1), ("alphabeta", h1)),
            (("minimax", h2), ("alphabeta", h2)),
        ]
        for (alg_a, heur_a), (alg_b, heur_b) in pairs:
            label = f"{alg_a}({heur_a}) vs {alg_b}({heur_b})"
            print(f"Running: {label} — {games} games")
            res = run_match(alg_a, heur_a, alg_b, heur_b, games=games, board_size=board_size, depth=depth)
            print(f"  Results: {res['stats']}, avg_moves={res['avg_moves']:.1f}, avg_time={res['avg_time']}")
            comparisons.append((label, res))
    else:
        n = len(ALGOS)
        if n < 2:
            print("Not enough algorithms/heuristics available for pairwise experiments.")
            return

        for i, j in combinations(range(n), 2):
            alg_a, heur_a = ALGOS[i]
            alg_b, heur_b = ALGOS[j]
            label = f"{alg_a}({heur_a}) vs {alg_b}({heur_b})"
            print(f"Running: {label} — {games} games")
            res = run_match(alg_a, heur_a, alg_b, heur_b, games=games, board_size=board_size, depth=depth)
            print(f"  Results: {res['stats']}, avg_moves={res['avg_moves']:.1f}, avg_time={res['avg_time']}")
            comparisons.append((label, res))

    plot_results(comparisons)


if __name__ == "__main__":
    
    run_all_pairwise(games=8, board_size=7, depth=1)
