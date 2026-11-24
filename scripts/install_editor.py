"""Manage the factory toolset in a project's existing Unreal Python startup path."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def editor_source():
    return Path(__file__).resolve().parents[1] / 'editor' / 'unreal_bp_assets.py'


def source_hash(directory=None):
    files = dependency_files()
    return hashlib.sha256(b''.join((source if directory is None else directory / relative).read_bytes()
                                  for relative, source in files.items())).hexdigest()


def dependency_files():
    source = editor_source().parent
    files = {Path(name): source / name for name in ('unreal_bp_assets.py', 'creation_rules.json', 'unreal_bp_console.py')}
    for name in ('__init__.py', 'assets.py', 'blueprints.py', 'commands.py', 'context.py',
                 'dependencies.py', 'errors.py', 'install_editor.py', 'library.py', 'materials.py', 'niagara.py', 'transport.py'):
        files[Path('unreal_bp_runtime') / name] = Path(__file__).parent / name
    return files


def install(project, check_only=False):
    project = Path(project).resolve()
    if len(list(project.glob('*.uproject'))) != 1:
        raise ValueError('project must contain exactly one .uproject file')
    source = editor_source()
    native_source = source.parent / 'UnrealBPBridge'
    native_destination = project / 'Plugins' / 'UnrealBPBridge'
    native_files = sorted(path for path in native_source.rglob('*') if path.is_file())
    native_ready = all((native_destination / path.relative_to(native_source)).is_file()
                       and (native_destination / path.relative_to(native_source)).read_bytes() == path.read_bytes()
                       for path in native_files)
    if not check_only and not native_ready:
        for path in native_files:
            target = native_destination / path.relative_to(native_source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        native_ready = True
    destination = project / 'Content' / 'Python'
    module = destination / source.name
    startup = destination / 'init_unreal.py'
    expected = source_hash()
    current = source_hash(destination) if all((destination / name).is_file() for name in dependency_files()) else None
    text = startup.read_text() if startup.exists() else ''
    line = 'import unreal_bp_assets'
    startup_ready = line in text.splitlines()
    changed = current != expected or not startup_ready
    if not check_only and changed:
        destination.mkdir(parents=True, exist_ok=True)
        if current != expected:
            for relative, content in dependency_files().items():
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(content, target)
        if not startup_ready:
            startup.write_text(text + ('\n' if text and not text.endswith('\n') else '') + line + '\n')
        current = source_hash(destination)
        startup_ready = line in startup.read_text().splitlines()
    code = '\n'.join([
        'import sys, importlib, pathlib, toolset_registry',
        f'expected_module = pathlib.Path({str(module)!r}).resolve()',
        "if 'unreal_bp_assets' in sys.modules:",
        "    assert pathlib.Path(sys.modules['unreal_bp_assets'].__file__).resolve() == expected_module, 'Editor module belongs to a different project'",
        f'sys.path.insert(0, {str(destination)!r})',
        'importlib.invalidate_caches()',
        "for name in ('errors', 'commands', 'context', 'transport', 'install_editor', 'dependencies', 'assets', 'blueprints', 'materials', 'niagara', 'library'):",
        "    key = 'unreal_bp_runtime.' + name",
        "    if key in sys.modules:",
        "        assert pathlib.Path(sys.modules[key].__file__).resolve() == expected_module.parent / 'unreal_bp_runtime' / (name + '.py'), 'Command runtime belongs to a different project'",
        "        importlib.reload(sys.modules[key])",
        "if 'unreal_bp_console' in sys.modules:",
        "    assert pathlib.Path(sys.modules['unreal_bp_console'].__file__).resolve() == expected_module.with_name('unreal_bp_console.py'), 'Console module belongs to a different project'",
        "    importlib.reload(sys.modules['unreal_bp_console'])",
        "if 'unreal_bp_assets' in sys.modules:",
        "    toolset_registry.reload_module(sys.modules['unreal_bp_assets'])",
        'else:',
        "    importlib.import_module('unreal_bp_assets')",
    ])
    return {'project': str(project), 'module': str(module), 'expected_hash': expected,
            'native': {'plugin': str(native_destination / 'UnrealBPBridge.uplugin'),
                       'source_ready': native_ready, 'activation': 'Build the editor target with -NoHotReloadFromIDE, verify UnrealEditor.modules points to the normal bridge binary, then restart with user approval; check runtime.native'},
            'disk_hash': current, 'startup_ready': startup_ready,
            'disk_ready': current == expected and startup_ready,
            'updated': changed and not check_only, 'load_code': code}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path, help='Directory containing one .uproject')
    parser.add_argument('--check', action='store_true', help='Inspect without writing')
    args = parser.parse_args()
    print(json.dumps(install(args.project, check_only=args.check), indent=2))
