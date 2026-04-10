# =============================================================================
# DS2-Craft  |  simulation/mass_properties/mass_estimate.py
# Revision A  —  Component Mass Roll-Up and Centre of Mass Estimate
# =============================================================================
# PURPOSE
# -------
# Rolls up all component masses and estimates the system centre of mass (CoM).
# Outputs: total dry mass, GVW, CoM coordinates, and a per-component table.
#
# KNOWN REQUIREMENTS
# ------------------
# • Target dry mass ≤ 160 kg
# • Rider mass = 250 lb (113 kg)
# • CoM should be close to mid-wheelbase for water stability
# • CoM height should be minimised (low battery pod, low pontoons)
#
# ASSUMPTIONS
# -----------
# A1. All CoM locations are rough centroid estimates — not from CAD mass props.
# A2. X measured from mid-wheelbase (+ = forward, − = rear).
# A3. Y measured from vehicle centreline (symmetric — all Y = 0 for net CoM).
# A4. Z measured from ground level.
# A5. Rider is modelled as a seated point mass at approximate hip position.
# A6. Component masses are Rev A budget values — update after detailed design.
# =============================================================================

# ---------------------------------------------------------------------------
# COMPONENT TABLE
# ---------------------------------------------------------------------------
# Each entry: (label, mass_kg, x_mm, y_mm, z_mm, notes)
#   x, y, z = estimated centroid location of the component

COMPONENTS = [
    # SYS-01 Chassis Frame
    # Space-frame runs full wheelbase; centroid near mid-chassis
    ("Chassis Frame",       28,     0,   0,  400,  "SYS-01: 4130 Cr-Mo space-frame"),

    # SYS-02 Flotation Pods (both together, symmetric → Y=0 net)
    # Pontoons centred longitudinally at X=0; centroid Z = PONTOON_OFFSET_Z = 390 mm
    ("Pontoons (×2)",       10,     0,   0,  390,  "SYS-02: Al shell + foam fill"),

    # SYS-03 Battery & Electronics Pod
    # Pod centred at mid-wheelbase; bottom at 320 mm, top at ~530 mm → centroid ~425 mm
    ("Battery Pod",         38,     0,   0,  425,  "SYS-03: 72V LiFePO4 + BMS + controller"),

    # SYS-04 Rear Drivetrain (motor, gearbox, rear axle)
    # Rear of vehicle at X = −700 mm; height ~ hub height
    ("Rear Drivetrain",     12,  -620,   0,  280,  "SYS-04: motor + reduction + axle"),

    # SYS-05 Front Steering Axle (knuckle, rack, tie-rods — no motor)
    ("Front Steering Axle",  6,   700,   0,  280,  "SYS-05: knuckle + rack + tie-rods"),

    # SYS-06 Suspension (A-arms, springs, dampers — all 4 corners; symmetric)
    ("Suspension (×4)",     18,     0,   0,  350,  "SYS-06: arms, springs, dampers"),

    # SYS-07 Wheels & Tires (4×; approx at axle height, symmetric X pairs)
    # Effective centroid X weighted: 2 front at +700, 2 rear at -700 → net X=0
    ("Wheels & Tires (×4)", 16,     0,   0,  280,  "SYS-07: paddle bias off-road tires"),

    # SYS-08 Rider Interface (seat, bars, pegs)
    # Seat at approximately wheelbase midpoint, low seat height ~600 mm
    ("Rider Interface",      6,    50,   0,  550,  "SYS-08: seat, bars, footpegs"),

    # SYS-09 Body / Fairings (non-structural, mostly low-slung)
    ("Body / Fairings",     10,     0,   0,  500,  "SYS-09: outer panels (estimate)"),

    # SYS-10 Wiring & Plumbing
    ("Wiring / Plumbing",    4,     0,   0,  380,  "SYS-10: harness, connectors"),
]

# Rider as a separate load (not part of dry vehicle)
RIDER_LABEL  = "Rider (250 lb)"
RIDER_MASS   = 113   # kg
RIDER_X      =  50   # mm  — hip slightly forward of mid-wheelbase
RIDER_Y      =   0   # mm
RIDER_Z      = 700   # mm  — approximate seated hip height


# ---------------------------------------------------------------------------
# CALCULATIONS
# ---------------------------------------------------------------------------

def compute_mass_properties(components, rider=None):
    """
    Roll up mass and CoM from a list of (label, mass, x, y, z, notes).

    If rider is provided as (label, mass, x, y, z), it is added separately.

    Returns:
        (total_mass_kg, com_x_mm, com_y_mm, com_z_mm, detail_list)
    """
    total_mass = 0.0
    wx = wy = wz = 0.0

    detail = []
    for row in components:
        label, m, x, y, z = row[0], row[1], row[2], row[3], row[4]
        total_mass += m
        wx += m * x
        wy += m * y
        wz += m * z
        detail.append((label, m, x, y, z))

    if rider:
        r_label, r_m, r_x, r_y, r_z = rider
        total_mass += r_m
        wx += r_m * r_x
        wy += r_m * r_y
        wz += r_m * r_z
        detail.append((r_label, r_m, r_x, r_y, r_z))

    if total_mass > 0:
        com_x = wx / total_mass
        com_y = wy / total_mass
        com_z = wz / total_mass
    else:
        com_x = com_y = com_z = 0.0

    return total_mass, com_x, com_y, com_z, detail


def run_report():
    """Compute and print the full mass properties report."""

    # — Dry vehicle —
    dry_mass, dry_cx, dry_cy, dry_cz, dry_detail = compute_mass_properties(
        COMPONENTS, rider=None
    )

    # — Gross vehicle weight (with rider) —
    gvw, gvw_cx, gvw_cy, gvw_cz, gvw_detail = compute_mass_properties(
        COMPONENTS,
        rider=(RIDER_LABEL, RIDER_MASS, RIDER_X, RIDER_Y, RIDER_Z)
    )

    target_dry = 160  # kg

    print("=" * 70)
    print("DS2-Craft  |  Mass Properties Estimate  |  Revision A")
    print("=" * 70)

    print("\n── COMPONENT BREAKDOWN ──────────────────────────────────────────────")
    print(f"  {'Component':<28} {'Mass':>7}  {'CoM X':>8}  {'CoM Y':>8}  {'CoM Z':>8}")
    print("  " + "-" * 65)
    for label, m, x, y, z in dry_detail:
        print(f"  {label:<28} {m:>6.1f}kg  {x:>7.0f}mm  {y:>7.0f}mm  {z:>7.0f}mm")

    print("  " + "-" * 65)
    print(f"  {'VEHICLE DRY TOTAL':<28} {dry_mass:>6.1f}kg  "
          f"{dry_cx:>7.1f}mm  {dry_cy:>7.1f}mm  {dry_cz:>7.1f}mm")

    print(f"\n  {'Rider':<28} {RIDER_MASS:>6.1f}kg  "
          f"{RIDER_X:>7.0f}mm  {RIDER_Y:>7.0f}mm  {RIDER_Z:>7.0f}mm")
    print(f"  {'GVW TOTAL':<28} {gvw:>6.1f}kg  "
          f"{gvw_cx:>7.1f}mm  {gvw_cy:>7.1f}mm  {gvw_cz:>7.1f}mm")

    print("\n── SUMMARY ──────────────────────────────────────────────────────────")
    print(f"  Dry mass           : {dry_mass:.1f} kg  (target ≤ {target_dry} kg)")
    if dry_mass <= target_dry:
        print(f"  ✅  Dry mass target MET  (margin {target_dry - dry_mass:.1f} kg)")
    else:
        print(f"  ❌  Dry mass target EXCEEDED by {dry_mass - target_dry:.1f} kg")

    print(f"  GVW                : {gvw:.1f} kg")
    print(f"  CoM X (dry)        : {dry_cx:.1f} mm from mid-wheelbase "
          f"({'forward' if dry_cx > 0 else 'rearward'})")
    print(f"  CoM Z (dry)        : {dry_cz:.1f} mm above ground")
    print(f"  CoM X (GVW)        : {gvw_cx:.1f} mm from mid-wheelbase")
    print(f"  CoM Z (GVW)        : {gvw_cz:.1f} mm above ground")

    print("\n── FRONT / REAR WEIGHT DISTRIBUTION (GVW) ──────────────────────────")
    wb = 1400  # mm  (half-wheelbase = 700)
    half_wb = wb / 2.0
    # Static axle loads (lever rule)
    rear_frac  = (gvw_cx + half_wb) / wb   # fraction at rear axle
    front_frac = 1.0 - rear_frac
    front_kg   = gvw * front_frac
    rear_kg    = gvw * rear_frac
    print(f"  Front axle load    : {front_kg:.1f} kg  ({front_frac * 100:.1f}%)")
    print(f"  Rear axle load     : {rear_kg:.1f} kg  ({rear_frac * 100:.1f}%)")

    print("\n── NOTES / ASSUMPTIONS ──────────────────────────────────────────────")
    print("  A1. CoM locations are centroid estimates, not CAD-derived.")
    print("  A2. All Y components are symmetric → net CoM Y ≈ 0.")
    print("  A3. Rider hip at X=50 mm (slightly forward of mid-WB), Z=700 mm.")
    print("  A4. Update after completing CAD geometry in Rev A.")
    print("=" * 70)


if __name__ == "__main__":
    run_report()
