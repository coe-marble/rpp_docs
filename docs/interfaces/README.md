# RPP interfaces

Shared Capn Proto contracts for RPP libraries. Implementations live in libraries
such as rpp_control, rpp_estimation, rpp_localization and MORE. RPP supplies
component resolution, parameters, lifecycle and guarded native calls.

The interfaces define numeric data and method signatures. They require no ROS
or CasADi runtime. CasADi-backed implementations can provide derivatives and
linearizations through the same numeric contracts as native implementations.

All timestamps, durations and relative offsets use unsigned 64-bit nanoseconds
(`UInt64` in Cap'n Proto and `std::uint64_t` in C++). Python integers use the same
range. Timestamps share the configured application clock; physical watchdogs
use a monotonic clock. ROS adapters check signed native time before conversion.

## Current contents

| Location | Purpose |
| --- | --- |
| [plugin_types/common](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/common) | Shared state/channel descriptors, constants and execution policy for all domains. |
| [plugin_types/reference](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/reference) | Desired-reference generators, monitor and progress constants. |
| [plugin_types/control](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/control) | Controller policy, actuation mapping and feasibility constraints. |
| [plugin_types/model](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/model) | Reference-independent prediction, observation, derivatives and coordinate operations. |
| [plugin_types/estimation](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/estimation) | Generic estimator owning state, covariance and correction/prediction history. |
| [plugin_types/hardware](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/hardware) | Shared Hardware device descriptions and numeric HardwareIO endpoint. |
| [Five component boundaries](component-boundaries.md) | Responsibilities, exact constant consumers and numeric data flow. |
| [Interface method reference](interface-methods.md) | Every method: when to call it, each argument, result sizes and failure behavior. |
| [Shared route and schematic](shared-bind-and-runtime.md) | Binding-only descriptors and flat double-buffer execution across the planned stack. |
| [Control proposal](control/ros-independent-control-framework.md) | Package boundaries, shared modeling and implementation sequence. |
| [Control contract](control/control-stack-and-message-map.md) | Data layouts, lifecycle, buffer ownership and method semantics. |
| [Estimation proposal](estimation/generic-estimation-and-localization.md) | Generic estimation algorithms and a localization composition preserving the existing 15-state behavior. |
| [plugins.json](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugins.json) | RPP library declaration for all shared schema families; no algorithm plugins. |

## Interface ownership

New shared contracts belong in `rpp_interfaces`, grouped by domain under
`plugin_types`.
Control implementations belong in rpp_control; generic filter implementations
belong in rpp_estimation; navigation-state models and localization compositions
belong in rpp_localization. Graph payload schemas belong in `rpp_interfaces` too
when the existing MORE payloads are consolidated. Graph serialization/evaluation helpers
remain in the implementation libraries that use CasADi.

StateDesc, StateFieldDesc and ChannelDesc are shared binding descriptions. Active
numeric state, command, measurement, reference and matrix payloads use flat
List(Float64), with sizes/order fixed during binding. RPP native bindings must
map them to borrowed inputs and caller-owned outputs. Descriptors never accompany
active samples. Description getters are part of the binding phase.

State fields are ordered declarations: vector size is explicit, while angle and
quaternion widths follow their coordinate kind. The shared layout builder
calculates offsets, tangent dimensions and totals during binding. Frame names
use frameId/childFrameId semantics; no separate expressedIn selector is required.
ReferenceGenerator.featuresDesc() advertises point, path and trajectory setters.

Reuse existing common geometry and static matrix types in cold configuration and
target submission. The schemas import canonical annotations and those messages
from rpp_common. Existing registered common, localization and MORE schemas need
a separate compatibility migration
before their definitions can be relocated. Keep one canonical definition of each
type rather than copying it into `rpp_interfaces`.

## Live layout inspector

Use Vizanti's **Layout Inspector** widget to inspect multiple
`marble_control_msgs/msg/ControlLayout` topics and their latest state/command values.
The widget uses Vizanti's existing adapter connection; it needs no separate Python
node or HTTP server. See Vizanti's plugin documentation for configuration and the
limits of the published routing information.

## Imports and native usage

The logical import root `rpp_interfaces` maps to this library's `plugin_types`
directory. Shared descriptions are imported using paths such as:

```capnp
using D = import "rpp_interfaces/common/descriptions.capnp";
```

With library name `rpp_interfaces`, generated native interfaces belong to that
C++ namespace. Implementations use `rpp_interfaces::ControlLaw`, for example;
their implementation classes can remain in rpp_control or an extension library.

The header-only CMake target `rpp_interfaces::rpp_interfaces` exports
`<rpp_interfaces/field_layout.hpp>`, `<rpp_interfaces/field_routing.hpp>`,
`<rpp_interfaces/signal_router.hpp>`, `<rpp_interfaces/reference_horizon.hpp>`,
and `<rpp_interfaces/control_law_layout.hpp>`.

`ControlLawDesc` declares flat `state`, `reference`, and `control` field lists.
Component instances define their own layouts, and the manager prepares field routes
between producers and consumers. Activation claims the control destinations;
expired reference values preserve those claims until deactivation.

`horizonLength = 0` means one current value per reference scalar and empty offsets.
For a positive horizon length `H` and reference width `R`, `horizonOffsetsNs`
contains either `H` shared offsets or `R * H` individual offsets. Values and
individual offsets use reference-major indexing `r * H + h`. Each horizon starts
at zero and strictly increases. Quaternion scalars have identical offsets.
`ReferenceHorizon` validates these rules and prepares bounded numeric offsets.
`ControlLawLayout` prepares the flat layouts and reference buffer size.
`inputValid` follows reference value order; `enabledAxes` follows control order.

`ReferenceGeneratorDesc.reference` and `MissionMonitorDesc.reference` describe
their reference fields directly. The generator's `bind(offsets, horizonLength)`
prepares sampling outside numeric execution. Its `sample()` returns flat values
in the same reference-major order used by controllers.

The headers use RPP-generated schemas. Register the schemas before compiling
a consumer and set `RPP_INTERFACES_CPP_DIR` if the generated headers are outside
`$RPP_HOME/interfaces/cpp` or the default `~/.rpp/interfaces/cpp`.

The installed Python package provides `FieldLayout(desc.fields)` and
`field_route(source, destination)`. It accepts generated field descriptors and
copies their attributes into an immutable layout. Routes contain flattened
source indices in destination order in both languages.

`validate_required_fields(available, required)` checks field compatibility and
returns a boolean without creating a route or raising on a mismatch. Extra
available fields and different field order are allowed.

`SignalRouter` connects described numeric signals independently of control,
localization, ROS, and plugin lifecycle. A caller registers each signal and its
sources, then connects input/output field subsets and calls `prepare_buffers()`.
Conflicting writers, missing fields, incompatible descriptions, and unavailable
rows are rejected while preparing connections. Row labels are opaque values;
the caller supplies their meaning and selects which sources participate.

During execution, `read()` copies a signal's selected values into a prepared
input buffer, and `write()` copies a complete valid result into the signal.
Invalid results return false without partially updating the signal. No field-name
lookup, buffer resizing, or allocation occurs in these operations. Input views
share their route buffer, which is reused on the next read of that route.
Reconfiguration happens outside execution; `reset()` keeps signal IDs and
discards routes so the caller can build a new set of connections.

RPP contexts resolve components. `get_subcomponent_context()` provides configured
access; active handles guard execution. Schema methods do not return component
instances or replace the runtime's registry.

## Status and compatibility

The initial control drafts were moved into `rpp_interfaces` preserving their
identities. The current shared-descriptor/flat-buffer revision changes those unregistered draft
APIs and requires regeneration before use. The old ControlState wrapper and
control-prefixed generic field/channel definitions have been removed.
The original registered controllers.capnp and localization contracts remain in
their implementation repositories until an explicit downstream migration.

These are experimental schemas, including the new Model and Estimator contracts.
Registration/code generation, native buffer bindings, algorithm implementations
and the generic estimation package remain integration work. The boundary revision
removes the task-kind/layout layer and moves numerical observation out of the
controller's tracking policy; existing generated consumers need regeneration.
The current descriptor revision also removes authored offsets, total dimensions
and frame-index tables. These experimental changes are not wire-compatible with
the earlier draft; the shared layout builder/native bindings remain to implement.
