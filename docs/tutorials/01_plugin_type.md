# Tutorial 1 Plugin type definition

Read [the annotated schema](../../../src/rpp_demos/tutorials/example_library/plugin_types/scalar_processor.capnp)
and its `PluginTypes` entry in [plugins.json](../../../src/rpp_demos/tutorials/example_library/plugins.json).
The contract accepts and returns one `Float64`. Gain and offset will be instance
settings. The annotation marks an RPP plugin type; an unannotated interface is
an ordinary Cap'n Proto interface. Keep published file IDs and ordinals stable.

Use the [shared prerequisites](README.md#prerequisites-and-execution),
then run from `rpp_dev/src/rpp_demos`:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
rpp init-home
python3 tutorials/01_plugin_type/run.py
```

[run.py](../../../src/rpp_demos/tutorials/01_plugin_type/run.py) omits implementations from the copied manifest under `$RPP_HOME/tutorials`, registers
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
