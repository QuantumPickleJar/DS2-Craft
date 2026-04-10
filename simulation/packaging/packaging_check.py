# =============================================================================
# DS2-Craft  |  simulation/packaging/packaging_check.py
# Revision A  —  Hard Clearance and Overlap Checks
# =============================================================================
# PURPOSE
# -------
# Verifies that major subsystem bounding boxes do not overlap each other and
# that each subsystem clears the ground by its required minimum clearance.
#
# This is a conservative axis-aligned bounding box (AABB) check only.
# Exact geometry interference requires a full FreeCAD Boolean check in Rev B.
#
# OUTPUTS
# -------
# • Ground clearance pass/fail for each subsystem
# • AABB overlap matrix between subsystem pairs
# • Overall PASS / FAIL verdict
#
# KNOWN REQUIREMENTS
# ------------------
# • GROUND_CLEARANCE = 280 mm (bottom of any structural component)
# • Battery pod bottom = BATT_POD_CLEARANCE_Z = 320 mm (above GC floor)
# • Pontoons must not contact the tire envelope
# • Battery pod must not overlap the pontoon cross-section
#
# ASSUMPTIONS
# -----------
# A1. Each subsystem represented as an AABB: (x_min, y_min, z_min, x_max, y_max, z_max)
# A2. All coordinates in mm; origin = mid-wheelbase, mid-track, ground level.
# A3. Tire envelope = cylinder; approximated as AABB for overlap check.
# A4. Pontoon approximated as AABB (conservative — actual cylinder is smaller).
# A5. Rider envelope is a bounding box around the seated rider.
# A6. Minimum ground clearance for any non-drivetrain component = 280 mm.
#     Wheel/tire contact patch = 0 mm (by definition).
# =============================================================================

# ---------------------------------------------------------------------------
# PARAMETERS
# ---------------------------------------------------------------------------

# Chassis geometry
WHEELBASE           = 1400   # mm
TRACK_FRONT         =  900   # mm
TRACK_REAR          =  800   # mm
GROUND_CLEARANCE    =  280   # mm
FRAME_HEIGHT        =  350   # mm

# Pontoon
PONTOON_LENGTH      = 1400   # mm
PONTOON_DIAMETER    =  220   # mm
PONTOON_OFFSET_Y    =  450   # mm   (from CL to pontoon CL)
PONTOON_OFFSET_Z    =  390   # mm   (pontoon CL height above ground; min = GC(280) + r(110))

# Battery pod (external dimensions derived here)
BATT_POD_LENGTH     =  620   # mm  (internal)
BATT_POD_WIDTH      =  280   # mm  (internal)
BATT_POD_HEIGHT     =  180   # mm  (internal)
BATT_POD_WALL       =    5   # mm
BATT_POD_CLEARANCE_Z=  320   # mm  (pod bottom above ground)

# Tires
TIRE_DIAMETER       =  560   # mm
TIRE_WIDTH          =  250   # mm

# Rider envelope
RIDER_HIP_X         =   50   # mm
RIDER_HIP_Z         =  700   # mm
RIDER_WIDTH         =  550   # mm  (shoulder width)
RIDER_HEIGHT        =  500   # mm  (hip to top of helmet)
RIDER_DEPTH         =  400   # mm  (fore-aft torso depth)

# Required clearances
MIN_GROUND_CLEARANCE_MM = 280   # mm  for non-contact components
MIN_INTER_PART_GAP_MM   =  10   # mm  minimum gap between any two subsystems


# ---------------------------------------------------------------------------
# BOUNDING BOX DEFINITIONS
# ---------------------------------------------------------------------------

def _pod_ext():
    """Battery pod external half-dimensions."""
    wall = BATT_POD_WALL
    eL = BATT_POD_LENGTH + 2 * wall
    eW = BATT_POD_WIDTH  + 2 * wall
    eH = BATT_POD_HEIGHT + 2 * wall
    return eL, eW, eH


def build_aabbs():
    """
    Return dict of subsystem AABBs:
        name → (x_min, y_min, z_min, x_max, y_max, z_max)  in mm
    """
    wb2 = WHEELBASE / 2.0

    # — Chassis frame (bounding box of the whole space-frame) —
    chassis = (
        -wb2,
        -TRACK_FRONT / 2.0,
        GROUND_CLEARANCE,
         wb2,
         TRACK_FRONT / 2.0,
        GROUND_CLEARANCE + FRAME_HEIGHT,
    )

    # — Pontoon LEFT —
    p_r  = PONTOON_DIAMETER / 2.0
    p_L2 = PONTOON_LENGTH  / 2.0
    p_yL = PONTOON_OFFSET_Y
    p_z  = PONTOON_OFFSET_Z
    pontoon_left = (
        -p_L2,  p_yL - p_r,  p_z - p_r,
         p_L2,  p_yL + p_r,  p_z + p_r,
    )
    pontoon_right = (
        -p_L2, -(p_yL + p_r),  p_z - p_r,
         p_L2, -(p_yL - p_r),  p_z + p_r,
    )

    # — Battery pod —
    eL, eW, eH = _pod_ext()
    battery_pod = (
        -eL / 2.0,  -eW / 2.0,  BATT_POD_CLEARANCE_Z,
         eL / 2.0,   eW / 2.0,  BATT_POD_CLEARANCE_Z + eH,
    )

    # — Front tires (both, as combined envelope) —
    t_r  = TIRE_DIAMETER / 2.0
    t_w2 = TIRE_WIDTH    / 2.0
    front_tires = (
        wb2 - t_r,  -(TRACK_FRONT / 2.0 + t_w2),  0,
        wb2 + t_r,   (TRACK_FRONT / 2.0 + t_w2),   TIRE_DIAMETER,
    )

    # — Rear tires (both, combined envelope) —
    rear_tires = (
        -wb2 - t_r,  -(TRACK_REAR / 2.0 + t_w2),  0,
        -wb2 + t_r,   (TRACK_REAR / 2.0 + t_w2),   TIRE_DIAMETER,
    )

    # — Rider envelope —
    rx0 = RIDER_HIP_X - RIDER_DEPTH / 2.0
    rx1 = RIDER_HIP_X + RIDER_DEPTH / 2.0
    ry0 = -RIDER_WIDTH / 2.0
    ry1 =  RIDER_WIDTH / 2.0
    rz0 =  RIDER_HIP_Z
    rz1 =  RIDER_HIP_Z + RIDER_HEIGHT
    rider = (rx0, ry0, rz0, rx1, ry1, rz1)

    return {
        "Chassis Frame":     chassis,
        "Pontoon Left":      pontoon_left,
        "Pontoon Right":     pontoon_right,
        "Battery Pod":       battery_pod,
        "Front Tires":       front_tires,
        "Rear Tires":        rear_tires,
        "Rider Envelope":    rider,
    }


# ---------------------------------------------------------------------------
# CHECK FUNCTIONS
# ---------------------------------------------------------------------------

def aabb_overlap(a, b):
    """
    Return True if two AABBs overlap (i.e. they intersect in all three axes).
    Touching edges (gap = 0) counts as overlap.
    """
    ax0, ay0, az0, ax1, ay1, az1 = a
    bx0, by0, bz0, bx1, by1, bz1 = b
    return (ax0 < bx1 and ax1 > bx0 and
            ay0 < by1 and ay1 > by0 and
            az0 < bz1 and az1 > bz0)


def aabb_gap(a, b):
    """
    Return the minimum gap between two AABBs (negative = penetration depth).
    Positive = separation distance on the closest axis.
    """
    ax0, ay0, az0, ax1, ay1, az1 = a
    bx0, by0, bz0, bx1, by1, bz1 = b

    # Per-axis signed gap: positive = separated, negative = overlapping
    if ax1 <= bx0: gx = bx0 - ax1
    elif bx1 <= ax0: gx = ax0 - bx1
    else: gx = -min(ax1 - bx0, bx1 - ax0)  # negative = overlapping

    if ay1 <= by0: gy = by0 - ay1
    elif by1 <= ay0: gy = ay0 - by1
    else: gy = -min(ay1 - by0, by1 - ay0)

    if az1 <= bz0: gz = bz0 - az1
    elif bz1 <= az0: gz = az0 - bz1
    else: gz = -min(az1 - bz0, bz1 - az0)

    # If any axis shows separation, the AABBs don't overlap; return the tightest gap.
    # If all axes show penetration (all negative), return the least-negative (shallowest).
    separations = [g for g in (gx, gy, gz) if g > 0]
    if separations:
        return min(separations)  # tightest clearance between the two boxes
    else:
        return max(gx, gy, gz)   # least-deep penetration axis


def ground_clearance_check(name, aabb):
    """Check that the bottom face of an AABB clears the ground."""
    z_min = aabb[2]
    passes = z_min >= MIN_GROUND_CLEARANCE_MM
    return passes, z_min


def run_check():
    aabbs = build_aabbs()
    names = list(aabbs.keys())
    boxes = list(aabbs.values())

    # Exempt from ground clearance check
    gc_exempt = {"Front Tires", "Rear Tires", "Rider Envelope"}

    all_pass = True

    print("=" * 70)
    print("DS2-Craft  |  Packaging Check  |  Revision A")
    print("=" * 70)

    # — Ground clearance —
    print("\n── GROUND CLEARANCE (min " + str(MIN_GROUND_CLEARANCE_MM) + " mm) ──────────────────────────────")
    print(f"  {'Subsystem':<25} {'Z_min':>8}  {'Required':>8}  Status")
    print("  " + "-" * 55)
    for name, aabb in aabbs.items():
        if name in gc_exempt:
            continue
        ok, z_min = ground_clearance_check(name, aabb)
        status = "✅ PASS" if ok else "❌ FAIL"
        if not ok:
            all_pass = False
        print(f"  {name:<25} {z_min:>7.0f}mm  {MIN_GROUND_CLEARANCE_MM:>7}mm  {status}")

    # Pairs that are EXPECTED to overlap because one is mounted inside/onto the other.
    # These are structural overlaps by design — they do not represent interference.
    EXPECTED_OVERLAPS = {
        frozenset({"Chassis Frame", "Battery Pod"}),    # pod is inside the chassis frame
        frozenset({"Chassis Frame", "Front Tires"}),    # tires are attached to chassis
        frozenset({"Chassis Frame", "Rear Tires"}),     # tires are attached to chassis
        frozenset({"Chassis Frame", "Rider Envelope"}), # rider sits on the chassis
        frozenset({"Chassis Frame", "Pontoon Left"}),   # pontoons are bolted to chassis rails
        frozenset({"Chassis Frame", "Pontoon Right"}),  # pontoons are bolted to chassis rails
    }

    # — AABB overlap matrix —
    print(f"\n── INTER-SUBSYSTEM CLEARANCE (min gap ≥ {MIN_INTER_PART_GAP_MM} mm) ─────────────────────")
    print("  (Only pairs with gap < 50 mm or overlapping are listed)")
    print("  (Pairs marked [BY DESIGN] are intentional structural overlaps)\n")
    any_unexp_overlap = False
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            gap = aabb_gap(boxes[i], boxes[j])
            if gap > 50:
                continue  # Plenty of room — skip
            pair = frozenset({names[i], names[j]})
            by_design = pair in EXPECTED_OVERLAPS
            overlaps = gap < 0
            tight    = 0 <= gap < MIN_INTER_PART_GAP_MM
            if overlaps and by_design:
                status = "ℹ️  BY DESIGN"
            elif overlaps:
                status = "❌ OVERLAP"
                all_pass = False
                any_unexp_overlap = True
            elif tight:
                status = "⚠️  TIGHT"
            else:
                status = "✅ OK"
            print(f"  {names[i]:<22} ↔ {names[j]:<22}  gap={gap:>7.1f} mm  {status}")

    if not any_unexp_overlap:
        print("\n  (No unexpected overlapping pairs found)")

    # — Verdict —
    print("\n── VERDICT ─────────────────────────────────────────────────────────")
    if all_pass:
        print("  ✅  PASS — All packaging checks passed.")
    else:
        print("  ❌  FAIL — Review flagged items above and adjust parameters.")

    print("\n── NOTES / ASSUMPTIONS ──────────────────────────────────────────────")
    print("  A1. All geometry represented as axis-aligned bounding boxes (AABB).")
    print("  A2. AABB is conservative — actual cylindrical pontoons are smaller.")
    print("  A3. Full Boolean interference check requires FreeCAD assembly (Rev B).")
    print("  A4. Rider envelope not checked against ground clearance.")
    print("  A5. Pontoon-tire AABB overlap (R-11): pontoons span full wheelbase and")
    print("      overlap the wheel envelope laterally.  Resolution options:")
    print("        (a) Shorten pontoons to X=±350 mm (clear of tire at X=±420 mm)")
    print("        (b) Route pontoon around tire with a taper/cutout at each end")
    print("        (c) Verify actual cylinder-to-cylinder clearance in FreeCAD (Rev B)")
    print("      Note: shortening pontoons will worsen the buoyancy deficit (R-01).")
    print("=" * 70)


if __name__ == "__main__":
    run_check()
