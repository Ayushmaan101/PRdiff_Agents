from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from state import AgentState

LLM_URL = "http://172.31.192.1:11434"

model = ChatOllama(
    model="qwen2.5-coder:7b",
    base_url=LLM_URL,
    temperature=0
)

def reviewer_agent(state: AgentState):
    code = state.get("diff", "")
    prompt = f"""
    You are a strict Senior QA Engineer. Review this code for:
    1. Division by Zero
    2. Case Sensitivity (e.g., 'Name' vs 'name')

    CODE:
    {code}

    INSTRUCTIONS:
    - If 100% bug-free, end with 'STATUS: APPROVED'.
    - If bugs exist, list them and end with 'STATUS: CHANGES_REQUESTED'.
    """
    response = model.invoke(prompt)
    is_approved = "STATUS: APPROVED" in response.content.upper()
    return {
        "review_comments": state.get("review_comments", []) + [response.content],
        "is_approved": is_approved,
        "messages": [response]
    }

def developer_agent(state: AgentState):
    feedback = state["review_comments"][-1]
    current_code = state["diff"]
    prompt = f"Fix these bugs: {feedback}\n\nCode:\n{current_code}\n\nReturn ONLY code, NO backticks."
    response = model.invoke(prompt)
    clean_code = response.content.replace("```python", "").replace("```", "").strip()
    return {
        "diff": clean_code,
        "revision_count": state.get("revision_count", 0) + 1,
        "messages": [response]
    }

def create_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("reviewer", reviewer_agent)
    workflow.add_node("developer", developer_agent)
    workflow.set_entry_point("reviewer")
    
    def should_continue(state):
        if state["is_approved"] or state["revision_count"] >= 3:
            return END
        return "developer"

    workflow.add_conditional_edges("reviewer", should_continue)
    workflow.add_edge("developer", "reviewer")
    return workflow.compile()