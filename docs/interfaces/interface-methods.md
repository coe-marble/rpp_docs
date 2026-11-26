# Interface method reference

This reference describes the current shared Cap'n Proto methods. Schemas define
signatures; the sections below explain calling and result semantics. See the
[interface index](README.md) for implementations and source locations, and
[shared layouts](shared-bind-and-runtime.md) for packing and frame rules.

## Reading the signatures

Read `getDesc()` after configuration to prepare routes and buffers. Only the
reference generator exposes `bind()`, for its sampling horizon; the other
interfaces declare layouts through configuration and `getDesc()`.
Reconfiguration invalidates affected bindings.

`FieldListDesc` contains ordered fields, not offsets or total dimensions.
`FieldLayout` derives stored width `n`, tangent width `nt`, and each field's
ranges from kind and size. See [layout and frame rules](shared-bind-and-runtime.md#state-fields-and-dimensions).
Each target, reference and observation description is compiled the same way.

| Symbol | Meaning |
| --- | --- |
| n / nt | Stored / tangent width of the bound state. |
| nu / na / nm | Controller/model inputs / actuator commands / hardware measurements. |
| H / R | ControlLawDesc.horizonLength / stored width of its reference layout. |
| np / npt | Stored / tangent width of ModelDesc.prediction. |
| nz / ne | Stored / tangent width of a model observation or selected estimator measurement. |
| M | Stored width of ControlConstraintDesc.values. |

Numeric matrices are flat row-major buffers. `$realtime` marks intended numeric
execution; allocation behavior depends on the selected implementation and
generated bindings. Native inputs can borrow prepared storage; retained results
must keep their backing storage alive. See [ownership and execution limits](shared-bind-and-runtime.md#native-execution-and-ownership).

All timestamps, durations and relative offsets use unsigned 64-bit nanoseconds:
Cap'n Proto `UInt64`, C++ `std::uint64_t`, and Python integers in `[0, 2^64 - 1]`.
Timestamps use one configured application clock. Compare timestamps before
subtracting, and check addition against `UINT64_MAX`; backward clock jumps must
be handled before calculating elapsed time. ROS adapters validate signed native
timestamps before converting them to this contract.

`dtNs` is an elapsed
integration/control interval. `inputDtNs` is the interval used for input rate/slew
semantics; it can differ from a model's prediction substep. Zero-duration support
depends on the operation; do not divide by an unvalidated interval.
Checked arithmetic rejects overflow. Physical watchdogs use a separate
monotonic clock. Future prediction times may differ from the current control tick.

`status` always uses common/constants.capnp `code*`. Contract version 1 defines
codeOk=0 and codeInvalid=1. Numeric outputs are consumable
only on codeOk or codeLimited. codeLimited still requires complete, valid outputs;
it is not permission to use a partial or infeasible command. Other results do not
authorize stale output reuse. On rejected estimator updates, preserve the last
committed estimate. Software/model/solver failures are handled by the coordinator;
hardware faults can require a coordinated stop because physical writes cannot be
rolled back. A thrown plugin call is an unrecoverable execution error in the
control worker, rather than an ordinary rejected update.

## StateProvider

Schema: [state/state_provider.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/state/state_provider.capnp).

### getDesc

Read the fixed `FieldListDesc` after configuration. `setState` and `getState`
use that complete flattened order. The interface is a state buffer; ROS ingress
and estimation are separate responsibilities.

### setState

Replace the complete sample with `state[n]` and acquisition `timeNs`.
Validate width, finite coordinates, and quaternion normalization before commit.
Rejection preserves the previous sample. The consumer owns freshness policy.

### getState

Return one coherent state view, acquisition time, and status. Return codeNotReady
before the first accepted write. Retaining the view must prevent later writes
from changing its values. The owner serializes numeric and lifecycle calls;
buffer exhaustion must not create an allocation in the numeric path.

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
PID axes restart without applying feedback from their disabled tick. State
and reference values remain present; the mask does not change layouts
or horizons. A cascade passes this mask to its innermost controller, whose command
layout matches the cascade's final outputs.

`control[nu]` is the next requested controller-space output. `status` reports the
result; optimization controllers must obey their configured work budget and
return failure if no acceptable feasible command is available. The law calls
bound model/constraint functions itself and never writes hardware.

### getAuxiliaryState

Read controller-owned described history and its timestamp with numeric updates
paused. RPP handover uses `ControllerHandoverState`; a controller's history is
separate from mapper history.

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

### getAuxiliaryState

Read mapper-owned described history and its timestamp with numeric updates paused.
Stateless mappers return empty state and description. RPP handover uses
`AllocatorHandoverState`, independently of controller auxiliary history.

## ControlConstraint

Schema: [control/constraints.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/control/constraints.capnp).
Use these methods inside a controller that enforces an optimization feasible set,
such as MPC. A simple feedback law can omit constraint slots. These mathematical
constraints do not replace physical hardware limits or watchdogs.

### getDesc

Read `ControlConstraintDesc` after configuration. `state` and `commands`
declare candidate inputs; the Euclidean `values` fields declare M constraint rows.
Parameters select resources, scales, and model/scene providers.
Rows and output capacities remain fixed while configured.

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

Schema: [model/model.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/model/model.capnp).
Numeric methods evaluate supplied arguments; they own no posterior, target,
or hardware connection.

### getDesc

Read `ModelDesc` after configuration. It declares `state`, `inputs`,
`prediction`, `observations`, `accelerations`, `efforts`, and `features`.
Prediction and observation layouts can differ from the input state.
Acceleration and effort layouts describe optional inverse dynamics.

Check the UInt8 feature mask before selecting the model: modelPredict=1,
modelLinearize=2, modelObserve=4, modelObservationJacobian=8, and
modelInverseDynamics=16. Linearization implies prediction; an observation
Jacobian implies observation. Unsupported optional methods return codeUnsupported.

### predict

Evaluate supplied `state[n]` and `input[nu]` at start `timeNs`, integration
duration `dtNs`, and input slew interval `inputDtNs`.
Return `next[np]` in `desc.prediction` order at timeNs+dtNs.
Input slew time is independent of any prediction substeps.

### linearize

Use the same arguments and discrete propagation as predict.
Return row-major `a[npt * nt]` and `b[npt * nu]`: output-tangent rows,
state-tangent or input-value columns. A continuous-time Jacobian is not a
substitute for the declared discrete transition.

### retract

Apply `delta[nt]` to `state[n]`, returning `next[n]` in `desc.state` order.
Use the declared coordinate operations, including angle wrapping and quaternion
normalization. This evaluates a supplied correction; it does not choose or store one.

### difference

Compare `origin[n]` and `target[n]` in `desc.state` order.
Return their local target-minus-origin `delta[nt]`, so retraction recovers
the target locally. The caller owns weighting and tracking policy.

### observe

Evaluate supplied `state[n]`, `input[nu]`, `timeNs`, and `inputDtNs`.
Return one flat `values[nz]` vector in `desc.observations` order.
There is no observation-port argument on Model; consumers prepare their own
subsets or configured model instances. The model does not subtract measurements
or desired references.

### observationJacobian

At the same candidate as observe, return
`stateJacobian[ne * nt]` and `inputJacobian[ne * nu]`.
Rows describe local observation increments; columns describe state increments
or input values. For orientation tracking, a controller may also need the
derivative of its difference operation against the chosen target.

### observationDifference

Compare `origin[nz]` and `target[nz]` in `desc.observations` order and return
`delta[ne]` in its tangent coordinates. There is no port argument.
An estimator uses this for its innovation; a controller chooses the argument
order and weighting for its tracking residual.

### inverseDynamics

Call only when modelInverseDynamics is supported. Supply `state[n]` and
acceleration values in `desc.accelerations` order. Return effort values in
`desc.efforts` order. These layouts declare their widths and meanings explicitly;
they need not equal the model input layout. Actuator conversion remains mapper work.

## Estimator

Schema: [estimation/estimator.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/estimation/estimator.capnp).
The estimator owns the estimate, covariance and bounded input/measurement history.
It calls configured model slots; models retain no second posterior state.

### getDesc

Read `EstimatorDesc` after configuration. `state` describes the owned estimate,
`inputs` its known input, and `measurements` the indexed measurement layouts.
The implementation resolves model slots, validates required features, and prepares
matrices and history during configuration. The schema has no estimator `bind()`.
A quaternion descriptor alone does not establish quaternion-filter support.

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

Call to fuse `measurement[nz]` from zero-based `measurementIndex` at acquisition
`timeNs`. `covariance[ne*ne]` is R in that observation's tangent
coordinates. The estimator uses the configured observation model and stored input
appropriate to that measurement time, computes an innovation, and applies its
configured gating/update policy. `status` acknowledges correction or explains
rejection. An intentionally gated-out measurement returns codeRejected and leaves
the posterior unchanged.

Late data is accepted only within explicitly supported bounded replay/history
policy; otherwise return codeStaleInput. Replay must reconstruct inputs and the
correct discrete Q for every replay interval. Q alone does not define newly split
intervals; the selected replay policy must supply that meaning or reject the
split. See [implemented replay policies](estimation/generic-estimation-and-localization.md#late-measurement-replay).

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

### getDesc

Read `HardwareDesc.interfaces` after configuration. Each endpoint name identifies
a configured RPP subcomponent, and `typeId` identifies its Cap'n Proto interface
node. Resolve those endpoints through RPP contexts. The description returns no
component instance and introduces no separate loader.

## HardwareIO

Schema: [hardware/hardware_io.capnp](https://github.com/coe-marble/rpp_interfaces/blob/develop/plugin_types/hardware/hardware_io.capnp).
This handles numeric acquisition/commands. Generic image/scan payloads remain
future contracts.

### getDesc

Read `HardwareIODesc` after configuration. `measurements` fixes the field order
returned by read; `commands` fixes the order consumed by write and returned as
accepted values. `limits` is a list of field-selecting `LimitDesc` records,
using the [shared limit rules](shared-bind-and-runtime.md#routes-and-limits).

The application prepares mappings and ownership. Measurements need not match
the control state. Command modes of one actuator share its resource identity.

### read

Return a coherent `values[nm]` vector and acquisition `timeNs`.
Time is acquisition time, not call completion or publication time. Independently
timed streams need appropriate separate endpoints. Status reports availability;
an unavailable sample must not become unmarked stale feedback.

### write

Supply the complete `command[na]` after application ownership, limit, and deadline
checks. Return exactly the `accepted[na]` values acknowledged by the endpoint.
Clipping returns codeLimited. Unknown acceptance or partial physical writes are
failures; separate devices have no implied atomic transaction.
Accepted commands can feed the mapper's feedback conversion.

### stop

`resources` contains indices into `desc.commands.fields`, rather than scalar
offsets, hashes, or frame IDs. The driver handles all modes of each selected
physical resource together. Validate the selection and supported mode during
configuration.

`mode` uses hardware/constants.capnp: stopConfigured, stopControlled, stopHold,
or stopDisable. stopInvalid is rejected; unsupported requests return
codeUnsupported. Status acknowledges the requested bounded stopping behavior,
not proof of mechanical rest. Completion needs feedback. This method does not
cancel references, reset an estimator, or change RPP lifecycle.
