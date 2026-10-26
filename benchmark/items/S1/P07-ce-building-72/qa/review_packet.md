# Review packet: P07-ce-building-72

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | derived | site | 1209 E 2nd St, Tucson AZ (32.23 N) | building_info.txt | 32.2217 | |
| floors | stated | geometry | 5 floors (basement + 4) | building_info.txt | 5 | |
| gfa | stated | geometry | 61,197 gross sq ft (5,685 m2) | building_info.txt | 5685.39 | |
| basement | stated | geometry | basement floor below grade | 72-1.pdf | 659.88 | |
| windows | assumed | fenestration | a 1964 office/lab building has windows: WWR 0.10-0.45 |  | 0.204 | |
| people | assumed | loads | capacity 577 is an upper bound; design occupancy 100-577 | building_info.txt | 577.0 | |
| lpd | assumed | loads | lighting 5-14 W/m2 |  | 7.6424 | |
| epd | assumed | loads | office/lab plug loads 5-25 W/m2 |  | 6.78 | |
| wall-u | assumed | envelope | 1964 masonry wall U 0.4-3.0 W/m2K |  | 2.1184 | |
| hvac | assumed | hvac | conditioned building (HVAC not stated) |  | 12 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
