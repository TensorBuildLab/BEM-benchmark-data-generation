# Review packet: V10-retail-atlanta

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Atlanta, GA | brief.md | 33.63 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 1 storeys | brief.md | 1 | |
| cfa | derived | geometry | conditioned floor area 1656.0 m2 | brief.md | 1656.0 | |
| height | stated | geometry | 1 x 5.57 m floor to floor = 5.57 m | brief.md | 5.57 | |
| zones | stated | geometry | 1 thermal zones | brief.md | 1 | |
| wwr-N | derived | fenestration | true-N window-to-wall ratio 0.050 | brief.md | 0.05 | |
| wwr-E | derived | fenestration | true-E window-to-wall ratio 0.000 | brief.md | 0.0 | |
| wwr-S | derived | fenestration | true-S window-to-wall ratio 0.050 | brief.md | 0.05 | |
| wwr-W | derived | fenestration | true-W window-to-wall ratio 0.390 | brief.md | 0.39 | |
| win-area | derived | fenestration | total window area 120.0 m2 | brief.md | 119.99 | |
| win-u | stated | fenestration | window U 2.41 W/m2K | brief.md | 2.412 | |
| win-shgc | stated | fenestration | SHGC 0.40 | brief.md | 0.401 | |
| doors | stated | fenestration | 2 exterior door(s) | brief.md | 2 | |
| door-S | stated | fenestration | entrance on the true-W facade | brief.md | {'W': 1, 'E': 1} | |
| door-N | stated | fenestration | entrance on the true-E facade | brief.md | {'W': 1, 'E': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.495 W/m2K | brief.md | 0.495 | |
| roof-u | stated | envelope | roof U (no films) 0.237 W/m2K | brief.md | 0.237 | |
| slab | stated | envelope | slab on grade | brief.md | 1 | |
| lpd | assumed | loads | lighting 9.0-17.0 W/m2 |  | 12.81 | |
| epd | assumed | loads | plug loads in a typical range |  | 3.9 | |
| eflh-light | derived | schedules | lighting full-load hours 3981 h/yr | brief.md | 3980.8509 | |
| eflh-equip | derived | schedules | plug-load full-load hours 5129 h/yr | brief.md | 5128.9793 | |
| ach | stated | infiltration | infiltration 0.35 ACH | brief.md | 0.3501 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.41 | brief.md | 3.41 | |
| cop-heat | stated | hvac | heating COP 3.38 | brief.md | 3.38 | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
