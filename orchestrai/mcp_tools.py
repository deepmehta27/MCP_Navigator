from __future__ import annotations

import os
import sys
import json
import socket
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


def repo_path(*parts: str) -> str:
    root = Path(__file__).resolve().parent.parent
    return str((root / Path(*parts)).resolve())


def ensure_weather_server() -> None:
    """Start Weather MCP server and wait until it's ready"""
    
    # Check if already running
    s = socket.socket()
    try:
        s.settimeout(0.3)
        s.connect(("127.0.0.1", 8000))
        s.close()
        print("✅ Weather MCP already running on :8000")
        return
    except Exception:
        pass
    
    # Start the server
    print("🚀 Starting Weather MCP on :8000...")
    DETACHED = 0x00000008 if sys.platform == "win32" else 0
    subprocess.Popen(
        [sys.executable, repo_path("servers", "weather.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=DETACHED,
    )
    
    # ✅ CRITICAL FIX: Wait for server to actually start
    max_attempts = 20  # Try for 10 seconds
    for attempt in range(max_attempts):
        time.sleep(0.5)  # Wait 500ms
        s = socket.socket()
        try:
            s.settimeout(0.3)
            s.connect(("127.0.0.1", 8000))
            s.close()
            print(f"✅ Weather MCP ready after {(attempt + 1) * 0.5:.1f}s")
            return  # ← Only returns when server is ACTUALLY ready
        except Exception:
            continue
    
    # If we get here, server never started
    raise RuntimeError(
        "❌ Weather MCP failed to start after 10 seconds.\n"
        "Check if port 8000 is already in use or if weather.py has errors."
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
    
    # Load external MCP servers from browser_mcp.json
    browser_cfg_path = Path(repo_path("servers", "browser_mcp.json"))
    
    if browser_cfg_path.exists():
        cfg = json.loads(browser_cfg_path.read_text(encoding="utf-8"))
        for name, spec in (cfg.get("mcpServers", {}) or {}).items():
            # Replace env vars in args
            args = spec.get("args", [])
            replaced_args = []
            for arg in args:
                # Replace ${VAR_NAME} with environment variable
                for key, value in os.environ.items():
                    arg = arg.replace(f"${{{key}}}", value)
                replaced_args.append(arg)
            
            connections[name] = {
                "command": spec.get("command"),
                "args": replaced_args,
                "transport": "stdio",
            }
    
    client = MultiServerMCPClient(connections)
    
    try:
        tools = await client.get_tools()
    except Exception as e:
        raise RuntimeError(
            "Failed to load MCP tools. One or more MCP servers failed to start.\n"
            "Common causes:\n"
            "- Remote MCP server unreachable\n"
            "- Invalid API keys\n"
            "- Network connectivity issues\n\n"
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
