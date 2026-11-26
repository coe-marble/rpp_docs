# Testing support and coverage

`rpp_testing` supplies shared source fixtures and packaged test data. Tests
remain in their implementation repositories; this page identifies the shared
support and the scope of important runtime scenarios. Test presence is not a
claim that a particular checkout passed.

See the [test image](test-image.md) for the environment and
[integration CI](integration.md) for coordinated revision checks.

## Precompiled fixture

[`scripts/build_rpp_autogen.sh`](https://github.com/coe-marble/rpp_testing/blob/develop/scripts/build_rpp_autogen.sh)
creates `rpp_testing/rpp_autogen/.rpp`, including generated interfaces and
precompiled fixture plugins. The fixture publishing workflow runs it manually.
`rpp_cpp` consumes that directory directly; its tests do not generate or
download missing test artifacts.

The script clones `rpp_dev`, builds with tests disabled, and runs the existing
fixture setup. `RPP_DEV_REF` selects the source revision; `RPP_AUTOGEN_DIR`
selects output. `--local` reuses an already-built ROS workspace and skips
the clone/build.

## Fixture layout

| Fixture group | Purpose |
| --- | --- |
| `example_plugins` | Small implementations installed by CLI test-fixture setup. |
| `complex_plugins` | Optional larger examples, not installed automatically. |
| `mock_workspaces` | Saved component/script configurations for runtime tests. |
| `test_component_cpp` / `test_component_py` | C++/Python component fixtures. |
| `test_libs` | Library registration fixtures. |

Sources live in [rpp_testing](https://github.com/coe-marble/rpp_testing/tree/develop).

## Native runtime scenarios

Start a behavior review with
[the component runtime scenarios](https://github.com/coe-marble/rpp_cpp/blob/develop/tests/test_component_runtime_scenarios.cpp).
The same scenarios run for `SingleThreaded` and `Concurrent`: activation,
deactivation/reactivation, switching with and without state handover, source and
target failure recovery, static slots, multiple-active slots, and shutdown order.
Concurrent-only scenarios cover closing admission while draining guarded calls
and retrying after a drain timeout. Lifecycle operations stay on one owner thread.
These are in-process integration tests of runtime, managers, and lifecycle plugins;
their small construction bridge uses production slot creation and registration.
They do not cover description loading, shared-library loading, or external hosts.

Shared test support lives in
[`fake_plugins.hpp`](https://github.com/coe-marble/rpp_cpp/blob/develop/tests/support/fake_plugins.hpp) (plugin behavior, failure
controls, and event recording) and
[`runtime_test_helpers.hpp`](https://github.com/coe-marble/rpp_cpp/blob/develop/tests/support/runtime_test_helpers.hpp) (the single
private-construction bridge and reusable fixtures). `simple_controllers()` keeps
the two-controller case; `nested_controllers()` builds two switchable branches:

```text
script.controllers (exclusive)
├── a
│   ├── a.left
│   │   └── a.left.leaf
│   └── a.right
└── b
    ├── b.left
    │   └── b.left.leaf
    └── b.right
```

Composite plugins explicitly activate/deactivate their subcomponents. Nested scenarios
check callback order, branch switching, independent descendant state, rollback
after partial activation, and cleanup after failure under both threading policies.
`FakeComponentTree` can describe additional shapes without adding local fake classes.

The RPC control layer is separate: `RpcControlService` and `RpcControlClient` in
`rpc_control_service.hpp` expose remote configuration/cleanup and adapter discovery.
[Its tests](https://github.com/coe-marble/rpp_cpp/blob/develop/tests/test_rpc_control_service.cpp) use the `RpcControlService` suite.
The shared generated `plugin_runtime.capnp` protocol still uses the wire interface
name `PluginRuntime`, which is also consumed by Python.

## Robotics interfaces and algorithm validation

`rpp_interfaces` declares C++ layout/router tests and Python field/helper tests
in its [CMake file](https://github.com/coe-marble/rpp_interfaces/blob/develop/CMakeLists.txt);
its CI runs both languages.

Control and localization retain algorithm/integration tests beside their
implementations. Localization's
[bag parity runbook](https://github.com/coe-marble/rpp_localization/blob/develop/test/robot_localization_parity/README.md)
describes saved accuracy, CPU, allocation, and replay evidence. Distinguish those
algorithm measurements from runtime/transport benchmarks.
