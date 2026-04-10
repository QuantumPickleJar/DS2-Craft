# DS2-Craft — Revision A Concept Package

> **Document type**: Engineering concept definition  
> **Status**: Draft — Revision A  
> **Last updated**: 2026-04-07

---

## 1  Subsystem Breakdown

Each subsystem is named and treated as an independently modelable module.

| ID | Subsystem Name | Short Description |
|----|----------------|-------------------|
| SYS-01 | **Chassis Frame** | Main structural spine and cross-members; houses all hard-point attachments |
| SYS-02 | **Flotation Pods** | Side-mounted pontoon volumes providing buoyancy reserve; integrated into bodywork |
| SYS-03 | **Battery & Electronics Pod** | Sealed central enclosure; 72 V pack + BMS + primary controller |
| SYS-04 | **Rear Drivetrain** | Motor(s), reduction, axle/hub carriers, rear suspension arm |
| SYS-05 | **Front Steering Axle** | Conventional front wheel pair, knuckle, tie-rod, rack-and-pinion or direct steer |
| SYS-06 | **Suspension** | Four-corner independent or semi-independent; hard-points defined in this revision |
| SYS-07 | **Wheels & Tires** | Paddle-biased off-road tires on steel or aluminium beadlock rims |
| SYS-08 | **Rider Interface** | Seat, footrests, handlebar/yoke; mass and CoM contribution modeled as point load |
| SYS-09 | **Body / Fairings** | Non-structural outer panels; not modeled in Rev A — envelope reserved |
| SYS-10 | **Corrosion & Sealing** | Drainage paths, connector specs, coating requirements (design rules, not geometry) |

---

## 2  Parameter List

All dimensions in **mm** unless noted.  All masses in **kg**.  
Parameters are defined in `cad/macros/parameters.py` — edit that file to change any value.

### 2.1  Chassis & Overall Envelope

| Parameter Name | Symbol | Value | Unit | Notes |
|---|---|---|---|---|
| `WHEELBASE` | L_wb | 1 400 | mm | Front axle to rear axle centerline |
| `TRACK_FRONT` | T_f | 900 | mm | Front wheel centerline to centerline |
| `TRACK_REAR` | T_r | 800 | mm | Rear wheel centerline to centerline |
| `GROUND_CLEARANCE` | GC | 280 | mm | Bottom of frame to ground |
| `FRAME_HEIGHT` | FH | 350 | mm | Ground to top of main rail |
| `OVERALL_LENGTH` | OAL | 2 050 | mm | Bumper to bumper estimate |
| `OVERALL_WIDTH` | OAW | 1 100 | mm | Pontoon tip to pontoon tip |
| `OVERALL_HEIGHT` | OAH | 1 200 | mm | Ground to top of rider envelope |
| `FRAME_TUBE_OD` | FT_od | 50 | mm | Main structural tube outer diameter |
| `FRAME_TUBE_WALL` | FT_w | 3 | mm | Main structural tube wall thickness |

### 2.2  Flotation System

| Parameter Name | Symbol | Value | Unit | Notes |
|---|---|---|---|---|
| `PONTOON_LENGTH` | P_L | 1 400 | mm | Full pontoon tube length |
| `PONTOON_DIAMETER` | P_D | 220 | mm | Outer diameter of cylindrical pontoon |
| `PONTOON_WALL` | P_w | 4 | mm | Wall thickness (structural shell) |
| `PONTOON_OFFSET_Y` | P_y | 450 | mm | Lateral offset from vehicle centerline |
| `PONTOON_OFFSET_Z` | P_z | 390 | mm | Height of pontoon centroid above ground (= GC + r = 280 + 110) |
| `FOAM_FILL_FRACTION` | F_fill | 0.85 | — | Fraction of pontoon volume filled with closed-cell foam |

### 2.3  Battery & Electronics Pod

| Parameter Name | Symbol | Value | Unit | Notes |
|---|---|---|---|---|
| `BATT_POD_LENGTH` | BP_L | 620 | mm | Internal cavity length |
| `BATT_POD_WIDTH` | BP_W | 280 | mm | Internal cavity width |
| `BATT_POD_HEIGHT` | BP_H | 180 | mm | Internal cavity height |
| `BATT_POD_WALL` | BP_wall | 5 | mm | Enclosure wall thickness |
| `BATT_POD_CLEARANCE_Z` | BP_cz | 320 | mm | Bottom of pod above ground |
| `VOLTAGE_NOMINAL` | V_sys | 72 | V | System bus voltage |
| `CAPACITY_NOMINAL` | C_nom | 40 | Ah | Target pack capacity |

### 2.4  Drivetrain

| Parameter Name | Symbol | Value | Unit | Notes |
|---|---|---|---|---|
| `MOTOR_PEAK_POWER` | P_pk | 5 000 | W | Single rear motor peak |
| `MOTOR_CONT_POWER` | P_cont | 3 000 | W | Continuous rating |
| `GEAR_RATIO` | GR | 8.5 | — | Motor to wheel reduction |
| `MOTOR_MOUNT_OFFSET_X` | MM_x | −620 | mm | From vehicle midpoint, toward rear |

### 2.5  Suspension (Hard-Points)

| Parameter Name | Symbol | Value | Unit | Notes |
|---|---|---|---|---|
| `SUSP_TRAVEL_UP` | S_up | 80 | mm | Bump travel from design position |
| `SUSP_TRAVEL_DOWN` | S_dn | 60 | mm | Droop travel from design position |
| `FRONT_SPRING_RATE` | k_f | 22 | N/mm | Assumption — revise after mass calc |
| `REAR_SPRING_RATE` | k_r | 28 | N/mm | Assumption — revise after mass calc |

### 2.6  Wheels & Tires

| Parameter Name | Symbol | Value | Unit | Notes |
|---|---|---|---|---|
| `TIRE_DIAMETER` | T_D | 560 | mm | Overall diameter (22 × 10 class) |
| `TIRE_WIDTH` | T_W | 250 | mm | Section width |
| `RIM_DIAMETER` | R_D | 305 | mm | 12-inch beadlock rim |
| `RIM_WIDTH` | R_W | 178 | mm | 7-inch rim width |

### 2.7  Mass Budget (Estimates)

| Item | Mass (kg) | Notes |
|---|---|---|
| Chassis frame | 28 | 4130 Cr-Mo TIG-welded |
| Battery pod + pack | 38 | 40 Ah LiFePO₄ at ~0.95 kg/Ah + enclosure |
| Rear drivetrain (motor + controller) | 12 | Brushless PMSM + inverter |
| Front steering axle (knuckle, rack) | 6 | No motor; tie-rods, knuckle, rack |
| Suspension + hubs (×4) | 18 | Knuckle, A-arm, spring-damper per corner |
| Wheels + tires (×4) | 16 | 4 kg per corner |
| Pontoons (×2) | 10 | Aluminium shell + foam fill |
| Body / fairings | 10 | Estimate — Rev B detail |
| Rider interface | 6 | Seat, bars, pegs |
| Wiring / plumbing | 4 | Harness, connectors, coolant if used |
| **Vehicle dry mass** | **148** | **Target ≤ 160 kg** |
| Rider (target) | 113 | 250 lb |
| **GVW** | **261** | **kg** |

---

## 3  Recommended Modeling Order

Build geometry in this sequence to maximise parametric dependency clarity:

| Step | File / Feature | Depends On |
|---|---|---|
| 1 | Define all parameters | Nothing — start here |
| 2 | Chassis spine (centerline sketch) | WHEELBASE, GROUND_CLEARANCE, FRAME_HEIGHT |
| 3 | Main frame rails (sweep) | Chassis spine, FRAME_TUBE_OD |
| 4 | Battery pod envelope | BATT_POD_*, BATT_POD_CLEARANCE_Z |
| 5 | Flotation pontoons | PONTOON_*, PONTOON_OFFSET_Y/Z |
| 6 | Suspension hard-points | TRACK_FRONT/REAR, SUSP_TRAVEL_* |
| 7 | Wheel/tire solids | TIRE_DIAMETER, RIM_DIAMETER |
| 8 | Motor mount location | MOTOR_MOUNT_OFFSET_X, rear axle hard-point |
| 9 | Rider envelope (box) | OVERALL_HEIGHT, seat position |
| 10 | Body fairing clearance envelope | All above + margin |

---

## 4  Risk List

Items that are still unknown or assumed, requiring validation before Rev B.

| Risk ID | Risk Description | Severity | Mitigation / Next Action |
|---|---|---|---|
| R-01 | **Buoyancy margin unconfirmed** | High | Run `simulation/buoyancy/buoyancy_estimate.py`; adjust pontoon diameter or length |
| R-02 | **Vehicle mass could exceed 160 kg** | High | Complete mass roll-up in `mass_estimate.py`; revisit battery chemistry if needed |
| R-03 | **CoM height may cause instability on water** | High | Confirm CoB vs CoM relationship; lower battery pod if needed |
| R-04 | **Paddle tire water propulsion efficiency unknown** | Medium | Physical test or CFD; paddle geometry not defined in Rev A |
| R-05 | **Spring rates assumed, not calculated** | Medium | Calculate after confirmed mass + suspension geometry |
| R-06 | **Motor selection not locked** | Medium | Power and voltage fixed; shaft/mount interface TBD |
| R-07 | **Corrosion sealing detail not specified** | Medium | Draft design-rule checklist in SYS-10 before Rev B |
| R-08 | **Body fairing envelope not modeled** | Low | Deferred to Rev B — reserve space only in Rev A |
| R-09 | **Steering geometry (Ackermann) not derived** | Medium | Required before Rev B to confirm rack travel and clearance |
| R-10 | **Regulatory / safety certification path** | Low | Out of scope for concept phase; flag for commercialisation track |
| R-11 | **Pontoon-tire geometric conflict** | Medium | Full-length pontoons (1 400 mm) overlap tire envelope in AABB check; shorten pontoon or add end cutouts in Rev B |

---

## 5  Proposed File / Folder Structure

```
DS2-Craft/
├── README.md
├── .gitignore
│
├── docs/
│   └── revision_A/
│       ├── concept_package.md      ← THIS FILE
│       └── source_of_truth.md      ← live parameter snapshot
│
├── cad/
│   ├── macros/                     ← FreeCAD Python macros (run in order)
│   │   ├── parameters.py           ← Step 1: master parameter definitions
│   │   ├── chassis_frame.py        ← Step 2–3: frame spine + rails
│   │   ├── battery_pod.py          ← Step 4: battery enclosure solid
│   │   ├── flotation_pods.py       ← Step 5: pontoon solids
│   │   └── suspension_hardpoints.py← Step 6: hard-point markers
│   │
│   └── revision_A/
│       ├── chassis/                ← .FCStd files for frame geometry
│       ├── flotation/              ← .FCStd files for pontoons
│       ├── suspension/             ← .FCStd files for suspension layout
│       ├── battery_pod/            ← .FCStd files for battery enclosure
│       ├── drivetrain/             ← .FCStd files for motor/reduction
│       └── assembly/               ← top-level assembly .FCStd
│
└── simulation/
    ├── buoyancy/
    │   └── buoyancy_estimate.py    ← pontoon volume vs GVW float check
    ├── mass_properties/
    │   └── mass_estimate.py        ← component mass roll-up + CoM estimate
    └── packaging/
        └── packaging_check.py      ← hard clearance / overlap checks
```

---

## 6  Revision A Simulation Findings

Run `python3 simulation/buoyancy/buoyancy_estimate.py` and related scripts to reproduce.

| Check | Result | Detail |
|---|---|---|
| **Dry mass target** | ✅ PASS | 148 kg dry — 12 kg margin under 160 kg target |
| **Weight distribution** | ✅ PASS | 49 / 51 front-rear split with rider |
| **Pontoon ground clearance** | ✅ PASS (after correction) | PONTOON_OFFSET_Z corrected to 390 mm |
| **Buoyancy margin** | ❌ FAIL → R-01 | Two 220 mm-dia × 1400 mm pontoons = 106 L; need 261 L for GVW. Buoyancy factor 0.41 (need ≥ 1.15). |
| **Packaging overlaps** | ❌ → R-11 | Pontoon AABB overlaps front/rear tire envelopes; by-design chassis mounts are correctly excluded. Rev B geometry task. |

**Buoyancy action** (see R-01): To achieve float margin ≥ 1.15 with current length, increase pontoon OD to **≈ 370 mm**, or add additional buoyant volume through chassis hull / underbody displacement. Pontoon-Y offset will need corresponding adjustment to maintain tire clearance.

---

*Next revision action*: complete buoyancy and mass-estimate scripts, then open Rev A FreeCAD assembly.
