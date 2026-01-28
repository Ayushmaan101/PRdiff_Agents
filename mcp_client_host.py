import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_orchestrator():
    # 1. Define how to start Server A
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"], 
    )

    # 2. Start the connection
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP connection
            await session.initialize()
            print("--- Connection Established ---")

            # 3. List tools just to confirm we see them
            tool_list = await session.list_tools()
            print(f"Server A tools found: {[t.name for t in tool_list.tools]}")

            # 4. EXECUTE A REAL TEST
            # IMPORTANT: Replace these strings with your real GitHub info!
            REPO = "Ayushmaan101/PRdiff_test" 
            PR_NUM = 1 

            print(f"\nRequesting diff for {REPO} PR #{PR_NUM}...")
            
            try:
                # This 'throws' the request from Server B to Server A
                result = await session.call_tool(
                    "fetch_diff", 
                    arguments={
                        "repo_name": REPO,
                        "pr_number": PR_NUM
                    }
                )
                
                # Print the 'diff' string that came all the way back from Server A
                print("\n--- RECEIVED DATA FROM SERVER A ---")
                print(result.content[0].text)
                print("-----------------------------------")
                
            except Exception as e:
                print(f"Error calling tool: {e}")

if __name__ == "__main__":
    asyncio.run(run_orchestrator())