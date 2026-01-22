from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # The current code being reviewed
    code_snippet: str
    
    # Comments from Agent 1 (The Reviewer)
    review_comments: List[str]
    
    # Whether the PR is approved
    is_approved: bool
    
    # The shared conversation history between agents
    messages: Annotated[list, add_messages]
    
    # Tracking the number of revisions to prevent infinite loops
    revision_count: int