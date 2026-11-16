# Core workflows

This page describes the main RPP workflows for libraries, plugins, interfaces, components, and workspaces. It is not a complete reference for every command; see [CLI](cli.md) for the full command set.

# Using libraries

RPP libraries should normally live outside the `rpp_dev` repository. The
recommended layout is to place a `libraries` directory beside `rpp_dev`, so
the integration checkout and user-owned libraries have the same parent:

```text
rpp/
├── libraries/
│   ├── rpp_control/
│   └── my_library/
└── rpp_dev/
```

Create or register a library from the `rpp_dev` environment with:

```bash
mkdir -p ../libraries
rpp library create my_library --path ../libraries
```

`create --path` creates and links the library in that directory. To register
an existing library there, use `rpp library register ../libraries/my_library --link`
instead. The `--link` option keeps the library at its original path. This is useful
during development because changes to plugin source and `plugins.json` remain
in the working library. A copied registration can be used when the library
should be managed independently of its original checkout.

## Libraries in a ROS 2 workspace

When RPP is used with ROS 2, place both the integration checkout and the
libraries inside the ROS workspace's `src` directory:

```text
ros_ws/
└── src/
	├── libraries/
	│   ├── rpp_control/
	│   └── my_library/
	└── rpp_dev/
```

In this layout, the parent of `rpp_dev` is `src`, and libraries remain
discoverable as sibling projects in the ROS workspace.

## Create and register a library

```bash
rpp library create my_library
rpp library my_library register path/to/plugin.py
rpp library refresh my_library
rpp library info my_library
```

Use `--link` when the library should remain at its existing location during
development. A copied registration is preferable for a relocatable library
bundle.

Every library contains a `plugins.json` file. Its `Plugins` array declares
concrete plugin implementations, while its `PluginTypes` array declares the
Cap'n Proto files containing plugin interfaces.

## Describe and register a plugin

The registrator can inspect a source file before changing the registry:

```bash
rpp registry describe path/to/plugin.py
rpp library my_library register path/to/plugin.py
```

Registration creates or updates plugin metadata and makes the plugin available
to workspace component creation. The registry uses plugin identity as its
upsert key, so registering the same identity updates the existing record.

## Generate an interface

Interfaces are generated from plugin type metadata rather than handwritten per
language:

The interface generator is owned by `rpp_plugin_registrator`. Register the
Cap'n Proto type source through the CLI to generate its interfaces:

```bash
rpp library my_library register path/to/my_library/plugin_types/Controller.capnp --type
```

The source must be inside the library. Use `--override` when replacing an
already registered type.

Generated interfaces live under `~/.rpp/interfaces` by default and must be
available to the runtime that loads the corresponding plugin. Registration can
compile native artifacts; see [profiles and compatibility](registry.md).

## Compose a workspace

```bash
rpp library create demo
rpp ws create demo
rpp ws --root <path-to-demo-library>
```

The workspace stores script descriptions/configurations and saved component
folders in `.rppws`; script source can live in the project directory. Each
component folder is self-contained and can be copied and registered/loaded in
another workspace or runtime. It includes its description, Python parameter
definition, local data, and concrete nested components. See
[folder layout and component reuse](workspaces.md#workspace-and-rppws-folder-layout)
and [Python parameters and YAML](workspaces.md#parameters-are-python-definitions).
Keep source libraries outside the workspace when they are shared by multiple
workspaces.

## Execute a saved configuration

Build a `ComponentRuntime` from a saved component or a `ScriptRuntime` from a
script's selected configuration. Construction prepares instances/transports;
configure resources and activate native components explicitly before calling
them. Close the runtime and check its result when finished.

See [managed lifecycle](runtime-lifecycle.md) for Python/C++ usage, slot
permissions, switching, handover, and shutdown. The
[workspace guide](workspaces.md) documents the configuration-based script format;
the old top-level `Components` description format is unsupported.

## Maintain an installation

Use [registry migration](registry.md#upgrade-an-existing-registry) after updating
the registrator and matching runtime artifacts. Refresh/reload are distinct:
registration refresh updates generated artifacts, while runtime reload replaces
a loaded instance using registered artifacts. ROS slot reload does not compile
or refresh the registry.

## Development checks

Package checks use each implementation repository's CI and declared test
extras. See [testing support](testing.md), the [test image](test-image.md), and
[integration CI](integration.md) for fixtures and coordinated revision checks.
