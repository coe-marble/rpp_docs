# Tutorial 2 Registration and inspection

## Prerequisites

Follow the [shared prerequisites](README.md#prerequisites-and-execution) and read
[Tutorial 01](01_plugin_types_and_plugins.md).
Run the commands below from `rpp_dev/src/rpp_demos` in your installed RPP
environment. Select the tutorial home before using the CLI:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
rpp init-home
```

## Description

Register the example [library][glossary-library] as a link using `rpp`, list its types and [plugins][glossary-plugin],
and inspect the generated Python and C++ interfaces. Start with the CLI steps
below, then explore the same registration in the Plugin Manager GUI. There is
no Python driver.

The library's [`package.json`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/package.json)
provides its identity. Its [`plugins.json`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugins.json)
lists schema files under `PluginTypes` and implementation files under `Plugins`.
A linked registration keeps the registered library associated with its source
folder, so source edits can be refreshed from the same location.

## Implementation

### Prepare a persistent source copy and link-register it

Keep the editable tutorial library under the selected home:

```bash
mkdir -p "$RPP_HOME/tutorials"
cp -a tutorials/example_library "$RPP_HOME/tutorials/"
library="$RPP_HOME/tutorials/example_library"

# Register all types and plugins declared by this library.
rpp library register "$library" --link
```

On the first registration, look for `Linked library:` followed by that source
path. If `example_library` is already linked to this folder from an earlier run,
use `rpp library refresh example_library` instead of registering it again.
`rpp library list` shows the existing registration and its source location.

Registration processes the declared types before their implementations. The
example library contains two [plugin types][glossary-plugin-type] and two Python plugins:

| Type | Plugin |
| --- | --- |
| `example_library::ScalarProcessor` | `example_library::AffineProcessor` |
| `example_library::ScalarAccumulator` | `example_library::AccumulatingProcessor` |

### Inspect the registry

```bash
# Inspect the initialized library of shared schemas from Tutorial 01.
rpp library info rpp_common

# List registered libraries and the example library's metadata.
rpp library list
rpp library info example_library

# List types, then implementations, in this library.
rpp registry list --type --library example_library
rpp registry list --library example_library

# Inspect the scalar contract and its implementation separately.
rpp registry info example_library::ScalarProcessor
rpp library example_library info AffineProcessor
```

`rpp registry list` lists implementations by default; `--type` selects types.
The type description records the contract. The plugin description identifies
its implementation source, language, and implemented type. For library-local
inspection, use `rpp library example_library list --type` and
`rpp library example_library list`.

### Inspect the Python and C++ code

Read the copied implementation and both generated contract files:

```bash
# The implementation source remains in the linked library.
less "$library/plugins/affine_processor.py"

# Registration generates these interfaces from scalar_processor.capnp.
less "$RPP_HOME/interfaces/python/rpp_plugin_types/example_library/ScalarProcessor.py"
less "$RPP_HOME/interfaces/cpp/rpp_plugin_types/example_library/ScalarProcessor.hpp"
```

Compare the Python `process` declaration and C++ `process` declaration with the
schema from Tutorial 01. They represent the same contract in each language.
`AffineProcessor` supplies the Python method body; the C++ header is a generated
interface for C++ implementations. The supplied example implementations are
Python. Edit their source files rather than generated files, which registration
can overwrite.

The other generated type is `ScalarAccumulator`; its implementation is
`AccumulatingProcessor`. Other method names listed in the generated interfaces
include `on_configure`, `on_activate`, `on_deactivate`, and `on_cleanup`.

### Register individual files and refresh edits

A library registration handles its manifest as a whole. The CLI also exposes
registration of individual types and plugins. For an already registered type,
use `--override` when registering its schema again:

```bash
rpp library example_library register \
    "$library/plugin_types/scalar_processor.capnp" --type --override
```

To practice registering an implementation file, remove only that plugin's
registration, then add it back from its source:

```bash
rpp library example_library unregister AffineProcessor
rpp library example_library register "$library/plugins/affine_processor.py"
rpp library example_library info AffineProcessor
```

The source file remains in the linked library. Unregistering removes its metadata
and manifest entry; registering the file restores them. When adding a new plugin
source later, register its file with the same command form.

After editing an existing implementation, refresh that plugin or the whole
library:

```bash
rpp library example_library refresh AffineProcessor
rpp library example_library refresh ScalarProcessor --type
rpp library refresh example_library
```

Refreshing a type re-registers its complete Cap'n Proto file, including the
other types and supporting structs defined there.

Inspect its metadata again after refreshing. These commands leave the tutorial
home, copied sources, and registration available to the following tutorials.

## GUI

Open the Plugin Manager in a graphical session with PyQt6 available. Keep the
same tutorial home so the GUI shows the registration made by the CLI:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
rpp pm
```

1. Select `example_library` in **Libraries**. Inspect its source location and
   registration information; it should point to
   `$RPP_HOME/tutorials/example_library`.
2. Browse **Plugin Types** and select `ScalarProcessor`. Compare its description
   with the output of `rpp registry info example_library::ScalarProcessor`.
3. Select `AffineProcessor` in the plugin table. Inspect its source language,
   plugin type, and metadata. Compare these with
   `rpp library example_library info AffineProcessor`.
4. After editing the copied source, use **Refresh library** to refresh the
   selected library, then inspect its metadata again.

To perform the initial link registration through the GUI instead of the CLI,
prepare the source copy above, click **Link library**, and select
`$RPP_HOME/tutorials/example_library`. For an existing registration, select it
and refresh it. **Register plugin type** and **Register plugin** select
individual source files in the selected library, corresponding to the CLI's
file-registration operations.

The GUI and CLI use the same selected RPP home. Close the GUI and run
`rpp library info example_library` to inspect the resulting metadata from the
terminal.

[glossary-plugin-type]: ../glossary.md#plugin-type "Plugin Type: a language-neutral contract implemented by plugins."
[glossary-plugin]: ../glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-library]: ../glossary.md#library "Library: a source directory grouping Plugin Types, Plugins, and related files."
