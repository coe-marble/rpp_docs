# RPP benchmarks

Runnable benchmark sources live in `rpp_dev/src/rpp_demos/benchmarks`.
The [development image](../development-image.md) supplies the RPP environment;
benchmark-specific preparation and Release builds are still required.

The [communication benchmark](communication.md) compares RPP [plugin][glossary-plugin]
calls and Cap'n Proto RPC with ROS 2 node communication across native and
subprocess language pairs. It includes configurable payload sizes and rates,
raw timing samples, latency distributions, bandwidth, and process-tree CPU.

Registration, loading, configuration, and lifecycle benchmarks remain planned.

For those later benchmarks, reuse the scalar processor contract with a small,
deterministic workload. Keep benchmark drivers in `rpp_demos/benchmarks` and reuse the shared
example library.

Measure registration and interface generation, loading, configuration,
lifecycle transitions, and steady-state invocation separately. Compare a
direct function call with an RPP call in the same language first; add
cross-language calls when both implementations are available. Distinguish
fresh registry generation from refresh and cold starts from warm starts.

Record runtime versions, language pair, execution mode, hardware, workload,
warmup, sample count, and whether process startup is included. Report latency
distributions and throughput with machine-readable raw results. Keep output
logging outside timed loops and verify results before timing the workload.

Localization accuracy and algorithm timing can be added later using identical
inputs and configuration. Report them separately from RPP runtime overhead.

[glossary-plugin]: https://github.com/coe-marble/rpp_docs/blob/develop/docs/glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
