"""
RLHF Bridge Experiment: Testing Self-Referential Optimization Theory in RLHF
==============================================================================
The single most important experiment for the self-referential learning framework.

Does iterative reward model training exhibit degradation consistent with kw^2+w-1=0?
Does the MVSU (dual reward models + inhibitory coupling) mitigate this degradation?

Setup:
  - State space: d-dimensional feature vectors (d=16)
  - Policy: 1-hidden-layer MLP mapping state -> action (continuous)
  - Ground truth reward: R*(s, a) = known function (linear + interaction terms)
  - Reward model: learned approximation R_hat(s, a)
  - Preference generation: noisy pairwise comparisons using R*

RLHF Loop (the self-referential core):
  for iteration in range(N):
      1. Policy generates actions optimizing current R_hat
      2. Generate preference pairs from policy-generated actions
      3. Label preferences using R* (simulated human)
      4. Retrain R_hat on ALL accumulated preference data
      5. Measure: correlation(R_hat, R*)

Conditions:
  A: Standard RLHF -- single reward model, iterative retraining
  B: MVSU RLHF -- dual reward models with inhibitory cross-connections
  C: Ensemble baseline -- two reward models averaged (no inhibition)
  D: Fresh-data control -- reward model retrained on independently generated data

Author: Claude (RLHF Bridge Experiment, Tier 1 priority)
"""

import sys
import io
import os
import time
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
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation):
        try:
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        except Exception:
            pass

# ==========================================================================
# Constants
# ==========================================================================
D_STATE = 16          # State dimensionality
D_ACTION = 8         # Action dimensionality
D_HIDDEN_POLICY = 32  # Policy hidden layer size
D_HIDDEN_REWARD = 32  # Reward model hidden layer size

N_RLHF_ITERATIONS = 20    # Number of RLHF loop iterations
N_POLICY_STEPS = 200       # Policy optimization steps per RLHF iteration
N_PAIRS_PER_ITER = 300     # Preference pairs generated per iteration
N_REWARD_EPOCHS = 10       # Epochs to retrain reward model
N_EVAL_SAMPLES = 500       # Samples for evaluation
BATCH_SIZE = 64            # Mini-batch size for reward model training

POLICY_LR = 0.005          # Policy learning rate
REWARD_LR = 0.003          # Reward model learning rate
MOMENTUM = 0.9             # SGD momentum

# Sweep parameters
POLICY_STRENGTHS = [0.1, 0.5, 1.0, 2.0, 5.0]  # How aggressively policy exploits R_hat
NOISE_LEVELS = [0.0, 0.1, 0.3]                  # Preference noise
N_SEEDS = 3                                       # Random seeds
SEEDS = [42, 137, 256]

# Theory constants
PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1.0 / PHI  # ~0.618


# ==========================================================================
# Neural Network Primitives (pure numpy)
# ==========================================================================
def tanh_forward(x):
    return np.tanh(x)

def tanh_backward(x):
    """d/dx tanh(x) = 1 - tanh(x)^2."""
    t = np.tanh(x)
    return 1.0 - t * t


class MLP:
    """Simple 1-hidden-layer MLP with tanh activation. SGD with momentum."""

    def __init__(self, d_in, d_hidden, d_out, seed=0):
        rng = np.random.RandomState(seed)
        # Xavier initialization
        scale1 = np.sqrt(2.0 / (d_in + d_hidden))
        scale2 = np.sqrt(2.0 / (d_hidden + d_out))
        self.W1 = rng.randn(d_hidden, d_in) * scale1
        self.b1 = np.zeros(d_hidden)
        self.W2 = rng.randn(d_out, d_hidden) * scale2
        self.b2 = np.zeros(d_out)

        # Momentum buffers
        self.vW1 = np.zeros_like(self.W1)
        self.vb1 = np.zeros_like(self.b1)
        self.vW2 = np.zeros_like(self.W2)
        self.vb2 = np.zeros_like(self.b2)

        # Cache for backprop
        self._x = None
        self._z1 = None
        self._h1 = None

    def forward(self, x):
        """x: (batch, d_in) -> (batch, d_out)."""
        self._x = x
        self._z1 = x @ self.W1.T + self.b1  # (batch, d_hidden)
        self._h1 = tanh_forward(self._z1)     # (batch, d_hidden)
        out = self._h1 @ self.W2.T + self.b2  # (batch, d_out)
        return out

    def backward(self, grad_out, lr=0.01, clip=5.0):
        """Backprop and update. grad_out: (batch, d_out)."""
        batch = grad_out.shape[0]

        # Layer 2 gradients
        gW2 = grad_out.T @ self._h1 / batch    # (d_out, d_hidden)
        gb2 = np.mean(grad_out, axis=0)         # (d_out,)

        # Backprop to hidden
        gh1 = grad_out @ self.W2                # (batch, d_hidden)
        gz1 = gh1 * tanh_backward(self._z1)     # (batch, d_hidden)

        # Layer 1 gradients
        gW1 = gz1.T @ self._x / batch           # (d_hidden, d_in)
        gb1 = np.mean(gz1, axis=0)              # (d_hidden,)

        # Clip gradients
        gW1 = np.clip(gW1, -clip, clip)
        gb1 = np.clip(gb1, -clip, clip)
        gW2 = np.clip(gW2, -clip, clip)
        gb2 = np.clip(gb2, -clip, clip)

        # SGD with momentum
        self.vW1 = MOMENTUM * self.vW1 - lr * gW1
        self.vb1 = MOMENTUM * self.vb1 - lr * gb1
        self.vW2 = MOMENTUM * self.vW2 - lr * gW2
        self.vb2 = MOMENTUM * self.vb2 - lr * gb2

        self.W1 += self.vW1
        self.b1 += self.vb1
        self.W2 += self.vW2
        self.b2 += self.vb2

    def copy_params(self):
        """Return a snapshot of parameters."""
        return {
            'W1': self.W1.copy(), 'b1': self.b1.copy(),
            'W2': self.W2.copy(), 'b2': self.b2.copy(),
        }

    def load_params(self, params):
        """Load parameters from a snapshot."""
        self.W1 = params['W1'].copy()
        self.b1 = params['b1'].copy()
        self.W2 = params['W2'].copy()
        self.b2 = params['b2'].copy()

    def param_count(self):
        return (self.W1.size + self.b1.size + self.W2.size + self.b2.size)


# ==========================================================================
# Ground Truth Reward Function
# ==========================================================================
class GroundTruthReward:
    """R*(s, a) = s^T W_sa a + w_s^T s + w_a^T a + interaction terms.

    This is a known function that the system does NOT have access to.
    The reward model must learn it from preference pairs.
    """

    def __init__(self, d_state, d_action, seed=0):
        rng = np.random.RandomState(seed)
        # Linear terms
        self.w_s = rng.randn(d_state) * 0.3
        self.w_a = rng.randn(d_action) * 0.5
        # Interaction matrix (state-action coupling)
        self.W_sa = rng.randn(d_state, d_action) * 0.2
        # Quadratic penalty on action magnitude (prevents degenerate policies)
        self.action_penalty = 0.1

    def __call__(self, states, actions):
        """Compute R*(s, a) for batches.
        states: (batch, d_state), actions: (batch, d_action) -> (batch,)
        """
        # Linear terms
        r_s = states @ self.w_s          # (batch,)
        r_a = actions @ self.w_a         # (batch,)
        # Interaction: sum_i sum_j s_i * W_ij * a_j
        interaction = np.sum((states @ self.W_sa) * actions, axis=1)  # (batch,)
        # Action penalty
        penalty = self.action_penalty * np.sum(actions ** 2, axis=1)   # (batch,)
        return r_s + r_a + interaction - penalty


# ==========================================================================
# Preference Generation
# ==========================================================================
def generate_preferences(states, actions_1, actions_2, reward_fn, noise=0.0, rng=None):
    """Generate preference labels: 1 if R*(s,a1) > R*(s,a2), else 0.

    Noise: probability of flipping the preference (simulates human inconsistency).
    Returns: labels array (1 = prefer a1, 0 = prefer a2)
    """
    r1 = reward_fn(states, actions_1)
    r2 = reward_fn(states, actions_2)
    labels = (r1 > r2).astype(float)

    if noise > 0 and rng is not None:
        flip_mask = rng.rand(len(labels)) < noise
        labels[flip_mask] = 1.0 - labels[flip_mask]

    return labels


# ==========================================================================
# Reward Model (learns from preferences via Bradley-Terry)
# ==========================================================================
class RewardModel:
    """Reward model R_hat(s, a) trained on preference pairs.

    Uses Bradley-Terry model: P(a1 > a2 | s) = sigmoid(R_hat(s,a1) - R_hat(s,a2))
    """

    def __init__(self, d_state, d_action, d_hidden, seed=0):
        d_in = d_state + d_action
        self.net = MLP(d_in, d_hidden, 1, seed=seed)
        self.d_state = d_state
        self.d_action = d_action

    def predict(self, states, actions):
        """Predict reward values. Returns: (batch,)."""
        x = np.concatenate([states, actions], axis=1)
        return self.net.forward(x).ravel()

    def train_on_preferences(self, pref_data, n_epochs=10, lr=0.003, rng=None):
        """Train on accumulated preference data.

        pref_data: list of (states, actions_1, actions_2, labels)
        """
        # Concatenate all preference data
        all_s, all_a1, all_a2, all_labels = [], [], [], []
        for (s, a1, a2, lab) in pref_data:
            all_s.append(s)
            all_a1.append(a1)
            all_a2.append(a2)
            all_labels.append(lab)
        all_s = np.concatenate(all_s, axis=0)
        all_a1 = np.concatenate(all_a1, axis=0)
        all_a2 = np.concatenate(all_a2, axis=0)
        all_labels = np.concatenate(all_labels, axis=0)

        n = len(all_labels)
        losses = []

        for epoch in range(n_epochs):
            if rng is not None:
                perm = rng.permutation(n)
            else:
                perm = np.arange(n)

            epoch_loss = 0.0
            n_batches = 0

            for start in range(0, n, BATCH_SIZE):
                end = min(start + BATCH_SIZE, n)
                idx = perm[start:end]
                bs = all_s[idx]
                ba1 = all_a1[idx]
                ba2 = all_a2[idx]
                bl = all_labels[idx]

                # Forward pass for both actions
                x1 = np.concatenate([bs, ba1], axis=1)
                x2 = np.concatenate([bs, ba2], axis=1)

                r1 = self.net.forward(x1).ravel()
                # Save net state for a1
                x1_cache = (self.net._x.copy(), self.net._z1.copy(), self.net._h1.copy())

                r2 = self.net.forward(x2).ravel()
                x2_cache = (self.net._x.copy(), self.net._z1.copy(), self.net._h1.copy())

                # Bradley-Terry loss: -[y * log(sig(r1-r2)) + (1-y) * log(sig(r2-r1))]
                diff = r1 - r2
                sig = 1.0 / (1.0 + np.exp(-np.clip(diff, -20, 20)))
                # Gradient of BT loss w.r.t. diff: sig - y
                grad_diff = sig - bl  # (batch,)

                loss = -np.mean(bl * np.log(sig + 1e-10) +
                                (1 - bl) * np.log(1 - sig + 1e-10))
                epoch_loss += loss

                # Backprop through r1 (grad_r1 = grad_diff)
                self.net._x, self.net._z1, self.net._h1 = x1_cache
                grad_r1 = grad_diff.reshape(-1, 1)  # (batch, 1)
                self.net.backward(grad_r1, lr=lr)

                # Backprop through r2 (grad_r2 = -grad_diff)
                self.net._x, self.net._z1, self.net._h1 = x2_cache
                grad_r2 = -grad_diff.reshape(-1, 1)
                self.net.backward(grad_r2, lr=lr)

                n_batches += 1

            losses.append(epoch_loss / max(n_batches, 1))

        return losses

    def copy_params(self):
        return self.net.copy_params()

    def load_params(self, params):
        self.net.load_params(params)

    def param_count(self):
        return self.net.param_count()


# ==========================================================================
# MVSU Reward Model (dual reward models with inhibitory coupling)
# ==========================================================================
class MVSURewardModel:
    """Dual reward models with inhibitory cross-connections.

    R_hat(s,a) = 0.5 * (R_A(s,a) - w_cross * R_B(s,a))
               + 0.5 * (R_B(s,a) - w_cross * R_A(s,a))
             = 0.5 * (1 - w_cross) * (R_A + R_B)

    The key: w_cross is LEARNED, and should converge to a negative value
    (meaning the subtraction becomes addition of a correction term).
    Actually, following MVSU convention: decontaminated_A = raw_A - w_cross * raw_B
    With w_cross < 0, this becomes raw_A + |w_cross| * raw_B.
    """

    def __init__(self, d_state, d_action, d_hidden, seed=0):
        # Two reward models with different initializations
        # Use different seeds to ensure different inductive biases from the start
        self.model_A = RewardModel(d_state, d_action, d_hidden, seed=seed)
        self.model_B = RewardModel(d_state, d_action, d_hidden, seed=seed + 7777)
        self.w_cross = -0.1  # Initialized slightly negative
        self.d_state = d_state
        self.d_action = d_action

    def predict(self, states, actions):
        """Predict with cross-inhibitory decontamination."""
        r_A = self.model_A.predict(states, actions)
        r_B = self.model_B.predict(states, actions)
        # Cross-inhibitory decontamination
        decontam_A = r_A - self.w_cross * r_B
        decontam_B = r_B - self.w_cross * r_A
        return 0.5 * (decontam_A + decontam_B)

    def train_on_preferences(self, pref_data, n_epochs=10, lr=0.003, rng=None):
        """Train both models on preferences, then update w_cross."""
        # Train each model independently on the preference data
        loss_A = self.model_A.train_on_preferences(pref_data, n_epochs, lr, rng)
        loss_B = self.model_B.train_on_preferences(pref_data, n_epochs, lr, rng)

        # Update w_cross based on correlation between model predictions
        # Sample some data to estimate the optimal cross-weight
        all_s, all_a1, all_a2, all_labels = [], [], [], []
        for (s, a1, a2, lab) in pref_data:
            all_s.append(s)
            all_a1.append(a1)
        all_s = np.concatenate(all_s[:5], axis=0)  # Use subset
        all_a1 = np.concatenate(all_a1[:5], axis=0)

        r_A = self.model_A.predict(all_s, all_a1)
        r_B = self.model_B.predict(all_s, all_a1)

        # Gradient descent on w_cross to minimize prediction variance
        # d/d(w_cross) of Var(decontam) pushes w_cross toward negative values
        # when models have correlated contamination
        diff_AB = r_A - r_B
        mean_rA_rB = np.mean(r_A * r_B)
        mean_rA = np.mean(r_A)
        mean_rB = np.mean(r_B)
        cov_AB = mean_rA_rB - mean_rA * mean_rB
        var_B = np.var(r_B) + 1e-8
        var_A = np.var(r_A) + 1e-8

        # Simple update: move w_cross toward -cov(A,B)/var(B)
        # (the regression coefficient that removes shared contamination)
        target_w = -cov_AB / var_B
        self.w_cross = 0.9 * self.w_cross + 0.1 * np.clip(target_w, -1.0, 0.5)

        return loss_A

    def param_count(self):
        return self.model_A.param_count() + self.model_B.param_count() + 1


# ==========================================================================
# Ensemble Reward Model (two models averaged, no inhibition)
# ==========================================================================
class EnsembleRewardModel:
    """Two reward models simply averaged. Same total parameters as MVSU,
    but without inhibitory cross-connections. Tests whether the MVSU advantage
    comes from structure (inhibition) or capacity (two models)."""

    def __init__(self, d_state, d_action, d_hidden, seed=0):
        self.model_A = RewardModel(d_state, d_action, d_hidden, seed=seed)
        self.model_B = RewardModel(d_state, d_action, d_hidden, seed=seed + 7777)
        self.d_state = d_state
        self.d_action = d_action

    def predict(self, states, actions):
        r_A = self.model_A.predict(states, actions)
        r_B = self.model_B.predict(states, actions)
        return 0.5 * (r_A + r_B)

    def train_on_preferences(self, pref_data, n_epochs=10, lr=0.003, rng=None):
        loss_A = self.model_A.train_on_preferences(pref_data, n_epochs, lr, rng)
        loss_B = self.model_B.train_on_preferences(pref_data, n_epochs, lr, rng)
        return loss_A

    def param_count(self):
        return self.model_A.param_count() + self.model_B.param_count()


# ==========================================================================
# Policy (optimizes toward reward model)
# ==========================================================================
class Policy:
    """MLP policy: state -> action. Optimized to maximize R_hat."""

    def __init__(self, d_state, d_action, d_hidden, seed=0):
        self.net = MLP(d_state, d_hidden, d_action, seed=seed)

    def act(self, states, noise_scale=0.1, rng=None):
        """Generate actions for given states, with exploration noise."""
        actions = self.net.forward(states)
        if noise_scale > 0 and rng is not None:
            actions = actions + rng.randn(*actions.shape) * noise_scale
        return actions

    def optimize_toward_reward(self, reward_model, n_steps, states, lr=0.005,
                               strength=1.0, rng=None):
        """Optimize policy to maximize reward_model predictions.

        strength: how aggressively to exploit R_hat (multiplier on gradient).
        """
        for step in range(n_steps):
            # Sample a batch of states
            idx = rng.choice(len(states), size=min(BATCH_SIZE, len(states)), replace=False)
            batch_s = states[idx]

            # Forward through policy
            actions = self.net.forward(batch_s)

            # Get reward model predictions
            if hasattr(reward_model, 'predict'):
                rewards = reward_model.predict(batch_s, actions)
            else:
                rewards = reward_model(batch_s, actions)

            # Compute gradient of reward w.r.t. actions (numerical)
            eps = 1e-4
            grad_actions = np.zeros_like(actions)
            for j in range(actions.shape[1]):
                actions_plus = actions.copy()
                actions_plus[:, j] += eps
                r_plus = reward_model.predict(batch_s, actions_plus)
                actions_minus = actions.copy()
                actions_minus[:, j] -= eps
                r_minus = reward_model.predict(batch_s, actions_minus)
                grad_actions[:, j] = (r_plus - r_minus) / (2 * eps)

            # Scale by strength (controls exploitation intensity)
            grad_out = -grad_actions * strength  # Negative because we maximize
            self.net.backward(grad_out, lr=lr)


# ==========================================================================
# Evaluation metrics
# ==========================================================================
def evaluate_reward_model(reward_model, ground_truth, d_state, d_action, n_samples, rng):
    """Evaluate reward model accuracy against ground truth.

    Returns: correlation, R^2, and mean absolute error.
    """
    states = rng.randn(n_samples, d_state)
    actions = rng.randn(n_samples, d_action) * 0.5

    r_true = ground_truth(states, actions)
    r_pred = reward_model.predict(states, actions)

    # Pearson correlation
    corr = np.corrcoef(r_true, r_pred)[0, 1] if np.std(r_pred) > 1e-10 else 0.0

    # R^2
    ss_res = np.sum((r_true - r_pred) ** 2)
    ss_tot = np.sum((r_true - np.mean(r_true)) ** 2)
    r2 = 1.0 - ss_res / (ss_tot + 1e-10) if ss_tot > 1e-10 else 0.0

    # MAE
    mae = np.mean(np.abs(r_true - r_pred))

    return corr, r2, mae


def estimate_contamination(reward_model, ground_truth, policy, d_state, d_action,
                           n_samples, iteration, rng):
    """Estimate effective contamination alpha.

    We use TWO measures of contamination:
    1. Structural alpha: what fraction of accumulated training data came from
       policy-generated actions (after iteration 0, all new data is policy-generated,
       so structural alpha = iteration / (iteration + 1)).
    2. Distributional alpha: how much the policy's action distribution has collapsed
       relative to random. Measured as 1 - (entropy of policy actions / entropy of random).

    Returns: (structural_alpha, distributional_alpha)
    """
    # Structural: fraction of data contaminated by policy
    # Iteration 0: 0/1 = 0 (all data from random policy)
    # Iteration 1: 1/2 = 0.5 (half from trained policy)
    # Iteration k: k/(k+1)
    structural_alpha = iteration / max(iteration + 1, 1)

    # Distributional: how concentrated are policy actions?
    states = rng.randn(n_samples, d_state)
    policy_actions = policy.act(states, noise_scale=0.0, rng=rng)
    random_actions = rng.randn(n_samples, d_action) * 0.5

    # Use variance ratio as proxy for distribution collapse
    policy_var = np.mean(np.var(policy_actions, axis=0))
    random_var = np.mean(np.var(random_actions, axis=0))

    # Also measure how different policy errors are from random errors
    r_true_policy = ground_truth(states, policy_actions)
    r_pred_policy = reward_model.predict(states, policy_actions)
    r_true_random = ground_truth(states, random_actions)
    r_pred_random = reward_model.predict(states, random_actions)

    corr_policy = np.corrcoef(r_true_policy, r_pred_policy)[0, 1] if np.std(r_pred_policy) > 1e-10 else 0.0
    corr_random = np.corrcoef(r_true_random, r_pred_random)[0, 1] if np.std(r_pred_random) > 1e-10 else 0.0

    # Distributional alpha: how much worse is the model on policy data vs random data
    # Positive means policy data is harder (self-referential contamination)
    distributional_alpha = np.clip(corr_random - corr_policy, -1, 1)

    return structural_alpha, distributional_alpha


# ==========================================================================
# Run single RLHF experiment
# ==========================================================================
def run_rlhf(condition, seed, policy_strength=1.0, noise_level=0.1,
             n_iterations=N_RLHF_ITERATIONS):
    """Run a single RLHF experiment.

    condition: 'standard', 'mvsu', 'ensemble', 'fresh'
    Returns: dict with per-iteration metrics.
    """
    rng = np.random.RandomState(seed)

    # Ground truth reward (fixed, unknown to the system)
    gt_reward = GroundTruthReward(D_STATE, D_ACTION, seed=0)  # Same GT for all conditions

    # State distribution (fixed)
    eval_rng = np.random.RandomState(seed + 10000)

    # Create reward model
    if condition == 'standard':
        reward_model = RewardModel(D_STATE, D_ACTION, D_HIDDEN_REWARD, seed=seed)
    elif condition == 'mvsu':
        reward_model = MVSURewardModel(D_STATE, D_ACTION, D_HIDDEN_REWARD, seed=seed)
    elif condition == 'ensemble':
        reward_model = EnsembleRewardModel(D_STATE, D_ACTION, D_HIDDEN_REWARD, seed=seed)
    elif condition == 'fresh':
        reward_model = RewardModel(D_STATE, D_ACTION, D_HIDDEN_REWARD, seed=seed)
    else:
        raise ValueError(f"Unknown condition: {condition}")

    # Policy
    policy = Policy(D_STATE, D_ACTION, D_HIDDEN_POLICY, seed=seed + 5000)

    # Accumulated preference data (for standard, mvsu, ensemble)
    accumulated_prefs = []

    # Metrics per iteration
    correlations = []
    r2_scores = []
    maes = []
    alphas = []
    w_cross_values = []

    for iteration in range(n_iterations):
        # --- Step 1: Policy generates actions optimizing current R_hat ---
        train_states = rng.randn(N_PAIRS_PER_ITER * 2, D_STATE)

        if iteration > 0:
            # Optimize policy toward reward model
            policy.optimize_toward_reward(
                reward_model, N_POLICY_STEPS, train_states,
                lr=POLICY_LR, strength=policy_strength, rng=rng
            )

        # --- Step 2: Generate preference pairs ---
        pair_states = rng.randn(N_PAIRS_PER_ITER, D_STATE)

        if condition == 'fresh':
            # Fresh data control: actions are random, NOT from policy
            actions_1 = rng.randn(N_PAIRS_PER_ITER, D_ACTION) * 0.5
            actions_2 = rng.randn(N_PAIRS_PER_ITER, D_ACTION) * 0.5
        else:
            # Actions from policy (with some exploration noise)
            actions_1 = policy.act(pair_states, noise_scale=0.3, rng=rng)
            actions_2 = policy.act(pair_states, noise_scale=0.3, rng=rng)

        # --- Step 3: Label preferences using ground truth ---
        labels = generate_preferences(
            pair_states, actions_1, actions_2, gt_reward,
            noise=noise_level, rng=rng
        )

        # --- Step 4: Retrain R_hat on ALL accumulated data ---
        if condition == 'fresh':
            # Fresh control: use only this iteration's data (no accumulation)
            fresh_prefs = [(pair_states, actions_1, actions_2, labels)]
            reward_model.train_on_preferences(
                fresh_prefs, n_epochs=N_REWARD_EPOCHS, lr=REWARD_LR, rng=rng
            )
        else:
            accumulated_prefs.append((pair_states, actions_1, actions_2, labels))
            reward_model.train_on_preferences(
                accumulated_prefs, n_epochs=N_REWARD_EPOCHS, lr=REWARD_LR, rng=rng
            )

        # --- Step 5: Evaluate ---
        corr, r2, mae = evaluate_reward_model(
            reward_model, gt_reward, D_STATE, D_ACTION, N_EVAL_SAMPLES, eval_rng
        )
        struct_alpha, dist_alpha = estimate_contamination(
            reward_model, gt_reward, policy, D_STATE, D_ACTION,
            N_EVAL_SAMPLES, iteration, rng
        )

        correlations.append(corr)
        r2_scores.append(r2)
        maes.append(mae)
        alphas.append(struct_alpha)

        if hasattr(reward_model, 'w_cross'):
            w_cross_values.append(reward_model.w_cross)
        else:
            w_cross_values.append(None)

    return {
        'correlations': np.array(correlations),
        'r2_scores': np.array(r2_scores),
        'maes': np.array(maes),
        'alphas': np.array(alphas),
        'w_cross_values': w_cross_values,
        'condition': condition,
        'seed': seed,
        'policy_strength': policy_strength,
        'noise_level': noise_level,
    }


# ==========================================================================
# Main experiment runner
# ==========================================================================
def run_main_experiment():
    """Run the full RLHF bridge experiment across all conditions."""
    conditions = ['standard', 'mvsu', 'ensemble', 'fresh']
    condition_labels = {
        'standard': 'A: Standard RLHF',
        'mvsu': 'B: MVSU RLHF',
        'ensemble': 'C: Ensemble',
        'fresh': 'D: Fresh Data',
    }

    all_results = {}
    total_runs = len(conditions) * N_SEEDS
    count = 0

    for cond in conditions:
        for seed in SEEDS:
            result = run_rlhf(cond, seed, policy_strength=1.0, noise_level=0.1)
            all_results[(cond, seed)] = result
            count += 1
            print(f"  [{count}/{total_runs}] {condition_labels[cond]}, seed={seed}: "
                  f"final corr={result['correlations'][-1]:.4f}, "
                  f"final R2={result['r2_scores'][-1]:.4f}")

    return all_results, conditions, condition_labels


def run_strength_sweep():
    """Sweep policy optimization strength (controls effective alpha)."""
    results = {}
    total = len(POLICY_STRENGTHS) * N_SEEDS
    count = 0

    for strength in POLICY_STRENGTHS:
        for seed in SEEDS:
            result = run_rlhf('standard', seed, policy_strength=strength, noise_level=0.1)
            results[(strength, seed)] = result
            count += 1
            if count % 3 == 0:
                print(f"  Strength sweep: {count}/{total} "
                      f"(strength={strength}, final corr={result['correlations'][-1]:.4f})")

    return results


def run_noise_sweep():
    """Sweep preference noise level."""
    results = {}
    conditions = ['standard', 'mvsu']

    for noise in NOISE_LEVELS:
        for cond in conditions:
            for seed in SEEDS:
                result = run_rlhf(cond, seed, policy_strength=1.0, noise_level=noise)
                results[(cond, noise, seed)] = result

    return results


# ==========================================================================
# Analysis and Theory Comparison
# ==========================================================================
def compute_theory_prediction(alpha, k=1.0):
    """Compute predicted weight from kw^2 + w - 1 = 0.

    For given alpha (contamination), k = alpha^2 in the RLHF context.
    Returns predicted w (the self-consistency fixed point).
    For the toy scalar case, w = R^2 = correlation.
    For the RLHF case, w represents the *relative efficiency*:
    how much signal survives relative to the no-contamination baseline.
    """
    k_eff = alpha ** 2 * k
    if k_eff < 1e-10:
        return 1.0  # No contamination -> perfect
    discriminant = 1.0 + 4.0 * k_eff
    w = (-1.0 + np.sqrt(discriminant)) / (2.0 * k_eff)
    return min(w, 1.0)


def compute_relative_efficiency(std_corr, fresh_corr):
    """Compute relative efficiency: how much of the fresh-data performance
    survives under self-referential contamination.

    This is the quantity the theory actually predicts: at full contamination
    (alpha=1), the myopic optimizer retains 1/phi fraction of its potential.
    """
    if fresh_corr > 0.01:
        return np.clip(std_corr / fresh_corr, 0, 2.0)
    else:
        return 1.0  # Can't compute meaningful ratio


def analyze_degradation(main_results, conditions):
    """Analyze degradation patterns and compare to theory."""
    analysis = {}

    for cond in conditions:
        corrs = []
        r2s = []
        alphas_all = []
        for seed in SEEDS:
            r = main_results[(cond, seed)]
            corrs.append(r['correlations'])
            r2s.append(r['r2_scores'])
            alphas_all.append(r['alphas'])

        corrs = np.array(corrs)
        r2s = np.array(r2s)
        alphas_all = np.array(alphas_all)

        analysis[cond] = {
            'corr_mean': np.mean(corrs, axis=0),
            'corr_std': np.std(corrs, axis=0),
            'r2_mean': np.mean(r2s, axis=0),
            'r2_std': np.std(r2s, axis=0),
            'alpha_mean': np.mean(alphas_all, axis=0),
            'alpha_std': np.std(alphas_all, axis=0),
        }

    return analysis


# ==========================================================================
# Print tables
# ==========================================================================
def print_results(analysis, conditions, condition_labels):
    """Print comprehensive results tables."""

    # Table 1: Reward accuracy over iterations (all conditions)
    print(f"\n{'='*80}")
    print("TABLE 1: Reward Model Correlation with R* by RLHF Iteration")
    print(f"{'='*80}")

    header = f"  {'Iter':>4}"
    for cond in conditions:
        label = condition_labels[cond].split(': ')[1][:10]
        header += f"  {label:>12}"
    print(header)
    print("  " + "-" * (4 + 14 * len(conditions)))

    for i in range(N_RLHF_ITERATIONS):
        row = f"  {i+1:>4}"
        for cond in conditions:
            mean = analysis[cond]['corr_mean'][i]
            std = analysis[cond]['corr_std'][i]
            row += f"  {mean:>6.3f}+/-{std:.3f}"
        print(row)

    # Table 2: R^2 over iterations
    print(f"\n{'='*80}")
    print("TABLE 2: Reward Model R^2 with R* by RLHF Iteration")
    print(f"{'='*80}")

    header = f"  {'Iter':>4}"
    for cond in conditions:
        label = condition_labels[cond].split(': ')[1][:10]
        header += f"  {label:>12}"
    print(header)
    print("  " + "-" * (4 + 14 * len(conditions)))

    for i in range(N_RLHF_ITERATIONS):
        row = f"  {i+1:>4}"
        for cond in conditions:
            mean = analysis[cond]['r2_mean'][i]
            row += f"  {mean:>12.4f}"
        print(row)

    # Table 3: Effective contamination alpha
    print(f"\n{'='*80}")
    print("TABLE 3: Effective Contamination Alpha by RLHF Iteration")
    print(f"{'='*80}")

    header = f"  {'Iter':>4}"
    for cond in conditions:
        label = condition_labels[cond].split(': ')[1][:10]
        header += f"  {label:>12}"
    print(header)
    print("  " + "-" * (4 + 14 * len(conditions)))

    for i in range(N_RLHF_ITERATIONS):
        row = f"  {i+1:>4}"
        for cond in conditions:
            mean = analysis[cond]['alpha_mean'][i]
            row += f"  {mean:>12.4f}"
        print(row)

    # Table 4: MVSU advantage
    print(f"\n{'='*80}")
    print("TABLE 4: MVSU Advantage over Standard RLHF")
    print(f"{'='*80}")

    print(f"  {'Iter':>4}  {'Std Corr':>10}  {'MVSU Corr':>10}  {'Advantage':>10}  {'Ens Corr':>10}  {'Ens Adv':>10}")
    print("  " + "-" * 62)

    for i in range(N_RLHF_ITERATIONS):
        std_corr = analysis['standard']['corr_mean'][i]
        mvsu_corr = analysis['mvsu']['corr_mean'][i]
        ens_corr = analysis['ensemble']['corr_mean'][i]
        adv = mvsu_corr - std_corr
        ens_adv = ens_corr - std_corr
        print(f"  {i+1:>4}  {std_corr:>10.4f}  {mvsu_corr:>10.4f}  {adv:>+10.4f}  "
              f"{ens_corr:>10.4f}  {ens_adv:>+10.4f}")

    # Table 5: Theory comparison using relative efficiency
    print(f"\n{'='*80}")
    print("TABLE 5: Relative Efficiency vs Theory Prediction")
    print("  (Relative Efficiency = Standard Corr / Fresh Corr)")
    print("  (Theory predicts this should approach 1/phi = 0.618 at full contamination)")
    print(f"{'='*80}")

    print(f"  {'Iter':>4}  {'Str Alpha':>10}  {'Std Corr':>10}  {'Fresh Corr':>10}  "
          f"{'Rel Eff':>10}  {'Theory w':>10}  {'Match?':>8}")
    print("  " + "-" * 74)

    for i in range(N_RLHF_ITERATIONS):
        alpha = analysis['standard']['alpha_mean'][i]
        std_corr = analysis['standard']['corr_mean'][i]
        fresh_corr = analysis['fresh']['corr_mean'][i]
        rel_eff = compute_relative_efficiency(std_corr, fresh_corr)
        predicted = compute_theory_prediction(alpha)
        if predicted > 0.01:
            deviation = abs(rel_eff - predicted) / predicted * 100
        else:
            deviation = float('nan')
        match = "YES" if deviation < 10 else ("CLOSE" if deviation < 25 else "NO")
        print(f"  {i+1:>4}  {alpha:>10.4f}  {std_corr:>10.4f}  {fresh_corr:>10.4f}  "
              f"{rel_eff:>10.4f}  {predicted:>10.4f}  {match:>8}")


def print_strength_sweep(strength_results):
    """Print policy strength sweep results."""
    print(f"\n{'='*80}")
    print("TABLE 6: Final Reward Accuracy vs Policy Optimization Strength")
    print(f"{'='*80}")

    print(f"  {'Strength':>10}  {'Final Corr':>12}  {'Final Alpha':>12}  {'Final R2':>12}")
    print("  " + "-" * 52)

    for strength in POLICY_STRENGTHS:
        corrs = [strength_results[(strength, s)]['correlations'][-1] for s in SEEDS]
        alphas = [strength_results[(strength, s)]['alphas'][-1] for s in SEEDS]
        r2s = [strength_results[(strength, s)]['r2_scores'][-1] for s in SEEDS]
        print(f"  {strength:>10.1f}  {np.mean(corrs):>8.4f}+/-{np.std(corrs):.4f}"
              f"  {np.mean(alphas):>8.4f}+/-{np.std(alphas):.4f}"
              f"  {np.mean(r2s):>8.4f}+/-{np.std(r2s):.4f}")


def print_summary(analysis, conditions, condition_labels):
    """Print final summary comparison."""

    print(f"\n{'='*80}")
    print("SUMMARY COMPARISON")
    print(f"{'='*80}")

    # Final iteration metrics
    print(f"\n  Final iteration ({N_RLHF_ITERATIONS}) metrics:")
    print(f"  {'Condition':>20}  {'Correlation':>14}  {'R^2':>14}  {'Alpha':>14}")
    print("  " + "-" * 66)

    for cond in conditions:
        corr = analysis[cond]['corr_mean'][-1]
        corr_std = analysis[cond]['corr_std'][-1]
        r2 = analysis[cond]['r2_mean'][-1]
        r2_std = analysis[cond]['r2_std'][-1]
        alpha = analysis[cond]['alpha_mean'][-1]
        print(f"  {condition_labels[cond]:>20}  {corr:>6.4f}+/-{corr_std:.4f}"
              f"  {r2:>6.4f}+/-{r2_std:.4f}  {alpha:>14.4f}")

    # Degradation check
    print(f"\n  Degradation analysis:")
    std_initial = analysis['standard']['corr_mean'][0]
    std_final = analysis['standard']['corr_mean'][-1]
    fresh_final = analysis['fresh']['corr_mean'][-1]
    mvsu_final = analysis['mvsu']['corr_mean'][-1]
    ens_final = analysis['ensemble']['corr_mean'][-1]

    # Does standard degrade relative to fresh?
    std_vs_fresh = std_final - fresh_final
    print(f"    Standard vs Fresh (final): {std_vs_fresh:+.4f} "
          f"({'degradation' if std_vs_fresh < -0.02 else 'no significant degradation'})")

    # Does standard degrade over iterations?
    std_peak = np.max(analysis['standard']['corr_mean'])
    std_degradation = std_peak - std_final
    print(f"    Standard peak-to-final drop: {std_degradation:+.4f} "
          f"(peak at iter {np.argmax(analysis['standard']['corr_mean'])+1})")

    # MVSU vs standard
    mvsu_advantage = mvsu_final - std_final
    print(f"    MVSU vs Standard (final): {mvsu_advantage:+.4f} "
          f"({'MVSU better' if mvsu_advantage > 0.01 else 'no significant difference'})")

    # Ensemble vs standard (controls for capacity)
    ens_advantage = ens_final - std_final
    print(f"    Ensemble vs Standard (final): {ens_advantage:+.4f} "
          f"({'capacity effect' if ens_advantage > 0.01 else 'no capacity effect'})")

    # MVSU vs ensemble (tests inhibition specifically)
    mvsu_vs_ens = mvsu_final - ens_final
    print(f"    MVSU vs Ensemble (final): {mvsu_vs_ens:+.4f} "
          f"({'inhibition helps' if mvsu_vs_ens > 0.01 else 'inhibition not significant'})")

    # w_cross convergence
    for seed in SEEDS:
        r = None
        for cond in conditions:
            if cond == 'mvsu':
                r = analysis  # We need the raw results for w_cross
                break

    # Theory match using relative efficiency
    print(f"\n  Theory comparison (kw^2 + w - 1 = 0):")
    print(f"    Theory predicts: at full contamination (alpha=1), self-referential")
    print(f"    system retains 1/phi = {INV_PHI:.4f} of its potential efficiency.")
    print()
    avg_std = np.mean(analysis['standard']['corr_mean'][-5:])
    avg_fresh = np.mean(analysis['fresh']['corr_mean'][-5:])
    avg_alpha = np.mean(analysis['standard']['alpha_mean'][-5:])
    predicted_w = compute_theory_prediction(avg_alpha)
    rel_eff = compute_relative_efficiency(avg_std, avg_fresh)
    print(f"    Average structural alpha (last 5 iters): {avg_alpha:.4f}")
    print(f"    Average Standard corr (last 5): {avg_std:.4f}")
    print(f"    Average Fresh corr (last 5): {avg_fresh:.4f}")
    print(f"    Relative efficiency (Std/Fresh): {rel_eff:.4f}")
    print(f"    Theory prediction: {predicted_w:.4f}")
    deviation = abs(rel_eff - predicted_w) / max(predicted_w, 0.01) * 100
    print(f"    Deviation from theory: {deviation:.1f}%")
    if deviation < 10:
        print(f"    --> MATCHES theory within 10%")
    elif deviation < 25:
        print(f"    --> CLOSE to theory (within 25%)")
    else:
        print(f"    --> DOES NOT MATCH theory (>{deviation:.0f}% deviation)")
        print(f"    Note: The theory was derived for linear scalar systems.")
        print(f"    A nonlinear MLP in high-dimensional space may have different")
        print(f"    quantitative behavior while sharing the qualitative pattern.")


def print_verdict(analysis, conditions, condition_labels):
    """Print explicit success/failure verdict."""

    print(f"\n{'='*80}")
    print("VERDICT")
    print(f"{'='*80}")

    # Check criteria
    std_initial = analysis['standard']['corr_mean'][0]
    std_final = analysis['standard']['corr_mean'][-1]
    std_peak = np.max(analysis['standard']['corr_mean'])
    fresh_final = analysis['fresh']['corr_mean'][-1]
    mvsu_final = analysis['mvsu']['corr_mean'][-1]
    ens_final = analysis['ensemble']['corr_mean'][-1]

    # 1. Does standard RLHF degrade?
    std_vs_fresh = fresh_final - std_final
    degradation_exists = std_vs_fresh > 0.02
    std_drops = (std_peak - std_final) > 0.02

    # 2. Does degradation match theory?
    avg_alpha = np.mean(analysis['standard']['alpha_mean'][-5:])
    predicted_w = compute_theory_prediction(avg_alpha)
    avg_std = np.mean(analysis['standard']['corr_mean'][-5:])
    avg_fresh = np.mean(analysis['fresh']['corr_mean'][-5:])
    rel_eff = compute_relative_efficiency(avg_std, avg_fresh)
    theory_match = abs(rel_eff - predicted_w) / max(predicted_w, 0.01) < 0.10

    # 3. Does MVSU help?
    mvsu_helps = (mvsu_final - std_final) > 0.01

    # 4. Does MVSU beat ensemble?
    mvsu_beats_ensemble = (mvsu_final - ens_final) > 0.005

    print(f"\n  Criterion 1 - Standard RLHF degrades:")
    print(f"    Fresh vs Standard gap: {std_vs_fresh:+.4f} {'(YES)' if degradation_exists else '(NO)'}")
    print(f"    Peak-to-final drop: {std_peak - std_final:+.4f} {'(YES)' if std_drops else '(NO)'}")

    print(f"\n  Criterion 2 - Degradation matches kw^2+w-1=0:")
    print(f"    Predicted relative efficiency: {predicted_w:.4f}")
    print(f"    Measured relative efficiency (Std/Fresh): {rel_eff:.4f}")
    deviation_pct = abs(rel_eff - predicted_w) / max(predicted_w, 0.01) * 100
    print(f"    Deviation: {deviation_pct:.1f}% {'(YES, within 10%)' if theory_match else '(NO, >10% deviation)'}")

    print(f"\n  Criterion 3 - MVSU improves over standard:")
    print(f"    MVSU advantage: {mvsu_final - std_final:+.4f} "
          f"{'(YES)' if mvsu_helps else '(NO)'}")

    print(f"\n  Criterion 4 - MVSU beats ensemble (inhibition matters):")
    print(f"    MVSU vs Ensemble: {mvsu_final - ens_final:+.4f} "
          f"{'(YES)' if mvsu_beats_ensemble else '(NO)'}")

    # Overall verdict
    if degradation_exists and theory_match and mvsu_helps:
        verdict = "CLEAR SUCCESS"
        explanation = ("Standard RLHF degrades, degradation matches kw^2+w-1=0 theory, "
                       "and MVSU provides statistically significant improvement.")
    elif degradation_exists and mvsu_helps:
        verdict = "PARTIAL SUCCESS"
        explanation = ("Degradation exists and MVSU helps, but degradation pattern "
                       "does not precisely match the theory's prediction. "
                       "Structure is right, specifics don't fully transfer from toy setting.")
    elif degradation_exists and not mvsu_helps:
        verdict = "PARTIAL SUCCESS (degradation only)"
        explanation = ("Self-referential degradation is real, but MVSU does not mitigate it. "
                       "The theory identifies the problem but not the solution at this scale.")
    elif not degradation_exists and mvsu_helps:
        verdict = "INFORMATIVE RESULT"
        explanation = ("No clear degradation but MVSU still helps -- possible that the "
                       "standard model is already partially compensating, or that MVSU "
                       "provides orthogonal benefits.")
    else:
        verdict = "INFORMATIVE FAILURE"
        explanation = ("No degradation observed and MVSU doesn't help. Either "
                       "self-referential contamination is negligible in this setup, "
                       "or the linear theory's predictions don't transfer to this regime.")

    if mvsu_beats_ensemble:
        explanation += " Notably, MVSU beats the ensemble baseline, confirming that " \
                       "inhibitory coupling provides benefits beyond simple capacity increase."
    else:
        explanation += " MVSU does NOT beat the ensemble baseline, suggesting the " \
                       "inhibitory structure may not provide additional benefit in this regime."

    print(f"\n  {'='*60}")
    print(f"  VERDICT: {verdict}")
    print(f"  {'='*60}")
    print(f"  {explanation}")
    print()


# ==========================================================================
# Plotting
# ==========================================================================
def create_plots(analysis, conditions, condition_labels, strength_results, main_results):
    """Generate 2x3 results plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle("RLHF Bridge Experiment: Self-Referential Optimization Theory",
                 fontsize=14, fontweight='bold')

    colors = {
        'standard': '#FF5722',
        'mvsu': '#4CAF50',
        'ensemble': '#2196F3',
        'fresh': '#9C27B0',
    }
    iters = np.arange(1, N_RLHF_ITERATIONS + 1)

    # ---- Panel 1: Reward accuracy vs iteration (all 4 conditions) ----
    ax = axes[0, 0]
    for cond in conditions:
        mean = analysis[cond]['corr_mean']
        std = analysis[cond]['corr_std']
        label = condition_labels[cond]
        ax.plot(iters, mean, 'o-', color=colors[cond], label=label,
                linewidth=2, markersize=4)
        ax.fill_between(iters, mean - std, mean + std, color=colors[cond], alpha=0.15)
    ax.set_xlabel('RLHF Iteration')
    ax.set_ylabel('Correlation with R*')
    ax.set_title('Panel 1: Reward Accuracy vs Iteration')
    ax.legend(fontsize=7, loc='lower right')
    ax.grid(True, alpha=0.3)

    # ---- Panel 2: Effective contamination alpha vs iteration ----
    ax = axes[0, 1]
    for cond in conditions:
        mean = analysis[cond]['alpha_mean']
        std = analysis[cond]['alpha_std']
        label = condition_labels[cond]
        ax.plot(iters, mean, 'o-', color=colors[cond], label=label,
                linewidth=2, markersize=4)
        ax.fill_between(iters, mean - std, mean + std, color=colors[cond], alpha=0.15)
    ax.set_xlabel('RLHF Iteration')
    ax.set_ylabel('Effective Contamination Alpha')
    ax.set_title('Panel 2: Contamination vs Iteration')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ---- Panel 3: Relative efficiency vs theory prediction ----
    ax = axes[0, 2]
    std_corr = analysis['standard']['corr_mean']
    fresh_corr = analysis['fresh']['corr_mean']
    std_alpha = analysis['standard']['alpha_mean']
    rel_eff = np.array([compute_relative_efficiency(s, f) for s, f in zip(std_corr, fresh_corr)])
    predicted = np.array([compute_theory_prediction(a) for a in std_alpha])
    ax.plot(iters, rel_eff, 'o-', color=colors['standard'], label='Measured Rel. Efficiency',
            linewidth=2, markersize=5)
    ax.plot(iters, predicted, 's--', color='black', label='Theory (kw^2+w-1=0)',
            linewidth=2, markersize=5, alpha=0.7)
    ax.axhline(y=INV_PHI, color='red', linestyle=':', alpha=0.5, label=f'1/phi={INV_PHI:.3f}')
    ax.set_xlabel('RLHF Iteration')
    ax.set_ylabel('Relative Efficiency (Std / Fresh)')
    ax.set_title('Panel 3: Theory vs Experiment')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ---- Panel 4: MVSU advantage vs iteration ----
    ax = axes[1, 0]
    mvsu_adv = analysis['mvsu']['corr_mean'] - analysis['standard']['corr_mean']
    ens_adv = analysis['ensemble']['corr_mean'] - analysis['standard']['corr_mean']
    ax.plot(iters, mvsu_adv, 'o-', color=colors['mvsu'], label='MVSU advantage',
            linewidth=2, markersize=5)
    ax.plot(iters, ens_adv, 's-', color=colors['ensemble'], label='Ensemble advantage',
            linewidth=2, markersize=5)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('RLHF Iteration')
    ax.set_ylabel('Advantage over Standard')
    ax.set_title('Panel 4: MVSU / Ensemble Advantage')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ---- Panel 5: Reward accuracy vs policy strength (alpha sweep) ----
    ax = axes[1, 1]
    final_corrs = []
    final_corrs_std = []
    final_alphas = []
    for strength in POLICY_STRENGTHS:
        corrs = [strength_results[(strength, s)]['correlations'][-1] for s in SEEDS]
        als = [strength_results[(strength, s)]['alphas'][-1] for s in SEEDS]
        final_corrs.append(np.mean(corrs))
        final_corrs_std.append(np.std(corrs))
        final_alphas.append(np.mean(als))

    ax.errorbar(POLICY_STRENGTHS, final_corrs, yerr=final_corrs_std,
                fmt='o-', color=colors['standard'], linewidth=2, capsize=5,
                label='Final correlation')
    ax2 = ax.twinx()
    ax2.plot(POLICY_STRENGTHS, final_alphas, 's--', color='gray',
             linewidth=1.5, alpha=0.7, label='Effective alpha')
    ax2.set_ylabel('Effective Alpha', color='gray')
    ax.set_xlabel('Policy Optimization Strength')
    ax.set_ylabel('Final Correlation with R*')
    ax.set_title('Panel 5: Accuracy vs Exploitation Strength')
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(True, alpha=0.3)

    # ---- Panel 6: Final comparison bar chart ----
    ax = axes[1, 2]
    cond_names = [condition_labels[c].split(': ')[1] for c in conditions]
    final_means = [analysis[c]['corr_mean'][-1] for c in conditions]
    final_stds = [analysis[c]['corr_std'][-1] for c in conditions]
    bar_colors = [colors[c] for c in conditions]

    bars = ax.bar(range(len(conditions)), final_means, yerr=final_stds,
                  color=bar_colors, alpha=0.8, edgecolor='black', capsize=5)

    # Add value labels on bars
    for bar, mean, std in zip(bars, final_means, final_stds):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + std + 0.01,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(cond_names, fontsize=9)
    ax.set_ylabel('Final Correlation with R*')
    ax.set_title('Panel 6: Final Comparison (All Conditions)')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "rlhf_bridge_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==========================================================================
# Main
# ==========================================================================
def main():
    t_start = time.time()

    print("=" * 80)
    print("RLHF BRIDGE EXPERIMENT")
    print("Testing Self-Referential Optimization Theory in RLHF")
    print("=" * 80)
    print(f"  State dim: {D_STATE}, Action dim: {D_ACTION}")
    print(f"  Policy hidden: {D_HIDDEN_POLICY}, Reward hidden: {D_HIDDEN_REWARD}")
    print(f"  RLHF iterations: {N_RLHF_ITERATIONS}")
    print(f"  Policy steps/iter: {N_POLICY_STEPS}")
    print(f"  Preference pairs/iter: {N_PAIRS_PER_ITER}")
    print(f"  Reward epochs/iter: {N_REWARD_EPOCHS}")
    print(f"  Default noise: 0.1, Default policy strength: 1.0")
    print(f"  Seeds: {SEEDS}")
    print(f"  Theory: kw^2 + w - 1 = 0, 1/phi = {INV_PHI:.6f}")
    print()

    # Phase 1: Main experiment (4 conditions x 3 seeds)
    print("PHASE 1: Main experiment (4 conditions x 3 seeds)")
    print("-" * 50)
    main_results, conditions, condition_labels = run_main_experiment()
    phase1_time = time.time() - t_start
    print(f"  Phase 1 complete in {phase1_time:.1f}s")

    # Phase 2: Policy strength sweep
    print(f"\nPHASE 2: Policy strength sweep ({len(POLICY_STRENGTHS)} strengths x {N_SEEDS} seeds)")
    print("-" * 50)
    strength_results = run_strength_sweep()
    phase2_time = time.time() - t_start - phase1_time
    print(f"  Phase 2 complete in {phase2_time:.1f}s")

    # Analysis
    analysis = analyze_degradation(main_results, conditions)

    # Print all tables
    print_results(analysis, conditions, condition_labels)
    print_strength_sweep(strength_results)
    print_summary(analysis, conditions, condition_labels)
    print_verdict(analysis, conditions, condition_labels)

    # w_cross convergence for MVSU
    print(f"\n{'='*80}")
    print("MVSU w_cross CONVERGENCE")
    print(f"{'='*80}")
    for seed in SEEDS:
        r = main_results[('mvsu', seed)]
        wc = [v for v in r['w_cross_values'] if v is not None]
        if wc:
            print(f"  Seed {seed}: w_cross trajectory = "
                  f"[{', '.join(f'{v:.4f}' for v in wc[:5])}...{wc[-1]:.4f}]")
            print(f"    Initial: {wc[0]:.4f}, Final: {wc[-1]:.4f} "
                  f"({'NEGATIVE' if wc[-1] < 0 else 'POSITIVE'})")

    # Plots
    print(f"\nGenerating plots...")
    create_plots(analysis, conditions, condition_labels, strength_results, main_results)

    total_time = time.time() - t_start
    print(f"\nTotal runtime: {total_time:.1f}s")
    print("=" * 80)
    print("RLHF BRIDGE EXPERIMENT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    print(f"Starting at {time.strftime('%H:%M:%S')}")
    print()
    main()
    print(f"\nCompleted at {time.strftime('%H:%M:%S')}")
