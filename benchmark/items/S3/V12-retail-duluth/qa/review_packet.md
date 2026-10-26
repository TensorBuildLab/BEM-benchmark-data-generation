# Review packet: V12-retail-duluth

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Duluth, MN | brief.md | 46.83 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 1 storeys | brief.md | 1 | |
| cfa | derived | geometry | conditioned floor area 1650.0 m2 | brief.md | 1650.0 | |
| height | stated | geometry | 1 x 5.19 m floor to floor = 5.19 m | brief.md | 5.19 | |
| zones | stated | geometry | 1 thermal zones | brief.md | 1 | |
| wwr-N | derived | fenestration | true-N window-to-wall ratio 0.000 | brief.md | 0.0 | |
| wwr-E | derived | fenestration | true-E window-to-wall ratio 0.050 | brief.md | 0.05 | |
| wwr-S | derived | fenestration | true-S window-to-wall ratio 0.310 | brief.md | 0.31 | |
| wwr-W | derived | fenestration | true-W window-to-wall ratio 0.050 | brief.md | 0.05 | |
| win-area | derived | fenestration | total window area 97.6 m2 | brief.md | 97.57 | |
| win-u | stated | fenestration | window U 2.16 W/m2K | brief.md | 2.161 | |
| win-shgc | stated | fenestration | SHGC 0.34 | brief.md | 0.341 | |
| doors | stated | fenestration | 2 exterior door(s) | brief.md | 2 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1, 'N': 1} | |
| door-N | stated | fenestration | entrance on the true-N facade | brief.md | {'S': 1, 'N': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.495 W/m2K | brief.md | 0.495 | |
| roof-u | stated | envelope | roof U (no films) 0.237 W/m2K | brief.md | 0.237 | |
| slab | stated | envelope | slab on grade | brief.md | 1 | |
| lpd | stated | loads | lighting 10.36 W/m2 | brief.md | 10.36 | |
| epd | stated | loads | plug loads 4.98 W/m2 | brief.md | 4.98 | |
| people | derived | loads | 221.8 occupants | brief.md | 221.76 | |
| eflh-light | assumed | schedules | lighting full-load hours 1,200-4,500 h/yr |  | 3980.7665 | |
| ach | stated | infiltration | infiltration 0.58 ACH | brief.md | 0.5801 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.65 (EER 12.5) | brief.md | 3.65 | |
| cop-heat | stated | hvac | heating COP 3.20 | brief.md | 3.2 | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
