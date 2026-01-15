from __future__ import annotations
import asyncio
from dotenv import load_dotenv 

from orchestrai.metrics import MetricsTracker
from .mcp_tools import load_mcp_tools
from .workflow import run_orchestration


async def main():
    load_dotenv()  
    
    print("\nLoading MCP tools...")
    tools, _ = await load_mcp_tools()
    
    metrics = MetricsTracker()

    print("\nOrchestrAI MCP")
    print("=" * 44)
    print("Examples:")
    print("  - Create a note titled 'ideas' with content 'Ship demo on Friday'")
    print("  - Weather in New York and create a packing checklist note")
    print("  - Search for python tutorials")  # ← UPDATE THIS (remove Airbnb example)
    print("Type 'exit' to quit.")
    print("=" * 44)

    while True:
        q = input("You: ").strip()
        
        if not q:
            continue
        
        if q.lower() == "exit":
            print("👋 Goodbye!")
            break
        
        # Handle metrics command
        if q.lower().startswith("metrics"):
            parts = q.split()
            last_n = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
            metrics.print_summary(last_n)
            continue
        
        try:
            result = await run_orchestration(q, tools)
            print("\nFinal Answer:")
            print(result.final_answer)
            print()
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user\n")
            continue
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue


if __name__ == "__main__":
    asyncio.run(main())
