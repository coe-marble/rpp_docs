# RPP tutorials

The sources live in `rpp_dev/src/rpp_demos/tutorials`; the walkthroughs live here
in `rpp_docs`. Start by reading contracts and implementations, then register
them through the CLI before moving on to [component][glossary-component] and script APIs.

| Tutorial | Focus | What you do |
| --- | --- | --- |
| [1. Plugin types and implementations](01_plugin_types_and_plugins.md) | Contracts, source files, and implementation methods | Read `rpp_common` and the example [library][glossary-library]; no driver to run |
| [2. CLI registration and inspection](02_registration.md) | Linked libraries, types, [plugins][glossary-plugin], and generated interfaces | Use `rpp` to register and inspect; read Python and C++ code |
| [3. Configuration and composition](03_configuration.md) | Component identities and independent settings | Save [parameters][glossary-parameter] and inspect them through the CLI and API |
| [4. Loading and invocation](04_loading.md) | Constructing [runtimes][glossary-runtime] and making typed calls | Load saved components and call `process` |
| [5. Script slots, loading, and execution](05_scripts.md) | Typed [slots][glossary-slot], assignments, and Python script execution | Run an affine processor and accumulator pipeline |
| [6. Lifecycle management and handover](06_lifecycle.md) | Transitions, state transfer, and resource ownership | Transfer total `7` to a second accumulator and continue at `12` |

```text
rpp_demos/tutorials/
  01_plugin_types_and_plugins/ # Reading guide; no Python driver
  02_registration/            # CLI guide; no Python driver
  03_configuration/run.py
  04_loading/run.py
  05_scripts/run.py
  06_lifecycle/run.py
  example_library/
    package.json
    plugins.json
    plugin_types/
    plugins/
    scripts/scalar_pipeline.py
```

## Prerequisites and execution

Use the [`rpp_dev` development image](../development-image.md)
or follow the [host installation guide](../getting-started.md).
You need Python 3.10 or newer, the installed RPP packages, and the native
registration dependencies. The examples use native Python components; ROS is
not required for their application logic.

For the development image, open a tutorial shell:

```bash
docker run --rm -it \
    --env RPP_CPP_CORE_PATH=/workspaces/rpp/ros2_ws/install/rpp_cpp/lib \
    --workdir /workspaces/rpp/ros2_ws/src/rpp_dev/src/rpp_demos \
    ghcr.io/coe-marble/rpp-dev:lyrical
```

Inside that shell, select a persistent tutorial home before using `rpp`:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
rpp init-home
```

Registration can compile supporting artifacts even for Python implementations.
On a host installation, set `RPP_CPP_CORE_PATH` to the directory containing
`librpp_cpp` and `librpp_cpp_core` before registering types and plugins. The
container command above supplies the isolated colcon library directory.

Read Tutorial 01, then follow Tutorial 02's CLI steps to copy the example library
to `$RPP_HOME/tutorials/example_library` and register it with `--link`. Tutorial
02 also shows how to inspect types, plugins, and generated Python and C++ code.
There are no Python drivers for those two tutorials.

After CLI registration, run the API examples from `rpp_dev/src/rpp_demos`:

```bash
python3 tutorials/03_configuration/run.py
python3 tutorials/04_loading/run.py
python3 tutorials/05_scripts/run.py
python3 tutorials/06_lifecycle/run.py
```

Run each in a fresh Python process because RPP caches [registry][glossary-registry] settings and
generated modules. Keep `RPP_HOME` set in every shell used for the CLI or scripts.
The standalone scripts use public RPP APIs directly; they do not register the
library for you or import a tutorial framework.

The configuration, loading, and [lifecycle][glossary-lifecycle] examples save their [workspaces][glossary-workspace] under
`$RPP_HOME/tutorials/<tutorial>/workspace`. The script example makes the copied
library itself a workspace and saves its script assignments there. Runtime
handles close on exit, including on exceptions. Registered metadata, generated
interfaces, copied sources, and component configurations persist for inspection.

After updating example sources, copy them again using Tutorial 02's instructions
and run `rpp library refresh example_library`. A linked registration reads the
copied source directory; changes elsewhere in the checkout take effect after
you update that copy. The runners reset their example component parameters when
preparing a run.

Each walkthrough provides commented inspection commands. Explore further with
`rpp registry --help`, `rpp library --help`, and `rpp ws component --help`.
The [workspace guide](../workspaces.md)
explains saved components, assignments, and parameter files in more detail.

## Example library

| Type | Implementation | Operation |
| --- | --- | --- |
| `example_library::ScalarProcessor` | `example_library::AffineProcessor` | `gain * value + offset` |
| `example_library::ScalarAccumulator` | `example_library::AccumulatingProcessor` | Accumulate successive scalar inputs |

The defaults for the affine processor are gain `1` and offset `0`. The configured
examples use gain `2` and offset `1`. Tutorial 06 explains the accumulator's
state transfer. Tutorial 05 connects both components using script slots and
produces totals `3`, `8`, and `15` for inputs `1`, `2`, and `3`.

## More examples

The [workspace guide](../workspaces.md#yaml-and-shared-parameter-data) shows how
to load shared YAML data from `params/parameters.py`.
For larger examples, see [localization and communication](../demos.md).

[glossary-plugin]: ../glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: ../glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
[glossary-library]: ../glossary.md#library "Library: a source directory grouping Plugin Types, Plugins, and related files."
[glossary-registry]: ../glossary.md#registry "Registry: metadata describing registered libraries, Plugin Types, and Plugins."
[glossary-workspace]: ../glossary.md#workspace "Workspace: a project directory containing saved component and script configuration in .rppws."
[glossary-runtime]: ../glossary.md#runtime "Runtime: an application-owned execution handle built from saved configuration."
[glossary-slot]: ../glossary.md#slot "Slot: a named, typed location for components in a script or composite plugin."
[glossary-parameter]: ../glossary.md#parameter "Parameter: a named configuration value resolved for a component instance."
[glossary-lifecycle]: ../glossary.md#lifecycle "Lifecycle: managed states and transitions for component configuration, activation, and shutdown."
