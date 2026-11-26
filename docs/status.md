# Implementation status

Reviewed against the integration checkout on 2026-11-26. This is a source
inventory, not a release certification or a record of passing tests. This
documentation review ran no builds, tests, or benchmarks.

## Present in the source

| Area | Current scope | Primary guide |
| --- | --- | --- |
| Python/C++ runtimes | Native loading, managed lifecycle, script slots, guarded calls, and native handover. | [Runtime lifecycle](runtime-lifecycle.md) |
| Language adapters | Generated RPC calls and remote configure/cleanup. | [Component connections](component_connection.md) |
| Registration | Dependency-aware registration, parallel C++ compilation, build profiles, and registry migration. | [Registry](registry.md) |
| Composition | Saved components, executable parameters, script configurations, CLI, and GUIs. | [Workspaces](workspaces.md) |
| Shared robotics contracts | Flat field layouts, routes, horizons, state buffers, references, mission monitors, control, models, estimation, and hardware schemas. | [Interfaces](interfaces/README.md) |
| Control | Native script, cascades, PID/RPP controllers, generators, mapper, monitors, ROS navigation inputs, and FollowPath adapter. | [Control execution](interfaces/control/control-stack-and-message-map.md) |
| Estimation | Generic EKF/UKF and navigation composition in rpp_localization, worker execution, and bounded replay. | [Estimation](interfaces/estimation/generic-estimation-and-localization.md) |
| Examples | Six core tutorials and communication benchmarks in rpp_demos; bag parity tooling in rpp_localization. | [Tutorials](tutorials/README.md), [benchmarks](benchmarks/README.md) |

## Unsupported or future work

- Adapted activation/deactivation and typed handover remain unsupported; ordinary
  RPC calls and remote configure/cleanup do not imply full native lifecycle parity.
- Remote-machine deployment is planned; the ordinary adapter path uses local
  component-server processes.
- rpp_navigation is a scaffold, not a second implemented navigation stack.
  Current FollowPath integration lives in rpp_control.
- A separate rpp_estimation package, CasADi control adapters, MPC packages, and
  whole-body control remain proposed extensions.
- Current generic Gaussian cores support Euclidean/scalar-angle states.
  Quaternion field descriptors do not establish quaternion-filter support.
- Hardware contracts exist; end-to-end physical-driver integration depends on
  the selected application. Generic image/scan interfaces remain future work.
- The integrated localization demo in rpp_demos is planned. The existing
  rpp_localization launch files and bag benchmark are separate runnable sources.

## Evidence and compatibility

Consult each implementation's CI and a specific saved benchmark run for verified
results. Historical reports describe their recorded revisions and settings.
Do not present a schema annotation or prepared buffer as proof that every call
path is allocation-free or meets a deadline.

Generators, runtimes, generated interfaces, and compiled plugins must be kept
compatible. Rebuilding a ROS executable does not refresh registered native
plugins. See [generated-code compatibility](registry.md#generated-code-compatibility).
Shared Cap'n Proto contract version 1 and native C++ ABI compatibility are
separate concerns.

Historical lifecycle decisions and checkpoint results remain under
[plans](plans/README.md); current guides take precedence.
