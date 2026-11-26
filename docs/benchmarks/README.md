# Benchmarks

| Benchmark | What it measures | Instructions |
| --- | --- | --- |
| Communication | RPP native/RPC calls and ROS 2 communication across Python/C++ processes. | [Communication benchmark](communication.md) |
| Localization | Estimate accuracy, CPU, allocations, and replay on recorded sensor data. | [Bag parity runbook](https://github.com/coe-marble/rpp_localization/blob/develop/test/robot_localization_parity/README.md) |

Communication sources live in `rpp_demos/benchmarks`; localization tooling
lives in `rpp_localization/test/robot_localization_parity`. Each runbook gives
the setup commands and explains its output files.

When comparing runs, keep inputs, configuration, requested rate, and build
profile the same. Record versions and hardware with the results. Compare the
amount of completed work alongside CPU and timing.

Localization worker CPU excludes replay performed on the ROS executor.
The [estimation guide](../interfaces/estimation/generic-estimation-and-localization.md#bag-comparison-and-measurements)
explains which CPU scopes and replay counters to compare.
