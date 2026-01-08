"""
Verification tool for fact-checking and validating information.
"""

from langchain.tools import tool
import json
from typing import List


@tool
def verify_fact(claim: str, context: str = "") -> str:
    """
    Verify a factual claim based on available context.
    
    This tool helps assess the credibility of a claim by analyzing
    the provided context and identifying potential verification needs.
    Note: For best results, provide relevant context or sources.
    
    Args:
        claim (str): The statement or fact to verify
        context (str): Supporting context or sources (optional)
    
    Returns:
        str: Verification assessment with confidence level
    
    Examples:
        >>> verify_fact("AI market is worth $11B", context="According to report X...")
        >>> verify_fact("Python is the most popular language")
    """
    try:
        # Simple heuristic-based verification
        # In production, this could integrate with fact-checking APIs
        
        confidence_indicators = {
            "high": ["according to", "research shows", "study found", "data from", 
                    "statistics show", "reported by", "published in"],
            "medium": ["estimated", "approximately", "around", "roughly", "believed"],
            "low": ["rumored", "allegedly", "supposedly", "might", "could be"]
        }
        
        claim_lower = claim.lower()
        context_lower = context.lower()
        combined = f"{claim_lower} {context_lower}"
        
        # Check for confidence indicators
        confidence = "medium"  # default
        for level, indicators in confidence_indicators.items():
            if any(ind in combined for ind in indicators):
                confidence = level
                break
        
        # Check for numbers/statistics (often more verifiable)
        has_numbers = any(char.isdigit() for char in claim)
        has_sources = any(word in context_lower for word in ["source", "according", "report", "study"])
        
        if has_numbers and has_sources:
            confidence = "high"
        elif has_numbers:
            confidence = "medium"
        
        # Generate recommendations
        recommendations = []
        if confidence != "high":
            recommendations.append("Cross-reference with multiple sources")
        if not has_sources:
            recommendations.append("Provide source citations")
        if not has_numbers and "market" in claim_lower or "value" in claim_lower:
            recommendations.append("Obtain specific numerical data")
        
        return json.dumps({
            "status": "success",
            "claim": claim,
            "confidence": confidence,
            "has_supporting_context": len(context) > 0,
            "has_numerical_data": has_numbers,
            "recommendations": recommendations,
            "assessment": f"Claim assessed with {confidence} confidence level"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Verification failed: {str(e)}"
        })


@tool
def check_source_credibility(source_name: str, source_type: str = "website") -> str:
    """
    Assess the credibility of a source.
    
    Args:
        source_name (str): Name of the source (e.g., "Nature", "Wikipedia", "RandomBlog")
        source_type (str): Type of source ("academic", "news", "website", "social_media")
    
    Returns:
        str: Credibility assessment
    
    Example:
        >>> check_source_credibility("Nature", "academic")
        >>> check_source_credibility("Twitter", "social_media")
    """
    try:
        # Credibility rankings (simplified)
        high_credibility = [
            "nature", "science", "cell", "lancet", "nejm",  # Academic journals
            "reuters", "ap news", "bbc", "npr",  # News agencies
            "who", "cdc", "nih", "fda"  # Official institutions
        ]
        
        medium_credibility = [
            "wikipedia", "forbes", "techcrunch", "wired",
            "harvard", "mit", "stanford"  # Universities
        ]
        
        source_lower = source_name.lower()
        
        # Determine credibility
        if any(src in source_lower for src in high_credibility):
            credibility = "high"
            reliability = "Very reliable source"
        elif any(src in source_lower for src in medium_credibility):
            credibility = "medium"
            reliability = "Generally reliable, verify critical claims"
        else:
            credibility = "unknown"
            reliability = "Credibility unknown, verify independently"
        
        # Adjust based on type
        if source_type == "academic":
            credibility = "high" if credibility != "low" else "medium"
        elif source_type == "social_media":
            reliability = "Verify with authoritative sources"
        
        return json.dumps({
            "status": "success",
            "source_name": source_name,
            "source_type": source_type,
            "credibility": credibility,
            "reliability": reliability
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Credibility check failed: {str(e)}"
        })


@tool
def citation_formatter(title: str, url: str, author: str = "", date: str = "") -> str:
    """
    Format a citation in multiple styles.
    
    Args:
        title (str): Title of the source
        url (str): URL of the source
        author (str): Author name (optional)
        date (str): Publication date (optional)
    
    Returns:
        str: Formatted citations in APA, MLA, and Chicago styles
    
    Example:
        >>> citation_formatter("AI in Healthcare", "https://example.com", "Smith, J.", "2024")
    """
    try:
        # Generate different citation styles
        apa = f"{author if author else 'Author'}. ({date if date else 'n.d.'}). {title}. Retrieved from {url}"
        
        mla = f"{author if author else 'Author'}. \"{title}.\" Web. {date if date else 'n.d.'}. <{url}>."
        
        chicago = f"{author if author else 'Author'}. \"{title}.\" Accessed {date if date else 'n.d.'}. {url}."
        
        return json.dumps({
            "status": "success",
            "citations": {
                "APA": apa,
                "MLA": mla,
                "Chicago": chicago,
                "Simple": f"{title} ({url})"
            }
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Citation formatting failed: {str(e)}"
        })
