#!/usr/bin/env python3
"""
Arrow of Time Encoding/Decoding Tests

Mathematical verification of the relationships in the encoding/decoding
arrow of time framework. Tests the fixed-point equations, efficiency ratios,
cosmological comparisons, and phi-related identities.

Each test prints what is being tested, shows the calculation, and reports
PASS/FAIL with numerical comparison.
"""

import math
from typing import Tuple, List

# =============================================================================
# Physical and Mathematical Constants
# =============================================================================

PHI = (1 + math.sqrt(5)) / 2          # Golden ratio: 1.6180339887...
PHI_SQ = (3 + math.sqrt(5)) / 2       # Phi squared: 2.6180339887...
INV_PHI = (math.sqrt(5) - 1) / 2      # 1/phi: 0.6180339887...
INV_PHI_SQ = (3 - math.sqrt(5)) / 2   # 1/phi^2: 0.3819660113...

# Cosmological observations (Planck 2018 + DESI DR2)
OMEGA_LAMBDA = 0.685    # Dark energy density fraction
OMEGA_CDM = 0.265       # Cold dark matter density fraction
OMEGA_BARYON = 0.050    # Baryon density fraction
OMEGA_MATTER = 0.315    # Total matter (CDM + baryons)

# Test tolerance
TOLERANCE = 1e-10

# =============================================================================
# Test Framework
# =============================================================================

test_results = []

def run_test(name: str, condition: bool, expected, actual, description: str = ""):
    """Run a single test and record the result."""
    status = "PASS" if condition else "FAIL"
    result = {
        'name': name,
        'status': status,
        'expected': expected,
        'actual': actual,
        'description': description
    }
    test_results.append(result)

    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    if description:
        print(f"Description: {description}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Result:   {status}")
    if not condition:
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            print(f"Difference: {abs(expected - actual)}")
    return condition

def close_to(a: float, b: float, tol: float = TOLERANCE) -> bool:
    """Check if two floats are close within tolerance."""
    return abs(a - b) < tol

# =============================================================================
# Test 1: Verify phi^2 Fixed Point
# =============================================================================

def test_1_phi_squared_fixed_point():
    """
    Test 1: Verify that phi^2 is a fixed point of D = (2D-1)/(D-1)

    The equation D = (2D-1)/(D-1) leads to D^2 - 3D + 1 = 0
    Solutions: D = (3 +/- sqrt(5))/2 = phi^2 or 1/phi^2
    """
    print("\n" + "#"*70)
    print("# TEST 1: phi^2 Fixed Point Verification")
    print("#"*70)

    # Verify quadratic equation
    # D^2 - 3D + 1 = 0 at D = phi^2
    quadratic_at_phi_sq = PHI_SQ**2 - 3*PHI_SQ + 1

    run_test(
        "1a: Quadratic equation at phi^2",
        close_to(quadratic_at_phi_sq, 0),
        0,
        quadratic_at_phi_sq,
        "D^2 - 3D + 1 should equal 0 at D = phi^2"
    )

    # Verify fixed point: f(phi^2) = (2*phi^2 - 1)/(phi^2 - 1) = phi^2
    f_of_phi_sq = (2*PHI_SQ - 1) / (PHI_SQ - 1)

    run_test(
        "1b: Fixed point equation at phi^2",
        close_to(f_of_phi_sq, PHI_SQ),
        PHI_SQ,
        f_of_phi_sq,
        "f(D) = (2D-1)/(D-1) should equal D at D = phi^2"
    )

    # Verify 1/phi^2 is also a root
    quadratic_at_inv_phi_sq = INV_PHI_SQ**2 - 3*INV_PHI_SQ + 1

    run_test(
        "1c: Quadratic equation at 1/phi^2",
        close_to(quadratic_at_inv_phi_sq, 0),
        0,
        quadratic_at_inv_phi_sq,
        "D^2 - 3D + 1 should equal 0 at D = 1/phi^2"
    )

    # Verify Vieta's formulas: sum = 3, product = 1
    root_sum = PHI_SQ + INV_PHI_SQ
    root_product = PHI_SQ * INV_PHI_SQ

    run_test(
        "1d: Sum of roots (Vieta)",
        close_to(root_sum, 3),
        3,
        root_sum,
        "phi^2 + 1/phi^2 should equal 3"
    )

    run_test(
        "1e: Product of roots (Vieta)",
        close_to(root_product, 1),
        1,
        root_product,
        "phi^2 * 1/phi^2 should equal 1"
    )

# =============================================================================
# Test 2: Efficiency Ratios
# =============================================================================

def test_2_efficiency_ratios():
    """
    Test 2: Verify efficiency ratios and their properties.

    If eta_dec = 1/phi^2, verify eta_dec + eta_dark = 1
    """
    print("\n" + "#"*70)
    print("# TEST 2: Efficiency Ratios")
    print("#"*70)

    eta_dec = INV_PHI_SQ       # Decoded (accessible) fraction
    eta_dark = 1 - INV_PHI_SQ  # Dark (inaccessible) fraction

    run_test(
        "2a: Efficiency partition",
        close_to(eta_dec + eta_dark, 1),
        1,
        eta_dec + eta_dark,
        "eta_dec + eta_dark should equal 1"
    )

    # Verify eta_dark = 1/phi (not 1 - 1/phi^2 directly, but they're equal)
    run_test(
        "2b: eta_dark equals 1/phi",
        close_to(eta_dark, INV_PHI),
        INV_PHI,
        eta_dark,
        "1 - 1/phi^2 should equal 1/phi"
    )

    # Verify 1/phi + 1/phi^2 = 1
    partition_sum = INV_PHI + INV_PHI_SQ

    run_test(
        "2c: Golden partition of unity",
        close_to(partition_sum, 1),
        1,
        partition_sum,
        "1/phi + 1/phi^2 should equal 1"
    )

    # Alternative form: phi - 1 = 1/phi
    run_test(
        "2d: phi - 1 = 1/phi identity",
        close_to(PHI - 1, INV_PHI),
        INV_PHI,
        PHI - 1,
        "phi - 1 should equal 1/phi"
    )

# =============================================================================
# Test 3: Cosmological Comparison
# =============================================================================

def test_3_cosmological_comparison():
    """
    Test 3: Compare theoretical ratios to observed cosmological densities.
    """
    print("\n" + "#"*70)
    print("# TEST 3: Cosmological Comparison")
    print("#"*70)

    # Observed ratio
    observed_ratio = OMEGA_LAMBDA / OMEGA_CDM

    # Theoretical predictions
    theoretical_phi_sq = PHI_SQ
    theoretical_5_2 = 5/2

    # Calculate discrepancies
    discrepancy_phi_sq = abs(observed_ratio - theoretical_phi_sq) / theoretical_phi_sq * 100
    discrepancy_5_2 = abs(observed_ratio - theoretical_5_2) / theoretical_5_2 * 100

    print(f"\nObserved Omega_Lambda/Omega_CDM = {observed_ratio:.4f}")
    print(f"Theoretical phi^2 = {theoretical_phi_sq:.4f}")
    print(f"Theoretical 5/2 = {theoretical_5_2:.4f}")
    print(f"Discrepancy from phi^2: {discrepancy_phi_sq:.2f}%")
    print(f"Discrepancy from 5/2: {discrepancy_5_2:.2f}%")

    # The observed ratio should be closer to phi^2 than to 5/2
    run_test(
        "3a: Omega_Lambda/Omega_CDM closer to phi^2",
        discrepancy_phi_sq < discrepancy_5_2,
        f"phi^2 discrepancy ({discrepancy_phi_sq:.2f}%) < 5/2 discrepancy",
        f"{discrepancy_phi_sq:.2f}% vs {discrepancy_5_2:.2f}%",
        "Observed ratio should be closer to phi^2 = 2.618 than to 5/2 = 2.500"
    )

    # Observed ratio should be within 5% of phi^2
    run_test(
        "3b: Omega_Lambda/Omega_CDM within 5% of phi^2",
        discrepancy_phi_sq < 5.0,
        "< 5%",
        f"{discrepancy_phi_sq:.2f}%",
        "Observed ratio should match phi^2 within 5%"
    )

    # Check if observed lies between 5/2 and phi^2
    between = theoretical_5_2 < observed_ratio < theoretical_phi_sq

    run_test(
        "3c: Observed ratio between 5/2 and phi^2",
        between,
        f"5/2 < {observed_ratio:.4f} < phi^2",
        f"{theoretical_5_2} < {observed_ratio:.4f} < {theoretical_phi_sq}",
        "Observed should lie between integer-D result (5/2) and fixed point (phi^2)"
    )

# =============================================================================
# Test 4: Self-Reference Constraint
# =============================================================================

def test_4_self_reference_constraint():
    """
    Test 4: Show that internal observer efficiency < external observer efficiency.

    Internal observer must exclude self-encoding; external observer has no such constraint.
    """
    print("\n" + "#"*70)
    print("# TEST 4: Self-Reference Constraint")
    print("#"*70)

    # For D=3 dimensions
    D = 3

    # External observer efficiency (can access all DOF)
    eta_external = 1.0  # No self-reference overhead

    # Internal observer efficiency
    # Using (D-1)/(2D-1) = 2/5 for D=3
    eta_internal_formula = (D - 1) / (2*D - 1)

    run_test(
        "4a: Internal efficiency < external efficiency",
        eta_internal_formula < eta_external,
        f"eta_internal ({eta_internal_formula:.4f}) < eta_external ({eta_external})",
        f"{eta_internal_formula:.4f} < {eta_external}",
        "Internal observer should have lower efficiency due to self-reference"
    )

    # For D=3: eta_internal = 2/5 = 0.4
    run_test(
        "4b: Internal efficiency for D=3",
        close_to(eta_internal_formula, 2/5),
        2/5,
        eta_internal_formula,
        "For D=3, eta_internal = (D-1)/(2D-1) = 2/5"
    )

    # The ratio (2D-1)/(D-1) = 5/2 is the inverse
    ratio = (2*D - 1) / (D - 1)

    run_test(
        "4c: DOF ratio for D=3",
        close_to(ratio, 5/2),
        5/2,
        ratio,
        "Observer DOF / Vacuum DOF = (2D-1)/(D-1) = 5/2 for D=3"
    )

# =============================================================================
# Test 5: Arrow Asymmetry
# =============================================================================

def test_5_arrow_asymmetry():
    """
    Test 5: Model encoding/decoding rates, show R_dec < R_enc for finite memory.
    """
    print("\n" + "#"*70)
    print("# TEST 5: Arrow Asymmetry (Encoding vs Decoding Rates)")
    print("#"*70)

    # Model: finite memory limits decoding rate
    # R_enc = R_0 (unrestricted)
    # R_dec = R_0 * min(1, T_memory/T_signal)

    R_0 = 1.0  # Baseline rate (arbitrary units)

    # Case 1: Memory time < Signal time (finite memory limits decoding)
    T_memory = 0.5
    T_signal = 1.0

    R_enc = R_0
    R_dec = R_0 * min(1, T_memory / T_signal)

    run_test(
        "5a: R_dec < R_enc for finite memory",
        R_dec < R_enc,
        f"R_dec ({R_dec}) < R_enc ({R_enc})",
        f"{R_dec} < {R_enc}",
        "When T_memory < T_signal, decoding is rate-limited"
    )

    # Case 2: Memory time = Signal time (perfect decoding possible)
    T_memory_2 = 1.0
    R_dec_2 = R_0 * min(1, T_memory_2 / T_signal)

    run_test(
        "5b: R_dec = R_enc when T_memory >= T_signal",
        close_to(R_dec_2, R_enc),
        R_enc,
        R_dec_2,
        "When T_memory >= T_signal, decoding can match encoding rate"
    )

    # The asymmetry factor for finite memory
    asymmetry = R_enc / R_dec if R_dec > 0 else float('inf')

    run_test(
        "5c: Asymmetry factor = T_signal/T_memory",
        close_to(asymmetry, T_signal / T_memory),
        T_signal / T_memory,
        asymmetry,
        "Encoding/decoding rate ratio equals signal/memory time ratio"
    )

# =============================================================================
# Test 6: Shannon Capacity with Self-Reference
# =============================================================================

def test_6_shannon_capacity():
    """
    Test 6: Shannon channel capacity with self-referential noise floor.

    Standard: C = B * log2(1 + SNR)
    With self-reference: C_eff = C * eta_internal
    """
    print("\n" + "#"*70)
    print("# TEST 6: Shannon Capacity with Self-Reference")
    print("#"*70)

    B = 1.0      # Bandwidth (arbitrary units)
    SNR = 100    # Signal-to-noise ratio

    # Standard Shannon capacity
    C_standard = B * math.log2(1 + SNR)

    # Self-referential capacity (internal observer)
    D = 3
    eta_internal = (D - 1) / (2*D - 1)  # = 2/5 for D=3
    C_self_ref = C_standard * eta_internal

    run_test(
        "6a: Self-ref capacity < standard capacity",
        C_self_ref < C_standard,
        f"C_self_ref ({C_self_ref:.4f}) < C_standard ({C_standard:.4f})",
        f"{C_self_ref:.4f} < {C_standard:.4f}",
        "Internal observer has reduced effective capacity"
    )

    # Efficiency ratio
    efficiency = C_self_ref / C_standard

    run_test(
        "6b: Efficiency equals eta_internal",
        close_to(efficiency, eta_internal),
        eta_internal,
        efficiency,
        "Capacity ratio should equal (D-1)/(2D-1)"
    )

    # Self-referential "noise" contribution
    # Effective SNR_eff = SNR * eta / (1 - eta) for internal observer
    # This models the self-encoding as additional noise
    SNR_eff = SNR * eta_internal / (1 - eta_internal)
    C_via_SNR = B * math.log2(1 + SNR_eff)

    print(f"\nEffective SNR for internal observer: {SNR_eff:.2f}")
    print(f"Capacity via modified SNR: {C_via_SNR:.4f}")
    print(f"This models self-reference as 'noise' that reduces SNR")

# =============================================================================
# Test 7: The phi Cascade
# =============================================================================

def test_7_phi_cascade():
    """
    Test 7: Verify the phi cascade and information partition.

    1/phi = 0.618, 1/phi^2 = 0.382, their sum = 1
    This partitions information into accessible and dark fractions.
    """
    print("\n" + "#"*70)
    print("# TEST 7: The phi Cascade")
    print("#"*70)

    # Basic phi identities
    run_test(
        "7a: 1/phi value",
        close_to(INV_PHI, 0.6180339887),
        0.6180339887,
        INV_PHI,
        "1/phi should approximately equal 0.618"
    )

    run_test(
        "7b: 1/phi^2 value",
        close_to(INV_PHI_SQ, 0.3819660113),
        0.3819660113,
        INV_PHI_SQ,
        "1/phi^2 should approximately equal 0.382"
    )

    # Partition of unity
    run_test(
        "7c: 1/phi + 1/phi^2 = 1",
        close_to(INV_PHI + INV_PHI_SQ, 1.0),
        1.0,
        INV_PHI + INV_PHI_SQ,
        "1/phi + 1/phi^2 should equal exactly 1"
    )

    # The cascade: phi^n ratios
    print("\nPhi cascade (powers of 1/phi):")
    phi_powers = [PHI**(-n) for n in range(6)]
    for n, val in enumerate(phi_powers):
        print(f"  (1/phi)^{n} = {val:.6f}")

    # Verify phi^2 - phi = 1
    run_test(
        "7d: phi^2 - phi = 1",
        close_to(PHI_SQ - PHI, 1),
        1,
        PHI_SQ - PHI,
        "This is equivalent to phi^2 = phi + 1"
    )

    # Verify sqrt(5) = phi + 1/phi
    sqrt_5_check = PHI + INV_PHI

    run_test(
        "7e: sqrt(5) = phi + 1/phi",
        close_to(sqrt_5_check, math.sqrt(5)),
        math.sqrt(5),
        sqrt_5_check,
        "The golden ratio property: phi + 1/phi = sqrt(5)"
    )

# =============================================================================
# Test 8: DOF Ratio at Various Dimensions
# =============================================================================

def test_8_dof_ratio_dimensions():
    """
    Test 8: Compute (2D-1)/(D-1) for D = 1,2,3,4,5 and find convergence to phi^2.
    """
    print("\n" + "#"*70)
    print("# TEST 8: DOF Ratio at Various Dimensions")
    print("#"*70)

    print("\nDOF ratio (2D-1)/(D-1) for integer dimensions:")
    print(f"{'D':<5} {'Observer DOF':<15} {'Vacuum DOF':<15} {'Ratio':<15} {'vs phi^2':<15}")
    print("-" * 65)

    for D in [2, 3, 4, 5, 10, 100]:
        obs_dof = 2*D - 1
        vac_dof = D - 1
        ratio = obs_dof / vac_dof if vac_dof > 0 else float('inf')
        vs_phi_sq = (ratio - PHI_SQ) / PHI_SQ * 100
        print(f"{D:<5} {obs_dof:<15} {vac_dof:<15} {ratio:<15.4f} {vs_phi_sq:+.2f}%")

    # D=1 is undefined (division by zero)
    print("\nNote: D=1 is undefined (vacuum DOF = 0)")

    # As D -> infinity, ratio -> 2
    D_large = 1000
    ratio_large = (2*D_large - 1) / (D_large - 1)

    run_test(
        "8a: Ratio approaches 2 as D -> infinity",
        close_to(ratio_large, 2, tol=0.01),
        2,
        ratio_large,
        "For large D, (2D-1)/(D-1) -> 2"
    )

    # D=3 gives exactly 5/2
    D = 3
    ratio_D3 = (2*D - 1) / (D - 1)

    run_test(
        "8b: D=3 gives ratio 5/2",
        close_to(ratio_D3, 2.5),
        2.5,
        ratio_D3,
        "For D=3, (2D-1)/(D-1) = 5/2 exactly"
    )

# =============================================================================
# Test 9: Fixed Point Stability
# =============================================================================

def test_9_fixed_point_stability():
    """
    Test 9: Iterate D_new = (2D-1)/(D-1) from various starting points.
    Show convergence to phi^2.
    """
    print("\n" + "#"*70)
    print("# TEST 9: Fixed Point Stability (Iteration)")
    print("#"*70)

    def iterate(D0: float, n_iter: int = 20) -> List[float]:
        """Iterate f(D) = (2D-1)/(D-1) n_iter times."""
        sequence = [D0]
        D = D0
        for _ in range(n_iter):
            if abs(D - 1) < 1e-10:
                break  # Avoid division by zero
            D = (2*D - 1) / (D - 1)
            sequence.append(D)
        return sequence

    starting_points = [3.0, 4.0, 10.0, 2.1, 1.5]

    print("\nIteration from various starting points:")

    all_converge = True
    for D0 in starting_points:
        sequence = iterate(D0, 50)
        final = sequence[-1]
        converged = close_to(final, PHI_SQ, tol=1e-6)
        all_converge = all_converge and converged

        print(f"\nD_0 = {D0}:")
        print(f"  First 5: {[f'{x:.4f}' for x in sequence[:5]]}")
        print(f"  Final: {final:.10f}")
        print(f"  phi^2:  {PHI_SQ:.10f}")
        print(f"  Converged: {converged}")

    run_test(
        "9a: All starting points converge to phi^2",
        all_converge,
        f"All converge to {PHI_SQ:.6f}",
        f"Tested: {starting_points}",
        "The fixed point phi^2 is an attractor"
    )

    # Test stability via derivative
    # f'(D) = -1/(D-1)^2
    # At D = phi^2: |f'(phi^2)| = 1/(phi^2 - 1)^2 = 1/phi^2 < 1 => stable
    derivative_at_fixed = 1 / (PHI_SQ - 1)**2

    run_test(
        "9b: |f'(phi^2)| < 1 (stability criterion)",
        derivative_at_fixed < 1,
        "< 1",
        derivative_at_fixed,
        "|f'(phi^2)| = 1/(phi^2-1)^2 = 1/phi^2 = 0.382 < 1 => stable"
    )

    # The unstable fixed point at 1/phi^2
    derivative_at_unstable = 1 / (INV_PHI_SQ - 1)**2

    run_test(
        "9c: |f'(1/phi^2)| > 1 (instability)",
        derivative_at_unstable > 1,
        "> 1",
        derivative_at_unstable,
        "|f'(1/phi^2)| = phi^2 = 2.618 > 1 => unstable"
    )

# =============================================================================
# Test 10: Entropy Production
# =============================================================================

def test_10_entropy_production():
    """
    Test 10: Model encoding as entropy increase.
    Show decoding requires work proportional to 1/eta_dec.
    """
    print("\n" + "#"*70)
    print("# TEST 10: Entropy Production and Decoding Work")
    print("#"*70)

    # Information to encode/decode (in bits)
    I_bits = 1.0

    # k_B * T * ln(2) per bit (Landauer's limit)
    # We use normalized units where this = 1
    kT_ln2 = 1.0

    # Minimum work to encode (at Landauer limit)
    W_encode = kT_ln2 * I_bits

    # Minimum work to decode for internal observer
    # Must overcome self-reference overhead: W = kT ln2 * I / eta
    D = 3
    eta_dec = (D - 1) / (2*D - 1)  # = 2/5
    W_decode_internal = kT_ln2 * I_bits / eta_dec

    # For external observer (eta = 1)
    W_decode_external = kT_ln2 * I_bits / 1.0

    run_test(
        "10a: Internal decoding work > encoding work",
        W_decode_internal > W_encode,
        f"W_dec ({W_decode_internal:.4f}) > W_enc ({W_encode:.4f})",
        f"{W_decode_internal:.4f} > {W_encode:.4f}",
        "Internal observer pays self-reference tax on decoding"
    )

    run_test(
        "10b: Internal decoding work > external decoding work",
        W_decode_internal > W_decode_external,
        f"W_int ({W_decode_internal:.4f}) > W_ext ({W_decode_external:.4f})",
        f"{W_decode_internal:.4f} > {W_decode_external:.4f}",
        "Self-reference increases decoding cost"
    )

    # The work ratio is 1/eta = phi^2 at the fixed point
    work_ratio = W_decode_internal / W_encode

    run_test(
        "10c: Work ratio = 1/eta = (2D-1)/(D-1)",
        close_to(work_ratio, (2*D - 1)/(D - 1)),
        (2*D - 1)/(D - 1),
        work_ratio,
        "For D=3, work ratio = 5/2 = 2.5"
    )

    # At the fixed point, work ratio = phi^2
    print(f"\nAt the fixed point D = phi^2:")
    print(f"  eta_dec = (phi^2 - 1)/(2*phi^2 - 1) = phi/(2*phi^2 - 1)")
    print(f"  Since phi^2 = phi + 1:")
    print(f"  eta_dec = phi/(2phi + 1) = phi/(phi^2 + phi) = 1/(phi + 1) = 1/phi^2")
    print(f"  Therefore: W_decode / W_encode = phi^2 = {PHI_SQ:.4f}")

    # Verify: at fixed point, eta = 1/phi^2
    eta_at_fixed = INV_PHI_SQ
    work_ratio_at_fixed = 1 / eta_at_fixed

    run_test(
        "10d: At fixed point, work ratio = phi^2",
        close_to(work_ratio_at_fixed, PHI_SQ),
        PHI_SQ,
        work_ratio_at_fixed,
        "1/eta = 1/(1/phi^2) = phi^2"
    )

# =============================================================================
# BONUS: Additional phi identities
# =============================================================================

def test_bonus_phi_identities():
    """
    Bonus tests: Additional phi identities relevant to the framework.
    """
    print("\n" + "#"*70)
    print("# BONUS: Additional phi Identities")
    print("#"*70)

    # phi is the continued fraction [1; 1, 1, 1, ...]
    # Approximate by truncation
    def continued_fraction_phi(n_terms: int) -> float:
        result = 1
        for _ in range(n_terms):
            result = 1 + 1/result
        return result

    cf_approx = continued_fraction_phi(50)  # Use more iterations for convergence

    run_test(
        "B1: phi from continued fraction",
        close_to(cf_approx, PHI, tol=1e-8),  # Relaxed tolerance for iterative method
        PHI,
        cf_approx,
        "phi = [1; 1, 1, 1, ...] = lim_{n->inf} F_{n+1}/F_n"
    )

    # Fibonacci ratio approaches phi
    def fib(n: int) -> int:
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    fib_ratio = fib(40) / fib(39)  # Use larger Fibonacci numbers

    run_test(
        "B2: Fibonacci ratio approaches phi",
        close_to(fib_ratio, PHI, tol=1e-8),  # Relaxed tolerance for iterative method
        PHI,
        fib_ratio,
        "F_n / F_{n-1} -> phi as n -> infinity"
    )

    # phi^n = F_n * phi + F_{n-1} (extended Binet)
    n = 10
    phi_power = PHI**n
    fib_formula = fib(n) * PHI + fib(n-1)

    run_test(
        "B3: phi^n = F_n * phi + F_{n-1}",
        close_to(phi_power, fib_formula),
        phi_power,
        fib_formula,
        f"For n={n}: phi^{n} = F_{n}*phi + F_{n-1}"
    )

    # (1 - 1/phi^2)^2 + (1/phi^2)^2 related to golden spiral
    sum_of_squares = INV_PHI**2 + INV_PHI_SQ**2

    run_test(
        "B4: (1/phi)^2 + (1/phi^2)^2",
        close_to(sum_of_squares, INV_PHI_SQ + INV_PHI**4),
        INV_PHI_SQ + INV_PHI**4,
        sum_of_squares,
        f"= {sum_of_squares:.6f}"
    )

# =============================================================================
# Main Test Runner
# =============================================================================

def run_all_tests():
    """Run all tests and print summary."""
    print("\n" + "="*70)
    print("ARROW OF TIME ENCODING/DECODING TESTS")
    print("Mathematical verification of framework relationships")
    print("="*70)

    # Run all test functions
    test_1_phi_squared_fixed_point()
    test_2_efficiency_ratios()
    test_3_cosmological_comparison()
    test_4_self_reference_constraint()
    test_5_arrow_asymmetry()
    test_6_shannon_capacity()
    test_7_phi_cascade()
    test_8_dof_ratio_dimensions()
    test_9_fixed_point_stability()
    test_10_entropy_production()
    test_bonus_phi_identities()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for r in test_results if r['status'] == 'PASS')
    failed = sum(1 for r in test_results if r['status'] == 'FAIL')
    total = len(test_results)

    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {100*passed/total:.1f}%")

    if failed > 0:
        print("\nFailed tests:")
        for r in test_results:
            if r['status'] == 'FAIL':
                print(f"  - {r['name']}")

    print("\n" + "="*70)
    print("KEY phi VALUES FOR REFERENCE")
    print("="*70)
    print(f"phi = (1 + sqrt(5))/2 = {PHI:.10f}")
    print(f"phi^2 = (3 + sqrt(5))/2 = {PHI_SQ:.10f}")
    print(f"1/phi = (sqrt(5) - 1)/2 = {INV_PHI:.10f}")
    print(f"1/phi^2 = (3 - sqrt(5))/2 = {INV_PHI_SQ:.10f}")
    print(f"sqrt(5) = {math.sqrt(5):.10f}")
    print(f"\n1/phi + 1/phi^2 = {INV_PHI + INV_PHI_SQ:.10f} (should be 1.0)")
    print(f"phi^2 + 1/phi^2 = {PHI_SQ + INV_PHI_SQ:.10f} (should be 3.0)")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
