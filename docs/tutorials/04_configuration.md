# Tutorial 4 Configuration and composition

## Prerequisites

Follow the [shared prerequisites](https://github.com/coe-marble/rpp_docs/blob/develop/docs/tutorials/README.md#prerequisites-and-execution) to prepare your RPP environment.
In the shell where you will run this tutorial, select and initialize its home:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
rpp init-home
```

Run the commands below from `rpp_dev/src/rpp_demos`, using that same shell.
The driver prepares the registrations and components it needs, so it can run
independently of the other tutorials.

## Description

Create two components from one implementation and inspect their independent saved settings.

An implementation is reusable; a component is a self-contained saved
configuration of that implementation. [run.py](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/04_configuration/run.py) creates `processor` and `identity` with
`Workspace.create_component`, using the same plugin and distinct component IDs.
`component_parameter_store.save` persists processor settings. Identity uses
the defaults. Both are configured without activation.

## Implementation

### Run the example

```bash
python3 tutorials/04_configuration/run.py
```

The driver prints component IDs and parameter file paths. Look for gain `2`,
offset `1` for processor, and gain `1`, offset `0` for identity.

Resolution is plugin defaults, saved component settings, then builder overrides.
The driver demonstrates a string gain in saved settings and an infinite gain
through `set_parameter_overrides`; both produce expected configuration failures.
Builder overrides are keyed by qualified plugin identity and affect matching
native Python components in future builds, rather than editing one component.

Runtime construction snapshots parameters. Close and rebuild to read changed
workspace settings. Independent roots are sufficient here; scripts and nested
component slots can follow in another tutorial. Runtime handles close
automatically; workspace data remains under `$RPP_HOME/tutorials`.

See [component folders and workspace layout](../workspaces.md#workspace-and-rppws-folder-layout)
for copying/reusing a component, and
[Python parameter definitions and YAML](../workspaces.md#parameters-are-python-definitions)
for executable configuration and the planned shared-parameter tutorial.

### Inspect the result

Inspect the saved configuration after the driver finishes:

```bash
workspace="$RPP_HOME/tutorials/04_configuration/workspace"

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
