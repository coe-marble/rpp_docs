
# Robotics Plugin Platform (RPP) Documentation

> Unofficially, RPP stands for **Robotics Plus Plus**. Following the proud
> industry tradition of adding a plus sign and calling it the next generation.

RPP is a language-independent framework for defining, registering, composing,
and executing robotics plugins. It separates plugin contracts from concrete
implementations, so the same system can support multiple languages, custom
plugin types, and reusable components.

## Motivation

RPP is inspired by nav2 and similar plugin architectures, but addresses two
limitations that become important as a system grows. First, adding a new
plugin type should be straightforward: developers can define a new type and
make it available to the rest of the system without changing a fixed central
list of built-in types. Second, a plugin system should not force every plugin
to use the same implementation language. RPP solves this by defining plugin types in a language-neutral schema, generating language-specific interfaces, and providing adapters for supported runtimes. In this way, a plugin type can be implemented in one language and used in another without requiring the plugin author to write language-specific code for each runtime.

## Supported languages

RPP currently supports:

- **Python**, through the `rpp_py` runtime.
- **C++**, through the `rpp_cpp` runtime.

## Start here

Use the [development image](docs/development-image.md), the recommended tutorial
environment, then follow the [six runnable tutorials](docs/tutorials/README.md).
For host installation, use [Installation and first run](docs/getting-started.md).

Existing installations should follow [registry migration](docs/registry.md#upgrade-an-existing-registry)
after updating packages and matching native artifacts.

## How RPP fits together

RPP is organized around three stages:

1. **Define** a language-neutral plugin type and its interface.
2. **Register** concrete implementations and their metadata in the RPP home
    directory, normally `~/.rpp`.
3. **Compose and execute** saved components through managed runtime handles and
    slots, with explicit configuration, activation, and shutdown. Workspaces are
    identified by their `.rppws` directory.

The registry owns metadata and generated interfaces. Libraries own plugin
source. Workspaces own composition, configuration, and component state. This
separation allows one implementation to be reused across multiple workspaces.

## Documentation map

| Topic | Guide |
| --- | --- |
| Setup | [Installation](docs/getting-started.md), [development image](docs/development-image.md) |
| Learning path | [Tutorials](docs/tutorials/README.md), [integrated demo plan](docs/demos.md) |
| Concepts | [Architecture](docs/architecture.md), [plugin contracts](docs/plugins-and-plugin-types.md) |
| Composition | [Core workflows](docs/workflows.md), [components, workspace layout, and parameters](docs/workspaces.md) |
| Execution | [Managed runtimes and lifecycle](docs/runtime-lifecycle.md), [component connections](docs/component_connection.md) |
| C++ details | [Runtime guide](docs/cpp-runtime.md), [construction and ownership](docs/cpp-context-flow.md) |
| ROS 2 | [Slot services and status topics](docs/ros2-integration.md) |
| Registry and commands | [Registration and upgrades](docs/registry.md), [CLI reference](docs/cli.md) |
| Measurements | [Benchmarks](docs/benchmarks/README.md), [communication benchmark](docs/benchmarks/communication.md) |
| Development | [Repository catalog](docs/repositories.md), [integration and CI](docs/integration.md), [testing support](docs/testing.md), [test image](docs/test-image.md) |
| Documentation | [Contributing](docs/contributing.md), [historical lifecycle design](docs/plans/managed-plugin-lifecycle/feature-description.md) |

## Documentation ownership

All RPP user and developer guides live in `rpp_docs`. Individual repositories
keep brief README descriptions and links here; executable examples, schemas,
fixtures, and source API comments stay beside their implementation. The
integration repository `rpp_dev` pins the coordinated source and docs revisions.

The nine implementation submodules are declared in
[`docs/repositories.yml`](docs/repositories.yml). The dependency-free inventory
checker is documented in [Contributing](docs/contributing.md); it checks catalog
paths without modifying implementation repositories.
