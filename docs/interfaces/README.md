# Shared robotics interfaces

`rpp_interfaces` owns the Cap'n Proto contracts shared by control, estimation,
models, mission supervision, state buffers, and hardware. It also supplies
C++ and Python field-layout helpers. Algorithm implementations belong to their
libraries; the current generic EKF/UKF implementations live in
`rpp_localization`.

Start with [component responsibilities](component-boundaries.md), then read
[layouts and numeric execution](shared-bind-and-runtime.md). Use the
[method reference](interface-methods.md) for arguments and result semantics.
The [implementation status](../status.md) separates available source from future work.

## Guides

| Guide | Owns |
| --- | --- |
| [Component boundaries](component-boundaries.md) | Responsibilities and data flow between plugin families. |
| [Shared descriptors and numeric runtime](shared-bind-and-runtime.md) | Field dimensions, frames, routing, buffer packing, horizons, and ownership. |
| [Interface method reference](interface-methods.md) | Calling rules and results for every shared interface method. |
| [Control execution](control/control-stack-and-message-map.md) | Script routing, cascade composition, goal ownership, supervision, and ROS integration. |
| [Control dependencies and extensions](control/ros-independent-control-framework.md) | Core dependencies and the boundary for optional modeling/optimization extensions. |
| [Generic estimation and localization](estimation/generic-estimation-and-localization.md) | Current estimator implementation, navigation composition, replay, and verification limits. |

## Schema inventory

All paths below are relative to the
[`rpp_interfaces` library](https://github.com/coe-marble/rpp_interfaces/tree/develop).

| Directory | Contracts |
| --- | --- |
| [`plugin_types/common`](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/common) | `FieldDesc`, `FieldListDesc`, `LimitDesc`, status/quantity/coordinate constants, realtime annotation. |
| [`plugin_types/state`](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/state) | `StateProvider`: coherent buffered state reads and writes. |
| [`plugin_types/reference`](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/reference) | `ReferenceGenerator`: point, path, and timed-trajectory sampling. |
| [`plugin_types/mission`](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/mission) | `MissionMonitor`: continuation decisions and selected goal completion. |
| [`plugin_types/control`](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/control) | `ControlLaw`, `ActuationMapper`, and `ControlConstraint`. |
| [`plugin_types/model`](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/model) | `Model`: prediction, observation, coordinate operations, and derivatives. |
| [`plugin_types/estimation`](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/estimation) | `Estimator`: owned state, covariance, prediction, and correction. |
| [`plugin_types/hardware`](https://github.com/coe-marble/rpp_interfaces/tree/develop/plugin_types/hardware) | `Hardware` endpoint descriptions and numeric `HardwareIO`. |

The library's `plugins.json` declares schemas and contains no concrete algorithm
plugins. For example, `rpp_interfaces::StateProvider` is the contract;
`rpp_control::BufferedStateProvider` is one implementation.

## Using the interfaces

Logical schema imports start at `rpp_interfaces`:

```capnp
using D = import "rpp_interfaces/common/descriptions.capnp";
```

Generated C++ plugin interfaces use that namespace, for example
`rpp_interfaces::ControlLaw`. The header-only CMake target
`rpp_interfaces::rpp_interfaces` exports field layouts, field routes,
`SignalRouter`, `ReferenceHorizon`, and `ControlLawLayout`.
The Python package provides `FieldLayout`, `field_route`, and parameter helpers.

Register the schemas before compiling consumers. Use `RPP_INTERFACES_CPP_DIR`
when generated headers are outside the normal registry interface directory.
See [registration and generated-code compatibility](../registry.md).

## Compatibility

The shared contract version remains **1**, and `codeOk = 0`. Schema IDs,
method ordinals, generated wrappers, and native binaries must agree.
A contract version does not establish native C++ ABI compatibility: rebuild
consumers and refresh affected registered plugins when shared headers change.

The flat layouts and helpers are implemented. They do not establish an
allocation or timing guarantee for every plugin, transport, or application.
See [numeric execution requirements](shared-bind-and-runtime.md#native-execution-and-ownership).
