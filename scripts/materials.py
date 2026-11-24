"""Material expression graphs and instance parameters through existing Unreal tools."""
import json
from urllib.error import URLError
from .errors import UnrealMCPError

MATERIAL = 'editor_toolset.toolsets.material.MaterialTools'
INSTANCE = 'editor_toolset.toolsets.material_instance.MaterialInstanceTools'
OBJECT = 'editor_toolset.toolsets.object.ObjectTools'
FUNCTION_CLASSES = ('/Script/Engine.MaterialFunction', '/Script/Engine.MaterialFunctionMaterialLayer',
                    '/Script/Engine.MaterialFunctionMaterialLayerBlend')


def call(context, toolset, tool, arguments):
    library = context.library
    if toolset not in library.schemas:
        schema = json.loads(library._tool('describe_toolset', {'toolset_name': toolset}))
        library.schemas[toolset] = {t['name'].rsplit('.', 1)[-1]: t for t in schema['tools']}
    stable = {'get_class', 'list_properties', 'list_expression_classes'}
    reads = stable | {'get_expressions', 'get_properties', 'get_expression_inputs',
                      'get_expression_input_names', 'get_expression_output_names',
                      'get_property_input', 'list_parameters'}
    key_arguments = {'class': call(context, OBJECT, 'get_class', arguments)} if tool == 'list_properties' else arguments
    key = (toolset, tool, json.dumps(key_arguments, sort_keys=True))
    if tool in reads and key in context.material_cache:
        return context.material_cache[key]
    membership_key = None
    if tool in ('add_expression', 'delete_expression'):
        membership_key = (MATERIAL, 'get_expressions', json.dumps({'material_or_function': arguments['material_or_function']}, sort_keys=True))
    members = context.material_cache.get(membership_key)
    live_reads = {'get_scalar_parameter', 'get_vector_parameter', 'get_texture_parameter', 'get_static_switch_parameter'}
    if tool not in reads | live_reads:
        # Invalidate before mutation: an error can still leave editor changes.
        for old in list(context.material_cache):
            old_args = json.loads(old[2])
            if tool in ('connect_expressions', 'disconnect_expressions'):
                invalid = old[1] == 'get_expression_inputs' and old_args['expression'] == arguments['to_expression']
            elif tool in ('connect_to_output', 'disconnect_from_output'):
                invalid = old[1] == 'get_property_input'
            elif tool == 'set_properties':
                invalid = old[1] not in stable and old[1] != 'get_expressions'
            elif tool in ('set_scalar_parameter', 'set_vector_parameter', 'set_texture_parameter', 'set_parameter_override'):
                invalid = old[1] not in stable and old[1] != 'list_parameters'
            else:
                invalid = tool == 'recompile' or old[1] not in stable
            if invalid:
                del context.material_cache[old]
    result = library._call(toolset, tool, arguments)
    if tool == 'add_expression':
        class_key = (OBJECT, 'get_class', json.dumps({'instance': result}, sort_keys=True))
        context.material_cache[class_key] = arguments['expression_class']
        if members is not None:
            context.material_cache[membership_key] = members + [result]
    elif tool == 'delete_expression' and members is not None:
        context.material_cache[membership_key] = [node for node in members if node != arguments['expression']]
    if tool in reads:
        context.material_cache[key] = result
    if tool == 'get_expression_inputs':
        names_key = (toolset, 'get_expression_input_names', json.dumps({'expression': arguments['expression']}, sort_keys=True))
        context.material_cache[names_key] = [pin['input_name'] for pin in result]
    return result


BATCH_ACTIONS = {'material_add', 'material_set', 'material_position', 'material_bind',
                 'material_output', 'material_compile', 'set_asset_properties',
                 'material_delete', 'material_unbind', 'material_unbind_output',
                 'material_parameter_set', 'material_override'}


def require_editor(context):
    if not context.material_dependency_checked:
        dependency = context.library.editor_dependency_status()
        if dependency['state'] != 'current':
            raise UnrealMCPError('Material batches/maps require the current editor dependency; run dependencies and load its returned code')
        if dependency['native']['state'] != 'current' or dependency['native']['version'] < 12:
            raise UnrealMCPError('Material operations require loaded UnrealBPBridge protocol 12; rebuild and activate the native module')
        context.material_dependency_checked = True


def execute_batch(library, context, commands):
    if context.selected_asset is None or context.blueprint is not None:
        raise UnrealMCPError('Select or create a Material/MaterialFunction before a material write batch')
    require_editor(context)
    context.material_cache.clear()
    result = json.loads(library._call(library.ASSET_CREATION, 'material_write_batch', {
        'material_or_function': context.selected_asset,
        'commands': json.dumps([{'line': line, 'action': action, 'args': args} for line, action, args in commands]),
        'aliases': json.dumps({name: ref['refPath'] for name, ref in context.aliases.items()})}))
    context.aliases = {name: {'refPath': path} for name, path in result['aliases'].items()}
    for entry in result['completed']:
        context.report({**entry, 'status': 'completed'})
    if result['failed'] is not None:
        message = f"Material batch stopped: {json.dumps(result['failed'])}; completed {len(result['completed'])} commands"
        context.report({'status': 'failed', 'action': 'material_write_batch',
                          'failed': result['failed'], 'aliases': result['aliases']})
        recovery_action = 'material_map'
        try:
            recovery_action = ('material_parameters' if asset_class(context, context.selected_asset) ==
                               '/Script/Engine.MaterialInstanceConstant' else 'material_map')
            current_map = execute(library, context, result['failed']['line'], recovery_action, {})
        except (UnrealMCPError, URLError, OSError, json.JSONDecodeError) as error:
            context.material_cache.clear()
            context.report({'status': 'failed', 'action': recovery_action,
                              'reason': 'batch_failure', 'error': str(error)})
            raise UnrealMCPError(f"{message}; current map read failed: {error}; read current map before resuming") from error
        context.report({'status': 'completed', 'action': recovery_action,
                          'reason': 'batch_failure', 'result': current_map})
        raise UnrealMCPError(f"{message}; current map emitted; inspect it before resuming")
    return result


def select(context, asset):
    context.selected_asset = asset
    context.blueprint = None
    context.graph = None
    context.aliases.clear()
    return asset


def asset_class(context, asset):
    return call(context, OBJECT, 'get_class', {'instance': asset})['refPath']


def expression(context, value):
    node = context.aliases[value] if value in context.aliases else {'refPath': value}
    nodes = call(context, MATERIAL, 'get_expressions', {'material_or_function': context.selected_asset})
    if node not in nodes:
        raise UnrealMCPError(f'Expression does not belong to selected material/function: {value}')
    return node


def properties(context, node, values=None):
    raw = call(context, OBJECT, 'list_properties', {'instance': node})
    schema = {} if raw == '' else json.loads(raw)
    if values is not None:
        unknown = values.keys() - schema.keys()
        if unknown:
            raise UnrealMCPError(f'Unknown expression properties: {sorted(unknown)}')
        require_editor(context)
        context.material_cache.clear()
        if context.library._call(context.library.ASSET_CREATION, 'material_properties', {'instance': node, 'values': json.dumps(values)}) is not True:
            raise UnrealMCPError(f'Expression property edit failed: {node}')
        if context.defer_material_reads:
            return {'expression': node, 'readback': 'deferred'}
    names = list(schema)
    data = json.loads(call(context, OBJECT, 'get_properties', {'instance': node, 'properties': names})) if names else {}
    return {'schema': schema, 'values': data}


def info(context, asset, node):
    props = properties(context, node)
    return {'expression': node, 'class': call(context, OBJECT, 'get_class', {'instance': node}),
            'position': {'x': props['values']['materialExpressionEditorX'], 'y': props['values']['materialExpressionEditorY']},
            'properties': props,
            'inputs': call(context, MATERIAL, 'get_expression_inputs', {'material_or_function': asset, 'expression': node}),
            'outputs': call(context, MATERIAL, 'get_expression_output_names', {'expression': node})}


def pin(context, address, direction):
    node_name, separator, name = address.rpartition('::')
    if not separator:
        raise UnrealMCPError('Expression pin requires NODE::PIN_NAME; use NODE:: for unnamed output')
    node = expression(context, node_name)
    names = call(context, MATERIAL, f'get_expression_{direction}_names', {'expression': node})
    if names.count(name) != 1:
        raise UnrealMCPError(f'Expected one {direction} pin {name!r} on {node}: {names}')
    return node, name


def output_properties(library):
    # The reflected enum also contains range markers and obsolete entries, not output sockets.
    schema = library.schemas[MATERIAL]['get_property_input']['inputSchema']['properties']['material_property']
    return [p for p in schema['enum'] if not p.endswith('_DEPRECATED') and p not in
            ('MP_LastCustomizedUVs', 'MP_NumCustomizedUVs', 'MP_CustomOutput')]


def execute(self, context, line, action, args):
    if action in ('material_select', 'material_instance_create', 'material_map', 'material_inspect', 'material_parameters'):
        context.material_cache.clear()
    if action == 'material_select':
        if not args['path'].startswith('/'):
            raise UnrealMCPError('material requires an exact Unreal asset path')
        asset = self._call(self.ASSETS, 'load_asset', {'asset_path': args['path']})
        if asset_class(context, asset) not in ('/Script/Engine.Material', '/Script/Engine.MaterialInstanceConstant') + FUNCTION_CLASSES:
            raise UnrealMCPError('Expected Material, MaterialFunction or MaterialInstanceConstant')
        return select(context, asset)
    if action == 'material_instance_create':
        if context.folder is None:
            raise UnrealMCPError('Select folder before creating a material instance')
        parent = self._call(self.ASSETS, 'load_asset', {'asset_path': args['path']})
        if asset_class(context, parent) not in ('/Script/Engine.Material', '/Script/Engine.MaterialInstanceConstant'):
            raise UnrealMCPError('Instance parent must be a Material or MaterialInstanceConstant')
        destination = context.folder + '/' + args['name']
        if self._call(self.ASSETS, 'exists', {'path': destination}):
            raise UnrealMCPError(f'Destination already exists: {destination}')
        return select(context, call(context, INSTANCE, 'create', {'folder_path': context.folder, 'asset_name': args['name'], 'parent': parent}))
    asset = context.selected_asset
    if asset is None:
        raise UnrealMCPError('Select or create a material asset first')
    kind = asset_class(context, asset) if action != 'material_map' else None
    if action in ('material_parameters', 'material_parameter_get', 'material_parameter_set', 'material_override'):
        if kind not in ('/Script/Engine.Material', '/Script/Engine.MaterialInstanceConstant'):
            raise UnrealMCPError('Parameter operations require Material or MaterialInstanceConstant')
        require_editor(context)
        if action == 'material_parameters':
            return json.loads(self._call(self.ASSET_CREATION, 'material_parameters', {'material': asset}))
        if kind != '/Script/Engine.MaterialInstanceConstant':
            raise UnrealMCPError('Parameter values and overrides require a MaterialInstanceConstant')
        return json.loads(self._call(self.ASSET_CREATION, 'material_parameter',
                                    {'instance': asset, 'action': action, 'arguments': json.dumps(args)}))
    if action != 'material_map' and kind not in ('/Script/Engine.Material',) + FUNCTION_CLASSES:
        raise UnrealMCPError('Expression graph operations require Material or MaterialFunction')
    owner = {'material_or_function': asset}
    if action == 'material_types':
        return call(context, MATERIAL, 'list_expression_classes', {**owner, 'search': args['filter']})
    if action == 'material_add':
        if args['alias'] in context.aliases:
            raise UnrealMCPError(f'Alias already exists: {args["alias"]}')
        cls = {'refPath': args['class']}
        classes = [ref for key, entries in context.material_cache.items()
                   if key[:2] == (MATERIAL, 'list_expression_classes')
                   and json.loads(key[2])['material_or_function'] == asset for ref in entries]
        if cls not in classes:
            classes = call(context, MATERIAL, 'list_expression_classes', {**owner, 'search': args['class']})
        if cls not in classes:
            raise UnrealMCPError(f'Expression class unavailable in this graph: {args["class"]}')
        call(context, MATERIAL, 'get_expressions', owner)
        node = call(context, MATERIAL, 'add_expression', {**owner, 'expression_class': cls, **args['position']})
        context.aliases[args['alias']] = node
        if context.defer_material_reads:
            return {'expression': node, 'readback': 'deferred'}
        return info(context, asset, node)
    if action == 'material_map':
        require_editor(context)
        if MATERIAL not in self.schemas:
            schema = json.loads(self._tool('describe_toolset', {'toolset_name': MATERIAL}))
            self.schemas[MATERIAL] = {t['name'].rsplit('.', 1)[-1]: t for t in schema['tools']}
        outputs = output_properties(self)
        result = json.loads(self._call(self.ASSET_CREATION, 'material_graph', {**owner, 'outputs': outputs}))
        kind = result['class']
        def remember(toolset, tool, arguments, value):
            context.material_cache[(toolset, tool, json.dumps(arguments, sort_keys=True))] = value
        remember(OBJECT, 'get_class', {'instance': asset}, {'refPath': result['class']})
        remember(MATERIAL, 'get_expressions', owner, [n['expression'] for n in result['expressions']])
        for node in result['expressions']:
            ref = node['expression']
            props = node['properties']
            remember(OBJECT, 'get_class', {'instance': ref}, node['class'])
            remember(OBJECT, 'list_properties', {'class': node['class']}, json.dumps(props['schema']))
            remember(OBJECT, 'get_properties', {'instance': ref, 'properties': list(props['schema'])}, json.dumps(props['values']))
            remember(MATERIAL, 'get_expression_inputs', {**owner, 'expression': ref}, node['inputs'])
            remember(MATERIAL, 'get_expression_input_names', {'expression': ref}, [p['input_name'] for p in node['inputs']])
            remember(MATERIAL, 'get_expression_output_names', {'expression': ref}, node['outputs'])
        if kind == '/Script/Engine.Material':
            for prop, value in result['material_outputs'].items():
                remember(MATERIAL, 'get_property_input', {'material': asset, 'material_property': prop}, value)
        return result
    if action in ('material_inspect', 'material_set', 'material_position', 'material_delete'):
        node = expression(context, args['node'])
        if action == 'material_delete':
            call(context, MATERIAL, 'delete_expression', {**owner, 'expression': node})
            for alias in [a for a, ref in context.aliases.items() if ref == node]:
                del context.aliases[alias]
            return {'deleted': node}
        if action in ('material_set', 'material_position'):
            values = args['values'] if action == 'material_set' else {'materialExpressionEditorX': args['position']['x'], 'materialExpressionEditorY': args['position']['y']}
            result = properties(context, node, values)
            if context.defer_material_reads:
                return result
        return info(context, asset, node)
    if action in ('material_bind', 'material_unbind'):
        dest, input_name = pin(context, args['input'], 'input')
        if action == 'material_bind':
            src, output_name = pin(context, args['output'], 'output')
            call(context, MATERIAL, 'connect_expressions', {'from_expression': src, 'from_output_name': output_name, 'to_expression': dest, 'to_input_name': input_name})
        else:
            call(context, MATERIAL, 'disconnect_expressions', {'to_expression': dest, 'to_input_name': input_name})
        if context.defer_material_reads:
            return {'expression': dest, 'readback': 'deferred'}
        return call(context, MATERIAL, 'get_expression_inputs', {**owner, 'expression': dest})
    if action in ('material_output', 'material_unbind_output'):
        if kind != '/Script/Engine.Material':
            raise UnrealMCPError('Material outputs require Material; functions use FunctionOutput expressions')
        require_editor(context)
        src, output_name = pin(context, args['output'], 'output') if action == 'material_output' else (None, '')
        context.material_cache.clear()
        return json.loads(self._call(self.ASSET_CREATION, 'material_output', {
            'material': asset, 'property_name': args['property'], 'action': action,
            'expression': src, 'output_name': output_name}))
    if action in ('material_layout', 'material_compile'):
        if action == 'material_layout':
            call(context, MATERIAL, 'layout_expressions', owner)
            return {'asset': asset, 'operation': action}
        require_editor(context)
        context.material_cache.clear()
        result = json.loads(self._call(self.ASSET_CREATION, 'material_compile', owner))
        if not result['success']:
            raise UnrealMCPError('Material compilation failed: ' + json.dumps(result))
        return result
    raise UnrealMCPError(f'Unhandled material command: {action}')
