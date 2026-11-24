"""Public library and serial command execution."""
import json
from . import assets
from . import materials
from . import niagara
from . import blueprints
from . import dependencies
from .commands import parse_commands
from .context import CommandContext
from .transport import UnrealTransport
from .errors import UnrealMCPError

class UnrealLibrary(UnrealTransport):
    supports_async_tools = True

    def editor_dependency_status(self):
        return dependencies.editor_dependency_status(self)

    def dependencies(self, project, check_only=False):
        return dependencies.dependencies(self, project, check_only=check_only)

    def asset_factories(self, refresh=False):
        return assets.asset_factories(self, refresh=refresh)

    def resolve_blueprint(self, target):
        return blueprints.resolve_blueprint(self, target)

    def blueprint_map(self, target, graph_name=None):
        return blueprints.blueprint_map(self, target, graph_name=graph_name)

    def inspect_asset(self, path, properties=()):
        return assets.inspect_asset(self, path, properties)

    def run(self, source, defer_material_reads=False, batch_material_writes=False, context=None, batch_commands=True):
        commands = parse_commands(source)
        if context is None:
            context = CommandContext(self)
        if context.library is not self:
            raise ValueError('CommandContext belongs to a different UnrealLibrary session')
        context.defer_material_reads = defer_material_reads or batch_material_writes
        if batch_commands and commands:
            # Async native tools need the MCP server to await completion while Unreal ticks.
            # Keep surrounding synchronous commands in their existing managed batches.
            for index, (line, action, args) in enumerate(commands):
                if niagara.is_async(action, args):
                    lines = source.splitlines()
                    sections = [('\n' * (line - 1) + lines[line - 1], False)]
                    if index:
                        sections.insert(0, ('\n'.join(lines[:line - 1]), True))
                    if index + 1 < len(commands):
                        sections.append(('\n' * line + '\n'.join(lines[line:]), True))
                    dependency = self.editor_dependency_status()
                    if dependency['state'] != 'current':
                        raise UnrealMCPError('Niagara commands require the current editor dependency; run dependencies and load its returned code')
                    for section, managed in sections:
                        self.run(section, defer_material_reads=defer_material_reads,
                                 batch_material_writes=batch_material_writes, context=context,
                                 batch_commands=managed)
                    return context
            dependency = self.editor_dependency_status()
            if dependency['state'] != 'current':
                raise UnrealMCPError('Command batches require the current editor dependency; run dependencies and load its returned code')
            context.report({'status': 'started', 'action': 'command_batch', 'lines': [c[0] for c in commands]})
            result = json.loads(self._call(self.ASSET_CREATION, 'command_batch', {
                'source': source, 'state': json.dumps(context.state()),
                'expected_hash': dependency['loaded_hash'],
                'batch_material_writes': batch_material_writes}))
            context.restore(result['state'])
            for entry in result['records']:
                context.report(entry)
            if result['failed'] is not None:
                context.report({'status': 'failed', 'action': 'command_batch', 'failed': result['failed'], 'state': result['state']})
                raise UnrealMCPError(f"Command batch stopped: {json.dumps(result['failed'])}; inspect current state before resuming; do not replay completed commands")
            return context
        index = 0
        while index < len(commands):
            line, action, args = commands[index]
            if batch_material_writes and action in materials.BATCH_ACTIONS:
                end = index + 1
                while end < len(commands) and commands[end][1] in materials.BATCH_ACTIONS:
                    end += 1
                context.report({'status': 'started', 'action': 'material_write_batch',
                                'lines': [c[0] for c in commands[index:end]]})
                materials.execute_batch(self, context, commands[index:end])
                index = end
                continue
            index += 1
            # Flushed progress records make partial execution visible on any failure.
            context.report({"line": line, "action": action, "status": "started"})
            if not action.startswith("material_") and action not in ("save", "folder", "list_assets", "list_folders"):
                context.material_cache.clear()
            handler = niagara.execute if action.startswith("niagara_") else materials.execute if action.startswith("material_") else assets.execute if action in assets.ACTIONS else blueprints.execute
            result = handler(self, context, line, action, args)
            context.report({"line": line, "action": action, "status": "completed", "result": result})
        return context
