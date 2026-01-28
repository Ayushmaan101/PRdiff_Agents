from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    repo_name: str
    pr_number: int
    diff: str                   # Holds the current version of the code
    review_comments: List[str]  # History of AI feedback
    is_approved: bool           # The exit condition
    revision_count: int         # Counter to prevent infinite loops
    messages: Annotated[List[BaseMessage], operator.add]