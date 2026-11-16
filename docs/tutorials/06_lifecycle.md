# Tutorial 6 Lifecycle management

## Prerequisites

Follow the [shared prerequisites](https://github.com/coe-marble/rpp_docs/blob/develop/docs/tutorials/README.md#prerequisites-and-execution) to prepare your RPP environment.
In the shell where you will run this tutorial, select and initialize its home:

```bash
export RPP_HOME="$HOME/.rpp_tutorials"
rpp init-home
```

Run the commands below from `rpp_dev/src/rpp_demos`, using that same shell.
The driver prepares the registrations and components it needs, so it can run
independently of the other tutorials.

## Description

Follow runtime lifecycle transitions, recover from invalid configuration, and close runtime resources.

The runtime owns transitions; the plugin owns its coefficients and active flag.
[run.py](https://github.com/coe-marble/rpp_demos/blob/develop/tutorials/06_lifecycle/run.py) uses the public runtime handle to exercise both.

## Implementation

### Run the example

```bash
python3 tutorials/06_lifecycle/run.py
```

The successful path is:

```text
UNCONFIGURED -> configure -> INACTIVE -> activate -> ACTIVE
ACTIVE -> deactivate -> INACTIVE -> activate -> ACTIVE
ACTIVE -> deactivate -> INACTIVE -> cleanup -> UNCONFIGURED
```

Each transition prints its result and `context.is_active()`. Look for
`active = 7` and `reactivated = 7`. This processor is stateless: reactivation
retains configured coefficients and carries no estimate or history. Calls
before activation and after deactivation fail with `processor is inactive`,
including through a retained native reference.

Activation before configuration is rejected. Another component fails
configuration because of an invalid gain and enters `ERROR`; activation is
rejected there too. Cleanup returns it to `UNCONFIGURED`. The driver closes it,
corrects the saved settings, and constructs a new runtime to read them.
Look for `recovered = 7`.

Finally, a non-finite input causes an invocation error. A `finally` block
closes the recovered runtime, deactivating it and clearing its configuration.
The retained plugin reference then rejects calls. Invocation failure does not
automatically imply a lifecycle transition: the application owns shutdown.
All remaining runtimes close on exit. Tutorial sources, registry entries, and
workspace data remain in `RPP_HOME`.

### Inspect the result

After observing the transitions, inspect the component that recovered from
failed configuration:

```bash
workspace="$RPP_HOME/tutorials/06_lifecycle/workspace"

# Find the processor and recoverable components left by the driver.
rpp ws component list "$workspace"

# Inspect the recovered component's identity and corrected saved parameters.
rpp ws component info "$workspace" recoverable
rpp ws component parameter get "$workspace" recoverable

# Locate its component folder and parameter files for further inspection.
rpp ws component context "$workspace" recoverable
```

The corrected parameters should contain gain `2` and offset `1`, even though
the runtime has closed. Saved configuration survives shutdown; lifecycle state
belongs to the runtime created by the driver. Use its printed transitions to
observe that state, and rerun the driver to repeat the failure and recovery.
