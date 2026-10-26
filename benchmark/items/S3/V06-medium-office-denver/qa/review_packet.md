# Review packet: V06-medium-office-denver

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Denver, CO | brief.md | 39.83 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 3 storeys | brief.md | 3 | |
| cfa | derived | geometry | conditioned floor area 4416.0 m2 | brief.md | 4416.0 | |
| height | stated | geometry | 3 x 3.99 m floor to floor = 11.97 m | brief.md | 11.97 | |
| zones | stated | geometry | 15 thermal zones | brief.md | 15 | |
| wwr-N | stated | fenestration | true-N window-to-wall ratio 0.260 | brief.md | 0.26 | |
| wwr-E | stated | fenestration | true-E window-to-wall ratio 0.260 | brief.md | 0.26 | |
| wwr-S | stated | fenestration | true-S window-to-wall ratio 0.250 | brief.md | 0.25 | |
| wwr-W | stated | fenestration | true-W window-to-wall ratio 0.310 | brief.md | 0.31 | |
| win-area | derived | fenestration | total window area 499.1 m2 | brief.md | 499.17 | |
| win-u | stated | fenestration | window U 1.73 W/m2K | brief.md | 1.73 | |
| win-shgc | stated | fenestration | SHGC 0.33 | brief.md | 0.33 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.495 W/m2K | brief.md | 0.495 | |
| roof-u | stated | envelope | roof U (no films) 0.158 W/m2K | brief.md | 0.158 | |
| slab | stated | envelope | slab on grade | brief.md | 5 | |
| lpd | stated | loads | lighting 8.50 W/m2 | brief.md | 8.5 | |
| epd | stated | loads | plug loads 7.26 W/m2 (server room excluded) | brief.md | 7.26 | |
| people | derived | loads | 212.0 occupants | brief.md | 211.9701 | |
| eflh-light | derived | schedules | lighting full-load hours 3046 h/yr | brief.md | 3045.8168 | |
| eflh-equip | derived | schedules | plug-load full-load hours 4469 h/yr | brief.md | 4468.7689 | |
| ach | stated | infiltration | infiltration 0.19 ACH | brief.md | 0.1897 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.49 (EER 11.9) | brief.md | 3.49 | |
| cop-heat | stated | hvac | heating COP 3.25 | brief.md | 3.25 | |
| hsp | assumed | control | heating setpoint 18-23 C |  | 21.0 | |
| csp | assumed | control | cooling setpoint 23-27 C |  | 24.0 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
