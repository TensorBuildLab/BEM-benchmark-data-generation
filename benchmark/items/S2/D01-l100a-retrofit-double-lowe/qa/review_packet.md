# Review packet: D01-l100a-retrofit-double-lowe

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| elev | stated | site | altitude 6145 ft (1873 m) | L100A_Text_C.txt (2.2.5) | 1873.0 | |
| weather | stated | site | Colorado Springs weather | L100A_Text_C.txt (2.2.5) | Colorado.Springs.AP-Peterson.Field CO USA SRC-TMYx WMO#=724660 | |
| zones | stated | geometry | attic modelled as a separate unconditioned zone (2 zones) | L100A_Text_C.txt (2.2.1) | [2, 1] | |
| cfa | stated | geometry | conditioned floor 57 ft x 27 ft = 1539 sq ft (142.98 m2) | L100A_Text_C.txt (Table 2-3) | 142.98 | |
| cvol | stated | geometry | conditioned air volume 12,312 cu ft (348.6 m3) | L100A_Text_C.txt (Table 2-4) | 348.637 | |
| win-area | stated | fenestration | 270 sq ft of windows incl. frame (25.1 m2); glass-only modelling gives about 18.3 m2 | L100A_Text_C.txt (Table 2-3) | 19.26 | |
| win-split | stated | fenestration | north and south carry twice the window area of east and west | L100A_Text_C.txt (Table 2-3) | 6.43 | |
| doors | stated | fenestration | 2 doors, 40 sq ft (3.72 m2) | L100A_Text_C.txt (Table 2-3) | [3.72, 3.72] | |
| wall-u | stated | envelope | exterior wall U 0.085 Btu/h-ft2-F air-to-air (0.483 W/m2K) | L100A_Text_C.txt (Table 2-3) | [0.483, 0.532] | |
| floor-u | stated | envelope | floor over vented crawl space U 0.071 Btu/h-ft2-F (0.403 W/m2K) | L100A_Text_C.txt (Table 2-3) | 0.405 | |
| infil-house | stated | infiltration | 0.67 ACH in the conditioned zone (program corrects for altitude) | L100A_Text_C.txt (Table 2-4) | 0.67 | |
| infil-attic | stated | infiltration | 2.4 ACH in the attic | L100A_Text_C.txt (Table 2-4) | [2.4] | |
| gains | stated | loads | 56,105 Btu/day sensible (+12,156 latent): 21.6-26.3 GJ/yr of internal gains | L100A_Text_C.txt (Table 2-4, Table 2-11) | 26.288 | |
| hsp | stated | control | HEAT = ON IF TEMP < 68 F (20.0 C) | L100A_Text_C.txt (2.2.10.1) | 20.0 | |
| no-cool | stated | control | COOL = OFF (heating-only case) | L100A_Text_C.txt (2.2.10.1) | False | |
| ideal | stated | hvac | pure loads: 100 % efficient, effectively infinite capacity | L100A_Text_C.txt (2.2.10) | ideal_loads | |
| annual | stated | simulation | the whole year may be simulated | L100A_Text_C.txt (2.2.10.1) | True | |
| win-u | stated | fenestration | replacement windows U 1.8 W/m2K (whole window) | addendum.md | 1.801 | |
| win-shgc | stated | fenestration | replacement windows SHGC 0.4 | addendum.md | 0.401 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
