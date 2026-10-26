# Review packet: V15-school-san-francisco

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | San Francisco, CA | brief.md | 37.62 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 1 storeys | brief.md | 1 | |
| cfa | derived | geometry | conditioned floor area 1260.0 m2 | brief.md | 1260.0 | |
| height | stated | geometry | 1 x 4.02 m floor to floor = 4.02 m | brief.md | 4.02 | |
| zones | stated | geometry | 1 thermal zones | brief.md | 1 | |
| wwr-N | derived | fenestration | true-N window-to-wall ratio 0.250 | brief.md | 0.25 | |
| wwr-E | derived | fenestration | true-E window-to-wall ratio 0.260 | brief.md | 0.26 | |
| wwr-S | derived | fenestration | true-S window-to-wall ratio 0.270 | brief.md | 0.27 | |
| wwr-W | derived | fenestration | true-W window-to-wall ratio 0.260 | brief.md | 0.26 | |
| win-area | derived | fenestration | total window area 217.4 m2 | brief.md | 217.4 | |
| win-u | stated | fenestration | window U 2.08 W/m2K | brief.md | 2.081 | |
| win-shgc | stated | fenestration | SHGC 0.32 | brief.md | 0.321 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.495 W/m2K | brief.md | 0.495 | |
| roof-u | stated | envelope | roof U (no films) 0.237 W/m2K | brief.md | 0.237 | |
| slab | stated | envelope | slab on grade | brief.md | 1 | |
| lpd | stated | loads | lighting 8.73 W/m2 | brief.md | 8.73 | |
| epd | stated | loads | plug loads 6.62 W/m2 (server room excluded) | brief.md | 6.62 | |
| people | derived | loads | 289.3 occupants | brief.md | 289.3 | |
| eflh-light | derived | schedules | lighting full-load hours 2427 h/yr | brief.md | 2427.0643 | |
| eflh-equip | derived | schedules | plug-load full-load hours 4032 h/yr | brief.md | 4031.8606 | |
| ach | assumed | infiltration | infiltration 0.05-1.0 ACH |  | 0.3298 | |
| hvac | stated | hvac | HVAC: ptac | brief.md | ptac | |
| cop-cool | stated | hvac | cooling COP 3.20 | brief.md | 3.2 | |
| hsp | assumed | control | heating setpoint 18-23 C |  | 21.0 | |
| csp | assumed | control | cooling setpoint 23-27 C |  | 24.0 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
