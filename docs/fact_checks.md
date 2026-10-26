# Fact checks and model facts

## Check language

| Key | Meaning |
| --- | --- |
| `path` | dotted path into the model facts; `[glob]` selects dictionary entries by name, e.g. `control.zones[*BATH*].heating_setpoint` |
| `op` | `eq`, `ne`, `approx` (with `tol` and/or `rtol`), `range` (`min`, `max`), `gt`, `ge`, `lt`, `le`, `in` (list), `contains`, `not_contains`, `true`, `false`, `exists`, `absent` |
| `agg` | for paths that return several values: `all` (default), `any`, `sum`, `mean`, `min`, `max`, `count` |
| `scale` | multiply the observed value before comparing |
| `any_of`, `all_of` | combine sub-checks; used to accept equivalent modelling idioms |

A check that cannot be evaluated (the fact is missing from the model) returns *not verified*. In QA of a reference this becomes a manual-check finding; in scoring of a candidate it counts as not satisfied.

## Model facts (selection)

| Path | Source |
| --- | --- |
| `site.latitude`, `site.elevation`, `site.north_axis` | `Site:Location`, `Building` (falls back to the location EnergyPlus used) |
| `meta.weather_file`, `meta.run_period`, `meta.annual_run`, `meta.timestep`, `meta.schedule_files`, `meta.pv_dc_kw` | input and SQLite |
| `geometry.total_floor_area`, `conditioned_floor_area`, `n_zones`, `n_conditioned_zones`, `n_levels`, `building_height`, `volume_total`, `conditioned_volume`, `underground_wall_area`, `boundary_conditions`, `zones[NAME].*` | SQLite `Zones` and tabular reports |
| `fenestration.wwr.{N,E,S,W,total}`, `window_area.*`, `gross_wall_area.*`, `window_area_total`, `window_u`, `window_shgc`, `window_vt`, `n_windows`, `n_doors` (opaque), `n_glass_doors`, `n_doors_all`, `door_area_total`, `door_area_by_construction`, `doors_by_direction`, `doors_by_direction_all` | Envelope Summary, Input Verification |
| `envelope.wall_u`, `wall_u_nofilm`, `wall_u_composite`, `roof_u`, `roof_u_nofilm`, `floor_u`, `floor_u_nofilm`, `n_ground_surfaces`, `has_internal_mass` | Envelope Summary over surfaces of conditioned zones |
| `loads.people_total`, `lpd_w_m2`, `epd_w_m2`, `lpd_w_m2_conditioned`, `epd_w_m2_conditioned`, `people_per_100m2`, `activity_w_per_person_max` | SQLite nominal tables |
| `infiltration.zones[NAME].{design_flow_m3s, ach, flow_per_ext_area, coef_a..coef_d}`, `ach_design_conditioned` | `.eio` nominal infiltration statistics |
| `control.zones[NAME].{types, heating_setpoint, heating_setback, cooling_setpoint, heats, cools}`, `control.heating_setpoint`, `cooling_setpoint`, `any_heating`, `any_cooling` | expanded input + schedule ranges |
| `hvac.primary`, `tags`, `n_air_loops`, `heating_fuels`, `cooling_cop(s)`, `heating_cop(s)` | expanded input |
| `results.heating_gj`, `cooling_gj`, `site_energy_gj`, `eui_mj_m2`, `end_uses_gj`, `unmet_*_h`, `design_*_load_w`, `internal_gains_gj`, `lighting_eflh_h`, `equipment_eflh_h` | ABUPS, System Summary, run-period outputs |
| `provenance.tagged_fraction` | `! source:` comments in the input |
