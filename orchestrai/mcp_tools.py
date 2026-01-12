from __future__ import annotations
import os
import sys
import json
import socket
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


def repo_path(*parts: str) -> str:
    root = Path(__file__).resolve().parent.parent
    return str((root / Path(*parts)).resolve())


def ensure_weather_server() -> None:
    s = socket.socket()
    try:
        s.settimeout(0.3)
        s.connect(("127.0.0.1", 8000))
        s.close()
        return
    except Exception:
        pass

    print("Starting Weather MCP on :8000")
    DETACHED = 0x00000008 if sys.platform == "win32" else 0
    subprocess.Popen(
        [sys.executable, repo_path("servers", "weather.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=DETACHED,
    )


async def load_mcp_tools() -> Tuple[List[Any], Dict[str, Any]]:
    ensure_weather_server()

    connections: Dict[str, Any] = {
        "notes": {
            "command": sys.executable,
            "args": [repo_path("servers", "notes_server.py")],
            "transport": "stdio",
        },
        "weather": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        },
    }

    browser_cfg_path = Path(repo_path("servers", "browser_mcp.json"))
    if browser_cfg_path.exists():
        cfg = json.loads(browser_cfg_path.read_text(encoding="utf-8"))
        for name, spec in (cfg.get("mcpServers", {}) or {}).items():
            connections[name] = {
                "command": spec.get("command"),
                "args": spec.get("args", []),
                "transport": "stdio",
            }

    client = MultiServerMCPClient(connections)

    try:
        tools = await client.get_tools()
    except Exception as e:
        raise RuntimeError(
            "Failed to load MCP tools. One or more MCP servers failed to start.\n"
            "Common causes:\n"
            "- Node-based MCP servers not installed\n"
            "- Playwright not set up\n"
            "- Windows stdio issues\n\n"
            f"Original error:\n{e}"
        )

    return tools, connections



def filter_tools(tools: List[Any], allow: List[str]) -> List[Any]:
    allowed = []
    for t in tools:
        name = getattr(t, "name", "") or ""
        if any(a in name for a in allow):
            allowed.append(t)
    return allowed

def get_tool_names(tools):
    return sorted({tool.name for tool in tools})
