# Tutorial 3 Registration

[package.json](../../../src/rpp_demos/tutorials/example_library/package.json) identifies the library.
[plugins.json](../../../src/rpp_demos/tutorials/example_library/plugins.json) lists contracts under
`PluginTypes` and implementations under `Plugins`, with relative source paths.

[run.py](../../../src/rpp_demos/tutorials/03_registration/run.py) calls `LibraryManager.register_plugin_library` with
`link_register=True`. RPP registers the type and generates its interface before
registering the implementation. The linked source is a persistent copy under
`$RPP_HOME/tutorials/example_library`. Later runs refresh this registration.

Use the [shared prerequisites](README.md#prerequisites-and-execution):

From `rpp_dev/src/rpp_demos`:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
rpp init-home
python3 tutorials/03_registration/run.py
```

A lookup for `example_library::MissingPlugin` demonstrates an unknown identity.
Then look for:

```text
Registered: example_library::AffineProcessor -> example_library::ScalarProcessor
Refreshed: example_library::AffineProcessor
```

The driver appends a comment to the copied source and calls
`refresh_plugin_library`, updating the same identity. It then removes that
source and calls explicit `register_plugin_from_source`, producing an expected
missing-file error. Whole-library refresh may skip missing files with a warning;
explicit registration demonstrates the error directly. A `finally` block
restores the source so the persistent registration remains usable.

Registration creates no configured component or active instance. Registry
records, generated artifacts, and copied sources remain in the selected
`RPP_HOME`; the checked-in example sources are unchanged.
