# GOLDEN CUBE NET (GCN): A Phi-Optimal ML Architecture

**Team:** Weekend Builders Collective
**Date:** 2026-02-17
**Status:** Design doc / ready to prototype
**Vibe:** Let's build this thing

---

## The Pitch (30 seconds)

We read all the theory. We read the experiments. Here's what we think the universe is telling us:

**Every self-referential information system hits an optimal redundancy fraction of ~38.2%.** Not 50%. Not 25%. Specifically 1/phi^2. The CNN stride experiments confirmed it. Dropout confirmed it. Attention head mixing confirmed it. The MVSU dual-channel architecture confirmed that inhibitory cross-correction kills self-contamination.

So we asked: what if we built a neural network that bakes ALL of this in from the start?

We're calling it **GCN -- Golden Cube Net**. Eight processing channels arranged on a cube graph, with phi-optimal everything. Here's the blueprint.

---

## The Architecture

### High-Level View

```
                    INPUT
                      |
                [Patch Embed + Pos]
                      |
            +---------+---------+
            |   CUBE BLOCK x N  |
            |                   |
            |  8 channels on    |
            |  cube vertices    |
            |  3 neighbors each |
            |  38% overlap      |
            |  inhibitory cross |
            +---------+---------+
                      |
                [Golden Pool]
                      |
                   OUTPUT
```

### The Cube Block (the core innovation)

Each Cube Block has 8 parallel processing channels. They're wired like the vertices of a cube -- each channel talks to exactly 3 neighbors. This is the sparse topology from the theory.

```
        Channel 5 --------- Channel 6
        /|                   /|
       / |                  / |
      /  |                 /  |
  Ch 7 --------- Ch 8    /   |
     |   |            |  /    |
     |   Ch 1 --------|--Ch 2
     |  /             | /
     | /              |/
  Ch 3 --------- Ch 4

  Each vertex = 1 processing channel
  Each edge = inhibitory cross-connection (w_cross < 0)
  Each channel sees 3 neighbors (3-regular graph)
```

### What Each Channel Does

```
For channel i (i = 1..8):

  1. LOCAL PROCESSING
     z_i = FFN_i(x)                    # Each channel has its OWN FFN
                                        # (architectural diversity!)

  2. SELF-ATTENTION (within channel)
     a_i = Attention(z_i)              # Standard self-attention

  3. CUBE MESSAGE PASSING (3 rounds, matching graph diameter)
     for round in [1, 2, 3]:
       z_i = (1 - alpha) * z_i + (alpha/3) * sum(w_cross_ij * z_j
                                                  for j in neighbors(i))
     where alpha = 0.382 (FIXED, not learned -- the experiments say this ties learnable)
     and w_cross_ij is LEARNED and initialized at -0.1

  4. CHANNEL OUTPUT
     out_i = LayerNorm(a_i + z_i)      # Residual + norm
```

### Why 8 Channels with 3 Neighbors?

The theory proves:
- 8 observers on cube vertices reconstruct a sphere optimally for their count
- Each observer's cap overlaps ~38% with each neighbor's cap
- 3 rounds of message passing = graph diameter = full information flow
- Sparse (3-regular) topology preserves channel specialization

In ML terms: 8 channels is enough diversity to decontaminate, 3 neighbors is enough communication to coordinate, and the cube topology prevents the "groupthink collapse" that all-to-all connectivity causes at scale.

---

## The Full Architecture (for image classification)

We're targeting CIFAR-10/100 first because the experiments already validated there.

### Hyperparameters (all phi-derived)

| Parameter | Value | Why |
|-----------|-------|-----|
| Channels per Cube Block | 8 | Cube vertices |
| Neighbors per channel | 3 | Cube edges (3-regular) |
| Message passing rounds | 3 | Graph diameter |
| Mixing alpha | 0.382 (fixed) | 1/phi^2, validated in Experiment 3 |
| Dropout rate | 0.382 | 1/phi^2, validated in Experiment 2 |
| Stride/kernel ratio | 0.618 | 1/phi, so overlap = 0.382 (Experiment 1) |
| Hidden dim multiplier | 1.618x | phi * base_dim (overparameterization ratio) |
| Cross-weight init | -0.1 | Negative hint for inhibitory learning |
| Base embedding dim | 64 | Practical choice, 8 channels x 8 per channel |
| Patch size | 4x4 | For 32x32 images -> 64 patches |
| Cube Blocks (depth) | 4 | Keeps it trainable on a single GPU |

### Layer-by-Layer Spec

```
INPUT: [B, 3, 32, 32]  (CIFAR images)

1. PATCH EMBEDDING
   Conv2d(3, 64, kernel_size=5, stride=3)     # overlap = 1 - 3/5 = 0.40 ~ 0.382
   + Learnable position embeddings              # [B, 64, 10, 10] -> flatten -> [B, 100, 64]

2. CUBE BLOCK x 4
   Each block:
     a. Split dim 64 into 8 channels of 8       # Each channel gets 8 dims
     b. Per-channel FFN:
        Linear(8, 13) -> GELU -> Linear(13, 8)  # 13 = ceil(8 * 1.618), the phi-expansion
     c. Per-channel self-attention:
        1 head, dim=8, within each channel's tokens
     d. Cube message passing (3 rounds):
        alpha=0.382, w_cross initialized at -0.1
        24 learnable cross-weights (12 edges x 2 directions)
     e. Residual + LayerNorm + Dropout(0.382)

3. GOLDEN POOLING
   Weighted average across all 8 channels
   Channel weights initialized to 1/8 but learnable
   Followed by global average over spatial tokens
   -> [B, 64]

4. CLASSIFIER HEAD
   Linear(64, 104) -> GELU -> Dropout(0.382) -> Linear(104, num_classes)
   # 104 = ceil(64 * 1.618)
```

### Total Parameter Count (approximate)

```
Patch embed:      3 * 64 * 5 * 5 + 64           =   4,864
Position embed:   100 * 64                       =   6,400
Per Cube Block:
  8 FFNs:         8 * (8*13 + 13 + 13*8 + 8)    =   1,832
  8 Attention:    8 * (3 * 8*8 + 8*8)            =   2,048
  Cross-weights:  24 scalars                     =      24
  LayerNorm:      2 * 64                         =     128
  Per block total:                               ~   4,032
4 Cube Blocks:                                   =  16,128
Golden Pool:      8 weights                      =       8
Classifier:       64*104 + 104 + 104*10 + 10     =   7,810
                                                 ----------
TOTAL:                                           ~  35,210
```

That's ~35K parameters. Tiny! Which is the point -- we want to see if phi-optimal wiring beats brute-force parameter scaling.

---

## The PyTorch Pseudocode

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

# The cube adjacency: vertex i -> list of 3 neighbors
CUBE_ADJ = {
    0: [1, 2, 4],  1: [0, 3, 5],
    2: [0, 3, 6],  3: [1, 2, 7],
    4: [0, 5, 6],  5: [1, 4, 7],
    6: [2, 4, 7],  7: [3, 5, 6],
}
PHI = (1 + 5**0.5) / 2
ALPHA = 1.0 / PHI**2  # 0.382

class CubeBlock(nn.Module):
    def __init__(self, dim=64, n_channels=8):
        super().__init__()
        self.ch_dim = dim // n_channels  # 8
        self.n_channels = n_channels
        hidden = int(self.ch_dim * PHI)  # phi-expanded FFN

        # Per-channel FFNs (architectural diversity via independent params)
        self.ffns = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.ch_dim, hidden),
                nn.GELU(),
                nn.Linear(hidden, self.ch_dim),
            ) for _ in range(n_channels)
        ])

        # Per-channel single-head attention
        self.attn_qkv = nn.ModuleList([
            nn.Linear(self.ch_dim, 3 * self.ch_dim)
            for _ in range(n_channels)
        ])
        self.attn_out = nn.ModuleList([
            nn.Linear(self.ch_dim, self.ch_dim)
            for _ in range(n_channels)
        ])

        # Inhibitory cross-weights: 12 edges x 2 directions = 24 params
        # Initialized NEGATIVE (the key insight from MVSU)
        self.w_cross = nn.ParameterDict()
        for i, neighbors in CUBE_ADJ.items():
            for j in neighbors:
                if f"{i}_{j}" not in self.w_cross:
                    self.w_cross[f"{i}_{j}"] = nn.Parameter(
                        torch.tensor(-0.1)
                    )

        self.norm = nn.LayerNorm(dim)
        self.dropout = nn.Dropout(ALPHA)  # 0.382 dropout

    def forward(self, x):
        # x: [B, T, D]
        B, T, D = x.shape
        residual = x

        # Split into 8 channels: [B, T, 8, ch_dim]
        channels = x.view(B, T, self.n_channels, self.ch_dim)

        # 1. Per-channel FFN
        ch_out = []
        for i in range(self.n_channels):
            ch_out.append(self.ffns[i](channels[:, :, i, :]))
        channels = torch.stack(ch_out, dim=2)  # [B, T, 8, ch_dim]

        # 2. Per-channel self-attention
        attn_out = []
        for i in range(self.n_channels):
            ci = channels[:, :, i, :]  # [B, T, ch_dim]
            qkv = self.attn_qkv[i](ci).chunk(3, dim=-1)
            q, k, v = qkv
            scores = (q @ k.transpose(-2, -1)) / (self.ch_dim ** 0.5)
            attn = F.softmax(scores, dim=-1)
            attn_out.append(self.attn_out[i](attn @ v))
        channels = torch.stack(attn_out, dim=2)

        # 3. Cube message passing (3 rounds)
        for _round in range(3):
            new_channels = []
            for i in range(self.n_channels):
                own = channels[:, :, i, :]
                neighbor_sum = torch.zeros_like(own)
                for j in CUBE_ADJ[i]:
                    key = f"{i}_{j}" if f"{i}_{j}" in self.w_cross else f"{j}_{i}"
                    w = self.w_cross[key]
                    neighbor_sum = neighbor_sum + w * channels[:, :, j, :]
                mixed = (1 - ALPHA) * own + (ALPHA / 3) * neighbor_sum
                new_channels.append(mixed)
            channels = torch.stack(new_channels, dim=2)

        # 4. Reassemble and residual
        out = channels.view(B, T, D)
        return self.dropout(self.norm(out + residual))


class GoldenCubeNet(nn.Module):
    def __init__(self, img_size=32, patch_size=4, dim=64,
                 n_blocks=4, n_classes=10):
        super().__init__()
        # Patch embedding with phi-optimal stride
        stride = max(1, int(patch_size * (1/PHI)))  # ~0.618 * patch = overlap ~0.382
        self.patch_embed = nn.Conv2d(
            3, dim, kernel_size=patch_size+1, stride=stride, padding=1
        )
        n_patches = ((img_size - patch_size) // stride + 1) ** 2
        self.pos_embed = nn.Parameter(torch.randn(1, n_patches, dim) * 0.02)

        # Stack of Cube Blocks
        self.blocks = nn.ModuleList([
            CubeBlock(dim=dim) for _ in range(n_blocks)
        ])

        # Golden pooling: learnable channel weights
        self.channel_weights = nn.Parameter(torch.ones(8) / 8)

        # Classifier with phi-expansion
        head_hidden = int(dim * PHI)
        self.head = nn.Sequential(
            nn.Linear(dim, head_hidden),
            nn.GELU(),
            nn.Dropout(ALPHA),
            nn.Linear(head_hidden, n_classes),
        )

    def forward(self, x):
        # Patch embed
        x = self.patch_embed(x)                  # [B, D, H', W']
        x = x.flatten(2).transpose(1, 2)         # [B, T, D]
        x = x + self.pos_embed[:, :x.size(1), :]

        # Cube blocks
        for block in self.blocks:
            x = block(x)

        # Golden pooling: weight channels then avg over tokens
        B, T, D = x.shape
        ch = x.view(B, T, 8, D // 8)
        w = F.softmax(self.channel_weights, dim=0)
        x = (ch * w.view(1, 1, 8, 1)).sum(dim=2)  # [B, T, D//8]

        x = x.mean(dim=1)                         # [B, D//8]

        # Pad back to head input dim
        x = F.pad(x, (0, D - D // 8))             # naive; see note below
        return self.head(x)
```

**Note:** The pooling-to-head connection needs cleaning up in the real implementation. We'd either make the head expect `dim//8` or use a projection. This is pseudocode, not production.

---

## Weekend Prototype

### What We'd Build Saturday Morning

**Simplest possible test: does phi-wired cube topology beat independent channels?**

```
Experiment: CIFAR-10 classification
Compare 4 configs (same total params):
  1. Standard:     8-head attention, independent, dropout=0.5
  2. Phi-dropout:  8-head attention, independent, dropout=0.382
  3. Cube-fixed:   8-head attention, cube topology, alpha=0.382, w_cross=fixed -0.1
  4. Cube-learned: 8-head attention, cube topology, alpha=0.382, w_cross=learned (init -0.1)

Training: 30 epochs, AdamW, lr=1e-3, cosine decay
Seeds: 5
Hardware: single GPU (RTX 3090 or whatever we have)
Time: ~2 hours total
```

### What We'd Build Saturday Afternoon (if morning works)

Add the full Cube Block with per-channel FFNs and 3-round message passing. Compare against a standard ViT with matched parameter count.

### What We'd Build Sunday

The full GCN with 4 blocks. Run on CIFAR-100 (harder task). Track:
- Final test accuracy
- Learned w_cross values (are they all negative?)
- Channel specialization (do different channels attend to different things?)
- Convergence speed (does cube topology converge faster?)

---

## Why We Think This Works

### The theory gives us 5 specific, testable design choices:

1. **8 channels on cube topology** -- The sphere reconstruction proof shows 8 observers on cube vertices is the minimal configuration that achieves full L=1 coverage with near-optimal redundancy. In ML terms: 8 heads with structured sparse communication should beat 8 independent heads AND 8 fully-connected heads.

2. **Alpha = 0.382, fixed** -- Experiment 3 showed that fixing alpha at 1/phi^2 ties with learning it. Free hyperparameter. Zero tuning cost. We just hardcode it.

3. **Dropout = 0.382** -- Experiment 2 showed this beats the standard 0.5 default. Again, free improvement, zero tuning cost.

4. **Inhibitory cross-connections (w_cross < 0)** -- The MVSU work proved this is the secret sauce. Two channels without inhibition = useless (identical to one channel). Two channels WITH inhibition = 38x better R^2. We scale this to 8 channels on the cube graph.

5. **Stride = 0.618 * kernel** -- Experiment 1 showed overlap ~0.38 beats stride=1 (overlap too high) and large strides (overlap too low). We bake this into the patch embedding.

### The deeper reason:

Every self-referential system -- and a neural network with residual connections IS a self-referential system (each layer processes data that previous layers, with shared parameters in weight-tied architectures, have already shaped) -- converges to the same partition: 61.8% signal, 38.2% structure. The GCN doesn't fight this partition. It's DESIGNED for it.

The cube topology ensures each channel has exactly 3 "viewpoints" to cross-check against. The inhibitory cross-weights ensure the channels SUBTRACT each other's contamination rather than amplifying it. The 3 rounds of message passing match the graph diameter, so every channel eventually hears from every other channel, but through a structured sparse path that preserves specialization.

---

## What Could Go Wrong

We're weekend builders, not professors. Here's what scares us:

### 1. Scale Mismatch
The theory was validated on TINY models (single-layer CNNs, 2-hidden-layer MLPs, 1-layer ViTs). Our architecture is still small (~35K params). The phi-zone might be an artifact of small-scale optimization landscapes. At ResNet-50 scale (25M params), the optimal overlap/dropout/mixing could shift to completely different values. **Mitigation:** Start small, scale up carefully, watch if w_cross stays negative.

### 2. Cube Topology May Not Beat All-to-All
Experiment 3 actually showed all-to-all beating cube topology at 8 heads. The theory says sparse should win at scale, but 8 heads might not be "at scale." **Mitigation:** Test both. If all-to-all wins, use it and call it "dense golden net" instead. The alpha=0.382 and inhibitory cross-weights are the important parts, not the specific graph.

### 3. Per-Channel FFNs May Not Specialize
We're hoping 8 independent FFNs develop 8 different "viewpoints" the way 8 observers see different caps of the sphere. But with shared input and shared gradients, they might just converge to the same thing (the dual-channel-without-inhibition failure mode). **Mitigation:** The inhibitory cross-weights should force differentiation. If they don't, add a diversity loss: penalize cosine similarity between channel outputs.

### 4. Message Passing Overhead
3 rounds of message passing per block, 4 blocks = 12 rounds total. Each round touches all 8 channels. This is sequential computation that can't be parallelized across channels within a round. Could be slow. **Mitigation:** The channels are small (dim=8 each). The message passing is just scalar multiply + add. Profile it before panicking.

### 5. We Might Be Overfitting to CIFAR
All the experiments used CIFAR-10. The phi-zone might be a CIFAR-specific phenomenon. **Mitigation:** Test on MNIST (trivial), SVHN (similar), Tiny ImageNet (harder), and a text task (completely different modality). If phi-optimal settings only work on CIFAR, we learn something important.

### 6. The Whole Thing Might Just Be a Fancy ViT
If we strip away the phi-specific numbers and look at the architecture, it's basically: a ViT with structured sparse inter-head communication and negative cross-attention. That's... not nothing, but it's also not radical. The novelty is in the SPECIFIC numbers (0.382 everywhere) and the SPECIFIC topology (cube). If the numbers don't matter much and any sparse topology works, then the theory is less predictive than we hoped. **Mitigation:** Run ablations. Swap 0.382 for 0.3 and 0.5. Swap cube for ring and complete. If our specific choices don't win, be honest about it.

---

## Stretch Goals (if the weekend prototype works)

### 1. Scale to 8 Cube Blocks of 8 Channels Each
That's 64 total channels, organized as 8 "super-channels" each containing an inner cube of 8 sub-channels. Fractal cube structure. We'd call it **GCN-Fractal**. The self-similar partition (content/structure at every level) becomes literal.

### 2. Dynamic Alpha
Instead of fixed alpha=0.382, let alpha adapt per-block based on a learned "contamination estimate." Early blocks (close to input, less self-reference) might want lower alpha. Deeper blocks (more processing history, more contamination risk) might want higher alpha. The theory suggests alpha should approach 0.618 under high noise conditions.

### 3. MVSU-Style Dual Architecture
Run two COMPLETE GCNs with different initializations. Connect them with a learned negative cross-weight at the final output. The theory says this should be unnecessary (the internal cube topology already provides decontamination), but the MVSU results were so strong that it's worth testing.

### 4. Non-Vision Tasks
Apply GCN to:
- Text classification (replace patch embed with token embed)
- Time series forecasting (replace patch embed with windowed embed)
- Graph property prediction (the cube topology IS a graph; graphs on graphs!)

---

## The Name

We considered:
- **PhiNet** (taken, probably)
- **CubeFormer** (too generic)
- **OuroNet** (too pretentious)
- **GOLDEN** (Generic Optimization via Learned Dual-channel Emergent Networks -- forced acronym)

We're going with **GCN: Golden Cube Net**. It's descriptive, memorable, and if someone asks "why golden?" we get to explain the math. If it doesn't work, at least the name was cool.

---

## Summary

| Component | Standard Practice | Our Choice | Source |
|-----------|------------------|------------|--------|
| Channel count | 8 (arbitrary) | 8 (cube vertices) | Discrete observer theory |
| Inter-channel topology | None or all-to-all | Cube (3-regular) | Sphere reconstruction proof |
| Communication strength | Learned from scratch | alpha=0.382, fixed | Experiment 3 |
| Cross-channel weights | Positive or none | Initialized negative, learned | MVSU experiments |
| Message passing rounds | 1 (if any) | 3 (graph diameter) | Algorithm 6.1 |
| Dropout rate | 0.5 | 0.382 | Experiment 2 |
| Conv overlap | ~0.67 (stride 1) | ~0.38 (stride/kernel ~ 0.618) | Experiment 1 |
| FFN expansion | 4x | 1.618x (phi) | Overparameterization theory |
| Cross-weight sign | Unconstrained | Negative init (-0.1) | MVSU inhibitory proof |

**Total new ideas from theory: 9.**
**Total new parameters: 24 cross-weights per block.**
**Total cost: one weekend and a GPU.**

Let's build it.

---

*Written by the Weekend Builders Collective, 2026-02-17. We are not responsible for any golden spirals that spontaneously appear in your training loss curves.*
