# Generic estimation and localization

`rpp_localization` combines sensor measurements into an estimate of motion.
The estimator keeps the state, its uncertainty, and the history needed to process
late measurements. The model describes how that state evolves and what each
measurement means.

The same estimator interface is used by `Ekf` and `Ukf`. Their algorithms
work with configured dimensions; the bundled navigation model supplies the
vehicle-specific 15-state layout.

## Prediction and correction

Suppose an estimator tracks position and velocity. Between sensor updates, it
uses velocity and elapsed time to predict position. Prediction also updates the
covariance, which describes uncertainty. Process covariance Q accounts for
uncertainty added during that interval.

When a position measurement arrives, correction compares it with the predicted
position. The estimator combines the two according to their uncertainty.
A more precise measurement has more influence; a noisier measurement has less.

For a single directly observed position coordinate, an update might be:

```text
Predicted position:     1.00 m, variance P = 0.04 m²
Measured position:      0.80 m, variance R = 0.01 m²
Measurement weight:     P / (P + R) = 0.8
Corrected position:     1.00 + 0.8 * (0.80 - 1.00) = 0.84 m
Corrected variance:     0.008 m²
```

The full filter applies this operation to vectors and covariance matrices,
including correlations between coordinates. A measurement can update part of
the state: position measurements do not need to supply velocity, orientation,
or every other estimated value.

## What the estimator and model each do

The model evaluates supplied values. `predict()` calculates the next state;
`observe()` calculates the sensor reading expected from a candidate state.
Derivatives and coordinate differences support the filter's calculations.

The estimator owns the changing estimate. It calls the model, propagates
covariance, computes innovations, applies gating, and commits accepted updates.
For example, a rejected measurement leaves the previous estimate available.

`SharedEstimatorBase` connects the Gaussian cores to the shared
`Estimator` and `Model` interfaces. `GenericLocalizationScript` prepares
the field routes between the application and estimator. Use Euclidean and
scalar-angle fields with the supplied Gaussian plugins.

## Configuration and execution

Configuration reads the estimator's `getDesc()`: its state fields, known input,
and measurement layouts. Each measurement layout has an index. A correction
supplies that index, its values, its covariance, and the acquisition time.
The filter therefore knows which observation is being corrected and how the
numbers are ordered.

Before activation, initialize the state, covariance, and reference time.
Configuration has already prepared the matrices, decompositions, queues,
snapshot pools, and replay checkpoints. Prediction and correction reuse them.

The ROS node divides work between two threads. The executor decodes sensor
messages, performs frame conversion, handles lifecycle/reset requests, and
publishes results. The numerical worker consumes prepared events and calls
the estimator and model. The supplied executables use a SingleThreadedExecutor
for the ROS side.

Full ingress returns `codeBudgetExceeded`. Publication can drop a snapshot
while filtering continues. A retained result holds its prepared output slot;
the slot becomes reusable when the view is released.

## The 15-state navigation composition

The bundled navigation model uses:

```text
[x, y, z, roll, pitch, yaw,
 vx, vy, vz, vroll, vpitch, vyaw,
 ax, ay, az]
```

This ordering belongs to the navigation model. The generic filter receives the
configured layout and does not choose navigation axes itself.

The navigation adapter converts odometry, pose, twist, and IMU messages into
configured measurements. Sensor masks choose which coordinates are used.
For example, a sensor supplying only yaw rate produces a yaw-rate correction;
missing position axes are not filled with invented zero measurements.
Covariance cross terms for retained axes are preserved.

The adapter handles configured frame transforms, relative/differential poses,
gravity removal, and planar constraints. It publishes filtered odometry and can
publish a control-state projection. In 2D that projection is
`[x, y, yaw, vx_body, vy_body, wz_body]`. This gives control the fields it needs
without changing the estimator's full state ordering.

Launch examples and sensor parameters are described in the
[localization runbook](https://github.com/coe-marble/rpp_localization/blob/develop/README.md).

## Time and process noise

A measurement's timestamp is its acquisition time. Its callback arrival time
may be later. The estimate's timestamp records the time represented by its
state; publication time can be later again.

Prediction advances from the previous estimate time to a requested end time.
`dtNs` must equal that difference. The supplied process covariance Q is already
discretized for that interval. Automatic ROS prediction obtains Q by multiplying
the configured `process_noise_density` by elapsed seconds.

Covariance uses tangent coordinates and is flattened row-major. For the
15-coordinate navigation state, P and Q contain 225 values. Measurement
covariance uses the selected measurement's tangent width.

## Late-measurement replay

Suppose the filter has processed states at 1.1 s and 1.2 s, then receives a
measurement acquired at 1.1 s. Correcting the 1.2 s state directly would associate
the measurement with the wrong time. Replay restores the saved state at the
measurement time, applies the correction, and processes the later events again.

`history_capacity` sets how many prepared history records are retained.
Setting it to zero disables history and spare-estimator construction.
Measurements older than retained history cannot be replayed.

With `replay_execution=ros`, the node uses two estimator/model instances behind
one logical estimator. The worker keeps processing live events. The ROS executor
repairs the idle instance and catches it up with those events. The worker adopts
the repaired instance only when both have consumed the same event sequence.
If new events arrive first, catch-up continues before adoption.

Queued corrections are processed in timestamp order in bounded batches. A batch
rewinds to its earliest affected checkpoint, then reprocesses the affected tail.
`replay_events_per_tick` defaults to 64. `replay_execution=worker` performs
replay inline in one estimator instead.

A late measurement between saved prediction times may need to split a prior
prediction interval. `replay_noise_policy=reject_split` rejects an update that
requires such a split. `constant_rate` permits proportional splitting of that
interval's frozen noise density. It reuses that density during replay.

## Bag comparison and measurements

The bag comparison runs the generic RPP estimator and robot_localization on the
same recorded sensor data. It saves estimated tracks, accuracy differences,
CPU, allocations, and replay counters. `PARITY_RL_REPLAY` selects replay for
both implementations.

Use both replay counters when reading a report. A background job is a repair
session; internal rewinds count the history reprocessing within it. Several
service batches can belong to one job.

Worker CPU excludes replay done by the ROS executor. To compare estimator cost,
add the worker-estimation and replay CPU scopes, or compare total process CPU.
Replay-state counts describe each implementation's saved history records.

The [bag parity runbook](https://github.com/coe-marble/rpp_localization/blob/develop/test/robot_localization_parity/README.md)
gives the build options, run commands, and output files. Rebuild the node and
refresh registered plugins together after changing native estimator/replay
headers.
