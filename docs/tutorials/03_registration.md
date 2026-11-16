# Tutorial 3 Registration

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

Register a library, inspect its identities, and refresh registration after a source change.

[package.json](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/package.json) identifies the library.
[plugins.json](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugins.json) lists contracts under
`PluginTypes` and implementations under `Plugins`, with relative source paths.

[run.py](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/03_registration/run.py) calls `LibraryManager.register_plugin_library` with
`link_register=True`. RPP registers the type and generates its interface before
registering the implementation. The linked source is a persistent copy under
`$RPP_HOME/tutorials/example_library`. Later runs refresh this registration.

## Implementation

### Run the example

```bash
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

### Inspect the result

Explore the persistent registration after running the driver:

```bash
# List libraries registered in the tutorial home.
rpp library list

# Show the example library's metadata, registered types, and implementations.
rpp library info example_library

# List this library's contracts, then its implementations.
rpp library example_library list --type
rpp library example_library list

# Refresh registration after editing the copied example sources.
rpp library refresh example_library
```

The registered library points to `$RPP_HOME/tutorials/example_library`. Make
experimental edits in that copy, then refresh to update its registered
artifacts. Inspect `rpp library example_library info AffineProcessor` afterward
to see the implementation's metadata. Rerunning a tutorial restores the example
sources from the checkout, so keep any edits you want to retain elsewhere.
