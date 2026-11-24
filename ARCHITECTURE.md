# Module ownership

The CLI remains `scripts/unreal_bp.py`; its public `UnrealLibrary`, `UnrealMCPError`, `COMMANDS` and `parse_commands` imports remain available.

| File | Responsibility |
| --- | --- |
| `scripts/unreal_bp.py` | CLI arguments, output and exit codes |
| `scripts/commands.py` | Syntax templates and parsing |
| `scripts/library.py` | Public library and serial command dispatch |
| `scripts/context.py` | Per-run asset/Blueprint/graph selection, aliases and pin resolution |
| `scripts/transport.py` | MCP session, schemas and RPC calls |
| `scripts/blueprints.py` | Blueprint lookup, maps and graph commands |
| `scripts/assets.py` | Factory catalog and asset commands |
| `scripts/dependencies.py` | Live editor dependency verification |
| `scripts/install_editor.py` | Deploy editor files and preserve startup import |
| `scripts/console.py` | CLI access to the installed Python console |
| `editor/unreal_bp_console.py` | Native Unreal Python execution and result/log handling |
| `scripts/errors.py` | Shared command-library error |
| `editor/unreal_bp_assets.py` | Unreal factory discovery, option validation and creation |
| `editor/creation_rules.json` | Reviewed factories and required/allowed creation options |
| `editor/UnrealBPBridge` | Editor-only C++ dependency: typed Anim Composite factory configuration |

Data flow: CLI → parser → one managed command_batch MCP call → the same serial dispatcher and BP/asset/Material handlers inside Unreal → existing ToolsetRegistry. The scripts are a Python package, deployed unchanged as unreal_bp_runtime by the existing dependency installer. EditorCommandLibrary changes only the transport boundary; it uses the same schema and return-value handling as UnrealTransport. One command context owns selections throughout the command file. Editor creation validates live property types and dependency references before invoking the existing factory helper.

Creation rules are configuration, not a second asset database. Unreal still supplies factory metadata and property schemas. Discovery alone does not authorize creation. The editor Python files and JSON rules participate in the existing dependency hash; changing either requires deploying and reloading the module. Missing installed files mean the dependency is incomplete; a missing or invalid rules file during module loading fails explicitly.

The existing dependency installer also deploys bundled native source to `Plugins/UnrealBPBridge`. Build the project's editor target with its matching engine. The plugin is enabled by default. First installation may require an editor restart because a running module manager does not know newly added plugin directories. Do not restart automatically. `ready` still describes the Python dependency; `native_ready` separately requires deployed native source and the loaded protocol version. Native behavior changes must increment both the C++ protocol version and the Python expected version. Copying source does not update a loaded binary.

AnimCompositeFactory requires `targetSkeleton`. Python reads its full reflected schema and validates the reference, then the bridge assigns that typed factory field. The existing asset helper still creates the asset. No generic protected-property writer or additional MCP server is introduced. The catalog disables this factory when the bridge is absent or its version differs. Creation currently produces an empty composite; animation segments are not configured.

Protocol 2 adds the native Data Asset class picker validation. Protocol 1 remains sufficient for Anim Composite; Python reports per-factory native requirements and does not enable DataAssetFactory on protocol 1. The rule's optional `required_console_bool` is evaluated in the catalog and again immediately before creation; a missing/disabled cvar causes explicit failure. The plugin never changes that setting implicitly. PoseAsset source skeleton validation runs before creating the factory asset.

Native updates must use the project's editor target with `-NoHotReloadFromIDE`. A successful hot-reload link can produce a suffixed binary without updating `UnrealEditor.modules`; restarting then loads the old version. Verify the plugin module manifest points to the normal binary after the build. UE 5.8 Mac was verified to relink `libUnrealEditor-UnrealBPBridge.dylib` and regenerate metadata with this flag. An already running editor still requires activation/restart; do not equate the on-disk build with the loaded protocol.

Protocol 3 adds typed PreviewMeshCollectionFactory.CurrentSkeleton assignment. The rule requires a live Skeleton reference before native configuration. Protocol requirements are per operation: Composite >=1, Data Asset >=2, Preview Mesh Collection >=3 (currently supported versions 1–3). Existing operations remain available while a newer optional operation awaits native activation.

Global batches preserve selection and aliases across calls; Material cache and dependency checks are refreshed at each batch boundary. Per-line records return with the batch result; the first command error stops execution without rollback. Prepared files must end before any decision requiring inspection of results. Dependency hashing includes every deployed command module and reloads those modules before the editor toolset.

Niagara command routing lives in `scripts/niagara.py` and uses the existing engine NiagaraToolsets through the same transport/registry. Live schemas own tool availability and typed arguments; no native Niagara implementation or copied parameter model is added. The parser exposes tool/schema discovery, explicit native calls, system selection/summary and compile/issue inspection. The shared dependency installer hashes, deploys and reloads this module. Async compile/issue/fix tools form explicit MCP dispatch boundaries between otherwise unchanged managed command batches; context and source line numbers are retained. Native bridge protocol remains unchanged.
