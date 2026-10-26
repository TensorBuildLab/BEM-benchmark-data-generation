# Review packet: R02-l100a-cos-std140

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| elev | stated | site | altitude 6145 ft (1873 m) | L100A_Text_C.txt (2.2.5) |  | |
| weather | stated | site | Colorado Springs weather | L100A_Text_C.txt (2.2.5) |  | |
| zones | stated | geometry | attic modelled as a separate unconditioned zone (2 zones) | L100A_Text_C.txt (2.2.1) |  | |
| cfa | stated | geometry | conditioned floor 57 ft x 27 ft = 1539 sq ft (142.98 m2) | L100A_Text_C.txt (Table 2-3) |  | |
| cvol | stated | geometry | conditioned air volume 12,312 cu ft (348.6 m3) | L100A_Text_C.txt (Table 2-4) |  | |
| win-area | stated | fenestration | 270 sq ft of windows incl. frame (25.1 m2); glass-only modelling gives about 18.3 m2 | L100A_Text_C.txt (Table 2-3) |  | |
| win-split | stated | fenestration | north and south carry twice the window area of east and west | L100A_Text_C.txt (Table 2-3) |  | |
| win-u | stated | fenestration | single pane: glass U 1.064, unit 1.039 Btu/h-ft2-F (5.9-6.0 W/m2K) | L100A_Text_C.txt (Table 2-3) |  | |
| win-shgc | stated | fenestration | SHGC 0.857 (glass) / 0.670 (unit) | L100A_Text_C.txt (Table 2-3) |  | |
| doors | stated | fenestration | 2 doors, 40 sq ft (3.72 m2) | L100A_Text_C.txt (Table 2-3) |  | |
| wall-u | stated | envelope | exterior wall U 0.085 Btu/h-ft2-F air-to-air (0.483 W/m2K) | L100A_Text_C.txt (Table 2-3) |  | |
| floor-u | stated | envelope | floor over vented crawl space U 0.071 Btu/h-ft2-F (0.403 W/m2K) | L100A_Text_C.txt (Table 2-3) |  | |
| infil-house | stated | infiltration | 0.67 ACH in the conditioned zone (program corrects for altitude) | L100A_Text_C.txt (Table 2-4) |  | |
| infil-attic | stated | infiltration | 2.4 ACH in the attic | L100A_Text_C.txt (Table 2-4) |  | |
| gains | stated | loads | 56,105 Btu/day sensible (+12,156 latent): 21.6-26.3 GJ/yr of internal gains | L100A_Text_C.txt (Table 2-4, Table 2-11) |  | |
| hsp | stated | control | HEAT = ON IF TEMP < 68 F (20.0 C) | L100A_Text_C.txt (2.2.10.1) |  | |
| no-cool | stated | control | COOL = OFF (heating-only case) | L100A_Text_C.txt (2.2.10.1) |  | |
| ideal | stated | hvac | pure loads: 100 % efficient, effectively infinite capacity | L100A_Text_C.txt (2.2.10) |  | |
| annual | stated | simulation | the whole year may be simulated | L100A_Text_C.txt (2.2.10.1) |  | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
