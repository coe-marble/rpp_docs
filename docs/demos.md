# Examples

The scalar-processing examples show how RPP separates a plugin's code,
configuration, and running state. They use two plugins: an affine processor
and an accumulator.

## Processing a stream

The processor calculates `gain * value + offset`. With gain 2 and offset 1,
it turns inputs 1, 2, and 3 into 3, 5, and 7. The accumulator adds each processed
value to its running total.

| Input | Processor result | Accumulated total |
| --- | --- | --- |
| 1 | 3 | 3 |
| 2 | 5 | 8 |
| 3 | 7 | 15 |

The script coordinates the calls: read an input, call the processor, pass its
result to the accumulator. Each component keeps its own configuration and
lifecycle. The script's saved configuration chooses which components fill the
two slots.

After registering the tutorial library and setting `RPP_HOME` as described
in the [tutorial setup](tutorials/README.md#prerequisites-and-execution), run
the pipeline from the `rpp_demos` checkout:

```bash
python3 tutorials/05_scripts/run.py
```

The driver prepares the saved configuration, builds a script runtime,
configures and activates its components, and prints the results above.

## Moving state between instances

The accumulator's total belongs to its running instance. A second accumulator
starts with its own total. To continue work in that second instance, the
application captures the first total, deactivates the first instance, and
activates the second with that handover value.

For example, transferring a total of 7 and then processing 5 produces 12.
This is the operation demonstrated by `tutorials/06_lifecycle/run.py`.
The [lifecycle walkthrough](tutorials/06_lifecycle.md) explains the calls and
the effect of cleanup on the accumulated state.

## Larger applications

Localization applies the same composition pattern to an estimator and its
model. ROS sensor callbacks produce measurements; the estimator worker updates
state and covariance; publication returns filtered odometry. The
[estimation guide](interfaces/estimation/generic-estimation-and-localization.md)
explains that flow and late-measurement replay.

The communication benchmark uses a request/reply workload instead. It sends a
sequence number and a payload, receives the full payload back, and records
round-trip time and completed exchanges. The
[communication guide](benchmarks/communication.md) explains how to run the
Python/C++ combinations and interpret their results.
