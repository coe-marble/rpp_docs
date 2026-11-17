# RPP glossary

RPP uses these terms consistently across its CLI, APIs, and documentation.
Start with the distinction between a Plugin Type, a Plugin, and a Component:

| Term | What it identifies | Example |
| --- | --- | --- |
| [Plugin Type](#plugin-type) | A contract defining supported operations | `example_library::ScalarProcessor` |
| [Plugin](#plugin) | A concrete implementation of a contract | `example_library::AffineProcessor` |
| [Component](#component) | A saved configuration selecting a plugin | A saved `processor` with gain `2` and offset `1` |
| [Runtime](#runtime) | A loaded execution handle built from saved configuration | A `ComponentRuntime` configured and activated by the application |

## Plugin Type

A language-neutral contract that declares the operations an implementation must
provide, including their input and output types. RPP defines plugin types using
annotated Cap'n Proto interfaces and generates language-specific interfaces from
them. One plugin type can have multiple implementations.

For example, `example_library::ScalarProcessor` declares `process(value)`.
See [plugin types and implementations](plugins-and-plugin-types.md).

## Plugin

A concrete implementation of a Plugin Type, written in a supported language.
A plugin defines behavior and may declare parameters and child component slots.
Registering it records its identity, source, and implemented contract.

For example, `example_library::AffineProcessor` implements `ScalarProcessor`
using `gain * value + offset`. See [CLI registration](tutorials/02_registration.md).

## Component

A self-contained saved configuration that selects a Plugin and supplies its
parameters, resources, and any concrete subcomponent assignments. It has a
persistent identity and a folder that can be copied and reused. Multiple
components can select the same plugin with different settings.

A Component is distinct from its loaded runtime instance. Loading its saved
configuration constructs a Runtime. See [components and workspace layout](workspaces.md).

## Library

A source directory grouping Plugin Types, Plugins, and related files.
`package.json` identifies the library; `plugins.json` declares sources for
registration. A linked registration points to its source directory. A library
can also be a workspace publishing scripts.

See [library registration](registry.md#home-and-source-ownership).

## Registry

The registered metadata that describes available libraries, Plugin Types, and
Plugins in the selected RPP Home. Registration validates sources and generates
the interfaces and other artifacts used to load and call implementations.

See [registry ownership](registry.md).

## RPP Home

The directory selected by `RPP_HOME` or the CLI's `--rpp-home` option, defaulting
to `~/.rpp`. It contains registry metadata, registered library references or
copies, configuration, and generated interfaces. Tutorials use
`~/.rpp_tutorials`.

See [RPP home and source ownership](registry.md#home-and-source-ownership).

## Workspace

A project directory containing `.rppws`, which stores component configurations,
script descriptions, and script assignments. The workspace owns saved
application composition. Its registry and generated interfaces are resolved
through the selected RPP Home.

See [workspace layout](workspaces.md#workspace-and-rppws-folder-layout).

## Runtime

An application-owned execution handle built from saved component or script
configuration. A `ComponentRuntime` owns a root component; a `ScriptRuntime`
owns a script's component slots and services. Runtime construction, configuration,
activation, and shutdown are explicit API operations.

See [managed runtimes](runtime-lifecycle.md).

## Script

Application logic declaring named component slots. A saved script description
records the slot contracts and named configurations assigning components to
them. Building a script runtime constructs the selected components. Executing
the script body is a separate application step.

See [script slots, loading, and execution](tutorials/06_scripts.md).

## Slot

A named, typed location for components in a script or composite plugin.
Its declaration identifies the required Plugin Type and whether it accepts
a single component, options, or a list. Slot managers administer membership and
component transitions according to that declaration.

See [slots and dynamic modification](runtime-lifecycle.md#slots-and-dynamic-modification).

## Parameter

A named configuration value declared by a plugin and resolved for a component
instance. Resolution combines plugin defaults, saved component settings, and
applicable builder overrides. A constructed runtime holds its resolved snapshot.

See [component parameters](workspaces.md#parameters-are-python-definitions).

## Lifecycle

The managed states and transitions controlling component configuration,
activation, deactivation, cleanup, and shutdown. The runtime administers these
transitions; plugin callbacks implement the corresponding behavior.

See [states, callbacks, and ownership](runtime-lifecycle.md#states-callbacks-and-ownership).

## Handover State

An owned application value exported during deactivation and optionally supplied
to another activation. A Plugin Type can declare its schema explicitly.
Handover State transfers application data, such as an accumulated total; it is
separate from a component's managed lifecycle state or saved configuration.

See [typed handover](runtime-lifecycle.md#typed-handover).
