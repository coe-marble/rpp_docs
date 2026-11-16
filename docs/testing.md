# Shared testing support

A Python package that installs testing data for RPP. Its fixture files are
declared as package data, so wheels and source distributions retain them.
This package is used by the other packages in a way that allows them to run tests without having to include the testing data in their own repositories. The testing data is stored in a separate repository and is installed as a package dependency.

Source fixtures and helper scripts live in
[`rpp_testing`](../../src/rpp_testing). See the [test image](test-image.md)
and [integration CI](integration.md) for the shared development infrastructure.

## Precompiled fixture

[`scripts/build_rpp_autogen.sh`](../../src/rpp_testing/scripts/build_rpp_autogen.sh) creates `rpp_testing/rpp_autogen/.rpp`,
including generated interfaces and precompiled fixture plugins. It is intended
for the manually triggered fixture publishing workflow. `rpp_cpp` consumes
this directory directly; it does not generate or download test artifacts. The
script clones `rpp_dev`, builds it with tests disabled, and runs the existing
RPP test-fixture setup.

Configure the source revision and output location with `RPP_DEV_REF` and
`RPP_AUTOGEN_DIR` respectively.

Pass `--local` to reuse the already-built ROS workspace containing this
checkout of `rpp_testing`; this skips both the clone and the build.

## Fixture layout


`example_plugins` contains a set of simple testing plugin implementations. These plugins are installed in the
testing rpp system from rpp_cli/testing module. The plugins are used to test the functionality of the rpp system and to provide examples of how to implement plugins.
`complex_plugins` contains a set of more complex testing plugin implementations. They are not automatically installed in the testing rpp system, but can be used to test the functionality of the rpp system and to provide examples of how to implement plugins.
`mock_workspaces` contains a set of mock workspaces that can be used to test the functionality of the rpp system and to provide examples of how to implement workspaces.
`test_component_cpp` contains a component that implements a simple C++ plugin.
`test_component_py` contains a component that implements a simple Python plugin.
`test_libs` contains a set of testing libraries
