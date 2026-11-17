# Tutorial 4 Loading and invocation

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

Load saved [components][glossary-component], configure and activate their [runtimes][glossary-runtime], and call them
through the generated contract. The script shows the whole construction path:
`LibraryManager` resolves registered [plugins][glossary-plugin], `Workspace` stores component
settings, `DataManager` reads them, and `ComponentRuntimeBuilder` constructs a
runtime from `ComponentRequest(record.folder)`.

Loading alone does not activate the component. Call `configure()` and
`activate()` before invoking its generated `ScalarProcessor` interface. The
application owns the runtime and closes it in a `finally` block.

## Implementation

### Run the example

Read the standalone [run.py](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/04_loading/run.py), then execute:

```bash
python3 tutorials/04_loading/run.py
```

The script creates or reuses `processor` and `identity` in
`$RPP_HOME/tutorials/04_loading/workspace`, and saves their [parameters][glossary-parameter] explicitly.
For each [component][glossary-component] it performs these API calls:

```python
runtime = builder.build_component(ComponentRequest(record.folder))
try:
    runtime.configure().require_success("configure component")
    runtime.activate().require_success("activate component")
    processor: ScalarProcessor = runtime.get_instance()
    print(processor.process(3.0))
finally:
    runtime.close().require_success("close component")
```

Look for:

```text
Loaded processor; active=False
processor = 7
Loaded identity; active=False
identity = 3
```

`processor` saves gain `2` and offset `1`; `identity` uses the [plugin][glossary-plugin] defaults.
The last two examples catch an unknown component name and a missing component
folder with ordinary Python `try`/`except`. The saved [workspace][glossary-workspace] remains available
after the [runtimes][glossary-runtime] close.

### Inspect the result

```bash
workspace="$RPP_HOME/tutorials/04_loading/workspace"

# Find both components and trace processor to its registered plugin.
rpp ws component list "$workspace"
rpp ws component info "$workspace" processor
rpp library example_library info AffineProcessor

# Locate the saved files and inspect the input used by the builder.
rpp ws component context "$workspace" processor
rpp ws component parameter get "$workspace" processor

# Inspect the generated contract used for calls.
rpp registry info example_library::ScalarProcessor
```

These commands inspect persistent descriptions. [Runtime][glossary-runtime] construction and
activation happen explicitly in the Python script.

[glossary-plugin]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
[glossary-library]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#library "Library: a source directory grouping Plugin Types, Plugins, and related files."
[glossary-workspace]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#workspace "Workspace: a project directory containing saved component and script configuration in .rppws."
[glossary-runtime]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#runtime "Runtime: an application-owned execution handle built from saved configuration."
[glossary-parameter]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#parameter "Parameter: a named configuration value resolved for a component instance."
