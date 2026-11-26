# Generic estimation and localization

Proposal for review, 2026-11-21.

Create rpp_estimation for reusable estimation algorithms. Build localization
from those algorithms plus navigation-state and sensor models. Shared contracts
belong in rpp_interfaces; implementations remain in their respective libraries.
The generic estimator and control foundations require neither ROS nor CasADi.

The [shared route and schematic](../shared-bind-and-runtime.md) defines the
common descriptions and planned execution path. StateDesc, StateFieldDesc,
ChannelDesc and numeric constants live in rpp_interfaces/common and are already
used by the flat-buffer control draft. Estimation reuses them without importing
the control domain. The Model and Estimator schemas now declare those draft
boundaries; filter extraction and implementations remain planned.

## Responsibilities

| Library | Responsibility |
| --- | --- |
| rpp_interfaces | State/measurement descriptions and numeric process-model, observation-model and estimator contracts, alongside the control contracts. |
| rpp_estimation | Generic EKF/UKF algorithms, numerical validation, bounded measurement processing and reusable estimation execution. |
| rpp_localization | Navigation state conventions, process/sensor-model adapters, frame bindings and localization compositions. |
| MORE and optional CasADi adapters | Shared dynamics/observation definitions and prepared numerical functions or derivatives. |
| Optional ROS integration | Sensor input, estimate publication, TF and clock translation. |

Localization provides a 15-state EKF composition. It does not implement a second
EKF algorithm: a generic EKF is configured with the navigation model and required
sensor models. The same estimator can later support actuator-state estimation,
joint-state estimation, bias estimation or other configured state spaces.

## Similar execution pattern to control

Use RPP typed slots, parameters and lifecycle for estimator and model composition.
Description getters end in `Desc`. Binding resolves dimensions, state meaning,
measurement models, units, frames and noise configuration before activation.
Numeric calls use prepared buffers and fixed capacities while active. Categories
use stable UInt8 constants; dimensions, identifiers and timestamps retain their
appropriate widths. Reuse existing common numeric containers and geometry.

The conceptual contracts are:

| Component | Calls and responsibility |
| --- | --- |
| Estimator | Initialize/reset an estimate, predict to a time, correct with a measurement and read the resulting estimate. Own estimated state and covariance. |
| Process model | Predict state from state, known inputs and elapsed time; supply transition derivatives and process-noise mapping when required. |
| Observation model | Predict a sensor reading from state; supply measurement derivatives and the innovation/residual convention. |
| State operations | Define state increments, residuals and, where needed, manifold retraction and covariance-coordinate transport. |
| Measurement ingress | Validate sensor identity, acquisition time, units, frame, covariance and model binding before scheduling a correction. |

These responsibilities are declared in the experimental Model/Estimator schemas.
A process provider uses Model.predict/linearize; an observation provider uses
Model.observe/observationJacobian/observationDifference. RPP slots and prepared
port maps connect them to the estimator. The [boundary contract](../component-boundaries.md)
defines their buffer sizes, time/noise rules and ownership. Implementations and
legacy compatibility adapters are still required.

## Generic state and measurements

State dimension is selected during configuration rather than fixed to 15.
A measurement has its own dimension, which can differ from the state dimension.
For EKF, the observation model supplies h(x) and its Jacobian H. A measurement
can therefore describe a nonlinear observation, not only selected state entries.
The existing masked-state correction is one useful observation model.

Estimation binds common StateDesc: ordered field kinds, vector sizes and frame names.
Binding derives all offsets and stored/tangent dimensions with the shared builder.
An estimate is a flat List(Float64), with covariance in a separate flat row-major
buffer. Its stored and local-error dimensions are fixed during binding. A
prepared source map selects the fields needed by the controller's state buffer.
Controllers bind that same common StateDesc directly, alongside reference and
command descriptions. Robot-specific coordinate roles remain inside their model
plugins. Estimation-specific descriptions add measurement/noise semantics without
duplicating geometry or dimension records.

For Euclidean state, covariance uses the state dimension. For a manifold state,
covariance uses the local-error dimension, which can differ from the stored
configuration dimension. Angle wrapping and quaternion residuals must follow
the selected state/observation model rather than hard-coded navigation indices.
Support these capabilities explicitly; a generic vector alone is insufficient
to claim support for every attitude or error-state filter.

## The 15-state localization composition

Preserve the existing navigation ordering:

```text
[x, y, z, roll, pitch, yaw,
 vx, vy, vz, vroll, vpitch, vyaw,
 ax, ay, az]
```

Frame, velocity and angular-rate conventions remain explicit in the navigation
model. A localization composition selects:

```text
estimator:        generic EKF from rpp_estimation
process model:   15-state navigation model from rpp_localization
observations:    configured pose, velocity, IMU and other observation models
output binding:  existing localization estimate or mapped control-state input
```

The 15-state dimension, navigation ordering, selected angles and sensor choices
belong to that composition. Generic EKF code handles propagation and correction
using the bound numerical model operations. UKF can reuse the same modeling and
state-operation infrastructure with its own algorithm requirements.

## Reuse and CasADi

Extract and generalize the existing numerical implementation rather than
developing another independent EKF. The current Ekf constructor explicitly
requires STATE_SIZE=15, correction selects measurement entries from that state,
and angle handling uses navigation indices. Those assumptions must move behind
model/observation/state-operation contracts before the algorithm is generic.

Use the existing native implementation for the estimator mechanisms. CasADi
adapters may provide process/observation functions and Jacobians using the same
MORE graph utilities used by simulation and control. Model definitions can be
shared while each consumer retains its own state, covariance and workspace.
Reuse existing MORE dynamics and sensor functions where their declared inputs,
outputs and frames match; localization adapters bind those functions to the
navigation state and measurement conventions. Do not reimplement their physics
or sensor equations in a second library. A model with different measurement
semantics must be selected explicitly rather than silently relabeled.
CasADi is required by the dynamics/MPC extensions that use it, not the generic
estimator or controller core.

## Time, lifecycle and communication

Measurements retain acquisition timestamps in a declared clock domain. Separate
state reference time from arrival time. Prediction and correction ordering,
late-measurement rejection/replay, gating and history limits are explicit policy.
The existing localization implementation has bounded replay behavior that must
be preserved through its compatibility composition.

Build replay storage and scratch outside active processing. Each configured
measurement source has known bounds; optional capabilities describe which
model operations and state representations the algorithm supports. Return
numeric status for ordinary validation/model failures and keep RPP lifecycle
transitions under runtime control.

Cross-process communication and sensor decoding happen in configured ingress
and publication components. The estimator consumes typed numerical measurements.
Control receives a timestamped filtered estimate through a validated mapping;
it does not re-run the estimator or overwrite filtered state with raw hardware
channels.

## Migration sequence

1. Define shared neutral descriptions and estimator/model contracts in
   rpp_interfaces, reviewing common requirements with control and MORE first.
2. Extract reusable EKF mathematics and workspace management into rpp_estimation;
   remove fixed navigation dimensions and selected-state-only measurement logic
   from the generic implementation.
3. Implement the 15-state navigation and observation models in rpp_localization.
   Adapt the existing EKF15/UKF15 public contracts to the generic machinery.
4. Preserve existing payload IDs, status values, timestamps, frames, covariance
   handling, gating and replay behavior during the compatibility migration.
   The existing LocalizationStatus uses UInt16 and different success values;
   new shared UInt8 status conventions require explicit translation.
5. Add optional CasADi-backed process/observation adapters and additional
   estimation compositions using the same core.

Existing registered localization schemas and plugins are unchanged by this
proposal. Migration of their schema ownership and generated C++ namespaces
requires updates to their consumers, compatibility handling and later verification.
