"""
MVSU — Minimum Viable Stable Unit (Reusable Module)
Dual-channel inhibitory architecture for self-referential decontamination.

When predictions contaminate future observations, a single channel can't
distinguish signal from echo. Two channels with different inits (free diversity)
develop different error patterns. Inhibitory cross-connections subtract
correlated contamination, preserving the true signal.

Usage:
    from mvsu import MVSUPredictor, LinearPredictor
    base = LinearPredictor(d_in=5, d_out=1)
    mvsu = MVSUPredictor(base)
    for t in range(T):
        pred = mvsu.predict(observation)
        mvsu.update(observation, true_signal, lr=0.01)
"""

import numpy as np


class LinearPredictor:
    """Linear predictor: y = W @ x + b."""

    def __init__(self, d_in, d_out, seed=None):
        rng = np.random.RandomState(seed)
        self.W = rng.randn(d_out, d_in) * 0.1
        self.b = np.zeros(d_out)
        self.d_in = d_in
        self.d_out = d_out
        self._last_x = None

    def predict(self, x):
        """Forward pass. x: (d_in,) -> (d_out,)."""
        x = np.asarray(x, dtype=float).ravel()
        self._last_x = x
        return self.W @ x + self.b

    def update(self, grad_output, lr=0.01, grad_clip=5.0):
        """Update weights given dL/d(prediction). grad_output: (d_out,)."""
        grad_output = np.asarray(grad_output, dtype=float).ravel()
        x = self._last_x
        grad_W = np.outer(grad_output, x)
        grad_b = grad_output
        self.W -= lr * np.clip(grad_W, -grad_clip, grad_clip)
        self.b -= lr * np.clip(grad_b, -grad_clip, grad_clip)

    def copy(self, seed=None):
        """Create a copy with different random initialization."""
        new = LinearPredictor(self.d_in, self.d_out, seed=seed)
        return new


class MLPPredictor:
    """MLP predictor: hidden = tanh(W1 @ x + b1); y = W2 @ hidden + b2."""

    def __init__(self, d_in, d_out, d_hidden=16, seed=None):
        rng = np.random.RandomState(seed)
        scale1 = np.sqrt(2.0 / d_in)
        scale2 = np.sqrt(2.0 / d_hidden)
        self.W1 = rng.randn(d_hidden, d_in) * scale1
        self.b1 = np.zeros(d_hidden)
        self.W2 = rng.randn(d_out, d_hidden) * scale2
        self.b2 = np.zeros(d_out)
        self.d_in = d_in
        self.d_out = d_out
        self.d_hidden = d_hidden
        self._last_x = None
        self._last_hidden = None
        self._last_pre_act = None

    def predict(self, x):
        """Forward pass."""
        x = np.asarray(x, dtype=float).ravel()
        self._last_x = x
        pre_act = self.W1 @ x + self.b1
        self._last_pre_act = pre_act
        hidden = np.tanh(pre_act)
        self._last_hidden = hidden
        return self.W2 @ hidden + self.b2

    def update(self, grad_output, lr=0.01, grad_clip=5.0):
        """Backprop and update."""
        grad_output = np.asarray(grad_output, dtype=float).ravel()
        hidden, x = self._last_hidden, self._last_x
        grad_W2 = np.outer(grad_output, hidden)
        grad_b2 = grad_output
        grad_hidden = self.W2.T @ grad_output
        grad_pre = grad_hidden * (1.0 - hidden ** 2)
        grad_W1 = np.outer(grad_pre, x)
        grad_b1 = grad_pre
        self.W2 -= lr * np.clip(grad_W2, -grad_clip, grad_clip)
        self.b2 -= lr * np.clip(grad_b2, -grad_clip, grad_clip)
        self.W1 -= lr * np.clip(grad_W1, -grad_clip, grad_clip)
        self.b1 -= lr * np.clip(grad_b1, -grad_clip, grad_clip)

    def copy(self, seed=None):
        """Create a copy with different random initialization."""
        return MLPPredictor(self.d_in, self.d_out, self.d_hidden, seed=seed)


class MVSUPredictor:
    """Dual-channel MVSU: two predictors with inhibitory cross-connections.

    decontaminated_A = raw_A - w_cross * raw_B  (and vice versa)
    output = mean(decontaminated_A, decontaminated_B)

    Channels develop different error patterns via different random init
    (free diversity). Cross-subtraction removes common contamination.
    """

    def __init__(self, predictor_A, predictor_B=None, w_cross_init=-0.1):
        self.channel_A = predictor_A
        if predictor_B is None:
            # Free diversity: same architecture, different random init
            self.channel_B = predictor_A.copy(seed=predictor_A.d_in * 7 + 31)
        else:
            self.channel_B = predictor_B
        self.w_cross = w_cross_init
        self._raw_A = None
        self._raw_B = None
        self._pred_A = None
        self._pred_B = None

    def predict(self, observation):
        """Predict with cross-inhibitory decontamination."""
        obs = np.asarray(observation, dtype=float).ravel()
        raw_A = self.channel_A.predict(obs)
        raw_B = self.channel_B.predict(obs)
        self._raw_A = raw_A.copy()
        self._raw_B = raw_B.copy()

        # Cross-inhibitory decontamination
        pred_A = raw_A - self.w_cross * raw_B
        pred_B = raw_B - self.w_cross * raw_A
        self._pred_A = pred_A
        self._pred_B = pred_B

        prediction = 0.5 * (pred_A + pred_B)
        return prediction

    def update(self, observation, true_signal, lr=0.01, grad_clip=5.0):
        """Update both channels and w_cross. Returns MSE loss."""
        true_signal = np.asarray(true_signal, dtype=float).ravel()
        pred_A = self._pred_A
        pred_B = self._pred_B
        prediction = 0.5 * (pred_A + pred_B)
        error = prediction - true_signal
        loss = float(np.mean(error ** 2))

        grad_pred = 2.0 * error
        grad_pred_A = 0.5 * grad_pred
        grad_pred_B = 0.5 * grad_pred
        # Through cross-inhibition: pred_A = raw_A - w_cross * raw_B
        grad_raw_A = grad_pred_A + (-self.w_cross * grad_pred_B)
        grad_raw_B = (-self.w_cross * grad_pred_A) + grad_pred_B
        self.channel_A.update(grad_raw_A, lr=lr, grad_clip=grad_clip)
        self.channel_B.update(grad_raw_B, lr=lr, grad_clip=grad_clip)
        # w_cross gradient
        grad_w_cross = float(np.dot(grad_pred_A, -self._raw_B) +
                             np.dot(grad_pred_B, -self._raw_A))
        grad_w_cross = np.clip(grad_w_cross, -grad_clip, grad_clip)
        self.w_cross -= lr * grad_w_cross

        return loss

    @property
    def w_cross_value(self):
        """Current cross-inhibition weight."""
        return self.w_cross


class MVSUEnsemble:
    """N-channel MVSU with pairwise inhibitory connections.
    Generalizes MVSUPredictor to N >= 2 channels.
    """

    def __init__(self, predictors, w_cross_init=-0.1):
        self.channels = predictors
        self.N = len(predictors)
        assert self.N >= 2, "Need at least 2 channels"
        self.w_cross = np.full((self.N, self.N), w_cross_init)
        np.fill_diagonal(self.w_cross, 0.0)
        self._raw_preds = None

    def predict(self, observation):
        """Predict with N-channel cross-inhibitory decontamination."""
        obs = np.asarray(observation, dtype=float).ravel()
        raw_preds = []
        for ch in self.channels:
            raw_preds.append(ch.predict(obs))
        self._raw_preds = [r.copy() for r in raw_preds]

        decontaminated = []
        for i in range(self.N):
            d = raw_preds[i].copy()
            for j in range(self.N):
                if i != j:
                    d -= self.w_cross[i, j] * raw_preds[j]
            decontaminated.append(d)

        prediction = np.mean(decontaminated, axis=0)
        self._decontaminated = decontaminated
        return prediction

    def update(self, observation, true_signal, lr=0.01, grad_clip=5.0):
        """Update all channels and cross-weights. Returns MSE loss."""
        true_signal = np.asarray(true_signal, dtype=float).ravel()
        prediction = np.mean(self._decontaminated, axis=0)
        error = prediction - true_signal
        loss = float(np.mean(error ** 2))
        grad_pred = 2.0 * error

        grad_per_channel = grad_pred / self.N
        grad_raw = [np.zeros_like(self._raw_preds[0]) for _ in range(self.N)]
        for i in range(self.N):
            grad_raw[i] += grad_per_channel
            for j in range(self.N):
                if i != j:
                    grad_raw[j] -= self.w_cross[i, j] * grad_per_channel

        for i in range(self.N):
            self.channels[i].update(grad_raw[i], lr=lr, grad_clip=grad_clip)
        for i in range(self.N):
            for j in range(self.N):
                if i != j:
                    grad_w = float(np.dot(grad_per_channel, -self._raw_preds[j]))
                    grad_w = np.clip(grad_w, -grad_clip, grad_clip)
                    self.w_cross[i, j] -= lr * grad_w

        return loss
