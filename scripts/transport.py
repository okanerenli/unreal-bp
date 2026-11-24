"""Existing Unreal MCP session, schemas and RPC transport."""
import urllib.request
import json
from .errors import UnrealMCPError

class UnrealTransport:
    ENDPOINT = "http://127.0.0.1:8000/mcp"
    ASSETS = "editor_toolset.toolsets.asset.AssetTools"
    BLUEPRINTS = "editor_toolset.toolsets.blueprint.BlueprintTools"
    ASSET_CREATION = "unreal_bp_assets.AssetCreationTools"

    def __init__(self):
        self.session = None
        self.request_id = 0
        self.schemas = {}
        self.factory_catalog = None

    def _request(self, method, params, notification=False):
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notification:
            self.request_id += 1
            message["id"] = self.request_id
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session is not None:
            headers["Mcp-Session-Id"] = self.session
        request = urllib.request.Request(
            self.ENDPOINT, data=json.dumps(message).encode(), headers=headers
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            if method == "initialize":
                self.session = response.headers["Mcp-Session-Id"]
            body = response.read()
        if notification:
            return
        result = json.loads(body)
        if result["id"] != message["id"]:
            raise UnrealMCPError(f"Mismatched MCP response ID for {method}")
        if "error" in result:
            raise UnrealMCPError(f"{method}: {json.dumps(result['error'])}")
        return result["result"]

    def _tool(self, name, arguments):
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError", False):
            raise UnrealMCPError(f"{name}: {json.dumps(result['content'])}")
        content = result["content"]
        if len(content) != 1 or content[0]["type"] != "text":
            raise UnrealMCPError(f"Unexpected response content from {name}: {result}")
        return content[0]["text"]

    def connect(self):
        self._request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "unreal-bp", "version": "0.1.0"},
        })
        self._request("notifications/initialized", {}, notification=True)
        self.available_toolsets = self._tool("list_toolsets", {})
        for toolset in (self.ASSETS, self.BLUEPRINTS):
            schema = json.loads(self._tool("describe_toolset", {"toolset_name": toolset}))
            self.schemas[toolset] = {
                tool["name"].rsplit(".", 1)[-1]: tool for tool in schema["tools"]
            }

    def _call(self, toolset, tool, arguments):
        if tool not in self.schemas[toolset]:
            raise UnrealMCPError(f"Required Unreal tool is unavailable: {toolset}.{tool}")
        result = json.loads(self._tool("call_tool", {
            "toolset_name": toolset, "tool_name": tool, "arguments": arguments,
        }))
        if "outputSchema" in self.schemas[toolset][tool]:
            return result["returnValue"]
        if result != {"returnValue": None}:
            raise UnrealMCPError(f"Unexpected void result from {tool}: {result}")
        return None  # Tools declared without an output have no return value.

