from __future__ import annotations
from mcp.server.fastmcp import FastMCP 
from pathlib import Path
import json
from typing import List, Dict, Optional

mcp = FastMCP("Notes")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
NOTES_FILE = DATA_DIR / "notes.json"

def _load() -> Dict[str, str]:
    if not NOTES_FILE.exists():
        return{}
    try:
        return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
    except Exception:
        # corrupted file? start fresh
        return {}

def _save(notes: Dict[str, str]) -> None:
    NOTES_FILE.write_text(
        json.dumps(notes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

@mcp.tool()
def list_notes()-> List[str]:
    """Return all note titles."""
    notes = _load()
    return sorted(notes.keys())

@mcp.tool()
def add_note(title: str, content: str) -> str:
    """Create or overwrite a note by title."""
    title = title.strip()
    if not title:
        return "Title cannot be empty."
    notes = _load()
    notes[title] = content
    _save(notes)
    return f"Saved note '{title}' ({len(content)} chars)."

@mcp.tool()
def get_note(title: str) -> Optional[str]:
    """Get the content of a note by title."""
    notes = _load()
    return notes.get(title)

@mcp.tool()
def delete_note(title: str) -> str:
    """Delete a note by title."""
    notes = _load()
    if title in notes:
        del notes[title]
        _save(notes)
        return f"Deleted note '{title}'."
    return f"No note found with title '{title}'."

@mcp.tool()
def search_notes(query: str, max_results:int =5) -> List[Dict[str,str]]:
    """Search notes by substring; returns matches with a small excerpt."""
    notes = _load()
    q = query.lower()
    results: List[Dict[str, str]] = []
    for title, content in notes.items():
        if q in title.lower() or q in content.lower():
            idx = content.lower().find(q)
            if idx == -1:
                excerpt = content[:120]
            else:
                start = max(0, idx - 40)
                end = min(len(content), idx + len(q) + 40)
                excerpt = content[start:end]
            results.append({"title": title, "excerpt": excerpt})
        if len(results) >= max_results:
            break
    return results

if __name__ == "__main__":
    # stdio transport so the client can spawn it as a subprocess
    mcp.run(transport="stdio")