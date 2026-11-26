# How the control packages fit together

The control script runs reference generators, controllers, and actuation
mappers. RPP supplies their configuration and lifecycle. The ROS node receives
measurements and goals, passes them to the script, and publishes its outputs.

| Package | Responsibility |
| --- | --- |
| `rpp_interfaces` | Shared numeric contracts and field-layout/routing helpers. |
| `rpp_common` | Common annotations, messages, and utilities. |
| `rpp_cpp` / `rpp_py` | Component construction, parameters, lifecycle, calls, and adapters. |
| `rpp_control` | Control script, reference generators, controllers, mappers, monitors, and ROS adapter. |
| `rpp_localization` | Estimation algorithms, navigation models, and sensor/estimate adapters. |
| MORE libraries | Dynamics and sensor models, graph utilities, and simulation. |

The numeric control loop runs separately from ROS message handling. The ROS
executor performs conversion and publication; the worker calls the script.

For example, a pose goal arrives as a ROS message. The node checks its frame,
ownership, and deadline, converts it to the configured goal layout, and stages
it in the reference generator. The worker then samples that generator and runs
the controllers. ROS message types stay at the adapter boundary; controllers
receive the flat state and reference arrays declared by their interfaces.

This also explains the package split. A controller implementation lives in
`rpp_control`, while its shared contract lives in `rpp_interfaces`. Applications
can use that contract without importing the controller's implementation. The
runtime loads the selected implementation from its registration and workspace
configuration.

See [control execution](control-stack-and-message-map.md) for the loop and
[component boundaries](../component-boundaries.md) for what each plugin receives
and returns.
