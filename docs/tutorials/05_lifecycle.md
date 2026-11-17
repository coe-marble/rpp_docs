# Tutorial 5 Lifecycle management and handover

## Prerequisites

Follow the [shared prerequisites](https://github.com/coe-marble/rpp_docs/blob/develop/docs/tutorials/README.md#prerequisites-and-execution) and complete
[Tutorial 02: CLI registration](https://github.com/coe-marble/rpp_docs/blob/develop/docs/tutorials/02_registration.md).
Keep using the same tutorial home:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
```

Run from `rpp_dev/src/rpp_demos`. The example [library][glossary-library] must already be linked
and its types and [plugins][glossary-plugin] registered through the CLI. This example uses public
RPP APIs directly in a standalone Python script.

## Description

Manage two native [component][glossary-component] [runtimes][glossary-runtime] and pass typed application state between
them. The runtime owns [lifecycle][glossary-lifecycle] transitions; `AccumulatingProcessor` owns its
running total and checks whether calls are allowed. Its contract declares
`AccumulatorState` as the handover value.

```text
UNCONFIGURED -> configure -> INACTIVE -> activate -> ACTIVE
ACTIVE -> deactivate -> INACTIVE -> cleanup -> UNCONFIGURED
```

Deactivation returns `DeactivationResult`: check `result` before passing `state`
to another runtime's `activate(state)`. That snapshot outlives the source's
configuration. A runtime state such as `ACTIVE` and an application handover
value such as total `7` serve different purposes.

## Implementation

### Run the example

Read the standalone [run.py](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/05_lifecycle/run.py), then execute:

```bash
python3 tutorials/05_lifecycle/run.py
```

The script uses `Workspace`, `ComponentRequest`, and
`ComponentRuntimeBuilder` directly to create `source` and `target`. It first
shows that activation before configuration fails and that the inactive [plugin][glossary-plugin]
rejects calls. After configuration and activation, the source accumulates `3`
and `4`.

The handover uses the public [runtime][glossary-runtime] methods explicitly:

```python
handover = source.deactivate()
handover.result.require_success("deactivate source")
source.cleanup().require_success("cleanup source")
target.activate(handover.state).require_success("activate target with state")
```

Look for:

```text
Activate before configure: success=False
Call while inactive: accumulator is inactive
Source total = 3
Source total = 7
Handover total = 7
Target total = 12
Reactivated total = 13
Rejected input: value must be finite
Total after rejected input = 13
Call after shutdown: accumulator is inactive
```

The target continues the transferred total by processing `5`. It then
explicitly deactivates and reactivates with its own exported state, and processes
`1`. A rejected non-finite input leaves the total unchanged. Standard Python
`ExitStack` closes both runtimes on exit, including if an operation raises.
A retained plugin reference rejects calls after shutdown.

This example uses native Python [components][glossary-component]. Remote adapter activation and
handover are not supported. Cleanup resets the instance's total; saved component
files do not persist the exported handover payload.

### Inspect the result

```bash
workspace="$RPP_HOME/tutorials/05_lifecycle/workspace"

# Find both components and see which implementation each uses.
rpp ws component list "$workspace"
rpp ws component info "$workspace" source
rpp ws component context "$workspace" target

# Inspect the stateful contract and its generated handover description.
rpp registry info example_library::ScalarAccumulator
rpp library example_library info AccumulatingProcessor
```

The CLI shows saved identities and metadata. Use the script's output to observe
[runtime][glossary-runtime] transitions and the application state transferred between instances.

[glossary-plugin]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
[glossary-library]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#library "Library: a source directory grouping Plugin Types, Plugins, and related files."
[glossary-runtime]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#runtime "Runtime: an application-owned execution handle built from saved configuration."
[glossary-lifecycle]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#lifecycle "Lifecycle: managed states and transitions for component configuration, activation, and shutdown."
