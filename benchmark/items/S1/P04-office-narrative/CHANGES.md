# Curation log: P04-office-narrative

Reference taken from candidate `harness` (agent harness (gbXML route)).

## Model repairs

- add_windows_by_wwr (fenestration): added 8 windows for WWR {'N': 0.25, 'E': 0.25, 'S': 0.3, 'W': 0.25}
- add_door (fenestration): added a 0.91 x 2.13 m door on the S facade
- add_door (fenestration): added a 0.91 x 2.13 m door on the E facade
- one_system_per_zone (hvac): one heat pump controlled from one zone served 2 zones; replaced by one packaged heat pump per zone (COP 3 cooling, 2.75 heating, gas supplemental heat kept); 37 HVAC objects removed
- add_sizing_factors (hvac): sizing factors heating 1.25, cooling 1.15

## Assumptions in the reference

- windows: located but not dimensioned: WWR 0.30 south, 0.25 elsewhere; double pane U 2.4, SHGC 0.35
- doors: 0.91 x 2.13 m main entrance (south) and service door (east)
- hvac: one packaged heat pump per floor (the candidate had one heat pump, controlled from level 1, serving both floors)
