# Review packet: V01-small-office-phoenix

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Phoenix, AZ | brief.md | 33.45 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 2 storeys | brief.md | 2 | |
| cfa | derived | geometry | conditioned floor area 1178.0 m2 | brief.md | 1178.0 | |
| height | stated | geometry | 2 x 3.62 m floor to floor = 7.24 m | brief.md | 7.24 | |
| zones | stated | geometry | 10 thermal zones | brief.md | 10 | |
| wwr-N | stated | fenestration | true-N window-to-wall ratio 0.260 | brief.md | 0.26 | |
| wwr-E | stated | fenestration | true-E window-to-wall ratio 0.360 | brief.md | 0.36 | |
| wwr-S | stated | fenestration | true-S window-to-wall ratio 0.310 | brief.md | 0.31 | |
| wwr-W | stated | fenestration | true-W window-to-wall ratio 0.210 | brief.md | 0.21 | |
| win-area | derived | fenestration | total window area 206.3 m2 | brief.md | 206.34 | |
| win-u | stated | fenestration | window U 2.85 W/m2K | brief.md | 2.853 | |
| win-shgc | stated | fenestration | SHGC 0.25 | brief.md | 0.251 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.495 W/m2K | brief.md | 0.495 | |
| roof-u | stated | envelope | roof U (no films) 0.237 W/m2K | brief.md | 0.237 | |
| slab | stated | envelope | slab on grade | brief.md | 5 | |
| lpd | constrained | loads | ASHRAE 90.1-2019 office LPD 0.64 W/ft2 (6.89 W/m2) | brief.md | 6.889 | |
| epd | stated | loads | plug loads 9.42 W/m2 (server room excluded) | brief.md | 9.42 | |
| people | derived | loads | 49.8 occupants | brief.md | 49.83 | |
| eflh-light | derived | schedules | lighting full-load hours 3046 h/yr | brief.md | 3045.7091 | |
| eflh-equip | derived | schedules | plug-load full-load hours 4469 h/yr | brief.md | 4468.7719 | |
| ach | stated | infiltration | infiltration 0.24 ACH | brief.md | 0.24 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.87 | brief.md | 3.87 | |
| cop-heat | stated | hvac | heating COP 3.32 | brief.md | 3.32 | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
