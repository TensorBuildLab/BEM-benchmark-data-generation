# Review packet: V23-rowhouse-seattle

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Seattle, WA | brief.md | 47.47 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 2 storeys | brief.md | 2 | |
| cfa | derived | geometry | conditioned floor area 163.5 m2 | brief.md | 163.52 | |
| height | stated | geometry | 2 x 3.09 m floor to floor = 6.18 m | brief.md | 6.18 | |
| zones | stated | geometry | 2 thermal zones | brief.md | 2 | |
| party | stated | envelope | party wall(s) adiabatic | brief.md | 4 | |
| wwr-N | derived | fenestration | true-N window-to-wall ratio 0.330 | brief.md | 0.33 | |
| wwr-S | derived | fenestration | true-S window-to-wall ratio 0.200 | brief.md | 0.2 | |
| win-area | derived | fenestration | total window area 23.9 m2 | brief.md | 23.9 | |
| win-u | stated | fenestration | window U 3.29 W/m2K | brief.md | 3.294 | |
| win-shgc | stated | fenestration | SHGC 0.33 | brief.md | 0.331 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-N facade | brief.md | {'N': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.198 W/m2K | brief.md | 0.198 | |
| roof-u | stated | envelope | roof U (no films) 0.296 W/m2K | brief.md | 0.296 | |
| slab | stated | envelope | slab on grade | brief.md | 1 | |
| lpd | stated | loads | lighting 5.99 W/m2 | brief.md | 5.99 | |
| epd | stated | loads | plug loads 6.49 W/m2 | brief.md | 6.49 | |
| people | stated | loads | 3.0 occupants | brief.md | 3.0 | |
| eflh-light | derived | schedules | lighting full-load hours 2123 h/yr | brief.md | 2124.1326 | |
| eflh-equip | derived | schedules | plug-load full-load hours 3886 h/yr | brief.md | 3886.9448 | |
| ach | stated | infiltration | infiltration 0.35 ACH | brief.md | 0.35 | |
| hvac | stated | hvac | HVAC: pthp | brief.md | pthp | |
| cop-cool | stated | hvac | cooling COP 3.32 | brief.md | 3.32 | |
| cop-heat | stated | hvac | heating COP 3.47 | brief.md | 3.47 | |
| hsp | stated | control | heating setpoint 20.7 C | brief.md | 20.7 | |
| csp | stated | control | cooling setpoint 25.0 C | brief.md | 25.0 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
