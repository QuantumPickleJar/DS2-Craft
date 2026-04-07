# DS2-Craft

Full-size adult-ridable electric off-road concept vehicle inspired by the visual language of the
Death Stranding 2 Tri-Cruiser.  This is a **practical engineering concept**, not a prop replica.

---

## Project Goals

| Goal | Detail |
|---|---|
| Rider capacity | Single adult, target mass 250 lb (113 kg) |
| Primary terrain | Land / off-road |
| Water capability | Tier 2 buoyancy — floats with rider, slow self-propulsion (1–3 mph) |
| Corrosion resistance | Tier 3 — sealed connectors, drainage paths, anti-corrosion materials/coatings |
| Visual language | Futuristic utility / off-road, evocative of reverse-trike silhouette |
| Drivetrain | 72 V electric, rear primary drive |
| Design philosophy | Parametric-first, modular, serviceable |

---

## Repository Layout

```
DS2-Craft/
├── docs/
│   └── revision_A/
│       ├── concept_package.md   ← subsystem breakdown, parameter list, modeling order, risk list
│       └── source_of_truth.md  ← living "current parameter" document
├── cad/
│   ├── revision_A/
│   │   ├── chassis/
│   │   ├── flotation/
│   │   ├── suspension/
│   │   ├── battery_pod/
│   │   ├── drivetrain/
│   │   └── assembly/
│   └── macros/
│       ├── parameters.py           ← master parameter table (edit here first)
│       ├── chassis_frame.py        ← parametric frame geometry
│       ├── flotation_pods.py       ← side pontoon / flotation volumes
│       ├── battery_pod.py          ← sealed battery enclosure
│       └── suspension_hardpoints.py← suspension pickup layout
└── simulation/
    ├── buoyancy/
    │   └── buoyancy_estimate.py
    ├── mass_properties/
    │   └── mass_estimate.py
    └── packaging/
        └── packaging_check.py
```

---

## Tooling

- **CAD**: [FreeCAD](https://www.freecad.org/) — parametric solid modeling, run macros from `cad/macros/`
- **Simulation**: Python 3 scripts in `simulation/` — buoyancy, mass-property, and packaging checks
- **No external dependencies** beyond Python standard library and (optionally) `numpy`

---

## Revision History

| Rev | Status | Notes |
|---|---|---|
| A | In progress | Initial concept package — chassis envelope, flotation, battery pod |

---

## Quick Start

1. Open FreeCAD.
2. Open **Macro → Macros…** and point FreeCAD at the `cad/macros/` folder.
3. Run `parameters.py` first to register all named parameters.
4. Run `chassis_frame.py`, `flotation_pods.py`, `battery_pod.py`, and `suspension_hardpoints.py`
   in order to build the Revision A geometry.
5. Save each result into the matching sub-folder under `cad/revision_A/`.

To run the simulation scripts independently:

```bash
python3 simulation/buoyancy/buoyancy_estimate.py
python3 simulation/mass_properties/mass_estimate.py
python3 simulation/packaging/packaging_check.py
```
