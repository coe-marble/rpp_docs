# Tutorial 5 Loading and invocation

[run.py](../../../src/rpp_demos/tutorials/05_loading/run.py) constructs runtime handles using
`ComponentRuntimeBuilder.build_component(ComponentRequest(record.folder))`.
The runtime resolves the saved component and registered implementation.
Loading alone does not activate it: configure and activate before invocation.
The caller imports the generated `ScalarProcessor` contract without importing
the concrete implementation.

Use the [shared prerequisites](README.md#prerequisites-and-execution).
The driver prepares its own registration and workspace:

From `rpp_dev/src/rpp_demos`:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
rpp init-home
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
