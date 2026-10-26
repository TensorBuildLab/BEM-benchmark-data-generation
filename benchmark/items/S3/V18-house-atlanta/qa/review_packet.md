# Review packet: V18-house-atlanta

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | stated | site | Atlanta, GA | brief.md | 33.63 | |
| annual | stated | simulation | full-year simulation (task) | task.md | True | |
| levels | stated | geometry | 2 storeys | brief.md | 2 | |
| cfa | derived | geometry | conditioned floor area 372.1 m2 | brief.md | 372.06 | |
| height | stated | geometry | 2 x 2.92 m floor to floor = 5.84 m | brief.md | 5.84 | |
| zones | stated | geometry | 3 thermal zones | brief.md | 3 | |
| garage | stated | geometry | attached garage is unconditioned | brief.md | 2 | |
| wwr-N | derived | fenestration | true-N window-to-wall ratio 0.083 | brief.md | 0.0826 | |
| wwr-E | derived | fenestration | true-E window-to-wall ratio 0.090 | brief.md | 0.09 | |
| wwr-S | derived | fenestration | true-S window-to-wall ratio 0.157 | brief.md | 0.1569 | |
| wwr-W | derived | fenestration | true-W window-to-wall ratio 0.050 | brief.md | 0.05 | |
| win-area | derived | fenestration | total window area 36.5 m2 | brief.md | 36.48 | |
| win-u | stated | fenestration | window U 3.22 W/m2K | brief.md | 3.224 | |
| win-shgc | stated | fenestration | SHGC 0.36 | brief.md | 0.361 | |
| doors | stated | fenestration | 1 exterior door(s) | brief.md | 1 | |
| door-S | stated | fenestration | entrance on the true-S facade | brief.md | {'S': 1} | |
| wall-u | derived | envelope | wall U (no films) 0.455 W/m2K | brief.md | 0.455 | |
| roof-u | derived | envelope | roof U (no films) 0.296 W/m2K | brief.md | 0.296 | |
| slab | stated | envelope | slab on grade | brief.md | 2 | |
| lpd | stated | loads | lighting 5.34 W/m2 | brief.md | 5.34 | |
| epd | stated | loads | plug loads 3.93 W/m2 | brief.md | 3.93 | |
| people | stated | loads | 3.0 occupants | brief.md | 3.0 | |
| eflh-light | derived | schedules | lighting full-load hours 2123 h/yr | brief.md | 2122.3404 | |
| eflh-equip | derived | schedules | plug-load full-load hours 3886 h/yr | brief.md | 3886.8484 | |
| ach | stated | infiltration | infiltration 0.34 ACH | brief.md | 0.34 | |
| hvac | stated | hvac | HVAC: psz_hp | brief.md | central_ashp | |
| cop-cool | stated | hvac | cooling COP 3.67 | brief.md | 3.67 | |
| cop-heat | stated | hvac | heating COP 3.37 | brief.md | 3.37 | |
| hsp | stated | control | heating setpoint 20.7 C | brief.md | 20.7 | |
| csp | stated | control | cooling setpoint 25.2 C | brief.md | 25.2 | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
