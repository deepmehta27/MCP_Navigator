from __future__ import annotations
import asyncio

from .mcp_tools import load_mcp_tools
from .workflow import run_orchestration


async def main():
    tools, _ = await load_mcp_tools()

    print("\nOrchestrAI MCP")
    print("=" * 44)
    print("Examples:")
    print("  - Create a note titled 'ideas' with content 'Ship demo on Friday'")
    print("  - Weather in New York and create a packing checklist note")
    print("  - Find cheapest Airbnb stays in NYC for Aug 13 and summarize options")
    print("Type 'exit' to quit.")
    print("=" * 44)

    while True:
        q = input("\nYou: ").strip()
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            print("bye!")
            return

        result = await run_orchestration(q, tools)
        print("\nFinal Answer:\n" + result.final_answer)


if __name__ == "__main__":
    asyncio.run(main())
