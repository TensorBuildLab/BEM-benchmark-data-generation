# Building V02: office building

The office building stands in Chicago, IL. Plan north is true north.

It has 2 storeys on a 118'-1" by 59'-1" footprint, 12'-8" floor to floor, with a flat roof and a slab on grade.
Model each floor with four perimeter zones 15'-0" deep and one core zone.

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
