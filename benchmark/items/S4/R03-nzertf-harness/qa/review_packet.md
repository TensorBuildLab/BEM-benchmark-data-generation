# Review packet: R03-nzertf-harness

Confirm each fact against the input documents and the reference model. Mark Agree / Disagree and note why.

| Fact | Kind | Facet | Statement | Source | Reference value | Agree? |
| --- | --- | --- | --- | --- | --- | --- |
| site-lat | derived | site | Gaithersburg MD 20899 (39.14 N) | nzertf-inputs.xlsx (SITE) |  | |
| elev | stated | site | elevation 136 m | nzertf-inputs.xlsx (SITE) |  | |
| weather | stated | site | weather file Gaithersburg-Montgomery County AP TMYx | nzertf-inputs.xlsx (SITE) |  | |
| timestep | stated | simulation | 60 time steps per hour | nzertf-inputs.xlsx (SIMULATION CONTROL) |  | |
| annual | stated | simulation | run period Jan 1 - Dec 31 | nzertf-inputs.xlsx (SIMULATION CONTROL) |  | |
| capmult | stated | simulation | temperature capacitance multiplier 7 | nzertf-inputs.xlsx (SIMULATION CONTROL) |  | |
| cfa | stated | geometry | heated and cooled floor area 386 m2 (basement, first floor, conditioned attic) | nzertf-inputs.xlsx (RESIDENTIAL FACILITY) |  | |
| levels | stated | geometry | 3 floors: 1 below ground, 2 above | nzertf-inputs.xlsx (RESIDENTIAL FACILITY) |  | |
| basement | stated | geometry | full heated basement below grade | nzertf-inputs.xlsx (Floor/Ground Coupling) |  | |
| people | stated | loads | 4 residents | nzertf-inputs.xlsx (RESIDENTIAL FACILITY) |  | |
| wwr-n | stated | fenestration | WWR 0.13 on every facade | nzertf-inputs.xlsx (Fenestration) |  | |
| win-u | stated | fenestration | window R 0.9 m2K/W (U 1.11 W/m2K) | nzertf-inputs.xlsx (Fenestration) |  | |
| win-shgc | stated | fenestration | SHGC 0.25 | nzertf-inputs.xlsx (Fenestration) |  | |
| win-vt | stated | fenestration | VT 0.4 | nzertf-inputs.xlsx (Fenestration) |  | |
| overhang | stated | geometry | external overhangs on the south | nzertf-inputs.xlsx (Fenestration) |  | |
| door | stated | fenestration | door area 40 sq ft (3.72 m2) | nzertf-inputs.xlsx (Fenestration) |  | |
| wall-u | stated | envelope | wall R 7.9 m2K/W (U 0.127 without films); unit cell garbled in the sheet | nzertf-inputs.xlsx (Wall) |  | |
| roof-u | stated | envelope | roof R 12.7 m2K/W (U 0.079); attic is conditioned so the roof is the boundary | nzertf-inputs.xlsx (Roof/Ceiling) |  | |
| hvac | stated | hvac | split air-source heat pump | nzertf-inputs.xlsx (Heating) |  | |
| cop-heat | stated | hvac | heating COP 2.65 | nzertf-inputs.xlsx (Heating) |  | |
| cop-cool | stated | hvac | cooling COP 3.82 | nzertf-inputs.xlsx (Cooling) |  | |
| erv | stated | hvac | dedicated ventilation with 78 % heat recovery | nzertf-inputs.xlsx (Air Distribution) |  | |
| dehum | stated | hvac | whole-house dehumidifier | nzertf-inputs.xlsx (Other HVAC) |  | |
| hpwh | stated | other | heat pump water heater | nzertf-inputs.xlsx (Service Hot Water) |  | |
| solar-thermal | stated | other | solar thermal water preheat | nzertf-inputs.xlsx (Service Hot Water) |  | |
| pv | stated | other | 10.24 kW PV | nzertf-inputs.xlsx (On-Site Generation) |  | |
| hsp | stated | control | heating 21 C at all times | nzertf-inputs.xlsx (General Controls) |  | |
| csp | stated | control | cooling 24 C at all times | nzertf-inputs.xlsx (General Controls) |  | |
| lpd | assumed | loads | all-LED lighting: 1-6 W/m2 |  |  | |
| tight | constrained | infiltration | ACH50 0.63 implies about 0.03 ACH natural (0.01-0.15) | nzertf-inputs.xlsx (RESIDENTIAL FACILITY) |  | |

Reviewer: ______  Date: ______  Verdict (accept / revise / reject): ______
