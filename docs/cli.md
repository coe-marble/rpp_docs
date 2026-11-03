# RPP CLI

The `rpp` executable is installed by `rpp_cli`. It manages libraries, plugin
registrations, workspaces, scripts, components, and test fixtures.

Run commands from the shell where RPP is installed. Paths are relative to the
current directory unless otherwise stated. Use `rpp --help` or append `--help`
to a command group for its arguments. In the reference below, uppercase words
are placeholders and square brackets mark optional arguments.

## Registry home and GUIs

```text
rpp [--rpp-home DIRECTORY] COMMAND ...
rpp init-home [--override] [--init-anot-only]
rpp pm
rpp ws [--root WORKSPACE_PATH]
```

The registry home defaults to `~/.rpp`, or the `RPP_HOME` environment variable
when set. Put `--rpp-home` before the command to select another home:

```bash
rpp --rpp-home ./demo-home init-home
rpp --rpp-home ./demo-home registry list --json
```

`init-home` initializes the home layout; `--override` rebuilds generated
registry/interface state, and `--init-anot-only` initializes only the annotation
schema. `pm` launches the plugin manager. `ws` without a subcommand launches
the workspace GUI, optionally at `--root`.

## Registry inspection and settings

```text
rpp registry describe SOURCE
rpp registry list [--plugins] [--library LIBRARY] [--json]
rpp registry info LIBRARY::PLUGIN_TYPE
rpp registry config [list]
rpp registry config get SETTING_NAME
rpp registry config set SETTING_NAME VALUE
```

`describe` prints parsed metadata and validation results for Python/C++ plugins
or Cap'n Proto plugin types. `list` shows plugin types by default; `--plugins`
selects implementations. `info` reads a registered plugin-type record, using
its qualified name rather than an internal ID. Use the library commands below
to inspect a plugin implementation.

Setting names are uppercase. The supported settings are `USE_ROS2_COMPILATION`
and `RPP_CPP_CORE_PATH`:

```bash
rpp registry config get USE_ROS2_COMPILATION
rpp registry config set USE_ROS2_COMPILATION false
rpp registry config set RPP_CPP_CORE_PATH /absolute/path/to/build/rpp_cpp
```

## Libraries, plugins, and plugin types

```text
rpp library create LIBRARY [--path DIRECTORY]
rpp library register LIBRARY_PATH [--link]
rpp library unregister LIBRARY
rpp library refresh LIBRARY
rpp library info LIBRARY
rpp library list

rpp library LIBRARY register SOURCE [--type] [--override]
rpp library LIBRARY refresh PLUGIN [PLUGIN ...]
rpp library LIBRARY unregister NAME [--type]
rpp library LIBRARY list [--type]
rpp library LIBRARY info NAME [--type]
```

`create` without `--path` creates the library under the registry home's
`libraries` directory. With `--path`, the directory must already exist; RPP
creates `DIRECTORY/LIBRARY` and registers it as a linked library. No additional
`register` command is needed:

```bash
mkdir -p ../libraries
rpp library create demo --path ../libraries
```

For an existing library, `register` copies it into the home by default.
`--link` keeps it at its current location. `unregister` removes that managed
copy or link; the external source of a linked library is retained.

Named library operations select plugin implementations by default. `--type`
selects plugin types; `register --type` accepts a Cap'n Proto source file.
`--override` applies to plugin-type registration. Registering an existing
implementation updates its metadata. Plugin sources must be inside their
library, normally under `plugins`; type sources belong under `plugin_types`.

For example, from the `rpp_dev` checkout after creating `demo` as above:

```bash
rpp library demo register ../libraries/demo/plugin_types/Controller.capnp --type
rpp library demo register ../libraries/demo/plugins/Controller.py
rpp library demo list
rpp library demo list --type
rpp library demo info Controller
rpp library demo refresh Controller
```

Whole-library `refresh` reads `plugins.json`. Named plugin `refresh` uses the
registered source path and unregisters/re-registers the selected implementation.

## Workspaces and scripts

```text
rpp ws create LIBRARY
rpp ws list [--json]
rpp ws info [WORKSPACE] [--json]
rpp ws script list [WORKSPACE] [--json]
rpp ws script create WORKSPACE NAME [--path DIRECTORY] [--language {python,cpp}]
rpp ws script load SCRIPT_REFERENCE [--workspace WORKSPACE]
rpp ws script load-file WORKSPACE SOURCE
rpp ws script remove WORKSPACE SCRIPT_REFERENCE
```

`ws create` initializes `.rppws` in an already registered library; its argument
is a library name. Other workspace operations accept a workspace path or a
registered library name containing `.rppws`. Where optional, `WORKSPACE`
defaults to the current directory.

`ws list` discovers registered libraries that contain workspaces and displays
their script references. `ws info` describes one workspace and its components.
Script references may be displayed names, filenames, or paths; ambiguous names
are rejected. Quote names containing spaces.

For script creation, `NAME` must contain no directory. `--path` selects an
existing directory relative to the workspace root and cannot escape it.
Without a filename extension, `--language` chooses Python by default or C++.

`script load` links a script discovered through `ws list`. A library name is
also accepted when that library has exactly one available script. `load-file`
links an existing file directly. Removing a linked script preserves its source.

## Script configurations

```text
rpp ws script config list WORKSPACE SCRIPT [--json]
rpp ws script config create WORKSPACE SCRIPT CONFIGURATION
rpp ws script config copy WORKSPACE SCRIPT SOURCE_CONFIGURATION NEW_CONFIGURATION
rpp ws script config rename WORKSPACE SCRIPT CONFIGURATION NEW_NAME
rpp ws script config activate WORKSPACE SCRIPT CONFIGURATION
rpp ws script config remove WORKSPACE SCRIPT CONFIGURATION
rpp ws script config import WORKSPACE SOURCE_WORKSPACE::SCRIPT CONFIGURATION
```

New scripts start with a `Default` configuration. `copy` duplicates assignments
within the same script; it does not copy component instances. `import` copies
the source configuration and its component trees into the target workspace,
giving the copied components new IDs. First link the source script into the
target using its reference from `ws list`:

```bash
rpp ws script load source_workspace::simulation --workspace demo
rpp ws script config import demo source_workspace::simulation Experiment
```

`Experiment` must exist on the source script and must not already exist on the
linked script in the target. Imports reject linked component trees, missing
component references, and component names already present in the target.

## Components, assignments, and parameters

```text
rpp ws component create WORKSPACE NAME LIBRARY::PLUGIN
rpp ws component list WORKSPACE [--json]
rpp ws component info WORKSPACE COMPONENT
rpp ws component rename WORKSPACE COMPONENT NEW_NAME
rpp ws component duplicate WORKSPACE COMPONENT [NEW_NAME]
rpp ws component remove WORKSPACE COMPONENT
rpp ws component assign WORKSPACE SCRIPT SLOT COMPONENT [--configuration NAME]
rpp ws component unassign WORKSPACE SCRIPT COMPONENT [--slot SLOT] [--configuration NAME]
rpp ws component subcomponent create WORKSPACE PARENT SLOT NAME LIBRARY::PLUGIN
rpp ws component subcomponent assign WORKSPACE PARENT SLOT COMPONENT
rpp ws component subcomponent remove WORKSPACE PARENT SLOT COMPONENT
rpp ws component parameter get WORKSPACE COMPONENT [PARAMETER]
rpp ws component parameter set WORKSPACE COMPONENT PARAMETER VALUE
rpp ws component context WORKSPACE COMPONENT
```

`COMPONENT` and `PARENT` accept component names or IDs from `component list`.
Script assignments use the active configuration unless `--configuration` is
specified. Subcomponent commands operate on a particular parent's slot.
`context` prints the component, descriptor, and parameter-source paths as JSON.

Parameter `get` prints one value or all values as JSON. `set` parses valid JSON
values and treats other input as a string. Quote JSON objects/arrays so the
shell passes them as a single argument:

```bash
rpp ws component parameter set demo Controller gain 2.5
rpp ws component parameter set demo Controller enabled false
rpp ws component parameter set demo Controller gains '[1.0, 2.0]'
rpp ws component parameter get demo Controller
```

Parameter names must be valid Python attribute names. For a linked component,
parameter operations use its resolved source folder.

## Compilation, test fixtures, and completion

```text
rpp compile SOURCE [--plugin-type-name LIBRARY::TYPE] [--library LIBRARY] [--verbose] [--type {plugin,plugin-type}]
rpp test setup_tmp_rpp_with_test_plugins [OUTPUT_DIRECTORY] [--override]
rpp completion [--shell bash]
```

`compile` currently compiles `.cpp` and `.hpp` implementations into a temporary
shared library for diagnostics; it does not install the result. It attempts to
infer the plugin type unless `--plugin-type-name` is supplied. Compiler failures
print diagnostics to standard error and return exit code 1; success returns 0. The
`--type plugin-type` branch currently checks the source extension and reports
it; it does not invoke interface generation. Register a type through
`library LIBRARY register SOURCE --type` to generate its interfaces.

The test command creates RPP fixtures from `rpp_testing` and prints their paths
and plugin metadata as JSON. An explicit output directory must already exist.
This command prepares fixtures; it does not run pytest.

Only Bash completion is supported. Enable it in the current Bash shell with:

```bash
eval "$(rpp completion --shell bash)"
```
