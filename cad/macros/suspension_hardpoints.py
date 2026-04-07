# =============================================================================
# DS2-Craft  |  cad/macros/suspension_hardpoints.py
# Revision A  —  Suspension Hard-Point Layout
# =============================================================================
# PURPOSE
# -------
# Places named datum points (vertices / datum objects) at the theoretical
# suspension pickup locations for all four corners.  Run AFTER chassis_frame.py.
#
# WHAT THIS REPRESENTS (real-world subsystem SYS-06)
# ---------------------------------------------------
# Suspension hard-points define where control arms, spring-damper units,
# and steering knuckles attach to the chassis and to the wheel hubs.
#
# In Rev A the model places:
#   • Upper control arm inboard pickup (chassis side) — front & rear
#   • Lower control arm inboard pickup (chassis side) — front & rear
#   • Wheel-center point (design ride-height, nominal load)
#   • Spring-damper top mount location
#
# Geometry is intentionally approximate — Ackermann and kinematics analysis
# is deferred to Rev B (flagged as R-09 in the risk list).
#
# COORDINATE SYSTEM
# -----------------
# Same as chassis_frame.py.
#
# ASSUMPTIONS
# -----------
# 1. All four corners use a double-wishbone geometry (Rev A placeholder).
# 2. Upper arm inboard pickup is at rail height (FRAME_HEIGHT/2 + GC).
# 3. Lower arm inboard pickup is at rocker height (GC + FRAME_TUBE_OD/2).
# 4. Wheel centre X: front = +WHEELBASE/2, rear = -WHEELBASE/2.
# 5. Wheel centre Y: ±TRACK_FRONT/2 (front) or ±TRACK_REAR/2 (rear).
# 6. Wheel centre Z: TIRE_DIAMETER/2 (ground = 0).
# 7. Spring-damper top mount is at upper arm inboard pickup X, Y midpoint.
# 8. Control arm lengths are NOT derived in Rev A — they are placeholder
#    offsets of 150 mm (inboard) toward vehicle centreline.
# =============================================================================

import math

try:
    import FreeCAD as App     # type: ignore
    import Part               # type: ignore
    import FreeCADGui as Gui  # type: ignore
    _IN_FREECAD = True
except ImportError:
    _IN_FREECAD = False


# ---------------------------------------------------------------------------
# PARAMETERS
# ---------------------------------------------------------------------------

def _param(doc, name, fallback):
    if not _IN_FREECAD:
        return fallback
    sheet = doc.getObject("DS2_Params")
    if sheet is None:
        return fallback
    try:
        return sheet.get(name)
    except Exception:
        return fallback


def load_params(doc=None):
    d = doc
    return {
        "WHEELBASE":        _param(d, "WHEELBASE",        1400),
        "TRACK_FRONT":      _param(d, "TRACK_FRONT",       900),
        "TRACK_REAR":       _param(d, "TRACK_REAR",        800),
        "GROUND_CLEARANCE": _param(d, "GROUND_CLEARANCE",  280),
        "FRAME_HEIGHT":     _param(d, "FRAME_HEIGHT",      350),
        "FRAME_TUBE_OD":    _param(d, "FRAME_TUBE_OD",      50),
        "TIRE_DIAMETER":    _param(d, "TIRE_DIAMETER",     560),
        "SUSP_TRAVEL_UP":   _param(d, "SUSP_TRAVEL_UP",    80),
        "SUSP_TRAVEL_DOWN": _param(d, "SUSP_TRAVEL_DOWN",  60),
    }


# ---------------------------------------------------------------------------
# HARD-POINT CALCULATION
# ---------------------------------------------------------------------------

# Inboard pickup offset from wheel-centre Y toward vehicle CL
_INBOARD_OFFSET = 150  # mm — Rev A placeholder; derived in Rev B


def calc_hardpoints(p):
    """
    Return a dict mapping hard-point label → (x, y, z) in mm.

    Corners:  FL = front-left, FR = front-right, RL = rear-left, RR = rear-right
    """
    wb  = p["WHEELBASE"]
    tf  = p["TRACK_FRONT"]
    tr  = p["TRACK_REAR"]
    gc  = p["GROUND_CLEARANCE"]
    fh  = p["FRAME_HEIGHT"]
    od  = p["FRAME_TUBE_OD"]
    td  = p["TIRE_DIAMETER"]

    wheel_z   = td / 2.0                       # wheel centre height at design ride
    lower_z   = gc + od / 2.0                  # lower rocker centreline
    upper_z   = gc + fh / 2.0                  # main rail centreline (approx upper arm)
    damper_z  = gc + fh * 0.85                 # spring-damper top mount (~85% of frame height)

    corners = {
        "FL": ( wb / 2.0,  tf / 2.0),
        "FR": ( wb / 2.0, -tf / 2.0),
        "RL": (-wb / 2.0,  tr / 2.0),
        "RR": (-wb / 2.0, -tr / 2.0),
    }

    hpts = {}
    for name, (cx, cy) in corners.items():
        sign_y = 1 if cy > 0 else -1
        inboard_y = cy - sign_y * _INBOARD_OFFSET

        hpts[f"{name}_wheel_center"] = (cx,          cy,         wheel_z)
        hpts[f"{name}_lower_inboard"] = (cx,          inboard_y,  lower_z)
        hpts[f"{name}_upper_inboard"] = (cx,          inboard_y,  upper_z)
        hpts[f"{name}_damper_top"]    = (cx,          inboard_y,  damper_z)

    return hpts


# ---------------------------------------------------------------------------
# FREECAD ENTRY POINT
# ---------------------------------------------------------------------------

def _make_point_vertex(x, y, z):
    """Create a small sphere to mark a hard-point location."""
    if not _IN_FREECAD:
        return None
    return Part.makeSphere(8, App.Vector(x, y, z))  # 8 mm radius marker sphere


def build_suspension_hardpoints():
    doc = App.ActiveDocument
    if doc is None:
        doc = App.newDocument("DS2_Craft_RevA")

    p  = load_params(doc)
    hpts = calc_hardpoints(p)

    shapes = []
    for label, (x, y, z) in hpts.items():
        s = _make_point_vertex(x, y, z)
        if s is not None:
            shapes.append(s)

    if shapes:
        compound = Part.makeCompound(shapes)
        obj = doc.addObject("Part::Feature", "Suspension_Hardpoints_RevA")
        obj.Shape = compound
        obj.Label = "Suspension Hard-Points (Rev A)"

    doc.recompute()
    if _IN_FREECAD and hasattr(Gui, "SendMsgToActiveView"):
        Gui.SendMsgToActiveView("ViewFit")

    App.Console.PrintMessage(
        f"Suspension hard-points placed: {len(hpts)} points.\n"
    )


# ---------------------------------------------------------------------------
# STANDALONE TEST
# ---------------------------------------------------------------------------

def _test():
    p = load_params(None)
    hpts = calc_hardpoints(p)
    print(f"Suspension Hard-Points — Revision A  ({len(hpts)} points)\n")
    print(f"  {'Label':<30} {'X':>8}  {'Y':>8}  {'Z':>8}  (mm)")
    print("  " + "-" * 62)
    for label, (x, y, z) in sorted(hpts.items()):
        print(f"  {label:<30} {x:>8.1f}  {y:>8.1f}  {z:>8.1f}")

    wheel_z  = p["TIRE_DIAMETER"] / 2.0
    travel_u = p["SUSP_TRAVEL_UP"]
    travel_d = p["SUSP_TRAVEL_DOWN"]
    print(f"\n  Design ride-height wheel Z : {wheel_z:.1f} mm")
    print(f"  Full bump   wheel Z        : {wheel_z - travel_u:.1f} mm")
    print(f"  Full droop  wheel Z        : {wheel_z + travel_d:.1f} mm")
    print(f"  (Inboard offset placeholder: {_INBOARD_OFFSET} mm — revise in Rev B)")


if __name__ == "__main__":
    _test()
else:
    build_suspension_hardpoints()
