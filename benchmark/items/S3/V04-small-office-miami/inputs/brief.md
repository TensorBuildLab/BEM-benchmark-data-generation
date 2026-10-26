# Building V04: office building

The office building stands in Miami, FL. Plan north is true north.

It has 2 storeys on a 127'-11" by 55'-9" footprint, 12'-4" floor to floor, with a flat roof and a slab on grade.
Model each floor with four perimeter zones 15'-0" deep and one core zone.

## Envelope

- Exterior walls: U-0.059 Btu/h-ft2-F (layers only, without surface films)
- Roof: U-0.042 Btu/h-ft2-F (layers only, without surface films)
- Windows: U-0.585 Btu/h-ft2-F (whole window), SHGC 0.23, visible transmittance 0.45
- Window sizes per facade are listed in `windows.csv`.
- Doors: one south facade door (as drawn), 3'-0" x 7'-0", insulated panel

## Internal loads and schedules

- Lighting: 0.88 W/sq ft
- Plug and process loads: 0.85 W/sq ft
- Occupant density: 4.49 people per 1,000 sq ft
- Hours of operation: weekdays 7 a.m. to 6 p.m., Saturdays 8 a.m. to noon, Sundays closed; no holidays.
- During operating hours occupancy is 95 %, lighting 90 % and plug loads 90 % of design; outside them occupancy is zero, lighting 5 % and plug loads 30 %.

## Air leakage

- Infiltration: 0.19 air changes per hour, constant.

## Systems and controls

- Each conditioned zone is served by its own packaged single-zone rooftop heat pump (ducted, constant volume, electric backup, no economizer).
- Cooling efficiency: EER 13.1 (gross, rated)
- Heat pump heating COP 3.19 (gross, rated)
- Thermostat: heating 70 F, cooling 75 F; outside operating hours setback to 60 F heating and setup to 85 F cooling, with recovery starting two hours before opening.
