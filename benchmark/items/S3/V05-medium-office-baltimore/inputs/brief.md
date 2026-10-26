# Building V05: office building

## Project data

- Building type: office building
- Location: Baltimore, MD
- Storeys: 3; floor-to-floor height 3.92 m; flat roof; slab on grade
- Footprint: 57.00 m x 29.00 m
- Orientation: entrance facade faces north (true azimuth 0 deg); see the north arrow on the drawing
- Zoning: core and four perimeter zones per floor, perimeter depth 4.57 m

## Envelope

Exterior walls and the roof are built up as listed in `envelope_layers.csv` (outside to inside).
- Windows: U = 2.20 W/m2K (whole window), SHGC 0.31, visible transmittance 0.55
- Window-to-wall ratio by facade (as drawn): bottom 22 %, right-hand 37 %, top 39 %, left-hand 26 %; sill height 0.90 m
- Doors: one bottom facade door (as drawn), 0.91 m x 2.13 m, insulated panel

## Internal loads and schedules

- Lighting: 8.2 W/m2
- Plug and process loads: 6.4 W/m2
- Occupant density: 6.3 people per 100 m2 of floor area
- Hours of operation: weekdays 7 a.m. to 6 p.m., Saturdays 8 a.m. to noon, Sundays closed; no holidays.
- During operating hours occupancy is 95 %, lighting 90 % and plug loads 90 % of design; outside them occupancy is zero, lighting 5 % and plug loads 30 %.

## Air leakage

- Infiltration: 0.18 air changes per hour, constant.

## Systems and controls

- Each conditioned zone is served by its own packaged single-zone rooftop heat pump (ducted, constant volume, electric backup, no economizer).
- Cooling efficiency: COP 3.59 (gross, rated)
- Heat pump heating COP 3.59 (gross, rated)
- Thermostat: heating 21.0 C, cooling 24.0 C; outside operating hours setback to 15.6 C heating and setup to 29.4 C cooling, with recovery starting two hours before opening.
