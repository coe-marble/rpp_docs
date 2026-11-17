# Repository catalog

`rpp_dev` pins nine implementation submodules under `src` and the documentation
submodule `rpp_docs`. The implementation inventory is declared in
[`repositories.yml`](repositories.yml); documentation lives here.

| Repository | Responsibility | Documentation |
| --- | --- | --- |
| `rpp_cli` | Registry, library, workspace and [component][glossary-component] commands | [CLI](cli.md) |
| `rpp_common` | Shared schemas, data models, parameter declarations | [Contracts](plugins-and-plugin-types.md) |
| `rpp_orchestrator` | Saved components, script configurations and workspace GUI | [Workspaces](workspaces.md) |
| `rpp_plugin_registrator` | Metadata, validation, registration and code generation | [Registry](registry.md) |
| `rpp_py` | Python managed runtime, loading and component server | [Runtime lifecycle](runtime-lifecycle.md) |
| `rpp_cpp` | C++ managed runtime, loading and component server | [C++ runtime](cpp-runtime.md) |
| `rpp_testing` | Shared fixtures and test libraries | [Testing support](testing.md) |
| `rpp_demos` | Runnable tutorials, demos and benchmarks | [Tutorials](tutorials/README.md), [benchmarks](benchmarks/README.md) |
| `rpp_ros2` | Slot command services and status topics | [ROS 2 integration](ros2-integration.md) |

Each source repository keeps a short README describing its purpose and linking
to the central guides. Runnable examples, schemas, fixtures, and source-level
API comments stay beside their implementation. User and developer guides,
walkthroughs, setup instructions, and design history are maintained in `rpp_docs`.

The [integration guide](integration.md) explains pinned revisions and CI.

[glossary-component]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
