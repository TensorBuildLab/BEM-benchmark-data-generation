# Review packet: V21-rowhouse-chicago

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Chicago, IL | brief.md | 41.98 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 2 storeys | brief.md | 2 | |
| cfa | derived | geometry | conditioned floor area 167.3 m2 | brief.md | 167.28 | |
| height | stated | geometry | 2 x 2.94 m floor to floor = 5.88 m | brief.md | 5.88 | |
| zones | stated | geometry | 2 thermal zones | brief.md | 2 | |
| party | stated | envelope | party wall(s) adiabatic | brief.md | 4 | |
| wwr-N | stated | fenestration | true-N window-to-wall ratio 0.280 | brief.md | 0.28 | |
| wwr-S | stated | fenestration | true-S window-to-wall ratio 0.390 | brief.md | 0.39 | |
| win-area | derived | fenestration | total window area 26.8 m2 | brief.md | 26.8 | |
| win-u | stated | fenestration | window U 1.45 W/m2K | brief.md | 1.45 | |
| win-shgc | stated | fenestration | SHGC 0.30 | brief.md | 0.301 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | derived | envelope | wall U (no films) 0.198 W/m2K | brief.md | 0.198 | |
| roof-u | derived | envelope | roof U (no films) 0.296 W/m2K | brief.md | 0.296 | |
| slab | stated | envelope | slab on grade | brief.md | 1 | |
| lpd | stated | loads | lighting 4.43 W/m2 | brief.md | 4.43 | |
| epd | stated | loads | plug loads 4.56 W/m2 | brief.md | 4.56 | |
| people | stated | loads | 2.0 occupants | brief.md | 2.0 | |
| eflh-light | derived | schedules | lighting full-load hours 2123 h/yr | brief.md | 2121.6131 | |
| eflh-equip | derived | schedules | plug-load full-load hours 3886 h/yr | brief.md | 3885.555 | |
| ach | stated | infiltration | infiltration 0.24 ACH | brief.md | 0.2399 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.78 | brief.md | 3.78 | |
| cop-heat | stated | hvac | heating COP 3.19 | brief.md | 3.19 | |
| hsp | stated | control | heating setpoint 20.3 C | brief.md | 20.3 | |
| csp | stated | control | cooling setpoint 25.4 C | brief.md | 25.4 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
