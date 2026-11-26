# Tutorial 1 Plugin types and implementations

## Prerequisites

Read the [shared prerequisites](https://github.com/coe-marble/rpp_docs/blob/develop/docs/tutorials/README.md#prerequisites-and-execution) for the repository layout and environment requirements.
Have the `rpp_common` and `rpp_demos` sources available in your integration
checkout. This tutorial is a source walkthrough; there is no Python driver or
registration step. Tutorial 02 introduces the CLI commands.

## Description

A [plugin type][glossary-plugin-type] defines the operations an implementation must provide. A [plugin][glossary-plugin]
implements those operations. A [library][glossary-library] groups their source files and declares
which ones RPP should register.

Start with the shared contracts in `rpp_common`, then read the example library's
contracts and Python implementations. Follow the declared method signatures
from a schema to an implementation without loading or executing a [component][glossary-component].

## Implementation

### Part 1: Read plugin types

Open [`rpp_common/msgs.capnp`](https://github.com/coe-marble/rpp_common/blob/develop/rpp_common/common_plugin_types/rpp_common/msgs.capnp).
It defines shared data such as `Point3D`, `Pose3D`, and `Wrench3D`. These structs
can be used as method inputs and results without defining a plugin type.

The accompanying [`rpp_common/anot.capnp`](https://github.com/coe-marble/rpp_common/blob/develop/rpp_common/common_plugin_types/rpp_common/anot.capnp)
defines the `plugin` annotation. A schema uses `$Anot.plugin(...)` to mark an
interface for registration. Each plugin [library][glossary-library] defines its
own contracts independently of the algorithms that implement them.

Now open the example library's
[`scalar_processor.capnp`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugin_types/scalar_processor.capnp):

```capnp
interface ScalarProcessor $Anot.plugin("ScalarProcessor") {
  process @0 (value :Float64) -> (result :Float64);
}
```

`process` takes one scalar and returns one scalar. `@0` is the method ordinal.
Keep published file IDs and ordinals stable. `ScalarProcessor` is the contract's
name; registration gives it the qualified identity
`example_library::ScalarProcessor`.

Read the `PluginTypes` entries in
[`plugins.json`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugins.json).
Each entry points to a schema file relative to the library root. The example
library declares these types:

| Type | Source |
| --- | --- |
| `ScalarProcessor` | [`scalar_processor.capnp`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugin_types/scalar_processor.capnp) |
| `ScalarAccumulator` | [`scalar_accumulator.capnp`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugin_types/scalar_accumulator.capnp) |

### Part 2: Read plugin implementations

Open [`affine_processor.py`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugins/affine_processor.py).
`AffineProcessor` inherits the generated `ScalarProcessor` interface and
implements `process(value)` as `gain * value + offset`. Its `PARAMETERS` declares
the defaults gain `1` and offset `0`; these settings belong to a [component][glossary-component]
instance rather than the method's input signature.

Find the corresponding `Plugins` entry in `plugins.json`. It supplies the source
path, the implementation name `AffineProcessor`, and its contract
`example_library::ScalarProcessor`. The [library][glossary-library] name comes from
[`package.json`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/package.json).

Then read [`accumulating_processor.py`](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/example_library/plugins/accumulating_processor.py).
`AccumulatingProcessor` inherits `ScalarAccumulator`. Its `process(value)` adds
the input to a running total and returns that total. Both implementations reject
non-finite inputs and results.

| Implementation | Implemented type | Main operation |
| --- | --- | --- |
| `AffineProcessor` | `ScalarProcessor` | `gain * value + offset` |
| `AccumulatingProcessor` | `ScalarAccumulator` | Add `value` to the running total |

Other method names present in these implementations are `on_configure`,
`on_activate`, `on_deactivate`, and `on_cleanup`. Their behavior is covered later.

Continue to [Tutorial 02: CLI registration and inspection](https://github.com/coe-marble/rpp_docs/blob/develop/docs/tutorials/02_registration.md)
to register the library and inspect the generated Python and C++ interfaces.

[glossary-plugin-type]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#plugin-type "Plugin Type: a language-neutral contract implemented by plugins."
[glossary-plugin]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
[glossary-library]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#library "Library: a source directory grouping Plugin Types, Plugins, and related files."
