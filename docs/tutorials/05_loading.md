# Tutorial 5 Loading and invocation

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

Load saved components, configure and activate their runtimes, and call them through the generated contract.

[run.py](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/05_loading/run.py) constructs runtime handles using
`ComponentRuntimeBuilder.build_component(ComponentRequest(record.folder))`.
The runtime resolves the saved component and registered implementation.
Loading alone does not activate it: configure and activate before invocation.
The caller imports the generated `ScalarProcessor` contract without importing
the concrete implementation.

## Implementation

### Run the example

```bash
python3 tutorials/05_loading/run.py
```

Look for:

```text
Loaded processor; active=False
processor = 7
Loaded identity; active=False
identity = 3
```

The driver then reports expected failures for an unknown workspace component
and an absent component description path. All constructed runtimes close
on exit, including on invocation failures. The workspace and registry persist
in `RPP_HOME`.

### Inspect the result

Trace the saved component back to its registered implementation:

```bash
workspace="$RPP_HOME/tutorials/05_loading/workspace"

# Find the two components and inspect processor's plugin identity.
rpp ws component list "$workspace"
rpp ws component info "$workspace" processor

# Locate the component folder and parameter files used during loading.
rpp ws component context "$workspace" processor

# Inspect the implementation resolved from that component's plugin identity.
rpp library example_library info AffineProcessor
```

Follow the `example_library::AffineProcessor` identity from the component info
to the implementation metadata, then inspect its contract with
`rpp registry info example_library::ScalarProcessor`. This is the chain the
builder resolves when loading a saved component. The CLI commands inspect
persistent descriptions; they do not construct or activate a runtime. Rerun
the driver to observe configuration, activation, and method calls again.
