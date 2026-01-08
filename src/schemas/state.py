"""
State schemas for the ResearchPro Agent.
Defines custom state management for tracking research progress.
"""

from typing import List, Dict, Any, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from datetime import datetime
from operator import add


class ResearchState(TypedDict):
    """
    Extended state schema to track research progress and context.
    
    Uses Annotated with operator.add to properly accumulate messages.
    """
    messages: Annotated[List, add]  # Messages accumulate with add operator
    citations: Annotated[List[Dict], add]  # Citations accumulate
    progress: int  # Progress counter


class Citation(BaseModel):
    """Single citation entry with metadata."""
    
    id: int = Field(description="Unique citation identifier")
    title: str = Field(description="Title of the source")
    url: str = Field(description="URL of the source")
    accessed_date: str = Field(description="Date when source was accessed")
    relevance_score: float = Field(ge=0, le=1, description="Relevance score 0-1")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "AI in Healthcare 2024",
                "url": "https://example.com/article",
                "accessed_date": "2024-01-07",
                "relevance_score": 0.95
            }
        }


class ResearchFinding(BaseModel):
    """Individual research finding with supporting information."""
    
    topic: str = Field(description="Main topic or category")
    content: str = Field(description="Detailed finding content")
    confidence: str = Field(description="Confidence level: High, Medium, or Low")
    citations: List[int] = Field(description="List of citation IDs supporting this finding")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Market Growth",
                "content": "The AI healthcare market is projected to grow from $11B to $188B by 2030",
                "confidence": "High",
                "citations": [1, 2, 3]
            }
        }


class ResearchReport(BaseModel):
    """
    Complete structured research report output.
    
    This defines the final output format for the agent,
    ensuring consistent, high-quality research deliverables.
    """
    
    executive_summary: str = Field(
        description="2-3 sentence overview of key findings"
    )
    findings: List[ResearchFinding] = Field(
        description="List of detailed research findings organized by topic"
    )
    key_statistics: List[str] = Field(
        description="Important statistics and data points"
    )
    citations: List[Citation] = Field(
        description="All sources cited in the research"
    )
    recommendations: List[str] = Field(
        description="Recommendations for further reading or action"
    )
    limitations: List[str] = Field(
        description="Acknowledged limitations or gaps in the research"
    )
    research_date: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        description="Date when research was conducted"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "executive_summary": "AI adoption in healthcare is accelerating rapidly...",
                "findings": [
                    {
                        "topic": "Market Size",
                        "content": "Current market valued at $11B",
                        "confidence": "High",
                        "citations": [1, 2]
                    }
                ],
                "key_statistics": [
                    "Market size: $11B (2024)",
                    "Projected growth: 32% CAGR"
                ],
                "citations": [
                    {
                        "id": 1,
                        "title": "Healthcare AI Report 2024",
                        "url": "https://example.com",
                        "accessed_date": "2024-01-07",
                        "relevance_score": 0.95
                    }
                ],
                "recommendations": [
                    "Further research on implementation costs needed"
                ],
                "limitations": [
                    "Limited data from developing countries"
                ],
                "research_date": "2024-01-07"
            }
        }
