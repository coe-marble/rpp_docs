# How RPP loads and runs components

RPP keeps plugin source, saved application configuration, and running instances
separate. To see why, consider a saved scalar processor configured with gain 2
and offset 1.

Its source code belongs to a library. Registration tells RPP where to find that
library and prepares the generated interfaces and native binaries. A workspace
then saves a component selecting that plugin and those two parameter values.
The application loads the saved component to create a running instance.

## What is stored where?

The library contains source files and `plugins.json`. That file lists the
Cap'n Proto files declaring plugin types and the Python/C++ files implementing
them. Linking a library keeps its source in your checkout.

The RPP home, selected by `RPP_HOME`, stores registrations, generated
interfaces, and compiled registered artifacts. The default is `~/.rpp`.
It tells the runtime which code implements a registered plugin name.

The workspace's `.rppws` directory stores saved components and script
configurations. A component folder contains its identity, parameters, and child
assignments. For example, its `params/parameters.py` can contain:

```python
class ComponentParameters:
    gain = 2.0
    offset = 1.0
```

A second component can select the same plugin with different values. Changing
one component's file does not change the other component or the plugin source.
The running instance reads resolved parameters during configuration.

## Loading the saved component

The application gives a component folder to a runtime builder. The builder
resolves the plugin name, loads its parameter definitions, constructs the
instance, and constructs its assigned children.

For a native Python component:

```python
from rpp_py.context_builder import ComponentRuntimeBuilder

# Path to a saved AffineProcessor component with gain 2 and offset 1.
component_path = "/path/to/saved/processor"
runtime = ComponentRuntimeBuilder().build_component_from_path(component_path)

try:
    runtime.configure().require_success()
    runtime.activate().require_success()

    processor = runtime.get_instance()
    result = processor.process(3.0)  # 2 * 3 + 1 = 7
finally:
    runtime.close().require_success()
```

The runtime is the application's handle for lifecycle and administration.
The plugin receives a `ComponentContext` during configuration. It uses that
context to read parameters, access logging and time, and work with its children.

## Why construction, configuration, and activation are separate

Construction creates the objects and any required transports. Configuration
validates parameters and prepares resources. For the scalar processor, that
means reading and storing gain and offset. For a controller, it also means
preparing layouts, routes, buffers, and algorithm history.

Activation lets the component begin its work. The application chooses when
to activate, so it can first finish preparing the rest of the system.
Deactivation stops the component's work while keeping it configured. Cleanup
releases configuration resources. Closing the runtime stops and releases its
owned tree.

The scalar processor rejects `process()` while inactive. Other plugins define
their own direct-call behavior. When calls can overlap lifecycle changes, use
a guarded call so the manager can stop admitting work and wait for current
calls before deactivation.

## Child slots and scripts

A plugin can declare typed child slots. A cascade controller can have one slot
for an outer controller and another for an inner controller. The saved component
chooses which implementations fill those slots.

Each slot has a manager that tracks its loaded entries and lifecycle states.
A single or optional slot selects at most one active entry; a list slot can
have several. The parent plugin decides when to activate or deactivate its
children during ordinary lifecycle callbacks.

A script coordinates slots without being a plugin itself. In the scalar
pipeline tutorial, the script calls a processor and passes its result to an
accumulator. The application configures the script's collection and activates
its children before running that loop.

## Calls across a language boundary

For a C++ plugin used by a Python application, the builder starts a C++
component-server process and gives the application a generated adapter.
That process owns the real plugin and its descendants.

Method calls and lifecycle requests travel to the host. A handover value sent
with activation is encoded using the plugin type's declared state schema.
The host decodes it and passes it to activation. Closing the owning runtime
also releases its hosts and transports.

The [connection guide](component_connection.md) explains result lifetimes and
nested calls. The [runtime guide](runtime-lifecycle.md) gives the lifecycle and
slot APIs.

## What happens when you change something?

Changing a plugin source file requires refreshing its registered library.
Changing a native header can also require rebuilding applications that include
it. A running process can keep its old loaded library until it restarts or
replaces the instance.

Changing a saved parameter affects instances constructed from that file.
Replacing a loaded instance is a runtime operation. It uses the already
registered artifacts and does not compile source.

These distinctions explain why `colcon build`, `rpp library refresh`, and a
slot reload are separate steps. The [registry guide](registry.md#refresh-rebuild-and-reload)
shows which files each operation updates.
