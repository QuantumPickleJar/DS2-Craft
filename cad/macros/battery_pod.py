# =============================================================================
# DS2-Craft  |  cad/macros/battery_pod.py
# Revision A  —  Sealed Battery & Electronics Enclosure
# =============================================================================
# PURPOSE
# -------
# Generates the sealed central battery pod envelope as a box solid.
# Run AFTER parameters.py.
#
# WHAT THIS REPRESENTS (real-world subsystem SYS-03)
# ---------------------------------------------------
# A welded aluminium (6061-T6) enclosure that houses:
#   • 72 V LiFePO₄ battery pack (target 40 Ah)
#   • Battery management system (BMS)
#   • Main contactor and fuse
#   • Primary motor controller / inverter
#   • 12 V auxiliary DC-DC converter
#
# Sealing approach (SYS-10 rules applied here):
#   • IP67 target for the enclosure itself
#   • All cable penetrations through bulkhead connectors (IP68 rated)
#   • Pressure-equalising Gore-Tex vent to prevent vacuum lock
#   • No pooling geometry inside — internal floor is angled to drain
#     toward the lowest bulkhead connector location
#
# COORDINATE SYSTEM
# -----------------
# Same as chassis_frame.py.  Pod is centred on vehicle X/Y centreline.
#
# ASSUMPTIONS
# -----------
# 1. Pod modelled as a solid rectangular box in Rev A (wall modelled as offset).
# 2. Pod is mounted at BATT_POD_CLEARANCE_Z above ground (bottom face).
# 3. Pod centroid is at X = 0 (mid-wheelbase) for optimal mass distribution.
# 4. External dimensions = internal cavity + 2 × BATT_POD_WALL on each face.
# 5. Connector and lid detail deferred to Rev B.
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
        "BATT_POD_LENGTH":      _param(d, "BATT_POD_LENGTH",      620),
        "BATT_POD_WIDTH":       _param(d, "BATT_POD_WIDTH",        280),
        "BATT_POD_HEIGHT":      _param(d, "BATT_POD_HEIGHT",       180),
        "BATT_POD_WALL":        _param(d, "BATT_POD_WALL",           5),
        "BATT_POD_CLEARANCE_Z": _param(d, "BATT_POD_CLEARANCE_Z",  320),
        "VOLTAGE_NOMINAL":      _param(d, "VOLTAGE_NOMINAL",        72),
        "CAPACITY_NOMINAL":     _param(d, "CAPACITY_NOMINAL",       40),
    }


# ---------------------------------------------------------------------------
# DERIVED GEOMETRY
# ---------------------------------------------------------------------------

def pod_external_dims(p):
    """
    Return external (envelope) dimensions of the battery pod.

    Internal cavity + 2 walls on each side.
    """
    wall = p["BATT_POD_WALL"]
    ext_L = p["BATT_POD_LENGTH"] + 2 * wall
    ext_W = p["BATT_POD_WIDTH"]  + 2 * wall
    ext_H = p["BATT_POD_HEIGHT"] + 2 * wall
    return ext_L, ext_W, ext_H


def pod_origin(p):
    """
    Return the (x, y, z) position of the pod's bottom-front-left corner
    so the pod is centred on X=0 and Y=0.
    """
    ext_L, ext_W, ext_H = pod_external_dims(p)
    x0 = -ext_L / 2.0
    y0 = -ext_W / 2.0
    z0 = p["BATT_POD_CLEARANCE_Z"]
    return x0, y0, z0


def pack_energy_kwh(p):
    """Nominal pack energy in kWh."""
    return p["VOLTAGE_NOMINAL"] * p["CAPACITY_NOMINAL"] / 1000.0


# ---------------------------------------------------------------------------
# FREECAD GEOMETRY
# ---------------------------------------------------------------------------

def make_pod_shape(p):
    """Build the battery pod as a hollow box (outer solid minus inner cavity)."""
    if not _IN_FREECAD:
        return None

    ext_L, ext_W, ext_H = pod_external_dims(p)
    x0, y0, z0 = pod_origin(p)

    # Outer box
    outer = Part.makeBox(ext_L, ext_W, ext_H, App.Vector(x0, y0, z0))

    # Inner cavity (subtract to create hollow shell)
    wall = p["BATT_POD_WALL"]
    int_L = p["BATT_POD_LENGTH"]
    int_W = p["BATT_POD_WIDTH"]
    int_H = p["BATT_POD_HEIGHT"]
    inner = Part.makeBox(
        int_L, int_W, int_H,
        App.Vector(x0 + wall, y0 + wall, z0 + wall)
    )

    pod = outer.cut(inner)
    return pod


# ---------------------------------------------------------------------------
# FREECAD ENTRY POINT
# ---------------------------------------------------------------------------

def build_battery_pod():
    doc = App.ActiveDocument
    if doc is None:
        doc = App.newDocument("DS2_Craft_RevA")

    p = load_params(doc)
    shape = make_pod_shape(p)

    if shape is not None:
        obj = doc.addObject("Part::Feature", "Battery_Pod_RevA")
        obj.Shape = shape
        obj.Label = "Battery & Electronics Pod (Rev A)"

    doc.recompute()
    if _IN_FREECAD and hasattr(Gui, "SendMsgToActiveView"):
        Gui.SendMsgToActiveView("ViewFit")

    ext_L, ext_W, ext_H = pod_external_dims(p)
    e_kwh = pack_energy_kwh(p)
    App.Console.PrintMessage(
        f"Battery pod built: {ext_L:.0f} × {ext_W:.0f} × {ext_H:.0f} mm  "
        f"(wall {p['BATT_POD_WALL']} mm), "
        f"pack energy = {e_kwh:.1f} kWh, "
        f"bottom at Z = {p['BATT_POD_CLEARANCE_Z']} mm.\n"
    )


# ---------------------------------------------------------------------------
# STANDALONE TEST
# ---------------------------------------------------------------------------

def _test():
    p = load_params(None)
    ext_L, ext_W, ext_H = pod_external_dims(p)
    x0, y0, z0 = pod_origin(p)
    vol_ext  = ext_L * ext_W * ext_H / 1e6   # mm³ ÷ 1e6 = litres
    vol_int  = p["BATT_POD_LENGTH"] * p["BATT_POD_WIDTH"] * p["BATT_POD_HEIGHT"] / 1e6
    e_kwh    = pack_energy_kwh(p)

    print("Battery Pod — Revision A")
    print("-" * 50)
    print(f"  Internal cavity   : {p['BATT_POD_LENGTH']} × {p['BATT_POD_WIDTH']} × {p['BATT_POD_HEIGHT']} mm")
    print(f"  External envelope : {ext_L:.0f} × {ext_W:.0f} × {ext_H:.0f} mm")
    print(f"  Wall thickness    : {p['BATT_POD_WALL']} mm")
    print(f"  Bottom face Z     : {z0:.0f} mm above ground")
    print(f"  Top face Z        : {z0 + ext_H:.0f} mm above ground")
    print(f"  Pod CL (X, Y)     : (0, 0)  — centred on vehicle")
    print(f"  External volume   : {vol_ext:.2f} L")
    print(f"  Cavity volume     : {vol_int:.2f} L")
    print(f"  Pack energy       : {e_kwh:.2f} kWh  "
          f"({p['VOLTAGE_NOMINAL']} V × {p['CAPACITY_NOMINAL']} Ah)")


if __name__ == "__main__":
    _test()
else:
    build_battery_pod()
