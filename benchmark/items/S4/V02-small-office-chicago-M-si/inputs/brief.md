# Building V02: office building

## Project data

- Building type: office building
- Location: Chicago, IL
- Storeys: 2; floor-to-floor height 3.87 m; flat roof; slab on grade
- Footprint: 36.00 m x 18.00 m
- Orientation: plan north = true north
- Zoning: core and four perimeter zones per floor, perimeter depth 4.57 m

## Envelope

Exterior walls and the roof are built up as listed in `envelope_layers.csv` (outside to inside).
- Windows: U = 1.49 W/m2K (whole window), SHGC 0.34, visible transmittance 0.46
- Window-to-wall ratio by facade (as drawn): south 33 %, east 34 %, north 27 %, west 33 %; sill height 0.90 m
- Doors: one south facade door (as drawn), 0.91 m x 2.13 m, insulated panel

## Internal loads and schedules

- Lighting: 7.5 W/m2
- Plug and process loads: 11.0 W/m2
- Occupant density: 5.8 people per 100 m2 of floor area
- Hours of operation: weekdays 7 a.m. to 6 p.m., Saturdays 8 a.m. to noon, Sundays closed; no holidays.
- During operating hours occupancy is 95 %, lighting 90 % and plug loads 90 % of design; outside them occupancy is zero, lighting 5 % and plug loads 30 %.

## Air leakage

- Infiltration: 0.42 air changes per hour, constant.

## Systems and controls

- Load calculation only: represent each conditioned zone with an ideal system of unlimited capacity that holds the thermostat setpoints exactly.
- Thermostat: heating 21.0 C, cooling 24.0 C; outside operating hours setback to 15.6 C heating and setup to 29.4 C cooling, with recovery starting two hours before opening.
