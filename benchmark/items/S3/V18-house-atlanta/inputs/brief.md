# Building V18: single-family house

## Project data

- Building type: single-family house
- Location: Atlanta, GA
- Storeys: 2; floor-to-floor height 2.92 m; flat roof; slab on grade
- Footprint: 15.90 m x 11.70 m
- Orientation: plan north = true north
- Zoning: one zone per floor
- Attached garage on the west side (as drawn): single storey, 6.70 m deep, 2.92 m high, unconditioned

## Envelope

Exterior walls and the roof are built up as listed in `envelope_layers.csv` (outside to inside).
- Windows: U = 3.22 W/m2K (whole window), SHGC 0.36, visible transmittance 0.51
- Window-to-wall ratio by facade (as drawn): south 19 %, east 9 %, north 10 %, west 10 % (upper floor only, above the garage); sill height 0.90 m
- Doors: one south facade door (as drawn), 0.91 m x 2.13 m, insulated panel

## Internal loads and schedules

- Lighting: 5.3 W/m2
- Plug and process loads: 3.9 W/m2
- Occupants: 3 people
- Schedules: typical residential profiles (see `schedules.csv`, hourly fractions).

## Air leakage

- Infiltration: 0.34 air changes per hour, constant; the garage leaks 1.0 air change per hour.

## Systems and controls

- Each conditioned zone is served by its own packaged single-zone rooftop heat pump (ducted, constant volume, electric backup, no economizer).
- Cooling efficiency: COP 3.67 (gross, rated)
- Heat pump heating COP 3.37 (gross, rated)
- Thermostat: heating 20.7 C, cooling 25.2 C.
