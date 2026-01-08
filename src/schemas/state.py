"""State schemas for the ResearchPro Agent."""

from typing import List, Dict, Annotated
from typing_extensions import TypedDict
from operator import add


class ResearchState(TypedDict):
    """State schema for the agent with message accumulation."""
    messages: Annotated[List, add]  # Messages accumulate
    citations: Annotated[List[Dict], add]  # Citations accumulate
    progress: int  # Progress counter
