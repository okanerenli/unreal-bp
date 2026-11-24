"""Command syntax and parsing; no editor connection."""
import json
import shlex
from .errors import UnrealMCPError

# Each template maps directly to an existing library operation. Quoted tokens use shlex.
COMMANDS = {
    "niagara_toolsets": "list niagara_toolsets",
    "niagara_tools": "list niagara_tools {group}",
    "niagara_tool_schema": "inspect niagara_tool {group} {tool}",
    "niagara_call": "call niagara {group} {tool} arguments {arguments}",
    "niagara_select": "niagara {path}",
    "niagara_map": "map niagara",
    "niagara_compile_state": "get niagara_compile_state",
    "niagara_issues": "get niagara_issues",
    "material_select": "material {path}",
    "material_map": "map material",
    "material_types": "find expressions filter {filter}",
    "material_add": "add expression class {class} position {position} as {alias}",
    "material_inspect": "inspect expression {node}",
    "material_set": "set expression {node} properties {values}",
    "material_position": "position expression {node} {position}",
    "material_delete": "delete expression {node}",
    "material_bind": "bind expression {output} to {input}",
    "material_unbind": "unbind expression {input}",
    "material_output": "bind expression {output} to material_output {property}",
    "material_unbind_output": "unbind material_output {property}",
    "material_layout": "layout material",
    "material_compile": "compile material",
    "material_instance_create": "create material_instance name {name} parent {path}",
    "material_parameters": "list material_parameters",
    "material_parameter_get": "get material_parameter {name}",
    "material_parameter_set": "set material_parameter {name} value {value}",
    "material_override": "set material_parameter {name} override {value}",

    "set_asset_properties": "set asset {path} properties {values}",
    "list_components": "list components",
    "create_component": "create component name {name} class {class}",
    "inspect_component": "inspect component {component}",
    "component_parent": "get component_parent {component}",
    "get_component_properties": "get component {component} properties {properties}",
    "set_component_properties": "set component {component} properties {values}",
    "edit_struct": "edit struct {path} fields {fields}",
    "struct_fields": "get struct_fields asset {path}",
    "enum_entries": "get enum_entries asset {path}",
    "add_enum_entries": "add enum_entries asset {path} names {names}",
    "rename_enum_entries": "rename enum_entries asset {path} names {names}",
    "delete_enum_entries": "delete enum_entries asset {path} ids {ids}",
    "delete_struct_field": "delete struct_field asset {path} name {name}",
    "move_struct_field": "move struct_field asset {path} name {name} {position} {relative_to}",
    "inspect_asset": "inspect asset {path}",
    "find_asset_types": "find asset_types filter {filter}",
    "refresh_asset_types": "refresh asset_types",
    "create_asset": "create asset type {type} name {name}",
    "create_asset_options": "create asset type {type} name {name} options {options}",
    "delete_asset": "delete asset {path}",
    "move_asset": "move asset {path} to {destination}",
    "copy_asset": "copy asset {path} to {destination}",
    "asset_referencers": "get referencers asset {path}",
    "asset_dependencies": "get dependencies asset {path}",
    "folder": "folder {folder}",
    "list_assets": "list assets",
    "list_folders": "list folders",
    "create_material": "create material name {name}",
    "create_material_function": "create material_function name {name}",
    "create_physics_asset": "create physics_asset from {path}",
    "create_datatable": "create datatable name {name} row_struct {row_struct}",
    "find_row_structs": "find row_structs filter {filter}",
    "datatable_select": "datatable {path}",
    "datatable_schema": "get datatable_schema",
    "datatable_list_rows": "list datatable_rows",
    "datatable_get_rows": "get datatable_rows {rows}",
    "datatable_add_rows": "add datatable_rows {rows}",
    "datatable_set_rows": "set datatable_rows {values}",
    "datatable_remove_rows": "delete datatable_rows {rows}",
    "datatable_rename_rows": "rename datatable_rows {renames}",
    "create_bp_in_folder": "create bp name {name} parent {parent}",
    "target": "target {target}",
    "graph": "graph {name}",
    "map": "map",
    "map_graph": "map graph",
    "get_flow": "get flow node {node}",
    "create_dispatcher": "create dispatcher name {name}",
    "list_dispatchers": "list dispatchers",
    "dispatcher_input": "add dispatcher_input name {name} type {type}",
    "event_functions": "list event_functions node {node}",
    "event_function": "set event_function node {node} name {name}",
    "create_bp": "create bp name {name} folder {folder} parent {parent}",
    "custom_event": "create custom_event name {name} position {position} as {alias}",
    "create_variable": "create variable type {type} name {name}",
    "create_object_variable": "create variable type object class {class} name {name}",
    "create_container_variable": "create variable type {type} container {container} name {name}",
    "create_function": "create function name {name}",
    "add_node": "add node type {type} position {position} as {alias}",
    "create_comment": "create comment text {text} position {position} size {size} as {alias}",
    "wrap_comment": "create comment text {text} nodes {nodes} padding {padding} as {alias}",
    "list_comments": "list comments",
    "inspect_comment": "inspect comment {node}",
    "set_comment": "set comment {node} properties {values}",
    "delete_comment": "delete comment {node}",
    "add_node_class": "add node type {type} class {class} position {position} as {alias}",
    "variable_get": "add variable_get name {name} position {position} as {alias}",
    "variable_set": "add variable_set name {name} position {position} as {alias}",
    "variable_get_owner": "add variable_get name {name} owner {owner} position {position} as {alias}",
    "variable_set_owner": "add variable_set name {name} owner {owner} position {position} as {alias}",
    "cast": "add cast class {class} position {position} as {alias}",
    "call": "add call name {name} owner {owner} position {position} as {alias}",
    "set_pin": "set pin {pin} value {value}",
    "function_input": "add function_input name {name} type {type}",
    "function_output": "add function_output name {name} type {type}",
    "find_types": "find node_types filter {filter}",
    "refresh_node_types": "refresh node_types",
    "find_categories": "find node_categories filter {filter}",
    "type_pins": "inspect node_type {type}",
    "types_pins": "inspect node_types {types}",
    "add_pin": "add pin node {node}",
    "remove_pin": "remove pin {pin} direction {direction}",
    "position": "position node {node} {position}",
    "bind": "bind {output} to {input}",
    "unbind": "unbind {output} from {input}",
    "delete_node": "delete node {node}",
    "delete_variable": "delete variable name {name}",
    "delete_function": "delete function name {name}",
    "delete_function_input": "delete function_input name {name}",
    "delete_function_output": "delete function_output name {name}",
    "delete_dispatcher_input": "delete dispatcher_input name {name}",
    "arrange": "arrange nodes {nodes} position {position}",
    "compile": "compile",
    "save": "save",
}


def parse_commands(source):
    commands = []
    for line, text in enumerate(source.splitlines(), 1):
        tokens = shlex.split(text, comments=True)
        if not tokens:
            continue
        options = {}
        if tokens[:2] in (["add", "function_input"], ["add", "function_output"], ["add", "dispatcher_input"]):
            tail = tokens[6:]
            if len(tail) % 2:
                raise UnrealMCPError(f"Line {line}: parameter options require KEY VALUE pairs")
            for key, value in zip(tail[::2], tail[1::2]):
                if key not in ("class", "struct", "container") or key in options:
                    raise UnrealMCPError(f"Line {line}: unknown or repeated parameter option {key}")
                options[key] = value
            tokens = tokens[:6]
        if tokens[:2] == ["create", "variable"]:
            header_length = 8 if len(tokens) > 4 and tokens[4] in ("class", "container") else 6
            tail = tokens[header_length:]
            if len(tail) % 2:
                raise UnrealMCPError(f"Line {line}: variable options require scope VALUE or default VALUE")
            for key, value in zip(tail[::2], tail[1::2]):
                if key not in ("scope", "default", "container", "struct") or key in options:
                    raise UnrealMCPError(f"Line {line}: unknown or repeated variable option {key}")
                options[key] = value
            if "scope" in options and options["scope"] not in ("member", "local"):
                raise UnrealMCPError(f"Line {line}: scope must be member or local")
            if options.get("scope") == "local" and "default" in options:
                raise UnrealMCPError(f"Line {line}: local default values are not exposed by the current Unreal tools")
            tokens = tokens[:header_length]
        for action, template in COMMANDS.items():
            pattern = template.split()
            if len(tokens) != len(pattern):
                continue
            if any(p != t for p, t in zip(pattern, tokens) if not p.startswith("{")):
                continue
            args = {p[1:-1]: t for p, t in zip(pattern, tokens) if p.startswith("{")}
            if args.keys() & options.keys():
                raise UnrealMCPError(f"Line {line}: repeated variable options")
            args.update(options)
            if action == "niagara_select" and not args['path'].startswith('/'):
                raise UnrealMCPError(f"Line {line}: niagara requires a full Unreal asset path")
            if action == "niagara_call":
                args['arguments'] = json.loads(args['arguments'])
                if not isinstance(args['arguments'], dict):
                    raise UnrealMCPError(f"Line {line}: Niagara arguments requires a JSON object")
            if action in ('enum_entries', 'add_enum_entries', 'rename_enum_entries', 'delete_enum_entries'):
                if not args['path'].startswith('/'):
                    raise UnrealMCPError(f'Line {line}: enum requires a full Unreal asset path')
                if action != 'enum_entries':
                    key = 'ids' if action == 'delete_enum_entries' else 'names'
                    args[key] = json.loads(args[key])
                    value = args[key]
                    if action == 'rename_enum_entries':
                        if not isinstance(value, dict) or not value or not all(isinstance(k, str) and k and isinstance(v, str) and v.strip() for k, v in value.items()):
                            raise UnrealMCPError(f'Line {line}: names requires a nonempty entry-id to display-name JSON object')
                    elif not isinstance(value, list) or not value or not all(isinstance(v, str) and v.strip() for v in value) or len(value) != len(set(value)):
                        raise UnrealMCPError(f'Line {line}: {key} requires a nonempty JSON array of distinct nonempty strings')
            if action == "set_comment":
                args['values'] = json.loads(args['values'])
                if not isinstance(args['values'], dict) or not args['values']:
                    raise UnrealMCPError(f"Line {line}: comment properties requires a nonempty JSON object")
            if action == "create_comment":
                dimensions = args['size'].split(',')
                if len(dimensions) != 2:
                    raise UnrealMCPError(f"Line {line}: size requires positive integer WIDTH,HEIGHT")
                args['size'] = dict(zip(('x', 'y'), map(int, dimensions)))
                if min(args['size'].values()) <= 0:
                    raise UnrealMCPError(f"Line {line}: comment dimensions must be positive")
            if action == "wrap_comment":
                args['nodes'] = args['nodes'].split(',')
                args['padding'] = int(args['padding'])
                if not all(args['nodes']) or args['padding'] < 0:
                    raise UnrealMCPError(f"Line {line}: provide nodes and nonnegative padding")
            if action in ("material_parameter_set", "material_override"):
                args['value'] = json.loads(args['value'])
                if action == "material_override" and type(args['value']) is not bool:
                    raise UnrealMCPError(f"Line {line}: override requires true or false")
            if action == "material_set":
                args['values'] = json.loads(args['values'])
                if not isinstance(args['values'], dict) or not args['values']:
                    raise UnrealMCPError(f"Line {line}: expression properties requires a nonempty JSON object")
            if action == "types_pins":
                args['types'] = json.loads(args['types'])
                if not isinstance(args['types'], list) or not args['types']:
                    raise UnrealMCPError(f"Line {line}: node_types requires a nonempty JSON array")
                for entry in args['types']:
                    if not isinstance(entry, dict) or 'type' not in entry or entry.keys() - {'type', 'class'}:
                        raise UnrealMCPError(f"Line {line}: each node type requires type and accepts optional class")
                    if not isinstance(entry['type'], str) or not entry['type']:
                        raise UnrealMCPError(f"Line {line}: node type must be a nonempty string")
                    if 'class' in entry and (not isinstance(entry['class'], str) or not entry['class'].startswith('/')):
                        raise UnrealMCPError(f"Line {line}: class requires a full Unreal class object path")
            if action == "add_node_class":
                if not args['class'].startswith('/'):
                    raise UnrealMCPError(f"Line {line}: class requires a full Unreal class object path")
                action = "add_node"
            if action in ("get_component_properties", "set_component_properties", "set_asset_properties"):
                key = 'properties' if action == 'get_component_properties' else 'values'
                args[key] = json.loads(args[key])
                if (key == 'properties' and (not isinstance(args[key], list) or not all(isinstance(p, str) for p in args[key]))) or (key == 'values' and not isinstance(args[key], dict)):
                    raise UnrealMCPError(f"Line {line}: properties requires a JSON name array for get or object for set")
            if action in ("edit_struct", "struct_fields", "delete_struct_field", "move_struct_field") and not args["path"].startswith("/"):
                raise UnrealMCPError(f"Line {line}: struct requires a full Unreal asset path")
            if action == "datatable_select" and not args['path'].startswith('/'):
                raise UnrealMCPError(f"Line {line}: datatable requires a full Unreal asset path")
            if action in ("datatable_get_rows", "datatable_add_rows", "datatable_remove_rows"):
                args['rows'] = json.loads(args['rows'])
                if not isinstance(args['rows'], list) or not args['rows'] or not all(isinstance(name, str) and name for name in args['rows']):
                    raise UnrealMCPError(f"Line {line}: rows requires a nonempty JSON array of nonempty row names")
            if action in ("datatable_set_rows", "datatable_rename_rows"):
                key = 'values' if action == 'datatable_set_rows' else 'renames'
                args[key] = json.loads(args[key])
                if not isinstance(args[key], dict) or not args[key] or not all(args[key]):
                    raise UnrealMCPError(f"Line {line}: {key} requires a nonempty JSON object with nonempty row names")
                if action == 'datatable_set_rows' and not all(isinstance(value, dict) and value for value in args[key].values()):
                    raise UnrealMCPError(f"Line {line}: each row update requires a nonempty property object")
                if action == 'datatable_rename_rows' and not all(isinstance(value, str) and value for value in args[key].values()):
                    raise UnrealMCPError(f"Line {line}: each rename requires a nonempty destination row name")
            if action == "move_struct_field" and args["position"] not in ("before", "after"):
                raise UnrealMCPError(f"Line {line}: struct field position must be before or after")
            if action == "edit_struct":
                args["fields"] = json.loads(args["fields"])
                if not isinstance(args["fields"], list) or not args["fields"]:
                    raise UnrealMCPError(f"Line {line}: fields must be a nonempty JSON array")
            if action == "create_asset_options":
                action = "create_asset"
                args["options"] = json.loads(args["options"])
                if not isinstance(args["options"], dict):
                    raise UnrealMCPError(f"Line {line}: factory options must be a JSON object")
            if action in ("delete_asset", "move_asset", "copy_asset", "asset_referencers", "asset_dependencies"):
                if not args["path"].startswith("/") or ":" in args["path"]:
                    raise UnrealMCPError(f"Line {line}: asset requires a full Unreal asset path")
                if "destination" in args and (not args["destination"].startswith("/") or args["destination"].endswith("/") or any(c in args["destination"] for c in (".", ":", "//"))):
                    raise UnrealMCPError(f"Line {line}: destination requires a package path including asset name, such as /Game/Data/Copy")
            if "folder" in args and (not args["folder"].startswith("/") or args["folder"] == "/" or "." in args["folder"] or "//" in args["folder"]):
                raise UnrealMCPError(f"Line {line}: folder requires an absolute Unreal content folder such as /Game/Data")
            if action == "create_bp_in_folder":
                action = "create_bp"
            if action in ("function_input", "function_output", "dispatcher_input"):
                for kind, key in (("object", "class"), ("struct", "struct")):
                    if (args["type"] == kind) != (key in args):
                        raise UnrealMCPError(f"Line {line}: type {kind} requires {key}; other types cannot use it")
                if "struct" in args and not args["struct"].startswith("/"):
                    raise UnrealMCPError(f"Line {line}: struct requires a full ScriptStruct object path")
                if "container" in args and args["container"] not in ("array", "set", "map"):
                    raise UnrealMCPError(f"Line {line}: container must be array, set or map (string keys)")
            if action == "create_object_variable":
                args["type"] = "object"
            if action in ("create_object_variable", "create_container_variable"):
                action = "create_variable"
            if action == "create_variable":
                if (args["type"] == "struct") != ("struct" in args):
                    raise UnrealMCPError(f"Line {line}: type struct requires struct PATH; other types cannot use it")
                if "struct" in args and not args["struct"].startswith("/"):
                    raise UnrealMCPError(f"Line {line}: struct requires a full ScriptStruct object path")
                if args["type"] == "object" and "class" not in args:
                    raise UnrealMCPError(f"Line {line}: object variables require class BLUEPRINT")
                if "container" in args and args["container"] not in ("array", "set", "map"):
                    raise UnrealMCPError(f"Line {line}: container must be array, set or map (string keys)")
                if "default" in args and ("container" in args or args["type"] == "object"):
                    raise UnrealMCPError(f"Line {line}: object/container defaults are not supported")
            if "default" in args:
                if args["type"] in ("string", "name", "text"):
                    pass  # These defaults are literal text, not JSON expressions.
                elif args["type"] in ("int", "byte", "float", "bool"):
                    value = json.loads(args["default"])
                    valid = {
                        "int": type(value) is int and -(2**31) <= value < 2**31,
                        "byte": type(value) is int and 0 <= value <= 255,
                        "float": type(value) in (int, float),
                        "bool": type(value) is bool,
                    }
                    if not valid[args["type"]]:
                        raise UnrealMCPError(f"Line {line}: invalid {args['type']} default")
                    args["default"] = value
                else:
                    raise UnrealMCPError(f"Line {line}: defaults currently support primitive variable types only")
            if "position" in args:
                coordinates = args["position"].split(",")
                if len(coordinates) != 2:
                    raise UnrealMCPError(f"Line {line}: position requires integer X,Y")
                args["position"] = dict(zip(("x", "y"), map(int, coordinates)))
            if action in ("variable_get_owner", "variable_set_owner"):
                action = action.removesuffix("_owner")
            commands.append((line, action, args))
            break
        else:
            raise UnrealMCPError(f"Line {line}: unsupported syntax: {text}")
    if not commands:
        raise UnrealMCPError("Command file is empty")
    return commands
