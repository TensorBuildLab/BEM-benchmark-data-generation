# Review packet: V19-house-fairbanks

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Fairbanks, AK | brief.md | 64.82 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 1 storeys | brief.md | 1 | |
| cfa | derived | geometry | conditioned floor area 160.3 m2 | brief.md | 160.29 | |
| height | stated | geometry | 1 x 2.93 m floor to floor = 2.93 m | brief.md | 2.93 | |
| zones | stated | geometry | 2 thermal zones | brief.md | 2 | |
| garage | stated | geometry | attached garage is unconditioned | brief.md | 1 | |
| wwr-N | derived | fenestration | true-N window-to-wall ratio 0.140 | brief.md | 0.14 | |
| wwr-E | derived | fenestration | true-E window-to-wall ratio 0.096 | brief.md | 0.0959 | |
| wwr-S | derived | fenestration | true-S window-to-wall ratio 0.000 | brief.md | 0.0 | |
| wwr-W | derived | fenestration | true-W window-to-wall ratio 0.123 | brief.md | 0.1233 | |
| win-area | derived | fenestration | total window area 17.6 m2 | brief.md | 17.65 | |
| win-u | stated | fenestration | window U 1.67 W/m2K | brief.md | 1.67 | |
| win-shgc | stated | fenestration | SHGC 0.38 | brief.md | 0.381 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-W facade | brief.md | {'W': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.198 W/m2K | brief.md | 0.198 | |
| roof-u | stated | envelope | roof U (no films) 0.296 W/m2K | brief.md | 0.296 | |
| slab | stated | envelope | slab on grade | brief.md | 2 | |
| lpd | stated | loads | lighting 4.99 W/m2 | brief.md | 4.99 | |
| epd | stated | loads | plug loads 5.80 W/m2 | brief.md | 5.8 | |
| people | stated | loads | 4.0 occupants | brief.md | 4.0 | |
| eflh-light | derived | schedules | lighting full-load hours 2123 h/yr | brief.md | 2121.9333 | |
| eflh-equip | derived | schedules | plug-load full-load hours 3886 h/yr | brief.md | 3887.2312 | |
| ach | assumed | infiltration | infiltration 0.05-1.0 ACH |  | 0.4 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 4.12 | brief.md | 4.12 | |
| cop-heat | stated | hvac | heating COP 3.06 | brief.md | 3.06 | |
| hsp | stated | control | heating setpoint 20.1 C | brief.md | 20.1 | |
| csp | stated | control | cooling setpoint 24.9 C | brief.md | 24.9 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
