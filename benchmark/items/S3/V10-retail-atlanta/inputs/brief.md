# Building V10: retail store

The retail store stands in Atlanta, GA. Its main entrance is on the facade that faces west (true 270 deg). The drawing is drawn with the entrance facade at the bottom of the sheet; its north arrow gives true north.

It has 1 storey on a 46.00 m by 36.00 m footprint, 5.57 m floor to floor, with a flat roof and a slab on grade.
Model each floor as one thermal zone.

## Envelope

- Exterior walls: U = 0.50 W/m2K (layers only, without surface films)
- Roof: U = 0.24 W/m2K (layers only, without surface films)
- Windows: U = 2.41 W/m2K (whole window), SHGC 0.40, visible transmittance 0.55
- Window-to-wall ratio by facade (as drawn): bottom 39 %, right-hand 5 %, top 0 %, left-hand 5 %; sill height 0.90 m
- Doors: one bottom, one top facade door (as drawn), 0.91 m x 2.13 m, insulated panel

## Internal loads and schedules

- Hours of operation: weekdays 9 a.m. to 9 p.m., Saturdays 9 a.m. to 9 p.m., Sundays 10 a.m. to 6 p.m.; no holidays.
- During operating hours occupancy is 95 %, lighting 90 % and plug loads 90 % of design; outside them occupancy is zero, lighting 5 % and plug loads 30 %.

## Air leakage

- Infiltration: 0.35 air changes per hour, constant.

## Systems and controls

- Each conditioned zone is served by its own packaged single-zone rooftop heat pump (ducted, constant volume, electric backup, no economizer).
- Cooling efficiency: COP 3.41 (gross, rated)
- Heat pump heating COP 3.38 (gross, rated)
- Thermostat: heating 21.0 C, cooling 24.0 C; outside operating hours setback to 15.6 C heating and setup to 29.4 C cooling, with recovery starting two hours before opening.
