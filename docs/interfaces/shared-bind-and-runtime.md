# Shared descriptors and numeric runtime

Plugins exchange flat numeric arrays. Their descriptions tell the application
what each part of an array means, so it can connect fields and allocate the
right buffers before execution. This page explains that preparation and the
packing used by samples, matrices, and reference horizons.

## Binding route

Each plugin's `getDesc()` declares fixed layouts after configuration.
The coordinator builds `FieldLayout` objects, checks routes, prepares indices
and buffers, then admits updates. Names and descriptors do not accompany every
numeric sample. Most interfaces have no schema-level `bind()`; the reference
generator's `bind()` specifically prepares its sampling horizon.

Reconfiguration or component replacement pauses affected execution and rebuilds
routes. Compatible reordering can use a prepared field map; field meaning cannot
be changed by relabeling a numeric vector.

## State fields and dimensions

`FieldListDesc.fields` is an ordered list of `FieldDesc` records.
Each field declares `name`, `kind`, `quantity`, `size`, `frameId`,
`childFrameId`, and `resource`. Offsets and total dimensions are derived by
`FieldLayout`; they are not authored in the schema.

| Coordinate kind | Authored size | Stored width | Tangent width |
| --- | --- | --- | --- |
| `coordinateEuclidean` | N > 0 | N | N |
| `coordinateContinuousAngle` | 0, or N > 0 | 1 if zero, otherwise N | Same as stored width |
| `coordinateQuaternion` | 0 or 4 | 4, in x/y/z/w order | 3 |

Continuous angles require `quantityAngularPosition`; quaternions require
`quantityOrientation`. Quantity fixes the SI unit: there is no separate
`unit` field. Position and orientation are separate fields rather than special
planar/spatial-pose coordinate kinds.

For example, a spatial state can contain:

| Field | Kind / quantity | Stored range | Tangent range |
| --- | --- | --- | --- |
| `base.position` | Euclidean size 3 / linear position | [0, 3) | [0, 3) |
| `base.orientation` | Quaternion / orientation | [3, 7) | [3, 6) |
| `base.velocity` | Euclidean size 3 / linear velocity | [7, 10) | [6, 9) |

Its stored width is 10 and tangent width is 9. A quaternion stores four
coefficients, while a small orientation change needs three rotation components.
That is why the stored state and its local-error vector have different widths.
A covariance in these tangent coordinates has 9 × 9 = 81 entries.

Names must be unique and nonempty within a layout. Invalid kinds, quantities,
sizes, and excessive width fail preparation. Numeric validation checks selected
values for finiteness and quaternion normalization. Quaternion update masks
select all four coefficients together.

## Frames

`frameId` identifies the coordinate basis. `childFrameId` identifies the body
or frame being described. `resource` identifies the physical or logical resource
used by routing and ownership.

A base position/orientation in odom uses `frameId=odom` and
`childFrameId=base_link`. Body velocity uses `frameId=base_link` and
`childFrameId=base_link`. The model/source convention still defines the
motion's reference; a frame name alone does not determine it.

Routes preserve coordinate kind, quantity, frame, and resource meaning.
They do not perform TF lookup, unit conversion, or a kinematic transformation.
Such conversions belong to explicitly configured ingress or model adapters.

Euclidean increments add, angles wrap, and quaternion coordinate operations
use rotation increments in the declared frame. Consumers must agree on those
operations and tangent coordinates before sharing covariance or Jacobians.

## Flat buffer conventions

Let n/nt denote stored/tangent state width, R reference width, H horizon length,
nu control/input width, and na actuator width.

| Buffer | Packing |
| --- | --- |
| State | n doubles in flattened field order. |
| State increment | nt doubles in tangent field order. |
| Covariance / matrix | Row-major rows × columns; state covariance uses nt × nt. |
| Measurement | One flat vector in its configured measurement layout. |
| Current reference, H = 0 | R doubles. |
| Reference horizon, H > 0 | R × H doubles, reference-major index `r * H + h`. |
| Control / realized control | nu doubles in the declared control order. |
| Actuators | na doubles in actuator field order. |

A controller has flat `state`, `reference`, and `control` arrays.
Separate generator/controller instances have their own buffers; a numeric
control call does not receive a list of reference-port lists.
Estimator descriptions contain a list of measurement layouts, but each
`correct()` call selects one measurement index and one flat sample.

Goal paths and trajectories use waypoint-major rows on submission.
Their storage order differs from a sampled reference horizon.

Timestamps, durations, and relative offsets are unsigned 64-bit nanoseconds.
They share the configured application clock. Check ordering and overflow before
time arithmetic. Physical watchdogs and thread scheduling use a monotonic clock.

## Reference horizons

`horizonLength = 0` means one current sample with empty offsets. For positive H,
`horizonOffsetsNs` contains H shared offsets or R × H per-scalar offsets in
reference-major order. Every horizon starts at zero and strictly increases.
Quaternion coefficients have identical offsets.

For example, take a reference with two scalars, x and yaw, and request samples
now, in 0.5 seconds, and in 1 second:

```text
horizonLength    = 3
horizonOffsetsNs = [0, 500000000, 1000000000]
reference        = [1.0, 1.5, 2.0,  0.0, 0.1, 0.2]
                    x at each time   yaw at each time
```

The first three values are the x horizon; the next three are the yaw horizon.
With `horizonLength = 0`, the same current reference is simply `[1.0, 0.0]`.
If the two scalars need different sample times, supply six offsets instead of
three, in that same reference-major order.

`ReferenceHorizon` validates this representation. `ControlLawLayout` combines
it with the controller's flat layouts. The control script prepares generator
sampling times and controller gather indices outside the tick.

`inputValid` follows flattened reference-value order. `enabledAxes` follows
control order. Goal update masks are different: they select which target values
and deadlines a submission replaces.

## Routes and limits

C++ `field_route` and Python `field_route(source, destination)` prepare source
indices in destination order. Extra source fields and different ordering are
allowed when the required fields are compatible.
`validate_required_fields` checks compatibility without building a route.

Suppose a producer stores `[vx, vy, wz, x, y, yaw]`, while a pose controller
requires `[x, y, yaw]`. Matching the described fields produces indices
`[3, 4, 5]`. Each tick gathers those positions into the controller's prepared
input buffer. Field-name lookup happens during preparation, not for every tick.

`SignalRouter` registers numeric signals and source layouts, connects field
subsets, and prepares buffers. Conflicting writers and missing/incompatible
fields fail preparation. Its numeric reads/writes use prepared indices and
buffers without resizing. A read view is reused on the next read of that route.

`LimitDesc` selects fields from a parent layout. Each lower/upper/maxRate list
is empty (unbounded) or matches that selected width. Multiple limits intersect;
contradictions fail configuration. Infinite bounds/rates disable an individual
restriction; NaN, negative rates, or lower greater than upper are invalid.

## Parameter helpers

Use `rpp_interfaces.parameter_helpers` from workspace `parameters.py` files
instead of copying common navigation field dictionaries. For a buffered planar
state provider:

```python
from rpp_interfaces.parameter_helpers import get_navigation_state

class ComponentParameters:
    state = get_navigation_state(resource="base", dimensions=2)
```

Reference generators can use `get_navigation_reference`, `get_velocity_reference`,
or `get_wrench_reference`. These layout helpers require an explicit `resource`.
Only reference helpers accept `inner_controller` to add cascade selection fields;
measured-state layouts do not depend on a controller name.
`get_pid_parameters` supplies PID settings. Each call returns a fresh dictionary.

## Native execution and ownership

Native RPP lists can borrow prepared storage. Retained output views must pin
their backing storage for as long as they are in use. Buffer pools, workspaces,
queues, and replay checkpoints are prepared before execution; pool exhaustion
returns failure or defers work rather than allocating a replacement.

The `$realtime` annotation marks the schema's numeric methods. In control and
localization, the numeric worker reuses prepared buffers; the ROS executor
handles message conversion and publication. Keep construction, resizing, and
configuration work outside those numeric calls.

Resolve components through RPP contexts and use guarded calls where lifecycle
can overlap execution. Direct instance access supplies no lifecycle guard.
All callers must respect view lifetimes and serialize calls according to their
configured threading policy.

The [method reference](interface-methods.md) uses these dimensions and packing
rules when describing each call's arguments and results.
