# ROS independent RPP control framework

Revised proposal for review, 2026-11-21.

RPP control provides native control execution and replaceable algorithms. The
existing MORE libraries provide shared CasADi models and graph infrastructure.
Simulation, localization and control consume those shared definitions through
explicit bindings. Core control mechanisms require neither ROS nor CasADi.

The schema families live in rpp_interfaces under `plugin_types/common`,
`reference`, `control`, `model`, `estimation` and `hardware`. They are
experimental contracts, not registered implementations. Generated native types
use the rpp_interfaces namespace; algorithm implementations remain in rpp_control.
The [stack and message map](control-stack-and-message-map.md) describes their
current signatures and numerical conventions. This plan establishes ownership,
dependency boundaries and the work needed before implementing them.

The [shared route and schematic](../shared-bind-and-runtime.md) defines the
common binding-only StateDesc/StateFieldDesc/ChannelDesc and flat runtime
List(Float64) buffers. Estimation/localization use those descriptions without
depending on control-specific layouts. All Desc getters belong to the binding
phase; numerical updates use prepared dimensions, offsets and buffers.
Fields declare kind, optional vector size and ROS-style frameId/childFrameId
names. The planned shared layout builder calculates all offsets and dimensions;
configuration does not author them. The [method reference](../interface-methods.md)
documents every call, including generator capability discovery and previous-input
validity in ControlLaw.compute().

The [five-family boundary contract](../component-boundaries.md) is the source of
responsibility and constant ownership. Reference generation supplies desired
values, control chooses commands, the model evaluates mathematics, estimation
owns the posterior, and hardware owns physical I/O. All bind common descriptions.

## Dependency boundaries

| Layer | Responsibility | CasADi dependency |
| --- | --- | --- |
| RPP runtime | Component construction, typed slots, parameters, lifecycle, active guards and replacement | None introduced by control |
| rpp_interfaces | Shared control and future estimation/model/sensor schemas; no algorithm implementations | None |
| rpp_common | Existing common geometry, numeric containers and neutral shared conventions | None introduced by control |
| rpp_control | Control execution, references, native algorithm contracts, resource claims, limits, faults and scalar HardwareIO | No required dependency |
| more_common | Shared graph serialization, descriptions, composition utilities and prepared function support | Required for its graph utilities |
| more_dynamics | Physical dynamics definitions and composition | Required |
| more_sensors | Existing symbolic sensor models | Required by the current graph-based library |
| more_simulation | Simulation using the shared dynamics and sensor models | Required by the current implementation |
| rpp_control_casadi, proposed extension | Implement native model/constraint interfaces using shared graphs and derivatives | Required within the extension |
| rpp_control_mpc, proposed extension | CasADi-based MPC implementing ControlLaw | Required within the extension |
| rpp_estimation, proposed | Generic estimation algorithms and execution | No required dependency |
| rpp_localization | Navigation models, sensor models and localization compositions using estimation | Base composition remains independent; graph adapters require CasADi |
| Optional ROS wrapper | Topics, services, actions, TF and clock translation | No required dependency introduced by the core |

Extension package names are proposed organizational boundaries. Use separate
libraries/packages or independently selectable build targets so installing and
building the core does not pull in the CasADi or ROS extensions. Public core
headers and plugin interfaces expose numeric data, not CasADi classes. Selecting
an extension brings its dependencies into that application.

`more_common` currently declares CasADi in its installation requirements. Core
control must not depend on it for otherwise neutral utilities. Reuse neutral
common types from rpp_common and keep graph helpers on the CasADi side.

## One shared modeling system

Reuse the existing graph-provider mechanism: RPP configures a plugin, the plugin
provides serialized CasADi functions and descriptions, and a consumer prepares
its numeric evaluator. Reuse `RppCasadiGraph`, `graph_to_bytes` and
`graph_from_bytes` rather than implementing another serialization mechanism.

The dynamics and sensor schemas currently duplicate IO/state descriptions and
use distinct graph payloads. Consolidate their shared descriptions and graph
payload schemas in rpp_interfaces with explicit migration of existing consumers.
Keep serialization/evaluation helpers in the MORE common layer. Preserve
sensor-specific metadata such as message identity. Do not add another competing
graph payload inside rpp_control.

Define robot geometry, joints, mounts, inertias, actuator behavior and calibration
once through the RPP GUI/system. Extend MORE with articulated and combined robot
models as needed. A mobile manipulator requires actual base/arm coupling in that
shared model; concatenating independent model predictions is insufficient.

Simulation uses the model to propagate simulated state. Localization uses a
selected process/observation model. MPC uses prediction and optimization functions.
They share physical definitions, conventions and reusable function preparation.
They retain independent state and scratch buffers: an MPC trial must not change
simulation truth or estimator state. Different fidelity or reduced models are
explicit selections from the same modeling infrastructure.

The current HullVessel graph is continuous-time and uses a 12-value Euler-angle
vessel state plus actuator state. The control adapter must explicitly map that
representation to the shared state fields, units and frames, and construct a discrete
prediction function. Derivatives of the discrete step must match the selected
integration scheme and manifold conventions. Share the step-construction code
with simulation where the same scheme applies.

The existing localization VehicleModel3D bridge uses numeric propagation and
rejects graph-only models. Shared graph support there is integration work, not
an already working connection. Reuse its existing filter API and state mapping;
add the graph-backed propagation adapter instead of another estimator.

## Native control contracts

All of these contracts are backend independent:

| Contract | Responsibility | Baseline native implementations or extensions |
| --- | --- | --- |
| ReferenceGenerator specializations | Point/path/trajectory to one or more flat reference buffers | PassThroughReference, JointTrajectoryReference, PlanarPathReference |
| ControlLaw | References and measured state to controller-space commands | JointPD, JointPID, VehiclePID; later Cartesian control and MPC |
| ReferenceMonitor | Measured arrival and progress | ToleranceMonitor with bounded progress history |
| ActuationMapper | Controller command to actuator command and estimated realization | DirectMapping, TransmissionMapping, VehicleAllocation, CompositeMapping |
| Model | Numeric prediction, observations, coordinate operations and optional derivatives | Adapter to shared mathematical definitions; no target references or tracking policy |
| ControlConstraint | Numeric bounds, values and derivatives when required | Native joint/input bounds; graph-backed nonlinear constraints |
| HardwareIO | Numeric feedback, commands, limits and stop behavior | MockHardwareIO and robot-specific endpoints |
| Hardware | Common device category and description of exported typed RPP subcomponents | Physical drivers whose endpoints share one backend |

These implementation names describe proposed deliverables. Existing registered
plugins remain supported during migration; their behavior and names are not
silently replaced by these examples.

Adapt the existing PID, cascade and allocation implementations where suitable;
do not copy their algorithms into new parallel implementations. Preserve explicit
normalized-command/SI conversions at compatibility boundaries. Basic feedback
laws and pass-through generators do not require a model plugin: validated neutral
robot-layout metadata can be supplied directly by configuration.

Reference generators remain standalone. A generator may fill several reference
ports, and multiple generators may fill disjoint ports. Port descriptions,
producer assignments and matrix shapes freeze before activation. A servo requests
one current sample; an MPC implementation requests a future sampling grid.

A point or path belongs to the generator. Objective weights and priorities belong
to the law. Reference generation finishing is separate from measured goal arrival.
A generator can accept joint or tool targets according to its typed contract.
A tool target is not silently reinterpreted as joint coordinates.

`Model.linearize`, `Model.observationJacobian` and `ControlConstraint.jacobian` describe
numeric computations. They do not prescribe CasADi. Native implementations can
supply analytic derivatives; the optional CasADi extension derives them from the
shared expression graph. Feature descriptions let configuration reject a model
that lacks operations required by its selected controller.

No core PID, scheduler, lifecycle, state binding, resource claim, hardware I/O,
command check or fault policy is implemented as a CasADi graph. Mathematical
controllers and mappings may have optional CasADi implementations.

## Execution and state sources

The [estimation proposal](../estimation/generic-estimation-and-localization.md)
separates generic EKF/UKF execution from localization models and compositions.
Control consumes its mapped estimates through the same state-input bindings.

```text
application or navigation: point / path / timed trajectory
    -> standalone reference generator(s)
    -> shared reference ports
    -> ControlLaw <--- filtered state; model/constraints when needed
    -> ActuationMapper
    -> ownership, limits and deadline validation
    -> HardwareIO endpoint of Hardware
```

Use existing RPP get_subcomponent_context() for configuration and active handles
for execution. The control layer adds an ordered control schedule, per-actuator
command ownership, state/reference validity and coordinated fault/switch policy.
It does not implement another plugin loader, lifecycle state machine or component
registry. Exported hardware endpoints are resolved by RPP, not returned as Capn
Proto capability objects.

Localization and joint filtering can run elsewhere. Explicit source bindings
select the producer for each q/v/auxiliary range. An ingress adapter maps the
existing filtered estimate into those ranges and preserves source timestamp,
validity and frame information in the coordinator's prepared snapshot metadata.
The controller receives the assembled state double buffer. Hardware read values do not
automatically replace filtered state. Each field has one authoritative producer.

External communication runs outside the control tick. Define maximum source age,
allowed cross-source skew, clock/frame conversion and any interpolation or
prediction policy. A tick consumes an available valid snapshot; unavailable or
stale required state invokes the configured physical hold/stop policy.

The explicit source-binding contract is still needed. Reuse existing localization
Estimate15 and status types at ingress; do not duplicate those filter messages.

## Preparation and runtime performance

Configuration resolves components, descriptions, indices, units, frames and
resources, validates algorithm capabilities, and allocates outputs and scratch.
Shape changes require deactivation and rebinding. Replacements preserve physical
resource ownership and cannot write concurrently with the previous owner.

CasADi extensions obtain graphs, construct derivatives and optimization problems,
and prepare numeric evaluation before execution. Code generation/compilation,
where selected, happens outside active control. Parameter changes that alter a
graph or its structure require rebuilding the prepared functions off-loop.

Numeric updates use native calls, borrowed inputs and caller-owned output views.
Generators write directly into their assigned reference buffers. Constraints and
model derivatives use prepared dimensions and scratch. Independent concurrent
solves use independent workspaces. Honor sparse/dense storage conventions when
mapping CasADi outputs into flat row-major matrix buffers of bound dimensions.

The current RPP generator returns owning data wrappers/tuples; the proposed
$realtime binding policy still requires implementation. Audit active-handle
acquisition as part of the allocation/bounded-work requirement. Neither an
annotation nor generated model code alone establishes deterministic execution.
Solver work, callbacks, I/O and communication handoffs also need explicit bounds.

## Vehicle, arm and combined configurations

| Composition | References | Law and model use | Actuation |
| --- | --- | --- | --- |
| Vehicle baseline | Planar generator | Native VehiclePID; uses only required numeric state | VehicleAllocation to a vehicle HardwareIO endpoint |
| Arm baseline | Joint generator | Native JointPD/PID; dynamic compensation is an optional model dependency | DirectMapping or TransmissionMapping to arm HardwareIO |
| Independent base and arm | Separate generators and laws | Independent loops, optionally at different rates | Disjoint resource ownership over existing driver endpoints |
| Whole body | One coordinated or several base/tool/posture generators | One MPC plugin using the shared coupled MORE model | CompositeMapping routes the jointly computed command |

A whole-body controller claims the union of base/arm resources. Downstream
mapping preserves the coordinated solution rather than running separate base
and arm feedback laws afterward. Prediction includes the same actuation behavior
and limits used for execution. Switching control modes transfers the affected
resource group at a coordinated boundary and reuses existing drivers.

## Future extensions

| Extension | Reused foundation | New work |
| --- | --- | --- |
| CasADi model/constraint adapters | MORE graphs and native numeric contracts | C++ preparation, derivatives, integration and state/layout mapping |
| MPC, NMPC and other optimization controllers | Same ControlLaw, references, shared models and actuation | Solver plugins, objectives, warm starts and bounded execution policies |
| Cartesian arm control | Shared kinematics and reference interfaces | Cartesian error laws, Jacobian-based control or IK generators |
| Articulated and whole-body models | Existing MORE model composition | Arm dynamics, mounting/coupling and generalized constraints |
| Localization graph adapter | Existing filters and shared process models | Prepared propagation/Jacobian integration through the filter model API |
| Simulated control hardware | more_simulation and MORE dynamics | HardwareIO endpoint backed by simulation state and commands |
| Generic sensors | Hardware/RPP subcomponents and existing sensor metadata | Data payloads, message-type constants, framing and publication contracts |
| Optional ROS wrapper | Core application and existing adapters | Boundary translations without importing ROS into core algorithms |

Generic Data sensor acquisition is deferred. HardwareIO measurements and commands
remain numeric for now; commandsDesc(), limits, write() and stop() retain their
current contracts. Sensor graphs model observations; physical acquisition and
message publication remain separate responsibilities.

## Delivery sequence

1. Agree ownership and dependency boundaries; audit proposed schemas against
   existing MORE descriptions and shared common types before freezing them.
2. Establish reusable graph/layout adapters in the MORE/CasADi layer, with a
   migration path for the existing graph payloads and state conventions.
3. Implement the ROS/CasADi-independent core, explicit state ingress and native
   buffer bindings. Start with pass-through, JointPD, DirectMapping and mock I/O.
4. Add the baseline vehicle and arm compositions through the same runtime.
5. Add CasADi-backed numeric model/constraint plugins and reuse their prepared
   functions in simulation and optional localization adapters.
6. Add the MPC extension and then the coupled whole-body model/composition.
7. Complete optional ROS integration and colcon verification of algorithms,
   faults, ownership switching, state timing and execution bounds.

Current registered APIs, units, watchdogs and safety limits remain supported
throughout migration. The current build still requires ROS; removing that core
build dependency is planned work, not a property of the existing package.
