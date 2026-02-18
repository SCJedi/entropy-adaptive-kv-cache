"""
MVSU Trading Test: Real Market Data Validation
================================================
Tests whether the MVSU multi-pair decontamination indicator actually works
for trading signals using real market data from yfinance.

Compares:
  - Raw indicator signals
  - Simple average of indicator pairs
  - MVSU decontaminated signals (with walk-forward validation)

Symbols: SPY (S&P 500 ETF), GLD (Gold ETF)

Author: Claude (MVSU Trading Framework)
"""

import sys
import io
import os
import warnings

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

warnings.filterwarnings("ignore")

import numpy as np

# matplotlib Agg backend
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ==========================================================================
# Constants
# ==========================================================================
SYMBOLS = ["SPY", "GLD"]
W_CROSS_SWEEP = np.linspace(-1.0, 0.0, 51)

# Indicator parameters (matching Pine Script)
RSI_PERIOD = 14
STOCH_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
MFI_PERIOD = 14
ADX_PERIOD = 14

WARMUP = 100  # bars to skip for indicator warmup

# Walk-forward split
TRAIN_FRACTION = 0.6

# Trading thresholds
BUY_THRESHOLD = 0.3
SELL_THRESHOLD = -0.3

# Pairs
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
# Data Fetching
# ==========================================================================
def fetch_data(symbol, period="2y", interval="1d"):
    """Fetch real OHLCV data using yfinance."""
    try:
        import yfinance as yf
        print(f"  Downloading {symbol} via yfinance...")
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        if df is None or len(df) == 0:
            raise ValueError(f"No data returned for {symbol}")

        # Handle multi-level columns from yfinance
        if hasattr(df.columns, 'levels') and len(df.columns.levels) > 1:
            df.columns = df.columns.get_level_values(0)

        # Extract arrays
        open_price = df['Open'].values.astype(float)
        high = df['High'].values.astype(float)
        low = df['Low'].values.astype(float)
        close = df['Close'].values.astype(float)
        volume = df['Volume'].values.astype(float)
        dates = df.index.to_pydatetime()

        print(f"  Got {len(close)} bars for {symbol} "
              f"({dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')})")
        return open_price, high, low, close, volume, dates

    except Exception as e:
        print(f"  yfinance failed for {symbol}: {e}")
        print(f"  Trying pandas-datareader...")
        try:
            import pandas_datareader.data as web
            from datetime import datetime, timedelta
            end = datetime.now()
            start = end - timedelta(days=730)
            df = web.DataReader(symbol, 'stooq', start, end)
            df = df.sort_index()
            open_price = df['Open'].values.astype(float)
            high = df['High'].values.astype(float)
            low = df['Low'].values.astype(float)
            close = df['Close'].values.astype(float)
            volume = df['Volume'].values.astype(float)
            dates = df.index.to_pydatetime()
            print(f"  Got {len(close)} bars for {symbol} via pandas-datareader")
            return open_price, high, low, close, volume, dates
        except Exception as e2:
            print(f"  pandas-datareader also failed: {e2}")
            raise RuntimeError(f"Could not fetch data for {symbol}")


# ==========================================================================
# Helper functions (from pre-trainer)
# ==========================================================================
def exponential_moving_avg(x, period):
    """Compute EMA matching Pine Script ta.ema()."""
    alpha = 2.0 / (period + 1.0)
    ema = np.zeros_like(x, dtype=float)
    ema[0] = x[0]
    for i in range(1, len(x)):
        ema[i] = alpha * x[i] + (1.0 - alpha) * ema[i - 1]
    return ema


def rolling_min(x, period):
    result = np.zeros_like(x, dtype=float)
    for i in range(len(x)):
        start = max(0, i - period + 1)
        result[i] = np.min(x[start:i + 1])
    return result


def rolling_max(x, period):
    result = np.zeros_like(x, dtype=float)
    for i in range(len(x)):
        start = max(0, i - period + 1)
        result[i] = np.max(x[start:i + 1])
    return result


def rolling_sum(x, period):
    result = np.zeros_like(x, dtype=float)
    for i in range(len(x)):
        start = max(0, i - period + 1)
        result[i] = np.sum(x[start:i + 1])
    return result


def true_range(high, low, close):
    tr = np.zeros(len(high), dtype=float)
    tr[0] = high[0] - low[0]
    for i in range(1, len(high)):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i - 1])
        lc = abs(low[i] - close[i - 1])
        tr[i] = max(hl, hc, lc)
    return tr


def normalize_to_pm1(x, lookback=100):
    result = np.zeros_like(x, dtype=float)
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
# Indicator computations (from pre-trainer)
# ==========================================================================
def compute_rsi(close, period):
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0).astype(float)
    loss = np.where(delta < 0, -delta, 0).astype(float)
    avg_gain = exponential_moving_avg(gain, period)
    avg_loss = exponential_moving_avg(loss, period)
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    return (rsi - 50.0) / 50.0


def compute_stochastic(high, low, close, period):
    lowest_low = rolling_min(low, period)
    highest_high = rolling_max(high, period)
    stoch = 100.0 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    return (stoch - 50.0) / 50.0


def compute_macd(close, fast, slow, signal):
    ema_fast = exponential_moving_avg(close, fast)
    ema_slow = exponential_moving_avg(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = exponential_moving_avg(macd_line, signal)
    histogram = macd_line - signal_line
    return normalize_to_pm1(histogram, lookback=100)


def compute_mfi(high, low, close, volume, period):
    typical_price = (high + low + close) / 3.0
    raw_money_flow = typical_price * volume
    delta = np.diff(typical_price, prepend=typical_price[0])
    positive_flow = np.where(delta > 0, raw_money_flow, 0).astype(float)
    negative_flow = np.where(delta <= 0, raw_money_flow, 0).astype(float)
    positive_mf_sum = rolling_sum(positive_flow, period)
    negative_mf_sum = rolling_sum(negative_flow, period)
    mfi = 100.0 - 100.0 / (1.0 + positive_mf_sum / (negative_mf_sum + 1e-10))
    return (mfi - 50.0) / 50.0


def compute_adx(high, low, close, period):
    up_move = np.diff(high, prepend=high[0])
    down_move = -np.diff(low, prepend=low[0])
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0).astype(float)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0).astype(float)
    tr = true_range(high, low, close)
    plus_di = 100.0 * exponential_moving_avg(plus_dm, period) / (exponential_moving_avg(tr, period) + 1e-10)
    minus_di = 100.0 * exponential_moving_avg(minus_dm, period) / (exponential_moving_avg(tr, period) + 1e-10)
    net_direction = plus_di - minus_di
    return normalize_to_pm1(net_direction, lookback=100)


def compute_all_indicators(open_price, high, low, close, volume):
    """Compute all 5 indicators."""
    return {
        'A': compute_rsi(close, RSI_PERIOD),
        'B': compute_stochastic(high, low, close, STOCH_PERIOD),
        'C': compute_macd(close, MACD_FAST, MACD_SLOW, MACD_SIGNAL),
        'D': compute_mfi(high, low, close, volume, MFI_PERIOD),
        'E': compute_adx(high, low, close, ADX_PERIOD),
    }


# ==========================================================================
# MVSU decontamination
# ==========================================================================
def compute_decontaminated_signal(signal_a, signal_b, w_cross):
    """signal_out = A + w_cross * B  (w_cross negative => subtract B)."""
    return signal_a + w_cross * signal_b


# ==========================================================================
# Prediction quality metrics
# ==========================================================================
def directional_accuracy(signal, next_returns, mask=None):
    """Fraction where sign(signal) == sign(next_return). Excludes zeros."""
    if mask is not None:
        s = signal[mask]
        r = next_returns[mask]
    else:
        s = signal
        r = next_returns

    nonzero = (s != 0) & (r != 0)
    if np.sum(nonzero) == 0:
        return 0.5
    return np.mean(np.sign(s[nonzero]) == np.sign(r[nonzero]))


def signal_correlation(signal, next_returns, mask=None):
    """Pearson correlation between signal and next_return."""
    if mask is not None:
        s = signal[mask]
        r = next_returns[mask]
    else:
        s = signal
        r = next_returns

    if len(s) < 2 or np.std(s) < 1e-10 or np.std(r) < 1e-10:
        return 0.0
    return np.corrcoef(s, r)[0, 1]


def sharpe_like_ratio(signal, next_returns, mask=None):
    """mean(signal * next_return) / std(signal * next_return)."""
    if mask is not None:
        s = signal[mask]
        r = next_returns[mask]
    else:
        s = signal
        r = next_returns

    product = s * r
    if np.std(product) < 1e-10:
        return 0.0
    return np.mean(product) / np.std(product)


# ==========================================================================
# Walk-forward w_cross optimization
# ==========================================================================
def optimize_w_cross(signal_a, signal_b, next_returns, mask):
    """Sweep w_cross on training data and return optimal value."""
    best_w = 0.0
    best_acc = 0.0

    for w_cross in W_CROSS_SWEEP:
        decon = compute_decontaminated_signal(signal_a, signal_b, w_cross)
        acc = directional_accuracy(decon, next_returns, mask)
        if acc > best_acc:
            best_acc = acc
            best_w = w_cross

    return best_w, best_acc


# ==========================================================================
# Trading strategy simulation
# ==========================================================================
def simulate_strategy(signal, close, dates, buy_thresh=BUY_THRESHOLD, sell_thresh=SELL_THRESHOLD):
    """
    Simple threshold strategy:
      - Buy when signal > buy_thresh
      - Sell when signal < sell_thresh
      - Hold otherwise

    Returns dict with metrics and trade arrays.
    """
    n = len(close)
    position = 0  # 0 = flat, 1 = long
    equity = np.ones(n)
    trades = np.zeros(n)  # 1 = buy, -1 = sell

    for i in range(1, n):
        # Determine position based on previous bar's signal
        if i - 1 >= 0:
            if signal[i - 1] > buy_thresh and position == 0:
                position = 1
                trades[i] = 1
            elif signal[i - 1] < sell_thresh and position == 1:
                position = 0
                trades[i] = -1

        # Update equity
        if position == 1:
            daily_return = (close[i] - close[i - 1]) / close[i - 1]
            equity[i] = equity[i - 1] * (1.0 + daily_return)
        else:
            equity[i] = equity[i - 1]

    total_return = (equity[-1] / equity[0] - 1.0) * 100.0

    # Sharpe ratio (annualized)
    daily_returns = np.diff(equity) / equity[:-1]
    if np.std(daily_returns) > 1e-10:
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
    else:
        sharpe = 0.0

    # Max drawdown
    running_max = np.maximum.accumulate(equity)
    drawdowns = (equity - running_max) / running_max
    max_drawdown = np.min(drawdowns) * 100.0

    n_trades = int(np.sum(np.abs(trades)))

    return {
        'total_return': total_return,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'n_trades': n_trades,
        'equity': equity,
        'trades': trades,
    }


def buy_and_hold(close):
    """Buy and hold strategy metrics."""
    equity = close / close[0]
    total_return = (equity[-1] - 1.0) * 100.0
    daily_returns = np.diff(equity) / equity[:-1]
    if np.std(daily_returns) > 1e-10:
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
    else:
        sharpe = 0.0
    running_max = np.maximum.accumulate(equity)
    drawdowns = (equity - running_max) / running_max
    max_drawdown = np.min(drawdowns) * 100.0
    return {
        'total_return': total_return,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'n_trades': 1,
        'equity': equity,
        'trades': np.zeros(len(close)),
    }


# ==========================================================================
# Main analysis for a single symbol
# ==========================================================================
def analyze_symbol(symbol, open_price, high, low, close, volume, dates):
    """Full MVSU analysis for one symbol. Returns results dict."""

    n = len(close)
    print(f"\n{'=' * 70}")
    print(f"  ANALYZING {symbol}  ({n} bars)")
    print(f"{'=' * 70}")

    # Compute indicators
    print("  Computing indicators...")
    indicators = compute_all_indicators(open_price, high, low, close, volume)

    # Next-bar returns (for prediction quality)
    next_returns = np.zeros(n)
    next_returns[:-1] = np.diff(close) / close[:-1]

    # Walk-forward split
    train_end = int(n * TRAIN_FRACTION)
    train_mask = np.zeros(n, dtype=bool)
    train_mask[WARMUP:train_end] = True
    test_mask = np.zeros(n, dtype=bool)
    test_mask[train_end:n - 1] = True  # exclude last bar (no next return)

    print(f"  Train: bars {WARMUP}-{train_end} ({np.sum(train_mask)} bars)")
    print(f"  Test:  bars {train_end}-{n - 2} ({np.sum(test_mask)} bars)")

    # --- Analyze all 10 pairs ---
    results = {}
    for pair in PAIRS:
        label_a, label_b = pair
        pair_name = f"{PAIR_NAMES[label_a]}-{PAIR_NAMES[label_b]}"
        ind_a = indicators[label_a]
        ind_b = indicators[label_b]

        # 1. Optimize w_cross on training data
        w_cross_opt, train_acc_mvsu = optimize_w_cross(ind_a, ind_b, next_returns, train_mask)

        # 2. Compute signals
        raw_signal = ind_a
        avg_signal = (ind_a + ind_b) / 2.0
        mvsu_signal = compute_decontaminated_signal(ind_a, ind_b, w_cross_opt)

        # 3. In-sample metrics
        raw_acc_train = directional_accuracy(raw_signal, next_returns, train_mask)
        avg_acc_train = directional_accuracy(avg_signal, next_returns, train_mask)
        # train_acc_mvsu already computed

        raw_corr_train = signal_correlation(raw_signal, next_returns, train_mask)
        avg_corr_train = signal_correlation(avg_signal, next_returns, train_mask)
        mvsu_corr_train = signal_correlation(mvsu_signal, next_returns, train_mask)

        raw_sharpe_train = sharpe_like_ratio(raw_signal, next_returns, train_mask)
        avg_sharpe_train = sharpe_like_ratio(avg_signal, next_returns, train_mask)
        mvsu_sharpe_train = sharpe_like_ratio(mvsu_signal, next_returns, train_mask)

        # 4. Out-of-sample metrics (using w_cross trained on train set)
        raw_acc_test = directional_accuracy(raw_signal, next_returns, test_mask)
        avg_acc_test = directional_accuracy(avg_signal, next_returns, test_mask)
        mvsu_acc_test = directional_accuracy(mvsu_signal, next_returns, test_mask)

        raw_corr_test = signal_correlation(raw_signal, next_returns, test_mask)
        avg_corr_test = signal_correlation(avg_signal, next_returns, test_mask)
        mvsu_corr_test = signal_correlation(mvsu_signal, next_returns, test_mask)

        raw_sharpe_test = sharpe_like_ratio(raw_signal, next_returns, test_mask)
        avg_sharpe_test = sharpe_like_ratio(avg_signal, next_returns, test_mask)
        mvsu_sharpe_test = sharpe_like_ratio(mvsu_signal, next_returns, test_mask)

        results[pair] = {
            'pair_name': pair_name,
            'w_cross': w_cross_opt,
            # In-sample
            'raw_acc_train': raw_acc_train,
            'avg_acc_train': avg_acc_train,
            'mvsu_acc_train': train_acc_mvsu,
            'raw_corr_train': raw_corr_train,
            'avg_corr_train': avg_corr_train,
            'mvsu_corr_train': mvsu_corr_train,
            'raw_sharpe_train': raw_sharpe_train,
            'avg_sharpe_train': avg_sharpe_train,
            'mvsu_sharpe_train': mvsu_sharpe_train,
            # Out-of-sample
            'raw_acc_test': raw_acc_test,
            'avg_acc_test': avg_acc_test,
            'mvsu_acc_test': mvsu_acc_test,
            'raw_corr_test': raw_corr_test,
            'avg_corr_test': avg_corr_test,
            'mvsu_corr_test': mvsu_corr_test,
            'raw_sharpe_test': raw_sharpe_test,
            'avg_sharpe_test': avg_sharpe_test,
            'mvsu_sharpe_test': mvsu_sharpe_test,
            # Signals for plotting
            'raw_signal': raw_signal,
            'avg_signal': avg_signal,
            'mvsu_signal': mvsu_signal,
        }

    # --- Consensus analysis ---
    # For each bar, count how many MVSU pairs agree on direction
    consensus_signals = np.zeros(n)
    for pair in PAIRS:
        r = results[pair]
        consensus_signals += np.sign(r['mvsu_signal'])
    consensus_frac = np.abs(consensus_signals) / len(PAIRS)

    # When >70% agree, what's the accuracy?
    strong_consensus_mask = test_mask & (consensus_frac > 0.7)
    weak_consensus_mask = test_mask & (consensus_frac <= 0.7)

    consensus_direction = np.sign(consensus_signals)
    strong_acc = directional_accuracy(consensus_direction, next_returns, strong_consensus_mask)
    weak_acc = directional_accuracy(consensus_direction, next_returns, weak_consensus_mask)
    overall_consensus_acc = directional_accuracy(consensus_direction, next_returns, test_mask)

    consensus_result = {
        'strong_consensus_bars': int(np.sum(strong_consensus_mask)),
        'weak_consensus_bars': int(np.sum(weak_consensus_mask)),
        'strong_acc': strong_acc,
        'weak_acc': weak_acc,
        'overall_acc': overall_consensus_acc,
        'consensus_signal': consensus_direction,
    }

    return results, indicators, next_returns, train_mask, test_mask, consensus_result


# ==========================================================================
# Printing functions
# ==========================================================================
def print_results_table(symbol, results, section="In-Sample"):
    """Print formatted results table."""
    if section == "In-Sample":
        acc_raw_key = 'raw_acc_train'
        acc_avg_key = 'avg_acc_train'
        acc_mvsu_key = 'mvsu_acc_train'
    else:
        acc_raw_key = 'raw_acc_test'
        acc_avg_key = 'avg_acc_test'
        acc_mvsu_key = 'mvsu_acc_test'

    sorted_pairs = sorted(PAIRS, key=lambda p: results[p]['w_cross'])

    print(f"\n=== {symbol} Results ({section}) ===")
    print(f"{'Pair':<12} | {'w_cross':>8} | {'Raw Acc':>8} | {'Avg Acc':>8} | {'MVSU Acc':>9} | {'MVSU vs Raw':>11}")
    print("-" * 70)

    for pair in sorted_pairs:
        r = results[pair]
        raw = r[acc_raw_key] * 100
        avg = r[acc_avg_key] * 100
        mvsu = r[acc_mvsu_key] * 100
        diff = mvsu - raw
        sign = "+" if diff >= 0 else ""
        print(f"{r['pair_name']:<12} | {r['w_cross']:>8.4f} | {raw:>7.1f}% | {avg:>7.1f}% | {mvsu:>8.1f}% | {sign}{diff:>9.1f}%")

    # Summary stats
    avg_raw = np.mean([results[p][acc_raw_key] for p in PAIRS]) * 100
    avg_avg = np.mean([results[p][acc_avg_key] for p in PAIRS]) * 100
    avg_mvsu = np.mean([results[p][acc_mvsu_key] for p in PAIRS]) * 100
    print("-" * 70)
    diff = avg_mvsu - avg_raw
    sign = "+" if diff >= 0 else ""
    print(f"{'AVERAGE':<12} | {'':>8} | {avg_raw:>7.1f}% | {avg_avg:>7.1f}% | {avg_mvsu:>8.1f}% | {sign}{diff:>9.1f}%")


def print_correlation_table(symbol, results, section="In-Sample"):
    """Print correlation results."""
    if section == "In-Sample":
        corr_raw_key = 'raw_corr_train'
        corr_avg_key = 'avg_corr_train'
        corr_mvsu_key = 'mvsu_corr_train'
    else:
        corr_raw_key = 'raw_corr_test'
        corr_avg_key = 'avg_corr_test'
        corr_mvsu_key = 'mvsu_corr_test'

    sorted_pairs = sorted(PAIRS, key=lambda p: results[p]['w_cross'])

    print(f"\n=== {symbol} Signal-Return Correlations ({section}) ===")
    print(f"{'Pair':<12} | {'Raw Corr':>9} | {'Avg Corr':>9} | {'MVSU Corr':>10}")
    print("-" * 50)

    for pair in sorted_pairs:
        r = results[pair]
        print(f"{r['pair_name']:<12} | {r[corr_raw_key]:>9.4f} | {r[corr_avg_key]:>9.4f} | {r[corr_mvsu_key]:>10.4f}")


def print_walk_forward(symbol, results):
    """Print walk-forward comparison."""
    sorted_pairs = sorted(PAIRS, key=lambda p: results[p]['w_cross'])

    print(f"\n=== {symbol} Walk-Forward (Out-of-Sample) ===")
    print(f"{'Pair':<12} | {'w_cross':>8} | {'IS Acc':>7} | {'OOS Acc':>8} | {'Overfit?':>9}")
    print("-" * 60)

    overfit_count = 0
    for pair in sorted_pairs:
        r = results[pair]
        is_acc = r['mvsu_acc_train'] * 100
        oos_acc = r['mvsu_acc_test'] * 100
        diff = oos_acc - is_acc
        overfit = "YES" if diff < -1.0 else "no"
        if diff < -1.0:
            overfit_count += 1
        print(f"{r['pair_name']:<12} | {r['w_cross']:>8.4f} | {is_acc:>6.1f}% | {oos_acc:>7.1f}% | {overfit:>9}")

    print("-" * 60)
    print(f"  Pairs showing overfitting (OOS > 1% worse than IS): {overfit_count}/{len(PAIRS)}")


def print_trading_results(symbol, strategies):
    """Print trading simulation results."""
    print(f"\n=== {symbol} Simple Strategy Backtest ===")
    print(f"{'Strategy':<20} | {'Return':>8} | {'Sharpe':>7} | {'MaxDD':>8} | {'Trades':>7}")
    print("-" * 60)

    for name, strat in strategies.items():
        print(f"{name:<20} | {strat['total_return']:>7.1f}% | {strat['sharpe']:>7.2f} | {strat['max_drawdown']:>7.1f}% | {strat['n_trades']:>7d}")


def print_consensus(symbol, consensus):
    """Print consensus analysis."""
    print(f"\n=== {symbol} Consensus Analysis (Out-of-Sample) ===")
    print(f"  Strong consensus (>70% agree): {consensus['strong_consensus_bars']} bars, accuracy = {consensus['strong_acc']*100:.1f}%")
    print(f"  Weak consensus (<=70% agree):  {consensus['weak_consensus_bars']} bars, accuracy = {consensus['weak_acc']*100:.1f}%")
    print(f"  Overall consensus accuracy:    {consensus['overall_acc']*100:.1f}%")
    edge = consensus['strong_acc'] - consensus['weak_acc']
    print(f"  Consensus edge (strong - weak): {edge*100:+.1f}%")


# ==========================================================================
# Plotting
# ==========================================================================
def create_plots(all_data):
    """Create 2x3 plot layout."""
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle("MVSU Trading Test: Real Market Data Validation", fontsize=14, fontweight='bold')

    symbols = list(all_data.keys())

    for sym_idx, symbol in enumerate(symbols[:2]):
        data = all_data[symbol]
        close = data['close']
        dates = data['dates']
        results = data['results']
        best_pair = data['best_pair']
        strategies = data['strategies']
        test_mask = data['test_mask']

        r_best = results[best_pair]
        pair_name = r_best['pair_name']

        # --- Plot 1/4: Price with buy/sell signals ---
        ax = axes[sym_idx, 0]
        ax.plot(dates, close, color='black', linewidth=0.8, alpha=0.7, label=f'{symbol} Price')

        # Show MVSU strategy trades
        mvsu_strat = strategies.get('MVSU Best', None)
        if mvsu_strat is not None:
            buy_idx = np.where(mvsu_strat['trades'] == 1)[0]
            sell_idx = np.where(mvsu_strat['trades'] == -1)[0]
            if len(buy_idx) > 0:
                ax.scatter([dates[i] for i in buy_idx], close[buy_idx],
                          marker='^', color='green', s=40, zorder=5, label='Buy')
            if len(sell_idx) > 0:
                ax.scatter([dates[i] for i in sell_idx], close[sell_idx],
                          marker='v', color='red', s=40, zorder=5, label='Sell')

        # Mark train/test boundary
        train_end_idx = int(len(close) * TRAIN_FRACTION)
        ax.axvline(x=dates[train_end_idx], color='blue', linestyle='--', alpha=0.5, label='Train|Test split')

        ax.set_title(f'{symbol} Price + MVSU Signals ({pair_name})')
        ax.set_ylabel('Price')
        ax.legend(fontsize=7, loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.tick_params(axis='x', rotation=30)

        # --- Plot 2/5: w_cross values for all pairs ---
        ax = axes[sym_idx, 1]
        sorted_pairs = sorted(PAIRS, key=lambda p: results[p]['w_cross'])
        pair_labels = [results[p]['pair_name'] for p in sorted_pairs]
        w_values = [results[p]['w_cross'] for p in sorted_pairs]

        colors = ['darkred' if w < -0.3 else 'steelblue' for w in w_values]
        bars = ax.barh(pair_labels, w_values, color=colors, edgecolor='black', linewidth=0.5)
        ax.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel('Optimal w_cross')
        ax.set_title(f'{symbol}: w_cross per Pair (train set)')
        ax.grid(True, alpha=0.3, axis='x')

        # --- Plot 3/6: Prediction accuracy comparison ---
        ax = axes[sym_idx, 2]

        if sym_idx == 0:
            # Bar chart: raw vs avg vs MVSU accuracy (out-of-sample)
            x = np.arange(len(PAIRS))
            width = 0.25
            sorted_pairs_for_chart = sorted(PAIRS, key=lambda p: results[p]['w_cross'])
            pair_labels_chart = [results[p]['pair_name'] for p in sorted_pairs_for_chart]

            raw_accs = [results[p]['raw_acc_test'] * 100 for p in sorted_pairs_for_chart]
            avg_accs = [results[p]['avg_acc_test'] * 100 for p in sorted_pairs_for_chart]
            mvsu_accs = [results[p]['mvsu_acc_test'] * 100 for p in sorted_pairs_for_chart]

            ax.bar(x - width, raw_accs, width, label='Raw', color='orange', alpha=0.8)
            ax.bar(x, avg_accs, width, label='Average', color='gray', alpha=0.8)
            ax.bar(x + width, mvsu_accs, width, label='MVSU', color='steelblue', alpha=0.8)

            ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Random (50%)')
            ax.set_xticks(x)
            ax.set_xticklabels(pair_labels_chart, rotation=45, ha='right', fontsize=7)
            ax.set_ylabel('Directional Accuracy (%)')
            ax.set_title(f'{symbol}: OOS Accuracy (Raw vs Avg vs MVSU)')
            ax.legend(fontsize=7)
            ax.grid(True, alpha=0.3, axis='y')
        else:
            # Walk-forward: in-sample vs out-of-sample accuracy
            sorted_pairs_wf = sorted(PAIRS, key=lambda p: results[p]['w_cross'])
            pair_labels_wf = [results[p]['pair_name'] for p in sorted_pairs_wf]

            is_accs = [results[p]['mvsu_acc_train'] * 100 for p in sorted_pairs_wf]
            oos_accs = [results[p]['mvsu_acc_test'] * 100 for p in sorted_pairs_wf]

            x = np.arange(len(PAIRS))
            width = 0.35
            ax.bar(x - width/2, is_accs, width, label='In-Sample', color='lightblue', edgecolor='blue')
            ax.bar(x + width/2, oos_accs, width, label='Out-of-Sample', color='salmon', edgecolor='red')

            ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Random (50%)')
            ax.set_xticks(x)
            ax.set_xticklabels(pair_labels_wf, rotation=45, ha='right', fontsize=7)
            ax.set_ylabel('MVSU Directional Accuracy (%)')
            ax.set_title(f'{symbol}: Walk-Forward (IS vs OOS)')
            ax.legend(fontsize=7)
            ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "mvsu_trading_test_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==========================================================================
# Honesty summary
# ==========================================================================
def print_honesty_summary(all_data):
    """Print honest assessment of MVSU effectiveness."""
    print("\n" + "=" * 70)
    print("  HONEST ASSESSMENT")
    print("=" * 70)

    for symbol, data in all_data.items():
        results = data['results']
        consensus = data['consensus']

        # 1. Does w_cross stay near zero?
        w_values = [results[p]['w_cross'] for p in PAIRS]
        mean_w = np.mean(w_values)
        min_w = np.min(w_values)
        n_significant = sum(1 for w in w_values if w < -0.2)

        print(f"\n--- {symbol} ---")
        print(f"  w_cross: mean={mean_w:.3f}, min={min_w:.3f}, pairs with w < -0.2: {n_significant}/{len(PAIRS)}")
        if abs(mean_w) < 0.05:
            print(f"  WARNING: w_cross near zero on average - little contamination detected")

        # 2. Does MVSU beat raw?
        raw_accs = [results[p]['raw_acc_test'] for p in PAIRS]
        mvsu_accs = [results[p]['mvsu_acc_test'] for p in PAIRS]
        avg_accs = [results[p]['avg_acc_test'] for p in PAIRS]

        n_mvsu_beats_raw = sum(1 for r, m in zip(raw_accs, mvsu_accs) if m > r)
        n_mvsu_beats_avg = sum(1 for a, m in zip(avg_accs, mvsu_accs) if m > a)

        mean_raw = np.mean(raw_accs) * 100
        mean_avg = np.mean(avg_accs) * 100
        mean_mvsu = np.mean(mvsu_accs) * 100

        print(f"  OOS accuracy: Raw={mean_raw:.1f}%, Avg={mean_avg:.1f}%, MVSU={mean_mvsu:.1f}%")
        print(f"  MVSU beats Raw in {n_mvsu_beats_raw}/{len(PAIRS)} pairs")
        print(f"  MVSU beats Avg in {n_mvsu_beats_avg}/{len(PAIRS)} pairs")

        if mean_mvsu <= mean_raw:
            print(f"  CONCLUSION: MVSU does NOT beat raw indicators out-of-sample for {symbol}")
        elif mean_mvsu - mean_raw < 1.0:
            print(f"  CONCLUSION: MVSU shows marginal improvement (+{mean_mvsu - mean_raw:.1f}%) for {symbol} - likely noise")
        else:
            print(f"  CONCLUSION: MVSU shows meaningful improvement (+{mean_mvsu - mean_raw:.1f}%) for {symbol}")

        # 3. Overfitting check
        is_accs = [results[p]['mvsu_acc_train'] for p in PAIRS]
        oos_accs = [results[p]['mvsu_acc_test'] for p in PAIRS]
        overfit_gap = np.mean(is_accs) * 100 - np.mean(oos_accs) * 100
        print(f"  Overfitting gap (IS - OOS): {overfit_gap:+.1f}%")
        if overfit_gap > 2.0:
            print(f"  WARNING: Significant overfitting detected ({overfit_gap:.1f}% gap)")

        # 4. Consensus
        if consensus['strong_consensus_bars'] > 0:
            print(f"  Consensus: strong={consensus['strong_acc']*100:.1f}%, weak={consensus['weak_acc']*100:.1f}%")
            edge = consensus['strong_acc'] - consensus['weak_acc']
            if edge > 0.02:
                print(f"  Consensus filtering adds +{edge*100:.1f}% accuracy edge")
            else:
                print(f"  Consensus filtering does NOT meaningfully improve accuracy")

        # 5. Trading results
        strats = data['strategies']
        mvsu_ret = strats.get('MVSU Best', {}).get('total_return', 0)
        bh_ret = strats.get('Buy & Hold', {}).get('total_return', 0)
        if mvsu_ret < bh_ret:
            print(f"  TRADING: MVSU strategy ({mvsu_ret:.1f}%) UNDERPERFORMS buy-and-hold ({bh_ret:.1f}%)")
        elif mvsu_ret < 0:
            print(f"  TRADING: MVSU strategy LOSES money ({mvsu_ret:.1f}%)")
        else:
            print(f"  TRADING: MVSU strategy ({mvsu_ret:.1f}%) vs buy-and-hold ({bh_ret:.1f}%)")


# ==========================================================================
# Main
# ==========================================================================
def main():
    print("=" * 70)
    print("  MVSU TRADING TEST: Real Market Data Validation")
    print("=" * 70)
    print(f"  Symbols: {SYMBOLS}")
    print(f"  Walk-forward: {TRAIN_FRACTION*100:.0f}% train / {(1-TRAIN_FRACTION)*100:.0f}% test")
    print(f"  w_cross sweep: {W_CROSS_SWEEP[0]:.2f} to {W_CROSS_SWEEP[-1]:.2f} ({len(W_CROSS_SWEEP)} points)")
    print(f"  Trading thresholds: buy > {BUY_THRESHOLD}, sell < {SELL_THRESHOLD}")

    all_data = {}

    for symbol in SYMBOLS:
        print(f"\n--- Fetching data for {symbol} ---")
        try:
            open_price, high, low, close, volume, dates = fetch_data(symbol)
        except RuntimeError as e:
            print(f"  FAILED: {e}")
            continue

        if len(close) < 200:
            print(f"  SKIPPED: Only {len(close)} bars (need at least 200)")
            continue

        # Run full analysis
        results, indicators, next_returns, train_mask, test_mask, consensus = \
            analyze_symbol(symbol, open_price, high, low, close, volume, dates)

        # Find best MVSU pair (by OOS accuracy)
        best_pair = max(PAIRS, key=lambda p: results[p]['mvsu_acc_test'])
        best_name = results[best_pair]['pair_name']
        print(f"\n  Best MVSU pair (OOS): {best_name} "
              f"(acc={results[best_pair]['mvsu_acc_test']*100:.1f}%, "
              f"w_cross={results[best_pair]['w_cross']:.4f})")

        # Print tables
        print_results_table(symbol, results, "In-Sample")
        print_results_table(symbol, results, "Out-of-Sample")
        print_correlation_table(symbol, results, "Out-of-Sample")
        print_walk_forward(symbol, results)
        print_consensus(symbol, consensus)

        # --- Trading simulation ---
        # Use test period only for fair comparison
        test_start = int(len(close) * TRAIN_FRACTION)
        test_close = close[test_start:]
        test_dates = dates[test_start:]

        # Strategies
        strategies = {}

        # 1. Buy & Hold
        strategies['Buy & Hold'] = buy_and_hold(test_close)

        # 2. Raw RSI strategy
        raw_rsi = indicators['A'][test_start:]
        strategies['Raw RSI'] = simulate_strategy(raw_rsi, test_close, test_dates)

        # 3. Simple average of best pair
        r_best = results[best_pair]
        avg_signal_test = r_best['avg_signal'][test_start:]
        strategies['Avg (best pair)'] = simulate_strategy(avg_signal_test, test_close, test_dates)

        # 4. MVSU best pair
        mvsu_signal_test = r_best['mvsu_signal'][test_start:]
        strategies['MVSU Best'] = simulate_strategy(mvsu_signal_test, test_close, test_dates)

        # 5. Consensus strategy (buy when >70% agree bullish)
        consensus_signal_test = consensus['consensus_signal'][test_start:]
        # Normalize to [-1, 1] range for thresholds
        consensus_norm = consensus_signal_test / len(PAIRS)
        strategies['Consensus'] = simulate_strategy(consensus_norm, test_close, test_dates,
                                                     buy_thresh=0.3, sell_thresh=-0.3)

        print_trading_results(symbol, strategies)

        all_data[symbol] = {
            'close': close,
            'dates': dates,
            'results': results,
            'best_pair': best_pair,
            'strategies': strategies,
            'indicators': indicators,
            'consensus': consensus,
            'test_mask': test_mask,
        }

    if not all_data:
        print("\n  ERROR: No data could be fetched. Exiting.")
        return

    # Honest assessment
    print_honesty_summary(all_data)

    # Generate plots
    print("\n\nGenerating plots...")
    create_plots(all_data)

    print("\n" + "=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
