"""
Middleware components for the ResearchPro Agent.
Handles message management, error handling, and dynamic prompts.
"""

from typing import Dict, Any, Optional


def trim_messages_middleware(state: Dict[str, Any], max_messages: int = 20) -> Optional[Dict[str, Any]]:
    """
    Trim conversation history to prevent context overflow.
    
    Keeps the system prompt and the most recent messages.
    
    Args:
        state: Current agent state
        max_messages: Maximum number of messages to keep
    
    Returns:
        Updated state with trimmed messages, or None if no trimming needed
    """
    messages = state.get("messages", [])
    
    if len(messages) <= max_messages:
        return None
    
    # Keep system message (first) + last N messages
    system_msg = messages[0] if messages and messages[0].get("role") == "system" else None
    recent_messages = messages[-(max_messages-1):] if system_msg else messages[-max_messages:]
    
    if system_msg:
        trimmed_messages = [system_msg] + recent_messages
    else:
        trimmed_messages = recent_messages
    
    return {"messages": trimmed_messages}


def get_dynamic_system_prompt(user_level: str = "general") -> str:
    """
    Generate system prompt based on user expertise level.
    
    Args:
        user_level: User expertise level ("expert", "beginner", "general")
    
    Returns:
        Customized system prompt
    """
    base_prompt = """You are ResearchPro, an expert research assistant with extensive knowledge.

IMPORTANT INSTRUCTIONS:
1. First, try to answer using your built-in knowledge
2. Use web_search ONLY when you need current information, specific data, or verification
3. Use scrape_webpage ONLY when the user provides a specific URL to analyze
4. After using a tool ONCE, provide your final comprehensive answer immediately
5. DO NOT call multiple tools in sequence - one tool call is enough

Available Tools:
- web_search: Search for current information online (use for recent events, statistics, comparisons)
- scrape_webpage: Extract content from a specific URL (use only when user provides a URL)

Output Format Requirements:
- Write in clean, plain text format suitable for terminal display
- NO markdown tables (|, --, etc.) - use simple aligned text instead
- NO asterisks for bold (**text**) - use UPPERCASE or simple emphasis
- Structure with clear headings using numbers or bullets
- Use indentation and spacing for readability
- Include sources when you used web_search
- Be comprehensive but well-organized

Example of good formatting:
  COMPARISON: Honda vs Toyota
  
  1. Overview
     Honda: 4.3M units sold, focuses on sporty cars
     Toyota: 10.5M units sold, broadest lineup
  
  2. Reliability
     Honda: 73/100 score, good CVT issues
     Toyota: 84/100 score, top-rated

"""
    
    if user_level == "expert":
        return base_prompt + "\nCommunication Style: Use technical terminology and detailed analysis. Assume advanced knowledge."
    elif user_level == "beginner":
        return base_prompt + "\nCommunication Style: Explain concepts in simple terms with examples. Avoid jargon."
    else:
        return base_prompt + "\nCommunication Style: Professional, objective, and informative. Balance technical accuracy with accessibility."


def format_tool_error(error: Exception, tool_name: str) -> str:
    """
    Format tool error messages in a user-friendly way.
    
    Args:
        error: The exception that occurred
        tool_name: Name of the tool that failed
    
    Returns:
        Formatted error message
    """
    error_msg = str(error)
    
    # Provide helpful error messages
    if "timeout" in error_msg.lower():
        return f"The {tool_name} tool timed out. Please try again or use a different approach."
    elif "not found" in error_msg.lower():
        return f"The {tool_name} tool couldn't find the requested resource. Please check the input and try again."
    elif "permission" in error_msg.lower():
        return f"The {tool_name} tool doesn't have permission to access the resource. Please check permissions."
    else:
        return f"The {tool_name} tool encountered an error: {error_msg}. Please try an alternative approach."
