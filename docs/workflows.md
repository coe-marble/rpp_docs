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
rpp library create my_library ../libraries
rpp library register ../libraries/my_library --link
```

The `--link` option keeps the library at its original path. This is useful
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

The interface generator is owned by `rpp_plugin_registrator`. Use its package
CLI from that repository, or the corresponding Python API, to generate an
interface from a plugin description for the target language.

Generated interfaces live under `~/.rpp/interfaces` by default and must be
available to the runtime that loads the corresponding plugin.

## Compose a workspace

```bash
rpp ws create demo /tmp
rpp ws --root /tmp/demo
```

The workspace stores scripts and component state in `.rppws`. Components refer
to registered plugins; component folders contain descriptions, parameters,
callbacks, and nested subcomponents as needed. Keep source libraries outside
the workspace when they are shared by multiple workspaces.

## Run tests

Python package tests are run from the relevant submodule with its normal test
runner. C++ tests are configured by `colcon` and generate temporary RPP test
data through `rpp_testing`:

```bash
colcon test --event-handlers console_direct+
colcon test-result --verbose
```