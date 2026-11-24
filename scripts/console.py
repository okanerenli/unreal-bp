"""Codex-side access to the installed Unreal Python console."""
import json
from .errors import UnrealMCPError


def execute(library, source, mode):
    library.editor_dependency_status()
    if library.ASSET_CREATION not in library.schemas or 'python_console' not in library.schemas[library.ASSET_CREATION]:
        raise UnrealMCPError('Python console is not installed; load the editor dependency first')
    # An older loaded dependency must remain callable to execute its reload code.
    return json.loads(library._call(library.ASSET_CREATION, 'python_console', {'source': source, 'mode': mode}))
