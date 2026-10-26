# Review packet: V03-small-office-seattle

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Seattle, WA | brief.md | 47.47 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 2 storeys | brief.md | 2 | |
| cfa | derived | geometry | conditioned floor area 1560.0 m2 | brief.md | 1560.0 | |
| height | stated | geometry | 2 x 3.87 m floor to floor = 7.74 m | floorplan.png | 7.74 | |
| zones | stated | geometry | 10 thermal zones | brief.md | 10 | |
| wwr-N | derived | fenestration | true-N window-to-wall ratio 0.360 | brief.md | 0.36 | |
| wwr-E | derived | fenestration | true-E window-to-wall ratio 0.260 | brief.md | 0.26 | |
| wwr-S | derived | fenestration | true-S window-to-wall ratio 0.260 | brief.md | 0.26 | |
| wwr-W | derived | fenestration | true-W window-to-wall ratio 0.380 | brief.md | 0.38 | |
| win-area | derived | fenestration | total window area 289.2 m2 | brief.md | 289.14 | |
| win-u | stated | fenestration | window U 2.73 W/m2K | brief.md | 2.733 | |
| win-shgc | stated | fenestration | SHGC 0.36 | brief.md | 0.361 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-E facade | brief.md | {'E': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.495 W/m2K | brief.md | 0.495 | |
| roof-u | stated | envelope | roof U (no films) 0.158 W/m2K | brief.md | 0.158 | |
| slab | stated | envelope | slab on grade | brief.md | 5 | |
| lpd | stated | loads | lighting 10.18 W/m2 | brief.md | 10.18 | |
| epd | stated | loads | plug loads 9.39 W/m2 | brief.md | 9.39 | |
| people | derived | loads | 75.5 occupants | brief.md | 75.5002 | |
| eflh-light | derived | schedules | lighting full-load hours 3046 h/yr | brief.md | 3045.7813 | |
| eflh-equip | derived | schedules | plug-load full-load hours 4469 h/yr | brief.md | 4468.8233 | |
| ach | assumed | infiltration | infiltration 0.05-1.0 ACH |  | 0.23 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.47 | brief.md | 3.47 | |
| cop-heat | stated | hvac | heating COP 3.05 | brief.md | 3.05 | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
