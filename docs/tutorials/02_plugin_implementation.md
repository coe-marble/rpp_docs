# Tutorial 2 Plugin implementation

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

Implement the contract and observe how parameters change the behavior of separate component instances.

[AffineProcessor](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugins/affine_processor.py) inherits the
generated interface. `PARAMETERS` declares gain and offset defaults.
Configuration validates both values before committing them to instance state.
Activation permits processing, deactivation blocks it, and cleanup releases
its coefficients. Separate instances share no mutable configuration.

## Implementation

### Run the example

```bash
python3 tutorials/02_plugin_implementation/run.py
```

Look for:

```text
default = 3
configured = 7
Expected failure (configure invalid.gain): ...gain must be a finite number...
```

The last component supplies a string gain and fails configuration. The plugin
also rejects non-finite coefficients, inputs, and results. Its own active flag
protects calls through retained native references while inactive. All runtime
handles close on exit, including the partially configured component. The
workspace and registry remain in `RPP_HOME` for inspection.

### Inspect the result

After the driver finishes, compare the contract and its implementation:

```bash
# List the implementation now registered for the example library.
rpp registry list --plugins --library example_library

# Inspect the implementation's metadata, including its plugin type.
rpp library example_library info AffineProcessor

# Inspect the contract implemented by AffineProcessor.
rpp registry info example_library::ScalarProcessor

# Inspect the configured component's saved gain and offset.
workspace="$RPP_HOME/tutorials/02_plugin_implementation/workspace"
rpp ws component parameter get "$workspace" configured
```

The implementation should identify `example_library::ScalarProcessor` as its
type. The `configured` component saves gain `2` and offset `1`; `default` uses
the defaults declared by the plugin. Use `rpp ws component list "$workspace"`
to see the separate component instances created from that one implementation.
