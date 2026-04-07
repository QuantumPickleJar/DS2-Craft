# =============================================================================
# DS2-Craft  |  cad/macros/flotation_pods.py
# Revision A  —  Side Flotation Pontoons
# =============================================================================
# PURPOSE
# -------
# Generates the two cylindrical side pontoons that provide buoyancy reserve.
# Run AFTER parameters.py and chassis_frame.py.
#
# WHAT THIS REPRESENTS (real-world subsystem SYS-02)
# ---------------------------------------------------
# Two horizontal cylinder pods, one on each side of the vehicle, mounted to
# the lower chassis rails.  Each pod is an aluminium shell filled with
# closed-cell polyurethane foam.  The foam fill provides residual buoyancy
# even if the shell is breached.
#
# Water-entry seams are sealed with marine-grade butyl tape + sealant and
# closed-head fasteners (per SYS-10 design rules).
#
# COORDINATE SYSTEM
# -----------------
# Same as chassis_frame.py:
#   +X = forward,  +Y = left,  +Z = up
#   Origin at mid-wheelbase / mid-track / ground level.
#
# ASSUMPTIONS
# -----------
# 1. Each pontoon is modelled as a plain cylinder (closed ends) in Rev A.
#    End caps, mounting flanges, and drain plugs are Rev B detail.
# 2. Pontoon centreline is horizontal (no rake angle in Rev A).
# 3. Pontoon is centred longitudinally on the vehicle (X = 0, ±PONTOON_LENGTH/2).
# 4. Foam fill fraction = FOAM_FILL_FRACTION of internal volume.
#    Internal diameter = PONTOON_DIAMETER − 2×PONTOON_WALL.
# 5. Pontoon buoyancy contribution calculated in simulation/buoyancy/ scripts.
# =============================================================================

import math

try:
    import FreeCAD as App   # type: ignore
    import Part             # type: ignore
    import FreeCADGui as Gui# type: ignore
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
        "PONTOON_LENGTH":   _param(d, "PONTOON_LENGTH",   1400),
        "PONTOON_DIAMETER": _param(d, "PONTOON_DIAMETER",  220),
        "PONTOON_WALL":     _param(d, "PONTOON_WALL",        4),
        "PONTOON_OFFSET_Y": _param(d, "PONTOON_OFFSET_Y",  450),
        "PONTOON_OFFSET_Z": _param(d, "PONTOON_OFFSET_Z",  390),  # GC(280) + r(110)
    }


# ---------------------------------------------------------------------------
# DERIVED GEOMETRY
# ---------------------------------------------------------------------------

def pontoon_properties(p):
    """
    Return geometric properties of one pontoon.

    Returns dict with:
        outer_radius, inner_radius, shell_volume_mm3,
        gross_volume_mm3, buoyant_volume_mm3 (water-displacing volume)
    """
    r_outer = p["PONTOON_DIAMETER"] / 2.0
    r_inner = r_outer - p["PONTOON_WALL"]
    L       = p["PONTOON_LENGTH"]

    gross_vol = math.pi * r_outer ** 2 * L          # mm³  (full cylinder)
    shell_vol = math.pi * (r_outer**2 - r_inner**2) * L  # mm³  (wall only)
    inner_vol = math.pi * r_inner ** 2 * L          # mm³  (interior cavity)

    return {
        "outer_radius":       r_outer,
        "inner_radius":       r_inner,
        "length":             L,
        "gross_volume_mm3":   gross_vol,
        "shell_volume_mm3":   shell_vol,
        "inner_volume_mm3":   inner_vol,
        # Entire exterior volume displaces water when submerged
        "buoyant_volume_mm3": gross_vol,
    }


def make_pontoon_shape(p, side="left"):
    """
    Create a single pontoon solid.

    side : "left"  →  +Y side
           "right" →  −Y side

    Returns Part.Shape or None if not in FreeCAD.
    """
    if not _IN_FREECAD:
        return None

    r_outer = p["PONTOON_DIAMETER"] / 2.0
    L       = p["PONTOON_LENGTH"]
    y_off   = p["PONTOON_OFFSET_Y"] * (1 if side == "left" else -1)
    z_off   = p["PONTOON_OFFSET_Z"]

    # Pontoon runs along X-axis, centred at X=0
    x_start = -L / 2.0
    base_pt = App.Vector(x_start, y_off, z_off)
    axis    = App.Vector(1, 0, 0)  # along +X

    cyl = Part.makeCylinder(r_outer, L, base_pt, axis)
    return cyl


# ---------------------------------------------------------------------------
# FREECAD ENTRY POINT
# ---------------------------------------------------------------------------

def build_pontoons():
    doc = App.ActiveDocument
    if doc is None:
        doc = App.newDocument("DS2_Craft_RevA")

    p = load_params(doc)
    props = pontoon_properties(p)

    shapes = []
    for side in ("left", "right"):
        shape = make_pontoon_shape(p, side=side)
        if shape is not None:
            shapes.append(shape)
            obj = doc.addObject("Part::Feature", f"Pontoon_{side.capitalize()}_RevA")
            obj.Shape = shape
            obj.Label = f"Flotation Pontoon — {side.capitalize()} (Rev A)"

    doc.recompute()
    if _IN_FREECAD and hasattr(Gui, "SendMsgToActiveView"):
        Gui.SendMsgToActiveView("ViewFit")

    vol_L = props["buoyant_volume_mm3"] * 2 / 1e6  # both pontoons in litres
    App.Console.PrintMessage(
        f"Pontoons built: OD={p['PONTOON_DIAMETER']} mm, "
        f"L={p['PONTOON_LENGTH']} mm, "
        f"total buoyant volume = {vol_L:.1f} L.\n"
    )


# ---------------------------------------------------------------------------
# STANDALONE TEST
# ---------------------------------------------------------------------------

def _test():
    p = load_params(None)
    props = pontoon_properties(p)
    print("Flotation Pontoon Properties (single pontoon)")
    print("-" * 48)
    for k, v in props.items():
        unit = "mm³" if "volume" in k else ("mm" if "radius" in k or k == "length" else "")
        if "volume" in k:
            print(f"  {k:<28} {v / 1e6:>10.3f} L   ({v:,.0f} mm³)")
        else:
            print(f"  {k:<28} {v:>10.1f} {unit}")

    vol_both_L = props["buoyant_volume_mm3"] * 2 / 1e6
    mass_water_displaced_kg = vol_both_L * 1.0  # 1 kg/L for fresh water
    print(f"\n  Both pontoons total buoyant volume : {vol_both_L:.2f} L")
    print(f"  Mass of water displaced (fresh)    : {mass_water_displaced_kg:.2f} kg")
    print(
        f"  Note: GVW ~255 kg → at least "
        f"{255 / mass_water_displaced_kg * 100:.0f}% of pontoon volume needed to float"
    )


if __name__ == "__main__":
    _test()
else:
    build_pontoons()
