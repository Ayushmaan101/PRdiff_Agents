from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    repo_name: str
    pr_number: int
    diff: str                   # Current code version
    review_comments: List[str]  # Feedback history
    is_approved: bool           # Approval status
    revision_count: int         # Loop safety counter
    messages: Annotated[List[BaseMessage], operator.add]