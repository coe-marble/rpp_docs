# Contributing documentation

`rpp_docs` owns RPP user and developer documentation: architecture, public API
usage, setup, tutorials, benchmarks, integration workflows, and design records.
Implementation repositories keep concise README entry points. Detailed package
runbooks can stay beside their launch/configuration sources and are linked from
the relevant guide.

## Where to document a change

- Update the topic's primary guide when public behavior or an API changes.
  Use the [documentation map](../README.md) to find it. Link from other pages
  rather than copying its explanation, signatures, or setup procedure.
- Keep executable examples, schemas, fixtures, and source API comments beside
  code. Link to them from the guide rather than copying whole implementations.
- Add an inventory entry when an implementation submodule is added or renamed.
- Leave links at former guide locations when moving documentation.
- Label historical plans and checkpoint results explicitly; current guides
  describe the implementation in the supported integration checkout.
- Update the repository catalog when adding or moving a package. Keep design
  discussions under [plans](plans/README.md).

## Links and commands

Use relative links between pages in this repository. For files in another
repository, link to that repository's actual GitHub URL and branch so the links
also work when browsing `rpp_docs` on its own. Preserve old guide paths as short
pointers when useful for existing links.

Explain the subject on the page, using concrete inputs, calls, and outputs.
Use links where an explanation connects to another topic or defines a glossary
term. Readers should not need to open several pages to understand one workflow.

## Glossary links

Link the first useful prose mention of [Plugin Type][glossary-plugin-type],
[Plugin][glossary-plugin], and [Component][glossary-component] on a page to the
[glossary](glossary.md). Avoid linking every repetition. Keep the original
capitalization and pluralization in the visible text. Use reference links with
short title text so readers can hover for a definition or click through:

```markdown
A [Plugin Type][glossary-plugin-type] defines the contract implemented by a
[Plugin][glossary-plugin]. A [Component][glossary-component] saves its configuration.

[glossary-plugin-type]: glossary.md#plugin-type "Plugin Type: a language-neutral contract implemented by plugins."
[glossary-plugin]: glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
```

Use relative glossary links inside rpp_docs and absolute glossary URLs in other
repositories. Do not add glossary markup inside code, commands, or identifiers.
Historical plans retain their original terminology.

## Command examples

Give readers the working directory and environment they need, then show the
command and what it does. Check names and arguments against the code.
For shared interfaces, compare methods and dimensions with the schema.
Describe existing behavior; leave guesses and suggested features out of usage
instructions. Keep complete method descriptions in one place and link to them.

## Review

Check that links lead to the intended page and that examples use the current
API. From `rpp_docs`, check the repository catalog with:

```bash
python3 tools/check_repositories.py --workspace ..
```

The checker reports catalog entries whose directories are missing. CI also
checks local Markdown links.

## Coordinated changes

Commit source README changes in their owning repositories and documentation
changes in `rpp_docs`; then update the `rpp_dev` submodule revisions together.
Record compatibility constraints where generators, runtimes, and compiled
artifacts must move together. Keep migration and regeneration instructions
current when a public protocol or generated interface changes.

[glossary-plugin-type]: glossary.md#plugin-type "Plugin Type: a language-neutral contract implemented by plugins."
[glossary-plugin]: glossary.md#plugin "Plugin: a concrete implementation of a Plugin Type."
[glossary-component]: glossary.md#component "Component: a saved plugin configuration with parameters and optional subcomponents."
