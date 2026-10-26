# Review packet: V14-school-helena

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Helena, MT | brief.md | 46.6 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 1 storeys | brief.md | 1 | |
| cfa | derived | geometry | conditioned floor area 1327.0 m2 | brief.md | 1327.0 | |
| height | stated | geometry | 1 x 4.12 m floor to floor = 4.12 m | floorplan.png | 4.12 | |
| zones | stated | geometry | 1 thermal zones | brief.md | 1 | |
| wwr-N | stated | fenestration | true-N window-to-wall ratio 0.280 | brief.md | 0.28 | |
| wwr-E | stated | fenestration | true-E window-to-wall ratio 0.250 | brief.md | 0.25 | |
| wwr-S | stated | fenestration | true-S window-to-wall ratio 0.350 | brief.md | 0.35 | |
| wwr-W | stated | fenestration | true-W window-to-wall ratio 0.390 | brief.md | 0.39 | |
| win-area | derived | fenestration | total window area 279.3 m2 | brief.md | 279.32 | |
| win-u | stated | fenestration | window U 2.19 W/m2K | brief.md | 2.191 | |
| win-shgc | stated | fenestration | SHGC 0.30 | brief.md | 0.301 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.495 W/m2K | brief.md | 0.495 | |
| roof-u | stated | envelope | roof U (no films) 0.237 W/m2K | brief.md | 0.237 | |
| slab | stated | envelope | slab on grade | brief.md | 1 | |
| lpd | stated | loads | lighting 7.12 W/m2 | brief.md | 7.12 | |
| epd | stated | loads | plug loads 4.02 W/m2 | brief.md | 4.02 | |
| people | derived | loads | 245.1 occupants | brief.md | 245.1 | |
| eflh-light | derived | schedules | lighting full-load hours 2427 h/yr | brief.md | 2426.9658 | |
| eflh-equip | derived | schedules | plug-load full-load hours 4032 h/yr | brief.md | 4031.9003 | |
| ach | stated | infiltration | infiltration 0.45 ACH | brief.md | 0.4497 | |
| hvac | stated | hvac | HVAC: pthp | brief.md | pthp | |
| cop-cool | stated | hvac | cooling COP 3.02 (EER 10.3) | brief.md | 3.02 | |
| cop-heat | stated | hvac | heating COP 3.03 | brief.md | 3.03 | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
