# Shared robotics interfaces

`rpp_interfaces` defines the numeric contracts used by controllers, reference
generators, state buffers, estimators, models, mission monitors, and hardware
endpoints. A contract declares what a plugin reads and returns. The plugin
implementation supplies the algorithm.

For example, `rpp_interfaces::ControlLaw` is the controller contract.
`rpp_control::PIDPoseController2D` implements it for planar pose control.
Its description declares position and yaw as inputs and body velocity as output.
The application can prepare connections from those declarations before calling
the controller.

## Descriptions explain the numbers

A flat array such as `[1, 2, 0.3]` does not say whether it contains position,
velocity, or force. Each configured plugin therefore provides `getDesc()`.
That description gives its fields names, coordinate kinds, quantities, frames,
sizes, and resources.

A planar measured-state layout built for resource `base` contains:

| Field | Values | Frame |
| --- | --- | --- |
| `base.position` | x, y | map |
| `base.orientation` | yaw | map |
| `base.linearVelocity` | vx, vy | base_link |
| `base.angularVelocity` | wz | base_link |

Its numeric state is `[x, y, yaw, vx, vy, wz]`. A pose controller needs the
first two fields; a velocity controller needs the last two. Their inputs are
prepared by field name and meaning, so neither must consume the complete
state array or assume the producer uses the same field order.

A matching name is only part of the connection. Quantities, sizes, frames, and
resources must agree too. A body-frame velocity cannot be connected to a
map-frame velocity by changing its label; an adapter must perform that conversion.

The [layout guide](shared-bind-and-runtime.md) explains those checks and the
stored/tangent dimensions.

## The calls inside a control loop

A state provider returns the latest measured sample and its acquisition time.
A reference generator uses that state and its accepted target to produce the
desired values for this tick. A controller compares the two and produces control
values. An actuation mapper converts those values into actuator commands.

For a planar cascade, the pose controller produces body velocity references.
The inner velocity controller uses measured velocity to produce force and yaw
moment. The allocator then produces the actuator commands. Each stage has a
different input/output layout even though every numeric payload is flat.

A mission monitor checks progress or another mission condition. All active
monitors can stop continuation through `isOk`. The action selects one
goal-capable monitor to decide completion through `isGoalReached`.
A generator reaching the end of its trajectory does not make that decision.

The [control guide](control/control-stack-and-message-map.md) follows a pose
goal through this chain, including ownership and expiry.

## Models and estimators

A model evaluates supplied state and input: for example, it predicts the next
state or predicts what a sensor would measure. It does not keep the vehicle's
estimate.

The estimator keeps that estimate, its covariance, and its processing history.
It predicts with the model, corrects using measurements, and returns a coherent
state/covariance sample. Measurement layouts can differ from the estimate layout;
a position measurement need not contain velocity or every other estimated value.

Generic EKF/UKF implementations live in `rpp_localization`. The
[estimation guide](estimation/generic-estimation-and-localization.md) explains
their numerical and ROS execution.

## Preparing and using a plugin

After configuring the plugin, read `getDesc()`, prepare routes and buffers,
and check the operations the application needs. For example, FollowPath requires
a generator advertising `setPath`. The generator's `bind()` prepares its
sampling horizon; other interfaces describe their layouts through configuration.

During execution, calls use the prepared field order. State, reference, control,
measurement, and matrix values are flat `List(Float64)` buffers. Time values are
unsigned nanoseconds; status uses the shared UInt8 codes. Contract version is
**1**, and `codeOk = 0`.

The [method reference](interface-methods.md) explains each argument and result.
Schemas live under `rpp_interfaces/plugin_types`, grouped into `common`,
`state`, `reference`, `mission`, `control`, `model`, `estimation`, and
`hardware`.

## C++ and Python helpers

The CMake target `rpp_interfaces::rpp_interfaces` exports field layouts,
field routes, `SignalRouter`, `ReferenceHorizon`, and `ControlLawLayout`.
The Python package provides `FieldLayout`, `field_route`, and parameter helpers.

For example, a state provider's `parameters.py` can declare the planar layout:

```python
from rpp_interfaces.parameter_helpers import get_navigation_state

class ComponentParameters:
    state = get_navigation_state(resource="base", dimensions=2)
```

Register shared schemas before compiling their consumers. After changing shared
headers, rebuild consumers and refresh the affected registered plugins.
