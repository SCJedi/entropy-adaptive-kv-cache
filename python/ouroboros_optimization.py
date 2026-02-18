#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification of Ouroboros Optimization Theory

Tests the DOF partition theorem, three golden partitions, fixed-point
convergence, and stability analysis from OUROBOROS_OPTIMIZATION_THEORY.md.
"""

import numpy as np
from typing import List
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
# Constants
# ============================================================================

phi = (1 + np.sqrt(5)) / 2
phi_sq = phi ** 2
phi_inv = 1 / phi
phi_sq_inv = 1 / phi_sq
sqrt5 = np.sqrt(5)

# DOF quantities at D = phi^2
D = phi_sq
observer_dof = 2 * D - 1      # 2*phi^2 - 1 = 2*phi + 1
environment_dof = D - 1        # phi^2 - 1 = phi
total_dof = observer_dof + environment_dof  # 3*D - 2 = 3*phi + 1

# Critical exponent
nu = phi / sqrt5

# ============================================================================
# SECTION 1: DOF Partition Algebra
# ============================================================================

print("=" * 80)
print("SECTION 1: DOF Partition Algebra")
print("=" * 80)

print(f"\n  D = phi^2 = {D:.15f}")
print(f"  Observer DOF  = 2D-1 = {observer_dof:.15f}")
print(f"  Environment DOF = D-1 = {environment_dof:.15f}")
print(f"  Total DOF = 3D-2 = {total_dof:.15f}")

# Test 1: Action fraction = (2phi+1)/(3phi+1) = phi/sqrt(5) = nu
action_fraction = observer_dof / total_dof
test_equality("DOF Partition", "(2phi+1)/(3phi+1) = phi/sqrt(5) = nu",
              action_fraction, nu,
              notes="Core identity: action fraction equals critical exponent")

# Verify the cross-multiplication proof
lhs = sqrt5 * (2 * phi + 1)
rhs = phi * (3 * phi + 1)
test_equality("DOF Partition", "Cross-multiply: sqrt(5)*(2phi+1) = phi*(3phi+1)",
              lhs, rhs, notes="LHS = 2*sqrt(5)+5, RHS = 5+2*sqrt(5)")

# Test 2: Perception fraction = 1 - nu
perception_fraction = environment_dof / total_dof
test_equality("DOF Partition", "Perception fraction = 1 - nu",
              perception_fraction, 1 - nu)

test_value("DOF Partition", "Action + Perception = 1", 1.0,
           action_fraction + perception_fraction)

# Test 3: Total DOF = 3*phi^2 - 2 = 3*phi + 1
test_equality("DOF Partition", "Total DOF = 3*phi^2 - 2 = 3*phi + 1",
              3 * phi_sq - 2, 3 * phi + 1,
              notes="Uses phi^2 = phi + 1")

test_value("DOF Partition", "Total DOF = 3*phi + 1", 3 * phi + 1, total_dof)

# Test 4: Action/Perception ratio = D = phi^2 (self-consistency)
action_perception_ratio = observer_dof / environment_dof
test_equality("DOF Partition", "Action/Perception = (2D-1)/(D-1) = D = phi^2",
              action_perception_ratio, phi_sq,
              notes="Self-consistency: the ratio IS the fixed point")

print(f"\n  Action fraction (nu) = {action_fraction:.15f}")
print(f"  Perception fraction  = {perception_fraction:.15f}")
print(f"  Action/Perception    = {action_perception_ratio:.15f}")
print(f"  phi^2                = {phi_sq:.15f}")

# ============================================================================
# SECTION 2: Three Partitions Are Distinct
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 2: Three Partitions Are Distinct")
print("=" * 80)

# Test 5: nu != 1/phi != 1/phi^2
diff_nu_phi_inv = abs(nu - phi_inv)
diff_nu_phi_sq_inv = abs(nu - phi_sq_inv)
diff_phi_inv_phi_sq_inv = abs(phi_inv - phi_sq_inv)

passed_distinct_1 = diff_nu_phi_inv > 0.1
result1 = TestResult("Distinct Partitions", "nu != 1/phi",
                     f"nu={nu:.6f}, 1/phi={phi_inv:.6f}",
                     f"diff = {diff_nu_phi_inv:.6f}",
                     passed_distinct_1, diff_nu_phi_inv,
                     "These are different golden-ratio quantities")
test_results.append(result1)

passed_distinct_2 = diff_nu_phi_sq_inv > 0.3
result2 = TestResult("Distinct Partitions", "nu != 1/phi^2",
                     f"nu={nu:.6f}, 1/phi^2={phi_sq_inv:.6f}",
                     f"diff = {diff_nu_phi_sq_inv:.6f}",
                     passed_distinct_2, diff_nu_phi_sq_inv)
test_results.append(result2)

passed_distinct_3 = diff_phi_inv_phi_sq_inv > 0.2
result3 = TestResult("Distinct Partitions", "1/phi != 1/phi^2",
                     f"1/phi={phi_inv:.6f}, 1/phi^2={phi_sq_inv:.6f}",
                     f"diff = {diff_phi_inv_phi_sq_inv:.6f}",
                     passed_distinct_3, diff_phi_inv_phi_sq_inv)
test_results.append(result3)

print(f"\n  nu       = phi/sqrt(5)  = {nu:.10f}")
print(f"  1/phi    = (sqrt(5)-1)/2 = {phi_inv:.10f}")
print(f"  1/phi^2  = (3-sqrt(5))/2 = {phi_sq_inv:.10f}")
print(f"  |nu - 1/phi|             = {diff_nu_phi_inv:.10f}")
print(f"  |nu - 1/phi^2|           = {diff_nu_phi_sq_inv:.10f}")
print(f"  |1/phi - 1/phi^2|        = {diff_phi_inv_phi_sq_inv:.10f}")

# ============================================================================
# SECTION 3: Fixed-Point Iteration Convergence
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 3: Fixed-Point Iteration Convergence")
print("=" * 80)

def R(D):
    """DOF ratio function R(D) = (2D-1)/(D-1)"""
    return (2 * D - 1) / (D - 1)

# Test 6: Fixed-point iteration from multiple starting points
starting_points = [3.0, 10.0, 2.5, 50.0]
n_iter = 60

for D0 in starting_points:
    D_n = D0
    for _ in range(n_iter):
        D_n = R(D_n)
    test_value("Convergence", f"R^{n_iter}({D0}) -> phi^2",
               phi_sq, D_n, tol=1e-10,
               notes=f"Starting from D0={D0}")
    print(f"  D0={D0:<6} -> D_{n_iter} = {D_n:.15f} (phi^2 = {phi_sq:.15f})")

# ============================================================================
# SECTION 4: Convergence Rate
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 4: Convergence Rate")
print("=" * 80)

def R_derivative(D):
    """R'(D) = -1/(D-1)^2"""
    return -1.0 / (D - 1) ** 2

# Test 7: |R'(phi^2)| = 1/phi^2
R_prime_at_fp = R_derivative(phi_sq)
test_value("Convergence Rate", "|R'(phi^2)| = 1/phi^2",
           phi_sq_inv, abs(R_prime_at_fp),
           notes="Contraction rate at fixed point")

# Verify numerically with finite difference
h = 1e-8
R_prime_numerical = (R(phi_sq + h) - R(phi_sq - h)) / (2 * h)
test_equality("Convergence Rate", "R'(phi^2) analytical = numerical",
              R_prime_at_fp, R_prime_numerical, tol=1e-6)

# Measure empirical convergence rate
D_n = 3.0
errors = []
for _ in range(20):
    D_n = R(D_n)
    errors.append(abs(D_n - phi_sq))

# Ratio of successive errors should approach |R'(phi^2)| = 1/phi^2
# Use mid-range iterations where errors are small but nonzero
rate_idx = None
for i in range(len(errors) - 1, 0, -1):
    if errors[i] > 1e-15 and errors[i - 1] > 1e-15:
        rate_idx = i
        break

if rate_idx is not None:
    empirical_rate = errors[rate_idx] / errors[rate_idx - 1]
    test_value("Convergence Rate", "Empirical rate -> 1/phi^2",
               phi_sq_inv, abs(empirical_rate), tol=1e-3,
               notes=f"Measured from iteration errors[{rate_idx}]/errors[{rate_idx-1}]")
    print(f"  Empirical contraction rate: {abs(empirical_rate):.10f}")
    print(f"  Theoretical (1/phi^2):      {phi_sq_inv:.10f}")

# ============================================================================
# SECTION 5: Stability Exponent beta'(phi^2)
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 5: Stability Exponent beta'(phi^2)")
print("=" * 80)

def beta(D):
    """Beta function: beta(D) = R(D) - D"""
    return R(D) - D

def beta_derivative(D):
    """beta'(D) = R'(D) - 1 = -1/(D-1)^2 - 1 = -(D^2 - 2D + 2)/(D-1)^2"""
    return -(D ** 2 - 2 * D + 2) / (D - 1) ** 2

# Test 8: beta'(phi^2) = -(3 - phi)
beta_prime_fp = beta_derivative(phi_sq)
expected_beta_prime = -(3 - phi)
test_equality("Stability", "beta'(phi^2) = -(3-phi)",
              beta_prime_fp, expected_beta_prime,
              notes="Stability exponent at fixed point")

# Verify numerically
beta_prime_numerical = (beta(phi_sq + h) - beta(phi_sq - h)) / (2 * h)
test_equality("Stability", "beta'(phi^2) analytical = numerical",
              beta_prime_fp, beta_prime_numerical, tol=1e-6)

# Verify nu = 1/|beta'(phi^2)|
nu_from_beta = 1.0 / abs(beta_prime_fp)
test_equality("Stability", "nu = 1/|beta'(phi^2)| = phi/sqrt(5)",
              nu_from_beta, nu)

print(f"\n  beta'(phi^2) = {beta_prime_fp:.15f}")
print(f"  -(3-phi)     = {expected_beta_prime:.15f}")
print(f"  nu = 1/|beta'| = {nu_from_beta:.15f}")
print(f"  phi/sqrt(5)    = {nu:.15f}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY OF RESULTS")
print("=" * 80)

total_tests = len(test_results)
passed_tests = sum(1 for r in test_results if r.passed)
failed_tests = total_tests - passed_tests

print(f"\nTotal Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {failed_tests}")
print(f"Success Rate: {100 * passed_tests / total_tests:.1f}%")

if failed_tests > 0:
    print("\n" + "=" * 80)
    print("FAILED TESTS:")
    print("=" * 80)
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

print("\n" + "=" * 80)
print("RESULTS BY CATEGORY:")
print("=" * 80)
for category in sorted(categories.keys()):
    stats = categories[category]
    total = stats["passed"] + stats["failed"]
    print(f"{category:<25} {stats['passed']:>3}/{total:<3} passed")

# Exit code
sys.exit(0 if failed_tests == 0 else 1)
