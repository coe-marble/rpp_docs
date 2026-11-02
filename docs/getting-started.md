# Installation and first run

## Prerequisites

- Git with submodule support
- Python 3 and `pip`
- CMake, a C++17 compiler, Cap'n Proto, pybind11, and `spdlog` for C++ support
- `colcon` when building the C++ runtime through a ROS 2 workspace
- ROS 2 only when ROS 2 logging or ROS 2 integration is required

## Install the development checkout

From the `rpp_dev` repository:

```bash
git submodule update --init --recursive
./setup.sh
```

The setup script installs the Python submodules in editable mode and runs
`rpp init-home`. Editable installs mean that changes in a submodule are visible
without reinstalling the package.

## Build the C++ runtime

Python-only users can skip this step. A standalone CMake build is sufficient
for C++ components after the Python packages have been installed:

```bash
cmake -S src/rpp_cpp -B build/rpp_cpp
cmake --build build/rpp_cpp
```

The C++ package uses ROS 2 logging when `rclcpp` is available; otherwise it
falls back to `spdlog`. In a ROS 2 workspace, `colcon build --symlink-install`
remains supported; source `install/setup.bash` afterwards.

## ROS 2 mode

Source the ROS 2 environment in the same shell that launches RPP. Then enable
ROS 2 compilation in the global RPP configuration:

```bash
rpp registry config set USE_ROS2_COMPILATION true
```

Inspect the active configuration with:

```bash
rpp registry config
```

## Launch the tools

```bash
rpp pm                 # plugin manager
rpp ws                 # workspace GUI
rpp library create demo
rpp ws create demo
```
