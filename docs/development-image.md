# Developing with the Docker image

This image is the recommended way to run the `rpp_demos` tutorials. It includes
all six tutorials, their example library, the installed RPP runtime, and the
native tools used during registration.

The image contains a fully configured and installed RPP workspace. To make its
sources editable, copy the complete workspace from a stopped container and
bind-mount it back at exactly the same path. This preserves the generated
`build/` and `install/` directories and keeps the RPP library registrations
valid.

Container filesystem changes are lost when a container is removed, so temporary development containers should not be the only copy of your work. To make the workspace persistent, export its configured files to the host once. Bind-mount that host copy back at the same path whenever you start a development container.

## 1. Obtain the image

The development image tag is `ghcr.io/coe-marble/rpp-dev:lyrical`:

```bash
docker pull ghcr.io/coe-marble/rpp-dev:lyrical
```

Alternatively, from the `rpp_dev` checkout, build a local image:

```bash
./docker/dev_img/build.sh
```

The build script defaults to `ghcr.io/coe-marble/rpp-dev:lyrical`. Set
`IMAGE_TAG` before running the script to use a different tag.

## Run the tutorials

For a tutorial session, start a temporary container with the included sources:

```bash
docker run --rm -it \
    --env RPP_CPP_CORE_PATH=/workspaces/rpp/ros2_ws/install/rpp_cpp/lib \
    --workdir /workspaces/rpp/ros2_ws/src/rpp_dev/src/rpp_demos \
    ghcr.io/coe-marble/rpp-dev:lyrical
```

Inside the container, read
[Tutorial 01](https://github.com/coe-marble/rpp_docs/blob/develop/docs/tutorials/01_plugin_types_and_plugins.md)
and follow [Tutorial 02's CLI registration steps](https://github.com/coe-marble/rpp_docs/blob/develop/docs/tutorials/02_registration.md).
Those two tutorials have no Python drivers. After registration, run the API
examples in separate Python processes:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"

python3 tutorials/03_configuration/run.py
python3 tutorials/04_loading/run.py
python3 tutorials/05_lifecycle/run.py
python3 tutorials/06_scripts/run.py
```

The shell sources the installed ROS and RPP workspace automatically.
`RPP_CPP_CORE_PATH` lets registration find the native runtime even though each
tutorial uses the selected RPP home and keeps its files under
`$RPP_HOME/tutorials`.
See the [tutorial guide](tutorials/README.md) for the learning path
and expected results. To keep source edits, use the exported workspace below.

## Run the GUIs from a container

`rpp pm` and `rpp ws --root ...` need access to a graphical display. The basic
container command above provides a terminal session. For a local Linux desktop
using X11 or XWayland, pass the desktop's `DISPLAY`, X11 socket, and an
authorization cookie into the container.

Run the following on the **desktop host**, where `DISPLAY` is already set and
the `xauth` command is available. The image user's UID must match the desktop
user's UID so it can read the cookie file; the image defaults to UID `1000`.

```bash
# Export the current display cookie in a form usable with the container hostname.
rpp_xauth_file="$(mktemp /tmp/rpp-xauth.XXXXXX)"
xauth nlist "$DISPLAY" | sed 's/^..../ffff/' | xauth -f "$rpp_xauth_file" nmerge -

docker run --rm -it \
    --env DISPLAY \
    --env QT_QPA_PLATFORM=xcb \
    --env XAUTHORITY=/tmp/rpp.xauth \
    --env RPP_CPP_CORE_PATH=/workspaces/rpp/ros2_ws/install/rpp_cpp/lib \
    --mount type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,readonly \
    --mount "type=bind,src=$rpp_xauth_file,dst=/tmp/rpp.xauth,readonly" \
    --workdir /workspaces/rpp/ros2_ws/src/rpp_dev/src/rpp_demos \
    ghcr.io/coe-marble/rpp-dev:lyrical

# Remove the temporary cookie after leaving the container.
rm -f "$rpp_xauth_file"
```

Inside this container, select `RPP_HOME` and follow the tutorial registration
steps before launching `rpp pm` or opening the configured workspace. To retain
existing tutorial files, use the same persistent mounts as your development
session.

If Qt reports `could not connect to display`, check that the host has a running
desktop session and that `DISPLAY`, the socket mount, and the authorization
cookie are available inside the container. An empty `DISPLAY` indicates that
the terminal session has no display selected. A remote or headless Docker host
needs a graphical session or display forwarding before these GUI commands can
open visible windows.

## 2. Export the configured workspace

Run these commands from an empty development directory on the host:

```bash
docker create --name rpp-dev-export ghcr.io/coe-marble/rpp-dev:lyrical
docker cp rpp-dev-export:/workspaces/rpp/ros2_ws ./ros2_ws
docker rm rpp-dev-export
```

`docker create` makes a stopped container only; it does not start the image.
The copy includes the source repositories and the workspace's `build/`,
`install/`, and `log/` directories.

## 3. Develop using the exported workspace

```bash
docker run --rm -it \
    --mount type=bind,src="$(pwd)/ros2_ws",dst=/workspaces/rpp/ros2_ws \
    --workdir /workspaces/rpp/ros2_ws \
    ghcr.io/coe-marble/rpp-dev:lyrical
```

The bind mount replaces the image's workspace with the host copy at the same
absolute path. RPP's existing editable installs and library registrations
therefore remain valid, while source changes are made directly on the host.

After changing C++ sources, rebuild from inside the container and re-source
the workspace:

```bash
colcon build --symlink-install --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```
