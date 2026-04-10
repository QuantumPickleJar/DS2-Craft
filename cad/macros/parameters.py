# =============================================================================
# DS2-Craft  |  cad/macros/parameters.py
# Revision A  —  Master Parameter Table
# =============================================================================
# PURPOSE
# -------
# This file is the single authoritative source for all named CAD parameters.
# Run this macro FIRST inside FreeCAD before running any geometry macro.
# The FreeCAD spreadsheet "DS2_Params" is created (or updated) with every
# named value so that subsequent Part/PartDesign features can reference them
# via the spreadsheet alias, e.g.  =DS2_Params.WHEELBASE
#
# HOW TO USE
# ----------
# 1. Open FreeCAD (any document, or a new empty one).
# 2. Macro → Macros… → select this file → Execute.
# 3. A spreadsheet named "DS2_Params" appears in the model tree.
# 4. Re-run any time you change a value here — the spreadsheet refreshes.
#
# ASSUMPTIONS
# -----------
# All linear dimensions are in MILLIMETRES (mm).
# All masses are in KILOGRAMS (kg).
# All angles are in DEGREES (°).
# =============================================================================

try:
    import FreeCAD as App  # type: ignore  (FreeCAD runtime import)
    _IN_FREECAD = True
except ImportError:
    App = None  # running outside FreeCAD — standalone test mode
    _IN_FREECAD = False

# ---------------------------------------------------------------------------
# HELPER — create or refresh the parameter spreadsheet
# ---------------------------------------------------------------------------

def _get_or_create_spreadsheet(doc, name="DS2_Params"):
    """Return the named spreadsheet, creating it if it does not exist."""
    obj = doc.getObject(name)
    if obj is None:
        obj = doc.addObject("Spreadsheet::Sheet", name)
        obj.Label = name
    return obj


def _set(sheet, row, label, value, unit="", notes=""):
    """Write one parameter row into the spreadsheet and set an alias."""
    sheet.set(f"A{row}", label)
    sheet.set(f"B{row}", str(value))
    sheet.set(f"C{row}", unit)
    sheet.set(f"D{row}", notes)
    try:
        sheet.setAlias(f"B{row}", label)
    except Exception:
        pass  # alias already exists or name conflict — safe to ignore


# ---------------------------------------------------------------------------
# PARAMETER DEFINITIONS  (edit values here)
# ---------------------------------------------------------------------------

# ── Chassis & Envelope ──────────────────────────────────────────────────────
WHEELBASE           = 1400   # mm  | Front axle to rear axle CL
TRACK_FRONT         =  900   # mm  | Front wheel CL to CL
TRACK_REAR          =  800   # mm  | Rear wheel CL to CL
GROUND_CLEARANCE    =  280   # mm  | Bottom of main frame to ground
FRAME_HEIGHT        =  350   # mm  | Ground to top of main rail
OVERALL_LENGTH      = 2050   # mm  | Bumper to bumper estimate
OVERALL_WIDTH       = 1100   # mm  | Pontoon tip to pontoon tip
OVERALL_HEIGHT      = 1200   # mm  | Ground to top of rider envelope
FRAME_TUBE_OD       =   50   # mm  | Main structural tube outer diameter
FRAME_TUBE_WALL     =    3   # mm  | Main structural tube wall thickness

# ── Flotation ───────────────────────────────────────────────────────────────
PONTOON_LENGTH      = 1400   # mm  | Full pontoon tube length
PONTOON_DIAMETER    =  220   # mm  | Outer diameter of cylindrical pontoon
PONTOON_WALL        =    4   # mm  | Structural shell wall thickness
PONTOON_OFFSET_Y    =  450   # mm  | Lateral offset from vehicle CL
PONTOON_OFFSET_Z    =  390   # mm  | Height of pontoon centroid above ground
                               #       = GROUND_CLEARANCE (280) + PONTOON_DIAMETER/2 (110)
FOAM_FILL_FRACTION  = 0.85   # —   | Fraction of volume filled with closed-cell foam

# ── Battery & Electronics Pod ───────────────────────────────────────────────
BATT_POD_LENGTH     =  620   # mm  | Internal cavity length
BATT_POD_WIDTH      =  280   # mm  | Internal cavity width
BATT_POD_HEIGHT     =  180   # mm  | Internal cavity height
BATT_POD_WALL       =    5   # mm  | Enclosure wall thickness
BATT_POD_CLEARANCE_Z=  320   # mm  | Bottom of pod above ground
VOLTAGE_NOMINAL     =   72   # V   | System bus voltage
CAPACITY_NOMINAL    =   40   # Ah  | Target pack capacity

# ── Drivetrain ───────────────────────────────────────────────────────────────
MOTOR_PEAK_POWER    = 5000   # W   | Single rear motor peak power
MOTOR_CONT_POWER    = 3000   # W   | Single rear motor continuous rating
GEAR_RATIO          =  8.5   # —   | Motor-to-wheel speed reduction
MOTOR_MOUNT_OFFSET_X= -620   # mm  | From vehicle mid-point toward rear

# ── Suspension Hard-Points ──────────────────────────────────────────────────
SUSP_TRAVEL_UP      =   80   # mm  | Bump travel from design-ride-height
SUSP_TRAVEL_DOWN    =   60   # mm  | Droop travel from design-ride-height
FRONT_SPRING_RATE   =   22   # N/mm| Assumption — revise after mass calc
REAR_SPRING_RATE    =   28   # N/mm| Assumption — revise after mass calc

# ── Wheels & Tires ──────────────────────────────────────────────────────────
TIRE_DIAMETER       =  560   # mm  | Overall tire diameter (~22-inch class)
TIRE_WIDTH          =  250   # mm  | Tread section width
RIM_DIAMETER        =  305   # mm  | 12-inch beadlock rim
RIM_WIDTH           =  178   # mm  | 7-inch rim width (bead to bead)

# ── Mass Budget (reference values) ──────────────────────────────────────────
MASS_CHASSIS        =   28   # kg  | Frame assembly
MASS_BATTERY_POD    =   38   # kg  | Pack + enclosure
MASS_MOTOR          =   12   # kg  | Motor + controller
MASS_SUSPENSION     =   18   # kg  | All four corners
MASS_WHEELS         =   16   # kg  | Four wheels + tires
MASS_PONTOONS       =   10   # kg  | Both pontoons
MASS_BODY           =   10   # kg  | Fairings estimate
MASS_RIDER_INTERFACE=    6   # kg  | Seat, bars, pegs
MASS_WIRING         =    4   # kg  | Harness + connectors
RIDER_MASS          =  113   # kg  | Target rider (250 lb)


# ---------------------------------------------------------------------------
# SPREADSHEET WRITER — runs when this macro is executed inside FreeCAD
# ---------------------------------------------------------------------------

def write_parameters():
    doc = App.ActiveDocument
    if doc is None:
        doc = App.newDocument("DS2_Craft_RevA")

    sheet = _get_or_create_spreadsheet(doc, "DS2_Params")

    # Header row
    sheet.set("A1", "Parameter")
    sheet.set("B1", "Value")
    sheet.set("C1", "Unit")
    sheet.set("D1", "Notes")

    params = [
        # (row, name, value, unit, notes)
        # Chassis
        ( 2,  "WHEELBASE",           WHEELBASE,           "mm",   "Front to rear axle CL"),
        ( 3,  "TRACK_FRONT",         TRACK_FRONT,         "mm",   "Front wheel CL-to-CL"),
        ( 4,  "TRACK_REAR",          TRACK_REAR,          "mm",   "Rear wheel CL-to-CL"),
        ( 5,  "GROUND_CLEARANCE",    GROUND_CLEARANCE,    "mm",   "Frame bottom to ground"),
        ( 6,  "FRAME_HEIGHT",        FRAME_HEIGHT,        "mm",   "Ground to top rail"),
        ( 7,  "OVERALL_LENGTH",      OVERALL_LENGTH,      "mm",   "Bumper to bumper"),
        ( 8,  "OVERALL_WIDTH",       OVERALL_WIDTH,       "mm",   "Pontoon tip to tip"),
        ( 9,  "OVERALL_HEIGHT",      OVERALL_HEIGHT,      "mm",   "Ground to rider top"),
        (10,  "FRAME_TUBE_OD",       FRAME_TUBE_OD,       "mm",   "Main tube outer diameter"),
        (11,  "FRAME_TUBE_WALL",     FRAME_TUBE_WALL,     "mm",   "Main tube wall thickness"),
        # Flotation
        (13,  "PONTOON_LENGTH",      PONTOON_LENGTH,      "mm",   "Pontoon total length"),
        (14,  "PONTOON_DIAMETER",    PONTOON_DIAMETER,    "mm",   "Pontoon outer diameter"),
        (15,  "PONTOON_WALL",        PONTOON_WALL,        "mm",   "Pontoon wall thickness"),
        (16,  "PONTOON_OFFSET_Y",    PONTOON_OFFSET_Y,    "mm",   "Lateral CL offset"),
        (17,  "PONTOON_OFFSET_Z",    PONTOON_OFFSET_Z,    "mm",   "Pontoon CL height above ground (min = GC + r)"),
        (18,  "FOAM_FILL_FRACTION",  FOAM_FILL_FRACTION,  "",     "Fraction of volume = closed-cell foam"),
        # Battery pod
        (20,  "BATT_POD_LENGTH",     BATT_POD_LENGTH,     "mm",   "Internal cavity length"),
        (21,  "BATT_POD_WIDTH",      BATT_POD_WIDTH,      "mm",   "Internal cavity width"),
        (22,  "BATT_POD_HEIGHT",     BATT_POD_HEIGHT,     "mm",   "Internal cavity height"),
        (23,  "BATT_POD_WALL",       BATT_POD_WALL,       "mm",   "Enclosure wall thickness"),
        (24,  "BATT_POD_CLEARANCE_Z",BATT_POD_CLEARANCE_Z,"mm",  "Pod bottom above ground"),
        (25,  "VOLTAGE_NOMINAL",     VOLTAGE_NOMINAL,     "V",    "System bus voltage"),
        (26,  "CAPACITY_NOMINAL",    CAPACITY_NOMINAL,    "Ah",   "Target pack capacity"),
        # Drivetrain
        (28,  "MOTOR_PEAK_POWER",    MOTOR_PEAK_POWER,    "W",    "Peak motor power"),
        (29,  "MOTOR_CONT_POWER",    MOTOR_CONT_POWER,    "W",    "Continuous motor power"),
        (30,  "GEAR_RATIO",          GEAR_RATIO,          "",     "Motor-to-wheel ratio"),
        (31,  "MOTOR_MOUNT_OFFSET_X",MOTOR_MOUNT_OFFSET_X,"mm",  "From midpoint, toward rear"),
        # Suspension
        (33,  "SUSP_TRAVEL_UP",      SUSP_TRAVEL_UP,      "mm",   "Bump travel"),
        (34,  "SUSP_TRAVEL_DOWN",    SUSP_TRAVEL_DOWN,    "mm",   "Droop travel"),
        (35,  "FRONT_SPRING_RATE",   FRONT_SPRING_RATE,   "N/mm", "Front spring rate (assumed)"),
        (36,  "REAR_SPRING_RATE",    REAR_SPRING_RATE,    "N/mm", "Rear spring rate (assumed)"),
        # Wheels
        (38,  "TIRE_DIAMETER",       TIRE_DIAMETER,       "mm",   "Overall tire OD"),
        (39,  "TIRE_WIDTH",          TIRE_WIDTH,          "mm",   "Tread section width"),
        (40,  "RIM_DIAMETER",        RIM_DIAMETER,        "mm",   "12-in beadlock rim"),
        (41,  "RIM_WIDTH",           RIM_WIDTH,           "mm",   "Rim bead-to-bead width"),
        # Mass budget
        (43,  "MASS_CHASSIS",        MASS_CHASSIS,        "kg",   ""),
        (44,  "MASS_BATTERY_POD",    MASS_BATTERY_POD,    "kg",   ""),
        (45,  "MASS_MOTOR",          MASS_MOTOR,          "kg",   ""),
        (46,  "MASS_SUSPENSION",     MASS_SUSPENSION,     "kg",   "All four corners"),
        (47,  "MASS_WHEELS",         MASS_WHEELS,         "kg",   "Four wheels + tires"),
        (48,  "MASS_PONTOONS",       MASS_PONTOONS,       "kg",   "Both pontoons"),
        (49,  "MASS_BODY",           MASS_BODY,           "kg",   "Fairings estimate"),
        (50,  "MASS_RIDER_INTERFACE",MASS_RIDER_INTERFACE,"kg",   "Seat, bars, pegs"),
        (51,  "MASS_WIRING",         MASS_WIRING,         "kg",   "Harness + connectors"),
        (52,  "RIDER_MASS",          RIDER_MASS,          "kg",   "Target rider (250 lb)"),
    ]

    for row, name, value, unit, notes in params:
        _set(sheet, row, name, value, unit, notes)

    doc.recompute()
    App.Console.PrintMessage(
        "DS2_Params spreadsheet written — "
        f"{len(params)} parameters registered.\n"
    )


# ---------------------------------------------------------------------------
# STANDALONE TEST  (run outside FreeCAD to verify syntax)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Print a summary table without requiring FreeCAD
    print(f"{'Parameter':<28} {'Value':>10}  Unit")
    print("-" * 50)
    params_plain = {
        "WHEELBASE": (WHEELBASE, "mm"),
        "TRACK_FRONT": (TRACK_FRONT, "mm"),
        "TRACK_REAR": (TRACK_REAR, "mm"),
        "GROUND_CLEARANCE": (GROUND_CLEARANCE, "mm"),
        "PONTOON_LENGTH": (PONTOON_LENGTH, "mm"),
        "PONTOON_DIAMETER": (PONTOON_DIAMETER, "mm"),
        "BATT_POD_LENGTH": (BATT_POD_LENGTH, "mm"),
        "VOLTAGE_NOMINAL": (VOLTAGE_NOMINAL, "V"),
        "MOTOR_PEAK_POWER": (MOTOR_PEAK_POWER, "W"),
        "TIRE_DIAMETER": (TIRE_DIAMETER, "mm"),
        "RIDER_MASS": (RIDER_MASS, "kg"),
    }
    for name, (val, unit) in params_plain.items():
        print(f"  {name:<26} {val:>10}  {unit}")
else:
    # Running inside FreeCAD — execute immediately
    write_parameters()
