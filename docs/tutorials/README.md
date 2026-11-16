# RPP demos and tutorials

The runnable sources live in `rpp_dev/src/rpp_demos`; this guide and the
individual walkthroughs are maintained here in `rpp_docs`.

Six runnable tutorials follow one plugin from its contract to lifecycle
management. Integrated demos and benchmarks have separate folders.

```text
rpp_demos/
  tutorials/
    example_library/          # Schema, implementation, and library metadata
    tutorial_support.py       # Isolated setup and cleanup
    01_plugin_type/
    02_plugin_implementation/
    03_registration/
    04_configuration/
    05_loading/
    06_lifecycle/
  demos/                      # Localization and ROS integration planned
  benchmarks/                 # RPP and ROS communication comparisons
```

## Prerequisites and execution

The recommended way to run these tutorials is the
[`rpp_dev` development image](../development-image.md), which includes the tutorial
sources, installed RPP runtime, and native registration tools. Start a tutorial shell from the host:

```bash
docker run --rm -it \
    --env RPP_CPP_CORE_PATH=/workspaces/rpp/ros2_ws/install/rpp_cpp/lib \
    --workdir /workspaces/rpp/ros2_ws/src/rpp_dev/src/rpp_demos \
    ghcr.io/coe-marble/rpp-dev:lyrical
```

Then run the tutorial commands below inside the container. For image setup and
persistent source edits, see the [image guide](../development-image.md).

For a host setup, follow [installation](../getting-started.md). Use Python 3.10 or newer in an installed RPP development environment providing
`rpp_common`, `rpp_plugin_registrator`, `rpp_orchestrator`, and `rpp_py` and their
dependencies. These drivers use the public `LibraryManager`, `Workspace`,
`ComponentRequest`, and `ComponentRuntimeBuilder` APIs. ROS is not required.

Registration generates interfaces and may compile native supporting artifacts
even for Python plugins. The container command explicitly exports
`RPP_CPP_CORE_PATH` so each temporary tutorial home can locate the native runtime
without inheriting the normal home's settings. In a host setup, export this
variable to the directory containing `librpp_cpp` and `librpp_cpp_core` before
running the drivers (for example, `build/rpp_cpp` for a standalone build or
`install/rpp_cpp/lib` for an isolated colcon installation). The examples do not install dependencies
or build the RPP runtime for you.

Run from `rpp_dev/src/rpp_demos` using your RPP environment's Python
(the container command above opens that directory):

```bash
python3 tutorials/01_plugin_type/run.py
python3 tutorials/02_plugin_implementation/run.py
python3 tutorials/03_registration/run.py
python3 tutorials/04_configuration/run.py
python3 tutorials/05_loading/run.py
python3 tutorials/06_lifecycle/run.py
```

Each driver includes its prerequisites from earlier stages and runs
independently. Run each in a fresh Python process because RPP caches
configuration and generated modules. Absolute driver paths also work from
other working directories.

Every driver copies the example library to a temporary directory, sets a
temporary `RPP_HOME` before importing RPP, registers the necessary artifacts,
and creates workspace components as needed. Runtime handles close before the
temporary sources, registry, generated artifacts, and workspace are deleted,
including on exceptions. The normal registry and checked-in sources are not
modified. A forcibly killed process may leave the printed temporary directory
behind; remove it after confirming the process has stopped.

## Learning path

`example_library::ScalarProcessor` declares `process(value)`.
`example_library::AffineProcessor` implements `gain * value + offset`.
Defaults are gain `1` and offset `0`; the component `processor` uses gain `2`
and offset `1`.

| Tutorial | Main lesson | Observable result |
| --- | --- | --- |
| [1. Plugin type](01_plugin_type.md) | Annotated schema and generated contract | Type registered with zero implementations |
| [2. Implementation](02_plugin_implementation.md) | Method, parameters, and lifecycle hooks | Default result `3`, configured result `7` |
| [3. Registration](03_registration.md) | Identities, source refresh, and missing sources | Plugin resolves to its registered type |
| [4. Configuration and composition](04_configuration.md) | Component identity, defaults, and overrides | Independent workspace settings |
| [5. Loading and invocation](05_loading.md) | Runtime construction and typed calls | `processor` returns `7`, `identity` returns `3` |
| [6. Lifecycle](06_lifecycle.md) | Transitions, recovery, and resource ownership | Inactive calls fail; reactivation succeeds |

Each driver includes an intentional failure and checks the expected outcome.
Unexpected errors propagate and produce an unsuccessful exit. Walkthroughs show
application output; initialization logs and detailed diagnostics depend on
the installed RPP version.

Registration publishes an implementation. Workspace configuration selects its
settings for a component instance. Loading constructs runtime objects.
Lifecycle transitions govern configuration, operation, and cleanup.

## Later work

Add a tutorial on executable parameter definitions, shared YAML beside
`params/parameters.py`, and storing evaluated values. The
[workspace guide](../workspaces.md#yaml-and-shared-parameter-data) describes the
pattern; this follow-up tutorial is not implemented yet.

Add a C++ implementation of the same contract and cross-language examples.
The [localization demo plan](../demos.md) covers multiple algorithms and
ROS lifecycle control through `rpp_ros2`. The
[communication benchmarks](../benchmarks/communication.md) compare native
and subprocess RPP/ROS communication with reproducible workloads.
