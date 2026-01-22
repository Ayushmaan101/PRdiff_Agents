from langchain_ollama import ChatOllama
from state import AgentState

# We point to your Windows Gateway IP you found earlier
# Replace '172.31.192.1' with the IP you got from 'ip route'
LLM_URL = "http://172.31.192.1:11434"

model = ChatOllama(
    model="qwen2.5-coder:7b",
    base_url=LLM_URL,
    temperature=0 # We want consistent code reviews, not creative ones
)

def reviewer_agent(state: AgentState):
    code = state["code_snippet"]
    
    prompt = f"""
    You are a Senior Software Engineer. Review this code:
    {code}
    
    CRITERIA:
    - If there are ANY bugs or improvements needed, list them and end with 'STATUS: CHANGES_REQUESTED'.
    - If and ONLY IF the code is 100% perfect, end with 'STATUS: APPROVED'.
    """
    
    response = model.invoke(prompt)
    
    # New strict check
    is_approved = "STATUS: APPROVED" in response.content.upper()
    
    # Only send comments if we didn't approve
    comments = [response.content] if not is_approved else []
    
    return {
        "review_comments": comments,
        "is_approved": is_approved,
        "messages": [response]
    }

def developer_agent(state: AgentState):
    """Agent 2: Acts as a Feature Dev resolving the PR based on feedback."""
    original_code = state["code_snippet"]
    feedback = state["review_comments"][-1] # Get the latest feedback
    
    prompt = f"""
    You are a Software Developer. You must fix the code based on the Senior Engineer's feedback.
    
    ORIGINAL CODE:
    {original_code}
    
    FEEDBACK TO RESOLVE:
    {feedback}
    
    Return ONLY the corrected code without any explanations or markdown backticks.
    """
    
    response = model.invoke(prompt)
    
    # Increment revision count to keep track of iterations
    new_count = state.get("revision_count", 0) + 1
    
    return {
        "code_snippet": response.content,
        "revision_count": new_count,
        "messages": [response]
    }