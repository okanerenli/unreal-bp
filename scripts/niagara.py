"""Command adapter for the engine's registered NiagaraToolsets; no native duplicate."""
import json
import re
from .errors import UnrealMCPError

PREFIX = 'NiagaraToolsets.NiagaraToolset_'
# These native tools return UToolCallAsyncResult and must run outside command_batch.
ASYNC_TOOLS = {'GetSystemCompileState', 'GetStackIssues', 'ApplyStackIssueFix'}


def is_async(action, args):
    return (action in ('niagara_compile_state', 'niagara_issues') or
            (action == 'niagara_call' and args['group'] == 'System' and args['tool'] in ASYNC_TOOLS))


def schema(library, group):
    toolset = PREFIX + group
    if f'- {toolset}:' not in library.available_toolsets:
        raise UnrealMCPError(f'Niagara toolset is not registered: {toolset}; use list niagara_toolsets')
    if toolset not in library.schemas:
        result = json.loads(library._tool('describe_toolset', {'toolset_name': toolset}))
        library.schemas[toolset] = {tool['name'].rsplit('.', 1)[-1]: tool for tool in result['tools']}
    return library.schemas[toolset]


def call(library, group, tool, arguments):
    tools = schema(library, group)
    if tool not in tools:
        raise UnrealMCPError(f'Niagara tool is not available: {group}.{tool}; inspect the live tool list')
    inputs = tools[tool]['inputSchema']
    missing = set(inputs.get('required', [])) - arguments.keys()
    unknown = arguments.keys() - inputs.get('properties', {}).keys()
    if missing or unknown:
        raise UnrealMCPError(f'{group}.{tool}: missing arguments {sorted(missing)}, unknown arguments {sorted(unknown)}')
    # Preserve the native schema, including stack references and instanced values.
    # The registry validates their reflected types and propagates native errors.
    return library._call(PREFIX + group, tool, arguments)


def system(library, context):
    if context.selected_asset is None:
        raise UnrealMCPError('Select a Niagara system first with niagara /Game/Path/System')
    asset_class = library._call(library.ASSETS, 'get_asset_class',
                               {'asset_path': context.selected_asset['refPath']})
    if asset_class != 'NiagaraSystem':
        raise UnrealMCPError(f'Selected asset is not a NiagaraSystem: {context.selected_asset}')
    return context.selected_asset


def execute(library, context, line, action, args):
    if is_async(action, args) and not library.supports_async_tools:
        raise UnrealMCPError('Async Niagara tools must be dispatched by the CLI outside command_batch')
    if action == 'niagara_toolsets':
        groups = re.findall(r'^- NiagaraToolsets\.NiagaraToolset_(\w+):', library.available_toolsets, re.MULTILINE)
        if not groups:
            raise UnrealMCPError('No NiagaraToolsets are registered in the connected editor')
        return groups
    if action in ('niagara_tools', 'niagara_tool_schema'):
        tools = schema(library, args['group'])
        if action == 'niagara_tools':
            return [{'tool': name, 'description': tool.get('description', '')} for name, tool in tools.items()]
        if args['tool'] not in tools:
            raise UnrealMCPError(f"Niagara tool is not available: {args['group']}.{args['tool']}")
        return tools[args['tool']]
    if action == 'niagara_call':
        return call(library, args['group'], args['tool'], args['arguments'])
    if action == 'niagara_select':
        asset = library._call(library.ASSETS, 'load_asset', {'asset_path': args['path']})
        result = call(library, 'System', 'GetSystemSummary', {'system': asset})
        context.selected_asset = asset
        context.blueprint = None
        context.graph = None
        context.aliases.clear()
        return {'asset': asset, 'summary': result}
    tool = {'niagara_map': 'GetSystemSummary', 'niagara_compile_state': 'GetSystemCompileState',
            'niagara_issues': 'GetStackIssues'}[action]
    return call(library, 'System', tool, {'system': system(library, context)})
