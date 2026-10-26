# Review packet: V08-medium-office-rochester

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Rochester, MN | brief.md | 43.9 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 3 storeys | brief.md | 3 | |
| cfa | derived | geometry | conditioned floor area 5088.0 m2 | brief.md | 5088.0 | |
| height | stated | geometry | 3 x 3.74 m floor to floor = 11.22 m | brief.md | 11.22 | |
| zones | stated | geometry | 15 thermal zones | brief.md | 15 | |
| wwr-N | stated | fenestration | true-N window-to-wall ratio 0.400 | brief.md | 0.4 | |
| wwr-E | stated | fenestration | true-E window-to-wall ratio 0.330 | brief.md | 0.33 | |
| wwr-S | stated | fenestration | true-S window-to-wall ratio 0.230 | brief.md | 0.23 | |
| wwr-W | stated | fenestration | true-W window-to-wall ratio 0.230 | brief.md | 0.23 | |
| win-area | derived | fenestration | total window area 575.7 m2 | brief.md | 575.7 | |
| win-u | stated | fenestration | window U 1.89 W/m2K | brief.md | 1.891 | |
| win-shgc | stated | fenestration | SHGC 0.34 | brief.md | 0.34 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | derived | envelope | wall U (no films) 0.337 W/m2K | brief.md | 0.337 | |
| roof-u | derived | envelope | roof U (no films) 0.158 W/m2K | brief.md | 0.158 | |
| slab | stated | envelope | slab on grade | brief.md | 5 | |
| lpd | constrained | loads | ASHRAE 90.1-2019 office LPD 0.64 W/ft2 (6.89 W/m2) | brief.md | 6.889 | |
| epd | stated | loads | plug loads 8.74 W/m2 | brief.md | 8.74 | |
| people | derived | loads | 213.2 occupants | brief.md | 213.1896 | |
| eflh-light | derived | schedules | lighting full-load hours 3046 h/yr | brief.md | 3045.7798 | |
| eflh-equip | derived | schedules | plug-load full-load hours 4469 h/yr | brief.md | 4468.7689 | |
| ach | stated | infiltration | infiltration 0.24 ACH | brief.md | 0.24 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.58 (EER 12.2) | brief.md | 3.58 | |
| cop-heat | stated | hvac | heating COP 3.55 | brief.md | 3.55 | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
