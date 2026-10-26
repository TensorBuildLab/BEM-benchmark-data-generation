# Building V02: office building

## Project data

- Building type: office building
- Location: Chicago, IL
- Storeys: 2; floor-to-floor height 12'-8"; flat roof; slab on grade
- Footprint: 118'-1" x 59'-1"
- Orientation: plan north = true north
- Zoning: core and four perimeter zones per floor, perimeter depth 15'-0"

## Envelope

Exterior walls and the roof are built up as listed in `envelope_layers.csv` (outside to inside).
- Windows: U-0.262 Btu/h-ft2-F (whole window), SHGC 0.34, visible transmittance 0.46
- Window-to-wall ratio by facade (as drawn): south 33 %, east 34 %, north 27 %, west 33 %; sill height 2'-11"
- Doors: one south facade door (as drawn), 3'-0" x 7'-0", insulated panel

## Internal loads and schedules

- Lighting: 0.70 W/sq ft
- Plug and process loads: 1.02 W/sq ft
- Occupant density: 5.36 people per 1,000 sq ft
- Hours of operation: weekdays 7 a.m. to 6 p.m., Saturdays 8 a.m. to noon, Sundays closed; no holidays.
- During operating hours occupancy is 95 %, lighting 90 % and plug loads 90 % of design; outside them occupancy is zero, lighting 5 % and plug loads 30 %.

## Air leakage

- Infiltration: 0.42 air changes per hour, constant.

## Systems and controls

- Load calculation only: represent each conditioned zone with an ideal system of unlimited capacity that holds the thermostat setpoints exactly.
- Thermostat: heating 70 F, cooling 75 F; outside operating hours setback to 60 F heating and setup to 85 F cooling, with recovery starting two hours before opening.
