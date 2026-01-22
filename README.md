# PR-Diff AI Agent (PoC)

An automated code review system built with **LangGraph**, **Ollama**, and **GitHub API**. This project uses a multi-agent architecture to analyze Pull Request "diffs," identify bugs, and suggest fixes directly on GitHub.

## Features
- **Multi-Agent Workflow**: Features a "Senior Reviewer" and "Feature Developer" agent loop.
- **Local LLM**: Powered by `qwen2.5-coder:7b` running locally via Ollama for privacy and speed.
- **Automated Feedback**: Fetches real-time GitHub PR data and posts fixes back as comments.
- **WSL2 Optimized**: Architected to run in Linux while leveraging Windows hardware.

## Architecture
The system follows a stateful directed graph:
1. **Reviewer Agent**: Analyzes code diffs for logical bugs and security flaws.
2. **Developer Agent**: Receives feedback and rewrite the code snippet.
3. **Loop**: The reviewer re-evaluates the fix until approval or max revisions (3) are reached.

## Setup Instructions
1. **Clone the repo**: `git clone <your-repo-url>`
2. **Conda Setup**: `conda env create -f environment.yml && conda activate prdiff_agent`
3. **Ollama**: Ensure Ollama is running on your host machine with `qwen2.5-coder:7b` pulled.
4. **Environment Variables**: Create a `.env` file with your `GITHUB_TOKEN`.

## Technologies Used
- **LangGraph** (State management)
- **LangChain** (LLM Orchestration)
- **Ollama** (Local Model Inference)
- **PyGithub** (GitHub API Wrapper)
- **Ubuntu/WSL2** (Development Environment)

## If you want to clone my setup exactly, you just need to run this in your terminal:
"conda env create -f environment.yml"

## Workflow Visualization
![Project Graph](./graph_viz.png)