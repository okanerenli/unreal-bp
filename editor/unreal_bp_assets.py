"""Factory-backed asset creation registered with Unreal's existing ToolsetRegistry."""
import json
import warnings
from pathlib import Path
import unreal
import toolset_registry
from toolset_registry.helpers import create_asset
from toolset_registry.registration import Registration
from unreal_bp_console import execute_python
from editor_toolset.toolsets.blueprint_node import NodeInfo
from editor_toolset.toolsets.blueprint import BlueprintTools, ContainerType
from unreal_bp_runtime.install_editor import source_hash
from unreal_bp_runtime.library import UnrealLibrary
from unreal_bp_runtime.context import CommandContext
from unreal_bp_runtime.errors import UnrealMCPError

# Hash the deployed editor files and shared command runtime together.
LOADED_SOURCE_HASH = source_hash(Path(__file__).parent)

# Only reviewed factories run without interactive ConfigureProperties dialogs.
RULES = json.loads(Path(__file__).with_name('creation_rules.json').read_text())


def native_status(minimum_version=16):
    bridge = getattr(unreal, 'UnrealBPBridgeLibrary', None)
    if bridge is None:
        return {'state': 'not_loaded', 'expected_version': minimum_version}
    version = bridge.get_protocol_version()
    return {'state': 'current' if minimum_version <= version <= 16 else 'outdated', 'version': version,
            'expected_version': minimum_version}


def unavailable_settings(rule):
    failures = []
    for requirement in rule.get('required_settings', []):
        cls = unreal.load_class(None, requirement['class'])
        if cls is None:
            raise ValueError(f"Required settings class is unavailable: {requirement['class']}")
        name = requirement['property']
        actual = json.loads(unreal.ToolsetLibrary.get_object_properties(unreal.get_default_object(cls), [name]))[name]
        if type(actual) is not bool:
            raise ValueError(f"Required settings property must be boolean: {requirement['class']}.{name}")
        if actual != requirement['value']:
            failures.append(f"{requirement['class']}.{name} must be {requirement['value']}")
    return failures


def factory_class(path):
    cls = unreal.load_class(None, path)
    if cls is None or not unreal.MathLibrary.class_is_child_of(cls, unreal.Factory.static_class()):
        raise ValueError(f'Not a Factory class: {path}')
    return cls


class EditorCommandLibrary(UnrealLibrary):
    """Use the existing command handlers through the in-process tool registry."""

    supports_async_tools = False

    def connect(self):
        self.toolsets = {schema['name']: schema for schema in json.loads(unreal.ToolsetRegistry.get_all_toolset_json_schemas())}
        self.available_toolsets = '\n'.join('- ' + name + ':' for name in self.toolsets)
        for name in (self.ASSETS, self.BLUEPRINTS):
            self.schemas[name] = {tool['name'].rsplit('.', 1)[-1]: tool for tool in self.toolsets[name]['tools']}

    def _tool(self, name, arguments):
        if name == 'describe_toolset':
            return json.dumps(self.toolsets[arguments['toolset_name']])
        if name != 'call_tool':
            raise UnrealMCPError(f'Unsupported editor transport operation: {name}')
        with toolset_registry.tool_raising_exceptions():
            result = unreal.ToolsetRegistry.execute_tool(arguments['toolset_name'], arguments['tool_name'], json.dumps(arguments['arguments']))
        if not result.is_complete:
            raise UnrealMCPError(f"Tool did not complete synchronously: {arguments['toolset_name']}.{arguments['tool_name']}; execution may still be pending, inspect editor before resuming")
        if result.error:
            raise UnrealMCPError(result.error)
        return result.value

    def editor_dependency_status(self):
        schema = self.toolsets[self.ASSET_CREATION]
        self.schemas[self.ASSET_CREATION] = {tool['name'].rsplit('.', 1)[-1]: tool for tool in schema['tools']}
        return {**json.loads(AssetCreationTools.dependency_status()), 'state': 'current'}


@unreal.uclass()
class AssetCreationTools(unreal.ToolsetDefinition):
    """Discover factory metadata and create assets using reviewed factory requirements."""

    @toolset_registry.tool_call
    @staticmethod
    def dependency_status() -> str:
        """Report the code loaded in this editor, not merely the current file on disk."""
        return json.dumps({'loaded_hash': LOADED_SOURCE_HASH, 'native': native_status(),
                           'module': str(Path(__file__).resolve()),
                           'project': unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())})

    @toolset_registry.tool_call
    @staticmethod
    def python_console(source: str, mode: str = 'exec') -> str:
        """Run explicit Python in the editor and return native result and captured logs."""
        return execute_python(source, mode)

    @toolset_registry.tool_call
    @staticmethod
    def command_batch(source: str, state: str, expected_hash: str, batch_material_writes: bool = False) -> str:
        """Run prepared commands in order using the shared CLI handlers; stop at the first error."""
        if expected_hash != LOADED_SOURCE_HASH:
            raise RuntimeError('Command runtime changed; reload the editor dependency before executing')
        library = EditorCommandLibrary()
        library.connect()
        context = CommandContext(library)
        context.restore(json.loads(state))
        records = []
        context.report = records.append
        failed = None
        try:
            library.run(source, defer_material_reads=context.defer_material_reads,
                        batch_material_writes=batch_material_writes, context=context, batch_commands=False)
        except (ValueError, RuntimeError, TypeError, KeyError) as error:
            started = [entry for entry in records if entry['status'] == 'started']
            failed = {**(started[-1] if started else {}), 'error': str(error)}
        return json.dumps({'records': records, 'state': context.state(), 'failed': failed})

    @toolset_registry.tool_call
    @staticmethod
    def material_write_batch(material_or_function: unreal.Object, commands: str, aliases: str) -> str:
        """Execute serial material writes; return completed lines and an explicit first failure."""
        from editor_toolset.toolsets.material import MaterialTools
        from editor_toolset.toolsets.object import ObjectTools
        if not isinstance(material_or_function, (unreal.Material, unreal.MaterialFunction, unreal.MaterialInstanceConstant)):
            raise ValueError('Expected Material, MaterialFunction or MaterialInstanceConstant')
        entries = json.loads(commands)
        supported = {'material_add', 'material_set', 'material_position', 'material_bind', 'material_output',
                     'material_compile', 'set_asset_properties', 'material_delete', 'material_unbind',
                     'material_unbind_output', 'material_parameter_set', 'material_override'}
        if not isinstance(entries, list) or not entries:
            raise ValueError('commands requires a nonempty array')
        for entry in entries:
            if set(entry) != {'line', 'action', 'args'} or entry['action'] not in supported:
                raise ValueError('Unsupported material batch command')
        is_instance = isinstance(material_or_function, unreal.MaterialInstanceConstant)
        instance_actions = {'material_parameter_set', 'material_override'}
        if any((entry['action'] in instance_actions) != is_instance for entry in entries):
            raise ValueError('Batch actions must match the selected graph or instance')
        nodes = {} if is_instance else {n.get_path_name(): n for n in MaterialTools.get_expressions(material_or_function)}
        names = json.loads(aliases)
        if not isinstance(names, dict) or any(path not in nodes for path in names.values()):
            raise ValueError('Aliases must reference expressions owned by the selected material/function')
        classes = None
        schemas = {}
        completed = []
        def node(value):
            path = names[value] if value in names else value
            if path not in nodes:
                raise ValueError(f'Expression not owned by selected graph: {value}')
            return nodes[path]
        def pin(address, direction):
            alias, separator, name = address.rpartition('::')
            if not separator:
                raise ValueError('Pin requires NODE::NAME')
            expression = node(alias)
            available = (MaterialTools.get_expression_input_names(expression) if direction == 'input'
                         else MaterialTools.get_expression_output_names(expression))
            if list(available).count(name) != 1:
                raise ValueError(f'Expected one {direction} pin {name!r} on {alias}')
            return expression, name
        with toolset_registry.tool_raising_exceptions():
            for entry in entries:
                action, args = entry['action'], entry['args']
                try:
                    if action in instance_actions:
                        result = json.loads(AssetCreationTools.material_parameter(material_or_function, action, json.dumps(args)))
                    elif action == 'material_delete':
                        target = node(args['node'])
                        path = target.get_path_name()
                        MaterialTools.delete_expression(material_or_function, target)
                        del nodes[path]
                        names = {alias: ref for alias, ref in names.items() if ref != path}
                        result = {'deleted': {'refPath': path}}
                    elif action == 'material_unbind':
                        dest, input_name = pin(args['input'], 'input')
                        MaterialTools.disconnect_expressions(dest, input_name)
                        result = {'expression': {'refPath': dest.get_path_name()}, 'readback': 'deferred'}
                    elif action == 'material_add':
                        if args['alias'] in names:
                            raise ValueError(f'Alias already exists: {args["alias"]}')
                        if classes is None:
                            classes = {c.export_text() for c in MaterialTools.list_expression_classes(material_or_function, '')}
                        if args['class'] not in classes:
                            raise ValueError(f'Unavailable expression class: {args["class"]}')
                        cls = unreal.load_class(None, args['class'])
                        if cls is None:
                            raise ValueError(f'Cannot load expression class: {args["class"]}')
                        created = MaterialTools.add_expression(material_or_function, cls, args['position']['x'], args['position']['y'])
                        path = created.get_path_name()
                        nodes[path] = created
                        names[args['alias']] = path
                        result = {'expression': {'refPath': path}, 'readback': 'deferred'}
                    elif action in ('material_set', 'material_position', 'set_asset_properties'):
                        if action == 'set_asset_properties':
                            target = unreal.load_asset(args['path'])
                            if target != material_or_function:
                                raise ValueError('Batch asset properties must target the selected material/function')
                        else:
                            target = node(args['node'])
                        values = ({'materialExpressionEditorX': args['position']['x'], 'materialExpressionEditorY': args['position']['y']}
                                  if action == 'material_position' else args['values'])
                        cls = target.get_class().get_path_name()
                        if cls not in schemas:
                            raw = ObjectTools.list_properties(target)
                            schemas[cls] = {} if raw == '' else json.loads(raw)
                        unknown = values.keys() - schemas[cls].keys()
                        if unknown:
                            raise ValueError(f'Unknown properties: {sorted(unknown)}')
                        if not AssetCreationTools.material_properties(target, json.dumps(values)):
                            raise RuntimeError(f'Property edit failed: {target.get_path_name()}')
                        result = {'expression': {'refPath': target.get_path_name()}, 'readback': 'deferred'}
                    elif action == 'material_bind':
                        src, output = pin(args['output'], 'output')
                        dest, input_name = pin(args['input'], 'input')
                        MaterialTools.connect_expressions(src, output, dest, input_name)
                        result = {'expression': {'refPath': dest.get_path_name()}, 'readback': 'deferred'}
                    elif action in ('material_output', 'material_unbind_output'):
                        src, output = pin(args['output'], 'output') if action == 'material_output' else (None, '')
                        result = json.loads(AssetCreationTools.material_output(material_or_function, args['property'], action, src, output))
                    else:
                        result = json.loads(AssetCreationTools.material_compile(material_or_function))
                        if not result['success']:
                            return json.dumps({'completed': completed, 'aliases': names,
                                               'failed': {'line': entry['line'], 'action': action,
                                                          'error': 'Material compilation failed', 'diagnostics': result}})
                    completed.append({'line': entry['line'], 'action': action, 'result': result})
                except (ValueError, RuntimeError, TypeError, KeyError) as error:
                    return json.dumps({'completed': completed, 'aliases': names,
                                       'failed': {'line': entry['line'], 'action': action, 'error': str(error)}})
        return json.dumps({'completed': completed, 'aliases': names, 'failed': None})

    @toolset_registry.tool_call
    @staticmethod
    def material_graph(material_or_function: unreal.Object, outputs: list[str]) -> str:
        """Read a complete material/function graph in one editor call."""
        from editor_toolset.toolsets.material import MaterialTools
        from editor_toolset.toolsets.object import ObjectTools
        if not isinstance(material_or_function, (unreal.Material, unreal.MaterialFunction)):
            raise ValueError('Expected Material or MaterialFunction')
        def reference(obj):
            return {'refPath': obj.get_path_name()} if obj is not None else 'None'
        def source(entry):
            return {'input_name': str(entry.input_name), 'expression': reference(entry.expression),
                    'output_name': str(entry.output_name)}
        result = {'asset': reference(material_or_function),
                  'class': material_or_function.get_class().get_path_name(), 'expressions': []}
        schemas = {}
        for node in MaterialTools.get_expressions(material_or_function):
            cls = node.get_class().get_path_name()
            if cls not in schemas:
                raw = ObjectTools.list_properties(node)
                schemas[cls] = {} if raw == '' else json.loads(raw)
            schema = schemas[cls]
            values = json.loads(ObjectTools.get_properties(node, list(schema))) if schema else {}
            result['expressions'].append({
                'expression': reference(node), 'class': reference(node.get_class()),
                'position': {'x': values['materialExpressionEditorX'], 'y': values['materialExpressionEditorY']},
                'properties': {'schema': schema, 'values': values},
                'inputs': [source(entry) for entry in MaterialTools.get_expression_inputs(material_or_function, node)],
                'outputs': list(MaterialTools.get_expression_output_names(node))})
        if isinstance(material_or_function, unreal.Material):
            if native_status(11)['state'] != 'current':
                raise RuntimeError('Full material outputs require UnrealBPBridge protocol 11')
            output_data = json.loads(unreal.UnrealBPBridgeLibrary.get_material_outputs(material_or_function, outputs))
            if 'error' in output_data:
                raise RuntimeError(output_data['error'])
            result['material_outputs'] = {name: entry for name, entry in output_data.items() if 'unavailable' not in entry}
            result['unavailable_material_outputs'] = [name for name, entry in output_data.items() if 'unavailable' in entry]
        return json.dumps(result)

    @toolset_registry.tool_call
    @staticmethod
    def material_properties(instance: unreal.Object, values: str) -> bool:
        """Set reflected properties; apply layer stacks atomically before emitting one editor notification."""
        from editor_toolset.toolsets.object import ObjectTools
        data = json.loads(values)
        if isinstance(instance, unreal.MaterialExpressionMaterialAttributeLayers) and 'defaultLayers' in data:
            if native_status(12)['state'] != 'current':
                raise RuntimeError('Atomic layer stack edits require UnrealBPBridge protocol 12')
            if not unreal.UnrealBPBridgeLibrary.set_material_layer_stack(instance, json.dumps(data.pop('defaultLayers'))):
                raise ValueError('Layer stack validation or assignment failed; inspect the current map')
        if data:
            return ObjectTools.set_properties(instance, json.dumps(data))
        return True

    @toolset_registry.tool_call
    @staticmethod
    def material_output(material: unreal.Material, property_name: str, action: str,
                        expression: unreal.MaterialExpression | None = None, output_name: str = '') -> str:
        """Read or edit a material output using the native enum, including Python-hidden entries."""
        from editor_toolset.toolsets.material import MaterialTools
        if native_status(11)['state'] != 'current':
            raise RuntimeError('Material output access requires UnrealBPBridge protocol 11')
        if action == 'material_output':
            success = unreal.UnrealBPBridgeLibrary.connect_material_output(material, property_name, expression, output_name)
        elif action == 'material_unbind_output':
            success = unreal.UnrealBPBridgeLibrary.disconnect_material_output(material, property_name)
        else:
            raise ValueError(f'Unknown material output action: {action}')
        if not success:
            raise RuntimeError(f'Material output edit failed: {property_name}')
        MaterialTools._refresh_editor(material)
        result = json.loads(unreal.UnrealBPBridgeLibrary.get_material_outputs(material, [property_name]))
        if 'error' in result:
            raise RuntimeError(result['error'])
        return json.dumps(result[property_name])

    @toolset_registry.tool_call
    @staticmethod
    def material_compile(material_or_function: unreal.Object) -> str:
        """Compile and return errors plus native expression diagnostics; function results cover its callers."""
        from editor_toolset.toolsets.material import MaterialTools
        if native_status(11)['state'] != 'current':
            raise RuntimeError('Material compile diagnostics require UnrealBPBridge protocol 11')
        if isinstance(material_or_function, unreal.Material):
            materials = [material_or_function]
        elif isinstance(material_or_function, unreal.MaterialFunction):
            unreal.MaterialEditingLibrary.update_material_function(material_or_function)
            materials = [entry.get_asset() for entry in MaterialTools.get_referencing_materials(material_or_function)]
        else:
            raise ValueError('Expected Material or MaterialFunction')
        reports = []
        for material in materials:
            errors = list(unreal.MaterialEditingLibrary.recompile_material(material))
            report = json.loads(unreal.UnrealBPBridgeLibrary.get_material_diagnostics(material))
            if 'error' in report:
                raise RuntimeError(report['error'])
            report['compiler_errors'] = errors
            reports.append(report)
        MaterialTools._refresh_editor(material_or_function)
        return json.dumps({'asset': {'refPath': material_or_function.get_path_name()},
                           'success': all(not r['compiler_errors'] and not r['errors'] and r['finished'] for r in reports),
                           'scope': 'material' if isinstance(material_or_function, unreal.Material) else 'referencing_materials',
                           'validated_material_count': len(reports), 'reports': reports})

    @toolset_registry.tool_call
    @staticmethod
    def material_parameters(material: unreal.MaterialInterface) -> str:
        """List exact parameter identities, including layer/blend association and index."""
        if native_status(11)['state'] != 'current':
            raise RuntimeError('Material parameter identity access requires UnrealBPBridge protocol 11')
        result = json.loads(unreal.UnrealBPBridgeLibrary.get_material_parameters(material))
        if isinstance(result, dict) and 'error' in result:
            raise RuntimeError(result['error'])
        if isinstance(material, unreal.MaterialInstanceConstant):
            for entry in result:
                identity = {key: entry[key] for key in ('name', 'association', 'index')}
                value = json.loads(AssetCreationTools.material_parameter(material, 'material_parameter_get',
                                   json.dumps({'name': json.dumps(identity)})))
                entry.update({'value': value['value'], 'override': value['override']})
        return json.dumps(result)

    @toolset_registry.tool_call
    @staticmethod
    def material_parameter(instance: unreal.MaterialInstanceConstant, action: str, arguments: str) -> str:
        """Read/write an exact scalar/vector/texture/static-switch parameter and return its effective value."""
        if native_status(11)['state'] != 'current':
            raise RuntimeError('Material parameter access requires UnrealBPBridge protocol 11')
        result = json.loads(unreal.UnrealBPBridgeLibrary.edit_material_parameter(instance, action, arguments))
        if 'error' in result:
            raise ValueError(result['error'])
        return json.dumps(result)

    @toolset_registry.tool_call
    @staticmethod
    def create_comment(graph: unreal.EdGraph, text: str, position: unreal.IntPoint, size: unreal.IntPoint) -> unreal.EdGraphNode:
        """Create a Blueprint comment box using the existing graph editor."""
        if size.x <= 0 or size.y <= 0:
            raise ValueError('Comment dimensions must be positive')
        editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
        if editor is None:
            raise ValueError('Comment creation requires a Blueprint graph editor')
        with unreal.ScopedEditorTransaction('Create comment'):
            node = editor.add_comment_node(text, unreal.Vector2D(position.x, position.y), unreal.Vector2D(size.x, size.y))
        if node is None:
            raise RuntimeError('Unreal failed to create comment')
        return node

    @toolset_registry.tool_call
    @staticmethod
    def wrap_comment(graph: unreal.EdGraph, text: str, nodes: list[unreal.EdGraphNode], padding: int) -> unreal.EdGraphNode:
        """Wrap selected K2 nodes using Unreal's comment bounds calculation."""
        if not nodes or padding < 0 or any(not isinstance(n, unreal.K2Node) or n.get_outer() != graph for n in nodes):
            raise ValueError('Comment wrapping requires K2 nodes in the selected graph and nonnegative padding')
        editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
        if editor is None:
            raise ValueError('Comment wrapping requires a Blueprint graph editor')
        with unreal.ScopedEditorTransaction('Wrap nodes in comment'):
            node = editor.add_comment_to_nodes(text, nodes, padding)
        if node is None:
            raise RuntimeError('Unreal failed to wrap nodes in comment')
        return node

    @toolset_registry.tool_call
    @staticmethod
    def delete_comment(node: unreal.EdGraphNode) -> None:
        """Remove a comment box while preserving its enclosed nodes."""
        if not isinstance(node, unreal.EdGraphNode_Comment):
            raise ValueError('Comment deletion requires a comment box')
        editor = unreal.BlueprintGraphEditor.get_graph_editor(node.get_outer())
        if editor is None:
            raise ValueError('Comment deletion requires a Blueprint graph editor')
        with unreal.ScopedEditorTransaction('Delete comment'):
            editor.remove_comment_node(node)

    @toolset_registry.tool_call
    @staticmethod
    def list_comments(graph: unreal.EdGraph) -> str:
        """Read only comment boxes in the selected graph."""
        editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
        if editor is None:
            raise ValueError('Comment listing requires a Blueprint graph editor')
        return json.dumps([json.loads(AssetCreationTools.node_comment(n, '{}')) for n in editor.list_comment_nodes()])

    @toolset_registry.tool_call
    @staticmethod
    def node_comment(node: unreal.EdGraphNode, values: str) -> str:
        """Read or edit a node comment; box-only fields are width, height and color."""
        if native_status(15)['state'] != 'current':
            raise RuntimeError('Comment inspection/editing requires UnrealBPBridge protocol 15')
        changes = json.loads(values)
        allowed = {'text', 'visible', 'pinned', 'width', 'height', 'color'}
        if not isinstance(changes, dict) or changes.keys() - allowed:
            raise ValueError('Comment properties accept only text, visible, pinned, width, height and color')
        if 'text' in changes and not isinstance(changes['text'], str):
            raise ValueError('Comment text must be a string')
        for key in ('visible', 'pinned'):
            if key in changes and type(changes[key]) is not bool:
                raise ValueError(f'{key} must be boolean')
        for key in ('width', 'height'):
            if key in changes and (type(changes[key]) is not int or changes[key] <= 0):
                raise ValueError(f'{key} must be a positive integer')
        is_box = isinstance(node, unreal.EdGraphNode_Comment)
        if changes.keys() & {'width', 'height', 'color'} and not is_box:
            raise ValueError('Width, height and color require a comment box')
        if 'color' in changes:
            color = changes['color']
            if not isinstance(color, dict) or color.keys() != {'r', 'g', 'b', 'a'} or any(type(v) not in (int, float) or not 0 <= v <= 1 for v in color.values()):
                raise ValueError('Comment color requires r, g, b, a numbers between 0 and 1')
        current = json.loads(unreal.UnrealBPBridgeLibrary.get_node_comment(node))
        if 'error' in current:
            raise ValueError(current['error'])
        if changes:
            with unreal.ScopedEditorTransaction('Edit comment'):
                if changes.keys() & {'text', 'visible', 'pinned'}:
                    updated = {**current, **changes}
                    if not unreal.UnrealBPBridgeLibrary.set_node_comment(node, updated['text'], updated['visible'], updated['pinned']):
                        raise RuntimeError('Unreal failed to edit node comment')
                if changes.keys() & {'width', 'height'}:
                    if not unreal.UnrealBPBridgeLibrary.resize_comment(node, changes.get('width', current['width']), changes.get('height', current['height'])):
                        raise RuntimeError('Unreal failed to resize comment')
                if 'color' in changes:
                    from editor_toolset.toolsets.object import ObjectTools
                    if not ObjectTools.set_properties(node, json.dumps({'commentColor': changes['color']})):
                        raise RuntimeError('Unreal failed to set comment color')
            current = json.loads(unreal.UnrealBPBridgeLibrary.get_node_comment(node))
            if 'error' in current:
                raise ValueError(current['error'])
        if is_box:
            color = node.get_editor_property('comment_color')
            current['color'] = {key: getattr(color, key) for key in ('r', 'g', 'b', 'a')}
        pos = node.get_node_pos()
        return json.dumps({'node': {'refPath': node.get_path_name()}, 'position': {'x': pos.x, 'y': pos.y}, **current})

    @toolset_registry.tool_call
    @staticmethod
    def inspect_node_types(graph: unreal.EdGraph, types: str) -> list[NodeInfo]:
        """Inspect a JSON list of type/optional class entries in one tool call.

        Results follow request order. Preview nodes are removed even if inspection fails.
        """
        from editor_toolset.toolsets.blueprint import BlueprintTools, _BlueprintCache
        entries = json.loads(types)
        if not isinstance(entries, list) or not entries:
            raise ValueError('types must be a nonempty JSON array')
        available = [t for bucket in _BlueprintCache.get(graph).values() for t in bucket]
        prepared = []
        for entry in entries:
            if not isinstance(entry, dict) or 'type' not in entry or entry.keys() - {'type', 'class'}:
                raise ValueError('Each entry requires type and accepts only optional class')
            type_id = entry['type']
            if not isinstance(type_id, str) or not type_id:
                raise ValueError('type must be a nonempty string')
            matches = [t for t in available if t.casefold() == type_id.casefold()]
            if not matches:
                raise ValueError(f'Node type not found: {type_id}; discover or refresh node_types')
            if len(matches) > 1 and 'class' not in entry:
                raise ValueError(f'Ambiguous node type: {type_id}; supply its declaring class')
            declaring_class = None
            if 'class' in entry:
                if not isinstance(entry['class'], str) or not entry['class'].startswith('/'):
                    raise ValueError('class requires a full Unreal class object path')
                declaring_class = unreal.load_class(None, entry['class'])
                if declaring_class is None:
                    raise ValueError(f"Declaring class not found: {entry['class']}")
            prepared.append((type_id, declaring_class))
        existing = {node: node.get_node_pos() for node in BlueprintTools.find_nodes(graph, '')}
        result = []
        for type_id, declaring_class in prepared:
            node = BlueprintTools.create_node(graph, type_id, unreal.IntPoint(0, 0), declaring_class)
            if node in existing:
                node.set_node_pos(existing[node])
            try:
                result.extend(BlueprintTools.get_node_infos([node]))
            finally:
                if node not in existing:
                    BlueprintTools.delete_node(node)
        return result

    @toolset_registry.tool_call
    @staticmethod
    def refresh_node_types(graph: unreal.EdGraph) -> int:
        """Invalidate the owning Blueprint's node discovery cache and rebuild this graph.

        Returns the number of cached type entries. Other graphs rebuild on their next lookup.
        """
        from editor_toolset.toolsets.blueprint import _BlueprintCache
        blueprint = unreal.Blueprint.cast(graph.get_outer())
        if blueprint is None:
            raise ValueError('Node discovery refresh requires a graph owned by a Blueprint')
        _BlueprintCache.invalidate(blueprint)
        categories = _BlueprintCache.get(graph)
        return sum(len(entries) for entries in categories.values())

    @toolset_registry.tool_call
    @staticmethod
    def enum_entries(enum: unreal.UserDefinedEnum) -> str:
        """Read stable entry ids, display names and current numeric values; omit the MAX sentinel."""
        if native_status(16)['state'] != 'current':
            raise RuntimeError('Enum entry operations require UnrealBPBridge protocol 16')
        result = unreal.UnrealBPBridgeLibrary.get_enum_entries(enum)
        entries = json.loads(result)
        if isinstance(entries, dict) and 'error' in entries:
            raise RuntimeError(entries['error'])
        return result

    @toolset_registry.tool_call
    @staticmethod
    def edit_enum_entries(enum: unreal.UserDefinedEnum, action: str, entries: str) -> str:
        """Add display names, rename by stable id or delete ids through EnumEditorUtils.

        Entries execute in order. Earlier changes remain applied on failure; inspect before resuming.
        """
        current = json.loads(AssetCreationTools.enum_entries(enum))
        values = json.loads(entries)
        if action == 'rename':
            if not isinstance(values, dict) or not values or not all(isinstance(k, str) and k and isinstance(v, str) and v.strip() for k, v in values.items()):
                raise ValueError('Rename requires an entry-id to display-name object')
            edits = list(values.items())
        elif action in ('add', 'delete'):
            if not isinstance(values, list) or not values or not all(isinstance(v, str) and v.strip() for v in values) or len(values) != len(set(values)):
                raise ValueError('Add/delete requires a nonempty list of distinct nonempty strings')
            edits = [('', name) if action == 'add' else (name, '') for name in values]
        else:
            raise ValueError('Enum action must be add, rename or delete')
        if action != 'add':
            missing = set(values) - {entry['id'] for entry in current}
            if missing:
                raise ValueError(f'Enum entry ids not found: {sorted(missing)}; inspect enum_entries')
        for entry, display_name in edits:
            if not unreal.UnrealBPBridgeLibrary.edit_enum_entry(enum, action, entry, display_name):
                raise RuntimeError(f'Enum {action} failed for {entry or display_name}; inspect enum_entries before resuming')
        return AssetCreationTools.enum_entries(enum)

    @toolset_registry.tool_call
    @staticmethod
    def struct_fields(struct: unreal.UserDefinedStruct) -> str:
        """Read struct field names, GUIDs, pin categories and default values."""
        if native_status()['state'] != 'current':
            raise RuntimeError('Struct editing requires UnrealBPBridge protocol 14 loaded')
        result = unreal.UnrealBPBridgeLibrary.get_struct_fields(struct)
        fields = json.loads(result)
        if isinstance(fields, dict) and 'error' in fields:
            raise RuntimeError(fields['error'])
        return result

    @toolset_registry.tool_call
    @staticmethod
    def edit_struct(struct: unreal.UserDefinedStruct, fields: str) -> str:
        """Edit named fields via StructureEditorUtils; no removal or implicit save.

        fields is a JSON array with name, default and either type or native pin_type text; optional rename_from,
        class, struct, container and tooltip.
        A failure leaves completed edits applied; read struct_fields before resuming.
        """
        if native_status()['state'] != 'current':
            raise RuntimeError('Struct editing requires UnrealBPBridge protocol 14 loaded')
        edits = json.loads(fields)
        if not isinstance(edits, list) or not edits:
            raise ValueError('fields must be a nonempty JSON array')
        current = json.loads(unreal.UnrealBPBridgeLibrary.get_struct_fields(struct))
        if isinstance(current, dict) and 'error' in current:
            raise RuntimeError(current['error'])
        names = {field['name'].casefold() for field in current}
        touched = set()
        prepared = []
        for field in edits:
            if not isinstance(field, dict) or not {'name', 'default'} <= field.keys() or field.keys() - {'name', 'type', 'pin_type', 'default', 'rename_from', 'class', 'struct', 'container', 'tooltip'}:
                raise ValueError('Each field requires name, default and exactly one of type or pin_type; optional: rename_from, class, struct, container, tooltip')
            if not all(isinstance(value, str) for value in field.values()) or not field['name']:
                raise ValueError('Field values must be strings; name must be nonempty')
            if ('type' in field) == ('pin_type' in field):
                raise ValueError('Specify exactly one of type or pin_type')
            if 'pin_type' in field and (not field['pin_type'] or {'class', 'struct', 'container'} & field.keys()):
                raise ValueError('pin_type requires nonempty FEdGraphPinType text and cannot be combined with class, struct or container')
            name = field['name'].casefold()
            source = field.get('rename_from', field['name']).casefold()
            if name in touched or source in touched:
                raise ValueError('A field may be edited only once per command')
            if 'rename_from' in field:
                if source not in names or (source != name and name in names):
                    raise ValueError('rename_from must exist and its destination must be free')
                names.remove(source)
            if 'pin_type' in field:
                pin_type = unreal.EdGraphPinType()
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter('error', RuntimeWarning)
                        if not pin_type.import_text(field['pin_type']):
                            raise ValueError(f"Invalid FEdGraphPinType text for field {field['name']}")
                except RuntimeWarning as error:
                    raise ValueError(f"Invalid FEdGraphPinType text for field {field['name']}: {error}") from error
                prepared.append((field, pin_type))
                touched.update((source, name))
                names.add(name)
                continue
            for kind, key in (('object', 'class'), ('struct', 'struct')):
                if (field['type'] == kind) != (key in field):
                    raise ValueError(f'type {kind} requires {key}; other types cannot use it')
                if key in field and not field[key].startswith('/'):
                    raise ValueError(f'{key} requires a full Unreal object path')
            if field['type'] == 'object':
                cls = unreal.load_class(None, field['class'])
                if cls is None:
                    raise ValueError(f"Class not found: {field['class']}; use the generated _C path for Blueprints")
                pin_type = unreal.BlueprintEditorLibrary.get_object_reference_type(cls)
            elif field['type'] == 'struct':
                member_struct = unreal.load_object(None, field['struct'])
                if not isinstance(member_struct, unreal.ScriptStruct):
                    raise ValueError(f"Not a ScriptStruct: {field['struct']}")
                pin_type = unreal.BlueprintEditorLibrary.get_struct_type(member_struct)
            else:
                pin_type = BlueprintTools._make_variable_type(field['type'])
            if 'container' in field:
                if field['container'] not in ('array', 'set', 'map'):
                    raise ValueError('container must be array, set or map (string keys)')
                pin_type = BlueprintTools._apply_container(pin_type, getattr(ContainerType, field['container'].upper()))
            prepared.append((field, pin_type))
            touched.update((source, name))
            names.add(name)
        for field, pin_type in prepared:
            if not unreal.UnrealBPBridgeLibrary.edit_struct_field(struct, field['name'], pin_type, field['default'], field.get('rename_from', '')):
                raise RuntimeError(f"Struct field edit failed: {field['name']}; read struct_fields before resuming")
            if 'tooltip' in field and not unreal.UnrealBPBridgeLibrary.set_struct_field_tooltip(struct, field['name'], field['tooltip']):
                raise RuntimeError(f"Struct field tooltip edit failed: {field['name']}; read struct_fields before resuming")
        return unreal.UnrealBPBridgeLibrary.get_struct_fields(struct)

    @toolset_registry.tool_call
    @staticmethod
    def delete_struct_field(struct: unreal.UserDefinedStruct, name: str) -> str:
        """Remove an existing field; the last field cannot be removed. Save explicitly."""
        if native_status()['state'] != 'current':
            raise RuntimeError('Struct editing requires UnrealBPBridge protocol 14 loaded')
        current = json.loads(AssetCreationTools.struct_fields(struct))
        if name not in [field['name'] for field in current]:
            raise ValueError(f'Struct field does not exist: {name}')
        if len(current) == 1:
            raise ValueError('Cannot delete the last struct field: Unreal requires a nonempty struct')
        if not unreal.UnrealBPBridgeLibrary.delete_struct_field(struct, name):
            raise RuntimeError(f'Struct field deletion failed: {name}; read struct_fields before resuming')
        return unreal.UnrealBPBridgeLibrary.get_struct_fields(struct)

    @toolset_registry.tool_call
    @staticmethod
    def move_struct_field(struct: unreal.UserDefinedStruct, name: str, position: str, relative_to: str) -> str:
        """Move an existing field before or after another existing field. Save explicitly."""
        if native_status()['state'] != 'current':
            raise RuntimeError('Struct editing requires UnrealBPBridge protocol 14 loaded')
        if position not in ('before', 'after'):
            raise ValueError('position must be before or after')
        current = json.loads(AssetCreationTools.struct_fields(struct))
        names = [field['name'] for field in current]
        if name not in names or relative_to not in names or name == relative_to:
            raise ValueError('Move requires two distinct existing field names')
        if not unreal.UnrealBPBridgeLibrary.move_struct_field(struct, name, relative_to, position == 'after'):
            raise RuntimeError(f'Struct field move failed: {name}; read struct_fields before resuming')
        return unreal.UnrealBPBridgeLibrary.get_struct_fields(struct)

    @toolset_registry.tool_call
    @staticmethod
    def catalog() -> str:
        """Return live factory candidates, supported classes and creation requirements.

        Discovery uses reflected factory defaults, not the Content Browser menu's
        C++ filtering. A discovered candidate is not a promise of creation support.
        """
        entries = []
        for ref in unreal.ToolsetLibrary.get_derived_classes(unreal.Factory.static_class()):
            path = ref.export_text()
            cls = factory_class(path)
            cdo = unreal.get_default_object(cls)
            supported = cdo.get_editor_property('supported_class')
            create_new = cdo.get_editor_property('create_new')
            entry = {
                'factory': path,
                'create_new_default': create_new,
                'asset_class': supported.get_path_name() if supported is not None else None,
                'creation_supported': path in RULES and bool(create_new) and supported is not None,
            }
            if path in RULES:
                required, allowed = RULES[path]['required'], RULES[path]['allowed']
                schema = json.loads(unreal.ToolsetLibrary.list_struct_properties(
                    cls, path not in ('/Script/UnrealEd.MaterialInstanceConstantFactoryNew', '/Script/UnrealEd.AnimCompositeFactory', '/Script/UnrealEd.PreviewMeshCollectionFactory', '/Script/PCGEditor.PCGGraphInstanceFactory', '/Script/StateTreeEditorModule.StateTreeFactory')))
                if path in ('/Script/UnrealEd.AnimCompositeFactory', '/Script/UnrealEd.DataAssetFactory', '/Script/UnrealEd.PreviewMeshCollectionFactory', '/Script/PCGEditor.PCGGraphInstanceFactory', '/Script/AudioEditor.SoundSourceEffectFactory', '/Script/AudioEditor.SoundSubmixEffectFactory', '/Script/StateTreeEditorModule.StateTreeFactory'):
                    entry['native_dependency'] = native_status({'/Script/UnrealEd.AnimCompositeFactory': 1, '/Script/UnrealEd.DataAssetFactory': 2, '/Script/UnrealEd.PreviewMeshCollectionFactory': 3, '/Script/PCGEditor.PCGGraphInstanceFactory': 4, '/Script/AudioEditor.SoundSourceEffectFactory': 5, '/Script/AudioEditor.SoundSubmixEffectFactory': 5, '/Script/StateTreeEditorModule.StateTreeFactory': 6}[path])
                    if entry['native_dependency']['state'] != 'current':
                        entry['creation_supported'] = False
                        entry['unavailable_reason'] = f"UnrealBPBridge version {entry['native_dependency']['expected_version']} or a supported newer version must be built and loaded"
                if RULES[path].get('concrete_classes'):
                    entry['native_dependency'] = native_status(7)
                    if entry['native_dependency']['state'] != 'current':
                        entry['creation_supported'] = False
                        entry['unavailable_reason'] = 'UnrealBPBridge version 7 must be built and loaded'
                entry['required_settings'] = RULES[path].get('required_settings', [])
                disabled = unavailable_settings(RULES[path])
                if disabled:
                    entry['creation_supported'] = False
                    entry['unavailable_reason'] = '; '.join(disabled)
                if path == '/Script/Blutility.EditorUtilityBlueprintFactory':
                    entry['native_dependency'] = native_status(8)
                    if entry['native_dependency']['state'] != 'current':
                        entry['creation_supported'] = False
                        entry['unavailable_reason'] = 'UnrealBPBridge version 8 must be built and loaded'
                if path == '/Script/GameplayCamerasEditor.CameraAssetFactory':
                    entry['native_dependency'] = native_status(9)
                    if entry['native_dependency']['state'] != 'current':
                        entry['creation_supported'] = False
                        entry['unavailable_reason'] = 'UnrealBPBridge version 9 must be built and loaded'
                entry['required_assets'] = RULES[path].get('required_assets', {})
                entry['required_options'] = list(required)
                entry['options'] = {name: schema[name] for name in allowed}
                console_bool = RULES[path].get('required_console_bool')
                if console_bool is not None:
                    entry['required_console_bool'] = console_bool
                    if not unreal.SystemLibrary.get_console_variable_bool_value(console_bool):
                        entry['creation_supported'] = False
                        entry['unavailable_reason'] = f'Required console variable is disabled or unavailable: {console_bool}'
            else:
                entry['unavailable_reason'] = 'Factory configuration requirements have not been reviewed'
            entries.append(entry)
        return json.dumps({'project': unreal.Paths.project_dir(),
                           'engine': unreal.SystemLibrary.get_engine_version(), 'factories': entries})

    @toolset_registry.tool_call
    @staticmethod
    def create(folder_path: str, asset_name: str, factory_path: str, options: str) -> unreal.Object:
        """Validate required factory references, then create exactly one unsaved asset.

        options is a JSON object using the exact keys from catalog(). Missing or
        incompatible dependencies fail before CreateAsset. No dependency is created
        implicitly, and no dialog is opened. Existing assets are not overwritten.
        """
        if factory_path not in RULES:
            raise ValueError(f'Factory configuration is not supported yet: {factory_path}; inspect catalog')
        disabled = unavailable_settings(RULES[factory_path])
        if disabled:
            raise ValueError('; '.join(disabled))
        console_bool = RULES[factory_path].get('required_console_bool')
        if console_bool is not None and not unreal.SystemLibrary.get_console_variable_bool_value(console_bool):
            raise ValueError(f'Required console variable is disabled or unavailable: {console_bool}')
        values = json.loads(options)
        if not isinstance(values, dict):
            raise ValueError('Factory options must be a JSON object')
        required, allowed = RULES[factory_path]['required'], RULES[factory_path]['allowed']
        missing = set(required) - values.keys()
        unknown = values.keys() - set(allowed)
        if missing or unknown:
            raise ValueError(f'Factory options: missing={sorted(missing)}, unknown={sorted(unknown)}')
        for path, expected_class in RULES[factory_path].get('required_assets', {}).items():
            dependency = unreal.load_object(None, path)
            base = unreal.load_class(None, expected_class)
            if dependency is None or base is None or not unreal.MathLibrary.class_is_child_of(dependency.get_class(), base):
                raise ValueError(f'Missing or incompatible factory dependency: {path}; expected {expected_class}')
        if factory_path == '/Script/NiagaraEditor.NiagaraSystemFactoryNew':
            settings_class = unreal.load_class(None, '/Script/NiagaraEditor.NiagaraEditorSettings')
            if settings_class is None:
                raise RuntimeError('NiagaraEditorSettings class is unavailable')
            settings = unreal.get_default_object(settings_class)
            script_ref = json.loads(unreal.ToolsetLibrary.get_object_properties(settings, ['RequiredSystemUpdateScript']))['RequiredSystemUpdateScript']['refPath']
            script = unreal.load_object(None, script_ref)
            if not isinstance(script, unreal.NiagaraScript):
                raise ValueError(f'RequiredSystemUpdateScript must resolve to a NiagaraScript: {script_ref}')
        cls = factory_class(factory_path)
        schema = json.loads(unreal.ToolsetLibrary.list_struct_properties(
            cls, factory_path not in ('/Script/UnrealEd.MaterialInstanceConstantFactoryNew', '/Script/UnrealEd.AnimCompositeFactory', '/Script/UnrealEd.PreviewMeshCollectionFactory', '/Script/PCGEditor.PCGGraphInstanceFactory', '/Script/StateTreeEditorModule.StateTreeFactory')))
        resolved = {}
        for key, value in values.items():
            if not isinstance(value, dict) or set(value) != {'refPath'} or not isinstance(value['refPath'], str):
                raise ValueError(f'{key} requires an explicit {{"refPath": "/..."}} object reference')
            path = value['refPath']
            title = schema[key]['title']
            if title.startswith('Class@'):
                obj = unreal.load_class(None, path)
                base = unreal.load_class(None, title.removeprefix('Class@'))
                valid = obj is not None and base is not None and unreal.MathLibrary.class_is_child_of(obj, base)
            else:
                obj = unreal.load_object(None, path)
                base = unreal.load_class(None, title)
                valid = obj is not None and base is not None and unreal.MathLibrary.class_is_child_of(obj.get_class(), base)
            if not valid:
                raise ValueError(f'Missing or incompatible dependency {key}: {path}; expected {title}')
            resolved[key] = obj
        for key in RULES[factory_path].get('concrete_classes', []):
            if native_status(7)['state'] != 'current':
                raise RuntimeError('UnrealBPBridge version 7 must be built and loaded')
            if not unreal.UnrealBPBridgeLibrary.is_concrete_factory_class(resolved[key]):
                raise ValueError(f'{key} is abstract, deprecated or superseded')
        if factory_path == '/Script/UnrealEd.SlateWidgetStyleAssetFactory' and resolved['styleType'].get_path_name() == '/Script/SlateCore.SlateWidgetStyleContainerBase':
            raise ValueError('styleType must be a derived SlateWidgetStyleContainerBase class')
        if factory_path == '/Script/Blutility.EditorUtilityBlueprintFactory':
            if native_status(8)['state'] != 'current':
                raise RuntimeError('UnrealBPBridge version 8 must be built and loaded')
            if not unreal.UnrealBPBridgeLibrary.is_editor_utility_parent_allowed(resolved['parentClass']):
                raise ValueError('parentClass must be an editor-only Blueprint parent and cannot be an EditorUtilityWidget')
        if factory_path == '/Script/TemplateSequenceEditor.TemplateSequenceFactoryNew' and not unreal.MathLibrary.class_is_child_of(resolved['boundActorClass'], unreal.Actor.static_class()):
            raise ValueError('boundActorClass must derive from Actor')
        if factory_path == '/Script/UnrealEd.DataAssetFactory':
            if native_status(2)['state'] != 'current':
                raise RuntimeError('UnrealBPBridge version 2 must be built and loaded')
            if not unreal.UnrealBPBridgeLibrary.is_data_asset_class_allowed(resolved['dataAssetClass']):
                raise ValueError('dataAssetClass is abstract, deprecated, superseded or hidden from the Data Asset class picker')
        if factory_path in ('/Script/AudioEditor.SoundSourceEffectFactory', '/Script/AudioEditor.SoundSubmixEffectFactory'):
            if native_status(5)['state'] != 'current':
                raise RuntimeError('UnrealBPBridge version 5 must be built and loaded')
            key = 'soundEffectSourcepresetClass' if factory_path == '/Script/AudioEditor.SoundSourceEffectFactory' else 'soundEffectSubmixPresetClass'
            if not unreal.UnrealBPBridgeLibrary.is_sound_effect_preset_class_allowed(resolved[key]):
                raise ValueError(f'{key} is abstract, deprecated or superseded and cannot be selected for a sound effect preset')
        if factory_path == '/Script/UnrealEd.PoseAssetFactory' and resolved['sourceAnimation'].get_editor_property('skeleton') is None:
            raise ValueError('sourceAnimation must have a skeleton before creating a PoseAsset')
        if unreal.MathLibrary.class_is_child_of(cls, unreal.DataTableFactory.static_class()):
            row = resolved['struct']
            native_rows = unreal.ToolsetLibrary.get_derived_structs(unreal.TableRowBase.static_struct())
            if not isinstance(row, unreal.UserDefinedStruct) and row not in native_rows:
                raise ValueError('struct must be a UserDefinedStruct or derive from TableRowBase')
        if factory_path == '/Script/UnrealEd.MaterialInstanceConstantFactoryNew' and 'initialParent' in resolved:
            from editor_toolset.toolsets.material_instance import MaterialInstanceTools
            instance = MaterialInstanceTools.create(folder_path, asset_name, resolved['initialParent'])
            if instance.get_editor_property('parent') != resolved['initialParent']:
                raise RuntimeError(f'Material Instance parent assignment failed: {instance.get_path_name()}')
            return instance
        if factory_path == '/Script/GameplayCamerasEditor.CameraAssetFactory' and native_status(9)['state'] != 'current':
            raise RuntimeError('UnrealBPBridge version 9 must be built and loaded')
        factory = unreal.new_object(cls)
        if factory_path == '/Script/UnrealEd.AnimCompositeFactory':
            if native_status(1)['state'] != 'current':
                raise RuntimeError('UnrealBPBridge version 1 or a supported newer version must be built and loaded')
            if not unreal.UnrealBPBridgeLibrary.configure_anim_composite_factory(factory, resolved['targetSkeleton']):
                raise RuntimeError('AnimComposite factory configuration failed')
        elif factory_path == '/Script/UnrealEd.PreviewMeshCollectionFactory':
            if native_status(3)['state'] != 'current':
                raise RuntimeError('UnrealBPBridge version 3 must be built and loaded')
            if not unreal.UnrealBPBridgeLibrary.configure_preview_mesh_collection_factory(factory, resolved['currentSkeleton']):
                raise RuntimeError('Preview Mesh Collection factory configuration failed')
        elif factory_path == '/Script/PCGEditor.PCGGraphInstanceFactory':
            if native_status(4)['state'] != 'current':
                raise RuntimeError('UnrealBPBridge version 4 must be built and loaded')
            if not unreal.UnrealBPBridgeLibrary.configure_pcg_graph_instance_factory(factory, resolved['parentGraph']):
                raise RuntimeError('PCG Graph Instance factory configuration failed')
        elif factory_path == '/Script/StateTreeEditorModule.StateTreeFactory':
            if native_status(6)['state'] != 'current':
                raise RuntimeError('UnrealBPBridge version 6 must be built and loaded')
            if not unreal.UnrealBPBridgeLibrary.configure_state_tree_factory(factory, resolved['stateTreeSchemaClass']):
                raise RuntimeError('StateTree factory requires a selectable StateTreeSchema class')
        elif values and not unreal.ToolsetLibrary.set_object_properties(factory, json.dumps(values)):
            raise RuntimeError(f'Could not configure factory: {factory_path}')
        if not factory.get_editor_property('create_new'):
            raise ValueError(f'Factory does not declare creation support: {factory_path}')
        supported = factory.get_editor_property('supported_class')
        if supported is None:
            raise ValueError(f'Factory has no resolved supported class: {factory_path}')
        asset = create_asset(folder_path, asset_name, supported, factory)
        if factory_path == '/Script/TemplateSequenceEditor.TemplateSequenceFactoryNew':
            spawnables = asset.get_spawnables()
            if len(spawnables) != 1:
                raise RuntimeError(f'Template Sequence must contain one spawnable; inspect partial asset: {asset.get_path_name()}')
            template = spawnables[0].get_object_template()
            if template is None or template.get_class() != resolved['boundActorClass']:
                raise RuntimeError(f'Template Sequence actor template mismatch; inspect partial asset: {asset.get_path_name()}')
        if factory_path == '/Script/GameplayCamerasEditor.CameraAssetFactory' and not unreal.UnrealBPBridgeLibrary.has_camera_director_class(asset, resolved['cameraDirectorClass']):
            raise RuntimeError(f'Camera director class mismatch; inspect partial asset: {asset.get_path_name()}')
        return asset


_registration = Registration([AssetCreationTools])
if not _registration.register():
    raise RuntimeError('Unreal ToolsetRegistry is unavailable; load this module after EditorToolset')
