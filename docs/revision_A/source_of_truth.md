# DS2-Craft — Source of Truth (Revision A)

> **Purpose**: Single authoritative reference for all current parameter values.  
> When parameters change, update this file AND `cad/macros/parameters.py` together.  
> Do not edit geometry files directly — change parameters here first.

---

## Current Revision

| Field | Value |
|---|---|
| Revision | A |
| Date | 2026-04-07 |
| Status | Draft |

---

## Chassis & Envelope

| Parameter | Value | Unit |
|---|---|---|
| WHEELBASE | 1 400 | mm |
| TRACK_FRONT | 900 | mm |
| TRACK_REAR | 800 | mm |
| GROUND_CLEARANCE | 280 | mm |
| FRAME_HEIGHT | 350 | mm |
| OVERALL_LENGTH | 2 050 | mm |
| OVERALL_WIDTH | 1 100 | mm |
| OVERALL_HEIGHT | 1 200 | mm |
| FRAME_TUBE_OD | 50 | mm |
| FRAME_TUBE_WALL | 3 | mm |

## Flotation

| Parameter | Value | Unit |
|---|---|---|
| PONTOON_LENGTH | 1 400 | mm |
| PONTOON_DIAMETER | 220 | mm |
| PONTOON_WALL | 4 | mm |
| PONTOON_OFFSET_Y | 450 | mm |
| PONTOON_OFFSET_Z | 390 | mm |
| FOAM_FILL_FRACTION | 0.85 | — |

## Battery Pod

| Parameter | Value | Unit |
|---|---|---|
| BATT_POD_LENGTH | 620 | mm |
| BATT_POD_WIDTH | 280 | mm |
| BATT_POD_HEIGHT | 180 | mm |
| BATT_POD_WALL | 5 | mm |
| BATT_POD_CLEARANCE_Z | 320 | mm |
| VOLTAGE_NOMINAL | 72 | V |
| CAPACITY_NOMINAL | 40 | Ah |

## Drivetrain

| Parameter | Value | Unit |
|---|---|---|
| MOTOR_PEAK_POWER | 5 000 | W |
| MOTOR_CONT_POWER | 3 000 | W |
| GEAR_RATIO | 8.5 | — |

## Suspension

| Parameter | Value | Unit |
|---|---|---|
| SUSP_TRAVEL_UP | 80 | mm |
| SUSP_TRAVEL_DOWN | 60 | mm |
| FRONT_SPRING_RATE | 22 | N/mm |
| REAR_SPRING_RATE | 28 | N/mm |

## Wheels & Tires

| Parameter | Value | Unit |
|---|---|---|
| TIRE_DIAMETER | 560 | mm |
| TIRE_WIDTH | 250 | mm |
| RIM_DIAMETER | 305 | mm |
| RIM_WIDTH | 178 | mm |

## Mass Budget

| Item | Mass (kg) |
|---|---|
| Chassis frame | 28 |
| Battery pod + pack | 38 |
| Rear drivetrain (motor + controller) | 12 |
| Front steering axle | 6 |
| Suspension + hubs (×4) | 18 |
| Wheels + tires (×4) | 16 |
| Pontoons (×2) | 10 |
| Body / fairings | 10 |
| Rider interface | 6 |
| Wiring / plumbing | 4 |
| **Vehicle dry mass** | **148** |
| Rider | 113 |
| **GVW** | **261** |

---

## Open Questions / Flags

- [ ] R-01: **Buoyancy deficit** — 106 L available vs 255 L needed; increase pontoon OD to ~365 mm or add hull displacement
- [ ] R-02: Vehicle mass roll-up — run `mass_estimate.py` (current: 148 kg dry ✅)
- [ ] R-03: CoM height vs CoB — confirm after mass calc (current GVW CoM Z ≈ 511 mm)
- [ ] R-04: Paddle tire water propulsion
- [ ] R-05: Spring rates — derive from confirmed mass
- [ ] R-06: Motor selection — shaft interface TBD
- [ ] R-07: Corrosion sealing detail checklist
- [ ] R-09: Ackermann steering geometry
- [ ] R-11: Pontoon-tire geometry conflict — full-length pontoons overlap tire envelope; resolve in Rev B
