"""
MVSU Trading Pre-Training: Optimal w_cross Computation for Pine Script Indicator
==================================================================================
Computes optimal w_cross values for the 10 indicator pairs in the MVSU trading
indicator by sweeping w_cross and measuring directional prediction accuracy.

The goal: find which pairs need the most decontamination (most negative w_cross)
and output ready-to-paste Pine Script input parameters.

Indicators (matching Pine Script exactly):
  A: RSI(14) normalized to [-1, 1]
  B: Stochastic(14) normalized to [-1, 1]
  C: MACD(12, 26, 9) histogram normalized
  D: MFI(14) normalized to [-1, 1]
  E: ADX net direction (+DI - -DI) normalized

Pairs: AB, AC, AD, AE, BC, BD, BE, CD, CE, DE

Author: Claude (MVSU Trading Framework)
"""

import sys
import io
import os
import numpy as np

# Windows Unicode fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        except Exception:
            pass

# ==========================================================================
# Constants
# ==========================================================================
N_BARS = 2000
N_SEEDS = 3
SEEDS = [42, 123, 456]
W_CROSS_SWEEP = np.linspace(-1.0, 0.0, 51)  # -1.0 to 0.0 in 0.02 steps

# Indicator parameters (matching Pine Script)
RSI_PERIOD = 14
STOCH_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
MFI_PERIOD = 14
ADX_PERIOD = 14

# Pairs to test
PAIRS = [
    ('A', 'B'), ('A', 'C'), ('A', 'D'), ('A', 'E'),
    ('B', 'C'), ('B', 'D'), ('B', 'E'),
    ('C', 'D'), ('C', 'E'),
    ('D', 'E'),
]

PAIR_NAMES = {
    'A': 'RSI',
    'B': 'Stoch',
    'C': 'MACD',
    'D': 'MFI',
    'E': 'ADX',
}


# ==========================================================================
# Helper functions
# ==========================================================================
def exponential_moving_avg(x, period):
    """Compute EMA matching Pine Script ta.ema()."""
    alpha = 2.0 / (period + 1.0)
    ema = np.zeros_like(x)
    ema[0] = x[0]
    for i in range(1, len(x)):
        ema[i] = alpha * x[i] + (1.0 - alpha) * ema[i - 1]
    return ema


def rolling_min(x, period):
    """Compute rolling minimum over period."""
    result = np.zeros_like(x)
    for i in range(len(x)):
        start = max(0, i - period + 1)
        result[i] = np.min(x[start:i + 1])
    return result


def rolling_max(x, period):
    """Compute rolling maximum over period."""
    result = np.zeros_like(x)
    for i in range(len(x)):
        start = max(0, i - period + 1)
        result[i] = np.max(x[start:i + 1])
    return result


def rolling_sum(x, period):
    """Compute rolling sum over period."""
    result = np.zeros_like(x)
    for i in range(len(x)):
        start = max(0, i - period + 1)
        result[i] = np.sum(x[start:i + 1])
    return result


def true_range(high, low, close):
    """Compute True Range."""
    tr = np.zeros(len(high))
    tr[0] = high[0] - low[0]
    for i in range(1, len(high)):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i - 1])
        lc = abs(low[i] - close[i - 1])
        tr[i] = max(hl, hc, lc)
    return tr


def normalize_to_pm1(x, lookback=100):
    """Normalize to [-1, 1] using rolling min/max."""
    result = np.zeros_like(x)
    for i in range(len(x)):
        start = max(0, i - lookback + 1)
        window = x[start:i + 1]
        min_val = np.min(window)
        max_val = np.max(window)
        if max_val - min_val > 1e-10:
            result[i] = 2.0 * (x[i] - min_val) / (max_val - min_val) - 1.0
        else:
            result[i] = 0.0
    return result


# ==========================================================================
# Synthetic price data generation
# ==========================================================================
def generate_ohlcv(n_bars, seed):
    """Generate realistic synthetic OHLCV data."""
    rng = np.random.RandomState(seed)

    # Start price
    base_price = 100.0

    # Generate returns with trend and mean-reversion components
    trend = 0.0001 * np.sin(2 * np.pi * np.arange(n_bars) / 200.0)  # slow trend
    mean_reversion = np.zeros(n_bars)
    returns = np.zeros(n_bars)

    for i in range(n_bars):
        # Random walk with momentum and mean reversion
        if i > 0:
            mean_reversion[i] = -0.02 * returns[i - 1]  # mean revert
        noise = rng.randn() * 0.01  # daily volatility ~1%
        returns[i] = trend[i] + mean_reversion[i] + noise

    # Compute close prices
    close = base_price * np.exp(np.cumsum(returns))

    # Generate OHLV from close
    high = np.zeros(n_bars)
    low = np.zeros(n_bars)
    open_price = np.zeros(n_bars)
    volume = np.zeros(n_bars)

    for i in range(n_bars):
        # Intrabar volatility
        intrabar_range = abs(rng.randn()) * 0.005 * close[i]
        high[i] = close[i] + intrabar_range * rng.uniform(0.3, 1.0)
        low[i] = close[i] - intrabar_range * rng.uniform(0.3, 1.0)

        # Open is yesterday's close with small gap
        if i > 0:
            gap = rng.randn() * 0.002 * close[i - 1]
            open_price[i] = close[i - 1] + gap
        else:
            open_price[i] = close[i]

        # Volume correlated with volatility
        vol_base = 1000000
        vol_vol = abs(returns[i]) * 5000000
        volume[i] = vol_base + vol_vol + abs(rng.randn()) * 200000

    return open_price, high, low, close, volume


# ==========================================================================
# Indicator computations
# ==========================================================================
def compute_rsi(close, period):
    """Compute RSI and normalize to [-1, 1]."""
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = exponential_moving_avg(gain, period)
    avg_loss = exponential_moving_avg(loss, period)

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100.0 - 100.0 / (1.0 + rs)

    # Normalize to [-1, 1]: RSI in [0, 100] -> [-1, 1]
    rsi_normalized = (rsi - 50.0) / 50.0
    return rsi_normalized


def compute_stochastic(high, low, close, period):
    """Compute Stochastic and normalize to [-1, 1]."""
    lowest_low = rolling_min(low, period)
    highest_high = rolling_max(high, period)

    stoch = 100.0 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)

    # Normalize to [-1, 1]: Stoch in [0, 100] -> [-1, 1]
    stoch_normalized = (stoch - 50.0) / 50.0
    return stoch_normalized


def compute_macd(close, fast, slow, signal):
    """Compute MACD histogram and normalize."""
    ema_fast = exponential_moving_avg(close, fast)
    ema_slow = exponential_moving_avg(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = exponential_moving_avg(macd_line, signal)
    histogram = macd_line - signal_line

    # Normalize histogram to [-1, 1] using rolling window
    histogram_normalized = normalize_to_pm1(histogram, lookback=100)
    return histogram_normalized


def compute_mfi(high, low, close, volume, period):
    """Compute MFI and normalize to [-1, 1]."""
    typical_price = (high + low + close) / 3.0
    raw_money_flow = typical_price * volume

    # Determine positive and negative flows
    delta = np.diff(typical_price, prepend=typical_price[0])
    positive_flow = np.where(delta > 0, raw_money_flow, 0)
    negative_flow = np.where(delta <= 0, raw_money_flow, 0)

    positive_mf_sum = rolling_sum(positive_flow, period)
    negative_mf_sum = rolling_sum(negative_flow, period)

    mfi = 100.0 - 100.0 / (1.0 + positive_mf_sum / (negative_mf_sum + 1e-10))

    # Normalize to [-1, 1]: MFI in [0, 100] -> [-1, 1]
    mfi_normalized = (mfi - 50.0) / 50.0
    return mfi_normalized


def compute_adx(high, low, close, period):
    """Compute ADX net direction (+DI - -DI) and normalize."""
    # Directional movement
    up_move = np.diff(high, prepend=high[0])
    down_move = -np.diff(low, prepend=low[0])

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    tr = true_range(high, low, close)

    # Smooth with EMA
    plus_di = 100.0 * exponential_moving_avg(plus_dm, period) / (exponential_moving_avg(tr, period) + 1e-10)
    minus_di = 100.0 * exponential_moving_avg(minus_dm, period) / (exponential_moving_avg(tr, period) + 1e-10)

    # Net direction
    net_direction = plus_di - minus_di

    # Normalize to [-1, 1]
    net_normalized = normalize_to_pm1(net_direction, lookback=100)
    return net_normalized


# ==========================================================================
# MVSU decontamination
# ==========================================================================
def compute_decontaminated_signal(signal_a, signal_b, w_cross):
    """Compute decontaminated signal using MVSU formula."""
    # signal_out = A - w_cross * B
    # This is the basic MVSU decontamination
    decontaminated = signal_a + w_cross * signal_b  # w_cross is negative, so this is A - |w_cross| * B
    return decontaminated


def compute_directional_accuracy(signal, price_returns):
    """Measure how well signal predicts next-bar return direction.

    Returns: fraction of bars where sign(signal[t]) == sign(return[t+1])
    """
    # Skip first 100 bars for warmup
    warmup = 100

    signal_sign = np.sign(signal[warmup:-1])  # signal at time t
    return_sign = np.sign(price_returns[warmup + 1:])  # return at time t+1

    matches = (signal_sign == return_sign).astype(float)
    accuracy = np.mean(matches)

    return accuracy


# ==========================================================================
# Sweep w_cross for a pair
# ==========================================================================
def sweep_pair(indicator_a, indicator_b, price_returns):
    """Sweep w_cross from -1.0 to 0.0 and find optimal value.

    Returns: (optimal_w_cross, optimal_accuracy, accuracy_curve)
    """
    accuracies = []

    for w_cross in W_CROSS_SWEEP:
        decontaminated = compute_decontaminated_signal(indicator_a, indicator_b, w_cross)
        accuracy = compute_directional_accuracy(decontaminated, price_returns)
        accuracies.append(accuracy)

    accuracies = np.array(accuracies)
    best_idx = np.argmax(accuracies)
    optimal_w_cross = W_CROSS_SWEEP[best_idx]
    optimal_accuracy = accuracies[best_idx]

    return optimal_w_cross, optimal_accuracy, accuracies


# ==========================================================================
# Main experiment
# ==========================================================================
def run_pretraining():
    """Run the full pre-training experiment."""

    print("=" * 70)
    print("MVSU TRADING PRE-TRAINING")
    print("Optimal w_cross Computation for Pine Script Indicator")
    print("=" * 70)
    print(f"  Bars per seed: {N_BARS}")
    print(f"  Seeds: {SEEDS}")
    print(f"  w_cross sweep: {W_CROSS_SWEEP[0]:.2f} to {W_CROSS_SWEEP[-1]:.2f} ({len(W_CROSS_SWEEP)} points)")
    print()

    # Store results across seeds
    all_optimal_w_cross = {pair: [] for pair in PAIRS}
    all_optimal_accuracy = {pair: [] for pair in PAIRS}
    all_accuracy_curves = {pair: [] for pair in PAIRS}
    all_correlations = []

    for seed_idx, seed in enumerate(SEEDS):
        print(f"Running seed {seed} ({seed_idx + 1}/{N_SEEDS})...")

        # Generate synthetic data
        open_price, high, low, close, volume = generate_ohlcv(N_BARS, seed)
        price_returns = np.diff(close, prepend=close[0])

        # Compute all 5 indicators
        print("  Computing indicators...")
        indicator_A = compute_rsi(close, RSI_PERIOD)
        indicator_B = compute_stochastic(high, low, close, STOCH_PERIOD)
        indicator_C = compute_macd(close, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
        indicator_D = compute_mfi(high, low, close, volume, MFI_PERIOD)
        indicator_E = compute_adx(high, low, close, ADX_PERIOD)

        indicators = {
            'A': indicator_A,
            'B': indicator_B,
            'C': indicator_C,
            'D': indicator_D,
            'E': indicator_E,
        }

        # Compute correlation matrix
        indicator_matrix = np.column_stack([indicator_A, indicator_B, indicator_C, indicator_D, indicator_E])
        correlation_matrix = np.corrcoef(indicator_matrix[100:].T)  # skip warmup
        all_correlations.append(correlation_matrix)

        # Sweep all 10 pairs
        print("  Sweeping w_cross for all pairs...")
        for pair in PAIRS:
            label_a, label_b = pair
            ind_a = indicators[label_a]
            ind_b = indicators[label_b]

            optimal_w, optimal_acc, acc_curve = sweep_pair(ind_a, ind_b, price_returns)

            all_optimal_w_cross[pair].append(optimal_w)
            all_optimal_accuracy[pair].append(optimal_acc)
            all_accuracy_curves[pair].append(acc_curve)

    print()

    # Compute mean results
    mean_optimal_w_cross = {pair: np.mean(all_optimal_w_cross[pair]) for pair in PAIRS}
    mean_optimal_accuracy = {pair: np.mean(all_optimal_accuracy[pair]) for pair in PAIRS}
    mean_accuracy_curves = {pair: np.mean(all_accuracy_curves[pair], axis=0) for pair in PAIRS}
    mean_correlation_matrix = np.mean(all_correlations, axis=0)

    # Rank pairs by optimal w_cross (most negative = most decontamination needed)
    sorted_pairs = sorted(PAIRS, key=lambda p: mean_optimal_w_cross[p])

    # Print results table
    print("=" * 70)
    print("RESULTS: Optimal w_cross per Pair")
    print("=" * 70)
    print()
    print(f"{'Pair':<12} {'Optimal w_cross':>15} {'Accuracy':>12} {'Quality':>10}")
    print("-" * 70)

    for pair in sorted_pairs:
        label_a, label_b = pair
        pair_name = f"{PAIR_NAMES[label_a]}-{PAIR_NAMES[label_b]}"
        w_cross = mean_optimal_w_cross[pair]
        accuracy = mean_optimal_accuracy[pair]

        # Quality: how much better than random (0.5)
        quality = (accuracy - 0.5) * 100

        print(f"{pair_name:<12} {w_cross:>15.4f} {accuracy:>12.4f} {quality:>9.1f}%")

    print()

    # Top 3 pairs
    print("=" * 70)
    print("TOP 3 PAIRS (Most Decontamination Needed)")
    print("=" * 70)
    print()

    for i, pair in enumerate(sorted_pairs[:3], 1):
        label_a, label_b = pair
        pair_name = f"{PAIR_NAMES[label_a]}-{PAIR_NAMES[label_b]}"
        w_cross = mean_optimal_w_cross[pair]
        accuracy = mean_optimal_accuracy[pair]
        quality = (accuracy - 0.5) * 100

        print(f"{i}. {pair_name}: w_cross = {w_cross:.4f}, accuracy = {accuracy:.4f} (+{quality:.1f}%)")

    print()

    # Correlation matrix
    print("=" * 70)
    print("INDICATOR CORRELATION MATRIX")
    print("=" * 70)
    print()
    print(f"{'':>6}", end='')
    for label in ['A', 'B', 'C', 'D', 'E']:
        print(f"{PAIR_NAMES[label]:>8}", end='')
    print()
    print("-" * 50)

    for i, label_i in enumerate(['A', 'B', 'C', 'D', 'E']):
        print(f"{PAIR_NAMES[label_i]:>6}", end='')
        for j, label_j in enumerate(['A', 'B', 'C', 'D', 'E']):
            print(f"{mean_correlation_matrix[i, j]:>8.3f}", end='')
        print()

    print()

    # Pine Script parameters
    print("=" * 70)
    print("PINE SCRIPT INPUT PARAMETERS (Copy-Paste Ready)")
    print("=" * 70)
    print()

    for pair in PAIRS:
        label_a, label_b = pair
        pair_code = f"{label_a}{label_b}"
        w_cross = mean_optimal_w_cross[pair]
        print(f'input float w_cross_{pair_code} = {w_cross:.4f}  // {PAIR_NAMES[label_a]}-{PAIR_NAMES[label_b]}')

    print()

    return {
        'pairs': PAIRS,
        'optimal_w_cross': mean_optimal_w_cross,
        'optimal_accuracy': mean_optimal_accuracy,
        'accuracy_curves': mean_accuracy_curves,
        'correlation_matrix': mean_correlation_matrix,
        'sorted_pairs': sorted_pairs,
    }


# ==========================================================================
# Plotting
# ==========================================================================
def create_plots(results):
    """Generate results plots."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available, skipping plots.")
        return

    pairs = results['pairs']
    optimal_w_cross = results['optimal_w_cross']
    optimal_accuracy = results['optimal_accuracy']
    accuracy_curves = results['accuracy_curves']
    correlation_matrix = results['correlation_matrix']
    sorted_pairs = results['sorted_pairs']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("MVSU Trading Pre-Training Results", fontsize=14, fontweight='bold')

    # Plot 1: w_cross sweep curves for all pairs
    ax = axes[0, 0]
    colors = plt.cm.tab10(np.linspace(0, 1, len(pairs)))

    for i, pair in enumerate(pairs):
        label_a, label_b = pair
        pair_name = f"{PAIR_NAMES[label_a]}-{PAIR_NAMES[label_b]}"
        ax.plot(W_CROSS_SWEEP, accuracy_curves[pair],
                color=colors[i], label=pair_name, alpha=0.7, linewidth=1.5)

    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Random (0.5)')
    ax.set_xlabel('w_cross')
    ax.set_ylabel('Directional Accuracy')
    ax.set_title('Accuracy vs w_cross for All Pairs')
    ax.legend(fontsize=7, ncol=2, loc='upper right')
    ax.grid(True, alpha=0.3)

    # Plot 2: Bar chart of optimal w_cross per pair
    ax = axes[0, 1]
    pair_names = [f"{PAIR_NAMES[p[0]]}-{PAIR_NAMES[p[1]]}" for p in sorted_pairs]
    w_cross_values = [optimal_w_cross[p] for p in sorted_pairs]

    bars = ax.barh(pair_names, w_cross_values, color='steelblue', edgecolor='black')
    ax.axvline(x=0, color='red', linestyle='--', alpha=0.5)
    ax.set_xlabel('Optimal w_cross')
    ax.set_title('Optimal w_cross per Pair (Sorted)')
    ax.grid(True, alpha=0.3, axis='x')

    # Color the top 3 differently
    for i in range(min(3, len(bars))):
        bars[i].set_color('darkred')

    # Plot 3: Correlation matrix heatmap
    ax = axes[1, 0]
    labels = ['RSI', 'Stoch', 'MACD', 'MFI', 'ADX']

    im = ax.imshow(correlation_matrix, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
    ax.set_xticks(np.arange(5))
    ax.set_yticks(np.arange(5))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    # Add correlation values
    for i in range(5):
        for j in range(5):
            text = ax.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                         ha='center', va='center', color='black', fontsize=9)

    ax.set_title('Indicator Correlation Matrix')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    # Plot 4: Best pair example (decontaminated vs raw)
    ax = axes[1, 1]

    # Use the first seed's data for visualization
    seed = SEEDS[0]
    open_price, high, low, close, volume = generate_ohlcv(N_BARS, seed)
    price_returns = np.diff(close, prepend=close[0])

    # Compute indicators
    indicator_A = compute_rsi(close, RSI_PERIOD)
    indicator_B = compute_stochastic(high, low, close, STOCH_PERIOD)
    indicator_C = compute_macd(close, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    indicator_D = compute_mfi(high, low, close, volume, MFI_PERIOD)
    indicator_E = compute_adx(high, low, close, ADX_PERIOD)

    indicators = {'A': indicator_A, 'B': indicator_B, 'C': indicator_C,
                  'D': indicator_D, 'E': indicator_E}

    # Get best pair
    best_pair = sorted_pairs[0]
    label_a, label_b = best_pair
    pair_name = f"{PAIR_NAMES[label_a]}-{PAIR_NAMES[label_b]}"

    ind_a = indicators[label_a]
    ind_b = indicators[label_b]
    w_cross_best = optimal_w_cross[best_pair]

    # Raw signal (just A)
    raw_signal = ind_a

    # Decontaminated signal
    decontaminated = compute_decontaminated_signal(ind_a, ind_b, w_cross_best)

    # Plot a window
    start_idx = 500
    end_idx = 700
    t = np.arange(start_idx, end_idx)

    ax.plot(t, raw_signal[start_idx:end_idx],
            color='orange', label=f'Raw ({PAIR_NAMES[label_a]})', alpha=0.7, linewidth=1.5)
    ax.plot(t, decontaminated[start_idx:end_idx],
            color='blue', label=f'Decontaminated (w_cross={w_cross_best:.3f})',
            alpha=0.7, linewidth=1.5)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)

    ax.set_xlabel('Bar Index')
    ax.set_ylabel('Normalized Signal')
    ax.set_title(f'Best Pair: {pair_name} (Raw vs Decontaminated)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "mvsu_trading_pretrain_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to: {out_path}")
    print()
    plt.close()


# ==========================================================================
# Main
# ==========================================================================
def main():
    results = run_pretraining()

    print("Generating plots...")
    create_plots(results)

    print("=" * 70)
    print("PRE-TRAINING COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Copy the Pine Script input parameters above")
    print("  2. Paste them into your TradingView indicator")
    print("  3. Use the top 3 pairs for your MVSU trading signals")
    print()


if __name__ == "__main__":
    main()
