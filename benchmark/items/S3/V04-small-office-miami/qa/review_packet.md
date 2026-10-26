# Review packet: V04-small-office-miami

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Miami, FL | brief.md | 25.82 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 2 storeys | brief.md | 2 | |
| cfa | derived | geometry | conditioned floor area 1326.0 m2 | brief.md | 1326.0 | |
| height | stated | geometry | 2 x 3.75 m floor to floor = 7.50 m | brief.md | 7.5 | |
| zones | stated | geometry | 10 thermal zones | brief.md | 10 | |
| wwr-N | derived | fenestration | true-N window-to-wall ratio 0.400 | brief.md | 0.4 | |
| wwr-E | derived | fenestration | true-E window-to-wall ratio 0.230 | brief.md | 0.23 | |
| wwr-S | derived | fenestration | true-S window-to-wall ratio 0.370 | brief.md | 0.37 | |
| wwr-W | derived | fenestration | true-W window-to-wall ratio 0.320 | brief.md | 0.32 | |
| win-area | derived | fenestration | total window area 295.4 m2 | brief.md | 295.34 | |
| win-u | stated | fenestration | window U 3.32 W/m2K | brief.md | 3.324 | |
| win-shgc | stated | fenestration | SHGC 0.23 | brief.md | 0.231 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.337 W/m2K | brief.md | 0.337 | |
| roof-u | stated | envelope | roof U (no films) 0.237 W/m2K | brief.md | 0.237 | |
| slab | stated | envelope | slab on grade | brief.md | 5 | |
| lpd | stated | loads | lighting 9.42 W/m2 | brief.md | 9.42 | |
| epd | stated | loads | plug loads 9.14 W/m2 | brief.md | 9.14 | |
| people | derived | loads | 64.0 occupants | brief.md | 64.0502 | |
| eflh-light | derived | schedules | lighting full-load hours 3046 h/yr | brief.md | 3045.768 | |
| eflh-equip | derived | schedules | plug-load full-load hours 4469 h/yr | brief.md | 4468.8713 | |
| ach | stated | infiltration | infiltration 0.19 ACH | brief.md | 0.19 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.85 (EER 13.1) | brief.md | 3.85 | |
| cop-heat | stated | hvac | heating COP 3.19 | brief.md | 3.19 | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6, 15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
