import os
from dotenv import load_dotenv
load_dotenv()

import mcp.server.fastmcp as fastmcp
from github_utils import get_pr_diff, post_pr_comment

# 1.Tool Server Initialization
mcp_server = fastmcp.FastMCP("GitHub Agent Tools")

# 2. Wrap the "Get Diff" function
@mcp_server.tool()
def fetch_diff(repo_name: str, pr_number: int) -> str:
    """Fetches code changes and the title from a GitHub PR."""
    diff, title = get_pr_diff(repo_name, pr_number)
    return f"Title: {title}\n\n{diff}"

# 3. Wrap the "Post Comment" function
@mcp_server.tool()
def add_comment(repo_name: str, pr_number: int, comment: str) -> str:
    """Posts a review or feedback comment to a specific GitHub PR."""
    post_pr_comment(repo_name, pr_number, comment)
    return "Comment posted successfully!"

if __name__ == "__main__":
    # tto keep the server running and waiting for instructions
    mcp_server.run()