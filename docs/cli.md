# RPP CLI

The `rpp` executable is installed by `rpp_cli` and is the integration entry
point for registry, library, workspace, test, and GUI operations.

## Top-level commands

```text
rpp init-home
rpp pm
rpp ws [create ...]
rpp registry <describe|list|info|config>
rpp library <command>
rpp test <command>
rpp compile <source>
```

The `pm` command launches the plugin manager GUI. The `ws` command launches
the workspace GUI when no subcommand is provided.

Use `rpp --help` and `<command> --help` for the complete argument list.

## Common commands

Inspect a plugin source file without registering it:

```bash
rpp registry describe path/to/plugin.py
```

Inspect registry state and configuration:

```bash
rpp registry list
rpp registry info <plugin-id>
rpp registry config
rpp registry config USE_ROS2_COMPILATION=True
```

Manage a library:

```bash
rpp library create my_library
rpp library register path/to/library --link
rpp library my_library register path/to/plugin.py
rpp library my_library info
rpp library list
```

Create or open a workspace:

```bash
rpp ws create demo /tmp
rpp ws --root /tmp/demo
```


