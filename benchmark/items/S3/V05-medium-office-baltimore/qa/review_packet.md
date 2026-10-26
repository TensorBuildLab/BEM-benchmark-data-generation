# Review packet: V05-medium-office-baltimore

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Baltimore, MD | brief.md | 39.17 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 3 storeys | brief.md | 3 | |
| cfa | derived | geometry | conditioned floor area 4959.0 m2 | brief.md | 4959.0 | |
| height | stated | geometry | 3 x 3.92 m floor to floor = 11.76 m | brief.md | 11.76 | |
| zones | stated | geometry | 15 thermal zones | brief.md | 15 | |
| wwr-N | derived | fenestration | true-N window-to-wall ratio 0.220 | brief.md | 0.22 | |
| wwr-E | derived | fenestration | true-E window-to-wall ratio 0.260 | brief.md | 0.26 | |
| wwr-S | derived | fenestration | true-S window-to-wall ratio 0.390 | brief.md | 0.39 | |
| wwr-W | derived | fenestration | true-W window-to-wall ratio 0.370 | brief.md | 0.37 | |
| win-area | derived | fenestration | total window area 623.8 m2 | brief.md | 623.76 | |
| win-u | stated | fenestration | window U 2.20 W/m2K | brief.md | 2.201 | |
| win-shgc | stated | fenestration | SHGC 0.31 | brief.md | 0.311 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-N facade | brief.md | {'N': 1} | |
| wall-u | derived | envelope | wall U (no films) 0.355 W/m2K | brief.md | 0.355 | |
| roof-u | derived | envelope | roof U (no films) 0.237 W/m2K | brief.md | 0.237 | |
| slab | stated | envelope | slab on grade | brief.md | 5 | |
| lpd | stated | loads | lighting 8.15 W/m2 | brief.md | 8.15 | |
| epd | stated | loads | plug loads 6.37 W/m2 | brief.md | 6.37 | |
| people | derived | loads | 312.9 occupants | brief.md | 312.9096 | |
| eflh-light | derived | schedules | lighting full-load hours 3046 h/yr | brief.md | 3045.766 | |
| eflh-equip | derived | schedules | plug-load full-load hours 4469 h/yr | brief.md | 4468.7913 | |
| ach | stated | infiltration | infiltration 0.18 ACH | brief.md | 0.1798 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.59 | brief.md | 3.59 | |
| cop-heat | stated | hvac | heating COP 3.59 | brief.md | 3.59 | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
