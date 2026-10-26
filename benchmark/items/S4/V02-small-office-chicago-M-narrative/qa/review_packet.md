# Review packet: V02-small-office-chicago-M-narrative

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Chicago, IL | brief.md | 41.98 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 2 storeys | brief.md | 2 | |
| cfa | derived | geometry | conditioned floor area 1296.0 m2 | brief.md | 1296.0 | |
| height | stated | geometry | 2 x 3.87 m floor to floor = 7.74 m | brief.md | 7.74 | |
| zones | stated | geometry | 10 thermal zones | brief.md | 10 | |
| wwr-N | stated | fenestration | true-N window-to-wall ratio 0.270 | brief.md | 0.27 | |
| wwr-E | stated | fenestration | true-E window-to-wall ratio 0.340 | brief.md | 0.34 | |
| wwr-S | stated | fenestration | true-S window-to-wall ratio 0.330 | brief.md | 0.33 | |
| wwr-W | stated | fenestration | true-W window-to-wall ratio 0.330 | brief.md | 0.33 | |
| win-area | derived | fenestration | total window area 260.5 m2 | brief.md | 260.52 | |
| win-u | stated | fenestration | window U 1.49 W/m2K | brief.md | 1.49 | |
| win-shgc | stated | fenestration | SHGC 0.34 | brief.md | 0.341 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | derived | envelope | wall U (no films) 0.495 W/m2K | brief.md | 0.495 | |
| roof-u | derived | envelope | roof U (no films) 0.237 W/m2K | brief.md | 0.237 | |
| slab | stated | envelope | slab on grade | brief.md | 5 | |
| lpd | stated | loads | lighting 7.53 W/m2 | brief.md | 7.53 | |
| epd | stated | loads | plug loads 10.97 W/m2 | brief.md | 10.97 | |
| people | derived | loads | 74.8 occupants | brief.md | 74.78 | |
| eflh-light | derived | schedules | lighting full-load hours 3046 h/yr | brief.md | 3045.6592 | |
| eflh-equip | derived | schedules | plug-load full-load hours 4469 h/yr | brief.md | 4468.7907 | |
| ach | stated | infiltration | infiltration 0.42 ACH | brief.md | 0.4194 | |
| hvac | stated | hvac | HVAC: ideal | brief.md | ideal_loads | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
