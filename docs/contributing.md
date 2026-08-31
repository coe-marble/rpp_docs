# Contributing documentation

`rpp_docs` is the system-level documentation repository. It is intentionally
independent of the implementation submodules so that architecture and workflow
decisions can be reviewed in one place.

## Where to document a change

- Add or update a system guide here when behavior crosses repositories.
- Add a repository page or catalog entry when a submodule is added or renamed.
- Keep a submodule README focused on installation and package-local API details;
  link to the central guide for concepts and workflows.
- Update examples whenever a public command, path, or generated artifact changes.

## Review checklist

- Does the documentation name the owning repository?
- Are commands executable from a stated working directory?
- Are default paths such as `~/.rpp` and `.rppws` explicit?
- Does the guide distinguish metadata, source libraries, and workspace state?
- Has `python3 tools/check_repositories.py --workspace <rpp_dev>` passed?
- If a public workflow changed, has the relevant package README or root integration README pointed back to this guide?

## Versioning

The docs repository describes the supported integration model, not every
historical submodule revision. When compatibility depends on a particular
submodule commit or release, record that constraint in the guide and in the
integration repository's submodule update.