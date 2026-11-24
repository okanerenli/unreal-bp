"""Selection and pin/node resolution shared by one command run."""
import json
from .errors import UnrealMCPError

class CommandContext:
    def __init__(self, library):
        self.library = library
        self.blueprint = None
        self.selected_asset = None
        self.folder = None
        self.graph = None
        self.aliases = {}
        self.material_cache = {}
        self.defer_material_reads = False
        self.material_dependency_checked = False

    def report(self, entry):
        print(json.dumps(entry), flush=True)

    def state(self):
        return {name: getattr(self, name) for name in (
            'blueprint', 'selected_asset', 'folder', 'graph', 'aliases', 'defer_material_reads')}

    def restore(self, state):
        if state.keys() != self.state().keys():
            raise UnrealMCPError('Command context state has an incompatible schema')
        for name, value in state.items():
            setattr(self, name, value)
        self.material_cache.clear()
        self.material_dependency_checked = False

    def bp_call(self, tool, arguments):
        return self.library._call(self.library.BLUEPRINTS, tool, arguments)

    def blueprint_class(self, owner):
        cdo = self.bp_call("get_default_object", {"blueprint": owner})
        toolset = "editor_toolset.toolsets.object.ObjectTools"
        if toolset not in self.library.schemas:
            schema = json.loads(self.library._tool("describe_toolset", {"toolset_name": toolset}))
            self.library.schemas[toolset] = {t["name"].rsplit(".", 1)[-1]: t for t in schema["tools"]}
        return self.library._call(toolset, "get_class", {"instance": cdo})

    def node_ref(self, value):
        node = self.aliases[value] if value in self.aliases else {"refPath": value}
        if self.graph is None or not node["refPath"].startswith(self.graph["refPath"] + "."):
            raise UnrealMCPError(f"Node must belong to the selected graph: {value}")
        return node

    def pin_ref(self, value, direction, require_unconnected=False):
        node_name, separator, pin_name = value.rpartition("::")
        if not separator:
            raise UnrealMCPError("Pin address must be NODE::PIN_NAME")
        info = self.bp_call("get_node_infos", {"nodes": [self.node_ref(node_name)]})[0]
        pins = [p for p in info[direction + "_pins"] if p["name"] == pin_name]
        if len(pins) != 1:
            raise UnrealMCPError(f"Expected one {direction} pin named {pin_name}: {info}")
        if require_unconnected and pins[0]["connected_pins"]:
            raise UnrealMCPError(f"Cannot set a constant on connected pin {value}; unbind it first")
        return pins[0]["pin_id"]
