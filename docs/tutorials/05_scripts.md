# Tutorial 5 Script slots, loading, and execution

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

The copied library must include
[`scripts/scalar_pipeline.py`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/scripts/scalar_pipeline.py).
After updating the checkout, follow Tutorial 02's source-copy and refresh steps
to update the linked library. Tutorial 04 introduces the [runtime][glossary-runtime] construction APIs used here.

## Description

Define named [component][glossary-component] [slots][glossary-slot], assign saved components to them, load their [script][glossary-script]
[runtime][glossary-runtime], and execute a Python script body. `ScalarPipeline` transforms each input
with an affine processor and feeds the result into a stateful accumulator.

Its `COMPONENTS` declaration maps slot names to [plugin][glossary-plugin] contracts:

```python
class ScalarPipeline:
    COMPONENTS = {
        "processor": "example_library::ScalarProcessor",
        "accumulator": "example_library::ScalarAccumulator",
    }
```

A slot declares the required type. The [workspace][glossary-workspace] configuration chooses the
concrete component, including its implementation and saved [parameters][glossary-parameter]. This
example uses single-component slots; the workspace validates that each assigned
component implements the slot's contract.

The script body accepts a context and input values. It obtains active native
instances through `context.get_subcomponent_instance(slot_name)` and calls their
contract methods. `build_script()` constructs a runtime for the assigned
components; execution of the Python body is an explicit application step.

## Implementation

### Define assignments and load the script

Read the standalone [runner](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/05_scripts/run.py), then execute:

```bash
python3 tutorials/05_scripts/run.py
```

The runner makes the registered example [library][glossary-library] a [workspace][glossary-workspace]. It creates or
reuses `pipeline_processor` (`AffineProcessor`, gain `2`, offset `1`) and
`pipeline_accumulator` (`AccumulatingProcessor`). `Workspace.create_script`
reads the existing library [script][glossary-script]'s [slot][glossary-slot] declarations and publishes a script
description under the library's `.rppws/script_descriptions` directory.
The runner recreates the example's assignments on each run:

```python
workspace.assign_component_to_script(script, "processor", processor_record.id)
workspace.assign_component_to_script(script, "accumulator", accumulator_record.id)
```

The `Default` configuration now contains [component][glossary-component] IDs and [plugin][glossary-plugin] identities for
both slots. The builder uses the library-qualified script identity to resolve
that description within this workspace:

```python
runtime = builder.build_script(ScriptRequest(
    LibraryScript("example_library", "scalar_pipeline"),
    configuration="Default"))
```

`ScriptPath` and `ScriptDescriptionPath` are other public request sources for
loading by source path or explicit description path. They select the same kind
of saved slot configuration.

### Configure, activate, and execute

The runner configures the loaded [components][glossary-component], then activates the context's
subcomponents explicitly:

```python
runtime.configure().require_success("configure pipeline components")
context = runtime.get_context()
context.activate_subcomponents().require_success("activate pipeline components")
```

A [script][glossary-script] [runtime][glossary-runtime] has [slots][glossary-slot] and services rather than a root [plugin][glossary-plugin] instance.
There is no `runtime.get_instance()` for scripts. The runner uses standard
Python `runpy.run_path()` to load the [library][glossary-library]'s class and calls its body:

```python
module = runpy.run_path(str(script.path))
pipeline = module["ScalarPipeline"]()
totals = pipeline.run(context, [1.0, 2.0, 3.0])
```

Look for:

```text
input=1, transformed=3, total=3
input=2, transformed=5, total=8
input=3, transformed=7, total=15
Pipeline totals: [3.0, 8.0, 15.0]
```

The affine component computes `2 * value + 1`; the accumulator remembers the
sum across successive calls. A `finally` block closes the script runtime and its
components even if execution raises. Rerunning constructs fresh runtime state.

### Inspect the saved script and configuration

```bash
workspace="$RPP_HOME/tutorials/example_library"

# The library workspace publishes scalar_pipeline as a script.
rpp ws script list "$workspace"
rpp ws script config list "$workspace" scalar_pipeline

# Inspect the slot specification, assignments, and saved component identities.
rpp ws info "$workspace" --json
rpp ws component list "$workspace"
rpp ws component parameter get "$workspace" pipeline_processor
```

The [script][glossary-script] description is at
`$RPP_HOME/tutorials/example_library/.rppws/script_descriptions/scalar_pipeline.json`.
Its `Spec` contains the [slot][glossary-slot] contracts, while
`Configurations.Default.Components` contains their selected [component][glossary-component] IDs and
[plugin][glossary-plugin] identities. Changing assignments selects components for future [runtime][glossary-runtime]
construction without changing the script's processing logic.

[glossary-plugin]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
[glossary-library]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#library "Library: a source directory grouping Plugin Types, Plugins, and related files."
[glossary-workspace]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#workspace "Workspace: a project directory containing saved component and script configuration in .rppws."
[glossary-runtime]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#runtime "Runtime: an application-owned execution handle built from saved configuration."
[glossary-script]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#script "Script: application logic declaring named component slots and using their assigned components."
[glossary-slot]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#slot "Slot: a named, typed location for components in a script or composite plugin."
[glossary-parameter]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#parameter "Parameter: a named configuration value resolved for a component instance."
