"""Asset catalog, creation and file operations."""
import json
from .errors import UnrealMCPError

ACTIONS = frozenset({'enum_entries', 'add_enum_entries', 'rename_enum_entries', 'delete_enum_entries', 'datatable_select', 'datatable_schema', 'datatable_list_rows', 'datatable_get_rows', 'datatable_add_rows', 'datatable_set_rows', 'datatable_remove_rows', 'datatable_rename_rows', 'set_asset_properties', 'edit_struct', 'struct_fields', 'delete_struct_field', 'move_struct_field', 'create_physics_asset', 'list_folders', 'create_material_function', 'list_assets', 'move_asset', 'asset_dependencies', 'find_asset_types', 'create_asset', 'find_row_structs', 'create_datatable', 'create_material', 'copy_asset', 'asset_referencers', 'folder', 'save', 'refresh_asset_types', 'delete_asset', 'inspect_asset'})

def asset_factories(self, refresh=False):
    if refresh or self.factory_catalog is None:
        dependency = self.editor_dependency_status()
        if dependency["state"] != "current":
            raise UnrealMCPError(f"Editor dependency is {dependency['state']}; run dependencies --project PROJECT, apply its load_code in Unreal Python, then verify dependencies --check")
    if self.ASSET_CREATION not in self.schemas:
        schema = json.loads(self._tool("describe_toolset", {"toolset_name": self.ASSET_CREATION}))
        self.schemas[self.ASSET_CREATION] = {t["name"].rsplit(".", 1)[-1]: t for t in schema["tools"]}
    if refresh or self.factory_catalog is None:
        self.factory_catalog = json.loads(self._call(self.ASSET_CREATION, "catalog", {}))
    return self.factory_catalog

def inspect_asset(self, path, properties=()):
    asset = self._call(self.ASSETS, "load_asset", {"asset_path": path})
    path = asset["refPath"]
    toolset = "editor_toolset.toolsets.object.ObjectTools"
    if toolset not in self.schemas:
        tools = json.loads(self._tool("describe_toolset", {"toolset_name": toolset}))
        self.schemas[toolset] = {t["name"].rsplit(".", 1)[-1]: t for t in tools["tools"]}
    properties_class = self._call(toolset, "get_class", {"instance": asset})
    if not properties_class:
        raise UnrealMCPError(f"Asset has no class for property inspection: {path}")
    raw_schema = self._call(toolset, "list_properties", {"instance": asset})
    # Unreal returns empty text when a valid class has no visible properties.
    schema = {} if raw_schema == "" else json.loads(raw_schema)
    unknown = set(properties) - schema.keys()
    if unknown:
        raise UnrealMCPError(f"Properties absent from readable schema: {sorted(unknown)}; inspect registry_tags for asset metadata")
    result = {
        "asset": asset,
        "asset_class": self._call(self.ASSETS, "get_asset_class", {"asset_path": path}),
        "registry_tags": self._call(self.ASSETS, "get_asset_tags", {"asset_path": path}),
        "properties_class": properties_class,
        "property_scope": "Blueprints: generated class defaults; other assets: instance",
        "property_schema": schema,
    }
    if properties:
        result["property_values"] = json.loads(self._call(toolset, "get_properties", {
            "instance": asset, "properties": list(properties),
        }))
    return result


def execute(self, context, line, action, args):
    result = None
    if action.startswith('datatable_'):
        toolset = 'editor_toolset.toolsets.data_table.DataTableTools'
        if toolset not in self.schemas:
            schema = json.loads(self._tool('describe_toolset', {'toolset_name': toolset}))
            self.schemas[toolset] = {tool['name'].rsplit('.', 1)[-1]: tool for tool in schema['tools']}
        if action == 'datatable_select':
            asset = self._call(self.ASSETS, 'load_asset', {'asset_path': args['path']})
            schema = json.loads(self._call(toolset, 'get_schema', {'data_table': asset}))
            context.selected_asset = asset
            context.blueprint = None
            context.graph = None
            context.aliases.clear()
            result = {'asset': asset, 'schema': schema}
        else:
            if context.selected_asset is None:
                raise UnrealMCPError(f'Line {line}: select or create a DataTable first')
            arguments = {'data_table': context.selected_asset}
            tool = {'datatable_schema': 'get_schema', 'datatable_list_rows': 'list_rows',
                    'datatable_get_rows': 'get_rows', 'datatable_add_rows': 'add_rows',
                    'datatable_set_rows': 'set_rows', 'datatable_remove_rows': 'remove_rows',
                    'datatable_rename_rows': 'rename_rows'}[action]
            if 'rows' in args:
                arguments['row_names'] = args['rows']
            elif 'values' in args:
                arguments['values'] = json.dumps(args['values'])
            elif 'renames' in args:
                arguments['renames'] = args['renames']
            result = self._call(toolset, tool, arguments)
            if action in ('datatable_schema', 'datatable_get_rows'):
                result = json.loads(result)
    elif action == "inspect_asset":
        result = inspect_asset(self, args["path"])
    elif action == "set_asset_properties":
        inspected = inspect_asset(self, args['path'], list(args['values']))
        asset = inspected['asset']
        toolset = "editor_toolset.toolsets.object.ObjectTools"
        if self._call(toolset, "set_properties", {"instance": asset, "values": json.dumps(args['values'])}) is not True:
            raise UnrealMCPError(f"Asset property edit failed: {args['path']}")
        result = {"before": inspected['property_values'], "after": json.loads(self._call(toolset, "get_properties", {"instance": asset, "properties": list(args['values'])}))}
        context.selected_asset = asset
        context.blueprint = None
        context.graph = None
        context.aliases.clear()
    elif action in ('enum_entries', 'add_enum_entries', 'rename_enum_entries', 'delete_enum_entries'):
        dependency = self.editor_dependency_status()
        if dependency['state'] != 'current' or dependency['native']['state'] != 'current':
            raise UnrealMCPError('Enum entry operations require the current editor dependency and native bridge; run dependencies --check')
        asset = self._call(self.ASSETS, 'load_asset', {'asset_path': args['path']})
        arguments = {'enum': asset}
        tool = 'enum_entries'
        if action != 'enum_entries':
            tool = 'edit_enum_entries'
            arguments.update(action=action.removesuffix('_enum_entries'),
                             entries=json.dumps(args['ids'] if action == 'delete_enum_entries' else args['names']))
        result = json.loads(self._call(self.ASSET_CREATION, tool, arguments))
        if action != 'enum_entries':
            context.selected_asset = asset
            context.blueprint = None
            context.graph = None
            context.aliases.clear()
    elif action in ("edit_struct", "struct_fields", "delete_struct_field", "move_struct_field"):
        dependency = self.editor_dependency_status()
        if dependency['state'] != 'current' or dependency['native']['state'] != 'current':
            raise UnrealMCPError('Struct editing requires the current editor dependency and native bridge; run dependencies --check')
        asset = self._call(self.ASSETS, "load_asset", {"asset_path": args["path"]})
        arguments = {"struct": asset}
        if action == "edit_struct":
            arguments['fields'] = json.dumps(args['fields'])
        elif action in ("delete_struct_field", "move_struct_field"):
            arguments['name'] = args['name']
            if action == "move_struct_field":
                arguments.update(position=args['position'], relative_to=args['relative_to'])
        result = json.loads(self._call(self.ASSET_CREATION, action, arguments))
        if action != "struct_fields":
            context.selected_asset = asset
            context.blueprint = None
            context.graph = None
            context.aliases.clear()
    elif action == "folder":
        context.folder = args["folder"]
        result = context.folder
    elif action in ("find_asset_types", "refresh_asset_types"):
        catalog = self.asset_factories(refresh=action == "refresh_asset_types")
        result = {**catalog, "factories": [f for f in catalog["factories"]
                  if action == "refresh_asset_types" or args["filter"].casefold() in json.dumps(f).casefold()]}
    elif action == "create_asset":
        if context.folder is None:
            raise UnrealMCPError(f"Line {line}: select folder first")
        catalog = self.asset_factories()
        candidates = [f for f in catalog["factories"] if args["type"] in
                      (f["factory"], f["factory"].rsplit(".", 1)[-1], f["asset_class"])]
        if len(candidates) != 1:
            raise UnrealMCPError(f"Expected one exact factory for {args['type']}: {candidates}; use find asset_types filter TEXT")
        factory = candidates[0]
        if not factory["creation_supported"]:
            raise UnrealMCPError(f"Factory is discovered but creation is not supported: {factory}")
        options = args.get("options", {})
        missing = set(factory["required_options"]) - options.keys()
        unknown = options.keys() - factory["options"].keys()
        if missing or unknown:
            raise UnrealMCPError(f"Factory options: missing={sorted(missing)}, unknown={sorted(unknown)}")
        context.selected_asset = self._call(self.ASSET_CREATION, "create", {
            "folder_path": context.folder, "asset_name": args["name"],
            "factory_path": factory["factory"], "options": json.dumps(options),
        })
        context.blueprint = context.selected_asset if factory["asset_class"] == "/Script/Engine.Blueprint" else None
        context.graph = None
        context.aliases.clear()
        result = context.selected_asset
    elif action == "create_physics_asset":
        toolset = "PhysicsToolsets.PhysicsAssetToolset"
        if toolset not in self.schemas:
            schema = json.loads(self._tool("describe_toolset", {"toolset_name": toolset}))
            self.schemas[toolset] = {t["name"].rsplit(".", 1)[-1]: t for t in schema["tools"]}
        mesh = self._call(self.ASSETS, "load_asset", {"asset_path": args["path"]})
        mesh_path = mesh["refPath"].split(".", 1)[0]
        destination = mesh_path + "_PhysicsAsset"
        if self._call(self.ASSETS, "exists", {"path": destination}):
            raise UnrealMCPError(f"Destination already exists: {destination}")
        context.selected_asset = self._call(toolset, "CreateFromMesh", {
            "meshPath": mesh_path, "bAssignToMesh": False,
        })
        context.blueprint = None
        context.graph = None
        context.aliases.clear()
        result = context.selected_asset
    elif action in ("list_assets", "list_folders"):
        if context.folder is None:
            raise UnrealMCPError(f"Line {line}: select folder first")
        result = self._call(self.ASSETS, "find_assets" if action == "list_assets" else "list_folders",
                            {"folder_path": context.folder, "name": "", "recursive": True} if action == "list_assets"
                            else {"root_path": context.folder, "recursive": True})
    elif action == "save":
        if context.selected_asset is None:
            raise UnrealMCPError(f"Line {line}: select or create an asset first")
        result = self._call(self.ASSETS, "save_assets", {"asset_paths": [context.selected_asset["refPath"]]})
        if result is not True:
            raise UnrealMCPError(f"Could not save {context.selected_asset['refPath']}")
    elif action in ("delete_asset", "move_asset", "copy_asset", "asset_referencers", "asset_dependencies"):
        source_asset = self._call(self.ASSETS, "load_asset", {"asset_path": args["path"]})
        source_path = source_asset["refPath"]
        if action in ("asset_referencers", "asset_dependencies"):
            result = self._call(self.ASSETS, "get_referencers" if action == "asset_referencers" else "get_dependencies", {"asset_path": source_path})
        else:
            arguments = {"path": source_path}
            if action != "delete_asset":
                if self._call(self.ASSETS, "exists", {"path": args["destination"]}):
                    raise UnrealMCPError(f"Destination already exists: {args['destination']}")
                arguments["new_path"] = args["destination"]
            if action != "copy_asset" and context.selected_asset == source_asset:
                context.selected_asset = None
                context.blueprint = None
                context.graph = None
                context.aliases.clear()
            tool = {"delete_asset": "delete", "move_asset": "move", "copy_asset": "duplicate"}[action]
            if self._call(self.ASSETS, tool, arguments) is not True:
                raise UnrealMCPError(f"{action} failed: {arguments}")
            if action == "delete_asset":
                if self._call(self.ASSETS, "exists", {"path": source_path}):
                    raise UnrealMCPError(f"Deleted asset still exists: {source_path}")
                result = {"deleted": source_path}
            else:
                context.selected_asset = self._call(self.ASSETS, "load_asset", {"asset_path": args["destination"]})
                context.blueprint = None
                context.graph = None
                context.aliases.clear()
                result = {"source": source_path, "asset": context.selected_asset}
    elif action in ("create_material", "create_material_function", "create_datatable", "find_row_structs"):
        toolset = "editor_toolset.toolsets.data_table.DataTableTools" if action in ("create_datatable", "find_row_structs") else "editor_toolset.toolsets.material.MaterialTools"
        if toolset not in self.schemas:
            schema = json.loads(self._tool("describe_toolset", {"toolset_name": toolset}))
            self.schemas[toolset] = {t["name"].rsplit(".", 1)[-1]: t for t in schema["tools"]}
        if action == "find_row_structs":
            result = self._call(toolset, "search_row_structs", {"struct_name": args["filter"]})
        else:
            if context.folder is None:
                raise UnrealMCPError(f"Line {line}: select folder first")
            creation = {"folder_path": context.folder, "asset_name": args["name"]}
            if action == "create_datatable":
                rows = self._call(toolset, "search_row_structs", {"struct_name": "*"})
                row = {"refPath": args["row_struct"]}
                if row not in rows:
                    raise UnrealMCPError(f"Not an available DataTable row struct: {args['row_struct']}; use find row_structs filter WILDCARD")
                creation["schema"] = row
            tool = {"create_material": "create_material", "create_material_function": "create_function", "create_datatable": "create"}[action]
            context.selected_asset = self._call(toolset, tool, creation)
            context.blueprint = None
            context.graph = None
            context.aliases.clear()
            result = context.selected_asset
    return result
