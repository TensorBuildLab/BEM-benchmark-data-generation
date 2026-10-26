# Building V08: office building

## Project data

- Building type: office building
- Location: Rochester, MN
- Storeys: 3; floor-to-floor height 12'-3"; flat roof; slab on grade
- Footprint: 173'-11" x 105'-0"
- Orientation: plan north = true north
- Zoning: core and four perimeter zones per floor, perimeter depth 15'-0"

## Envelope

Exterior walls and the roof are built up as listed in `envelope_layers.csv` (outside to inside).
- Windows: U-0.333 Btu/h-ft2-F (whole window), SHGC 0.34, visible transmittance 0.49
- Window-to-wall ratio by facade (as drawn): south 23 %, east 33 %, north 40 %, west 23 %; sill height 2'-11"
- Doors: one south facade door (as drawn), 3'-0" x 7'-0", insulated panel

## Internal loads and schedules

- Lighting: installed at the ASHRAE Standard 90.1-2019 building area method allowance for an office.
- Plug and process loads: 0.81 W/sq ft
- Occupant density: 3.89 people per 1,000 sq ft
- Hours of operation: weekdays 7 a.m. to 6 p.m., Saturdays 8 a.m. to noon, Sundays closed; no holidays.
- During operating hours occupancy is 95 %, lighting 90 % and plug loads 90 % of design; outside them occupancy is zero, lighting 5 % and plug loads 30 %.

## Air leakage

- Infiltration: 0.24 air changes per hour, constant.

## Systems and controls

- Each conditioned zone is served by its own packaged single-zone rooftop heat pump (ducted, constant volume, electric backup, no economizer).
- Cooling efficiency: EER 12.2 (gross, rated)
- Heat pump heating COP 3.55 (gross, rated)
- Thermostat: heating 70 F, cooling 75 F; outside operating hours setback to 60 F heating and setup to 85 F cooling, with recovery starting two hours before opening.
