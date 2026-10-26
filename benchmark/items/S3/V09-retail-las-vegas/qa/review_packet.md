# Review packet: V09-retail-las-vegas

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Las Vegas, NV | brief.md | 36.072 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 1 storeys | brief.md | 1 | |
| cfa | derived | geometry | conditioned floor area 1590.0 m2 | brief.md | 1590.0 | |
| height | stated | geometry | 1 x 5.45 m floor to floor = 5.45 m | brief.md | 5.45 | |
| zones | stated | geometry | 1 thermal zones | brief.md | 1 | |
| wwr-N | stated | fenestration | true-N window-to-wall ratio 0.000 | brief.md | 0.0 | |
| wwr-E | stated | fenestration | true-E window-to-wall ratio 0.050 | brief.md | 0.05 | |
| wwr-S | stated | fenestration | true-S window-to-wall ratio 0.270 | brief.md | 0.27 | |
| wwr-W | stated | fenestration | true-W window-to-wall ratio 0.050 | brief.md | 0.05 | |
| win-area | derived | fenestration | total window area 94.3 m2 | brief.md | 94.33 | |
| win-u | stated | fenestration | window U 2.98 W/m2K | brief.md | 2.984 | |
| win-shgc | stated | fenestration | SHGC 0.39 | brief.md | 0.391 | |
| doors | stated | fenestration | 2 exterior door(s) | brief.md | 2 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1, 'N': 1} | |
| door-N | stated | fenestration | entrance on the true-N facade | brief.md | {'S': 1, 'N': 1} | |
| wall-u | stated | envelope | wall U (no films) 0.495 W/m2K | brief.md | 0.495 | |
| roof-u | stated | envelope | roof U (no films) 0.237 W/m2K | brief.md | 0.237 | |
| slab | stated | envelope | slab on grade | brief.md | 1 | |
| lpd | stated | loads | lighting 12.93 W/m2 | brief.md | 12.93 | |
| epd | stated | loads | plug loads 2.43 W/m2 (server room excluded) | brief.md | 2.43 | |
| people | derived | loads | 167.4 occupants | brief.md | 167.43 | |
| eflh-light | derived | schedules | lighting full-load hours 3981 h/yr | brief.md | 3980.7424 | |
| eflh-equip | derived | schedules | plug-load full-load hours 5129 h/yr | brief.md | 5128.9351 | |
| ach | stated | infiltration | infiltration 0.51 ACH | brief.md | 0.5102 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.51 (EER 12.0) | brief.md | 3.51 | |
| cop-heat | stated | hvac | heating COP 3.40 | brief.md | 3.4 | |
| hsp | stated | control | heating setpoint 21.0 C | brief.md | 21.0 | |
| csp | stated | control | cooling setpoint 24.0 C | brief.md | 24.0 | |
| setback | stated | control | night heating setback 15.6 C | brief.md | [15.6] | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
