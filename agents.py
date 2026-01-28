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
    """Node 1: Evaluates the code objectively."""
    code = state.get("diff", "")
    
    prompt = f"""
    You are a strict Senior Quality Assurance Engineer. 
    Review the following Python code for logical bugs (like Division by Zero) and syntax errors (like Case Sensitivity).

    CODE TO REVIEW:
    {code}

    INSTRUCTIONS:
    1. If the code correctly handles division by zero AND has no case-sensitivity errors, you MUST end with 'STATUS: APPROVED'.
    2. If there are remaining bugs, list them specifically and end with 'STATUS: CHANGES_REQUESTED'.
    3. Be concise. Do not suggest 'cleaner' code if the logic is already correct.
    """
    
    response = model.invoke(prompt)
    is_approved = "STATUS: APPROVED" in response.content.upper()
    
    new_comments = state.get("review_comments", []) + [response.content]
    
    return {
        "review_comments": new_comments,
        "is_approved": is_approved,
        "messages": [response]
    }

def developer_agent(state: AgentState):
    """Node 2: Fixes identified bugs."""
    feedback = state["review_comments"][-1]
    current_code = state["diff"]
    
    prompt = f"""
    You are a Software Developer. Fix the bugs identified by the reviewer.
    
    IDENTIFIED BUGS:
    {feedback}
    
    CURRENT CODE:
    {current_code}

    OUTPUT INSTRUCTIONS:
    - Return ONLY the corrected Python code.
    - Do NOT include markdown backticks (```).
    - Do NOT include any explanations.
    """
    
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