"""Analyze phi initialization experiment results."""

import json
import numpy as np
from pathlib import Path

# Load results
results_path = Path(__file__).parent / 'phi_init_results.json'
with open(results_path, 'r') as f:
    data = json.load(f)

print("="*80)
print("PHI INITIALIZATION EXPERIMENT RESULTS")
print("="*80)
print(f"\nDataset: {data['dataset']}")
print(f"Epochs: {data['num_epochs']}")
print(f"Seeds: {data['num_seeds']}")
print(f"Phi: {data['phi']:.6f}")
print(f"1/Phi: {data['inv_phi']:.6f}")

print("\n" + "="*80)
print("SUMMARY TABLE")
print("="*80)

# Collect statistics for each initialization
stats = {}
for scale_name, results in data['results'].items():
    final_accs = [r['final_test_acc'] for r in results]
    conv_epochs = [r['convergence_epoch'] for r in results]
    init_grads = [r['init_grad_stats'] for r in results]

    # Compute initial gradient stats
    init_grad_means = [g['mean'] for g in init_grads]
    init_grad_stds = [g['std'] for g in init_grads]

    stats[scale_name] = {
        'mean_acc': np.mean(final_accs),
        'std_acc': np.std(final_accs),
        'mean_conv': np.mean(conv_epochs),
        'std_conv': np.std(conv_epochs),
        'init_grad_mean': np.mean(init_grad_means),
        'init_grad_std': np.mean(init_grad_stds)
    }

# Sort by mean accuracy
sorted_stats = sorted(stats.items(), key=lambda x: x[1]['mean_acc'], reverse=True)

print(f"\n{'Method':<12} {'Test Acc (%)':<18} {'Conv (epochs)':<18} {'Init Grad Mean':<15} {'Init Grad Std':<15}")
print("-" * 90)

for scale_name, s in sorted_stats:
    print(f"{scale_name:<12} {s['mean_acc']:5.2f} ± {s['std_acc']:4.2f}  "
          f"       {s['mean_conv']:4.1f} ± {s['std_conv']:3.1f}  "
          f"        {s['init_grad_mean']:8.5f}      {s['init_grad_std']:8.5f}")

print("\n" + "="*80)
print("RANKING BY FINAL ACCURACY")
print("="*80)

for rank, (scale_name, s) in enumerate(sorted_stats, 1):
    print(f"{rank}. {scale_name:<12} {s['mean_acc']:.2f}% ± {s['std_acc']:.2f}%")

print("\n" + "="*80)
print("ANALYSIS")
print("="*80)

# Group methods
phi_methods = ['phi', 'phi_v2', 'phi_v3']
standard_methods = ['xavier', 'he', 'lecun']
control_methods = ['small', 'large']

phi_accs = [stats[m]['mean_acc'] for m in phi_methods]
standard_accs = [stats[m]['mean_acc'] for m in standard_methods]
control_accs = [stats[m]['mean_acc'] for m in control_methods]

print(f"\nPhi-based methods (phi=0.618, sqrt(1/phi²)=0.618, phi=1.618):")
print(f"  Mean accuracy: {np.mean(phi_accs):.2f}%")
print(f"  Range: {np.min(phi_accs):.2f}% - {np.max(phi_accs):.2f}%")

print(f"\nStandard methods (Xavier, He, LeCun):")
print(f"  Mean accuracy: {np.mean(standard_accs):.2f}%")
print(f"  Range: {np.min(standard_accs):.2f}% - {np.max(standard_accs):.2f}%")

print(f"\nControl methods (small=0.3, large=2.0):")
print(f"  Mean accuracy: {np.mean(control_accs):.2f}%")
print(f"  Range: {np.min(control_accs):.2f}% - {np.max(control_accs):.2f}%")

# Find best method
best_method, best_stats = sorted_stats[0]
worst_method, worst_stats = sorted_stats[-1]

print(f"\nBest method: {best_method} ({best_stats['mean_acc']:.2f}% ± {best_stats['std_acc']:.2f}%)")
print(f"Worst method: {worst_method} ({worst_stats['mean_acc']:.2f}% ± {worst_stats['std_acc']:.2f}%)")
print(f"Difference: {best_stats['mean_acc'] - worst_stats['mean_acc']:.2f}%")

# Statistical significance check (simple)
phi_best = max(phi_accs)
standard_best = max(standard_accs)

print(f"\nBest phi-based: {phi_best:.2f}%")
print(f"Best standard: {standard_best:.2f}%")

if phi_best > standard_best:
    print(f"Phi-based methods outperform standard by: {phi_best - standard_best:.2f}%")
else:
    print(f"Standard methods outperform phi-based by: {standard_best - phi_best:.2f}%")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

# Determine verdict
diff = np.mean(phi_accs) - np.mean(standard_accs)

if diff > 0.5:
    verdict = "SUPPORTED: Phi-based initialization outperforms standard methods."
elif diff < -0.5:
    verdict = "REFUTED: Phi-based initialization underperforms standard methods."
else:
    verdict = "INCONCLUSIVE: Phi-based initialization performs comparably to standard methods."

print(f"\n{verdict}")
print(f"Mean difference: {diff:.2f}%")

# Specific findings
print("\nSpecific findings:")
for method in phi_methods:
    rank = [i for i, (name, _) in enumerate(sorted_stats, 1) if name == method][0]
    print(f"  - {method}: Ranked #{rank}/8 with {stats[method]['mean_acc']:.2f}% accuracy")

print("\n" + "="*80)
