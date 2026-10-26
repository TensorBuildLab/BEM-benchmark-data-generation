# Building V22: apartment building

## Project data

- Building type: apartment building
- Location: Baltimore, MD
- Storeys: 2; floor-to-floor height 9'-3"; flat roof; slab on grade
- Footprint: 20'-4" x 41'-0"
- Orientation: plan north = true north
- Zoning: one zone per floor
- East wall (as drawn): party wall, adiabatic, no windows
- West wall (as drawn): party wall, adiabatic, no windows

## Envelope

- Exterior walls: U-0.059 Btu/h-ft2-F (layers only, without surface films)
- Roof: U-0.052 Btu/h-ft2-F (layers only, without surface films)
- Windows: U-0.567 Btu/h-ft2-F (whole window), SHGC 0.34, visible transmittance 0.51
- Window-to-wall ratio by facade (as drawn): south 39 %, north 20 %; sill height 2'-11"
- Doors: one south facade door (as drawn), 3'-0" x 7'-0", insulated panel

## Internal loads and schedules

- Lighting: 0.33 W/sq ft
- Plug and process loads: 0.32 W/sq ft
- Occupants: 2 people
- Schedules: typical residential profiles (see `schedules.csv`, hourly fractions).

## Air leakage

- Infiltration: 0.22 air changes per hour, constant.

## Systems and controls

- Each conditioned zone is served by its own packaged single-zone rooftop heat pump (ducted, constant volume, electric backup, no economizer).
- Cooling efficiency: EER 11.8 (gross, rated)
- Heat pump heating COP 3.28 (gross, rated)
- Thermostat: heating 69 F, cooling 78 F.
