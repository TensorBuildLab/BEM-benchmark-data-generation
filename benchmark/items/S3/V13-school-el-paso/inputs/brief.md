# Building V13: school classroom building

The school classroom building stands in El Paso, TX. Its main entrance is on the facade that faces north (true 0 deg). The drawing is drawn with the entrance facade at the bottom of the sheet; its north arrow gives true north.

It has 1 storey on a 69.00 m by 14.00 m, with a wing of 15.00 m by 33.00 m extending from the west end of the north facade (see the drawing) footprint, 4.11 m floor to floor, with a flat roof and a slab on grade.
Model each floor as one thermal zone.

## Envelope

Exterior walls and the roof are built up as listed in `envelope_layers.csv` (outside to inside).
- Windows: U = 2.60 W/m2K (whole window), SHGC 0.42, visible transmittance 0.47
- Window-to-wall ratio by facade (as drawn): bottom 26 %, right-hand 34 %, top 28 %, left-hand 36 %; sill height 0.90 m
- Doors: one bottom facade door (as drawn), 0.91 m x 2.13 m, insulated panel

## Internal loads and schedules

- Lighting: 7.8 W/m2
- Plug and process loads: 6.5 W/m2
- Occupant density: 23.1 people per 100 m2 of floor area
- Hours of operation: weekdays 7 a.m. to 4 p.m., Saturdays closed, Sundays closed; no holidays.
- During operating hours occupancy is 95 %, lighting 90 % and plug loads 90 % of design; outside them occupancy is zero, lighting 5 % and plug loads 30 %.

## Air leakage

- Infiltration: 0.35 air changes per hour, constant.

## Systems and controls

- Each conditioned zone has a through-the-wall packaged terminal heat pump with electric supplemental heat.
- Cooling efficiency: COP 3.29 (gross, rated)
- Heat pump heating COP 3.30 (gross, rated)
- Thermostat: heating 21.0 C, cooling 24.0 C; outside operating hours setback to 15.6 C heating and setup to 29.4 C cooling, with recovery starting two hours before opening.
