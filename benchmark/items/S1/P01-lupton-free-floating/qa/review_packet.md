# Review packet: P01-lupton-free-floating

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | latitude 35.06 N | input1.txt (Overview) | 35.06 | |
| site-lon | stated | site | longitude 109.08 W | input1.txt (Overview) | -109.08 | |
| site-elev | stated | site | elevation 1780 m | input1.txt (Overview) | 1780.0 | |
| weather | stated | site | nearest weather file: Gallup NM | input1.txt (Overview) | Gallup.Muni.AP NM USA SRC-TMYx WMO#=723627 | |
| zones | stated | geometry | single zone | input1.txt (Overview) | 1 | |
| floor-area | derived | geometry | floor area 167.7 + 14.7 + 13.8 = 196.2 m2 | input1.txt (Geometry) | 196.11 | |
| height | stated | geometry | envelope height 4.445 m (flat roof at z = 4.445 m) | input1.txt (Geometry) | 4.445 | |
| slab | stated | envelope | slab on grade | input1.txt (Geometry) | 1 | |
| roof-u | stated | envelope | roof U about 0.2 W/m2K from the foam alone | input1.txt (Geometry) | 0.19 | |
| wall-u | assumed | envelope | 9 in. adobe wall: U (no film) 1.4-3.2 W/m2K for k 0.5-1.0 W/mK |  | 2.953 | |
| internal-mass | stated | envelope | 14.86 m2 internal mass | input1.txt (Geometry) | True | |
| win-count | stated | fenestration | 6 windows (2 on SE, 2 on SW, 1 S, 1 W) | input1.txt (Openings table) | 6 | |
| door-count | stated | fenestration | 2 wood doors (SE and SW) | input1.txt (Openings table) | 2 | |
| door-area | derived | fenestration | doors 3'2" x 7' = 2.06 m2 each, 4.12 m2 total | input1.txt (Openings table) | 4.12 | |
| win-north | stated | fenestration | no openings on the north, NE and NW faces | input1.txt (Openings table) | 0.0 | |
| win-u | stated | fenestration | glazing U 2.05 W/m2K | input1.txt (Openings) | 2.051 | |
| win-shgc | stated | fenestration | SHGC 0.40 | input1.txt (Openings) | 0.401 | |
| people | stated | loads | 4 occupants | input1.txt (Internal gains) | 4.0 | |
| activity | stated | loads | 120 W per person | input1.txt (Internal gains) | 120.0 | |
| lpd | stated | loads | LED lighting 5 W/m2 | input1.txt (Internal gains) | 5.0 | |
| epd | stated | loads | appliances 7 W/m2 | input1.txt (Internal gains) | 7.0 | |
| infil | stated | infiltration | 0.000302 m3/s per m2 of exterior surface, constant | input1.txt (Internal gains and infiltration) | [0.0003] | |
| no-hvac | stated | hvac | no HVAC at all | input1.txt (Overview) | none | |
| no-thermostat | stated | control | no thermostat (free-floating) | input1.txt (Overview) | 0 | |
| annual | assumed | simulation | annual run (not stated; customary) |  | True | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
