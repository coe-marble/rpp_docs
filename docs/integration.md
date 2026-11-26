# Integration checkout and CI

`rpp_dev` pins the RPP source repositories as submodules. See
[installation](getting-started.md) and the [repository catalog](repositories.md)
for checkout and package responsibilities. Submodule changes are committed in
the owning repository before the integration gitlink can pin that revision.

## Continuous integration

`rpp_dev` aggregates the existing CI results of its pinned submodule commits.
Its **Submodule CI** workflow runs on pushes and pull requests to `main` and
`develop`, and can also be started manually. It does not build packages or
rerun their tests.

The job uses the `delayed-ci` environment. In **Settings → Environments →
delayed-ci**, enable a **10-minute wait timer**. GitHub holds the job before
allocating a runner, so this delay does not consume runner minutes. The timer
is configured in repository settings, not in the workflow YAML.

For every submodule in the committed `.gitmodules`, including documentation,
the workflow checks the latest `ci.yml` run for the exact recorded commit.
All must already have finished with `success`. Each submodule is checked once;
the job exits immediately after collecting the results, without sleeping or
polling. Missing or unfinished runs are reported as pending and cause a
nonzero exit code. Failed, cancelled, skipped, or inaccessible runs also do
not pass. The job summary links each pinned commit and its CI result. After
the submodule workflows finish, rerun **Submodule CI** to refresh the result.

For private repositories, configure an `RPP_CI_TOKEN` repository secret with
**Actions: read** access to every submodule repository. A fine-grained personal
access token or GitHub App token can provide this permission. The default
`GITHUB_TOKEN` only has access to `rpp_dev`; it cannot read private submodules.
[Component][glossary-component] workflows may also require **Contents: read** for their existing
cross-repository checkouts. Branch protection should require the **Submodule
CI** job instead of the former integration-test job.

From the `rpp_dev` checkout, run the same check with a suitable token in `GH_TOKEN`:

```bash
python3 .github/scripts/submodule_ci.py
```

The checker uses only Python's standard library. Its own regression tests run
without GitHub access:

```bash
python3 -m unittest discover -s .github/scripts -p 'test_*.py'
```

## Design history

The [design-history index](plans/README.md) links lifecycle proposals and
checkpoint evidence. Their old APIs and test results do not describe every
current revision; the [current status](status.md) and guides take precedence.

[glossary-component]: glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
