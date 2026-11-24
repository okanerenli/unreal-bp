"""Blueprint maps, graph edits and node operations."""
import json
from .errors import UnrealMCPError

def resolve_blueprint(self, target):
    if not target.strip():
        raise UnrealMCPError("Blueprint target must not be empty")
    if target.startswith("/"):
        asset_path = target
    else:
        candidates = self._call(self.ASSETS, "find_assets", {
            "folder_path": "", "name": target,
            "asset_type": {"refPath": "/Script/Engine.Blueprint"},
            "recursive": True,
        })
        if not candidates:
            raise UnrealMCPError(f"Blueprint not found: {target}")
        if len(candidates) != 1:
            raise UnrealMCPError(
                f"Ambiguous Blueprint target {target!r}; supply an asset path: "
                + json.dumps(candidates)
            )
        asset_path = candidates[0]
    blueprint = self._call(self.ASSETS, "load_asset", {"asset_path": asset_path})
    return blueprint

def graph_map(self, graph):
    nodes = self._call(self.BLUEPRINTS, "find_nodes", {"graph": graph, "title": ""})
    # Empty graphs are valid and have no node information to request.
    infos = self._call(self.BLUEPRINTS, "get_node_infos", {"nodes": nodes}) if nodes else []
    return {"graph": graph, "nodes": infos}

def blueprint_map(self, target, graph_name=None):
    blueprint = self.resolve_blueprint(target)
    if graph_name is None:
        graphs = self._call(self.BLUEPRINTS, "list_graphs", {"blueprint": blueprint})
    else:
        graphs = [self._call(self.BLUEPRINTS, "get_graph", {"blueprint": blueprint, "graph_name": graph_name})]
    graph_maps = [graph_map(self, graph) for graph in graphs]
    return {"blueprint": blueprint, "graphs": graph_maps}

def execute(self, context, line, action, args):
    result = None
    if action == "target":
        context.blueprint = self.resolve_blueprint(args["target"])
        context.selected_asset = context.blueprint
        context.graph = None
        context.aliases.clear()
        result = context.blueprint
    elif action == "create_bp":
        destination = args["folder"] if "folder" in args else context.folder
        if destination is None:
            raise UnrealMCPError(f"Line {line}: select folder or provide folder PATH")
        context.blueprint = context.bp_call("create", {
            "folder_path": destination, "asset_name": args["name"],
            "asset_type": {"refPath": args["parent"]},
        })
        context.selected_asset = context.blueprint
        context.graph = None
        context.aliases.clear()
        result = context.blueprint
    else:
        if context.blueprint is None:
            raise UnrealMCPError(f"Line {line}: select target or create bp first")
        if action == "graph":
            context.graph = context.bp_call("get_graph", {"blueprint": context.blueprint, "graph_name": args["name"]})
            context.aliases.clear()
            result = context.graph
        elif action == "map":
            result = self.blueprint_map(context.blueprint["refPath"])
        elif action == "map_graph":
            if context.graph is None:
                raise UnrealMCPError(f"Line {line}: map graph requires a selected graph")
            result = {"blueprint": context.blueprint, "graphs": [graph_map(self, context.graph)]}
        elif action == "create_dispatcher":
            context.graph = context.bp_call("add_event_dispatcher", {"blueprint": context.blueprint, "name": args["name"]})
            context.aliases.clear()
            result = context.graph
        elif action == "list_dispatchers":
            result = context.bp_call("list_event_dispatchers", {"blueprint": context.blueprint})
        elif action == "delete_function":
            removed = context.bp_call("get_graph", {"blueprint": context.blueprint, "graph_name": args["name"]})
            dispatchers = context.bp_call("list_event_dispatchers", {"blueprint": context.blueprint})
            entries = context.bp_call("find_nodes", {
                "graph": removed, "title": "",
                "node_class": {"refPath": "/Script/BlueprintGraph.K2Node_FunctionEntry"},
            })
            if removed in dispatchers or len(entries) != 1:
                raise UnrealMCPError("delete function requires a function graph")
            context.bp_call("remove_function_graph", {"blueprint": context.blueprint, "graph_name": args["name"]})
            if context.graph == removed:
                context.graph = None
                context.aliases.clear()
        elif action == "create_function":
            functions = context.bp_call("list_functions", {"blueprint": context.blueprint})
            if any(f["name"].casefold() == args["name"].casefold() for f in functions):
                raise UnrealMCPError(f"Function already exists or is inherited: {args['name']}")
            context.graph = context.bp_call("add_function_graph", {"blueprint": context.blueprint, "graph_name": args["name"]})
            context.aliases.clear()
            result = context.graph
        elif action == "create_variable":
            variable_context = {"blueprint": context.blueprint}
            if args.get("scope", "member") == "local":
                if context.graph is None:
                    raise UnrealMCPError("Local variables require a selected function graph")
                entries = context.bp_call("find_nodes", {
                    "graph": context.graph, "title": "",
                    "node_class": {"refPath": "/Script/BlueprintGraph.K2Node_FunctionEntry"},
                })
                if len(entries) != 1:
                    raise UnrealMCPError("Local variables require a function graph, not an event or macro graph")
                variable_context["graph"] = context.graph
            names = context.bp_call("list_variables", variable_context)
            if args["name"].casefold() in [n.casefold() for n in names]:
                raise UnrealMCPError(f"Variable already exists: {args['name']}")
            if "container" in args:
                variable_context["container_type"] = args["container"].upper()
            if args["type"] == "object":
                owner = self.resolve_blueprint(args["class"])
                context.bp_call("add_object_variable", {
                    **variable_context, "name": args["name"], "object_class": context.blueprint_class(owner),
                })
            elif args["type"] == "struct":
                context.bp_call("add_struct_variable", {
                    **variable_context, "name": args["name"], "struct_type": {"refPath": args["struct"]},
                })
            else:
                context.bp_call("add_variable", {**variable_context, "name": args["name"], "type_name": args["type"]})
            result = {"variable": args["name"], "scope": args.get("scope", "member")}
            if "default" in args:
                context.bp_call("compile_blueprint", {"blueprint": context.blueprint})
                toolset = "editor_toolset.toolsets.object.ObjectTools"
                if toolset not in self.schemas:
                    schema = json.loads(self._tool("describe_toolset", {"toolset_name": toolset}))
                    self.schemas[toolset] = {t["name"].rsplit(".", 1)[-1]: t for t in schema["tools"]}
                properties = json.loads(self._call(toolset, "list_properties", {"instance": context.blueprint}))
                keys = [key for key in properties if key.casefold() == args["name"].casefold()]
                if len(keys) != 1:
                    raise UnrealMCPError(f"Cannot resolve the created variable in Class Defaults: {args['name']}")
                key = keys[0]
                success = self._call(toolset, "set_properties", {
                    "instance": context.blueprint, "values": json.dumps({key: args["default"]}),
                })
                if success is not True:
                    raise UnrealMCPError(f"Failed to set Class Default for {args['name']}")
                result["defaults"] = json.loads(self._call(toolset, "get_properties", {
                    "instance": context.blueprint, "properties": [key],
                }))
        elif action in ("list_components", "create_component", "inspect_component", "component_parent", "get_component_properties", "set_component_properties"):
            actor_tools = "editor_toolset.toolsets.actor.ActorTools"
            object_tools = "editor_toolset.toolsets.object.ObjectTools"
            for toolset in (actor_tools, object_tools):
                if toolset not in self.schemas:
                    schema = json.loads(self._tool("describe_toolset", {"toolset_name": toolset}))
                    self.schemas[toolset] = {t["name"].rsplit(".", 1)[-1]: t for t in schema["tools"]}
            actor = context.bp_call("get_default_object", {"blueprint": context.blueprint})
            components = self._call(actor_tools, "get_components", {"actor": actor})
            if action == "list_components":
                result = components
            elif action == "create_component":
                result = self._call(actor_tools, "add_component", {
                    "owner": context.blueprint, "component_type": {"refPath": args['class']}, "name": args['name'],
                })
            else:
                component = {"refPath": args['component']}
                if component not in components:
                    raise UnrealMCPError('Component must be an exact reference returned by list components for the selected Blueprint')
                if action == "component_parent":
                    result = self._call(actor_tools, "get_parent_component", {"component": component})
                else:
                    schema = json.loads(self._call(object_tools, "list_properties", {"instance": component}))
                    if action == "inspect_component":
                        result = schema
                    else:
                        properties = args['properties'] if action == "get_component_properties" else list(args['values'])
                        unknown = set(properties) - schema.keys()
                        if unknown:
                            raise UnrealMCPError(f'Unknown component properties: {sorted(unknown)}; inspect component first')
                        previous = json.loads(self._call(object_tools, "get_properties", {"instance": component, "properties": properties}))
                        result = previous
                        if action == "set_component_properties":
                            if self._call(object_tools, "set_properties", {"instance": component, "values": json.dumps(args['values'])}) is not True:
                                raise UnrealMCPError('Component property edit failed')
                            result = {"before": previous, "after": json.loads(self._call(object_tools, "get_properties", {"instance": component, "properties": properties}))}
        elif action == "delete_variable":
            names = context.bp_call("list_variables", {"blueprint": context.blueprint})
            if args["name"] not in names:
                raise UnrealMCPError(f"Variable does not exist: {args['name']}")
            context.bp_call("remove_variable", {"blueprint": context.blueprint, "name": args["name"]})
        elif action == "compile":
            context.bp_call("compile_blueprint", {"blueprint": context.blueprint})
        else:
            if context.graph is None:
                raise UnrealMCPError(f"Line {line}: select graph first")
            if action == "get_flow":
                result = context.bp_call("get_connected_subgraph", {"node": context.node_ref(args["node"])})
            elif action == "event_functions":
                result = context.bp_call("list_compatible_event_functions", {"node": context.node_ref(args["node"])})
            elif action == "event_function":
                node = context.node_ref(args["node"])
                names = context.bp_call("list_compatible_event_functions", {"node": node})
                if args["name"] not in names:
                    raise UnrealMCPError(f"Incompatible event function {args['name']}; compatible functions: {names}")
                context.bp_call("set_create_event_function", {"node": node, "function_name": args["name"]})
                result = context.bp_call("get_create_event_function", {"node": node})
            elif action == "refresh_node_types":
                dependency = self.editor_dependency_status()
                if dependency['state'] != 'current':
                    raise UnrealMCPError('Node discovery refresh requires the current editor dependency; run dependencies and load its returned code')
                result = self._call(self.ASSET_CREATION, "refresh_node_types", {"graph": context.graph})
            elif action in ("find_types", "find_categories"):
                result = context.bp_call("find_node_types" if action == "find_types" else "find_node_categories", {
                    "graph": context.graph,
                    "type_id_filter" if action == "find_types" else "category_filter": args["filter"],
                    "context_pins": [],
                })
            elif action == "type_pins":
                result = context.bp_call("get_node_type_pins", {"graph": context.graph, "type_id": args["type"]})
            elif action == "types_pins":
                dependency = self.editor_dependency_status()
                if dependency['state'] != 'current':
                    raise UnrealMCPError('Batch node inspection requires the current editor dependency')
                result = self._call(self.ASSET_CREATION, "inspect_node_types", {"graph": context.graph, "types": json.dumps(args['types'])})
            elif action in ("create_comment", "wrap_comment", "list_comments", "inspect_comment", "set_comment", "delete_comment"):
                if action in ("create_comment", "wrap_comment"):
                    if args['alias'] in context.aliases:
                        raise UnrealMCPError(f"Node alias already exists: {args['alias']}")
                    arguments = {'graph': context.graph, 'text': args['text']}
                    if action == 'create_comment':
                        arguments.update(position=args['position'], size=args['size'])
                    else:
                        arguments.update(nodes=[context.node_ref(n) for n in args['nodes']], padding=args['padding'])
                    result = self._call(self.ASSET_CREATION, action, arguments)
                    context.aliases[args['alias']] = result
                elif action == 'list_comments':
                    result = json.loads(self._call(self.ASSET_CREATION, 'list_comments', {'graph': context.graph}))
                elif action == 'delete_comment':
                    node = context.node_ref(args['node'])
                    self._call(self.ASSET_CREATION, 'delete_comment', {'node': node})
                    context.aliases = {k: v for k, v in context.aliases.items() if v != node}
                else:
                    result = json.loads(self._call(self.ASSET_CREATION, 'node_comment', {
                        'node': context.node_ref(args['node']),
                        'values': json.dumps(args['values'] if action == 'set_comment' else {}),
                    }))
            elif action == "add_pin":
                node = context.node_ref(args["node"])
                pin = context.bp_call("add_node_pin", {"node": node})
                result = {"added_pin": pin, "node_info": context.bp_call("get_node_infos", {"nodes": [node]})[0]}
            elif action == "remove_pin":
                if args["direction"] not in ("input", "output"):
                    raise UnrealMCPError("Pin direction must be input or output")
                pin = context.pin_ref(args["pin"], args["direction"])
                context.bp_call("remove_node_pin", {"node": pin["node"], "pin": pin})
                result = context.bp_call("get_node_infos", {"nodes": [pin["node"]]})[0]
            elif action in ("delete_function_input", "delete_function_output", "delete_dispatcher_input"):
                dispatchers = context.bp_call("list_event_dispatchers", {"blueprint": context.blueprint})
                if action == "delete_dispatcher_input":
                    if context.graph not in dispatchers:
                        raise UnrealMCPError("Dispatcher parameters require a selected dispatcher graph")
                else:
                    entries = context.bp_call("find_nodes", {
                        "graph": context.graph, "title": "",
                        "node_class": {"refPath": "/Script/BlueprintGraph.K2Node_FunctionEntry"},
                    })
                    if context.graph in dispatchers or len(entries) != 1:
                        raise UnrealMCPError("Function parameters require a selected function graph")
                context.bp_call("remove_function_param", {
                    "graph": context.graph, "param_name": args["name"],
                    "input_param": action != "delete_function_output",
                })
            elif action in ("function_input", "function_output", "dispatcher_input"):
                dispatchers = context.bp_call("list_event_dispatchers", {"blueprint": context.blueprint})
                if action == "dispatcher_input" and context.graph not in dispatchers:
                    raise UnrealMCPError("Dispatcher parameters require a selected dispatcher graph")
                if action != "dispatcher_input" and context.graph in dispatchers:
                    raise UnrealMCPError("Use add dispatcher_input on dispatcher graphs; outputs are unsupported")
                entries = context.bp_call("find_nodes", {
                    "graph": context.graph, "title": "",
                    "node_class": {"refPath": "/Script/BlueprintGraph.K2Node_FunctionEntry"},
                })
                if action != "dispatcher_input" and len(entries) != 1:
                    raise UnrealMCPError("Function parameters require a selected function graph")
                param = {
                    "graph": context.graph, "param_name": args["name"],
                    "input_param": action != "function_output",
                }
                if "container" in args:
                    param["container_type"] = args["container"].upper()
                if args["type"] == "object":
                    param["object_class"] = context.blueprint_class(self.resolve_blueprint(args["class"]))
                    tool = "add_object_function_param"
                elif args["type"] == "struct":
                    param["struct_type"] = {"refPath": args["struct"]}
                    tool = "add_struct_function_param"
                else:
                    param["param_type"] = args["type"]
                    tool = "add_function_param"
                result = context.bp_call(tool, param)
            elif action in ("custom_event", "add_node", "variable_get", "variable_set", "cast", "call"):
                if args["alias"] in context.aliases:
                    raise UnrealMCPError(f"Node alias already exists: {args['alias']}")
                creation = {"graph": context.graph, "pos": args["position"]}
                if action == "add_node" and "class" in args:
                    creation['declaring_class'] = {'refPath': args['class']}
                if action == "custom_event":
                    events = context.bp_call("list_events", {"blueprint": context.blueprint})
                    if any(e["name"].casefold() == args["name"].casefold() for e in events):
                        raise UnrealMCPError(f"Event name already exists or is inherited: {args['name']}")
                    type_id = "AddEvent|Custom|" + args["name"]
                elif action == "call":
                    owner = self.resolve_blueprint(args["owner"])
                    functions = context.bp_call("list_functions", {"blueprint": owner})
                    names = [f["name"] for f in functions if f["name"].casefold() == args["name"].casefold()]
                    if len(names) != 1:
                        raise UnrealMCPError(f"Expected one function named {args['name']} on {owner}: {names}")
                    creation["declaring_class"] = context.blueprint_class(owner)
                    title = "".join(names[0].split())
                    types = context.bp_call("find_node_types", {"graph": context.graph, "type_id_filter": title, "context_pins": []})
                    prefix = "Class|" + "".join(owner["refPath"].rsplit(".", 1)[-1].split()) + "|"
                    matches = [t for t in types if t.startswith(prefix) and t.rsplit("|", 1)[-1] == title]
                    if len(matches) != 1:
                        raise UnrealMCPError(f"Expected one callable node for {title} on {owner}: {matches}")
                    type_id = matches[0]
                elif action == "cast":
                    owner = self.resolve_blueprint(args["class"])
                    creation["declaring_class"] = context.blueprint_class(owner)
                    title = "CastTo" + "".join(owner["refPath"].rsplit(".", 1)[-1].split())
                    types = context.bp_call("find_node_types", {"graph": context.graph, "type_id_filter": title, "context_pins": []})
                    matches = [t for t in types if t == "Utilities|Casting|" + title]
                    if len(matches) != 1:
                        raise UnrealMCPError(f"Expected one object cast for {owner}: {matches}")
                    type_id = matches[0]
                elif action in ("variable_get", "variable_set"):
                    owner = self.resolve_blueprint(args["owner"]) if "owner" in args else context.blueprint
                    names = context.bp_call("list_variables", {"blueprint": owner})
                    entries = context.bp_call("find_nodes", {
                        "graph": context.graph, "title": "",
                        "node_class": {"refPath": "/Script/BlueprintGraph.K2Node_FunctionEntry"},
                    })
                    if "owner" not in args and len(entries) == 1:
                        names += context.bp_call("list_variables", {"blueprint": context.blueprint, "graph": context.graph})
                    matches = [name for name in names if name.casefold() == args["name"].casefold()]
                    if len(matches) != 1:
                        raise UnrealMCPError(f"Expected one member or local variable named {args['name']}; found {matches}")
                    title = ("Get" if action == "variable_get" else "Set") + "".join(matches[0].split())
                    types = context.bp_call("find_node_types", {
                        "graph": context.graph, "type_id_filter": title, "context_pins": [],
                    })
                    if "owner" in args:
                        creation["declaring_class"] = context.blueprint_class(owner)
                        prefix = "Class|" + "".join(owner["refPath"].rsplit(".", 1)[-1].split()) + "|"
                    else:
                        prefix = "Variables|"
                    matches = [t for t in types if t.startswith(prefix) and t.rsplit("|", 1)[-1] == title]
                    if len(matches) != 1:
                        raise UnrealMCPError(f"Expected one variable node type for {title}; found {matches}")
                    type_id = matches[0]
                else:
                    type_id = args["type"]
                result = context.bp_call("create_node", {**creation, "type_id": type_id})
                context.aliases[args["alias"]] = result
            elif action == "set_pin":
                pin = context.pin_ref(args["pin"], "input", require_unconnected=True)
                context.bp_call("set_pin_value", {"pin": pin, "value": args["value"]})
                result = {"pin": pin, "value": context.bp_call("get_pin_value", {"pin": pin})}
            elif action == "position":
                context.bp_call("set_node_position", {"node": context.node_ref(args["node"]), "pos": args["position"]})
            elif action == "delete_node":
                node = context.node_ref(args["node"])
                context.bp_call("delete_node", {"node": node})
                context.aliases = {k: v for k, v in context.aliases.items() if v != node}
            elif action in ("bind", "unbind"):
                output_pin = context.pin_ref(args["output"], "output")
                input_pin = context.pin_ref(args["input"], "input")
                context.bp_call("connect_pins" if action == "bind" else "break_pins", {
                    "output_pin": output_pin, "input_pin": input_pin,
                })
            elif action == "arrange":
                nodes = [context.node_ref(n) for n in args["nodes"].split(",")]
                if len({n["refPath"] for n in nodes}) != len(nodes):
                    raise UnrealMCPError("arrange requires distinct nodes")
                result = []
                for index, node in enumerate(nodes):
                    pos = {"x": args["position"]["x"] + index * 280, "y": args["position"]["y"]}
                    context.bp_call("set_node_position", {"node": node, "pos": pos})
                    result.append({"node": node, "position": pos})
                    context.report({"line": line, "status": "positioned", "node": node, "position": pos})
    return result
