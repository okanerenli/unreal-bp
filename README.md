# Unreal BP

Blueprint and Material editing tools for AI-assisted workflows in Unreal Engine 5.8. Includes a Python command-line library, a Codex skill, and an editor-side C++ bridge for operations missing from the engine's exposed tools.

The library uses Unreal's existing local MCP server and ToolsetRegistry. It does not run a separate MCP server or provide an AI model.

## Compatibility

| Environment | Status |
| --- | --- |
| Unreal Engine 5.8.2 on macOS | Development and recorded validation environment |
| Windows / Linux | Not verified in this repository |
| Unreal Engine 5.7 and earlier | Not verified; required MCP/toolset APIs must be available |
| Unreal Engine 5.9 | Not supported by this release; prefer the engine's native toolsets and Blueprint Graph DSL |

This is a source release, with no prebuilt editor binaries. The current code depends on UE 5.8 Python toolset names and schemas; UE 5.9 moves many of these operations to native toolsets. Do not assume that changing the engine version makes this package compatible.

## Features

- Read whole Blueprints, individual graphs, or connected node flows, including pins, defaults, positions and links.
- Create and edit Blueprint functions, events, variables, parameters, dispatchers, nodes, connections and comments.
- Read and edit Material and Material Function graphs, compile them and inspect diagnostics.
- Edit Material Instance parameters with layer/blend association and index-aware identities.
- Discover reviewed asset factories, create assets, edit DataTables, user-defined structs and enums.
- Discover and call the engine's existing Niagara toolsets.
- Execute prepared command files through a shared editor-side batch, with explicit inspection, compilation and saving.

See the [command reference](skills/blueprint-map/references/commands.md) for supported syntax and operation-specific requirements. The [factory inventory](FACTORY_INVENTORY.md) contains historical development records, not a guarantee that every factory is available in every project. Project-specific names in the reference are examples; replace them with assets discovered in your project.

## Requirements

- Unreal Editor 5.8.2 and a local project.
- Python 3 on the host. The CLI uses the Python standard library; no pip dependencies are required.
- Unreal's Python Editor Script Plugin, Model Context Protocol, Toolset Registry, and relevant editor toolsets enabled. The All Toolsets plugin can enable the engine toolsets together.
- A running Unreal MCP endpoint at `http://127.0.0.1:8000/mcp`. This address is currently fixed in the transport.
- For bridge-backed operations, a working C++ editor build environment for your engine and platform. The bridge also declares StateTree and GameplayCameras plugin dependencies.

Only connect one editor at this endpoint and run one command invocation at a time.

## Setup

### 1. Get the source

```sh
git clone https://github.com/okanerenli/unreal-bp.git
```

Keep the entire repository together, including `.codex-plugin`, `scripts`, `skills`, and `editor`. Commands below use placeholder absolute paths; replace them with your checkout and Unreal project paths. Run them from your Unreal project directory.

### 2. Check the base connection

Open your project in Unreal Editor with the required plugins enabled and the MCP server running. Read an existing Blueprint:

```sh
python3 /absolute/path/unreal-bp/scripts/unreal_bp.py map /Game/Blueprints/BP_Example --graph EventGraph
```

Replace the asset path and graph name with real ones. This standalone read uses the engine's base tools and does not require the bundled runtime to be installed first.

### 3. Install the editor dependency

```sh
python3 /absolute/path/unreal-bp/scripts/unreal_bp.py dependencies --project /absolute/path/MyProject
```

The project directory must contain exactly one `.uproject` file. The installer:

- Copies the bundled Python modules and creation rules into `Content/Python`, including `unreal_bp_runtime`.
- Adds `import unreal_bp_assets` to `Content/Python/init_unreal.py`, preserving existing startup text.
- Copies the native bridge source into `Plugins/UnrealBPBridge`.

The command prints JSON. Exit code `2` with `ready: false` means activation is incomplete. When `disk_ready` is true, save the returned `load_code` string as a Python file, preserving actual newlines, and execute it in Unreal's Python console:

```python
exec(open('/absolute/path/load_unreal_bp.py', encoding='utf-8').read())
```

For updates where the bundled Python console tool is already loaded, that same file can be executed from the CLI:

```sh
python3 /absolute/path/unreal-bp/scripts/unreal_bp.py console python --file /absolute/path/load_unreal_bp.py
```

Verify activation:

```sh
python3 /absolute/path/unreal-bp/scripts/unreal_bp.py dependencies --project /absolute/path/MyProject --check
```

Require `ready: true` before running command files. This confirms the Python runtime, not the C++ bridge.

### 4. Build the native bridge

For the full feature set, build your project's Editor target with the matching Unreal Engine and `-NoHotReloadFromIDE`, then restart the editor. If the project has no C++ Editor target, create one through Unreal's normal C++ project workflow before building.

The installer copies source only; it does not compile or activate a native module. After building, verify the bridge's `UnrealEditor.modules` manifest refers to the normal binary rather than a hot-reload suffixed binary. Run the dependency check again and require `native_ready: true` for the complete current bridge (protocol 16).

Bridge requirements vary by operation. Material maps, output editing, diagnostics, identity-aware instance parameters, struct/enum editing, comments and some factories require native support. See the command reference for individual requirements.

### 5. Use with an AI agent

The repository includes a Codex plugin manifest at `.codex-plugin/plugin.json` and the [blueprint-map skill](skills/blueprint-map/SKILL.md). Use the skill instructions with your agent and keep its script paths pointed at this checkout. Cloning alone does not register the plugin in Codex or install its Unreal dependencies.

The CLI can also be used directly without Codex. AI service access is separate from this repository.

## Usage

List command syntax without connecting to Unreal:

```sh
python3 /absolute/path/unreal-bp/scripts/unreal_bp.py syntax
```

Read an asset's property schema:

```sh
python3 /absolute/path/unreal-bp/scripts/unreal_bp.py inspect /Game/Blueprints/BP_Example
```

For a first command-file read, save the following as `inspect.txt`, replacing the Blueprint path:

```text
target /Game/Blueprints/BP_Example
graph EventGraph
map graph
```

Run it after installing and verifying the shared runtime:

```sh
python3 /absolute/path/unreal-bp/scripts/unreal_bp.py run /absolute/path/inspect.txt
```

For prepared Material/Material Function construction, the existing batching option groups writes and defers intermediate reads:

```sh
python3 /absolute/path/unreal-bp/scripts/unreal_bp.py run /absolute/path/material_commands.txt --batch-material-writes
```

Follow the discovery and inspection boundaries in the command reference. Do not invent node identifiers, pin addresses or asset classes.

## Execution behavior

- Command files execute serially and stop at the first error. Earlier changes remain applied; batches do not roll back.
- Inspect the current asset after a failed or interrupted mutation. Do not blindly replay a whole command file.
- Compilation and saving are explicit commands.
- A read inside a command file does not pause for review. Split files when returned information determines the next edits.
- Node references and pin indices can change after reconstruction. Refresh before using stale references.
- The tools edit editor assets; they do not convert C++ or provide runtime execution tracing.

## Repository layout

| Path | Purpose |
| --- | --- |
| `.codex-plugin/` | Codex plugin metadata |
| `skills/blueprint-map/` | Agent instructions and command reference |
| `scripts/` | CLI, parser, transport and shared command handlers |
| `editor/` | Unreal Python toolset, creation rules and native bridge source |
| `ARCHITECTURE.md` | Module ownership and implementation notes |
| `FACTORY_INVENTORY.md` | Historical factory discovery and validation records |

## Issues

Report issues at [GitHub Issues](https://github.com/okanerenli/unreal-bp/issues). Include your exact engine version, operating system, command, error output and dependency status. Remove private project paths or content before posting. Compatibility beyond the environments listed above is not promised.

## License

The original code in this repository is available under the [MIT License](LICENSE). Unreal Engine and other third-party dependencies remain subject to their own licenses; they are not included in this repository.
