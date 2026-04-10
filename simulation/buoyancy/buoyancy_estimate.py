# =============================================================================
# DS2-Craft  |  simulation/buoyancy/buoyancy_estimate.py
# Revision A  —  Static Buoyancy Check
# =============================================================================
# PURPOSE
# -------
# Estimates whether the vehicle + rider system can float given the two
# side pontoons and any additional buoyant volume in the chassis/body.
#
# This is a first-order static calculation only:
#   • Archimedes principle:  Buoyant force = ρ × g × V_submerged
#   • Stability not assessed here (see risk R-03)
#   • Water propulsion not assessed here (see risk R-04)
#
# OUTPUTS
# -------
# 1. Displaced volume required to float (m³ and litres)
# 2. Available pontoon volume (m³ and litres)
# 3. Float margin (positive = surplus buoyancy, negative = sinks)
# 4. Draft estimate (how deep the pontoons must be submerged to float)
# 5. Freeboard estimate (how much pontoon remains above waterline)
# 6. Pass / Fail recommendation
#
# KNOWN REQUIREMENTS
# ------------------
# • Must float with rider aboard  →  GVW = vehicle dry + rider mass
# • Buoyancy source: two cylindrical pontoons (SYS-02)
# • No fantasy submarine logic — treat as simple closed-top cylinders
#
# ASSUMPTIONS
# -----------
# A1. Pontoons are fully sealed and foam-filled; no water intrusion assumed
#     for this pass/fail check.
# A2. Water density = 1 000 kg/m³ (fresh water); salt water = 1 025 kg/m³
#     is also reported for completeness.
# A3. Vehicle body/chassis displacement (hull effect) is ignored in Rev A.
#     It provides a small safety margin; include in Rev B if margin is tight.
# A4. Pontoons are horizontal, circular cross-section cylinders.
# A5. Draft is estimated geometrically assuming pontoons are the sole
#     buoyant volumes.  This ignores trim angle (horizontal assumed).
# A6. GVW from mass estimate script; defaults used here are Rev A budget values.
# =============================================================================

import math

# ---------------------------------------------------------------------------
# PARAMETERS  (edit to match current source of truth)
# ---------------------------------------------------------------------------

# — Pontoon geometry —
PONTOON_LENGTH_MM       = 1400   # mm
PONTOON_DIAMETER_MM     =  220   # mm
PONTOON_WALL_MM         =    4   # mm   (foam fill assumed; shell weight in mass_estimate)
FOAM_FILL_FRACTION      = 0.85   # fraction of internal volume = foam (not buoyant)

# — Mass budget —
VEHICLE_DRY_MASS_KG     = 148    # kg   (from mass budget Rev A — includes front steering axle)
RIDER_MASS_KG           = 113    # kg   (250 lb target rider)

# — Physics constants —
RHO_FRESH_KG_M3         = 1000   # kg/m³  fresh water
RHO_SALT_KG_M3          = 1025   # kg/m³  salt water
G_M_S2                  = 9.81   # m/s²

# — Safety factor —
BUOYANCY_SAFETY_FACTOR  = 1.15   # target: pontoons provide 15% more than needed


# ---------------------------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------------------------

def pontoon_gross_volume_m3(diameter_mm, length_mm):
    """Full external cylinder volume in m³."""
    r = (diameter_mm / 1000.0) / 2.0
    L = length_mm / 1000.0
    return math.pi * r**2 * L


def pontoon_inner_volume_m3(diameter_mm, wall_mm, length_mm):
    """Internal cavity volume in m³ (air + foam space)."""
    r_inner = ((diameter_mm - 2 * wall_mm) / 1000.0) / 2.0
    L = length_mm / 1000.0
    return math.pi * r_inner**2 * L


def buoyant_volume_per_pontoon_m3():
    """
    Effective buoyant volume of one pontoon.

    The foam fill occupies FOAM_FILL_FRACTION of the internal volume and has
    negligible density relative to water — it does NOT displace water
    (the shell and foam together are lighter than the water they displace).
    The entire gross external volume displaces water when submerged.
    """
    return pontoon_gross_volume_m3(PONTOON_DIAMETER_MM, PONTOON_LENGTH_MM)


def required_displacement_m3(total_mass_kg, rho=RHO_FRESH_KG_M3):
    """Volume of water that must be displaced to support total_mass_kg."""
    return total_mass_kg / rho


def draft_fraction(required_vol_m3, gross_vol_per_pontoon_m3, n_pontoons=2):
    """
    Fraction of pontoon diameter that must be submerged.

    Uses the formula for a partially submerged horizontal cylinder:
        A_segment = r²·(θ − sin θ·cos θ)  where θ = arccos(1 − draft/r)
        V_segment = A_segment × L

    Solves numerically: find θ such that 2 × A_segment × L = required_vol_m3
    Returns (draft_m, freeboard_m, submerged_fraction).
    """
    r_m = (PONTOON_DIAMETER_MM / 1000.0) / 2.0
    L_m = PONTOON_LENGTH_MM / 1000.0

    # Total volume available from n_pontoons
    v_target = required_vol_m3  # we need this from both pontoons combined

    # Volume of partially submerged cylinder as function of depth d (0 ≤ d ≤ 2r)
    def v_partial(d):
        if d <= 0:
            return 0.0
        if d >= 2 * r_m:
            return math.pi * r_m**2 * L_m
        # Segment area formula
        theta = math.acos(1.0 - d / r_m)
        A = r_m**2 * (theta - math.sin(theta) * math.cos(theta))
        return n_pontoons * A * L_m

    # Binary search for draft depth d such that v_partial(d) = v_target
    d_lo, d_hi = 0.0, 2 * r_m
    for _ in range(60):
        d_mid = (d_lo + d_hi) / 2.0
        if v_partial(d_mid) < v_target:
            d_lo = d_mid
        else:
            d_hi = d_mid
    draft = (d_lo + d_hi) / 2.0
    freeboard = 2 * r_m - draft
    submerged_frac = draft / (2 * r_m)
    return draft, freeboard, submerged_frac


def run_check():
    """Run the buoyancy check and print a full report."""
    gvw_kg = VEHICLE_DRY_MASS_KG + RIDER_MASS_KG

    v_per_pontoon  = buoyant_volume_per_pontoon_m3()
    v_total        = 2 * v_per_pontoon
    v_required_fw  = required_displacement_m3(gvw_kg, RHO_FRESH_KG_M3)
    v_required_sw  = required_displacement_m3(gvw_kg, RHO_SALT_KG_M3)

    buoyant_force_fresh_N = v_total * RHO_FRESH_KG_M3 * G_M_S2
    buoyant_force_fresh_kg = buoyant_force_fresh_N / G_M_S2

    margin_fw  = v_total - v_required_fw
    margin_sw  = v_total - v_required_sw
    factor_fw  = v_total / v_required_fw
    factor_sw  = v_total / v_required_sw

    draft_fw, freeboard_fw, frac_fw = draft_fraction(v_required_fw, v_per_pontoon)

    passes = factor_fw >= BUOYANCY_SAFETY_FACTOR

    print("=" * 65)
    print("DS2-Craft  |  Buoyancy Estimate  |  Revision A")
    print("=" * 65)

    print("\n── INPUTS ──────────────────────────────────────────────────")
    print(f"  Vehicle dry mass        : {VEHICLE_DRY_MASS_KG:>8.1f} kg")
    print(f"  Rider mass              : {RIDER_MASS_KG:>8.1f} kg  (250 lb)")
    print(f"  GVW                     : {gvw_kg:>8.1f} kg")
    print(f"  Pontoon diameter        : {PONTOON_DIAMETER_MM:>8.0f} mm")
    print(f"  Pontoon length          : {PONTOON_LENGTH_MM:>8.0f} mm")
    print(f"  Number of pontoons      : {'2':>8}")
    print(f"  Foam fill fraction      : {FOAM_FILL_FRACTION:>8.2f}")

    print("\n── VOLUMES ─────────────────────────────────────────────────")
    print(f"  Vol per pontoon (gross) : {v_per_pontoon * 1000:>8.3f} L")
    print(f"  Total buoyant volume    : {v_total * 1000:>8.3f} L")
    print(f"  Required (fresh water)  : {v_required_fw * 1000:>8.3f} L")
    print(f"  Required (salt water)   : {v_required_sw * 1000:>8.3f} L")

    print("\n── FLOAT MARGIN ─────────────────────────────────────────────")
    print(f"  Fresh water margin      : {margin_fw * 1000:>+8.3f} L  "
          f"({'SURPLUS' if margin_fw > 0 else 'DEFICIT'})")
    print(f"  Salt water  margin      : {margin_sw * 1000:>+8.3f} L  "
          f"({'SURPLUS' if margin_sw > 0 else 'DEFICIT'})")
    print(f"  Buoyancy factor (fresh) : {factor_fw:>8.3f}  "
          f"(target ≥ {BUOYANCY_SAFETY_FACTOR:.2f})")
    print(f"  Buoyancy factor (salt)  : {factor_sw:>8.3f}")

    print("\n── DRAFT ESTIMATE (fresh water, horizontal) ─────────────────")
    print(f"  Draft (both pontoons)   : {draft_fw * 1000:>8.1f} mm")
    print(f"  Freeboard               : {freeboard_fw * 1000:>8.1f} mm")
    print(f"  Submerged fraction      : {frac_fw * 100:>8.1f} %")

    print("\n── VERDICT ─────────────────────────────────────────────────")
    if passes:
        print(f"  ✅  PASS — Buoyancy factor {factor_fw:.3f} ≥ {BUOYANCY_SAFETY_FACTOR:.2f}")
    else:
        print(f"  ❌  FAIL — Buoyancy factor {factor_fw:.3f} < {BUOYANCY_SAFETY_FACTOR:.2f}")
        needed_L = v_required_fw * BUOYANCY_SAFETY_FACTOR * 1000
        delta_L  = needed_L - v_total * 1000
        print(f"       Need {delta_L:.1f} L more buoyant volume.")
        # Suggest larger diameter
        new_r = math.sqrt(
            (v_required_fw * BUOYANCY_SAFETY_FACTOR / 2) / (math.pi * PONTOON_LENGTH_MM / 1000)
        )
        print(f"       Suggestion: increase pontoon OD to ≈ {new_r * 2 * 1000:.0f} mm "
              f"(keep same length).")

    print("\n── NOTES / ASSUMPTIONS ──────────────────────────────────────")
    print("  A1. Pontoons fully sealed; no water intrusion in this check.")
    print("  A2. Fresh water baseline; salt water adds ~2.5% buoyancy margin.")
    print("  A3. Chassis hull displacement ignored (conservative).")
    print("  A4. Trim angle assumed zero (horizontal).")
    print("  A5. Stability (roll/pitch CoM vs CoB) not assessed here — see R-03.")
    print("=" * 65)


if __name__ == "__main__":
    run_check()
