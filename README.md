
# Robotics Plugin Platform (RPP) Documentation

> Unofficially, RPP stands for **Robotics Plus Plus**. Following the proud
> industry tradition of adding a plus sign and calling it the next generation.

RPP is a language-independent framework for defining, registering, composing,
and executing robotics plugins. It separates plugin contracts from concrete
implementations, so the same system can support multiple languages, custom
plugin types, and reusable components.

## Motivation

RPP is inspired by nav2 and similar plugin architectures, but addresses two
limitations that become important as a system grows. First, adding a new
plugin type should be straightforward: developers can define a new type and
make it available to the rest of the system without changing a fixed central
list of built-in types. Second, a plugin system should not force every plugin
to use the same implementation language. RPP solves this by defining plugin types in a language-neutral schema, generating language-specific interfaces, and providing adapters for supported runtimes. In this way, a plugin type can be implemented in one language and used in another without requiring the plugin author to write language-specific code for each runtime.

## Supported languages

RPP currently supports:

- **Python**, through the `rpp_py` runtime.
- **C++**, through the `rpp_cpp` runtime.

## Quick start

The integration checkout is `rpp_dev`. Initialize its submodules and install
the Python packages with:

```bash
git submodule update --init --recursive
./setup.sh
```

For C++ support, build the runtime and source the generated environment:

```bash
colcon build --symlink-install
source install/setup.bash
```

Then launch the main tools:

```bash
rpp pm                 # plugin manager GUI
rpp ws                 # workspace GUI
rpp ws create demo /tmp
```

See [Installation and first run](docs/getting-started.md) for prerequisites,
ROS 2 configuration, and the complete setup flow.

## How RPP fits together

RPP is organized around three stages:

1. **Define** a language-neutral plugin type and its interface.
2. **Register** concrete implementations and their metadata in the RPP home
    directory, normally `~/.rpp`.
3. **Compose and execute** plugin instances as components inside an RPP
    workspace, identified by its `.rppws` directory.

The registry owns metadata and generated interfaces. Libraries own plugin
source. Workspaces own composition, configuration, and component state. This
separation allows one implementation to be reused across multiple workspaces.

## Documentation map

- [System architecture](docs/architecture.md): layers, responsibilities, and runtime data flow.
- [Repository catalog](docs/repositories.md): every RPP submodule and its public entry points.
- [CLI](docs/cli.md): `rpp` commands for registry, libraries, workspaces, and testing.
- [Plugin types and interfaces](docs/plugin-types.md): extension contracts and language boundaries.
- [Installation and first run](docs/getting-started.md): development setup, C++, and ROS 2.
- [Core workflows](docs/workflows.md): libraries, plugins, interfaces, components, and workspaces.
- [Contributing documentation](docs/contributing.md): ownership and maintenance rules for this documentation.

## Documentation ownership

System documentation is maintained here rather than scattered across the
submodules:

- `rpp_docs` owns architecture, terminology, integration behavior, and
  cross-repository workflows.
- Each implementation repository owns package-local API details and source
  examples in its own README.
- `rpp_dev` owns the integration checkout and submodule revisions.

The repository inventory is declared in
[`docs/repositories.yml`](docs/repositories.yml). Validate it from a checkout
of `rpp_dev` with:

```bash
python3 tools/check_repositories.py --workspace ../
```

The dependency-free checker confirms that all seven declared submodule paths
exist. It does not copy or modify files in the implementation repositories.
