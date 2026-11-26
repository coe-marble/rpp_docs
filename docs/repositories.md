# Repository catalog

`rpp_dev` pins the source submodules under `src` and the documentation
submodule `rpp_docs`. The implementation inventory is declared in
[`repositories.yml`](repositories.yml); documentation lives here.

| Repository | Responsibility | Documentation |
| --- | --- | --- |
| `rpp_cli` | Registry, library, workspace and [component][glossary-component] commands | [CLI](cli.md) |
| `rpp_common` | Shared schemas, data models, parameter declarations | [Contracts](plugins-and-plugin-types.md) |
| `rpp_interfaces` | Shared robotics contracts, field layouts, routes, and horizons | [Interfaces](interfaces/README.md) |
| `rpp_orchestrator` | Saved components, script configurations and workspace GUI | [Workspaces](workspaces.md) |
| `rpp_plugin_registrator` | Metadata, validation, registration and code generation | [Registry](registry.md) |
| `rpp_py` | Python managed runtime, loading and component server | [Runtime lifecycle](runtime-lifecycle.md) |
| `rpp_cpp` | C++ managed runtime, loading and component server | [C++ runtime](cpp-runtime.md) |
| `rpp_testing` | Shared fixtures and test libraries | [Testing support](testing.md) |
| `rpp_demos` | Runnable tutorials, demos and benchmarks | [Tutorials](tutorials/README.md), [benchmarks](benchmarks/README.md) |
| `rpp_ros2` | Slot command services and status topics | [ROS 2 integration](ros2-integration.md) |
| `rpp_navigation` | Navigation scaffold; no implementations yet | [Implementation status](status.md) |

Each source repository keeps a short README describing its purpose and linking
to the central guides. Runnable examples, schemas, fixtures, and source-level
API comments stay beside their implementation. Shared user/developer guides,
walkthroughs, setup instructions, and design history are maintained in `rpp_docs`.

Application libraries such as `rpp_control`, `rpp_localization`, and MORE can be
sibling checkouts in a ROS workspace; they are not all rpp_dev submodules.
See [library/workspace placement](workflows.md#libraries-in-a-ros-2-workspace).

The [integration guide](integration.md) explains pinned revisions and CI.

[glossary-component]: glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
