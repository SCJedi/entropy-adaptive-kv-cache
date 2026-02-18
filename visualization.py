"""
Visualization tools for vacuum state physics.

Creates plots demonstrating:
- Divergence of mode vacuum energy with cutoff
- Coherent state wavefunctions and uncertainty
- Comparison between |0⟩ and |Ω⟩ approaches
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from typing import Optional, Tuple

from constants import (
    HBAR, C, PLANCK_LENGTH, OBSERVED_DARK_ENERGY_DENSITY,
    NEUTRINO, ELECTRON
)
from vacuum_energy import ModeVacuumCalculator, CellVacuumCalculator
from coherent_states import CoherentState, CellVacuumState


def plot_divergence(save_path: Optional[str] = None):
    """
    Plot how mode vacuum energy density diverges with cutoff.

    Shows ρ ∝ k_max⁴ quartic divergence.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    calc = ModeVacuumCalculator()

    # k values from atomic to Planck scale
    k_values = np.logspace(10, 35, 100)  # m⁻¹
    rho_values = [calc.energy_density_with_cutoff(k) for k in k_values]

    # Left plot: log-log
    ax1.loglog(k_values, rho_values, 'b-', linewidth=2, label='Mode vacuum ρ(k_max)')
    ax1.axhline(OBSERVED_DARK_ENERGY_DENSITY, color='g', linestyle='--',
                linewidth=2, label=f'Observed ρ_Λ = {OBSERVED_DARK_ENERGY_DENSITY:.0e} J/m³')

    # Mark specific scales
    scales = {
        'Atomic': 1e10,
        'Nuclear': 1e15,
        'Electroweak': 5e15,
        'Planck': 1/PLANCK_LENGTH
    }
    for name, k in scales.items():
        rho = calc.energy_density_with_cutoff(k)
        ax1.scatter([k], [rho], s=100, zorder=5)
        ax1.annotate(name, (k, rho), textcoords="offset points",
                    xytext=(10, 10), fontsize=9)

    ax1.set_xlabel('Cutoff wavenumber k_max (m⁻¹)', fontsize=12)
    ax1.set_ylabel('Energy density ρ (J/m³)', fontsize=12)
    ax1.set_title('Mode Vacuum: Quartic Divergence ρ ∝ k⁴', fontsize=14)
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)

    # Right plot: ratio to observed
    ratio_values = np.array(rho_values) / OBSERVED_DARK_ENERGY_DENSITY
    ax2.loglog(k_values, ratio_values, 'r-', linewidth=2)
    ax2.axhline(1, color='g', linestyle='--', linewidth=2, label='Observed = 1')

    ax2.set_xlabel('Cutoff wavenumber k_max (m⁻¹)', fontsize=12)
    ax2.set_ylabel('ρ_mode / ρ_observed', fontsize=12)
    ax2.set_title('The "10¹²³ Problem": Ratio to Observation', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Annotate the Planck scale discrepancy
    k_planck = 1/PLANCK_LENGTH
    ratio_planck = calc.energy_density_planck_cutoff() / OBSERVED_DARK_ENERGY_DENSITY
    ax2.annotate(f'Planck: 10^{np.log10(ratio_planck):.0f}',
                (k_planck, ratio_planck), textcoords="offset points",
                xytext=(-60, -20), fontsize=11,
                arrowprops=dict(arrowstyle='->', color='red'))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {save_path}")
    else:
        plt.show()

    return fig


def plot_coherent_state_wavefunction(alpha: complex = np.sqrt(0.5),
                                      save_path: Optional[str] = None):
    """
    Plot the wavefunction of a coherent state.

    Shows the Gaussian envelope with minimum uncertainty.
    """
    # Use electron mass for concrete numbers
    omega = ELECTRON.mass_kg * C**2 / HBAR
    state = CoherentState(alpha=alpha, omega=omega, mass=ELECTRON.mass_kg)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Position space wavefunction
    x = np.linspace(-5*state.delta_x, 5*state.delta_x, 500)
    psi = state.wavefunction(x)

    ax = axes[0, 0]
    ax.plot(x/state.delta_x, np.abs(psi)**2 / np.max(np.abs(psi)**2),
            'b-', linewidth=2)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
    ax.fill_between(x/state.delta_x, np.abs(psi)**2 / np.max(np.abs(psi)**2),
                   alpha=0.3)
    ax.set_xlabel('x / Δx', fontsize=12)
    ax.set_ylabel('|ψ(x)|² (normalized)', fontsize=12)
    ax.set_title(f'Position Space: |α|² = {state.alpha_squared:.1f}', fontsize=14)

    # Number state distribution
    ax = axes[0, 1]
    n_max = 10
    n_values = range(n_max)
    probs = [state.number_state_probability(n) for n in n_values]
    ax.bar(n_values, probs, color='steelblue', edgecolor='navy')
    ax.set_xlabel('Number of quanta n', fontsize=12)
    ax.set_ylabel('P(n) = |⟨n|α⟩|²', fontsize=12)
    ax.set_title('Poissonian Number Distribution', fontsize=14)
    ax.set_xticks(n_values)

    # Phase space uncertainty ellipse
    ax = axes[1, 0]
    theta = np.linspace(0, 2*np.pi, 100)
    x_ellipse = state.delta_x * np.cos(theta)
    p_ellipse = state.delta_p * np.sin(theta)

    ax.plot(x_ellipse/state.delta_x, p_ellipse/state.delta_p, 'b-', linewidth=2)
    ax.fill(x_ellipse/state.delta_x, p_ellipse/state.delta_p, alpha=0.3)
    ax.scatter([0], [0], color='red', s=100, zorder=5, label='⟨x⟩, ⟨p⟩')
    ax.set_xlabel('Δx units', fontsize=12)
    ax.set_ylabel('Δp units', fontsize=12)
    ax.set_title('Phase Space: Minimum Uncertainty Circle', fontsize=14)
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Uncertainty comparison table
    ax = axes[1, 1]
    ax.axis('off')

    table_data = [
        ['State Type', 'Δx', 'Δp', 'Δx·Δp'],
        ['Position eigenstate', '0', '∞', 'undefined'],
        ['Coherent |α⟩', f'{state.delta_x:.2e}', f'{state.delta_p:.2e}', 'ℏ/2 ✓'],
        ['Momentum eigenstate', '∞', '0', 'undefined'],
        ['Mode vacuum |0⟩', '∞ (delocalized)', 'Definite', 'N/A'],
    ]

    table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                    colWidths=[0.3, 0.25, 0.25, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    # Color header
    for j in range(4):
        table[(0, j)].set_facecolor('#4472C4')
        table[(0, j)].set_text_props(color='white', fontweight='bold')

    ax.set_title('Uncertainty Relations Comparison', fontsize=14, pad=20)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {save_path}")
    else:
        plt.show()

    return fig


def plot_vacuum_comparison(save_path: Optional[str] = None):
    """
    Visual comparison of mode vacuum vs cell vacuum.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Mode vacuum (delocalized modes)
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(-2, 2)

    x = np.linspace(0, 10, 1000)
    for i, k in enumerate([0.5, 1, 2, 3]):
        y = 0.5 * np.sin(k * np.pi * x) * (0.8 ** i)
        ax.plot(x, y, alpha=0.7, linewidth=1.5)

    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_xlabel('Position x', fontsize=12)
    ax.set_ylabel('Mode amplitude', fontsize=12)
    ax.set_title('Mode Vacuum |0⟩: Each mode spans ALL space\n'
                'Δk = definite, Δx = ∞', fontsize=12)
    ax.text(5, 1.7, 'Modes: eⁱᵏˣ extend everywhere', ha='center', fontsize=11,
           style='italic')

    # Right: Cell vacuum (localized cells)
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 1.5)

    cell_width = 1.0
    for i in range(10):
        # Draw cell boundary
        ax.axvline(i, color='gray', linestyle='--', alpha=0.5)

        # Draw Gaussian in each cell
        x_cell = np.linspace(i, i+1, 100)
        center = i + 0.5
        gaussian = np.exp(-20*(x_cell - center)**2)
        ax.fill_between(x_cell, gaussian, alpha=0.6)
        ax.plot(x_cell, gaussian, 'b-', linewidth=1)

    ax.axvline(10, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_xlabel('Position x', fontsize=12)
    ax.set_ylabel('Cell amplitude', fontsize=12)
    ax.set_title('Cell Vacuum |Ω⟩: Product of localized states\n'
                'Δx = λ_C (finite), independent cells', fontsize=12)
    ax.text(5, 1.3, '|Ω⟩ = |α₁⟩ ⊗ |α₂⟩ ⊗ |α₃⟩ ⊗ ...', ha='center', fontsize=11,
           style='italic')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {save_path}")
    else:
        plt.show()

    return fig


def plot_energy_density_scales(save_path: Optional[str] = None):
    """
    Compare energy densities across different approaches and mass scales.
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Energy densities to plot (J/m³)
    data = {
        'Observed ρ_Λ': OBSERVED_DARK_ENERGY_DENSITY,
        'Cell (neutrino)': CellVacuumCalculator(NEUTRINO.mass_kg).energy_density,
        'Cell (electron)': CellVacuumCalculator(ELECTRON.mass_kg).energy_density,
        'Mode (Electroweak)': ModeVacuumCalculator().energy_density_with_cutoff(5e15),
        'Mode (GUT)': ModeVacuumCalculator().energy_density_with_cutoff(5e31),
        'Mode (Planck)': ModeVacuumCalculator().energy_density_planck_cutoff(),
    }

    # Convert to log scale for visualization
    names = list(data.keys())
    values = list(data.values())
    log_values = [np.log10(v) for v in values]

    colors = ['green', 'limegreen', 'gold', 'orange', 'red', 'darkred']

    bars = ax.barh(names, log_values, color=colors, edgecolor='black')

    # Add value labels
    for bar, val in zip(bars, values):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
               f'{val:.1e}', va='center', fontsize=10)

    ax.set_xlabel('log₁₀(ρ) where ρ in J/m³', fontsize=12)
    ax.set_title('Vacuum Energy Density: Different Approaches', fontsize=14)
    ax.axvline(np.log10(OBSERVED_DARK_ENERGY_DENSITY), color='green',
              linestyle='--', linewidth=2, alpha=0.7)

    # Add annotation
    ax.annotate('Cell vacuum with neutrino mass\nmatches observation!',
               xy=(np.log10(data['Cell (neutrino)']), 1),
               xytext=(20, 3),
               fontsize=11,
               arrowprops=dict(arrowstyle='->', color='green'),
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

    ax.annotate('Mode vacuum at Planck scale:\n"10¹²³ problem"',
               xy=(np.log10(data['Mode (Planck)']), 5),
               xytext=(60, 4),
               fontsize=11,
               arrowprops=dict(arrowstyle='->', color='red'),
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {save_path}")
    else:
        plt.show()

    return fig


def create_all_figures(output_dir: str = "."):
    """Generate all visualization figures."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    print("Generating figures...")

    plot_divergence(f"{output_dir}/mode_vacuum_divergence.png")
    plot_coherent_state_wavefunction(save_path=f"{output_dir}/coherent_state.png")
    plot_vacuum_comparison(f"{output_dir}/vacuum_comparison.png")
    plot_energy_density_scales(f"{output_dir}/energy_density_scales.png")

    print(f"\nAll figures saved to {output_dir}/")


if __name__ == "__main__":
    # Show all plots interactively
    plt.ion()

    print("1. Mode vacuum divergence...")
    plot_divergence()

    print("2. Coherent state properties...")
    plot_coherent_state_wavefunction()

    print("3. Vacuum state comparison...")
    plot_vacuum_comparison()

    print("4. Energy density scales...")
    plot_energy_density_scales()

    plt.ioff()
    plt.show()
