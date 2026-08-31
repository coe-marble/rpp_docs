# Installation and first run

## Prerequisites

- Git with submodule support
- Python 3 and `pip`
- CMake, a C++17 compiler, Cap'n Proto, and `colcon` for C++ support
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

Python-only users can skip this step. For C++ components, build from the
integration workspace after the Python packages have been installed:

```bash
colcon build --symlink-install
source install/setup.bash
```

The C++ package uses ROS 2 logging when `rclcpp` is available; otherwise it
falls back to `spdlog`.

## ROS 2 mode

Source the ROS 2 environment in the same shell that launches RPP. Then enable
ROS 2 compilation in the global RPP configuration:

```bash
rpp registry config USE_ROS2_COMPILATION=True
```

Inspect the active configuration with:

```bash
rpp registry config
```

## Launch the tools

```bash
rpp pm                 # plugin manager
rpp ws                 # workspace GUI
rpp ws create demo /tmp
```