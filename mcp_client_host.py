import asyncio
import os
import sys
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agents import create_graph

load_dotenv()

async def run_orchestrator():
    if len(sys.argv) > 2:
        target_repo, target_pr = sys.argv[1], int(sys.argv[2])
    else:
        target_repo, target_pr = "Ayushmaan101/PRdiff_test", 1

    server_params = StdioServerParameters(command="python", args=["mcp_server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(f"✅ Connected to Server A | Target: {target_repo} #{target_pr}")

            mcp_result = await session.call_tool("fetch_diff", arguments={
                "repo_name": target_repo, "pr_number": target_pr
            })
            
            app = create_graph()
            state = {
                "repo_name": target_repo, "pr_number": target_pr,
                "diff": mcp_result.content[0].text, "review_comments": [],
                "is_approved": False, "revision_count": 0, "messages": []
            }

            print("🤖 Starting Internal Review-Fix Loop...")
            current_final_state = state
            async for event in app.astream(state):
                for node_name, state_update in event.items():
                    print(f"[{node_name}] running...")
                    current_final_state.update(state_update)

            final_feedback = current_final_state["review_comments"][-1]
            status_icon = "✅" if current_final_state["is_approved"] else "⚠️"
            
            print(f"\n🚀 Posting final results to GitHub...")
            await session.call_tool("add_comment", arguments={
                "repo_name": target_repo, "pr_number": target_pr,
                "comment": f"## AI Review Report {status_icon}\n\n{final_feedback}"
            })
            print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(run_orchestrator())