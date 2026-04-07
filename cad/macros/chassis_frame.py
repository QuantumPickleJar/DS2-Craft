# =============================================================================
# DS2-Craft  |  cad/macros/chassis_frame.py
# Revision A  —  Parametric Chassis Frame
# =============================================================================
# PURPOSE
# -------
# Generates the primary structural frame envelope as extruded/swept tube
# solids inside FreeCAD.  Run AFTER parameters.py.
#
# WHAT THIS REPRESENTS (real-world subsystem SYS-01)
# ---------------------------------------------------
# The chassis is a space-frame of round steel tubes (4130 CrMo or DOM mild
# steel).  In Rev A the geometry is an approximation: two longitudinal spine
# rails, front and rear cross-members, and diagonal gussets at the battery-
# pod region.  Exact gusset and bracket geometry is deferred to Rev B.
#
# COORDINATE SYSTEM
# -----------------
#   +X  = forward (toward front of vehicle)
#   +Y  = left (driver's perspective)
#   +Z  = up
#   Origin = mid-wheelbase, mid-track, at ground level
#
# ASSUMPTIONS
# -----------
# 1. Frame material is 4130 CrMo round tube, OD=FRAME_TUBE_OD, wall=FRAME_TUBE_WALL.
# 2. Spine rails run full wheelbase length at Y = ±(TRACK_REAR/2 - margin).
# 3. Front cross-member at X = +WHEELBASE/2.
# 4. Rear cross-member at X = -WHEELBASE/2.
# 5. Centre cross-member (battery pod mount) at X = 0.
# 6. All tubes modelled as solid cylinders in Rev A (hollow sweep in Rev B).
# 7. Ground clearance is applied: lowest tube at Z = GROUND_CLEARANCE.
# =============================================================================

import math

# ── Guard: only import FreeCAD when running inside FreeCAD ──────────────────
try:
    import FreeCAD as App          # type: ignore
    import Part                    # type: ignore
    import FreeCADGui as Gui       # type: ignore
    _IN_FREECAD = True
except ImportError:
    _IN_FREECAD = False

# ---------------------------------------------------------------------------
# PARAMETERS  (pulled from spreadsheet when in FreeCAD; literals otherwise)
# ---------------------------------------------------------------------------

def _param(doc, name, fallback):
    """Read a value from the DS2_Params spreadsheet, or return fallback."""
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
    """Return a dict of all parameters needed by this macro."""
    d = doc  # may be None outside FreeCAD
    return {
        "WHEELBASE":        _param(d, "WHEELBASE",        1400),
        "TRACK_FRONT":      _param(d, "TRACK_FRONT",       900),
        "TRACK_REAR":       _param(d, "TRACK_REAR",        800),
        "GROUND_CLEARANCE": _param(d, "GROUND_CLEARANCE",  280),
        "FRAME_HEIGHT":     _param(d, "FRAME_HEIGHT",      350),
        "FRAME_TUBE_OD":    _param(d, "FRAME_TUBE_OD",      50),
        "FRAME_TUBE_WALL":  _param(d, "FRAME_TUBE_WALL",     3),
    }


# ---------------------------------------------------------------------------
# GEOMETRY HELPERS
# ---------------------------------------------------------------------------

def make_tube_solid(p1, p2, radius_mm):
    """
    Create a cylindrical solid between two 3-D points.
    (Rev A approximation — not a hollow tube sweep.)

    Parameters
    ----------
    p1, p2 : tuple (x, y, z) in mm
    radius_mm : outer radius in mm

    Returns
    -------
    Part.Shape  (cylinder approximating a tube segment)
    """
    if not _IN_FREECAD:
        return None
    vec1 = App.Vector(*p1)
    vec2 = App.Vector(*p2)
    axis = vec2 - vec1
    length = axis.Length
    if length < 1e-6:
        raise ValueError(f"Degenerate tube: p1={p1}, p2={p2}")
    cyl = Part.makeCylinder(radius_mm, length, vec1, axis.normalize())
    return cyl


def make_frame_geometry(p):
    """
    Build the chassis frame Part shapes from parameter dict p.

    Returns a list of (label, shape) tuples.
    """
    wb  = p["WHEELBASE"]
    tf  = p["TRACK_FRONT"]
    tr  = p["TRACK_REAR"]
    gc  = p["GROUND_CLEARANCE"]
    fh  = p["FRAME_HEIGHT"]
    od  = p["FRAME_TUBE_OD"]
    r   = od / 2.0  # tube outer radius

    # Rail height: spine sits at mid-frame-height above ground
    z_rail = gc + fh / 2.0

    # ── Longitudinal spine rails (left and right) ────────────────────────────
    # Rails run the full wheelbase; Y offset = half rear track
    y_rail = tr / 2.0

    rail_left_front  = ( wb / 2.0,  y_rail, z_rail)
    rail_left_rear   = (-wb / 2.0,  y_rail, z_rail)
    rail_right_front = ( wb / 2.0, -y_rail, z_rail)
    rail_right_rear  = (-wb / 2.0, -y_rail, z_rail)

    # ── Cross-members ────────────────────────────────────────────────────────
    # Front cross-member spans track_front at the front axle X
    front_xm_left  = ( wb / 2.0,  tf / 2.0, z_rail)
    front_xm_right = ( wb / 2.0, -tf / 2.0, z_rail)

    # Rear cross-member spans track_rear at the rear axle X
    rear_xm_left   = (-wb / 2.0,  tr / 2.0, z_rail)
    rear_xm_right  = (-wb / 2.0, -tr / 2.0, z_rail)

    # Centre cross-member at X=0 (battery pod forward mount)
    centre_xm_left  = (0,  tr / 2.0, z_rail)
    centre_xm_right = (0, -tr / 2.0, z_rail)

    # ── Lower rockers (ground-clearance level, full wheelbase) ───────────────
    z_low = gc + r  # just above ground clearance line
    rocker_left_front  = ( wb / 2.0,  y_rail, z_low)
    rocker_left_rear   = (-wb / 2.0,  y_rail, z_low)
    rocker_right_front = ( wb / 2.0, -y_rail, z_low)
    rocker_right_rear  = (-wb / 2.0, -y_rail, z_low)

    # ── Vertical uprights (connect rocker to rail at each corner) ───────────
    upright_fl_bot = ( wb / 2.0,  y_rail, z_low)
    upright_fl_top = ( wb / 2.0,  y_rail, z_rail)
    upright_fr_bot = ( wb / 2.0, -y_rail, z_low)
    upright_fr_top = ( wb / 2.0, -y_rail, z_rail)
    upright_rl_bot = (-wb / 2.0,  y_rail, z_low)
    upright_rl_top = (-wb / 2.0,  y_rail, z_rail)
    upright_rr_bot = (-wb / 2.0, -y_rail, z_low)
    upright_rr_top = (-wb / 2.0, -y_rail, z_rail)

    members = [
        # Spine rails
        ("rail_left",         rail_left_front,   rail_left_rear),
        ("rail_right",        rail_right_front,  rail_right_rear),
        # Cross-members
        ("xm_front",          front_xm_left,     front_xm_right),
        ("xm_rear",           rear_xm_left,      rear_xm_right),
        ("xm_centre",         centre_xm_left,    centre_xm_right),
        # Lower rockers
        ("rocker_left",       rocker_left_front, rocker_left_rear),
        ("rocker_right",      rocker_right_front,rocker_right_rear),
        # Vertical uprights
        ("upright_front_left",  upright_fl_bot,  upright_fl_top),
        ("upright_front_right", upright_fr_bot,  upright_fr_top),
        ("upright_rear_left",   upright_rl_bot,  upright_rl_top),
        ("upright_rear_right",  upright_rr_bot,  upright_rr_top),
    ]

    return members, r


# ---------------------------------------------------------------------------
# FREECAD ENTRY POINT
# ---------------------------------------------------------------------------

def build_chassis():
    """Main macro entry — builds and adds chassis geometry to the active document."""
    doc = App.ActiveDocument
    if doc is None:
        doc = App.newDocument("DS2_Craft_RevA")

    p = load_params(doc)
    members, radius = make_frame_geometry(p)

    shapes = []
    for label, p1, p2 in members:
        shape = make_tube_solid(p1, p2, radius)
        if shape is not None:
            shapes.append(shape)

    if shapes:
        compound = Part.makeCompound(shapes)
        obj = doc.addObject("Part::Feature", "Chassis_Frame_RevA")
        obj.Shape = compound
        obj.Label = "Chassis Frame (Rev A)"

    doc.recompute()
    if _IN_FREECAD and hasattr(Gui, "SendMsgToActiveView"):
        Gui.SendMsgToActiveView("ViewFit")
    App.Console.PrintMessage(
        f"Chassis frame built: {len(members)} members, tube OD={p['FRAME_TUBE_OD']} mm.\n"
    )


# ---------------------------------------------------------------------------
# STANDALONE TEST  (run outside FreeCAD — prints expected member geometry)
# ---------------------------------------------------------------------------

def _test():
    """Print member endpoints for inspection without FreeCAD."""
    p = load_params(None)
    members, radius = make_frame_geometry(p)
    print(f"Chassis frame — {len(members)} members, tube radius = {radius} mm\n")
    print(f"  {'Member':<28} {'P1':^36} {'P2':^36}")
    print("  " + "-" * 100)
    for label, p1, p2 in members:
        length = math.sqrt(sum((b - a) ** 2 for a, b in zip(p1, p2)))
        print(f"  {label:<28} {str(p1):^36} {str(p2):^36}  L={length:.1f} mm")


if __name__ == "__main__":
    _test()
else:
    # Running inside FreeCAD
    build_chassis()
