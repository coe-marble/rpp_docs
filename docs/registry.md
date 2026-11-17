# Registry, registration, and upgrades

`rpp_plugin_registrator` discovers annotated [plugin types][glossary-plugin-type], validates Python/C++
implementations, records library metadata, and generates interfaces and adapters.
Use the public `rpp` [CLI](cli.md) and `LibraryManager` API. The old standalone
`rpp_registrator.py` command examples are superseded by these interfaces.

## Home and source ownership

Select `RPP_HOME` before importing RPP or use `rpp --rpp-home DIRECTORY ...`.
The default home is `~/.rpp`. Configuration and generated modules are cached;
use a fresh process when changing homes.

| Location under the home | Purpose |
| --- | --- |
| `config.json` | Registry settings |
| `.initialized` | Initialization marker |
| `libraries/` | Managed copies or links to registered source libraries |
| `registry/rpp_plugin_types.json` | [Plugin-type][glossary-plugin-type] index |
| `registry/libraries/<library>/manifest.json` | Library registration metadata |
| `registry/libraries/<library>/rpp_plugins/` | Implementation descriptions |
| `registry/libraries/<library>/rpp_plugin_types/` | Type descriptions |
| `registry/capnp/` | Registered schemas |
| `registry/cpp/shared/` | Compiled [plugin][glossary-plugin] and plugin-type libraries |
| `interfaces/` | Generated language interfaces and adapters |

Library `package.json` (or `package.xml`) supplies package metadata;
`plugins.json` declares type sources, implementation sources, and dependencies.
Keep declared source paths relative to the library. A linked registration keeps
sources in their checkout; a copied registration owns its managed copy.
Workspace settings and saved [component][glossary-component] identity are separate from registration.

```bash
rpp library register /path/to/my_library --link
rpp library info my_library
rpp library my_library list --type
rpp library refresh my_library
```

Library lookup resolves a bare library name through its registered location
before considering a same-named working-directory folder. Use an explicit path
when you intend to select a filesystem location.

Registration publishes a plugin; it does not configure or activate a runtime.
Generated schema IDs are preserved when an already registered Cap'n Proto file
is registered again. Keep published file IDs and field/method ordinals stable.

## C++ registration profiles

Select the global default:

```bash
rpp registry config set BUILD_TYPE RelWithDebInfo
rpp registry config get BUILD_TYPE
rpp library refresh my_library
```

The default is `RelWithDebInfo`. Supported modes are `Debug`, `Release`, and
`RelWithDebInfo`. This setting governs registration builds independently of
CMake's build type for the runtime or application. Existing artifacts need
refreshing to use a new profile.

Debug and RelWithDebInfo validation binaries retain symbols for GDB metadata
extraction and can be reused for registration. Release uses a separate debug
validation build, then compiles the installed optimized binary. The GDB helper
remains an unoptimized debug build. [Plugin types][glossary-plugin-type] use the requested profile.

API calls can select a profile without changing the global setting:

```python
manager.refresh_plugin_library("my_library", build_type="Debug")
manager.register_plugin_from_source(source_path, "my_library", build_type="Release")
```

In the [plugin][glossary-plugin] manager GUI, **Register in Debug** selects the requested mode for
registration/refresh. Unchecked selects Release, independently of the global
RelWithDebInfo default. The read-only **Debug** column reports the recorded
mode, with older untracked modes shown as Unknown in its tooltip. Worker-based
registration keeps logs available; build failures retain diagnostic details.

## Upgrade an existing registry

After installing matching updated packages and rebuilding the native runtime,
stop [plugin][glossary-plugin] managers and applications using generated interfaces. Preview the
migration, then apply it:

```bash
rpp registry migrate --dry-run
rpp registry migrate
```

For another home, put `--rpp-home DIRECTORY` before `registry migrate`.
Migration targets the installed registrator version; it does not upgrade Python
packages. It regenerates bundled native libraries (`rpp_common`, `rpp_testing`)
and refreshes registered user libraries in dependency order, including libraries
already marked current. This may compile native code and requires the normal
registration toolchain.

The preview writes nothing and does not compile. Missing dependencies, cycles,
missing declared sources, and libraries registered by a newer registrator are
reported before regeneration.

Migration preserves library registrations, linked source paths, and workspace
data. Before regeneration it makes a complete sibling backup of the registry
home and prints the backup path. On regeneration failure or interruption it
restores generated files and registrations from that backup. The backup remains
available after success or failure. `--no-restore` retains the backup but leaves
partial migration changes in place on failure. With all RPP processes stopped,
manual recovery copies the backup's contents back into the selected home.
Restart applications after a successful migration.

`rpp init-home --override` deletes and recreates generated directories and
installed libraries. Use migration to preserve an existing installation.

## Generated-code compatibility

The removed `initialize()` API, managed lifecycle interfaces, and RPC control
protocol require matching generators, Python/C++ runtimes, and compiled adapters.
Regenerate dependent libraries and rebuild downstream C++ code together.
Generated adapter clients support ordinary calls and remote configure/cleanup;
remote activation/deactivation and typed state handover remain pending.

C++ interface headers (`<Type>.hpp`) keep adapter implementations separate.
Code constructing adapters includes `<Type>_Adapter_Client.hpp` or
`<Type>_Adapter_Server.hpp` explicitly. Native-only code can include the interface
without introducing adapter linkage.

C++ returned RPC views now retain their original response rather than borrowing
a destroyed response. Existing generated adapters do not acquire this fix until
regenerated and rebuilt. See [result lifetime](component_connection.md#c-rpc-result-lifetime)
for shutdown and thread-affinity requirements.

Source references: [registry paths and settings](https://github.com/coe-marble/rpp_plugin_registrator/blob/develop/rpp_plugin_registrator/registry_config.py),
[library manager](https://github.com/coe-marble/rpp_plugin_registrator/blob/develop/rpp_plugin_registrator/library_manager.py),
and [C++ registration profiles](https://github.com/coe-marble/rpp_plugin_registrator/blob/develop/rpp_plugin_registrator/plugin_registrator/cpp.py).

[glossary-plugin-type]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#plugin-type "Plugin Type: a language-neutral contract implemented by plugins."
[glossary-plugin]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
