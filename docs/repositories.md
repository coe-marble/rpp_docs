# Repository catalog

The integration repository pins the implementation repositories as git
submodules under `src`. This page is the human-readable view of
[`repositories.yml`](repositories.yml), which is the machine-checkable source
of truth for the inventory.

| Repository | Responsibility | Main entry point |
| --- | --- | --- |
| `rpp_cli` | User-facing command line operations | `rpp` |
| `rpp_common` | Shared contracts and data models | Python/C++ imports |
| `rpp_orchestrator` | Workspaces, components, scripts, GUI | `rpp ws` |
| `rpp_plugin_registrator` | Libraries, registry, validation, interfaces | `rpp pm` and registry commands |
| `rpp_py` | Python loading and component server | `rpp_component_server_python` |
| `rpp_cpp` | C++ runtime and component server | `rpp_component_server_cpp` |
| `rpp_testing` | Shared fixtures and test implementations | test support package |

## Ownership rule

Package-specific implementation details belong in the corresponding source
repository. System behavior, terminology, cross-package assumptions, setup
instructions, and integration decisions belong in `rpp_docs`.