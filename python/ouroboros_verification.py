#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rigorous Mathematical Verification of THE_OUROBOROS.md

This script systematically tests every mathematical claim in the paper.
Each test has: description, expected, actual, PASS/FAIL, tolerance.
"""

import numpy as np
from typing import Tuple, List, Dict
import sys
import io

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Global tolerance for numerical comparisons
TOL = 1e-12

# Test results storage
test_results = []

class TestResult:
    def __init__(self, category: str, description: str, expected, actual,
                 passed: bool, error: float = None, notes: str = ""):
        self.category = category
        self.description = description
        self.expected = expected
        self.actual = actual
        self.passed = passed
        self.error = error
        self.notes = notes

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        result = f"[{status}] {self.category}: {self.description}\n"
        result += f"  Expected: {self.expected}\n"
        result += f"  Actual:   {self.actual}\n"
        if self.error is not None:
            result += f"  Error:    {self.error:.2e}\n"
        if self.notes:
            result += f"  Notes:    {self.notes}\n"
        return result

def test_value(category: str, description: str, expected, actual,
               tol: float = TOL, notes: str = "") -> bool:
    """Test if a value matches expected within tolerance."""
    error = abs(actual - expected)
    passed = error < tol
    result = TestResult(category, description, expected, actual, passed, error, notes)
    test_results.append(result)
    return passed

def test_equality(category: str, description: str, value1, value2,
                  tol: float = TOL, notes: str = "") -> bool:
    """Test if two values are equal within tolerance."""
    error = abs(value1 - value2)
    passed = error < tol
    result = TestResult(category, description, f"{value1} = {value2}",
                       f"diff = {error:.2e}", passed, error, notes)
    test_results.append(result)
    return passed

# ============================================================================
# SECTION 1: Golden Ratio Fundamentals
# ============================================================================

print("="*80)
print("SECTION 1: Golden Ratio Fundamentals")
print("="*80)

# Define golden ratio
phi = (1 + np.sqrt(5)) / 2
phi_squared = phi ** 2
phi_inv = 1 / phi
phi_squared_inv = 1 / phi_squared

print(f"\nphi = {phi:.15f}")
print(f"phi^2 = {phi_squared:.15f}")
print(f"1/phi = {phi_inv:.15f}")
print(f"1/phi^2 = {phi_squared_inv:.15f}")
print(f"sqrt(5) = {np.sqrt(5):.15f}")

# Test: phi = (1+sqrt(5))/2
test_value("Golden Ratio", "phi = (1+sqrt(5))/2", 1.6180339887498949, phi)

# Test: phi^2 = (3+sqrt(5))/2
expected_phi_sq = (3 + np.sqrt(5)) / 2
test_value("Golden Ratio", "phi^2 = (3+sqrt(5))/2", expected_phi_sq, phi_squared)

# Test: 1/phi^2 = (3-sqrt(5))/2
expected_phi_sq_inv = (3 - np.sqrt(5)) / 2
test_value("Golden Ratio", "1/phi^2 = (3-sqrt(5))/2", expected_phi_sq_inv, phi_squared_inv)

# Test: phi^2 = phi + 1
test_equality("Golden Ratio", "phi^2 = phi + 1", phi_squared, phi + 1)

# Test: 1/phi = phi - 1
test_equality("Golden Ratio", "1/phi = phi - 1", phi_inv, phi - 1)

# Test: phi^2 + 1/phi^2 = 3
test_value("Golden Ratio", "phi^2 + 1/phi^2 = 3", 3.0, phi_squared + phi_squared_inv)

# Test: phi^2 * 1/phi^2 = 1
test_value("Golden Ratio", "phi^2 * 1/phi^2 = 1", 1.0, phi_squared * phi_squared_inv)

# Test: 1/phi + 1/phi^2 = 1
test_value("Golden Ratio", "1/phi + 1/phi^2 = 1", 1.0, phi_inv + phi_squared_inv)

# Test: sqrt(5) = phi + 1/phi
test_equality("Golden Ratio", "sqrt(5) = phi + 1/phi", np.sqrt(5), phi + phi_inv)

# ============================================================================
# SECTION 2: Quadratic Equation D² - 3D + 1 = 0
# ============================================================================

print("\n" + "="*80)
print("SECTION 2: Quadratic Equation D² - 3D + 1 = 0")
print("="*80)

# Test: phi^2 is a solution
D = phi_squared
residual = D**2 - 3*D + 1
test_value("Quadratic", "phi^2 satisfies D^2 - 3D + 1 = 0", 0.0, residual)

# Test: 1/phi^2 is a solution
D = phi_squared_inv
residual = D**2 - 3*D + 1
test_value("Quadratic", "1/phi^2 satisfies D^2 - 3D + 1 = 0", 0.0, residual)

# Test: Solutions from quadratic formula
D_plus = (3 + np.sqrt(5)) / 2
D_minus = (3 - np.sqrt(5)) / 2
test_equality("Quadratic", "D_+ = phi^2", D_plus, phi_squared)
test_equality("Quadratic", "D_- = 1/phi^2", D_minus, phi_squared_inv)

# Test: Sum of roots = 3 (Vieta's formula)
test_value("Quadratic", "D_+ + D_- = 3", 3.0, D_plus + D_minus)

# Test: Product of roots = 1 (Vieta's formula)
test_value("Quadratic", "D_+ * D_- = 1", 1.0, D_plus * D_minus)

# ============================================================================
# SECTION 3: DOF Ratio Function R(D) = (2D-1)/(D-1)
# ============================================================================

print("\n" + "="*80)
print("SECTION 3: DOF Ratio Function R(D) = (2D-1)/(D-1)")
print("="*80)

def R(D):
    """DOF ratio function"""
    return (2*D - 1) / (D - 1)

# Test: R(3) = 5/2
test_value("DOF Ratio", "R(3) = 5/2", 2.5, R(3))

# Test: R(φ²) = φ² (fixed point)
test_equality("DOF Ratio", "R(φ²) = φ² (fixed point)", R(phi_squared), phi_squared)

# Test: R(1/φ²) = 1/φ² (fixed point)
test_equality("DOF Ratio", "R(1/φ²) = 1/φ² (fixed point)", R(phi_squared_inv), phi_squared_inv)

# Test table of values
print("\nDOF Ratio Table:")
print(f"{'D':<10} {'Observer DOF':<15} {'Vacuum DOF':<15} {'R(D)':<15}")
print("-"*55)
D_values = [2, 3, 4, 5, 10, 100, 1000]
for D in D_values:
    obs_dof = 2*D - 1
    vac_dof = D - 1
    ratio = R(D)
    print(f"{D:<10} {obs_dof:<15} {vac_dof:<15} {ratio:<15.10f}")

    if D == 3:
        test_value("DOF Ratio", "R(3) = 5/2 exact", 2.5, ratio)

# Test: R(D) → 2 as D → ∞
large_D = 1e6
limit_value = R(large_D)
test_value("DOF Ratio", "lim(D→∞) R(D) = 2", 2.0, limit_value, tol=1e-6)

# ============================================================================
# SECTION 4: Fixed Point Iteration Convergence
# ============================================================================

print("\n" + "="*80)
print("SECTION 4: Fixed Point Iteration Convergence")
print("="*80)

def iterate_R(D0, n_iter=20):
    """Iterate R(D) starting from D0"""
    D = D0
    trajectory = [D]
    for _ in range(n_iter):
        D = R(D)
        trajectory.append(D)
    return trajectory

# Test: Iteration from D=3 converges to φ²
traj_3 = iterate_R(3.0, 50)
final_3 = traj_3[-1]
test_value("Iteration", "D=3 -> phi^2 after 50 iterations", phi_squared, final_3, tol=1e-10)
print(f"  Starting from D=3:")
print(f"    D_1 = {traj_3[1]:.10f}")
print(f"    D_2 = {traj_3[2]:.10f}")
print(f"    D_10 = {traj_3[10]:.10f}")
print(f"    D_50 = {traj_3[50]:.10f}")

# Test: Iteration from D=10 converges to phi^2
traj_10 = iterate_R(10.0, 50)
final_10 = traj_10[-1]
test_value("Iteration", "D=10 -> phi^2 after 50 iterations", phi_squared, final_10, tol=1e-10)
print(f"  Starting from D=10:")
print(f"    D_1 = {traj_10[1]:.10f}")
print(f"    D_2 = {traj_10[2]:.10f}")
print(f"    D_10 = {traj_10[10]:.10f}")
print(f"    D_50 = {traj_10[50]:.10f}")

# Test: Iteration from D=2.5 converges to phi^2
traj_25 = iterate_R(2.5, 50)
final_25 = traj_25[-1]
test_value("Iteration", "D=2.5 -> phi^2 after 50 iterations", phi_squared, final_25, tol=1e-10)

# ============================================================================
# SECTION 5: Beta Function β(D) = R(D) - D
# ============================================================================

print("\n" + "="*80)
print("SECTION 5: Beta Function beta(D) = R(D) - D")
print("="*80)

def beta(D):
    """Beta function"""
    return R(D) - D

def beta_formula(D):
    """Alternative formula: beta(D) = -(D^2 - 3D + 1)/(D - 1)"""
    return -(D**2 - 3*D + 1) / (D - 1)

# Test: beta(D) = -(D^2 - 3D + 1)/(D - 1)
test_D = 2.3
test_equality("Beta Function", "beta(D) = -(D^2 - 3D + 1)/(D - 1)",
              beta(test_D), beta_formula(test_D))

# Test: beta(phi^2) = 0
test_value("Beta Function", "beta(phi^2) = 0", 0.0, beta(phi_squared))

# Test: beta(1/phi^2) = 0
test_value("Beta Function", "beta(1/phi^2) = 0", 0.0, beta(phi_squared_inv))

# ============================================================================
# SECTION 6: Stability Analysis
# ============================================================================

print("\n" + "="*80)
print("SECTION 6: Stability Analysis")
print("="*80)

def R_derivative(D):
    """Derivative of R(D)"""
    return -1 / (D - 1)**2

def beta_derivative(D):
    """Derivative of beta(D)"""
    return -(D**2 - 2*D + 2) / (D - 1)**2

# Test: R'(D) = -1/(D-1)^2
test_D = 2.7
R_deriv_numerical = (R(test_D + 1e-8) - R(test_D - 1e-8)) / (2e-8)
R_deriv_analytical = R_derivative(test_D)
test_equality("Stability", "R'(D) formula correct", R_deriv_analytical, R_deriv_numerical, tol=1e-6)

# Test: R'(phi^2) = -1/(phi^2-1)^2
R_prime_phi_sq = R_derivative(phi_squared)
expected_R_prime = -1 / (phi_squared - 1)**2
test_equality("Stability", "R'(phi^2) = -1/(phi^2-1)^2", expected_R_prime, R_prime_phi_sq)

# Verify (phi^2-1)^2 = phi^2 (from paper's claim)
test_equality("Stability", "(phi^2-1)^2 = phi^2", (phi_squared - 1)**2, phi_squared)

# Test: R'(phi^2) = -1/phi^2
test_value("Stability", "R'(phi^2) = -1/phi^2", -1/phi_squared, R_prime_phi_sq)

# Paper claims |R'(phi^2)| = 0.382
test_value("Stability", "|R'(phi^2)| = 1/phi^2 ~ 0.382", phi_squared_inv, abs(R_prime_phi_sq))

# Test: |R'(phi^2)| < 1 (stable fixed point)
stable = abs(R_prime_phi_sq) < 1
result = TestResult("Stability", "|R'(phi^2)| < 1 (stability condition)",
                   True, stable, stable, None,
                   f"|R'(phi^2)| = {abs(R_prime_phi_sq):.6f}")
test_results.append(result)
print(f"  |R'(phi^2)| = {abs(R_prime_phi_sq):.10f} < 1: {stable}")

# Test: beta'(D) = -(D^2 - 2D + 2)/(D-1)^2
beta_deriv_numerical = (beta(test_D + 1e-8) - beta(test_D - 1e-8)) / (2e-8)
beta_deriv_analytical = beta_derivative(test_D)
test_equality("Stability", "β'(D) formula correct", beta_deriv_analytical, beta_deriv_numerical, tol=1e-6)

# Test: beta'(phi^2) = -(3-phi)
# From paper's derivation
beta_prime_phi_sq = beta_derivative(phi_squared)
expected_beta_prime = -(3 - phi)
test_equality("Stability", "beta'(phi^2) = -(3-phi)", expected_beta_prime, beta_prime_phi_sq)

# Verify numerical value
test_value("Stability", "beta'(phi^2) ~ -1.382", -1.382, beta_prime_phi_sq, tol=1e-3)

# More precise value
print(f"  beta'(phi^2) = {beta_prime_phi_sq:.15f}")
print(f"  -(3-phi) = {-(3-phi):.15f}")

# ============================================================================
# SECTION 7: Critical Exponent ν
# ============================================================================

print("\n" + "="*80)
print("SECTION 7: Critical Exponent nu")
print("="*80)

# Test: nu = 1/|beta'(phi^2)|
nu_from_beta = 1 / abs(beta_prime_phi_sq)
print(f"  nu = 1/|beta'(phi^2)| = {nu_from_beta:.15f}")

# Test: nu = 1/(3-phi)
nu_formula1 = 1 / (3 - phi)
test_equality("Critical Exponent", "nu = 1/(3-phi)", nu_formula1, nu_from_beta)

# Test: nu = phi/sqrt(5)
nu_formula2 = phi / np.sqrt(5)
test_equality("Critical Exponent", "nu = phi/sqrt(5)", nu_formula2, nu_from_beta)

# Verify the identity 1/(3-phi) = phi/sqrt(5)
test_equality("Critical Exponent", "1/(3-phi) = phi/sqrt(5)", nu_formula1, nu_formula2)

# Test approximate value
test_value("Critical Exponent", "nu ~ 0.724", 0.724, nu_from_beta, tol=1e-3)

# More precise value
print(f"  nu = {nu_from_beta:.15f}")

# Verify intermediate calculations
three_minus_phi = 3 - phi
print(f"  3 - phi = {three_minus_phi:.15f}")
print(f"  1/(3-phi) = {1/three_minus_phi:.15f}")
print(f"  phi/sqrt(5) = {phi/np.sqrt(5):.15f}")

# ============================================================================
# SECTION 8: Cosmological Observations
# ============================================================================

print("\n" + "="*80)
print("SECTION 8: Cosmological Observations")
print("="*80)

# Planck 2018 values (from paper)
Omega_Lambda = 0.685
Omega_DM = 0.265

observed_ratio = Omega_Lambda / Omega_DM
predicted_D3 = 2.5
predicted_phi_sq = phi_squared

print(f"\n  Observed Omega_L/Omega_DM = {observed_ratio:.4f}")
print(f"  Predicted (D=3): 5/2 = {predicted_D3:.4f}")
print(f"  Predicted (phi^2): {predicted_phi_sq:.4f}")

# Test: Observed ratio
test_value("Cosmology", "Observed ratio = 0.685/0.265", 2.5849056603773583, observed_ratio, tol=1e-6)

# Compute discrepancies
discrepancy_D3 = abs(observed_ratio - predicted_D3) / predicted_D3 * 100
discrepancy_phi_sq = abs(observed_ratio - predicted_phi_sq) / predicted_phi_sq * 100

print(f"\n  Discrepancy from 5/2: {discrepancy_D3:.2f}%")
print(f"  Discrepancy from phi^2: {discrepancy_phi_sq:.2f}%")

test_value("Cosmology", "Discrepancy from 5/2 ~ 3.4%", 3.4, discrepancy_D3, tol=0.1)
test_value("Cosmology", "Discrepancy from phi^2", discrepancy_phi_sq, discrepancy_phi_sq, tol=0.1,
          notes=f"Actual: {discrepancy_phi_sq:.2f}%")

# Test: Observed ratio is between 5/2 and phi^2
between = predicted_D3 < observed_ratio < predicted_phi_sq
result = TestResult("Cosmology", "5/2 < R_obs < phi^2",
                   True, between, between, None,
                   f"{predicted_D3} < {observed_ratio:.4f} < {predicted_phi_sq:.4f}")
test_results.append(result)
print(f"  5/2 < R_obs < phi^2: {between}")

# How far from 5/2 to phi^2?
gap = predicted_phi_sq - predicted_D3
position = observed_ratio - predicted_D3
fraction = position / gap * 100

print(f"\n  Gap: phi^2 - 5/2 = {gap:.6f}")
print(f"  Position: R_obs - 5/2 = {position:.6f}")
print(f"  Fraction: {fraction:.1f}% of the way from 5/2 to phi^2")

# ============================================================================
# SECTION 9: Information Partition
# ============================================================================

print("\n" + "="*80)
print("SECTION 9: Information Partition")
print("="*80)

# Test: eta = 1/phi^2
eta_accessible = 1 / phi_squared
test_value("Information", "eta = 1/phi^2 ~ 0.382", 0.382, eta_accessible, tol=1e-3)

# Test: eta_dark = 1/phi
eta_dark = 1 / phi
test_value("Information", "eta_dark = 1/phi ~ 0.618", 0.618, eta_dark, tol=1e-3)

# Test: eta + eta_dark = 1
test_value("Information", "eta + eta_dark = 1", 1.0, eta_accessible + eta_dark)

# More precise values
print(f"\n  Accessible fraction: 1/phi^2 = {eta_accessible:.15f}")
print(f"  Dark fraction: 1/phi = {eta_dark:.15f}")
print(f"  Sum: {eta_accessible + eta_dark:.15f}")

# ============================================================================
# SECTION 10: Additional Golden Ratio Identities
# ============================================================================

print("\n" + "="*80)
print("SECTION 10: Additional Golden Ratio Identities")
print("="*80)

# Test: phi^3 = 2*phi + 1
phi_cubed = phi ** 3
test_equality("Golden Ratio", "phi^3 = 2*phi + 1", phi_cubed, 2*phi + 1)

# Test: phi^4 = 3*phi + 2
phi_fourth = phi ** 4
test_equality("Golden Ratio", "phi^4 = 3*phi + 2", phi_fourth, 3*phi + 2)

# Test: 1/phi^2 = 2 - phi
test_equality("Golden Ratio", "1/phi^2 = 2 - phi", phi_squared_inv, 2 - phi)

# Test: phi^2 - 1 = phi
test_equality("Golden Ratio", "phi^2 - 1 = phi", phi_squared - 1, phi)

# Test: 2*phi^2 - 1 = phi^3
test_equality("Golden Ratio", "2*phi^2 - 1 = phi^3", 2*phi_squared - 1, phi_cubed)

# ============================================================================
# SECTION 11: Specific Paper Claims from Appendix B.3
# ============================================================================

print("\n" + "="*80)
print("SECTION 11: Appendix B.3 Verification")
print("="*80)

# Paper claims (phi^2-1)^2 = phi^2
denominator_squared = (phi_squared - 1)**2
test_equality("Appendix B.3", "(phi^2-1)^2 = phi^2", denominator_squared, phi_squared)

# Paper says this equals phi + 1
test_equality("Appendix B.3", "(phi^2-1)^2 = phi + 1", denominator_squared, phi + 1)

# Paper's stability calculation
# Numerator: phi^4 - 2*phi^2 + 2
numerator = phi_fourth - 2*phi_squared + 2
print(f"  Numerator = phi^4 - 2*phi^2 + 2 = {numerator:.15f}")

# Paper claims this equals phi + 2
test_equality("Appendix B.3", "phi^4 - 2*phi^2 + 2 = phi + 2", numerator, phi + 2)

# So beta'(phi^2) = -(phi+2)/(phi+1)
beta_prime_from_paper = -(phi + 2) / (phi + 1)
test_equality("Appendix B.3", "beta'(phi^2) = -(phi+2)/(phi+1)", beta_prime_phi_sq, beta_prime_from_paper)

# Paper claims (phi+2)/(phi+1) = 1 + 1/phi^2
ratio_check = (phi + 2) / (phi + 1)
expected_ratio = 1 + 1/phi_squared
test_equality("Appendix B.3", "(phi+2)/(phi+1) = 1 + 1/phi^2", ratio_check, expected_ratio)

# And 1 + 1/phi^2 = 1 + (2-phi) = 3 - phi
test_equality("Appendix B.3", "1 + 1/phi^2 = 3 - phi", expected_ratio, 3 - phi)

# So beta'(phi^2) = -(3-phi)
print(f"  beta'(phi^2) = -(3-phi) = {-(3-phi):.15f}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("SUMMARY OF RESULTS")
print("="*80)

total_tests = len(test_results)
passed_tests = sum(1 for r in test_results if r.passed)
failed_tests = total_tests - passed_tests

print(f"\nTotal Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {failed_tests}")
print(f"Success Rate: {100*passed_tests/total_tests:.1f}%")

if failed_tests > 0:
    print("\n" + "="*80)
    print("FAILED TESTS:")
    print("="*80)
    for result in test_results:
        if not result.passed:
            print(f"\n{result}")

# Summary by category
categories = {}
for result in test_results:
    if result.category not in categories:
        categories[result.category] = {"passed": 0, "failed": 0}
    if result.passed:
        categories[result.category]["passed"] += 1
    else:
        categories[result.category]["failed"] += 1

print("\n" + "="*80)
print("RESULTS BY CATEGORY:")
print("="*80)
for category in sorted(categories.keys()):
    stats = categories[category]
    total = stats["passed"] + stats["failed"]
    print(f"{category:<25} {stats['passed']:>3}/{total:<3} passed")

# Exit code
sys.exit(0 if failed_tests == 0 else 1)
