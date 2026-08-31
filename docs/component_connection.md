# Component connections

RPP presents native and foreign-language subcomponents through the same
component API. A component method is synchronous from plugin code:

```python
result = component.validate(state)
```

The adapter hides RPC transport and language boundaries.

## Calling components

Use the same component object whether its implementation is native or runs in
another language. The context builder and generated adapter select the required
connection automatically.

### Synchronous calls

Use the regular method when the caller should wait for the result:

```python
controller = context.get_component("ctl_main")
is_valid = controller.validate(state)
```

The C++ component API is also synchronous by default:

```cpp
auto controller = context.get_component<MotionController2D>("ctl_main");
const bool is_valid = controller->validate(state);
```

These calls work for native and foreign-language components. The adapter sends
an RPC only when the component lives in another process.

### Asynchronous calls

Generated Python adapter clients provide an `_async` variant of each component
method. Await it from an asyncio coroutine when other work can continue while
the component responds:

```python
controller = context.get_component("ctl_main")
is_valid = await controller.validate_async(state)
```

Independent calls can run concurrently:

```python
results = await asyncio.gather(
    controller_a.validate_async(state),
    controller_b.validate_async(state),
)
```

For C++, schedule the plugin call on a `ComponentCallExecutor`. The executor
runs the lambda on its dedicated KJ event-loop thread:

```cpp
rpp::ComponentCallExecutor executor;
executor.start();

const bool is_valid = executor.call([&](kj::AsyncIoContext&) {
    return controller->validate(state);
});

executor.stop();
```

`call()` schedules the work asynchronously on the executor thread and waits
for the lambda result before returning it to the caller. This lets the server
event loop remain available to receive RPC responses.

## Important components

| Component | Responsibility |
| --- | --- |
| `ComponentContextBuilder` | Builds native components locally and groups foreign-language components into external runtime processes. It stops traversing a subtree at the first foreign-language component; that server then builds the remainder of the subtree. |
| `ExternalComponentProcessRegistry` | Maps a source language to the server factory/command that can host it. The default registrations are Python and C++. |
| `ExternalComponentProcess` | Owns one external server process, its runtime connection, adapter clients, and its dedicated call executor. Multiple components of the same foreign language can share one process where supported. |
| `CppExternalComponentProcess` | Python's C++-specific external-process implementation. It resolves `rpp_component_server_cpp` directly, then uses `RPP_CPP_CORE_PATH` when ROS 2 compilation is enabled. |
| `rpp_component_server_python` / `rpp_component_server_cpp` | Build the component roots passed on their command line, expose their adapters through a `PluginRuntime` endpoint, and own all descendants of those roots. |
| `RppRuntimeClientContext` | Owns the transport connection to a server's `PluginRuntime` endpoint. It resolves an adapter capability by connection name; it does not own the component tree or child process. |
| Generated adapter clients and servers | Translate typed component calls to and from Cap'n Proto RPC. Client adapters are injected into the parent context; server adapters expose native instances from the external process. |
| `ComponentCallExecutor` | Runs transport work on a dedicated event loop, allowing component methods to remain synchronous without blocking a server callback's event loop. |

## Building scripts

Both language builders expose the same script entry points:

```cpp
context_builder.build_script_from_path(script_path);
context_builder.build_script_from_library(library_name, script_name);
```

Both accept an optional configuration. `build_script_from_path` finds the
nearest `.rppws/script_descriptions/<script-stem>.json`; the library form
searches the configured workspace's `script_descriptions` directory by its
`ScriptLibrary` and `ScriptName` metadata.

## Language boundary

A context builder traverses components implemented in its own language. At the
first component implemented in another language, it creates an adapter root and
does not traverse its descendants. The external component server owns and
builds that complete subtree.

## Advanced: client-server ownership model

The ownership boundary is the external process, not the adapter and not the
runtime connection. A parent context owns an adapted child context; that child
context owns the adapter instance and a shared `ExternalComponentProcess`.
The process owns the server process and the transport resources used to reach
it.

```text
Parent ComponentContext
├── native component instance
└── adapted child ComponentContext
    ├── generated adapter client / plugin instance
    └── ExternalComponentProcess
        ├── component-server child process
        ├── RppRuntimeClientContext
        ├── PluginRuntime client
        ├── adapter-client connections
        └── ComponentCallExecutor + transport event loop
```

The external component server owns the other side of that boundary:

```text
component-server process
├── ComponentContextBuilder
├── complete component subtree rooted at its command-line components
├── native component instances and their subcontexts
├── generated adapter servers
└── RppServerHost / PluginRuntime endpoint
```

This model composes recursively. For example, a Python component can own a C++
child server, and that C++ server can own a Python child server. Each process
only owns its direct foreign-language server; each launched server owns the
rest of its own subtree.

### Construction and calls

For each foreign-language component process:

1. The host-language process starts the target-language component server.
2. A client connection is created to that server's PluginRuntime endpoint.
3. Adapter clients resolve their component capability by connection name.
4. Calls to the adapter are sent over that connection.

`RppRuntimeClientContext` owns a client runtime connection and its start/stop
lifecycle.
It is not responsible for component-tree construction or process ownership.

### Synchronous component calls

RPC transports require an event loop, but a component method may be called from
within a server callback. Blocking that server's event loop while waiting for a
child RPC response would deadlock or cause a re-entrant event-loop error.

Each external component process therefore owns a dedicated call executor with a
separate transport event loop:

```text
component method (caller thread)
    -> call executor (transport loop thread)
        -> adapter client RPC
            -> external component server
```

The caller blocks on the executor result while the transport loop remains free
to receive the response. This preserves one synchronous public component API
for native and adapted components.

### Asynchronous component calls

Generated Python adapter clients also expose an asynchronous variant of every
component method. The method name has an `_async` suffix and can be awaited
from an asyncio coroutine:

```python
async def validate_children(context, state):
    controller = context.get_component("ctl_main")
    is_valid = await controller.validate_async(state)
    return is_valid
```

For several independent foreign-language components, start the calls together
and await them as a group:

```python
results = await asyncio.gather(
    controller_a.validate_async(state),
    controller_b.validate_async(state),
)
```

The synchronous method, such as `controller.validate(state)`, blocks the
calling thread until the response arrives. The `_async` form submits the same
transport operation to the component call executor and returns an awaitable,
leaving the caller's asyncio loop free to perform other work. Both forms use
the same connection and return the same declared result value.

Use the synchronous form for ordinary plugin methods that expose a synchronous
API. Use `_async` inside application-level asyncio code or when multiple
independent component requests can proceed concurrently. Do not call the
synchronous form from the component call executor's own worker thread.

### C++ scheduled component calls

`ComponentCallExecutor::call()` schedules the supplied lambda on its dedicated
KJ event-loop thread. It then waits for the lambda result on the caller thread.
Use it when a plugin function must run away from the current server event loop;
the server event loop remains able to process RPC traffic while the scheduled
call executes.

For native components, or adapters without an external executor, the generated
method performs the same request directly on its available KJ context.

### Python ownership

`ExternalComponentProcess` owns:

- the external subprocess;
- `RppRuntimeClientContext`;
- `ComponentCallExecutor`.

It starts the client context and connects adapter clients on the executor loop.
Generated Python adapter clients receive that executor internally. Their public
methods synchronously return declared result values; generated `*_async`
methods are transport-level implementations.

`CppExternalComponentProcess` specializes only how the C++ server command is
located. Once started, it has the same ownership and lifecycle contract as any
other Python external process.

### C++ ownership

`ExternalComponentProcess` owns:

- the external subprocess;
- `RppRuntimeClientContext` and adapter clients used on that worker thread.
- `ComponentCallExecutor` with a dedicated KJ event-loop thread;

Generated C++ adapter methods execute request/send/wait operations through the
executor. They must not wait on `RppServerHost`'s server event loop.

### Shutdown order

Stopping a component context first releases the adapter instances that hold RPC
capabilities. The external runtime then requests remote `PluginRuntime`
shutdown, disconnects its adapter clients, releases the client context, and
stops its transport executor. It waits briefly for the server to exit cleanly
before terminating it if necessary.

This order is important for both implementations: all adapters and Cap'n Proto
capabilities must be released before the corresponding event loop is destroyed.
It also gives a nested Python or C++ server time to run its own shutdown path
and stop its descendants, preventing orphaned server processes.
