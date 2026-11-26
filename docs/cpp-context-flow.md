# C++ context construction and lifecycle

This describes the implementation in the current integration checkout. Native
managed lifecycle is implemented; adapted activation and typed handover remain
unsupported. This documentation update does not establish build/test validation.

## Application entry points

```cpp
rpp::RppDataManager data_manager(rpp_home, workspace_path);
rpp::ComponentRuntimeBuilder builder(data_manager, rpp::ClockOptions{}, true);
auto runtime = builder.build_script_from_path(script_path);

runtime.configure().require_success();
runtime.get_context().activate_subcomponents().require_success();
auto controller = runtime.get_context().get_subcomponent<Controller>("controller");
// The application calls controller-specific methods from its own loop.
runtime.close().require_success();
```

The builder's third argument is `allow_dynamic_components`, defaulting to false.
Alternatively, use `ComponentRuntimeBuilder(data_manager, policy, clock_options,
validators)`, where `policy(slot_name, ComponentSlot)` returns the permission.
These are separate constructors; the builder resolves the selected permission policy.
It is evaluated once for each slot, including declared empty slots. `ComponentSlot`
contains the base [plugin type][glossary-plugin-type] and `SINGLE`, `OPTION`, or `LIST` kind. Descendant
slots use the same policy, including descendants loaded later. Capture values
or keep referenced data alive for those later builds. The decision sets each
locally constructed manager's permission, including managers holding adapted
[components][glossary-component]. Neither permission mode is forwarded to external hosts by the builder.
The application does not create a slot manager. Building a context constructs
objects and prepares transports; configuration and activation are separate calls.

## Responsibilities and construction

| Type | Responsibility |
| --- | --- |
| `ComponentRuntimeBuilder` | Public construction facade. Assemble roots or a script slot collection with retained build settings. |
| `ComponentConstructor<Threading>` | Resolve records and [plugin][glossary-plugin] metadata, prepare external hosts, load instances and parameters, and construct slots. |
| `SlotManager` | Own entries in one single/option/list slot. Enforce admission, lifecycle state, selection, replacement and guarded-call draining. |
| `ComponentRuntime` | Application lifecycle/administration handle. Retain a fixed root slot or directly own a script's slot collection. |
| `ComponentContext` | Non-template view of services and subcomponent slots; no own-slot membership operations. |
| `SubcomponentContext` | Non-template view of one registered subcomponent: activation/deactivation, identity and typed instance access. |

For component roots, the builder submits one batch to `construct_components()`.
The constructor resolves records and prepares non-native hosts together, then creates
each component's data. Native components recursively create slot managers and admit
their assigned subcomponents. An external host owns its subtree; its local proxy has
no local descendant slots.

The builder admits each root to a fixed exclusive slot with exactly one entry and
no dynamic membership permission. Root lifecycle uses the same slot machinery as
nested components. A component already assigned to a slot uses that slot's manager;
there is no additional manager per candidate.

For scripts, the constructor reads the selected configuration, prepares transports,
and constructs the assigned/declared slots. The runtime directly owns that collection
and the services used by its context view. There is no script manager, plugin instance,
component UUID or script lifecycle state machine.

Each slot retains its constructor and shared build settings. Building never calls
configuration or activation callbacks, and the builder may be destroyed after building.
`construct_components()` remains the single component-construction path; later loads
and reloads submit one request and initial assignments reuse their prepared host batch.

## Ownership and slot selection

```text
component root runtime
  └── fixed single SlotManager
      └── component data
          ├── plugin, parameters, logger, clock and context
          └── subcomponent slot managers
              └── component entries, recursively

script runtime
  └── script services and slot collection
      └── SlotManager per assigned/declared slot
          └── component entries, recursively
```

Slots own component data with `unique_ptr`. A script runtime directly owns its
collection data. No manager stores runtime objects: runtime snapshots are handles
created on demand with a slot, registration name and instance UUID. They retain
their slot, but do not prevent explicit unloading or replacement.

`ComponentContext` holds a non-owning reference to its data, with an internal
variant for the two threading policies. The concrete context class is never
templated. Component data identifies its owning slot and registration name;
script collection data has no owning slot. Release detaches the context before
its data can disappear, so retained subcomponent views reject stale access.
Moves transfer handles or unique script storage without rebinding contexts.

A plugin can manage its subcomponents and request deferred self-deactivation.
Its context does not expose loading, unloading, switching or replacement in the
slot containing itself. Those membership decisions belong to the parent/application
that controls that slot.

Single `T` and `Option[T]` use exclusive activation; `List[T]` allows multiple active
entries. Admission does not activate anything. The first admitted exclusive entry
is initially selected. Initial single-slot cardinality is validated separately.

Dynamic permission is fixed per slot during construction and inherited through
retained build settings for later descendants. Disabling it still permits initial
admission and ordinary lifecycle, but rejects membership changes and selection of
another exclusive candidate. Unloading a permitted parent may shut down its whole
subtree even when nested slots forbid direct replacement. External hosts choose
their own local policies.

`runtime.allows_dynamic_components()` reports this handle's owning-slot permission;
fixed roots and scripts return false. The overload taking a slot name reports that
subcomponent slot's permission independently.

## Configuration and activation

Component-root and subcomponent-runtime commands use the same owning-manager path.
`runtime.configure()`, `activate()`, `deactivate()` and `cleanup()` forward to that
manager, which validates state and transitions and executes the callback traversal.
Script runtime commands traverse their slot collection and delegate to its slot managers.
Runtime has no root-state enum, transition flag, plugin callback execution or rollback implementation.

`SlotManager::configure_component()` visits subcomponents through their slot managers before
calling its own instance's `Plugin::configure(context)`, which dispatches
`on_configure(ComponentContext)`. A script root has no own callback. All registered
candidates are configured, including inactive option candidates.

Activation/deactivation are local to the current plugin:

```text
runtime.activate(state)
  → owning SlotManager::activate(entry)
  → SlotManager::activate_component(component, state)
  → Plugin::activate_state(state)
  → plugin.on_activate(optional_state)
  → manager marks ACTIVE on success
```

`on_activate()` runs before the manager opens the active-call gate. For
`deactivate()`, the manager first drains guarded calls, runs `on_deactivate()`, and
marks the entry INACTIVE on success. The plugin chooses whether and when to invoke
`context.activate_subcomponents()` or `context.deactivate_subcomponents()` from those
callbacks. Script roots have no plugin, so applications call the helpers directly;
`activate()`/`deactivate()` on a script do not transition its assignments.

Subcomponent lifecycle helpers live on `ComponentContext`. Applications reach them
through `runtime.get_context()` using the same view supplied to plugins.
These helpers ask each manager to activate selected exclusive candidates
or all loaded list entries, without handover state. Only a failed helper call
rolls back entries that it newly activated; previously active entries are preserved.
If the helper succeeds but the parent callback later fails, subcomponent states remain
under plugin control. Deactivation of contained components visits active entries
in reverse order, continues after failures, and returns the first error without
subcomponent handover snapshots. Each subcomponent's own callbacks independently decide whether
to transition its descendants. Neither helper changes dynamic permissions.

No generic update loop starts. The application retains its timer/update loop.

## Reading and managing components

`get_parameter<T>()` reads the context's resolved parameters.
`get_logger()` and `get_clock()` return shared pointers to const objects. Logging
and reading timestamps remain available; callers cannot mutate the clock through
the context getter.
`get_subcomponent<T>(slot, component_name)` returns the named loaded instance.
Without a name, single and option slots return their selected entry. A `List[T]`
slot always requires a name, even when it has zero or one loaded entries; omission
throws `LifecycleError`. Applications and plugins use this same context accessor. `get_subcomponents<T>(slot)` returns the
loaded instances in that slot, including inactive candidates.

`runtime.get_context()` returns the manager-owned self view. Its
`get_subcomponent_context(slot, component_name)` returns control of one named
subcomponent; `get_subcomponent_contexts(slot)` snapshots shared subcomponent views.
`list_subcomponents()` belongs to this context; application registration/state
snapshots remain available through `runtime.get_subcomponent_statuses(slot)`.

`ComponentStatus::instance_id` is the loaded runtime's UUID, also exposed by
`runtime.get_context().get_instance_id()` and the restricted subcomponent view. Component paths and
slot-local registration names identify configuration/registration; the UUID
identifies a particular loaded copy. Lifecycle transitions and moves preserve it.
Reload creates a new UUID, and successful unload clears the entry's current ID.
Multiple registrations of the same component path have distinct instance IDs;
registration names are still unique within each slot.

`with_active_component()` accepts an optional `expected_instance_id` string view.
The check rejects replacement under the same registration name without copying
the ID into every guarded call. The view is consumed synchronously and not retained.

Subcomponent view lifecycle calls go directly to their manager. Registration name
and instance UUID checks prevent an old retained view from operating on a replacement.

Managers own transition checks, callback execution, shutdown, and subcomponent coordination.
The constructor helper assembles prepared component data and subcomponent-slot managers.
Runtime commands forward to manager operations. The concrete, non-template
`ComponentContext` reads its data and delegates subcomponent operations to the
corresponding slots. `SubcomponentContext` forwards lifecycle calls to the owning
slot recorded in that component's data. Neither facade owns
lifecycle bookkeeping. Both threading policies share these implementations.
Lifecycle and membership changes run on one owning thread in both policies.
Concurrent managers use one short-held slot gate for registry snapshots, admission,
and guarded-call counts. No gate is held during callbacks or component construction; draining
releases it while waiting. There are no thread-ID maps or lifecycle mutation locks.
Single-threaded managers retain ordinary transition and local nesting checks.
Validators cannot reenter membership changes; direct plugin calls remain unrestricted
by slot admission and are governed by the plugin's own state and synchronization.
The explicit activation helper records newly activated subcomponents to limit rollback
to work started by that helper.

For concurrent calls and transitions, use
`with_active_component<T>(slot, entry, callback)`. It borrows the instance for
the callback, tracks the call, and releases it afterward. Ordinary getter
references must not be retained across unloading/replacement.

For runtime loading, the call chain is:

```text
runtime.load_component(slot, entry, component_path)
  → slot manager.load(...)
  → permission and entry-state checks
  → manager delegates to its retained ComponentConstructor
  → helper constructs component data using retained build settings
  → type/admission validation against registered entries
  → commit as UNCONFIGURED
```

Configure and activate the new entry explicitly. Switching is a runtime
operation: it delegates to the slot manager, stops the source, transfers the
optional owned state, and activates/selects the target on success.

Validators receive the prepared candidate runtime handle and existing runtime
snapshots, including inactive candidates. Inspect contexts through `get_context()`. They inspect metadata/parameters and
return `CallbackResult`; they must not perform lifecycle operations. Initial
validators are supplied to the builder, keyed by base slot plugin type and then
the name of the candidate being registered. Initial names come from the workspace
component name; empty names are rejected on registration. Dynamic registrations use
the caller's name. Rules apply throughout the tree wherever the type and candidate
name match. `List[T]` and `Option[T]` both use `T` as the key. Missing rules permit
normal type validation. The runtime setter changes future
admission without evicting or revalidating current entries.

## Shutdown and failures

Root `close()` deactivates its own plugin and explicitly stops remaining active
descendants, including descendants under inactive parents. It then performs
cleanup if configuration was attempted and releases runtime resources. Managed
unload performs the same descendant shutdown before cleanup and release. This
explicit teardown does not depend on plugin callbacks opting into subcomponent lifecycle.
Teardown deactivation and cleanup visit parents before subcomponents and continue through
independent subcomponents and reports failures. A failed lifecycle phase prevents
destruction of the affected instance. Closing an individual borrowed subcomponent is
an unload request to its manager and obeys the dynamic-modification permission.

Explicitly check `close()` results; destructor fallback does not replace
deterministic lifecycle shutdown. Managers retain instances whose shutdown
cannot safely complete rather than treating failure as permission to unload
active code.

## Adapted components

For an adapted node, the constructor helper prepares `ExternalComponentProcess`, loads an
adapter client and starts/connects the hosting process. Runtime construction
attaches that proxy and its process owner without creating local subcomponent slots.
The host constructs the real component tree through its own runtime-builder facade. Configure/cleanup travel through `RpcControlClient` and
`plugin_runtime.capnp` to the real context in that process.
The C++ endpoint is `RpcControlService` in `rpc_control_service.hpp`. This is RPC
control, separate from the owning `ComponentRuntime`. `PluginRuntime` remains the
shared generated wire interface name for compatibility with Python consumers.

Transport preparation during building is not plugin activation. Adapted
activation/deactivation and state handover are still explicitly unsupported in
this increment. Native C++ trees create no RPC executor or external process.

## Source map

- [RppDataManager](https://github.com/coe-marble/rpp_cpp/blob/develop/include/rpp_cpp/data_manager.hpp)
- [ComponentRuntimeBuilder](https://github.com/coe-marble/rpp_cpp/blob/develop/include/rpp_cpp/component_runtime_builder.hpp)
- [ComponentRuntime facade](https://github.com/coe-marble/rpp_cpp/blob/develop/include/rpp_cpp/runtime.hpp), [implementation](https://github.com/coe-marble/rpp_cpp/blob/develop/src/runtime.cpp), and [internal component data](https://github.com/coe-marble/rpp_cpp/blob/develop/include/rpp_cpp/component_data.hpp)
- [ComponentContext interface](https://github.com/coe-marble/rpp_cpp/blob/develop/include/rpp_cpp/context.hpp) and [implementation](https://github.com/coe-marble/rpp_cpp/blob/develop/src/context.cpp)
- [SlotManager interface](https://github.com/coe-marble/rpp_cpp/blob/develop/include/rpp_cpp/slot_manager.hpp) and [lifecycle implementation](https://github.com/coe-marble/rpp_cpp/blob/develop/src/slot_manager.cpp)
- [ComponentConstructor interface](https://github.com/coe-marble/rpp_cpp/blob/develop/include/rpp_cpp/component_constructor.hpp) and [implementation](https://github.com/coe-marble/rpp_cpp/blob/develop/src/component_constructor.cpp)
- [Native plugin loader](https://github.com/coe-marble/rpp_cpp/blob/develop/src/plugin_loader.cpp)

## Threading and plugin-facing API

The construction path selects one threading policy for the locally owned tree,
including later loads. External hosts select their own local policy.
`ComponentContext` remains a concrete, non-template borrowed view.

The [C++ runtime guide](cpp-runtime.md#selecting-a-threading-mode) owns threading
selection, guarded-call admission, and direct-call limitations. Its
[subcomponent-control section](cpp-runtime.md#subcomponent-control-and-self-deactivation)
owns `SubcomponentContext`, deferred self-deactivation, and application safe points.

[glossary-plugin-type]: glossary.md#plugin-type "Plugin Type: a language-neutral contract implemented by plugins."
[glossary-plugin]: glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
