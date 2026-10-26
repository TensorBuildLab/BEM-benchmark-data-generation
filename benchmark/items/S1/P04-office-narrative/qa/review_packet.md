# Review packet: P04-office-narrative

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| stories | stated | geometry | 2 storeys | input4.txt (para 1) | 2 | |
| area | stated | geometry | about 1500 m2 | input4.txt (para 1) | 1500.0 | |
| height | stated | geometry | total height about 7.2 m | input4.txt (para 1) | 7.2 | |
| wall-area | derived | geometry | gross wall area 2 x (30 + 25) x 7.2 = 792 m2 | input4.txt (para 1) | 792.0 | |
| people | stated | loads | 75 occupants per floor, 150 in total | input4.txt (para 2) | 150.0 | |
| lpd | stated | loads | lighting about 8 W/m2 | input4.txt (para 2) | 8.0 | |
| epd | stated | loads | equipment about 10 W/m2 | input4.txt (para 2) | 10.0 | |
| wall-insulated | stated | envelope | brick-insulation-gypsum walls: insulated (U below 1.0) | input4.txt (para 3) | 0.449 | |
| roof-insulated | stated | envelope | insulated roof (U below 0.8) | input4.txt (para 3) | 0.359 | |
| slab | stated | envelope | ground floor on a concrete slab on grade | input4.txt (para 5) | 1 | |
| win-dp | stated | fenestration | double-pane windows: U 1.5-3.6 W/m2K | input4.txt (para 3) | 2.402 | |
| win-s | stated | fenestration | windows on the south facade (both floors) | input4.txt (para 4) | 0.2939 | |
| win-n | stated | fenestration | windows on the north facade (both floors) | input4.txt (para 4) | 0.25 | |
| win-e | stated | fenestration | windows on the east facade (both floors) | input4.txt (para 4) | 0.2438 | |
| win-w | stated | fenestration | windows on the west facade (both floors) | input4.txt (para 4) | 0.25 | |
| doors | stated | fenestration | main entrance (south) and service door (east) | input4.txt (para 4) | 2 | |
| wwr-range | assumed | fenestration | window sizes not given: WWR 0.10-0.50 |  | 0.2606 | |
| orient | stated | site | faces due south (north axis 0) | input4.txt (para 5) | 0.0 | |
| hvac | assumed | hvac | some HVAC system (not stated) |  | central_ashp | |
| hsp | assumed | control | heating setpoint 18-23 C |  | 21.11 | |
| csp | assumed | control | cooling setpoint 23-27 C |  | 23.89 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
