# Review packet: P03-office-minimal

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| stories | stated | geometry | 2 storeys | input3.txt | 2 | |
| area | stated | geometry | total floor area 1500 m2 | input3.txt | 1500.0 | |
| height | derived | geometry | 2 x 3.6 m = 7.2 m tall | input3.txt | 7.2 | |
| volume | stated | geometry | volume 5400 m3 | input3.txt | 5400.0 | |
| wall-area | derived | geometry | gross wall area 2 x (30 + 25) x 7.2 = 792 m2 | input3.txt | 792.0 | |
| site-lat | stated | site | ZIP 85730: Tucson, AZ (32.2 N) | clarification | 32.2217 | |
| windows | assumed | fenestration | an office has windows: WWR 0.10-0.50 (none described) |  | 0.3 | |
| lpd | assumed | loads | office lighting 5-12 W/m2 |  | 6.8889 | |
| epd | assumed | loads | office plug loads 4-15 W/m2 |  | 6.78 | |
| occ | assumed | loads | office occupancy 2-12 people per 100 m2 |  | 2.2117 | |
| hvac | assumed | hvac | some HVAC system (not stated) |  | central_ashp | |
| hsp | assumed | control | heating setpoint 18-23 C |  | 21.11 | |
| csp | assumed | control | cooling setpoint 23-27 C |  | 23.89 | |
| wall-u | assumed | envelope | wall U 0.15-2.5 W/m2K |  | 0.449 | |
| infil | assumed | infiltration | infiltration 0.05-1.0 ACH |  | 0.3 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
