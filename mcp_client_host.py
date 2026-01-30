import asyncio
import os
import sys
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agents import create_graph

load_dotenv()

async def run_orchestrator():
    # Eg usage: python mcp_client_host.py Ayushmaan101/PRdiff_test 1
    if len(sys.argv) > 2:
        target_repo = sys.argv[1]
        target_pr = int(sys.argv[2])
    else:
        # Defaults arguments
        target_repo = "Ayushmaan101/PRdiff_test"
        target_pr = 1

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"], 
    )

    print(f"Starting MCP Orchestrator for {target_repo} #{target_pr}")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(f"Connected to Server A")

            print(f"Fetching diff for {target_repo}")
            try:
                mcp_result = await session.call_tool("fetch_diff", arguments={
                    "repo_name": target_repo,
                    "pr_number": target_pr
                })
                initial_diff = mcp_result.content[0].text
            except Exception as e:
                print(f"Error fetching diff: {e}")
                return

            app = create_graph()
            state = {
                "repo_name": target_repo,
                "pr_number": target_pr,
                "diff": initial_diff,
                "review_comments": [],
                "is_approved": False,
                "revision_count": 0,
                "messages": []
            }

            print("Starting Internal Review Fix Loop")

            current_final_state = state

            async for event in app.astream(state):
                for node_name, state_update in event.items():
                    print(f"\n[Node: {node_name}] is running...")
                    current_final_state.update(state_update)
                    
                    if node_name == "reviewer":
                        is_app = state_update.get("is_approved", False)
                        status = "APPROVED" if is_app else "CHANGES REQUESTED"
                        print(f"Status: {status}")

            # --- DUAL EXTRACTION LOGIC ---
            # Extract the final textual feedback from the Reviewer
            if current_final_state["review_comments"]:
                final_feedback = current_final_state["review_comments"][-1]
            else:
                final_feedback = "No qualitative feedback generated."
            
            # Extract the final code version from the Developer
            final_code_fix = current_final_state.get("diff", "No code changes proposed.")
            
            print(f"\nPosting combined final results to GitHub via MCP")
            try:
                # Formatting a structured professional report
                report_body = (
                    f"## AI Review Final Report\n\n"
                    f"### Analysis & Feedback\n"
                    f"{final_feedback}\n\n"
                    f"--- \n"
                    f"### Proposed Optimized Code\n"
                    f"```python\n"
                    f"{final_code_fix}\n"
                    f"```"
                )

                await session.call_tool("add_comment", arguments={
                    "repo_name": target_repo,
                    "pr_number": target_pr,
                    "comment": report_body
                })
                print("Final comment with code fix posted successfully!")
            except Exception as e:
                print(f"Error posting comment: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_orchestrator())
    except KeyboardInterrupt:
        print("\nStopping Orchestrator...")