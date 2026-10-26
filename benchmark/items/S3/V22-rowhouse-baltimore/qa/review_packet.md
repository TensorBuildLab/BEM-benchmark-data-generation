# Review packet: V22-rowhouse-baltimore

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Baltimore, MD | brief.md | 39.17 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 2 storeys | brief.md | 2 | |
| cfa | derived | geometry | conditioned floor area 155.0 m2 | brief.md | 155.0 | |
| height | stated | geometry | 2 x 2.83 m floor to floor = 5.66 m | brief.md | 5.66 | |
| zones | stated | geometry | 2 thermal zones | brief.md | 2 | |
| party | stated | envelope | party wall(s) adiabatic | brief.md | 4 | |
| wwr-N | stated | fenestration | true-N window-to-wall ratio 0.200 | brief.md | 0.2 | |
| wwr-S | stated | fenestration | true-S window-to-wall ratio 0.390 | brief.md | 0.3896 | |
| win-area | derived | fenestration | total window area 20.7 m2 | brief.md | 20.69 | |
| win-u | stated | fenestration | window U 3.22 W/m2K | brief.md | 3.224 | |
| win-shgc | stated | fenestration | SHGC 0.34 | brief.md | 0.341 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.337 W/m2K | brief.md | 0.337 | |
| roof-u | stated | envelope | roof U (no films) 0.296 W/m2K | brief.md | 0.296 | |
| slab | stated | envelope | slab on grade | brief.md | 1 | |
| lpd | stated | loads | lighting 3.54 W/m2 | brief.md | 3.54 | |
| epd | stated | loads | plug loads 3.49 W/m2 | brief.md | 3.49 | |
| people | stated | loads | 2.0 occupants | brief.md | 2.0 | |
| eflh-light | derived | schedules | lighting full-load hours 2123 h/yr | brief.md | 2121.1753 | |
| eflh-equip | derived | schedules | plug-load full-load hours 3886 h/yr | brief.md | 3887.1943 | |
| ach | stated | infiltration | infiltration 0.22 ACH | brief.md | 0.2199 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.45 (EER 11.8) | brief.md | 3.45 | |
| cop-heat | stated | hvac | heating COP 3.28 | brief.md | 3.28 | |
| hsp | stated | control | heating setpoint 20.6 C | brief.md | 20.6 | |
| csp | stated | control | cooling setpoint 25.3 C | brief.md | 25.3 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
