"""Install and verify the editor dependency."""
from pathlib import Path
from .install_editor import install, source_hash
import json
from .errors import UnrealMCPError

def editor_dependency_status(self):
    if f"- {self.ASSET_CREATION}:" not in self.available_toolsets:
        return {"state": "not_loaded"}
    schema = json.loads(self._tool("describe_toolset", {"toolset_name": self.ASSET_CREATION}))
    self.schemas[self.ASSET_CREATION] = {t["name"].rsplit(".", 1)[-1]: t for t in schema["tools"]}
    if "dependency_status" not in self.schemas[self.ASSET_CREATION]:
        return {"state": "legacy_loaded"}
    result = json.loads(self._call(self.ASSET_CREATION, "dependency_status", {}))
    result["state"] = "current" if result["loaded_hash"] == source_hash() else "outdated"
    return result

def dependencies(self, project, check_only=False):
    runtime = self.editor_dependency_status()
    if "project" in runtime and Path(runtime["project"]).resolve() != Path(project).resolve():
        raise UnrealMCPError(f"Connected editor belongs to {runtime['project']}, not {project}")
    result = install(project, check_only=check_only)
    result["runtime"] = runtime
    result["native_ready"] = (result["native"]["source_ready"]
                              and runtime.get("native", {}).get("state") == "current")
    result["ready"] = (result["disk_ready"] and runtime["state"] == "current"
                       and Path(runtime["module"]).resolve() == Path(result["module"]).resolve())
    if result["ready"]:
        del result["load_code"]
    return result
