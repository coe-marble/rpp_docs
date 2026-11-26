# Robotics Plugin Platform (RPP)

> Unofficially, RPP stands for **Robotics Plus Plus**. Following the proud
> industry tradition of adding a plus sign and calling it the next generation.

RPP lets an application choose implementations and their settings without
putting those choices into the application's control logic. You define the
operations a plugin must provide, implement them in Python or C++, and save the
implementation and parameters you want to use.

For example, a control application can use a reference generator without knowing
which interpolation algorithm it uses. A localization application can call an
estimator while its configuration selects EKF or UKF.

## A small example

The tutorials start with a [plugin type](docs/glossary.md#plugin-type) named
`ScalarProcessor`. Its contract declares one operation:
`process(value) -> result`.

`AffineProcessor` is a [plugin](docs/glossary.md#plugin) implementing that
operation as `gain * value + offset`. Gain and offset are parameters, so you
can create two saved [components](docs/glossary.md#component) from the same
plugin:

| Component | Parameters | Result of process(3) |
| --- | --- | --- |
| `processor_a` | gain = 2, offset = 1 | 7 |
| `processor_b` | gain = 4, offset = 0 | 12 |

Both use the same implementation. Each has its own settings and, when loaded,
its own instance. The application calls `process()` through the shared contract.

## From a source file to a running component

Registration makes a library's plugin types and implementations available to
RPP. It generates the language interfaces and adapters and compiles the native
artifacts needed to load them. Registration is usually done when installing
a library or changing its code.

A workspace saves your choices: which plugin a component uses, its parameters,
and which child components fill its slots. A cascade controller, for example,
can have a pose controller in one slot and a velocity controller in another.

The application builds a runtime from that saved configuration. Building loads
instances. Configuration reads parameters and prepares resources. Activation
starts the component's work. The application then calls its methods from its
own loop and closes the runtime when finished.

These are separate operations. Editing a saved parameter affects the next
construction; refreshing a library updates registered artifacts; reloading a
running component replaces its instance.

## Python and C++

When caller and plugin use the same language, the runtime loads the plugin
in the same process. Across a language boundary, RPP starts a component-server
process and uses generated Cap'n Proto RPC adapters. The application still
calls the plugin's declared methods. The host runs lifecycle callbacks and
owns that component's children.

RPP also provides ROS 2 services for managing loaded slots. The application
still decides when it is safe to reconfigure or switch its components.

## Robotics components

The shared robotics interfaces describe what numeric values mean and how they
are ordered. A controller declares the state and references it reads and the
control values it produces. The application connects compatible fields and
prepares the numeric routes before execution.

In a pose/velocity cascade, the reference generator supplies a desired pose.
The pose controller produces desired velocity, the velocity controller produces
force and moment, and an allocator converts those into actuator commands.
Mission monitors decide whether the mission can continue and whether its goal
has been reached.

Estimation runs alongside this chain. It combines sensor measurements with a
model to produce a filtered state and covariance, which can then supply the
controller's measured state.

The [control guide](docs/interfaces/control/control-stack-and-message-map.md)
follows that loop in detail. The
[estimation guide](docs/interfaces/estimation/generic-estimation-and-localization.md)
explains prediction, correction, and replay.

## Getting started

Use the [installation guide](docs/getting-started.md) to prepare an environment,
then follow the [six tutorials](docs/tutorials/README.md) to run the scalar
example. The [architecture guide](docs/architecture.md) explains how the saved
files, registry, and runtime fit together.

For command syntax, use the [CLI reference](docs/cli.md).
