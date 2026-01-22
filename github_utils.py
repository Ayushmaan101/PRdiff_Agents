import os
from github import Github
from dotenv import load_dotenv

# Load the token from our secret .env file
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

# Initialize the GitHub client
g = Github(token)

def get_pr_diff(repo_name: str, pr_number: int):
    """Fetches the code changes (diff) from a specific GitHub PR."""
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    # Get all files changed in this PR
    files = pr.get_files()
    
    diff_content = ""
    for file in files:
        diff_content += f"File: {file.filename}\n"
        diff_content += f"Changes:\n{file.patch}\n\n"
        
    return diff_content, pr.title

def post_pr_comment(repo_name: str, pr_number: int, comment: str):
    """Posts the final agent review as a comment on the PR."""
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(comment)