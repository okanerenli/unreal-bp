# Blueprint command reference

One command per line. Quote names and paths containing spaces. Blank lines and `#` comments are accepted. All syntax is parsed before contacting Unreal; runtime errors can leave earlier commands applied. `syntax` prints the accepted templates directly from the implementation.

## Shared execution

`run FILE` sends the prepared file in one `command_batch` MCP call after setup and dependency verification. No BP/Material-specific flag is needed for transport batching. The existing handlers run sequentially inside Unreal through ToolsetRegistry, including live pin resolution and existing readbacks. This requires the current managed Python dependency; it introduces no new native protocol requirement.

Batch start is printed immediately; per-line results arrive together when the editor returns. The first error stops later commands and returns completed records and the latest context. Earlier mutations remain applied. If transport fails, inspect live state before resuming; do not replay the file. Separate runs are required when discovery or inspection results determine subsequent commands. A read command inside a file does not pause execution for human/agent review. Compile and save remain explicit.

The existing `--batch-material-writes` option still enables its Material-specific grouping and deferred readback within the common batch; `--defer-material-reads` retains its meaning. Command modules are deployed from the same source as the CLI through the managed dependency, not reimplemented in an editor-only executor.

## Blueprint comments

Select a Blueprint and graph first. These commands use the shared batch executor; comment inspection/editing requires native bridge protocol 15.

```text
create comment text "Inventory checks" position 0,0 size 600,300 as note
create comment text "Validation flow" nodes check,branch padding 50 as group
list comments
inspect comment note
set comment note properties '{"text":"Inventory validation","width":700,"height":350,"color":{"r":0.15,"g":0.3,"b":0.6,"a":1}}'
position node note 100,100
set comment branch properties '{"text":"Reject invalid inventory","visible":true,"pinned":true}'
delete comment note
```

`nodes` is a comma-separated list of existing aliases or exact node paths in the selected graph. Wrapping uses Unreal's bounds calculation for K2 nodes; it does not accept comment boxes. Dimensions must be positive integers, padding nonnegative. `text`, `visible` and `pinned` apply to node comment bubbles as well as boxes. `width`, `height` and RGBA `color` apply only to boxes; color channels range from 0 to 1. Empty `text` clears a node's comment. Unspecified fields are preserved.

`list comments` reads only boxes in the selected graph. `inspect comment NODE` reads one box or node bubble, including its text, visibility and position; boxes also return size and color. A normal graph map does not include comment text. Deleting a box uses `delete comment` and does not delete enclosed nodes. Moving uses the existing node position operation; do not assume that it also moves enclosed nodes. Save explicitly after review.

## Target and graph

```text
target SpaceGovernorGI
graph EventGraph
map graph
```

Target resolution uses the same path as `map TARGET`. Graph commands require an explicit graph selection. Switching target or graph clears node aliases.

Choose the smallest required read scope. `map graph` reads only the selected function/event/macro graph and fails if none is selected. `map` explicitly retains the full Blueprint read, even when a graph is selected. Standalone CLI: `unreal_bp.py map TARGET --graph EXACT_GRAPH_NAME`; library: `library.blueprint_map(target, graph_name="ExactFunctionName")`. A missing graph fails; it never falls back to the full Blueprint. Both scopes return the same `blueprint`/`graphs` structure, with a single graph for a scoped read. Graph scope is applied before querying nodes, not by filtering a full map afterward. For one connected chain, use `get flow node NODE`; do not fetch a full Blueprint just to inspect one function.


## Planned Blueprint builds

Use the default global `run FILE` batch. Complete one function/graph through B1–B8 before building callers that depend on it. Reuse existing graphs, declarations and nodes; read only the affected graph (`map graph`) or connected flow. Full Blueprint maps are for whole-Blueprint questions.

1. **B1 / Plan and discover:** Identify the selected Blueprint/graph, required variables and function/dispatcher signatures, node aliases, constants and intended connections. Read the existing affected graph once. Gather missing node types with one deduplicated `inspect node_types` request, including declaring classes. Inspect its result in a separate run before writing the build commands. Preview pins are not placed-node addresses.
2. **B2 / Declare:** Create only missing variables, functions, dispatchers and signature parameters through existing commands. Finish dependencies before callers. Read changed signatures before placing dependent call nodes. Adding a member default may compile through its existing command; do not assume batching changes that behavior.
3. **B3 / Add:** Place all planned missing nodes for this phase with unique aliases and positions. Reuse exact returned references. Do not wire during node placement or request a graph map after every node.
4. **B4 / Configure:** Apply planned pin constants, Create Event function selections and dynamic-pin edits using supported commands. Constants require unconnected inputs. Where an earlier edit changes the pins needed by a later edit, end the run and inspect the affected graph before preparing the dependent command; never predict a reconstructed pin index. Do not invent unsupported node-property editing commands.
5. **B5 / Inspect:** Read one `map graph` after placement/configuration. End the run and inspect the returned actual pin names, directions, types, defaults and links before preparing the wiring phase. Reuse this result. Verify graph ownership and resolve any ambiguous pin names; do not guess.
6. **B6 / Connect:** Send the known connections together with existing bind/unbind commands. Pin resolution remains live inside each command; global batching does not freeze pin addresses or skip checks. When a connection reconstructs a node and makes later connections uncertain, split at that dependency and inspect again. Preserve unrelated links.
7. **B7 / Verify:** Read one affected `map graph` or smaller connected flow and compare all intended nodes, values and connections. Resolve confirmed mismatches before `compile`. Check compiler output and inspect the graph again after compilation if reconstruction affects the planned pins. A successful transport response or a void compile return is not proof of semantic correctness. For signature/function deletions, follow the separate caller/stale-reference workflow before compiling.
8. **B8 / Save:** Explicitly save the verified asset, then proceed to its caller. A failed batch leaves earlier edits applied: read its completed records and current graph, reconcile aliases, then send only remaining work. Never replay the complete creation batch.

A prepared file runs without review pauses. Keep discovery results, signature checks, B5 inspection and B7 verification in separate calls whenever they determine the next commands. For staged library runs, retain the same `CommandContext` to preserve selected graph and aliases. Across CLI processes, reselect the graph and use exact returned node references.

## Creation

`refresh node_types` requires a selected target and graph plus the current editor dependency. It invalidates the existing EditorToolset node-type cache for the selected Blueprint and rebuilds the selected graph through the same discovery path. It returns the count of cached type entries, including any duplicates in Unreal's discovery output. Other graphs of that Blueprint rebuild on their next lookup. Use it when newly created input actions or other external assets do not appear in `find node_types`; refresh does not change graph nodes or save assets, and is not an automatic invalidation policy. It uses EditorToolset's existing `_BlueprintCache`, so engine updates must preserve that API or fail explicitly.

Discover node types in the selected graph before creating unfamiliar nodes:

For a planned flow, collect the required types and inspect them together by default:

```text
inspect node_types '[{"type":"Input|EnhancedActionEvents|IA_Move"},{"type":"Math|Vector2D|BreakVector2D"},{"type":"Pawn|GetControlRotation","class":"/Script/Engine.Pawn"},{"type":"Pawn|Input|AddMovementInput"}]'
```

Requires the current editor dependency. Each entry requires `type` and accepts optional `class` as a full class object path. Results are existing NodeInfo records in request order, including real pin names, types and defaults. Actual type IDs in results may differ from discovery labels. References belong to temporary preview nodes and cannot be used for wiring. The editor executes probes serially within one tool call and removes each temporary node in a finally block; if Unreal returns a pre-existing event node, it restores that node's position and reads it without deleting it. All type/class entries are checked before probing; ambiguous types require an explicit class. No partial list is returned on failure. This does not introduce a persistent schema cache or change the binding executor. Deduplicate known requests by type/class and reuse the results during planning; only newly discovered needs or invalidated information justify another query. Single-type inspection remains available for isolated questions.

```text
find node_categories filter FlowControl
find node_types filter "Utilities|FlowControl|Sequence"
refresh node_types
inspect node_type "Utilities|FlowControl|Sequence"
```

These expose existing Unreal discovery tools. Filters are substrings, not exact matches; use a specific category/type prefix and inspect the returned candidates. Broad terms can produce very large results, so redirect output to a file. Results are returned unchanged, including any duplicates reported by Unreal. This version uses no context-pin filter. `inspect node_type` describes a type's pins; its returned preview node/pin references are not references to a placed graph node. Read map or command creation results for actual placed nodes.

```text
create bp name ExampleBP folder /Game/Examples parent /Script/Engine.Actor
graph EventGraph
create custom_event name Deneme position 100,200 as event1
create variable type int name WidgetIndex
create variable type int name StartIndex default 7
add node type "Development|PrintString" position 400,200 as print1
```

`create bp` selects the created Blueprint; its `parent` is a class object path, not a Blueprint asset path. Creation uses the current Unreal `BlueprintFactory` tool; do not assume every specialized asset factory is supported.

Custom events use `create_node` with `AddEvent|Custom|NAME`, not `add_event`'s inherited-event override behavior. Existing/inherited event names are rejected. Use a valid event graph. Aliases are scoped to this invocation and point to returned real node references.

Variable creation adds a member declaration, not a Get/Set node. Supported basic types are `bool`, `int`, `float`, `byte`, `string`, `name`, `text`, `Vector`, `Rotator`, `Transform`, `Vector2D`, `LinearColor`. Custom structs use `create variable type struct name Stats struct /Game/Data/ST_Stats.ST_Stats`, routed to the existing `add_struct_variable` tool. Struct variables support the same scope/container options; explicit defaults remain primitive-only. Existing names are rejected.

Object references and containers use the same declaration path:

```text
create variable type object class SpaceGovernorGI name GIRef
create variable type int container array name WidgetIndexes
create variable type int container set name UniqueWidgetIndexes
create variable type int container map name WidgetIndexByName
create variable type object class SpaceGovernorGI name GIRefs container array
```

`class` accepts a Blueprint asset name/path and resolves its actual generated class via the CDO; native class paths are not exposed here. The object reference is populated at runtime using a Set node connected to the cast result. Read it using the existing variable Get command and connect the reference to external Get/Set/Call `self` pins. Execute the assignment before consuming the reference.

Containers map to the existing tool's `ARRAY`, `SET`, `MAP` values. MAP keys are always strings with this Unreal tool; `type` specifies the map value type. Object and container declarations also accept `scope local` in a function graph. `container` may follow the name; do not repeat it. Explicit object/container defaults are rejected before execution. Unsupported element/key combinations remain Unreal errors.

Variable options follow the name, in any order: `scope member|local`, `container array|set|map` and `default VALUE`. Omitted scope means member. Explicit defaults currently support scalar primitives only: JSON numbers for int/byte/float, `true` or `false` for bool, literal quoted text for string/name/text. Member defaults are applied through the existing Class Defaults properties after compiling the newly declared variable. The result includes the read-back value. This compilation may fail and leave the declaration created; do not replay the command blindly.

```text
create function name DenemeFunction
create variable type int name LocalWidgetIndex scope local
```

`create function` creates and selects a new function graph, clearing node aliases. Existing or inherited function names are rejected rather than overridden. To work in an existing function, use `graph NAME`. Local creation requires a graph containing exactly one FunctionEntry node; EventGraph and macro graphs are rejected before variable creation. Local variables use the existing `add_variable` graph argument.

`scope local` combined with `default` is rejected during command-file parsing, before execution: the current Unreal tools do not expose local-variable defaults. No Set node is substituted. `delete variable` still targets members only; local deletion is not exposed by the command syntax yet.

`add node` requires an actual Unreal type ID; do not invent one from a display label. If a type has multiple declaring classes, use `add node type TYPE class /Script/Module.Class position X,Y as ALIAS` with a verified class object path. This passes the existing `declaring_class` argument to Unreal's node creation tool. For example, `add node type Pawn|GetControlRotation class /Script/Engine.Pawn position 0,0 as rotation` explicitly selects the Pawn function. Read the created node's actual target and pins before wiring; `inspect node_type` does not expose a declaring-class argument. If the correct declaring class is unknown, stop instead of choosing arbitrarily.

For existing member variables or locals in the selected function, use:

```text
add variable_get name WidgetIndex position 100,400 as indexGet
add variable_set name WidgetIndex position 400,200 as indexSet
bind indexGet::WidgetIndex to indexSet::WidgetIndex
```

These commands create graph nodes, not variable declarations. The library resolves the name against member variables and, for function graphs, locals; missing names or a member/local name collision raise an error. It searches Unreal's existing node types and requires exactly one `Variables|...|GetNAME` or `Variables|...|SetNAME` match. Inherited variables are not included by the current variable-list tool path. A Set node only performs an assignment when its `execute` pin is driven; connect the event/function's `then` output explicitly. Get/Set node creation does not change the variable's Class Default.

## Links and placement

### Blueprint components

Select an Actor Blueprint with `target`. `list components` returns its actual component templates, including inherited components. Use exact returned references with these commands; there is no separate component selection or cached property state:

```text
list components
create component name FirstPersonCamera class /Script/Engine.CameraComponent
inspect component COMPONENT_REF
get component_parent COMPONENT_REF
get component COMPONENT_REF properties '["relativeLocation","bUsePawnControlRotation"]'
set component COMPONENT_REF properties '{"relativeLocation":{"x":0,"y":0,"z":64},"bUsePawnControlRotation":true}'
compile
save
```

Replace COMPONENT_REF with a path from `list components`; the location is an example, not a character-specific default. Creation uses ActorTools.add_component with the selected Blueprint as owner. Scene components attach to its root through Unreal's existing SubobjectDataSubsystem path. Creation compiles internally; inspect the returned reference and refresh the list before subsequent edits. Do not assume a requested name is unique or blindly repeat creation after a failure.

Property operations use ObjectTools.list_properties → get_properties → set_properties and read back the result. Inspect schema and current values before deciding changes. Every operation re-enumerates the selected Blueprint's components and rejects references outside that list. Parent reads require a SceneComponent; null means it has no parent. Commands do not edit scene actor instances or introduce runtime Get Component nodes. Compile and save the Blueprint explicitly; re-list after structural edits or compilation instead of assuming template reference stability.

Dynamic pins on supported placed nodes (Sequence, Switch, Make Array, etc.):

```text
add pin node seq
remove pin seq::then_2 direction output
```

`add pin` returns the added PinID and freshly read node information. `remove pin` requires `input` or `output` to resolve the exact current named pin and returns the updated node information. Re-read after pin changes; indices and names may shift. Remove only the intended pin; removal may also remove its links. When preserving an explicit sequence of changes, unbind first. These commands do not edit macro tunnel signatures or function parameters; unsupported node kinds fail through Unreal's tool.

Branch, Sequence and existing macros such as Gate use the existing `add node type ...` path. Gate macro placement does not create a new macro definition. Inspect real pin names (`then_0`, `Condition`, `bStartClosed`, etc.) rather than using display labels.

Function parameters use the currently selected function graph:

```text
graph DenemeFunction
add function_input name Index type int
add function_output name Success type bool
add function_input name GI type object class SpaceGovernorGI
add function_input name Indexes type int container array
add function_input name Location type struct struct /Script/CoreUObject.Vector
```

These call the existing `add_function_param`, `add_object_function_param` or `add_struct_function_param` tool and return its real PinID. A function input appears as an output on FunctionEntry inside the function; a function output appears as an input on FunctionResult (Return). Use map to retrieve node references, then wire execution to Return and wire or set its result values. Compile the owning Blueprint, re-read affected call nodes, and connect their new inputs/outputs using fresh pin information. Parameters do not wire themselves. `function_input` and `function_output` require function graphs. Use `dispatcher_input` for dispatcher signatures; ordinary custom-event parameters are not handled by these commands. Supported types match basic variable types. Duplicate parameter names are handled as errors by Unreal's existing tool. Optional trailing options: `class BLUEPRINT` for `type object`, `struct /FULL/SCRIPTSTRUCT.OBJECT` for `type struct`, and `container array|set|map` for any type. Map keys are strings. Struct paths must identify an actual ScriptStruct; no name guessing is performed. Object classes use the existing Blueprint class resolver.

To call a function declared on another Blueprint and assign an input pin constant:

```text
add call name DenemeFunction owner SpaceGovernorGI position 900,200 as call1
set pin print1::InString value "Merhaba"
```

`add call` resolves the owner's function list, requires one exact class-qualified node type, and creates it using the actual `declaring_class`. Owner accepts a Blueprint name/asset path; native class paths and node titles that differ from the function identifier are not supported by this command. Wire its target (`self`) and exec pins explicitly using map. It creates a call node; it does not execute the function in the editor.

`set pin` resolves an input pin by its current name, rejects connected inputs, and uses `set_pin_value` followed by `get_pin_value` for read-back. Values use Unreal's pin text format: numeric `42`, boolean `true`, quoted strings, or an asset object path. The existing Unreal tool determines whether the pin supports defaults and whether its value is valid. This edits the node's literal input, not the variable's Class Default.

For an object cast and variables on another Blueprint instance:

```text
add cast class SpaceGovernorGI position 300,200 as giCast
add variable_get name WidgetIndex owner SpaceGovernorGI position 600,400 as indexGet
add variable_set name WidgetIndex owner SpaceGovernorGI position 900,200 as indexSet
```

`class` and `owner` currently accept Blueprint asset names or asset paths, not native class paths. The library resolves the Blueprint, gets its CDO and actual class reference, and passes that as `declaring_class` to the existing node creation tool. Cast selects the object-cast type, not the class-cast variant. External Get/Set resolves member variables on the owner and requires its exact class-qualified node type. Missing/ambiguous types fail; inherited variables and external local variables are not supported.

These commands do not wire automatically. Read the created node pins with map, then connect the source object to cast `Object`, the cast result to each external getter/setter `self`, and cast success `then` to the consuming executable node. Cast result pin names can contain spaces; quote the full pin address. Do not drive the consumer from `CastFailed`. Get/Set does not modify Class Defaults; the setter operates on the connected instance when executed.

```text
bind event1::then to print1::execute
unbind event1::then from print1::execute
position node event1 100,400
arrange nodes event1,print1 position 100,400
```

Node arguments accept either a local alias or the full `refPath` returned by map. Pin arguments use `NODE::PIN_NAME`; output and input direction come from the command. Each endpoint is resolved against freshly read node information. Missing or ambiguous pin names are errors. `bind` means a pin connection, not delegate-function binding. Unreal controls connection compatibility and may replace existing links according to its graph schema; inspect occupied endpoints before binding and verify the resulting map.

`arrange` places only the explicitly listed, distinct nodes left-to-right in the supplied order. Each node is treated as 200×200 with an 80-unit gap (X stride 280), starting at the given position. This is the user's chosen temporary layout convention, not a measured size. It does not infer execution order or avoid unrelated nodes; choose the order and a free origin using map. Intermediate successful positions are emitted individually.

## Deletion and finalization

```text
delete node print1
delete variable name WidgetIndex
compile
save
```

Deletion is explicit; `delete variable` removes the member declaration and is not the same as deleting a Get/Set node. Compilation affects the selected Blueprint; saving affects the selected asset (a Blueprint target or the most recently created asset). Save never passes an empty asset list (which would save all dirty assets). A compile error stops the file before a following save.

## Current tool mapping

| Command | Existing tool |
|---|---|
| target | AssetTools.find_assets → load_asset |
| find node_types / find node_categories | find_node_types / find_node_categories |
| inspect node_type | get_node_type_pins |
| add pin / remove pin | add_node_pin / remove_node_pin, followed by get_node_infos |
| graph / map | BlueprintTools.get_graph / list_graphs → find_nodes → get_node_infos |
| create bp | BlueprintTools.create |
| create function | BlueprintTools.add_function_graph |
| create custom_event / add node | BlueprintTools.create_node |
| add variable_get / add variable_set | list_variables → find_node_types → create_node |
| add cast / Get/Set owner | resolve Blueprint → get_default_object → ObjectTools.get_class → find_node_types → create_node with declaring_class |
| add call | list_functions → find_node_types → create_node with declaring_class |
| set pin | get_node_infos → set_pin_value → get_pin_value |
| add function_input / add function_output | add_function_param / add_object_function_param / add_struct_function_param with input_param true / false |
| create variable / delete variable | BlueprintTools.add_variable / remove_variable |
| create variable type object | resolve Blueprint class → add_object_variable |
| create variable container | add_variable / add_object_variable with container_type |
| create variable scope local | BlueprintTools.add_variable with selected function graph |
| create variable default | compile_blueprint → ObjectTools.list_properties → set_properties → get_properties (Class Defaults) |
| position / arrange | BlueprintTools.set_node_position |
| bind / unbind | BlueprintTools.connect_pins / break_pins |
| delete node | BlueprintTools.delete_node |
| compile | BlueprintTools.compile_blueprint |
| save | AssetTools.save_assets |


## Dispatchers and connected flow

```text
create dispatcher name WidgetChanged
add dispatcher_input name WidgetIndex type int
compile
list dispatchers
graph EventGraph
find node_types filter WidgetChanged
```

Creating a dispatcher selects its signature graph and clears node aliases. `dispatcher_input` uses the same primitive/object/struct/container parameter path as function inputs. Dispatcher outputs are unsupported. Existing names fail through Unreal.

Dispatcher Bind, Call, and Unbind nodes use the existing `add node type TYPE_ID position X,Y as ALIAS` command. Discover exact type IDs in the target graph; categories depend on the dispatcher. For example, the GI demo exposes `Default|BindEventtoDenemeWidgetChanged`, `Default|CallDenemeWidgetChanged`, and `Default|UnbindEventfromDenemeWidgetChanged`. Creating these nodes does not wire them. Use ordinary `bind` to connect execution, target, data, and delegate pins.

For an `EventDispatchers|CreateEvent` node, connect its delegate output to the dispatcher's Bind delegate input before choosing the handler:

```text
list event_functions node handler
set event_function node handler name DenemeWidgetChangedHandler
get flow node start
```

`set event_function` requires an exact name returned by `list event_functions`; it calls `set_create_event_function` and reads the binding back. A handler function must match the delegate signature.

`get flow node ALIAS_OR_NODE_PATH` calls `get_connected_subgraph` once and returns full node information for the connected component: node references/types/positions, pin names/types/defaults and links. Traversal follows all connections in both directions, including data and delegate links, with cycles visited once. Shared data sources may include other event chains. This is graph topology, not execution order, runtime pin values or an automatic error diagnosis. It does not expand function/macro bodies or follow dispatcher subscriptions into other graphs. A disconnected node cannot be discovered from this component; use `map` to inspect the whole Blueprint. Failed command files already identify the started line/action without a completed record; inspect current state before resuming.

## Deleting signatures and functions

```text
graph DenemeFunction
delete function_input name Index
delete function_output name Success
graph DenemeWidgetChanged
delete dispatcher_input name WidgetIndex
delete function name DenemeFunction
compile
map
save
```

Parameter deletion calls `remove_function_param` with the selected graph and explicit input/output direction. Use `dispatcher_input` only on dispatcher graphs; dispatcher outputs are unsupported. A missing parameter is an error. Re-read the signature and affected call nodes after deletion and compilation: Unreal owns pin reconstruction and may retain linked orphan pins requiring explicit cleanup. Do not assume deletion rewires the remaining flow.

`delete function name NAME` resolves a function graph on the selected Blueprint and calls `remove_function_graph`. It rejects dispatcher and non-function graphs. If the deleted graph was selected, graph selection and aliases are cleared; select another graph before node commands. Unreal's tool may close the open Blueprint editor. Call sites are not automatically removed by this command; inspect and explicitly remove or update affected calls. Compile and save remain explicit.


## Folder context and asset creation

```text
folder /Game/Examples
create material_function name MF_Example
save
create material name M_Example
save
find row_structs filter *Star*
create datatable name DT_Example row_struct /Script/SpaceGovernor.StarTypeRow
save
create bp name BP_Example parent /Script/Engine.Actor
compile
save
list assets
list folders
```

`folder PATH` selects an absolute Unreal content folder for this command file. It does not navigate the Content Browser, select an asset, or create an empty directory. Asset creation creates the destination as needed through its existing Unreal factory. `list assets` and `list folders` search recursively within the selected folder. These commands work without selecting a Blueprint. Folder context survives `target` and `graph` changes.

`create bp name NAME parent CLASS_PATH` uses the selected folder. The original `create bp name NAME folder PATH parent CLASS_PATH` remains supported; its explicit folder overrides context for that command only. `target` remains a Blueprint selector, not a generic material/table editor.

Material and Material Function creation call MaterialTools.create_material/create_function. DataTable creation calls DataTableTools.create with an exact row struct object reference returned by `find row_structs filter WILDCARD` (search_row_structs). The row struct must already exist and be supported as a table schema. The SpaceGovernor path above is project-specific. These commands create assets, not populated material graphs or table rows.

Each created asset becomes the `save` target. Creating a non-Blueprint asset clears the Blueprint, graph and aliases; Blueprint commands require selecting a Blueprint again. `save` saves only that asset, never all dirty assets. Save each asset before creating/selecting the next if it should be persisted. `compile` remains Blueprint-only.

New Struct assets are created through `create asset type StructureFactory name NAME` when the bundled editor toolset is installed. The shorthand `create struct` is not defined. Struct variables and struct function parameters still refer to existing types.


## Asset delete, move and copy

```text
get referencers asset /Game/Materials/M_Source
get dependencies asset /Game/Materials/M_Source
copy asset /Game/Materials/M_Source to /Game/Materials/M_Copy
save
move asset /Game/Materials/M_Copy to /Game/New/M_Copy
save
get referencers asset /Game/New/M_Copy
# Inspect the returned references before running deletion in a subsequent invocation.
delete asset /Game/New/M_Copy
```

These commands operate on one asset, not directories. Source paths are explicit Unreal asset/package paths and are resolved with load_asset before mutation; they are not relative to `folder`. Redirector source paths may resolve to the redirected asset: inspect the resolved source and use the intended current asset path. Destination paths include the new asset name, with package syntax `/Game/Folder/Name`. Existing destinations are rejected; there is no overwrite or force option.

`copy asset` maps to AssetTools.duplicate; `move asset` maps to AssetTools.move. Both load the destination afterward, select it for `save`, and clear BP graph context. Select a Blueprint again before graph edits. Move may leave Unreal redirectors; this command does not fix or delete them automatically. Copy is a normal duplicate, not dependency copying or Advanced Copy; references may still point to original dependencies.

`delete asset` maps to AssetTools.delete and verifies that the resolved asset path no longer exists. Deleting the selected asset clears asset/BP/graph selection and aliases. Tool false results are errors. Asset deletion is not rolled back by the command runner.

Before deletion, agents MUST read and inspect `get referencers asset PATH` and the relevant dependency context in a separate step, resolve affected references within the user's authorized task, and only then delete. The library does not automatically delete referencers or rewrite their contents. Registry results do not prove that all runtime or unsaved references have been found; report any known unresolved scope. After moving/copying, inspect returned addresses, save the intended assets explicitly, and verify affected references as appropriate.

Advanced Copy is not exposed by the current connected asset toolset and has no command yet. Implementing it requires a verified path for dependency selection and remapping copied references; looping over duplicate alone is not equivalent.


## Generic factory creation

Manage the bundled editor-side dependency from Codex:

```sh
python3 /absolute/plugin/path/scripts/unreal_bp.py dependencies --project /absolute/UnrealProject
python3 /absolute/plugin/path/scripts/unreal_bp.py dependencies --project /absolute/UnrealProject --check
```

The first command installs/updates only changed module content and a missing startup import using the existing `install_editor.py` path. It preserves other startup text. The second is read-only. Both inspect the connected editor; a known project mismatch fails before writing. A missing or legacy loaded module has no project handshake, so use the explicitly identified active project and require verification after loading.

JSON reports expected/disk hashes, startup state, runtime state and `ready`. Exit 0 with `ready: true` means the loaded module and installed files match this plugin and project. Exit 2 with `ready: false` means the dependency is not ready. For installed files needing activation, `load_code` contains the exact Python import/reload step for Codex to execute in Unreal, followed by another `--check`. The command does not automatically operate the console or start/restart Unreal. Missing base MCP/Python/ToolsetRegistry is an explicit blocker. The bundled skill owns this installation-and-verification workflow; there is no fictional marketplace dependency field.

The module runs through the project's existing `Content/Python/init_unreal.py` and ToolsetRegistry; there is no new HTTP server or engine C++ patch. The runtime reports a hash captured when imported, so updating a file alone cannot pass verification. A current dependency is not rewritten or reloaded. Generic factory commands reject missing/legacy/outdated runtime code; BP-only commands do not require the additional module. The lower-level installer remains available as `install_editor.py PROJECT [--check]` and returns JSON, but disk-only success is not runtime readiness.

```text
find asset_types filter StructureFactory
folder /Game/Data
create asset type StructureFactory name ST_Ships
save
create asset type DataTableFactory name DT_Ships options '{"struct":{"refPath":"/Game/Data/ST_Ships.ST_Ships"}}'
save
create asset type BlueprintFactory name BP_Ship options '{"parentClass":{"refPath":"/Script/Engine.Actor"}}'
compile
save
```

`type` accepts the exact factory class path, its exact short name, or an asset class path resolving to exactly one factory. Ambiguity is an error, not a selection heuristic. Options use JSON with exact keys exposed by the catalog and explicit object/class references. The created asset becomes the save target; BlueprintFactory also selects the new Blueprint, while other types clear graph context. Existing convenience commands retain their existing tools.

The catalog is discovered live, contains project and engine identity, and is cached only inside the current library process. `refresh asset_types` fetches it again; no catalog from another project/session is reused. Discovery reads reflected Factory defaults (`create_new`, `supported_class`); it is NOT the fully filtered Content Browser menu or a guarantee that every discovered class can run. `creation_supported` marks factories with reviewed configuration rules. Unknown factory requirements fail explicitly instead of guessing. Current rules cover StructureFactory, EnumFactory, MaterialFactoryNew, MaterialFunctionFactoryNew, BlueprintFactory (parentClass required), DataTableFactory (struct required), and AnimSequenceFactory (targetSkeleton required; previewSkeletalMesh optional). MaterialInstanceConstantFactoryNew accepts optional initialParent (MaterialInterface reference). This factory uses full property discovery for its reviewed initialParent option; supplied parents are validated before the existing MaterialInstanceTools.create operation creates and assigns the parent. The resulting parent is verified. Omitting initialParent creates an unparented instance. CurveFloatFactory, CurveVectorFactory and CurveLinearColorFactory need no options. Animation Sequence creation was live-verified with the project UE4 Mannequin skeleton; preview mesh configuration was not exercised.

The generic tool validates required/unknown option keys and resolves/type-checks dependencies before calling the existing Unreal CreateAsset helper. DataTable rows must be UserDefinedStruct or native TableRowBase descendants. Blueprint parent eligibility and other factory-specific semantic checks still belong to Unreal's factory. Options are applied to a transient factory, never the shared factory default object. No missing dependency is created implicitly; assets are not overwritten or automatically saved.

Commands execute in source order. Create a dependency before its consumer and read returned canonical paths. This is per-command validation, not an all-file dependency planner or transaction: earlier successful commands remain when a later command fails. A newly created Struct has Unreal's factory defaults; use `edit struct` below to edit its fields.

### DataTable rows

Select an existing DataTable by exact asset path, or use the existing creation commands. Selection returns its schema and clears Blueprint/graph aliases. All row operations use `DataTableTools` and the global command batch; no additional native bridge version is needed.

```text
datatable /Game/Data/DT_Items
list datatable_rows
get datatable_rows '["ItemA","ItemB"]'
```

Read the returned schema before preparing writes; `get datatable_schema` reads it again if needed. Use exact row names and schema property names. Example writes (replace `price` with an actual schema property):

```text
add datatable_rows '["ItemA","ItemB"]'
set datatable_rows '{"ItemA":{"price":10},"ItemB":{"price":20}}'
get datatable_rows '["ItemA","ItemB"]'
rename datatable_rows '{"ItemA":"ItemC"}'
delete datatable_rows '["ItemB"]'
save
```

Add creates rows with struct defaults and rejects existing names; set updates existing rows only and preserves unmentioned fields. Rename takes an old-to-new name object; remove takes row names. Missing rows and name collisions are checked by the existing Unreal tools. Names and inputs must be nonempty; use the exact canonical names returned by list rows. Read results explicitly to verify edits before saving. No implicit save, upsert or rollback: a failed set after add leaves the added rows in place. Before deletion/rename, inspect known row-handle and name-based consumers; these tools do not rewrite external references.

Performance boundary: Unreal's current `get_rows` exports the whole table internally, even though it returns only requested rows. Add/set/rename export and refill the table through JSON. Remove calls Unreal's row deletion operation for each requested name. Global batching removes per-command MCP round trips; it does not change these engine operations or make the file atomic.

### Enum entries

Requires the current editor dependency and native bridge protocol 16. These operations edit UserDefinedEnum assets, not native C++ enums. Create an Enum asset through the existing EnumFactory catalog path if needed, then read its entries:

```text
get enum_entries asset /Game/Enums/E_State
add enum_entries asset /Game/Enums/E_State names '["Idle","Walking","Running"]'
save
```

Readback returns each entry's `id`, `display_name` and current numeric `value`; the generated MAX sentinel is excluded. Add appends new display names. Rename and delete use exact `id` values from readback, never array indexes or display names. For example, if readback reports `NewEnumerator0` and `NewEnumerator2`:

```text
rename enum_entries asset /Game/Enums/E_State names '{"NewEnumerator0":"Resting"}'
delete enum_entries asset /Game/Enums/E_State ids '["NewEnumerator2"]'
save
```

Rename changes the display name through Unreal's EnumEditorUtils and preserves the internal id. Invalid/duplicate display names and missing ids fail explicitly. Each command supports multiple entries in one global batch; entries execute in input order and earlier edits remain applied if a later edit fails. Renames are sequential, so swapping two occupied names requires an explicit unused intermediate name. Inspect current entries after failure before resuming. Successful writes select the enum for explicit `save` and clear Blueprint context; reads preserve selection.

Before deleting entries, inspect asset referencers and affected Blueprint enum literals, switches, struct defaults and DataTable values. Unreal performs its usual enum-change notifications and value remapping; deletion can change numeric values and invalidate uses of deleted entries. Inspect affected consumers and resolve confirmed stale uses before compiling/saving them. Do not treat successful deletion as proof that consumers remain valid.

### Struct fields

Requires loaded UnrealBPBridge protocol 14 and the current editor dependency. Read the actual field names first:

```text
get struct_fields asset /Game/UnrealBPDemo/FirstPerson/ST_CharacterStats
edit struct /Game/UnrealBPDemo/FirstPerson/ST_CharacterStats fields '[{"rename_from":"MemberVar_0","name":"Health","type":"float","default":"100"},{"name":"MaxHealth","type":"float","default":"100"}]'
save
```

Use the returned name for `rename_from`; the example is not a promise of the factory's current name. Each entry requires `name`, `default`, and exactly one of `type` or `pin_type` as strings; `default` is Unreal's text representation. Supported types reuse Blueprint variable types: bool, int, float, byte, name, string, text, Vector, Rotator, Transform, Vector2D and LinearColor. For `type: "object"`, supply `class` with a full native class or generated Blueprint `_C` object path. For `type: "struct"`, supply `struct` with a full ScriptStruct object path. Optional `container: "array"|"set"|"map"` uses the existing Blueprint container conversion; map keys are strings and `type` describes the value. Unreal rejects unsupported member types and recursive structs. Optional `tooltip` sets the field tooltip, including an empty string to clear it; omission preserves it. Existing names are updated; absent names are added. `rename_from` explicitly renames an existing field while preserving its GUID. Unmentioned fields are preserved; there is no implicit placeholder removal or field deletion. Explicit deletion and ordering use:

```text
delete struct_field asset /Game/UnrealBPDemo/FirstPerson/ST_CharacterStats name MaxHealth
move struct_field asset /Game/UnrealBPDemo/FirstPerson/ST_CharacterStats name Health before Armor
move struct_field asset /Game/UnrealBPDemo/FirstPerson/ST_CharacterStats name Health after Armor
```

Use actual returned names. Deleting the last field or a missing field fails. Move requires two distinct existing fields; a field already in the requested position is unchanged. Each field can be touched only once in a command.

For types beyond the short names, `pin_type` carries Unreal's own `FEdGraphPinType` text representation. `get struct_fields` returns this representation for each field. Reuse that value or supply a valid Unreal definition; Unreal Python imports it with `EdGraphPinType.import_text` and passes the actual type to the same `EditStructField` path. Unreal decides whether it is a valid struct member type. Do not combine `pin_type` with `type`, `class`, `struct` or `container`: the complete type, including its container/map terminal type, belongs to FEdGraphPinType itself.

Unreal categories distinguish enum (`PinCategory="byte"` with a UEnum in `PinSubCategoryObject`), class (`"class"`), soft object (`"softobject"`) and soft class (`"softclass"`). Class/object categories reference the actual class object; Blueprint classes require the generated `_C` path. These are not aliases for object reference. There are no separate editing methods per category. Use exact existing enum/class paths and enum member names for defaults. Type text is imported while preparing the fields, before edits begin. Unreal member-type validation occurs when each field executes, so a later invalid member type can leave earlier edits applied.

Example type text for a soft reference constrained to Actor: `(PinCategory="softobject",PinSubCategoryObject="/Script/Engine.Actor")`. The JSON field is `"pin_type":"(PinCategory=\"softobject\",PinSubCategoryObject=\"/Script/Engine.Actor\")"`. Prefer returned type text when preserving or copying an existing type, including container flags and map value type. This generic path requires loaded native protocol 14.

Changes use the real UserDefinedStruct and StructureEditorUtils, including Unreal's dependent-Blueprint notifications. The result reads back fields in their editor order, with names, GUIDs, pin categories, referenced type object paths, container kind, map value type, tooltip and default values. Editing selects the struct for explicit `save` and clears Blueprint context; reads do not change selection. Schema/type/name checks run before edits, but native failures can leave completed changes applied. After failure, read `get struct_fields` and affected Blueprint graphs before resuming; never blindly replay a rename. Before deleting a field, inspect asset referencers and record affected Blueprint pins/defaults and DataTable uses. After deletion or a type change, inspect affected consumers for references to the exact changed member and resolve confirmed stale uses before compiling; report any unverified consumer scope. Compile and save affected Blueprints explicitly after inspecting their updated pins/defaults.


## Python console

```sh
python3 /absolute/plugin/scripts/unreal_bp.py console python --code '1+2' --mode eval
python3 /absolute/plugin/scripts/unreal_bp.py console python --file /absolute/inspect.py
```

`--code` and `--file` are mutually exclusive. Files are read by the CLI and their source is sent to Unreal. `exec` is the default; `eval` returns an expression result as Unreal's string representation. Successful responses contain `success`, `result`, and the native per-call `logs`. Failures surface through MCP and exit nonzero. Unreal’s Python binding discards the native result/log tuple on failure, so this response reports failure without the original traceback; detailed errors remain in the Unreal output log. No unrelated log tail is presented as this call’s traceback; commands are never retried or rolled back. Calls must be serial. This is Python execution in the editor process, not a sandbox, OS shell, or raw Unreal console-command interface. Use only for work authorized by the user.

The console remains callable with an outdated loaded dependency so the installer-provided `load_code` can reload it. Verify `dependencies --check` afterward. A missing console requires the initial UI bootstrap. No UI focus is needed for subsequent console calls. Asynchronous work started by a script is not awaited by this synchronous call.


```text
folder /Game/UnrealBPDemo/FactoryCommands
create asset type MaterialInstanceConstantFactoryNew name MI_Example options '{"initialParent":{"refPath":"/Game/UnrealBPDemo/AssetCommands/M_CommandDemo.M_CommandDemo"}}'
save
```


Additional reviewed factories with no creation options: `MediaPlaylistFactoryNew`, `PlatformMediaSourceFactoryNew`, `StreamMediaSourceFactoryNew`, `FileMediaSourceFactoryNew`, `SoundMixFactory`, `ReverbEffectFactory`, `SoundClassFactory`, `SoundAttenuationFactory`, `AudioBusFactory`, `SoundConcurrencyFactory`, `DialogueVoiceFactory`, `ImgMediaSourceFactoryNew`, `BehaviorTreeFactory`, `BlackboardDataFactory`, `NiagaraValidationRuleSetFactoryNew`, `NiagaraEffectTypeFactoryNew`. These create default assets; content configuration remains separate. See `FACTORY_INVENTORY.md` at the plugin root for the discovery snapshot and unreviewed candidates.

Further factories requiring no options: `VirtualTextureBuilderFactory`, `RuntimeVirtualTextureFactory`, `DataLayerFactory`, `HLODLayerFactory`, `AnimBoneCompressionSettingsFactory`, `AnimCurveCompressionSettingsFactory`, `VariableFrameStrippingSettingsFactory`, `LandscapeGrassTypeFactory`, `NiagaraSimCacheFactoryNew`, `NiagaraParameterDefinitionsFactory`, `PaperFlipbookFactory`, `InputAction_Factory`, `InputMappingContext_Factory`, `StringTableFactory`, `MaterialParameterCollectionFactoryNew`. Input factories use their base classes; subclass selection is not exposed. Virtual texture builders, simulation caches and flipbooks are created empty/unbuilt and require content separately.

Profile/feedback factories with no options: `ObjectLibraryFactory`, `ForceFeedbackAttenuationFactory`, `ForceFeedbackEffectFactory`, `HapticFeedbackEffectCurveFactory`, `HapticFeedbackEffectBufferFactory`, `HapticFeedbackEffectSoundWaveFactory`, `SubsurfaceProfileFactory`, `SpecularProfileFactory`, `NeuralProfileFactory`, `ToonProfileFactory`, `TouchInterfaceFactory`, `SubUVAnimationFactory`. This creates default assets, without assigning SubUV textures, sound waves, haptic data or touch controls.

Additional no-option creation rules: `CompositeCurveTableFactory`, `EnvironmentQueryFactory`, `LocalizedOverlaysFactoryNew`, `BasicOverlaysFactoryNew`, `AnimationSharingSetupFactory`, `NiagaraParameterCollectionFactoryNew`, `VariantManagerFactoryNew`, `SoundSourceBusFactory`. These create default assets; query logic, collection members, variants and overlay content remain separate. Overlay factories are valid despite being hidden from the native New menu.

Specialized no-option factories: `BlueprintFunctionLibraryFactory`, `BlueprintInterfaceFactory`, `BlueprintMacroFactory`, `UIMaterialFactoryNew`, `MaterialFunctionMaterialLayerFactory`, `MaterialFunctionMaterialLayerBlendFactory`. Blueprint library parents/types are the factory defaults (FunctionLibrary, Interface, Actor for MacroLibrary); custom parents are not exposed. Use the exact factory name because several factories share an asset class. UI Material sets the UI domain; layer factories set their respective function usage.


## Inspect asset

Asset properties can be edited through the same ObjectTools path used for components:

```text
set asset /Game/UnrealBPDemo/FirstPerson/Input/IA_Move properties '{"valueType":"Axis2D"}'
save
```

Inspect the asset schema and current values first. The command validates top-level property names, reads old values, writes through ObjectTools.set_properties and returns before/after values. It selects the asset for explicit save and clears Blueprint graph context. Unreal owns nested JSON conversion; a true tool result alone does not verify semantic equality. Inspect returned values and nested object settings before saving. Array assignments replace the supplied array; preserve existing entries explicitly when editing a populated asset. There is no implicit append, merge or rollback.

Enhanced Input in UE 5.8 uses `defaultKeyMappings.mappings`; the deprecated top-level `mappings` can still appear in the schema. Each mapping uses the actual InputAction reference, key, triggers and modifiers. For instanced modifiers use a class `refPath`, e.g. `{"refPath":"/Script/EnhancedInput.InputModifierSwizzleAxis"}`. The converter creates the modifier under the context and read-back returns its actual subobject path. Existing owned subobject references can be passed back to preserve them. Do not use the stale `instance` syntax in ObjectTools' description: it produced null modifiers in the live editor. Modifier settings are properties of the real modifier object; class creation uses its native defaults, which must be verified. Negate followed by YXZ swizzle was verified for S; YXZ for W; Negate for A. Action types and six first-person mappings were saved; gameplay wiring is separate.

```sh
python3 /absolute/plugin/scripts/unreal_bp.py inspect /Game/Path/Asset
python3 /absolute/plugin/scripts/unreal_bp.py inspect /Game/Path/MI_Example --property parent
```

Command files support `inspect asset /Game/Path/Asset`. This does not change the selected asset, folder, Blueprint or graph. Use exact asset paths. Output separates registry_tags from property_schema and properties_class. CLI `--property` may be repeated to request exact schema keys; unknown keys fail explicitly. With no requested properties, values are not fetched. An empty schema is valid for classes such as Blueprint interfaces.

Existing ObjectTools reads generated-class defaults for Blueprints, and the asset instance for other objects. `asset_class` preserves AssetTools' convention (Blueprints return their generated class name); it is not a full UObject class path. Registry tags such as BlueprintType/ParentClass describe the asset and are not live CDO properties. They may lag unsaved edits. This command does not expose protected fields or require the custom editor dependency.

No-option PCG/rig/helper factories: `PCGComputeSourceFactory`, `PCGBuilderSettingsFactory`, `PCGGraphFactory`, `IKRetargetFactory`, `IKRigDefinitionFactory`, `ConsoleVariablesEditorFactory`, `PaperTileSetFactory`. Creates default assets only: no PCG template/generation, rig/mesh configuration, console commands, or tile texture assignment.

Additional default helper factories: `MaterialCacheVirtualTextureTagFactory`, `WorldBookmarkFactory`, `MeshDeformerCollectionFactory`, `PhysicsControlAssetFactory`, `SlateVectorArtDataFactory`, `TaggedAssetBrowserConfigurationFactory`, `OptimusSourceFactory`, `EaseCurveLibraryFactory`, `CameraVariableCollectionFactory`, `CameraRigProxyAssetFactory`, `InterchangeImportTestPlanFactory`, `AnimationCompressionLibraryDatabaseFactory`, `ResonanceAudioSpatializationSourceSettingsFactory`, `ResonanceAudioReverbPluginPresetFactory`, `WaveTableBankFactory`, `ChaosSolverFactory`.

CompositeDataTableFactory requires `struct` and uses the same row compatibility validation as DataTableFactory. BlendSpaceFactoryNew, BlendSpaceFactory1D, AimOffsetBlendSpaceFactoryNew, AimOffsetBlendSpaceFactory1D and AnimMontageFactory require `targetSkeleton` only. They create empty animation assets; source animations, samples and preview meshes are not exposed by these rules.

### Native factory dependency

`dependencies` also copies the bundled `UnrealBPBridge` source into the project's `Plugins` directory. Its `native_ready` flag is separate from Python `ready`. Build the project's existing editor target with the matching Unreal engine and `-NoHotReloadFromIDE` before loading the native module. Verify `Plugins/UnrealBPBridge/Binaries/<platform>/UnrealEditor.modules` names the normal binary rather than an older hot-reload suffix; build success alone is insufficient. First installation can require an editor restart; do not restart automatically. Inspect `runtime.native` after activation and require `state: current` before using a native-backed factory. Native source changes require rebuilding, and protocol changes require matching Python/native versions.

`/Script/UnrealEd.AnimCompositeFactory` requires `options {"targetSkeleton":{"refPath":"/Game/.../Skeleton.Skeleton"}}`. This creates an empty composite through the existing asset helper; segment editing is not implemented. The catalog reports it unavailable until UnrealBPBridge is loaded. No UI interaction or separate MCP server is used for factory configuration.


DataAssetFactory requires `dataAssetClass` as a class refPath and native bridge protocol 2. It rejects abstract, deprecated, superseded or hidden classes using the editor's class picker rules; protocol 1 still supports Anim Composite. A factory may declare `required_console_bool`; inspect the reported condition before creation. Do not enable experimental settings implicitly. NiagaraStatelessEmitterTemplateFactoryNew requires `fx.NiagaraStateless.AllowTemplateCreation`, which the engine labels experimental with possible data loss.

AnimBankFactory requires `targetSkeleton`; PoseAssetFactory requires `sourceAnimation` with an existing skeleton. Pose names are generated by Unreal from the source animation; custom pose names are not exposed.


PreviewMeshCollectionFactory requires `currentSkeleton` as a Skeleton refPath and native bridge protocol 3. It creates the skeleton-bound collection; collection mesh members are not configured. WidgetBlueprintFactory and EditorUtilityWidgetBlueprintFactory currently expose default creation only; select the resulting asset with `target` to compile/save it. Parent and root widget overrides are not exposed.

### Physics Asset creation

`create physics_asset from /Game/Path/SkeletalMesh` uses the existing PhysicsAssetToolset to generate collision bodies with Unreal defaults. It creates `/Game/Path/SkeletalMesh_PhysicsAsset`, regardless of the selected folder. An existing destination is rejected before creation. It does not assign the result to the source mesh. The result is selected for explicit `save`; use existing `move asset SOURCE to DESTINATION` to rename or relocate it. Generation failures stop the command; inspect the destination before retrying because Unreal may have created a partial asset.

### PCG Graph Instance

Requires UnrealBPBridge protocol 4 loaded in the editor. Select a folder, then use:

```text
create asset type PCGGraphInstanceFactory name PCGI_Demo options '{"parentGraph":{"refPath":"/Game/PCG/MyGraph"}}'
save
```

The parent must be an existing PCGGraphInterface asset. The native bridge configures the factory's reflected ParentGraph field; the existing factory creates the instance. No private PCGEditor header or separate creation pipeline is used. Missing/incompatible parents are rejected before creation.

### Sound effect preset creation

SoundSourceEffectFactory requires `soundEffectSourcepresetClass`; SoundSubmixEffectFactory requires `soundEffectSubmixPresetClass`. Supply an explicit class refPath in options using the existing generic creation syntax. Protocol 5 must be loaded. The class must derive from the corresponding preset base and must not be abstract, deprecated or superseded. Creation uses factory defaults; preset settings are not configured by these rules.

Factory catalog entries may include `required_assets`, mapping factory-owned dependency paths to expected classes. Creation validates these references before invoking the factory. ControlRigShapeLibraryFactory uses this for the bundled default shape mesh and materials; no options are needed.

StateTreeFactory requires `stateTreeSchemaClass` as a class refPath and UnrealBPBridge protocol 6. The class must be selectable under Unreal's StateTreeSchema picker rules. The native factory initializes editor data, adds the root state and compiles. StateTree is declared as a bridge plugin dependency.

`concrete_classes` in reviewed creation rules rejects abstract, deprecated and superseded option classes using bridge protocol 7 or newer. CurveFactory and AudioSynesthesia factory class options use this filter. SlateWidgetStyleAssetFactory requires styleType and additionally excludes the base container class.

`required_settings` exposes editor setting conditions in the factory catalog; creation rechecks them. Procedural Foliage and Sprite Atlas remain unavailable while their respective settings are false. Do not enable these settings automatically; the user chose to keep them disabled.

NiagaraEmitterFactoryNew creates the native default emitter with modules/renderers and verifies its seven required script assets. NiagaraSystemFactoryNew reads and validates the current RequiredSystemUpdateScript setting. These rules do not expose template/parent selection. WorldFactory creates an inactive map using project partition defaults.

EditorUtilityBlueprintFactory requires parentClass and protocol 8: editor-only Blueprint parents are accepted, EditorUtilityWidget is excluded, and EditorFunctionLibrary selects BPTYPE_FunctionLibrary. TemplateSequenceFactoryNew requires a concrete boundActorClass derived from Actor and verifies its spawnable after creation. CameraAssetFactory requires a concrete cameraDirectorClass and protocol 9, with native director-class postvalidation. Failed postvalidation leaves the asset for inspection; do not blindly retry.

## Material graphs and instances

Use `material EXACT_ASSET_PATH` to select a Material, MaterialFunction (including Material Layer and Layer Blend subclasses) or MaterialInstanceConstant in the existing asset context. This clears Blueprint/graph selection and aliases. Existing `create material` and `create material_function` also select their result. `save` saves that selected asset. Blueprint `target`, `map` and pin addresses retain their original meaning.

```text
material /Game/Materials/M_Example.M_Example
map material
find expressions filter Multiply
add expression class /Script/Engine.MaterialExpressionMultiply position -400,0 as multiply
inspect expression multiply
set expression multiply properties '{"constB":2}'
position expression multiply -400,100
bind expression source::RGB to multiply::A
unbind expression multiply::A
bind expression multiply:: to material_output MP_EmissiveColor
unbind material_output MP_EmissiveColor
layout material
compile material
save
```

`source` above denotes a previously created alias or an exact expression path from the map. Discover classes before adding; read actual pins after creation or property changes. Pin syntax is `NODE::NAME`, including `NODE::` for an unnamed output. Input/output names are case-sensitive. Expression membership is checked against the selected material/function. `inspect expression` and `map material` include actual references, classes, XY positions, reflected property schemas/values, input sources and output names. Material maps also include fixed material output connections; function graphs expose FunctionOutput nodes instead. The graph is assembled inside Unreal through the managed `material_graph` tool in one editor RPC, after normal session/schema/dependency setup. Material output access and compile diagnostics require native bridge protocol 12 plus the current managed editor dependency. Its result fills the per-run context cache; subsequent commands reuse that snapshot until mutation invalidation or explicit refresh. The connection data retains MaterialTools' source/output-name semantics, including the server's string `None` for an unconnected expression reference; do not treat that string as a connected node.

`set expression` accepts only properties from ObjectTools' reflected schema and reads values and pins back afterwards. Position uses `materialExpressionEditorX/Y`. `delete expression NODE` deletes just that node and clears aliases referring to it; inspect affected connections before compile. `layout material` explicitly rearranges the whole graph. Compile and save remain explicit; failures preserve completed changes, so read the current map before resuming.

Material Functions use the same expression commands. Create FunctionInput/FunctionOutput expressions using discovered classes and their reflected properties. To use a function inside a material, add `/Script/Engine.MaterialExpressionMaterialFunctionCall`, then assign the existing function through its reflected property:

```text
set expression function_call properties '{"materialFunction":{"refPath":"/Game/Materials/MF_Example.MF_Example"}}'
inspect expression function_call
```

The alias `function_call` must already identify a call expression. Read its refreshed pins after assignment before connecting. Compile the function before compiling materials that call it. No custom function-call bridge is involved.

```text
folder /Game/Materials
create material_instance name MI_Example parent /Game/Materials/M_Example.M_Example
list material_parameters
get material_parameter Roughness
set material_parameter Roughness value 0.4
set material_parameter Tint value '{"r":1,"g":0.2,"b":0.1,"a":1}'
set material_parameter Albedo value '"/Game/Textures/T_Example.T_Example"'
set material_parameter UseDetail value true
set material_parameter Roughness override false
save
```

Use real discovered parameter names. Listing returns name, type, association and index; instance listings also include effective value and override state. Scalar, vector (RGBA), texture and static switch access requires native bridge protocol 12. Get/set/override returns an object containing name, association, index, effective `value` and `override`. This replaces the former bare-value result. A name is accepted only when exactly one parameter matches across all associations. For a repeated layer/blend name, pass its exact identity from the list as the quoted name token:

```text
get material_parameter '{"name":"Roughness","association":"LayerParameter","index":1}'
set material_parameter '{"name":"Roughness","association":"LayerParameter","index":1}' value 0.4
set material_parameter '{"name":"Roughness","association":"LayerParameter","index":1}' override false
```

Do not infer an index from the displayed name or default to layer zero. Disabling a non-static override removes that local value and returns the inherited value. Static switch writes update shader state. A texture value may legitimately be null when unassigned; writes require an existing Texture asset path. Instance parameter listing/readback uses the actual native `FMaterialParameterInfo`, including association and index. Other parameter types are outside this typed command scope. Instances have no independent expression graph.

`compile material` returns `success`, `scope`, `validated_material_count` and per-material reports containing compiler messages, active-editor-platform errors and `error_expressions`. The expression list is a set of implicated nodes, not a positional one-to-one mapping to messages. A function updates and compiles its referencing materials; zero callers means zero validated materials, not proof that all function outputs compile in every use. A reported shader failure stops execution and includes diagnostics. Compile reports cover the active editor shader platform, not every target platform.



Material command runs reuse class references, class property schemas, expression membership, pin names, properties and connections in the existing CommandContext. The cache lives only for that run. Newly returned expressions populate membership and class information. Input connection reads also populate input names. Connection edits invalidate the destination wiring; output edits invalidate material output wiring. Property edits invalidate dynamic values/pins/parameter discovery; function assignment therefore reads new pins. Node creation/deletion invalidates dynamic graph information and updates a known membership list. Compile clears the cache. Instance effective-value getters always read Unreal; setters retain parameter-name discovery when names cannot change.

Explicit `material PATH`, `map material`, `inspect expression` and `list material_parameters` refresh the cache from Unreal. Switching through other asset/Blueprint commands clears it too (folder/list/save do not mutate graph data). If editing manually or through another tool during a command run, refresh explicitly before relying on cached data. There is no cross-run cache or editor change subscription. Mutations invalidate before executing, including failure paths; failed command runs still stop without replay. Full maps and post-write value/connection readback remain live; cache hits only reuse information within these boundaries.

`map material` uses the existing native bridge to resolve material output names, including Python-hidden Customized UVs, Pixel Depth Offset and other real engine inputs. `unavailable_material_outputs` now lists only enum entries for which the engine has no expression input. Those entries are not disconnected sockets. Bind/unbind uses the same native enum resolution and fails explicitly for invalid or unavailable targets.


### Planned multi-node material builds

`run FILE --defer-material-reads` keeps the same commands and serial mutation tools but defers automatic readback after expression add/set/position and expression/material-output connect/disconnect. These operations return references plus `readback: "deferred"`; that marks an applied operation, not verified final state. Property schema validation, ownership checks, real pin resolution, failure stopping and cache invalidation remain active. Instance parameter operations and explicit reads retain their normal behavior. Without the flag, existing immediate readback is unchanged.

Material build method (use `--batch-material-writes`; defer-only above is an alternative execution mode):

1. Plan the complete build before mutations: required functions, expression classes, aliases, function inputs/outputs, parameter names/types/defaults, material settings and intended connections. Reuse available discovery and map data. Gather only missing class/schema information in the preparation phase; deduplicate requests by class. Do not repeat discovery for each instance of a known class.
2. If reusing or editing an existing graph, select it and read one initial `map material`; reconcile the plan with existing nodes instead of creating duplicates. If a function is missing, create and finish it before any caller that depends on it. Build nested functions from dependencies outward. Reuse existing functions without rebuilding them.

**Function build — execute steps F1–F8 for one function before starting its caller:**

1. **F1 / Select:** Create or select the function asset. Any functions it calls must already be complete.
2. **F2 / Add all nodes:** Add ALL planned missing expressions, including FunctionInput, FunctionOutput, parameter and function-call nodes. Assign aliases and positions. Do not set properties or connect nodes until ALL additions are complete. Do not query after individual additions.
3. **F3 / Set all values:** Set ALL planned constants, parameter names/defaults, function input/output settings and called-function references. Do not connect any nodes during this step. Do not query after individual assignments.
4. **F4 / Read map:** Only after F2 and F3 are complete, read ONE `map material`. Read the returned actual pins and values before preparing connections. Do not separately query information already in this map.
5. **F5 / Connect all:** Send ALL planned function connections together, including connections to FunctionOutput nodes. Do not query after individual connections. Do not use fixed material outputs for a function.
6. **F6 / Check:** Read ONE `map material` and compare ALL planned nodes, values and connections. Do not compile while a known mismatch remains.
7. **F7 / Compile and verify:** Run `compile material`, check its result, then read the post-compile map and verify the graph.
8. **F8 / Save:** Save the verified function. Then build the next dependent function using F1–F8. Start the main material only after ALL required functions are complete.

**Material build — execute steps M1–M8 after the required functions are complete:**

1. **M1 / Select:** Create or select the material asset.
2. **M2 / Add all nodes:** Add ALL planned missing expressions, including parameter nodes and ALL function-call nodes. Assign aliases and positions. Do not set properties or connect nodes until ALL additions are complete. Do not query after individual additions.
3. **M3 / Set all values:** Set ALL planned constants, parameter names/defaults, function references and material-level settings. Do not connect any nodes during this step. Do not query after individual assignments.
4. **M4 / Read map:** Only after M2 and M3 are complete, read ONE `map material`. Read the returned actual pins and values before preparing connections. Do not separately query information already in this map.
5. **M5 / Connect all:** Send ALL planned internal connections and fixed material-output connections together. Do not query after individual connections.
6. **M6 / Check:** Read ONE `map material` and compare ALL planned nodes, values and connections. Do not compile while a known mismatch remains.
7. **M7 / Compile and verify:** Run `compile material`, check its result, then read the post-compile map and verify the graph.
8. **M8 / Save:** Save the verified material.

If an instance is requested, create it after M8. List exposed parameters once, set the requested values/overrides using the typed commands and their readbacks, then save. Do not repeat expression discovery for instance editing; instance value/override writes are grouped by the same batch executor, separately from graph writes.

These are phase barriers, not a per-node loop: finish ALL additions, then ALL settings, then read the map, then make ALL connections. Keep additions and settings in one consecutive write batch; the boundary between them does not require a query or a separate tool call. Consume the map before preparing bindings; never guess unseen pin names to keep one command file. The no-query rule governs agent-requested reads, not the executor's internal ownership/schema/pin validation. Existing graphs retain their unrelated connections; this sequence does not authorize disconnecting them.

Keep related commands in the same session and CommandContext when their required inputs are already known. For staged Python orchestration, create one `CommandContext(library)` and pass `context=context` to each `library.run(source, batch_material_writes=True, context=context)`. Read each returned map before preparing the next phase. The same context retains selection and aliases. Each global batch uses fresh dependency checks and a fresh Material cache; within a batch, existing mutation/map invalidation still applies. Do not repeat `material PATH` when the intended asset is already selected: explicit selection clears aliases/cache. Never share a context between different library sessions or use it concurrently. A separate CLI process still loses in-memory aliases/cache: use returned exact references rather than repeating node creation or class discovery. The map output retained from a prior phase remains planning evidence unless an intervening edit invalidates it.

Interrupt the sequence only for an explicit missing class/property/pin, a pin-shaping change, a known external edit, or a failure. Query the identified missing information, finish the required settings and refresh the map before dependent wiring. For a verification mismatch, correct only the affected nodes/values/links, then repeat verification. For a reported batch failure, inspect its automatic recovery map; if unavailable or interrupted by transport failure, read a fresh map before resuming. Never replay the whole build. Value-only edits use the relevant property/parameter read, set and readback commands instead of this construction sequence.


### Batched material writes

Use `run FILE --batch-material-writes` for known multi-node material/function builds. It implies deferred readback and groups consecutive `add expression`, `set expression`, `position expression`, `bind expression`, `bind expression ... to material_output`, `compile material`, `delete expression`, `unbind expression`, `unbind material_output`, and `set asset ... properties` commands into one `material_write_batch` editor call. The asset-property command must target the selected Material/MaterialFunction. Other commands, including maps and saves, are boundaries and keep their existing behavior. Consecutive instance value/override commands are also batched when an instance is selected; graph commands and instance commands cannot mix in the same batch. Parameter reads/listing and asset creation remain boundaries.

The current managed editor dependency is required and checked once per run. The executor uses the existing MaterialTools/ObjectTools in serial order inside Unreal. It validates expression class availability, node ownership, property schemas and actual pin names there. Add results carry the real expression references; aliases survive across batches in the same command context. Cache is invalidated before a batch, and an explicit map populates it again. No parallel editor writes, automatic rollback, or hidden fallback to per-command mutation occurs.

Each batch returns completed source lines, alias references, and either no failure or the first failed line/action/error. On a reported batch failure, the client prints completed results, the failure and aliases, then refreshes and emits the current graph map (or instance parameter values/overrides) through the existing read command before raising; later commands do not run. If that read fails, both errors remain visible and the cache is cleared. Expected validation/editor errors are caught only at this batch reporting boundary to expose partial completion, never converted into success. A transport failure can still leave an uncertain partial result: read the current graph before recovery. Do not replay completed commands.

Follow the Material build method above for phase order and query boundaries. `--defer-material-reads` remains available for serial writes with deferred readback; without either option immediate readback is unchanged.


### Custom HLSL and Material Layers

Custom HLSL uses the existing `MaterialExpressionCustom` node and `set expression ... properties`: set `code`, `outputType`, named `inputs` and any `additionalOutputs` before the wiring map. Reflected schemas for these fields were read from the running engine. An input entry contains `inputName`; an additional output contains `outputName` and `outputType`. Output types include `CMOT_Float1` through `CMOT_Float4` and `CMOT_MaterialAttributes`. Read actual pins after assignment and use compile diagnostics to check the HLSL. Editing input arrays on an existing connected node requires rechecking affected connections.

Layer and Blend assets reuse the existing generic factories `/Script/UnrealEd.MaterialFunctionMaterialLayerFactory` and `/Script/UnrealEd.MaterialFunctionMaterialLayerBlendFactory`, then the function graph commands. The `MaterialExpressionMaterialAttributeLayers` node exposes `defaultLayers` through the real reflected structure: `layers`, `blends` and `editorOnly`. Do not set only guessed layer paths: preserve the structure's existing layer states, names, GUIDs, link states and blend associations. Changing stack order invalidates parameter indices; list parameters again before instance edits. Custom HLSL compilation and shader-failure recovery were verified live. Layer/Blend graph creation was also verified. `defaultLayers` writes use the existing native bridge (protocol 12) to construct and validate the real FMaterialLayersFunctions value before a single assignment/notification; the generic per-field writer must not handle this property because intermediate array lengths can crash the editor. Live verification passed for a two-layer stack with a blend: stack assignment and compilation, repeated scalar names at layer indices 0/1, blend parameter identity, independent edits and override inheritance. Malformed metadata lengths are rejected before mutation; the map remains unchanged. Both batch and normal expression-property paths use the atomic setter. This does not claim every possible layer topology or target platform has been tested.

## Niagara Toolsets

Niagara commands call the engine's existing `NiagaraToolsets.NiagaraToolset_*` tools. No extra native bridge or Niagara data model is installed. The connected editor must have NiagaraToolsets enabled and registered. Groups and tools come from the live registry, not a copied catalog:

```text
list niagara_toolsets
list niagara_tools System
inspect niagara_tool System GetSystemSummary
niagara /Game/Hack_And_Slash_FX/VFX_Niagara/Slashes/NS_Holy_Slash1
map niagara
get niagara_compile_state
get niagara_issues
```

`niagara PATH` loads the exact system, reads its summary, selects it for the existing `save`, and clears Blueprint/graph/alias context. `map niagara` is deliberately a lightweight system summary, not a full emitter graph dump. Use returned emitter identities with `GetEmitterTopology`, then scoped module/input/renderer reads. Selection does not inject a system into explicit tool arguments.

All registered Niagara operations are accessible through one schema-preserving command:

```text
inspect niagara_tool System GetEmitterTopology
call niagara System GetSystemSummary arguments '{"system":{"refPath":"/Game/Hack_And_Slash_FX/VFX_Niagara/Slashes/NS_Holy_Slash1.NS_Holy_Slash1"}}'
call niagara Assets GetAssetDiscoveryInfo arguments '{}'
```

Use the exact group/tool names returned by discovery. `inspect niagara_tool GROUP TOOL` returns the native input/output schemas. `arguments` must be a quoted JSON object matching that schema, including required stack-reference fields, native property-value JSON strings, and instanced-value structs. Do not invent omitted defaults or flatten typed values. Read `Info.UEnum_Info` before writing an enum. Unknown/missing top-level arguments fail before the tool call; the existing registry validates native argument types and reports tool errors. Native return values are preserved without renaming, alias substitution or success masking. Void tools legitimately return null; verify mutations using the corresponding native read operation.

The System group owns emitter/module/renderer/user-variable operations, while Assets owns script discovery; Component, Blueprint and Info retain their existing native responsibilities. Calls do not auto-select created/modified assets, auto-save, retarget references or roll back edits. After a create call, explicitly select the returned system path before saving. After a call against a different system, explicitly select that system before saving. Existing asset copy/move/save operations remain the owner of those actions.

`GetSystemCompileState`, `GetStackIssues` and `ApplyStackIssueFix` are asynchronous native tools. The CLI splits the managed batch before each, awaits it through the same MCP transport, then resumes remaining commands with the same context and original line numbers. They are rejected before invocation if sent directly to the synchronous in-editor command_batch. This is deliberate routing, not retry/fallback behavior. The existing transport timeout still applies: a timeout is an uncertain result, especially for a fix; re-read live state before recovery. Other synchronous Niagara commands use the shared managed batch normally.

Compile-state inspection waits for an in-flight compile; it is not a force-recompile command. Inspect `bIsStale`, `bHasErrors`, per-script events and stack issues before deciding to save. Do not assume successful tool execution means a clean compile. A planned edit should read schema/topology first, perform the smallest mutation, read it back, inspect compile state/issues in a separate run, then `save` explicitly. Read returned issues/fixes before invoking ApplyStackIssueFix; do not auto-fix all issues. Renderer indices and stack references can change after structural edits: reacquire them before subsequent edits. Stop after a failed operation and inspect the affected system; never replay the whole mutation file.
