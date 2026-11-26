# Robotics Plugin Platform (RPP)

> Unofficially, RPP stands for **Robotics Plus Plus**. Following the proud
> industry tradition of adding a plus sign and calling it the next generation.

RPP defines language-neutral plugin contracts and composes their Python/C++
implementations into managed runtimes. A plugin type is a contract, a plugin
implements it, and a component saves a plugin's parameters and child assignments.
Start with the [glossary](docs/glossary.md) for these distinctions.

## Start here

1. Choose the [development image](docs/development-image.md) or
   [host installation](docs/getting-started.md).
2. Follow the [six tutorials](docs/tutorials/README.md): contracts, registration,
   configuration, loading, scripts, and lifecycle.
3. Read [architecture](docs/architecture.md) and [core workflows](docs/workflows.md)
   when composing your own application.

For an existing installation, use
[registration and upgrades](docs/registry.md#upgrade-an-existing-registry).
The [implementation status](docs/status.md) distinguishes current source,
unsupported paths, and future extensions.

## Working with RPP

| Task | Guide |
| --- | --- |
| Define or implement a plugin contract | [Plugins and plugin types](docs/plugins-and-plugin-types.md) |
| Register, rebuild, or migrate libraries | [Registry](docs/registry.md) |
| Save components, parameters, and script configurations | [Workspaces](docs/workspaces.md) |
| Configure, activate, switch, or close components | [Runtime lifecycle](docs/runtime-lifecycle.md) |
| Use native or adapted calls | [Component connections](docs/component_connection.md) |
| Use C++ runtime APIs and threading policies | [C++ runtime](docs/cpp-runtime.md) |
| Expose slot operations through ROS 2 | [ROS 2 integration](docs/ros2-integration.md) |
| Find a command or flag | [CLI reference](docs/cli.md) |

## Robotics interfaces and execution

| Topic | Guide |
| --- | --- |
| Contracts and available schema families | [Shared interfaces](docs/interfaces/README.md) |
| Component responsibilities | [Component boundaries](docs/interfaces/component-boundaries.md) |
| Field routing, dimensions, frames, and flat buffers | [Shared layouts](docs/interfaces/shared-bind-and-runtime.md) |
| Method arguments and results | [Method reference](docs/interfaces/interface-methods.md) |
| Control routing, cascades, goals, and mission supervision | [Control execution](docs/interfaces/control/control-stack-and-message-map.md) |
| Generic filters, navigation, and replay | [Estimation and localization](docs/interfaces/estimation/generic-estimation-and-localization.md) |

## Developing and measuring

- [Repository catalog](docs/repositories.md) and [integration CI](docs/integration.md).
- [C++ construction and ownership internals](docs/cpp-context-flow.md).
- [Testing support](docs/testing.md) and [test image](docs/test-image.md).
- [Benchmarks](docs/benchmarks/README.md) and [integrated demo status](docs/demos.md).
- [Contributing documentation](docs/contributing.md).
- [Historical lifecycle plans](docs/plans/README.md).

## Documentation ownership

This repository owns the shared user/developer guides. Implementation repositories
own schemas, runnable examples, tests, and source API comments; guides link to
those sources. Package runbooks may contain detailed launch/configuration examples.

Each topic has one primary guide. Overviews link to it rather than maintaining
another copy of its API or installation steps. Current guides describe the
integration checkout; plans and measured historical results state their scope.

The source inventory lives in [repositories.yml](docs/repositories.yml).
`rpp_dev` pins the coordinated source and documentation revisions.
