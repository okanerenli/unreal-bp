"""Codex-side Unreal library using the existing Unreal MCP transport."""
import argparse
import json
import sys
import urllib.error
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import console
from scripts.commands import COMMANDS, parse_commands
from scripts.errors import UnrealMCPError
from scripts.library import UnrealLibrary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    read_map = commands.add_parser("map", help="Read a Blueprint map, optionally limited to one graph")
    read_map.add_argument("target", help="Blueprint asset name, unique substring or asset path")
    read_map.add_argument("--graph", help="Read only this exact function/event/macro graph name")
    run = commands.add_parser("run", help="Execute a command file serially; stop on the first error")
    run.add_argument("file", help="UTF-8 command file")
    run.add_argument("--batch-material-writes", action="store_true", help="Execute consecutive material writes in one editor call; implies deferred readback")
    run.add_argument("--defer-material-reads", action="store_true", help="Defer material mutation readback to explicit map material commands")
    commands.add_parser("syntax", help="List supported command forms without connecting to Unreal")
    dependency = commands.add_parser("dependencies", help="Install/update the Unreal module and verify the live editor version")
    dependency.add_argument("--project", required=True, help="Local Unreal project directory")
    dependency.add_argument("--check", action="store_true", help="Inspect disk and runtime without writing")
    console_parser = commands.add_parser("console", help="Run Python through Unreal without focusing the editor")
    console_parser.add_argument("language", choices=["python"])
    console_source = console_parser.add_mutually_exclusive_group(required=True)
    console_source.add_argument("--code", help="Python source")
    console_source.add_argument("--file", help="Local UTF-8 Python source file")
    console_parser.add_argument("--mode", choices=["exec", "eval"], default="exec")
    inspect_parser = commands.add_parser("inspect", help="Read asset tags and property schema")
    inspect_parser.add_argument("path", help="Exact Unreal asset path")
    inspect_parser.add_argument("--property", action="append", default=[], help="Read an exact property from the schema; repeat for multiple values")
    args = parser.parse_args()
    if args.command == "syntax":
        print("\n".join(COMMANDS.values()))
        print("create variable options: [scope member|local] [container array|set|map] [struct PATH] [default VALUE] (struct PATH required for type struct; local/object/struct/container defaults unsupported; map keys are strings)")
        return
    if args.command == "run":
        with open(args.file, encoding="utf-8") as source_file:
            source = source_file.read()
        parse_commands(source)
    library = UnrealLibrary()
    library.connect()
    if args.command == "dependencies":
        result = library.dependencies(args.project, check_only=args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["ready"]:
            sys.exit(2)
    elif args.command == "console":
        if args.file:
            with open(args.file, encoding="utf-8") as source_file:
                source = source_file.read()
        else:
            source = args.code
        print(json.dumps(console.execute(library, source, args.mode), ensure_ascii=False, indent=2))
    elif args.command == "inspect":
        print(json.dumps(library.inspect_asset(args.path, args.property), ensure_ascii=False, indent=2))
    elif args.command == "run":
        library.run(source, defer_material_reads=args.defer_material_reads, batch_material_writes=args.batch_material_writes)
    else:
        print(json.dumps(library.blueprint_map(args.target, graph_name=args.graph), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (UnrealMCPError, urllib.error.URLError) as error:
        print(f"unreal-bp: {error}", file=sys.stderr)
        sys.exit(1)
