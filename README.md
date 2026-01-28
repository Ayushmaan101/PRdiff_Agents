Here is the updated content for your README.md formatted with a professional tone and no emojis.

PR-Diff AI Agent (PoC)
An automated code review system built with LangGraph, Model Context Protocol (MCP), and the GitHub API. This project uses a stateful multi-agent architecture to autonomously analyze Pull Request "diffs," identify bugs, and iterate on fixes directly within GitHub PR comments.

Recent Upgrades (MCP Migration)
MCP Tool Architecture: Decoupled GitHub interactions into a dedicated MCP server for modularity and scalability.

Dynamic CLI: Supports any repository and PR number via command-line arguments (e.g., python mcp_client_host.py <repo> <pr_number>).

Stateful Agent Loop: Improved iterative logic between the "Senior Reviewer" and "Feature Developer" using LangGraph.

Features
Multi-Agent Workflow: Simulates a real-world code review lifecycle between two specialized AI agents.

Local LLM: Powered by qwen2.5-coder:7b via Ollama, ensuring data privacy and low-latency inference.

Automated Feedback: Fetches real-time diffs and posts structured status reports (APPROVED or CHANGES_REQUESTED) to GitHub.

WSL2 Optimized: Developed and tested on Ubuntu/WSL2 on Windows.

Architecture
The system follows a directed acyclic graph (DAG) managed by LangGraph:

Orchestrator: Parses CLI input and initializes the MCP client connection.

Reviewer Agent: Utilizes MCP tools to fetch PR diffs and analyze them for logical flaws.

Developer Agent: Proposes code fixes based on the reviewer's critique.

Iterative Resolution: The agents loop until the code is approved or the revision limit is reached.

Setup Instructions
Clone the repo: git clone https://github.com/Ayushmaan101/PRdiff_Agents.git

Conda Setup: conda env create -f environment.yml && conda activate prdiff_agent

MCP Server Configuration: Ensure mcp_server.py is configured with your GITHUB_TOKEN.

Ollama: Ensure qwen2.5-coder:7b is pulled and Ollama is running on your host.

Usage
To trigger a review on a specific Pull Request, run:

Bash
python mcp_client_host.py <username/repo> <pr_number>
Technologies Used
Model Context Protocol (MCP) (Tool-Agent communication)

LangGraph (State management & workflow orchestration)

Ollama (Local LLM inference)

PyGithub (GitHub API integration)

FastAPI/Uvicorn (Internal MCP server communication)