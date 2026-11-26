# Control dependencies and extensions

The current [control execution guide](control-stack-and-message-map.md) describes
implemented routing and ROS integration. This page records dependency boundaries;
it does not introduce a second control contract or implementation sequence.

## Dependency boundaries

| Layer | Responsibility |
| --- | --- |
| `rpp_interfaces` | Shared numeric contracts and field-layout/routing helpers. |
| `rpp_common` | Common annotations, messages, and neutral utilities. |
| `rpp_cpp` / `rpp_py` | Component construction, parameters, lifecycle, guarded calls, and adapters. |
| `rpp_control` | Control script, reference generators, controllers, mappers, monitors, and optional ROS adapter. |
| `rpp_localization` | Generic estimation, navigation models, and ROS sensor/estimate adapters. |
| MORE libraries | Dynamics/sensor definitions, graph utilities, and simulation. |

The numeric control core does not require ROS message handling or CasADi.
The ROS adapter owns subscriptions, services, actions, conversion, and publication.
Selecting a graph-backed model or optimization plugin brings that extension's
dependencies into the application.

## Future extensions

Prepared CasADi model/derivative adapters, MPC, and articulated or combined
vehicle/arm compositions remain extensions. Proposed package names such as
`rpp_control_casadi`, `rpp_control_mpc`, and `rpp_estimation` do not identify
implemented packages in the current checkout.

Reuse shared physical definitions across simulation, estimation, and control
where their state conventions, frames, inputs, and integration methods agree.
Each consumer keeps its own mutable state and workspace. A simulation model is
not automatically a compatible estimator or controller model.

See [implementation status](../../status.md) for available source and remaining
integration work, and [component boundaries](../component-boundaries.md) for
the responsibilities an extension must preserve.
