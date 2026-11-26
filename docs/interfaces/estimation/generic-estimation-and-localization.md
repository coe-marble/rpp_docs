# Generic estimation and localization

`rpp_localization` currently contains both generic estimation machinery and
navigation-specific composition. There is no separate implemented
`rpp_estimation` package. Shared contracts belong to `rpp_interfaces`;
the numerical cores do not depend on ROS messages or CasADi.

Use the [method reference](../interface-methods.md#estimator) for the public
contract and [shared layouts](../shared-bind-and-runtime.md) for dimensions,
frames, and covariance packing.

## Responsibilities

| Layer | Current owner |
| --- | --- |
| Estimator/Model contracts and field helpers | `rpp_interfaces` |
| Runtime-sized EKF/UKF, workspaces, checkpoints, replay | `rpp_localization/include/rpp_localization/estimation` |
| Native plugin adapters | `rpp_localization::Ekf`, `Ukf`; instrumented `ProfiledEkf`, `ProfiledUkf` for benchmarks |
| Navigation model | `rpp_localization::NavigationModel` |
| Generic coordinator | `GenericLocalizationScript` |
| ROS ingress/publication and worker ownership | `EstimatorScriptNode` |
| Odometry, pose, twist, IMU, and TF conversion | The localization ROS `NavigationInterface` |

An estimator owns state, covariance, and history. Its model evaluates supplied
state/input and owns no second posterior. `SharedEstimatorBase` provides common
Gaussian-filter adaptation; other estimator families can implement
`rpp_interfaces::Estimator` directly.

## Configuration and execution

The estimator's `getDesc()` declares state, known input, and indexed measurement
layouts. Configuration validates model capabilities and prepares field routes,
Eigen workspaces, decompositions, output pools, queues, and history. Initialize
or reset the posterior while inactive, then activate through RPP lifecycle.

The ROS executor converts sensors, handles lifecycle/reset operations, services
offloaded replay, and publishes estimates. A dedicated numerical worker processes
prepared ingress and native guarded estimator/model calls. RPC components are
rejected inside this numerical chain. The supplied executables use a
SingleThreadedExecutor for ROS-side ownership.

Queues and snapshot pools have fixed capacities. Full ingress reports
codeBudgetExceeded; retaining all output slots prevents another snapshot until
one is released. Publication may drop snapshots while estimation continues.
Reconfiguration pauses the worker and rebuilds routes/storage.

## The 15-state navigation composition

The bundled navigation model uses:

```text
[x, y, z, roll, pitch, yaw,
 vx, vy, vz, vroll, vpitch, vyaw,
 ax, ay, az]
```

That ordering belongs to the navigation model and configuration, rather than a
hard-coded generic filter dimension. Prepared observation subsets retain sensor
masks and covariance cross terms.

Current Gaussian cores support Euclidean and scalar-angle coordinates.
Quaternion descriptors and tangent-sized transport buffers do not by themselves
establish quaternion/error-state Gaussian-filter support.

The navigation ROS adapter handles sensor selection, frame transforms,
relative/differential poses, gravity removal, and planar constraints.
It publishes filtered odometry and can project state for control. See the
[package runbook](https://github.com/coe-marble/rpp_localization/blob/develop/README.md)
for launch/configuration and the generic ROS topic/service table.

## Late-measurement replay

`history_capacity` bounds prepared event/checkpoint storage. Zero disables
history and spare-estimator construction.

The default `replay_execution=ros` uses two identically configured physical
estimator/model instances behind one logical estimator. A late measurement
forks history to the idle instance. The worker continues live processing while
the ROS executor repairs/catches up the candidate. Adoption changes the running
instance only at an execution boundary after both consumed the same event sequence.

A replay service borrows bounded batches and merges queued events in timestamp
order, sharing one rewind for the affected batch. `replay_events_per_tick`
defaults to 64. Preparation allocates views, sorting storage, and checkpoints.
Stale or unsupported corrections are skipped; other replay failure retains the
live posterior. `replay_execution=worker` keeps replay inline in one estimator.

Prediction receives additive discrete Q. The default `replay_noise_policy=reject_split`
rejects corrections that need an undefined subdivision of Q.
`constant_rate` explicitly permits proportional splitting of the frozen
per-interval noise density. It does not recompute state-dependent noise under
a revised trajectory.

Rebuild the ROS node and refresh registered plugins together after native
estimator/replay-header changes. The native binding rejects incompatible shared
estimator ABIs. This is separate from Cap'n Proto contract version 1.

## Legacy compatibility and measurement

The previous fixed-size ROS implementation remains available through legacy
entrypoints for comparison. The generic stack and legacy stack have separate
implementations and execution behavior; their equivalence needs measured evidence.

The [bag parity runbook](https://github.com/coe-marble/rpp_localization/blob/develop/test/robot_localization_parity/README.md)
owns build options, replay flags, run commands, counters, and report generation.
`PARITY_RL_REPLAY` applies to generic, legacy, and external robot_localization.
Reports should show both background jobs and internal rewinds.

Worker CPU excludes offloaded ROS replay. Compare total process CPU or the sum
of the disjoint worker-estimation and replay CPU scopes when assessing estimator
cost. Replay-state counts also depend on checkpoint granularity.

Consult a specific saved run for accuracy and cost, rather than treating
implementation presence or regression-test source as validation.
