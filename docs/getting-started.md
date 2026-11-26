# Installation and first run

## Recommended tutorial environment

Use the `rpp_dev` [development image](development-image.md) for the
[tutorials](tutorials/README.md). It includes their sources, editable RPP packages,
ROS 2 Lyrical, and native registration tools. The image guide explains temporary
sessions and exporting a persistent workspace for development.

The instructions below install a source checkout on the host instead. Commands
start in the `rpp_dev` repository unless another directory is stated.

## Prerequisites

- Git with access to the submodule repositories.
- Python 3.10 or newer, `pip`, and `venv`.
- A native development toolchain: CMake, a C++17 compiler, Python development
  headers, pybind11, nlohmann-json, GDB, and either ROS 2 logging or `spdlog`.
- Cap'n Proto **1.1.0**. The development setup pins `capnproto=1.1.0-2.1` and
  `libcapnp-dev=1.1.0-2.1`; C++ generated sources require the matching release.
- Qt Python bindings (`python3-pyqt6`) for the GUIs.
- ROS 2 and `colcon` for ROS integration; ROS itself is optional for native RPP.

Registration can generate and compile native supporting artifacts even for
Python [plugins][glossary-plugin]. A Python-only application may still need these native tools.

## Install the development checkout

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
./setup.sh
```

`setup.sh` requires an active virtual environment. It installs its pinned system
packages using `sudo`, initializes submodules recursively, and installs Python
packages editable with their declared dependencies. `--system-site-packages`
keeps system-provided Qt and ROS modules available. On a machine where system
packages and submodules are already prepared, `./setup.sh --install` performs
only Python dependency/package installation.

Setup does not initialize the RPP home. Prepare the native runtime before
initialization/registration so generated libraries can locate it.

## Build the C++ runtime

A standalone build from the checkout:

```bash
cmake -S src/rpp_cpp -B build/rpp_cpp -DBUILD_TESTING=OFF
cmake --build build/rpp_cpp
export RPP_CPP_CORE_PATH="$(pwd)/build/rpp_cpp"
rpp init-home
```

`RPP_CPP_CORE_PATH` selects the directory containing the built RPP shared
libraries. The same setting can be persisted using
`rpp registry config set RPP_CPP_CORE_PATH /absolute/path/to/build/rpp_cpp`.
CMake uses `rclcpp` logging when available and `spdlog` otherwise.

For a ROS 2 workspace, activate the Python environment and source ROS in the
same shell, then build from the workspace root containing `src/rpp_dev`:

```bash
source /opt/ros/lyrical/setup.bash
colcon build --base-paths src/rpp_dev/src --packages-up-to rpp_cpp \
    --symlink-install --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export RPP_USE_ROS2_COMPILATION=true
rpp init-home
rpp registry config set USE_ROS2_COMPILATION true
```

The environment setting enables ROS lookup during first initialization; the
registry setting persists it. Keep the overlay sourced whenever launching RPP.
Build `rpp_ros2` through ament/colcon when using its
[slot services and status topics](ros2-integration.md).

## Launch the tools

```bash
rpp pm                 # plugin manager GUI
rpp ws                 # workspace GUI
rpp library create demo
rpp ws create demo
```

See [workflows](workflows.md) for registering libraries and composing [components][glossary-component],
and [CLI](cli.md) for command arguments. Select an isolated registry using
`RPP_HOME` or `rpp --rpp-home DIRECTORY ...` before loading RPP modules.

## Upgrade an existing installation

Update the source packages and matching native runtime, then follow
[registry migration](registry.md#upgrade-an-existing-registry). Regenerate
interfaces/adapters and rebuild downstream C++ artifacts together.
`rpp init-home --override` resets installed library registrations; use migration
when preserving an existing registry.

[glossary-plugin]: glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
