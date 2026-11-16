# Tutorial 1 Plugin type definition

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

Define and register a plugin contract before adding an implementation.

Read [the annotated schema](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugin_types/scalar_processor.capnp)
and its `PluginTypes` entry in [plugins.json](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugins.json).
The contract accepts and returns one `Float64`. Gain and offset will be instance
settings. The annotation marks an RPP plugin type; an unannotated interface is
an ordinary Cap'n Proto interface. Keep published file IDs and ordinals stable.

## Implementation

### Run the example

```bash
python3 tutorials/01_plugin_type/run.py
```

[run.py](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/01_plugin_type/run.py) omits implementations from the copied manifest under `$RPP_HOME/tutorials`, registers
the type, and imports its generated interface. Tutorial 3 explains registration.
Look for:

```text
Registered type: example_library::ScalarProcessor
Generated interface: ScalarProcessor
Implementations: 0
```

A lookup for `MissingType` produces an expected failure: only registered
identities resolve. The registry and generated interfaces remain in `RPP_HOME`
after exit.

### Inspect the result

After running the driver, inspect the registered type from the same shell:

```bash
# List registered plugin types; look for example_library::ScalarProcessor.
rpp registry list

# Show the type's registered description as JSON.
rpp registry info example_library::ScalarProcessor

# Restrict the list to this tutorial's library.
rpp registry list --library example_library

# List implementations registered by this tutorial: there should be none yet.
rpp registry list --plugins --library example_library
```

`registry list` lists plugin types by default; `--plugins` selects their
implementations. Inspect the JSON description to connect the registered type
to the contract in `scalar_processor.capnp`. Both commands read the home selected
by `RPP_HOME`, here `~/.rpp_tutorials`.
