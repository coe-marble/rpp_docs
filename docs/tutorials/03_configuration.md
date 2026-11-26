# Tutorial 3 Configuration and composition

## Prerequisites

Follow the [shared prerequisites](README.md#prerequisites-and-execution) and complete
[Tutorial 02: CLI registration](02_registration.md).
Keep using the same tutorial home:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
```

Run from `rpp_dev/src/rpp_demos`. The example [library][glossary-library] must already be linked
and its types and [plugins][glossary-plugin] registered through the CLI. This example uses public
RPP APIs directly in a standalone Python script.

## Description

Create two [components][glossary-component] from one implementation and inspect their independent saved settings.

An implementation is reusable; a component is a self-contained saved
configuration of that implementation. [run.py](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/03_configuration/run.py) creates `processor` and `identity` with
`Workspace.create_component`, using the same plugin and distinct component IDs.
`component_parameter_store.save` persists processor settings. Identity uses
the defaults. Both are configured without activation.

## Implementation

### Run the example

```bash
python3 tutorials/03_configuration/run.py
```

The driver prints component IDs and [parameter][glossary-parameter] file paths. Look for gain `2`,
offset `1` for processor, and gain `1`, offset `0` for identity.

Resolution is plugin defaults, saved component settings, then builder overrides.
The driver demonstrates a string gain in saved settings and an infinite gain
through `set_parameter_overrides`; both produce expected configuration failures.
The final two lines are deliberately labeled `Expected failure`:

```text
Expected failure (invalid saved gain): success=False; ...gain must be a finite number
Expected failure (invalid gain override): success=False; ...gain must be a finite number
```

These rejections demonstrate validation working correctly; they do not indicate
that the tutorial failed.

Builder overrides are keyed by qualified plugin identity and affect matching
native Python components in future builds, rather than editing one component.

[Runtime][glossary-runtime] construction snapshots parameters. Close and rebuild to read changed
[workspace][glossary-workspace] settings. Independent roots are sufficient here; scripts and nested
component [slots][glossary-slot] can follow in another tutorial. Runtime handles close
automatically; workspace data remains under `$RPP_HOME/tutorials`.

See [component folders and workspace layout](../workspaces.md#workspace-and-rppws-folder-layout)
for copying/reusing a component, and
[Python parameter definitions and YAML](../workspaces.md#parameters-are-python-definitions)
for executable configuration and the planned shared-parameter tutorial.

### Inspect the result

Inspect the saved configuration after the driver finishes:

```bash
workspace="$RPP_HOME/tutorials/03_configuration/workspace"

# Show the workspace summary and the components it contains.
rpp ws info "$workspace"
rpp ws component list "$workspace"

# Show processor's identity and the paths to its saved configuration.
rpp ws component info "$workspace" processor
rpp ws component context "$workspace" processor

# Read all saved parameters, or just one value.
rpp ws component parameter get "$workspace" processor
rpp ws component parameter get "$workspace" processor gain
```

### Change a saved parameter

The saved gain should be `2`. To explore editing through the CLI, run:

```bash
# Save a new gain, inspect it, then restore the tutorial value.
rpp ws component parameter set "$workspace" processor gain 3.0
rpp ws component parameter get "$workspace" processor gain
rpp ws component parameter set "$workspace" processor gain 2.0
```

These commands edit the persisted component settings. A runtime reads them
when it is constructed; an existing runtime keeps its parameter snapshot.
Rerunning the driver also resets its saved parameters to the tutorial values.

## GUI

After running the example, open its saved workspace in the
workspace GUI. Use a graphical session with PyQt6 available:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
workspace="$RPP_HOME/tutorials/03_configuration/workspace"
rpp ws --root "$workspace"
```

`RPP_HOME` selects the registry used to resolve plugins; `--root` selects the
workspace containing the saved components.

1. Select `processor` in the component tree. Inspect its name, plugin identity,
   and component folder, then compare them with
   `rpp ws component info "$workspace" processor`.
2. Click **Open Parameter File** to open its saved parameter file in your system
   editor. Find gain `2` and offset `1`.
3. Select `identity` and inspect its parameter file too. Its defaults resolve
   to gain `1` and offset `0`; both components select the same plugin with
   independent saved settings.
4. To edit the processor's gain, change it to `3.0` in its parameter file and
   save the file in the editor. **Open Component Context** lets you inspect the
   surrounding component files.

Close the GUI and verify the saved edit from the terminal, then restore the
tutorial value:

```bash
rpp ws component parameter get "$workspace" processor gain
rpp ws component parameter set "$workspace" processor gain 2.0
```

Editing saved parameters affects future runtime construction.
The GUI opens the same files used by the CLI and API. Rerunning the example
resets its component parameters to the values shown in this tutorial.

[glossary-plugin]: ../glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: ../glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
[glossary-library]: ../glossary.md#library "Library: a source directory grouping Plugin Types, Plugins, and related files."
[glossary-workspace]: ../glossary.md#workspace "Workspace: a project directory containing saved component and script configuration in .rppws."
[glossary-runtime]: ../glossary.md#runtime "Runtime: an application-owned execution handle built from saved configuration."
[glossary-slot]: ../glossary.md#slot "Slot: a named, typed location for components in a script or composite plugin."
[glossary-parameter]: ../glossary.md#parameter "Parameter: a named configuration value resolved for a component instance."
