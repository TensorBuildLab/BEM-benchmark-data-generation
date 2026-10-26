# Review packet: P02-lupton-heat-pump

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | latitude 35.06 N | input2.txt (Overview) | 35.06 | |
| site-lon | stated | site | longitude 109.08 W | input2.txt (Overview) | -109.08 | |
| site-elev | stated | site | elevation 1780 m | input2.txt (Overview) | 1780.0 | |
| zones | stated | geometry | single zone | input2.txt (Overview) | 1 | |
| floor-area | derived | geometry | floor area 167.7 + 14.7 + 13.8 = 196.2 m2 | input2.txt (Geometry) | 196.1 | |
| height | stated | geometry | envelope height 4.445 m (flat roof at z = 4.445 m) | input2.txt (Geometry) | 4.445 | |
| slab | stated | envelope | slab on grade | input2.txt (Geometry) | 1 | |
| roof-u | stated | envelope | roof U about 0.2 W/m2K from the foam alone | input2.txt (Geometry) | 0.19 | |
| wall-u | assumed | envelope | 9 in. adobe wall: U (no film) 1.4-3.2 W/m2K for k 0.5-1.0 W/mK |  | 2.953 | |
| internal-mass | stated | envelope | 14.86 m2 internal mass | input2.txt (Geometry) | True | |
| win-count | stated | fenestration | 6 windows (2 on SE, 2 on SW, 1 S, 1 W) | input2.txt (Openings table) | 6 | |
| door-count | stated | fenestration | 2 wood doors (SE and SW) | input2.txt (Openings table) | 2 | |
| door-area | derived | fenestration | doors 3'2" x 7' = 2.06 m2 each, 4.12 m2 total | input2.txt (Openings table) | 4.12 | |
| win-north | stated | fenestration | no openings on the north, NE and NW faces | input2.txt (Openings table) | 0.0 | |
| win-u | stated | fenestration | glazing U 2.05 W/m2K | input2.txt (Openings) | 2.051 | |
| win-shgc | stated | fenestration | SHGC 0.40 | input2.txt (Openings) | 0.401 | |
| people | stated | loads | 4 occupants | input2.txt (Internal gains) | 4.0 | |
| activity | stated | loads | 120 W per person | input2.txt (Internal gains) | 120.0 | |
| lpd | stated | loads | LED lighting 5 W/m2 | input2.txt (Internal gains) | 5.0 | |
| epd | stated | loads | appliances 7 W/m2 | input2.txt (Internal gains) | 7.0 | |
| infil | stated | infiltration | 0.000302 m3/s per m2 of exterior surface, constant | input2.txt (Internal gains and infiltration) | [0.0003] | |
| annual | assumed | simulation | annual run (not stated; customary) |  | True | |
| hvac-type | stated | hvac | central ducted air-source heat pump on one air loop | input2.txt (HVAC) | central_ashp | |
| air-loops | stated | hvac | one AirLoopHVAC | input2.txt (HVAC) | 1 | |
| cop-cool | stated | hvac | cooling COP 3.666 | input2.txt (HVAC) | 3.666 | |
| cop-heat | stated | hvac | heating COP 2.75 | input2.txt (HVAC) | 2.75 | |
| all-electric | stated | hvac | all electric (backup is electric resistance) | input2.txt (Fuel and use) | ['Electricity'] | |
| hsp | stated | control | heating setpoint 21 C all year | input2.txt (HVAC) | 21.0 | |
| csp | stated | control | cooling setpoint 24 C all year | input2.txt (HVAC) | 24.0 | |
| no-setback | stated | control | no setback | input2.txt (HVAC) | [21.0] | |
| weather | assumed | site | weather file not named; a station near Lupton AZ (Gallup NM) is expected |  | Gallup.Muni.AP NM USA SRC-TMYx WMO#=723627 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
