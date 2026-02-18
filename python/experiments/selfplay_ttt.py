#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Play Tic-Tac-Toe Experiment: Testing Ouroboros Optimization Predictions

Phase 1 cheap falsification: do self-referential dynamics in self-play produce
specific golden-ratio-related ratios as predicted by the Ouroboros theory?

Two conditions:
  A. Self-play: both players share a single value function (self-referential)
  B. Frozen-opponent: opponent uses periodically-frozen copy of V (breaks tight coupling)

Predictions from Ouroboros theory:
  - Value R^2 ceiling ~ 0.382 (= 1/phi^2) for self-play
  - Policy accuracy ceiling ~ 0.382 for self-play
  - Optimal exploration epsilon ~ 0.276 (= 1 - phi/sqrt(5))
  - State coverage ~ 0.382 for self-play
  - Policy entropy ~ 0.276 for self-play
  - Convergence oscillation present in self-play

Dependencies: numpy (matplotlib optional for plots)
"""

import numpy as np
import sys
import io
import time
from collections import defaultdict
from typing import Dict, Tuple, List, Set, Optional

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Try importing matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Golden ratio constants
PHI = (1 + np.sqrt(5)) / 2
PHI_SQ = PHI ** 2
INV_PHI = 1.0 / PHI       # ~0.618
INV_PHI_SQ = 1.0 / PHI_SQ  # ~0.382
NU = PHI / np.sqrt(5)      # ~0.7236
ONE_MINUS_NU = 1 - NU      # ~0.2764

# Random seed for reproducibility
RNG_SEED = 42


# =============================================================================
# 1. Tic-Tac-Toe Engine (optimized: tuple-based, no numpy per move)
# =============================================================================

def ttt_legal_moves(board: tuple) -> list:
    """Return list of indices where board[i] == 0."""
    return [i for i in range(9) if board[i] == 0]


def ttt_check_winner(board: tuple) -> Optional[int]:
    """Return 1 if X wins, -1 if O wins, 0 if draw, None if ongoing."""
    lines = [
        (0,1,2), (3,4,5), (6,7,8),  # rows
        (0,3,6), (1,4,7), (2,5,8),  # cols
        (0,4,8), (2,4,6)            # diags
    ]
    for a, b, c in lines:
        s = board[a] + board[b] + board[c]
        if s == 3:
            return 1
        if s == -3:
            return -1
    if 0 not in board:
        return 0  # draw
    return None  # ongoing


def ttt_make_move(board: tuple, pos: int, player: int) -> tuple:
    """Return new board tuple with player's mark at pos."""
    lst = list(board)
    lst[pos] = player
    return tuple(lst)


def ttt_current_player(board: tuple) -> int:
    """Determine current player from board state. X=1 moves first."""
    x_count = sum(1 for v in board if v == 1)
    o_count = sum(1 for v in board if v == -1)
    return 1 if x_count == o_count else -1


def make_state_key(board: tuple) -> tuple:
    """State key = (board, current_player)."""
    return (board, ttt_current_player(board))


# =============================================================================
# 2. Minimax Solver + State Graph Pre-computation
# =============================================================================

class GameGraph:
    """Pre-computed game graph for fast evaluation.

    Stores:
    - value_cache: state_key -> V*(s) from mover's perspective
    - optimal_actions: state_key -> set of optimal move indices
    - all_states: set of all reachable state_keys
    - non_terminal_keys: list of non-terminal state_keys
    - children: state_key -> list of (move_idx, child_state_key)
    - n_legal: state_key -> number of legal moves
    """

    def __init__(self):
        self.value_cache: Dict[tuple, float] = {}
        self.optimal_actions: Dict[tuple, Set[int]] = {}
        self.all_states: Set[tuple] = set()
        self.non_terminal_keys: List[tuple] = []
        self.children: Dict[tuple, List[tuple]] = {}  # key -> [(move, child_key), ...]
        self.n_legal: Dict[tuple, int] = {}
        self.is_terminal: Dict[tuple, bool] = {}

    def build(self):
        """Solve game and pre-compute all structures."""
        print("Solving tic-tac-toe with minimax...")
        t0 = time.time()

        init_board = (0,) * 9
        self._minimax(init_board, 1)

        # Second pass: compute ALL optimal actions (alpha-beta may have pruned some)
        for key in list(self.all_states):
            if self.is_terminal.get(key, False):
                continue
            board, player = key
            moves = ttt_legal_moves(board)
            opt_val = self.value_cache[key]
            opt_moves = set()
            for m in moves:
                child_board = ttt_make_move(board, m, player)
                child_key = make_state_key(child_board)
                child_val = -self.value_cache[child_key]
                if abs(child_val - opt_val) < 1e-9:
                    opt_moves.add(m)
            self.optimal_actions[key] = opt_moves

        # Build non-terminal list
        self.non_terminal_keys = [k for k in self.all_states if not self.is_terminal.get(k, False)]

        # Pre-compute children for non-terminal states (for fast eval)
        for key in self.non_terminal_keys:
            board, player = key
            moves = ttt_legal_moves(board)
            self.n_legal[key] = len(moves)
            children = []
            for m in moves:
                child_board = ttt_make_move(board, m, player)
                child_key = make_state_key(child_board)
                children.append((m, child_key))
            self.children[key] = children

        t1 = time.time()
        print(f"  Total reachable states: {len(self.all_states)}")
        print(f"  Non-terminal states: {len(self.non_terminal_keys)}")
        root_key = (init_board, 1)
        print(f"  Root value (X to move): {self.value_cache[root_key]}")
        print(f"  Solve time: {t1-t0:.2f}s")

    def _minimax(self, board: tuple, player: int) -> float:
        """Full minimax (no alpha-beta -- TTT is small enough).
        Returns value from mover's perspective."""
        key = (board, player)

        if key in self.value_cache:
            return self.value_cache[key]

        self.all_states.add(key)

        winner = ttt_check_winner(board)
        if winner is not None:
            if winner == 0:
                val = 0.0
            elif winner == player:
                val = 1.0  # Shouldn't happen in normal play
            else:
                val = -1.0  # Opponent just won
            self.value_cache[key] = val
            self.is_terminal[key] = True
            return val

        self.is_terminal[key] = False
        moves = ttt_legal_moves(board)
        best_val = -2.0
        next_player = -player

        for m in moves:
            child_board = ttt_make_move(board, m, player)
            child_val = -self._minimax(child_board, next_player)
            if child_val > best_val:
                best_val = child_val

        self.value_cache[key] = best_val
        return best_val


# =============================================================================
# 3. Training: Self-Play and Frozen-Opponent Conditions
# =============================================================================

def get_agent_action(board: tuple, player: int, V: Dict, epsilon: float,
                     rng: np.random.Generator) -> int:
    """Select action using epsilon-greedy based on value function V.

    V is stored from the mover's perspective. After taking action, the opponent
    faces child state s' with V(s') from THEIR perspective. Agent wants to
    MINIMIZE V(s') (minimizing opponent's value = maximizing own).
    """
    moves = ttt_legal_moves(board)

    if rng.random() < epsilon:
        return moves[rng.integers(len(moves))]

    best_val = float('inf')
    best_moves = []
    next_player = -player

    for m in moves:
        child_board = ttt_make_move(board, m, player)
        child_key = (child_board, next_player)
        child_v = V.get(child_key, 0.0)
        if child_v < best_val - 1e-12:
            best_val = child_v
            best_moves = [m]
        elif abs(child_v - best_val) < 1e-12:
            best_moves.append(m)

    return best_moves[rng.integers(len(best_moves))]


def get_minimax_action(board: tuple, player: int, graph: GameGraph,
                       rng: np.random.Generator) -> int:
    """Select a minimax-optimal action (random among ties)."""
    key = (board, player)
    optimal = list(graph.optimal_actions.get(key, set()))
    if not optimal:
        moves = ttt_legal_moves(board)
        return moves[rng.integers(len(moves))]
    return optimal[rng.integers(len(optimal))]


def train_selfplay(n_episodes: int, epsilon: float, alpha_init: float,
                   eval_interval: int, graph: GameGraph,
                   rng: np.random.Generator, decay_alpha: bool = True) -> dict:
    """Train via self-play: both players share the SAME value function."""
    V: Dict[tuple, float] = {}
    visit_count: Dict[tuple, int] = defaultdict(int)
    eval_results = []

    for episode in range(n_episodes):
        alpha = alpha_init / (1 + episode / 10000) if decay_alpha else alpha_init

        board = (0,) * 9
        player = 1
        trajectory = []  # List of (state_key, player_at_state)

        while True:
            key = (board, player)
            trajectory.append((key, player))
            visit_count[key] += 1
            if key not in V:
                V[key] = 0.0

            action = get_agent_action(board, player, V, epsilon, rng)
            board = ttt_make_move(board, action, player)
            player = -player

            winner = ttt_check_winner(board)
            if winner is not None:
                break

        # MC update: outcome from each player's perspective
        for state_key, p in trajectory:
            if winner == 0:
                outcome = 0.0
            elif winner == p:
                outcome = 1.0
            else:
                outcome = -1.0
            V[state_key] += alpha * (outcome - V[state_key])

        if (episode + 1) % eval_interval == 0:
            metrics = evaluate_fast(V, visit_count, graph)
            metrics['episode'] = episode + 1
            eval_results.append(metrics)

    return {'V': V, 'visit_count': visit_count, 'eval_results': eval_results}


def train_frozen(n_episodes: int, epsilon: float, alpha_init: float,
                 eval_interval: int, graph: GameGraph,
                 rng: np.random.Generator, decay_alpha: bool = True,
                 freeze_interval: int = 5000) -> dict:
    """Train via self-play with frozen opponent.

    Same as self-play but opponent uses a periodically-frozen copy of V.
    This breaks the tight self-referential coupling while preserving
    the same exploration dynamics and state distribution.
    """
    V: Dict[tuple, float] = {}
    V_frozen: Dict[tuple, float] = {}
    visit_count: Dict[tuple, int] = defaultdict(int)
    eval_results = []

    for episode in range(n_episodes):
        alpha = alpha_init / (1 + episode / 10000) if decay_alpha else alpha_init

        # Snapshot V_frozen every freeze_interval episodes
        if episode % freeze_interval == 0:
            V_frozen = dict(V)

        board = (0,) * 9
        player = 1
        # Randomly assign which player is the learning agent
        agent_player = 1 if rng.random() < 0.5 else -1
        trajectory = []  # Only agent's states

        while True:
            key = (board, player)

            if player == agent_player:
                # Agent uses live V
                trajectory.append((key, player))
                visit_count[key] += 1
                if key not in V:
                    V[key] = 0.0
                action = get_agent_action(board, player, V, epsilon, rng)
            else:
                # Frozen opponent uses V_frozen
                action = get_agent_action(board, player, V_frozen, epsilon, rng)

            board = ttt_make_move(board, action, player)
            player = -player

            winner = ttt_check_winner(board)
            if winner is not None:
                break

        # Only update V from the agent's trajectory
        for state_key, p in trajectory:
            if winner == 0:
                outcome = 0.0
            elif winner == p:
                outcome = 1.0
            else:
                outcome = -1.0
            V[state_key] += alpha * (outcome - V[state_key])

        if (episode + 1) % eval_interval == 0:
            metrics = evaluate_fast(V, visit_count, graph)
            metrics['episode'] = episode + 1
            eval_results.append(metrics)

    return {'V': V, 'visit_count': visit_count, 'eval_results': eval_results}


# =============================================================================
# 4. Fast Evaluation (uses pre-computed graph)
# =============================================================================

def evaluate_fast(V: Dict, visit_count: Dict, graph: GameGraph) -> dict:
    """Evaluate agent's value function against ground truth.

    Uses pre-computed game graph for speed -- no TicTacToe objects created.
    """
    all_states = graph.all_states
    n_total = len(all_states)

    # (a) Value R^2: all states, visited only, unvisited only
    v_true_all = []
    v_learned_all = []
    v_true_visited = []
    v_learned_visited = []
    v_true_unvisited = []
    v_learned_unvisited = []

    for key in all_states:
        vt = graph.value_cache[key]
        vl = V.get(key, 0.0)
        v_true_all.append(vt)
        v_learned_all.append(vl)
        if visit_count.get(key, 0) > 0:
            v_true_visited.append(vt)
            v_learned_visited.append(vl)
        else:
            v_true_unvisited.append(vt)
            v_learned_unvisited.append(vl)

    def compute_r2(y_true, y_pred):
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        if len(y_true) == 0:
            return float('nan')
        ss_res = np.sum((y_pred - y_true) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    value_r2_all = compute_r2(v_true_all, v_learned_all)
    value_r2_visited = compute_r2(v_true_visited, v_learned_visited)
    value_r2_unvisited = compute_r2(v_true_unvisited, v_learned_unvisited)

    # (b) Policy accuracy (over non-terminal states)
    correct = 0
    total_policy = 0
    for key in graph.non_terminal_keys:
        children = graph.children[key]
        if not children:
            continue

        total_policy += 1

        # Agent's greedy action: minimize opponent's V among children
        best_val = float('inf')
        best_moves = set()
        for move, child_key in children:
            child_v = V.get(child_key, 0.0)
            if child_v < best_val - 1e-12:
                best_val = child_v
                best_moves = {move}
            elif abs(child_v - best_val) < 1e-12:
                best_moves.add(move)

        # Check overlap with optimal
        optimal = graph.optimal_actions.get(key, set())
        if best_moves & optimal:
            correct += 1

    policy_accuracy = correct / total_policy if total_policy > 0 else 0.0

    # (c) State coverage
    visited = sum(1 for key in all_states if visit_count.get(key, 0) > 0)
    state_coverage = visited / n_total

    # (d) Greedy policy entropy (over visited non-terminal states with >1 legal move)
    # For each state, compute greedy action(s) = argmin of children's V.
    # If ties, policy is uniform over tied actions. Entropy of that distribution,
    # normalized by log(n_legal).
    entropy_sum = 0.0
    entropy_count = 0
    for key in graph.non_terminal_keys:
        if visit_count.get(key, 0) == 0:
            continue
        n_legal = graph.n_legal[key]
        if n_legal <= 1:
            continue

        children = graph.children[key]
        # Find greedy action(s): minimize opponent's V
        best_val = float('inf')
        n_best = 0
        for move, child_key in children:
            child_v = V.get(child_key, 0.0)
            if child_v < best_val - 1e-12:
                best_val = child_v
                n_best = 1
            elif abs(child_v - best_val) < 1e-12:
                n_best += 1

        # Greedy policy: uniform over n_best actions, zero on others
        # Entropy = log(n_best), normalized by log(n_legal)
        H = np.log(n_best) if n_best > 1 else 0.0
        H_max = np.log(n_legal)
        if H_max > 0:
            entropy_sum += H / H_max
            entropy_count += 1

    policy_entropy = entropy_sum / entropy_count if entropy_count > 0 else 0.0

    return {
        'value_r2': value_r2_all,
        'value_r2_visited': value_r2_visited,
        'value_r2_unvisited': value_r2_unvisited,
        'policy_accuracy': policy_accuracy,
        'state_coverage': state_coverage,
        'policy_entropy': policy_entropy,
    }


# =============================================================================
# 5. Main Experiment
# =============================================================================

def run_experiment():
    """Run the full self-play vs frozen-opponent experiment."""

    print("=" * 70)
    print("Self-Play Tic-Tac-Toe: Ouroboros Predictions Experiment")
    print("=" * 70)
    print()

    start_time = time.time()

    # --- Solve the game and build graph ---
    graph = GameGraph()
    graph.build()
    print()

    # --- Experiment parameters ---
    epsilons = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    n_episodes = 100_000
    eval_interval = 5_000
    alpha_init = 0.1
    freeze_interval = 5_000

    print(f"Training parameters:")
    print(f"  Episodes: {n_episodes:,}")
    print(f"  Alpha: {alpha_init} (decaying)")
    print(f"  Eval interval: {eval_interval:,}")
    print(f"  Epsilon values: {epsilons}")
    print(f"  Frozen opponent snapshot interval: {freeze_interval:,}")
    print(f"  Random seed: {RNG_SEED}")
    print()

    selfplay_results = {}
    frozen_results = {}

    for i, eps in enumerate(epsilons):
        print(f"[{i+1}/{len(epsilons)}] Epsilon = {eps:.3f}")

        # Self-play
        rng = np.random.default_rng(RNG_SEED)
        t0 = time.time()
        sp_result = train_selfplay(n_episodes, eps, alpha_init, eval_interval, graph, rng)
        t1 = time.time()
        selfplay_results[eps] = sp_result
        final_sp = sp_result['eval_results'][-1]
        print(f"  Self-play:  R2={final_sp['value_r2']:.4f}  "
              f"R2v={final_sp['value_r2_visited']:.4f}  "
              f"R2u={final_sp['value_r2_unvisited']:.4f}  "
              f"Policy={final_sp['policy_accuracy']:.4f}  "
              f"Coverage={final_sp['state_coverage']:.4f}  "
              f"Entropy={final_sp['policy_entropy']:.4f}  "
              f"({t1-t0:.1f}s)")

        # Frozen-opponent
        rng = np.random.default_rng(RNG_SEED)
        t0 = time.time()
        fr_result = train_frozen(n_episodes, eps, alpha_init, eval_interval, graph, rng,
                                 freeze_interval=freeze_interval)
        t1 = time.time()
        frozen_results[eps] = fr_result
        final_fr = fr_result['eval_results'][-1]
        print(f"  Frozen:     R2={final_fr['value_r2']:.4f}  "
              f"R2v={final_fr['value_r2_visited']:.4f}  "
              f"R2u={final_fr['value_r2_unvisited']:.4f}  "
              f"Policy={final_fr['policy_accuracy']:.4f}  "
              f"Coverage={final_fr['state_coverage']:.4f}  "
              f"Entropy={final_fr['policy_entropy']:.4f}  "
              f"({t1-t0:.1f}s)")
        print()

    elapsed = time.time() - start_time
    print(f"Total training time: {elapsed:.1f}s")
    print()

    # --- Analysis ---
    analyze_results(selfplay_results, frozen_results, epsilons, graph)

    # --- Plotting ---
    if HAS_MATPLOTLIB:
        plot_results(selfplay_results, frozen_results, epsilons)
    else:
        print("\n(matplotlib not available -- skipping plots)")


def analyze_results(selfplay_results, frozen_results, epsilons, graph):
    """Analyze and print comparison table."""

    print()
    print("=" * 100)
    print("FULL EPSILON SWEEP RESULTS")
    print("=" * 100)

    # Self-play sweep
    print("\nSelf-Play Condition (converged values = last evaluation point):")
    print(f"{'Epsilon':>8} | {'R2 all':>8} | {'R2 vis':>8} | {'R2 unvis':>9} | {'Policy':>8} | {'Coverage':>9} | {'Entropy':>8} | {'Osc CV':>8}")
    print("-" * 95)

    sp_final = {}
    for eps in epsilons:
        results = selfplay_results[eps]['eval_results']
        final = results[-1]

        # Convergence oscillation: CV of value R2 over last 20% of training
        n_evals = len(results)
        tail_start = int(0.8 * n_evals)
        tail_r2 = [r['value_r2'] for r in results[tail_start:]]
        if len(tail_r2) > 1 and np.mean(tail_r2) != 0:
            osc_cv = np.std(tail_r2) / abs(np.mean(tail_r2))
        else:
            osc_cv = 0.0

        sp_final[eps] = {**final, 'osc_cv': osc_cv}
        r2v = final['value_r2_visited']
        r2u = final['value_r2_unvisited']
        r2v_str = f"{r2v:8.4f}" if not np.isnan(r2v) else "     NaN"
        r2u_str = f"{r2u:9.4f}" if not np.isnan(r2u) else "      NaN"
        print(f"{eps:8.3f} | {final['value_r2']:8.4f} | {r2v_str} | {r2u_str} | "
              f"{final['policy_accuracy']:8.4f} | {final['state_coverage']:9.4f} | "
              f"{final['policy_entropy']:8.4f} | {osc_cv:8.5f}")

    # Frozen sweep
    print("\nFrozen-Opponent Condition (converged values = last evaluation point):")
    print(f"{'Epsilon':>8} | {'R2 all':>8} | {'R2 vis':>8} | {'R2 unvis':>9} | {'Policy':>8} | {'Coverage':>9} | {'Entropy':>8} | {'Osc CV':>8}")
    print("-" * 95)

    fr_final = {}
    for eps in epsilons:
        results = frozen_results[eps]['eval_results']
        final = results[-1]

        n_evals = len(results)
        tail_start = int(0.8 * n_evals)
        tail_r2 = [r['value_r2'] for r in results[tail_start:]]
        if len(tail_r2) > 1 and np.mean(tail_r2) != 0:
            osc_cv = np.std(tail_r2) / abs(np.mean(tail_r2))
        else:
            osc_cv = 0.0

        fr_final[eps] = {**final, 'osc_cv': osc_cv}
        r2v = final['value_r2_visited']
        r2u = final['value_r2_unvisited']
        r2v_str = f"{r2v:8.4f}" if not np.isnan(r2v) else "     NaN"
        r2u_str = f"{r2u:9.4f}" if not np.isnan(r2u) else "      NaN"
        print(f"{eps:8.3f} | {final['value_r2']:8.4f} | {r2v_str} | {r2u_str} | "
              f"{final['policy_accuracy']:8.4f} | {final['state_coverage']:9.4f} | "
              f"{final['policy_entropy']:8.4f} | {osc_cv:8.5f}")

    # Find best epsilon for each condition (by value R2 all)
    best_sp_eps = max(epsilons, key=lambda e: sp_final[e]['value_r2'])
    best_fr_eps = max(epsilons, key=lambda e: fr_final[e]['value_r2'])

    # Find epsilon that maximizes each metric for self-play
    best_sp_policy_eps = max(epsilons, key=lambda e: sp_final[e]['policy_accuracy'])

    sp_best = sp_final[best_sp_eps]
    fr_best = fr_final[best_fr_eps]

    # Check for oscillation
    sp_oscillates = "Yes" if sp_best['osc_cv'] > 0.01 else "No"
    fr_oscillates = "Yes" if fr_best['osc_cv'] > 0.01 else "No"

    # Get R2 visited/unvisited strings for table
    def fmt_r2(val):
        return f"{val:.4f}" if not np.isnan(val) else "NaN"

    print()
    print("=" * 85)
    print("OUROBOROS PREDICTIONS vs OBSERVATIONS")
    print("=" * 85)
    print()
    print(f"{'Metric':<28} | {'Prediction':>10} | {'Self-Play (best eps)':>22} | {'Frozen (best eps)':>20}")
    print("-" * 85)
    print(f"{'Value R2 (all states)':<28} | {INV_PHI_SQ:10.4f} | {sp_best['value_r2']:10.4f} (e={best_sp_eps:.2f})   | "
          f"{fr_best['value_r2']:8.4f} (e={best_fr_eps:.2f})")
    print(f"{'Value R2 (visited only)':<28} | {'---':>10} | {fmt_r2(sp_best['value_r2_visited']):>10} (e={best_sp_eps:.2f})   | "
          f"{fmt_r2(fr_best['value_r2_visited']):>8} (e={best_fr_eps:.2f})")
    print(f"{'Value R2 (unvisited only)':<28} | {'---':>10} | {fmt_r2(sp_best['value_r2_unvisited']):>10} (e={best_sp_eps:.2f})   | "
          f"{fmt_r2(fr_best['value_r2_unvisited']):>8} (e={best_fr_eps:.2f})")
    print(f"{'Policy accuracy':<28} | {INV_PHI_SQ:10.4f} | "
          f"{sp_final[best_sp_policy_eps]['policy_accuracy']:10.4f} (e={best_sp_policy_eps:.2f})   | "
          f"{fr_final[best_fr_eps]['policy_accuracy']:8.4f} (e={best_fr_eps:.2f})")
    print(f"{'Optimal exploration (eps)':<28} | {ONE_MINUS_NU:10.4f} | {best_sp_eps:10.3f}              | "
          f"{best_fr_eps:8.3f}           ")
    print(f"{'State coverage':<28} | {INV_PHI_SQ:10.4f} | {sp_best['state_coverage']:10.4f} (e={best_sp_eps:.2f})   | "
          f"{fr_best['state_coverage']:8.4f} (e={best_fr_eps:.2f})")
    print(f"{'Policy entropy (greedy)':<28} | {ONE_MINUS_NU:10.4f} | {sp_best['policy_entropy']:10.4f} (e={best_sp_eps:.2f})   | "
          f"{fr_best['policy_entropy']:8.4f} (e={best_fr_eps:.2f})")
    print(f"{'Convergence oscillation':<28} | {'Yes':>10} | {sp_oscillates:>22} | {fr_oscillates:>20}")
    print()

    # Reference constants
    print("Reference golden-ratio constants:")
    print(f"  1/phi^2 = {INV_PHI_SQ:.6f}")
    print(f"  1/phi   = {INV_PHI:.6f}")
    print(f"  1-nu    = {ONE_MINUS_NU:.6f}  (nu = phi/sqrt(5))")
    print(f"  nu      = {NU:.6f}")
    print()

    # Summary assessment
    print("=" * 85)
    print("ASSESSMENT")
    print("=" * 85)

    r2_ratio = sp_best['value_r2'] / fr_best['value_r2'] if fr_best['value_r2'] > 0 else float('inf')
    print(f"\nSelf-play R2 / Frozen R2 = {r2_ratio:.4f}")
    print(f"  (Prediction: self-play should be constrained relative to frozen)")

    r2_error = abs(sp_best['value_r2'] - INV_PHI_SQ) / INV_PHI_SQ
    eps_error = abs(best_sp_eps - ONE_MINUS_NU) / ONE_MINUS_NU
    coverage_error = abs(sp_best['state_coverage'] - INV_PHI_SQ) / INV_PHI_SQ
    entropy_error = abs(sp_best['policy_entropy'] - ONE_MINUS_NU) / ONE_MINUS_NU

    print(f"\nDeviation from predictions:")
    print(f"  Value R2 vs 1/phi^2:       {r2_error*100:6.1f}%  (observed={sp_best['value_r2']:.4f}, predicted={INV_PHI_SQ:.4f})")
    print(f"  Optimal eps vs 1-nu:       {eps_error*100:6.1f}%  (observed={best_sp_eps:.3f}, predicted={ONE_MINUS_NU:.4f})")
    print(f"  State coverage vs 1/phi^2: {coverage_error*100:6.1f}%  (observed={sp_best['state_coverage']:.4f}, predicted={INV_PHI_SQ:.4f})")
    print(f"  Policy entropy vs 1-nu:    {entropy_error*100:6.1f}%  (observed={sp_best['policy_entropy']:.4f}, predicted={ONE_MINUS_NU:.4f})")

    policy_error = abs(sp_final[best_sp_policy_eps]['policy_accuracy'] - INV_PHI_SQ) / INV_PHI_SQ
    print(f"  Policy acc vs 1/phi^2:     {policy_error*100:6.1f}%  (observed={sp_final[best_sp_policy_eps]['policy_accuracy']:.4f}, predicted={INV_PHI_SQ:.4f})")


def plot_results(selfplay_results, frozen_results, epsilons):
    """Create figure with three panels."""
    import os

    sp_final_r2 = {eps: selfplay_results[eps]['eval_results'][-1]['value_r2'] for eps in epsilons}
    fr_final_r2 = {eps: frozen_results[eps]['eval_results'][-1]['value_r2'] for eps in epsilons}
    sp_final_r2v = {eps: selfplay_results[eps]['eval_results'][-1]['value_r2_visited'] for eps in epsilons}
    fr_final_r2v = {eps: frozen_results[eps]['eval_results'][-1]['value_r2_visited'] for eps in epsilons}
    best_sp_eps = max(epsilons, key=lambda e: sp_final_r2[e])
    best_fr_eps = max(epsilons, key=lambda e: fr_final_r2[e])

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Panel 1: Value R2 (all) vs episode for self-play vs frozen (best eps each)
    ax1 = axes[0]
    sp_data = selfplay_results[best_sp_eps]['eval_results']
    fr_data = frozen_results[best_fr_eps]['eval_results']

    ax1.plot([d['episode'] for d in sp_data], [d['value_r2'] for d in sp_data],
             'b-', label=f'Self-play (eps={best_sp_eps})', linewidth=1.5)
    ax1.plot([d['episode'] for d in fr_data], [d['value_r2'] for d in fr_data],
             'r-', label=f'Frozen (eps={best_fr_eps})', linewidth=1.5)
    ax1.axhline(y=INV_PHI_SQ, color='gold', linestyle='--', alpha=0.7, label=f'1/phi^2 = {INV_PHI_SQ:.3f}')
    ax1.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5, label='Perfect')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Value R^2 (all states)')
    ax1.set_title('Learning Curves (best epsilon)')
    ax1.legend(fontsize=8)
    ax1.set_ylim(-0.1, 1.1)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Value R2 (all) at convergence vs epsilon (both conditions)
    ax2 = axes[1]
    ax2.plot(epsilons, [sp_final_r2[e] for e in epsilons], 'bo-', label='Self-play', linewidth=1.5)
    ax2.plot(epsilons, [fr_final_r2[e] for e in epsilons], 'rs-', label='Frozen', linewidth=1.5)
    ax2.axhline(y=INV_PHI_SQ, color='gold', linestyle='--', alpha=0.7, label=f'1/phi^2 = {INV_PHI_SQ:.3f}')
    ax2.axvline(x=ONE_MINUS_NU, color='green', linestyle='--', alpha=0.7, label=f'1-nu = {ONE_MINUS_NU:.3f}')
    ax2.set_xlabel('Epsilon')
    ax2.set_ylabel('Value R^2 (all) at convergence')
    ax2.set_title('Epsilon Sweep: R^2 (all states)')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Panel 3: Value R2 (visited only) at convergence vs epsilon (both conditions)
    ax3 = axes[2]
    sp_r2v_vals = [sp_final_r2v[e] if not np.isnan(sp_final_r2v[e]) else 0.0 for e in epsilons]
    fr_r2v_vals = [fr_final_r2v[e] if not np.isnan(fr_final_r2v[e]) else 0.0 for e in epsilons]
    ax3.plot(epsilons, sp_r2v_vals, 'bo-', label='Self-play', linewidth=1.5)
    ax3.plot(epsilons, fr_r2v_vals, 'rs-', label='Frozen', linewidth=1.5)
    ax3.axhline(y=INV_PHI_SQ, color='gold', linestyle='--', alpha=0.7, label=f'1/phi^2 = {INV_PHI_SQ:.3f}')
    ax3.axvline(x=ONE_MINUS_NU, color='green', linestyle='--', alpha=0.7, label=f'1-nu = {ONE_MINUS_NU:.3f}')
    ax3.set_xlabel('Epsilon')
    ax3.set_ylabel('Value R^2 (visited) at convergence')
    ax3.set_title('Epsilon Sweep: R^2 (visited states)')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_path = os.path.join(script_dir, 'ttt_results.png')
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    print(f"\nFigure saved to: {fig_path}")
    plt.close()


if __name__ == '__main__':
    run_experiment()
