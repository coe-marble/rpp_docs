# Components, workspaces, and script configurations

`rpp-orchestrator` provides workspace and GUI management. It depends on `rpp-py`
for component-slot metadata and parsing shared with the runtime.

The orchestrator stores one script description per script in
`.rppws/script_descriptions/<script-name>.json`.

See [core workflows](workflows.md) for creation and registration,
[CLI](cli.md#script-configurations) for configuration commands, and
[managed runtimes](runtime-lifecycle.md) for execution.

## Components are self-contained, reusable folders

A plugin is an implementation registered in an RPP library. A **component** is
one saved configuration of that plugin: its description, parameters, local data,
and concrete subcomponents live together in a directory. A workspace collects
these component folders and assigns them to scripts through named configurations.
A running component instance is constructed later from the saved folder.

The component folder is the unit of reuse. **You can copy and paste the whole
folder, then register/load that component in another workspace or runtime.** You
do not have to recreate its parameters and nested composition in the GUI.
Keep paths to bundled files relative to the component or its parameter script,
so the copy can move without depending on the original directory.

The destination still needs the plugin implementation and its dependencies
registered in its RPP home. The component folder carries its configuration and
resources; the implementation is resolved by its qualified `PluginName`.

## Workspace and `.rppws` folder layout

A workspace is an ordinary project directory containing `.rppws`. Scripts can
live in the project directory; `.rppws` stores their descriptions, configurations,
and saved components. A typical layout is:

```text
my_workspace/
├── run_processor.py                     # Application/script source
└── .rppws/
    ├── script_descriptions/
    │   └── run_processor.json           # Script metadata and configurations
    ├── parts/
    │   └── <plugin-id>/                 # Implementation grouping
    │       └── <component-id>/          # One complete component folder
    │           ├── description.json
    │           ├── callbacks.py
    │           ├── params/
    │           │   ├── parameters.py
    │           │   └── common.yaml     # Optional, user-provided parameter data
    │           ├── data/               # Component-local files
    │           └── subcomponents/
    │               └── <child-id>/     # Same component layout, recursively
    │                   ├── description.json
    │                   ├── callbacks.py
    │                   ├── params/
    │                   │   └── parameters.py
    │                   ├── data/
    │                   └── subcomponents/
    ├── data/                           # Workspace-level data
    ├── builds/                         # Workspace build output location
    └── logs/                           # Workspace log location
```

`Workspace.ensure_layout()` creates `script_descriptions`, `parts`, `data`,
`builds`, and `logs` under `.rppws`. Creating a component creates its standard
files and directories. `common.yaml` in this example is optional and is loaded
explicitly by the parameter script; it is not an RPP-required file.

| Item | What it owns |
| --- | --- |
| `script_descriptions/<script-name>.json` | Script source reference, slot specification, named configurations, and active configuration |
| `parts/<plugin-id>/<component-id>/` | A saved root component and its complete concrete subtree |
| `description.json` | Saved component ID/name, plugin identity/type, child slot specification and assignments, and parent metadata when nested |
| `params/parameters.py` | Executable parameter definition exposing `ComponentParameters` |
| `data/` inside a component | Files that should travel with that component |
| `subcomponents/<child-id>/` | Owned child component folders, with their own parameters/data/children |
| `callbacks.py` | Component callback file created by the storage layout; plugin lifecycle hooks remain implemented by the plugin |

`<plugin-id>` is the storage identifier derived from the qualified plugin name;
use the folder created by RPP rather than substituting the display name.
`<component-id>` is the saved configuration's UUID. Script assignments refer to
that ID together with `PluginName`. A loaded runtime has a separate
[instance UUID](runtime-lifecycle.md#access-identity-and-guarded-calls).

`.rppws` contains the saved configuration of the application. Preserve its
component folders and script descriptions when sharing or versioning a workspace;
they are not disposable caches. The RPP home (`~/.rpp` by default) separately
owns registered libraries and generated interfaces.

## Copy, discover, and register a component

Copy the entire root component directory, including `params`, `data`, and
`subcomponents`. For workspace discovery, place it under the destination's
`.rppws/parts/<plugin-id>/<component-id>/` with its description and IDs intact.
Opening a new `Workspace` scans component descriptions under `parts` and indexes
the saved records. Reopen the workspace after pasting folders into an already
open project, then assign the discovered component to a script/configuration.

For example, after copying a folder into an existing destination workspace:

```python
from pathlib import Path
from rpp_orchestrator.workspace import Workspace

workspace = Workspace(Path("/path/to/destination_workspace"))
component = workspace.get_component("copied-component-id")
# The component is now available for workspace/script assignments.
```

There is no separate `rpp ws component register` CLI command in the current
implementation: opening the workspace performs saved-record discovery.
Registration into a running slot uses the public runtime API. Given a runtime
with a declared `processors` slot and dynamic modification enabled:

```python
runtime.load_component("processors", "primary", "/path/to/copied-component-folder").require_success()
runtime.configure_component("processors", "primary").require_success()
runtime.activate_component("processors", "primary").require_success()
```

The folder can be loaded by its path without first moving it into that runtime's
workspace. The registration name `primary` is local to the slot; it is distinct
from the folder's saved component ID. Loading does not configure or activate it.
See [dynamic slots](runtime-lifecycle.md#slots-and-dynamic-modification).

When creating a second independent copy inside the same workspace, use
`rpp ws component duplicate WORKSPACE COMPONENT [NEW_NAME]` or
`Workspace.duplicate_component()`. Duplication copies the tree and assigns new
component IDs while updating its internal references. A raw copy preserves IDs;
use it for transfer to another workspace without an existing copy of those IDs.

Concrete subcomponents travel with their parent. A linked subcomponent instead
refers to another saved component; copy/register that referenced component too,
or compose the portable unit with concrete children. Cross-workspace linked
component resolution is not currently supported. Bundle shared files inside
the copied tree when they should travel with it.

## Parameters are Python definitions

Parameters are specified in `params/parameters.py` using class attributes:

```python
class ComponentParameters:
    gain = 2.0
    offset = 1.0
```

The plugin declares parameter names and defaults using `ParameterDescription`
and `ParamSet`. Component attributes supply the saved values for that instance;
omitted declared parameters fall back to plugin defaults. Builder overrides take
precedence over these values for matching native components.

RPP imports and evaluates the parameter module and reads `ComponentParameters`.
This also applies to C++ plugins: the C++ parameter loader uses Python through
pybind11. The plugin subsequently reads resolved values from its context.
The Python runtime's loader and the workspace editor both evaluate the module;
parameter code may therefore run again when inspecting or rebuilding a component.

Python is deliberate: parameter definitions can compute values, call custom
helper scripts/functions, select a configuration, or load another format when
needed. The exported attributes are the evaluated parameter values, not callback
functions that the runtime invokes on every plugin call. Keep setup repeatable
and resolve bundled resources from `__file__` rather than the shell's working
directory. Changing a parameter file does not change an existing runtime's
snapshot; rebuild/reload the instance to read it again.

For example, a computed parameter needs no separate configuration format:

```python
from math import pi

class ComponentParameters:
    gain = 2.0 * pi
    offset = 1.0 / 10.0
```

## YAML and shared parameter data

If YAML is convenient, load it from the Python parameter definition. RPP does
not automatically interpret a sibling YAML file as component parameters.
For a portable component, keep the data beside the script:

```text
params/
├── parameters.py
└── common.yaml
```

For example, `common.yaml` can hold reusable base values:

```yaml
gain: 2.0
offset: 1.0
```

With PyYAML installed in the Python environment used by RPP, `parameters.py`
can load and adapt those values:

```python
from pathlib import Path
import yaml

with Path(__file__).with_name("common.yaml").open(encoding="utf-8") as stream:
    _common = yaml.safe_load(stream) or {}

class ComponentParameters:
    gain = float(_common["gain"])
    offset = float(_common.get("offset", 0.0))
```

The YAML is reusable data; Python controls how it is loaded, evaluated, combined
with other inputs, and exposed as declared parameters. The complete `params`
directory travels with the copied component. Sharing one file outside that folder
is also an application choice, but that external file then becomes a dependency
of the copy. A parent component can instead bundle shared data within its own
portable subtree and let child parameter scripts locate it relative to their
files.

Workspace/GUI parameter saves and `rpp ws component parameter set` serialize
resolved values into a generated `ComponentParameters` class, replacing
`parameters.py`. They do not preserve a hand-written YAML loader or helper logic.
Edit the script directly to retain executable definitions; save evaluated values
through the parameter store when you deliberately want to materialize them.
The YAML file is not rewritten by this save operation.

A later tutorial will demonstrate loading shared YAML, evaluating custom
parameter logic, and storing the resulting values. The six existing tutorials
remain the current learning path; see
[configuration and composition](tutorials/04_configuration.md).

## Script configurations

Every script description must use the configuration-based format:

```json
{
    "ScriptPath": "/path/to/script.py",
    "Language": "python",
    "Configurations": {
        "Default": {
            "Components": {
                "controller": [
                    {
                        "Id": "component-id",
                        "PluginName": "library::Plugin"
                    }
                ]
            }
        }
    },
    "ActiveConfiguration": "Default",
    "Linked": false,
    "ScriptName": "controller",
    "ScriptLibrary": "workspace_library",
    "Spec": {
        "controller": "plugin_type::Controller"
    }
}
```

`ActiveConfiguration` must name an entry in `Configurations`. Each configuration
owns an independent `Components` mapping. Descriptions using the old top-level
`Components` field are not supported.

The workspace API supports creating, duplicating, renaming, deleting, and
activating configurations. A script must always retain at least one
configuration.

## GUI behavior

The left-side script tree contains configuration children. Selecting a
configuration displays and edits its assignments under **Configuration
Components**. Double-clicking a configuration activates it; the active
configuration is highlighted in green.

The contextual action group shows script actions when no configuration is
selected and configuration actions when a configuration is selected.
