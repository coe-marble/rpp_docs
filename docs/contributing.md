# Contributing documentation

`rpp_docs` owns RPP user and developer documentation: architecture, public API
usage, setup, tutorials, benchmarks, integration workflows, and design records.
Implementation repositories keep concise README entry points linking here.

## Where to document a change

- Update the central guide when public behavior or an API changes, including
  package-specific usage. Avoid maintaining the same guide in a package README.
- Keep executable examples, schemas, fixtures, and source API comments beside
  code. Link to them from the guide rather than copying whole implementations.
- Add an inventory entry when an implementation submodule is added or renamed.
- Leave links at former guide locations when moving documentation.
- Label historical plans and checkpoint results explicitly; current guides
  describe the implementation in the supported integration checkout.

## Links and commands

Relative links work in the `rpp_dev/rpp_docs` integration layout, including links
into sibling source repositories. Package READMEs also provide a GitHub docs link
for readers browsing a source repository on its own. Preserve old guide paths
as short pointers when useful for existing links.

State the working directory, Python environment, ROS overlay, and registry home
required by command examples. Distinguish preparation/build instructions from
measurements and distinguish implementation status from verified results.
Review examples against current source APIs; older package prose may lag.

## Review

Review local links and Markdown changes. The existing documentation link CI
checks the integration layout. When permitted by the task, the dependency-free
inventory checker can be run from `rpp_docs`:

```bash
python3 tools/check_repositories.py --workspace ..
```

It checks that catalog paths exist; it does not establish API correctness or
runtime validation. Follow task-specific restrictions on tests/builds and report
what was actually checked.

## Coordinated changes

Commit source README changes in their owning repositories and documentation
changes in `rpp_docs`; then update the `rpp_dev` submodule revisions together.
Record compatibility constraints where generators, runtimes, and compiled
artifacts must move together. Keep migration and regeneration instructions
current when a public protocol or generated interface changes.
