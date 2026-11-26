# Interface method reference

Experimental native API contract, 2026-11-21. This document covers every method
in the shared reference, control, model, estimation and hardware interfaces.
RPP owns lifecycle and component resolution; `bind()` is preparation, not a
replacement lifecycle system. Implementations and the native buffer/layout
builder remain to be implemented.

## Reading the signatures

All methods ending in `Desc` return descriptions and run during binding. `bind()`
also runs inactive, after RPP parameters and typed slots are configured. It checks
compatibility, calculates layouts, prepares numeric functions, and reserves all
storage before activation. Reconfiguration invalidates affected bindings.

StateDesc contains ordered field declarations, not offsets or total dimensions.
The shared builder derives stored width `n`, tangent width `nt`, and each field's
ranges from kind and size. See [layout and frame rules](shared-bind-and-runtime.md#state-fields-and-dimensions).
Each target, reference and observation description is compiled the same way.

| Symbol | Meaning |
| --- | --- |
| n / nt | Stored / tangent width of the bound state. |
| nu / na / nm | Controller/model inputs / actuator commands / hardware measurements. |
| H | ControlLaw.horizonDesc().offsetsNs length. |
| nr[i] | Stored width of reference port i, for one horizon row. |
| nz[p] / ne[p] | Stored / tangent width of observation port p. |
| M | Fixed number of rows returned by ControlConstraint.bind(). |

Numeric matrices are flat row-major buffers. The `$realtime` methods are planned
native calls with borrowed inputs and caller-owned outputs; the current generator
does not yet enforce that policy. No descriptor parsing, allocation or Capn Proto
serialization belongs in an active update. Inputs and writable outputs cannot
alias. Each plugin has prepared scratch for its declared execution concurrency.

All timestamps, durations and relative offsets use unsigned 64-bit nanoseconds:
Cap'n Proto `UInt64`, C++ `std::uint64_t`, and Python integers in `[0, 2^64 - 1]`.
Timestamps use one configured application clock. Compare timestamps before
subtracting, and check addition against `UINT64_MAX`; backward clock jumps must
be handled before calculating elapsed time. ROS adapters validate signed native
timestamps before converting them to this contract.

`dtNs` is an elapsed
integration/control interval. `inputDtNs` is the interval used for input rate/slew
semantics; it can differ from a model's prediction substep. Both are positive
where used; checked arithmetic rejects overflow. Physical watchdogs use a separate
monotonic clock. Future prediction times may differ from the current control tick.

`status` always uses common/constants.capnp `code*`. Contract version 1 defines
codeOk=0 and codeInvalid=1. Numeric outputs are consumable
only on codeOk or codeLimited. codeLimited still requires complete, valid outputs;
it is not permission to use a partial or infeasible command. Other results do not
authorize stale output reuse. On rejected estimator updates, preserve the last
committed estimate. Software/model/solver failures are handled by the coordinator;
hardware faults can require a coordinated stop because physical writes cannot be
rolled back. Plugin methods do not change RPP lifecycle themselves.

## ReferenceGenerator

Schema: [reference/reference.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/reference/reference.capnp).
The description defines the coordinate layouts. Goal submission and reference
sampling use flat numeric arrays.

### getDesc

Read after configuration to prepare measured-state inputs, goal updates, and
reference outputs. `state` describes the measured-state row. `targetMask` selects
goal fields from `reference`, independently of measured inputs. `reference` is a flat `FieldListDesc` describing one generated
sample. Component configuration selects the fields and their physical meaning.

Use `features` to choose supported application goal operations before activation.
It is an OR of independent UInt8 bits from reference/constants.capnp:

| Constant | Value | Enabled method |
| --- | --- | --- |
| generatorSetPoint | 1 | setPoint |
| generatorSetPath | 2 | setPath |
| generatorSetTrajectory | 4 | setTrajectory |

For example, features=3 supports points and paths. Support is for the configured
instance and stays fixed until reconfiguration. Unsupported setters return
codeUnsupported without changing the accepted target. The other four methods
are always part of the contract; there are no feature bits for them.

### bind

Call with numeric updates paused. Supply `horizonLength` and `horizonOffsetsNs`.
Zero length and empty offsets request one current value per reference scalar.
For positive `H` and reference width `R`, offsets contain either `H` shared times
or `R * H` individual times in reference-major order. Each horizon starts at
zero and strictly increases. Quaternion coefficients use identical times.

Binding validates capacities and sampling offsets, prepares numeric storage, and
atomically commits the complete horizon. Failure preserves the previous binding.
Accepted goals and component activation state survive successful rebinding.

### setPoint

Call with numeric updates paused to stage one desired row in the declared reference layout.
`targetMask` selects reference fields. `updateMask` follows scalar reference order and
preserves unselected curves. Quaternion coefficients update together. An empty
update mask selects all target scalars. The generator determines the resulting
motion profile. Successful staging acknowledges acceptance of the target.

### setPath

Call with numeric updates paused to stage nonempty waypoint states, flattened
in waypoint-major order using the declared reference layout. `updateMask` selects
the same scalars in every waypoint. Speed, interpolation, and path progression
belong to the generator's parameters and algorithm. Rejection preserves the old target.

### setTrajectory

Call with numeric updates paused for timed waypoint `states`. `timesNs` has the same nonzero count,
starts at zero and strictly increases. Times are relative to the first sample
that activates this submission. Each waypoint follows
the declared state layout. Validate sizes, finite values, geometry and capacity
before acknowledging `status`. Rejection preserves the previous target.

### cancel

Call with numeric updates paused to clear the accepted target. `status`
acknowledges the request. The interpolating generator subsequently returns
measured values for unset targets. The coordinator clears their validity flags
and produces safe actuator output through its control execution policy.

### sample

Call with a coherent `state` snapshot and unsigned nanosecond `timeNs`.
With zero horizon length, the returned flat `reference` contains one current
value per reference scalar. Otherwise it contains `R * H` values at index
`r * H + h`, sampled using the bound offsets.

Sampling returns reference values and status; it does not report arrival.
Trajectories retain their final values, with a throttled executor warning if
requested times move past the supplied trajectory. A timed submission must
initially cover the bound horizon.
The interpolating generator supplies measured values for unset targets; the
coordinator supplies their false validity flags to controllers.
A failed sample makes its consumers unavailable for the tick.

## MissionMonitor

Schema: [mission/mission_monitor.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/mission/mission_monitor.capnp).

### getDesc

Read after configuration. Flat `state` and `reference` layouts declare the
observations and current generated reference fields needed by `isOk`.
The flat `goal` layout declares final-target fields needed by `isGoalReached`.
An empty goal layout identifies a guard-only monitor.

### resetHistory

Clear history for a new mission. Replanning preserves mission watchdogs.
The method has an explicit name because RPP's inherited `reset()` returns void.

### isOk

Evaluate every active mission monitor against one coherent measured/reference
snapshot and the caller's `timeNs`. Only `ok=true, status=codeOk` permits
continuation. A valid stop vote returns `ok=false, status=codeOk`; evaluation
errors or a missing required instance also stop the mission. The supervisor
cancels the mission's reference; monitors do not command hardware or change lifecycle.
The additional `message` string explains a stop/error or supplies optional context.
Empty text means there is nothing to report. Diagnostic text handling runs outside
the realtime numeric worker. Supervision preserves the message in ROS monitor
status and includes the first veto/error message in the action's failure result.

### isGoalReached

The action selects exactly one active goal-capable monitor. That instance also
participates in `isOk`. After all guards approve, call only its `isGoalReached`
with the same measured snapshot and the final target in `desc.goal` order.
The selected monitor decides arrival independently of generator timing.
Changing the target clears target-specific history without restarting watchdogs.
Guard-only instances return codeUnsupported when asked for arrival.

## ControlLaw

Schema: [control/control_law.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/control/control_law.capnp).

### getDesc

The configured instance declares flat `state`, `reference`, and `control`
field lists. State is measured input, reference is desired input, and control
is produced output. The manager prepares field routes and validates exclusive
control destinations.

`horizonLength = 0` uses one current reference value per scalar and empty offsets.
Positive `H` accepts `H` shared offsets or `R * H` per-scalar offsets. Values
and per-scalar offsets use reference-major order `r * H + h`. The description
stays fixed while configured. `ControlLawLayout` validates the field lists,
buffer dimensions, sampling offsets, and quaternion timing.

### compute

Call once per control tick. `state[n]` is a coherent snapshot at `timeNs`;
`reference` contains the flattened samples described above. `dtNs` is the elapsed control
interval, used by integration, derivatives and rate policies. First-cycle policy
must provide a configured valid interval rather than divide by an unknown value.

`previousControl[nu]` reports feedback in the controller's command layout. At the
actuator boundary it estimates the previous hardware-accepted actuation, mapped
back to controller space by ActuationMapper.feedbackMap. At an internal cascade
boundary it can report the previous selected reference consumed by the next
stage. It supports anti-windup, slew handling and solver initialization.
`previousControlValid=false` means ignore its contents, including on the first tick
or when back-mapping is unsupported. The buffer still has its fixed nu capacity.

`inputValid` is empty (all valid) or contains one flag per flattened reference
scalar. False means an unavailable or expired input. Values remain present, and
the controller determines which outputs can still be computed. Goal update masks
are separate: true replaces the selected goal value and its expiration; false
preserves both. The coordinator retains deadlines per input value.

`enabledAxes` is empty to enable all command axes, or contains `nu` boolean flags
in command order. Disabled axes output zero and clear their controller history.
PID axes restart without applying feedback from their disabled tick. All state
and reference values remain present and valid; the mask does not change layouts
or horizons. A cascade passes this mask to its innermost controller, whose command
layout matches the cascade's final outputs.

`control[nu]` is the next requested controller-space output. `status` reports the
result; optimization controllers must obey their configured work budget and
return failure if no acceptable feasible command is available. The law calls
bound model/constraint functions itself and never writes hardware.

## ActuationMapper

Schema: [control/control_law.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/control/control_law.capnp).

### getDesc

Call after configuration to read the fixed layouts. `state` declares the measured
or actuation/history fields the mapper needs; `control` describes nu controller
inputs; `actuators` describes na hardware channels. Each entry in `limits` selects
actuator fields and declares optional lower, upper, and absolute rate bounds.
Both mapping calls use these same field orders. A forwarding mapper is valid
when the command and actuator spaces already coincide.

### commandMap

Call to map the selected command before writing, or for a candidate during a
solve. `state[n]` and `control[nu]` are explicit inputs. `dtNs` supplies the
input rate interval; necessary previous actuator/input values live in bound state.
`actuators[na]` is the proposed hardware vector; `realizedEstimate[nu]` estimates
the input it would produce after allocation/saturation. `status` reports validity/limiting.
This call performs no physical I/O and commits no hidden prediction history.

### feedbackMap

Map `state[n]` and `actuators[na]` feedback to `realized[nu]` in the controller's
command order. With hardware connected, use the actuator values it reports or
acknowledges. The current control script uses limited actuator commands as its
feedback source. This call returns `realized`, while `commandMap` returns
`realizedEstimate` for the proposed command. On success, store `realized` as the
next tick's previousControl and set previousControlValid=true. If unsupported, return
codeUnsupported and leave that flag false. Other failures follow the configured
fault policy. Hardware acknowledgements do not imply measured physical effort.

## ControlConstraint

Schema: [control/constraints.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/control/constraints.capnp).
Use these methods inside a controller that enforces an optimization feasible set,
such as MPC. A simple feedback law can omit constraint slots. These mathematical
constraints do not replace physical hardware limits or watchdogs.

### bind

Call before activation with `state` and scalar `commands` in the controller's
input order. RPP parameters choose the constraint, resources, scales and any
configured scene/model sources. `rows` fixes M, the number of constraints, and
all output capacities. `status` reports compatibility; row counts stay fixed active.

### bounds

Call for a solver stage at `timeNs`; cache only bounds known to be constant.
`bounds[2*M]` packs all M lower bounds followed by all M upper bounds. Equal
bounds represent equality; +/-infinity can disable a bound. Reject NaN and
lower>upper. `status` reports whether the stage's bounds are valid.

### evaluate

Call for candidate `state[n]` and `input[nu]` at stage `timeNs`. `inputDtNs`
provides rate/slew semantics matching the candidate model input. `values[M]`
contains g(x,u,t), whose feasibility is lower<=g<=upper. Every returned value is
finite. `status` reports whether evaluation succeeded. Scene/contact snapshots
are staged and held consistent for all evaluations in one solve.

### jacobian

Call at the same candidate/time/inputDt as evaluate when the solver needs
derivatives. `stateJacobian[M*nt]` differentiates g(retract(x,delta),u,t) at
delta=0; `inputJacobian[M*nu]` differentiates the numeric input. Rows, units and
scales agree with evaluate/bounds. `status` reports valid derivatives. This is
a local derivative, not an instruction to apply the candidate to hardware.

## Model

Schema: [model/model.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/model/model.capnp). All numeric methods
are mathematical evaluations on supplied arguments; they do not own the robot's
posterior state, desired reference or hardware connection.

### stateDesc

Call during binding to obtain `state`, the model's ordered state-field definition.
Its kinds/sizes determine n and nt through the shared builder. Model parameters
define physical coordinate roles without a separate control-specific layout.

### inputsDesc

Call during binding to obtain `inputs`, the nu scalar model-input channels in
their required order and units. Controller outputs and estimator known inputs
must match or use a prepared explicit mapping. Zero inputs are valid for an
autonomous process/observation model.

### bind

Call before activation with requested physical `observations`, in port order.
Each StateDesc defines the quantity, packing and frame of one observation. These
are spaces to evaluate, not measured values or desired targets. Prepare all
numeric functions and reject unsupported observation semantics. An empty list is
valid for a process-only model. `inverseDynamicsSize` fixes both acceleration and
effort width for inverseDynamics, or is zero when that operation is unsupported;
this width does not describe their ordering. That ordering follows the model's
configured generalized coordinates. `status` reports complete binding acceptance.

### featuresDesc

Call during binding to read the configured model's UInt8 `features` mask from
model/constants.capnp: modelPredict=1, modelLinearize=2, modelObserve=4,
modelObservationJacobian=8, modelInverseDynamics=16. Check algorithm requirements
before activation. Linearize implies predict; observationJacobian implies observe.
Retraction/difference are mandatory. ObservationDifference is mandatory for
observed ports when observe is supported. Unsupported optional numerical methods
return codeUnsupported; no graph construction or capability discovery occurs in a tick.

### predict

Call for a simulation/prediction stage using `state[n]`, `input[nu]`, stage start
`timeNs`, integration duration `dtNs`, and input slew interval `inputDtNs`.
`next[n]` is the state at timeNs+dtNs. Input is held over the integration interval
under the bound model's actuation semantics. Different substep durations must not
silently change the input slew interval. `status` reports valid prediction.

### linearize

Call at the same arguments as predict when a filter or optimizer needs the
discrete transition derivative. `a[nt*nt]` and `b[nt*nu]` satisfy, locally:

```text
y  = predict(x, u, time, dt, inputDt)
y' = predict(retract(x, dx), u + du, time, dt, inputDt)
difference(y, y') ~= a * dx + b * du
```

The input/output tangents follow the shared frame convention at x and y.
`status` reports valid derivatives. A continuous-time Jacobian cannot be returned
as a discrete transition without the required discretization.

### retract

Call whenever a solver/filter needs to apply `delta[nt]` to `state[n]`.
`next[n]` follows the shared field-kind operations, including normalized
quaternions and frameId-axis rotation increments. `status` reports validity.
This operation applies a supplied correction; it does not decide that correction
or mutate an estimator. Quaternion filter covariance transport needs additional
algorithm support beyond having this operation.

### difference

Call to compare `origin[n]` with `target[n]` in the same bound state layout.
`delta[nt]` is target minus origin under the shared local coordinate convention,
so retract(origin,delta) recovers target locally. It handles angle wrap and
orientation geometry. `status` reports validity. It supplies no weights, priorities
or tracking policy; the caller chooses the two arguments and how to use the result.

### observe

Call to predict a physical observation, for example a tool pose or an IMU-model
output. `state[n]` and `input[nu]` are explicit candidates; zero-based `port`
selects the bound observation. `timeNs` is evaluation time, and `inputDtNs` gives
the input slew interval where the observation depends on actuation. `values[nz[port]]`
contains h(x,u,t). `status` reports validity. This method does not subtract a goal
or measurement, and the port must have been bound before activation.

### observationJacobian

Call at the same arguments as observe when its local derivative is needed.
`stateJacobian[ne[port]*nt]` and `inputJacobian[ne[port]*nu]` differentiate
observationDifference(port,h(x,u),h(retract(x,dx),u+du)) at zero perturbation.
`status` reports valid derivatives. For rotations this is not automatically the
Jacobian of a tracking residual against a distant fixed target; the controller
must include the relevant difference derivative.

### observationDifference

Call for bound `port` with `origin[nz[port]]` and `target[nz[port]]`.
`delta[ne[port]]` is the local target-minus-origin difference using that
observation's field kinds and frameId axes. An estimator typically compares
predicted to measured values; a controller chooses the argument order for its
tracking cost. `status` reports validity. No measured or desired state is stored.

### inverseDynamics

Call only when modelInverseDynamics is advertised, for example from a computed-
torque controller. `state[n]` contains the configured positions/velocities;
`acceleration[inverseDynamicsSize]` uses the model's generalized acceleration
ordering, and `effort` has that same width and corresponding generalized effort
ordering. These are not arbitrary observation-space accelerations or necessarily
the nu input channels. `status` reports valid effort. Conversion/allocation to
actuators remains control/mapper work.

## Estimator

Schema: [estimation/estimator.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/estimation/estimator.capnp).
The estimator owns the estimate, covariance and bounded input/measurement history.
It calls configured model slots; models retain no second posterior state.

### bind

Call before activation with `state`, known scalar `inputs`, and ordered
`observations`. Resolve each observation to its configured model/output and
prepare filter matrices, scratch and bounded history. Validate required model
features and supported state/error-coordinate conventions. `status` reports
compatibility. A quaternion descriptor alone does not establish quaternion EKF support.

### initialize

Call after successful binding while inactive to establish `state[n]`, tangent
`covariance[nt*nt]` and their reference `timeNs`. Validate finite values, geometry,
and symmetric positive-semidefinite covariance. Clear processing history.
`status` acknowledges the initial estimate; rejected input does not create a
partially initialized filter. Runtime methods return codeNotReady before initialization.

### predict

Call to advance the owned estimate to end `timeNs` using known `input[nu]`.
`dtNs` must equal timeNs minus the estimate's previous reference time. The process
model receives the previous reference time as its predict start time.
`inputDtNs` is the input slew interval, independently of the integration duration.
`processCovariance[nt*nt]` is already-discretized additive Q for this interval,
in the destination state's tangent coordinates. The estimator propagates P and
adds Q; it does not reinterpret Q as a continuous spectral density. `status`
acknowledges the committed advance. Obtain state/P afterward with estimate().

### correct

Call to fuse `measurement[nz[port]]` from a bound zero-based `port` at acquisition
`timeNs`. `covariance[ne[port]*ne[port]]` is R in that observation's tangent
coordinates. The estimator uses the configured observation model and stored input
appropriate to that measurement time, computes an innovation, and applies its
configured gating/update policy. `status` acknowledges correction or explains
rejection. An intentionally gated-out measurement returns codeRejected and leaves
the posterior unchanged.

Late data is accepted only within explicitly supported bounded replay/history
policy; otherwise return codeStaleInput. Replay must reconstruct inputs and the
correct discrete Q for every replay interval. This draft's Q argument does not by
itself supply noise discretization for newly split intervals. Generic filters
remain native; optional model/derivative providers may use CasADi.

### estimate

Call after updates or to publish/read the current result. Write one coherent
`state[n]`, `covariance[nt*nt]` and their reference `timeNs` into prepared outputs.
`status` reports availability/validity. Time is the state reference time, not
publication time or a guarantee that the estimate is fresh enough for control;
the coordinator enforces source age/skew rules.

### reset

Call while inactive to replace state, covariance and reference time using the
same argument rules as initialize. Clear replay, gating and numerical history.
Use it for explicit reinitialization after a fault or global state jump, rather
than pretending a reset is an ordinary noisy correction. `status` reports acceptance.

## Hardware

Schema: [hardware/hardware_io.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/hardware/hardware_io.capnp).

### interfacesDesc

Call during binding to obtain `interfaces`, the device's exported typed endpoint
descriptions. Each name identifies an existing configured RPP subcomponent; typeId
identifies its Capn Proto interface node, not its source-file ID. Resolve/check
that slot with RPP contexts, then use active handles for calls. The method does
not return a component instance or define another loader. Exported endpoints can
share one device backend/connection and are configured before activation.

## HardwareIO

Schema: [hardware/hardware_io.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/hardware/hardware_io.capnp).
This interface handles scalar numeric acquisition/commands. Camera/lidar and
generic Data sensor endpoints remain future contracts.

### measurementsDesc

Call during binding for `channels`, the nm scalar entries returned by read, in
exact order. Each describes quantity, unit, applicable frame/coordinate mapping
and source name. Bind hardware feedback/state or estimator-ingress mappings once.
This is not a sample, an automatic ROS publisher declaration or a sensor decoder.

### commandsDesc

Call during binding for `channels`, the na scalar entries consumed by write, in
exact order. Each identifies its physical resource, mode/quantity and units.
Resolve controller ownership and mapper outputs against these channels. Modes
of the same physical actuator share resource identity and cannot have conflicting owners.

### limitsDesc

Call during binding to obtain static `limits`, a common FloatMatrix with three
rows and na columns: all lower bounds, all upper bounds, then all maximum absolute
rates per second. Infinite bounds/rates disable those restrictions; NaN, negative
rates or lower>upper are invalid. The mapper/coordinator caches these limits and
prepares rate enforcement. Dynamic model constraints remain ControlConstraint work.

### read

Call from the configured acquisition schedule. `values[nm]` follows measurementsDesc;
`timeNs` is acquisition time, not read-call completion. Values form one coherent
timestamped group. A driver needing independently timed streams exposes appropriate
separate endpoints instead of silently assigning one time to unrelated samples.
`status` reports availability/validity. This does not perform application localization.
An unavailable source must not be replaced with an unmarked stale value.

### write

Call after ownership, numeric, limit and deadline validation with the complete
`command[na]`. `accepted[na]` reports exactly what the endpoint acknowledged;
clipping returns codeLimited with the clipped values. `status` reports the write
result. Unknown acceptance or partial physical writes are failures, not success
with the requested vector echoed back. Different devices have no implied atomic
write transaction. On success, pass the accepted actuator values to feedbackMap.

### stop

Call for the configured fault policy, cancellation policy or deliberate physical
stop. `resources` contains prepared command-channel indices, not resource-name
hashes or frame IDs. A nonempty request covers the selected physical resources;
the driver handles all modes of each selected resource together. Empty or invalid
selections are rejected. `mode` is hardware/constants.capnp stopConfigured,
stopControlled, stopHold or stopDisable; stopInvalid is rejected. Supported
mode/resource combinations are validated during configuration, with unsupported
requests returning codeUnsupported.

`status` acknowledges initiation of the device's configured bounded stopping
behavior; it does not prove mechanical rest. Verify completion through feedback
and keep physical watchdogs active. The method does not implement reference
cancellation, estimator reset or RPP lifecycle transitions.
