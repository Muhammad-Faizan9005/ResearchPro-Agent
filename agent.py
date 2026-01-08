"""
ResearchPro Agent - An intelligent research assistant using LangChain and Ollama Cloud.

This agent demonstrates advanced LangChain concepts:
- Tool Calling with 16 custom tools
- Structured Output with Pydantic
- State Management with TypedDict
- Middleware for message handling
- Ollama Cloud API (llama3.1:8b)
"""

import os
from dotenv import load_dotenv
from typing import Literal, Annotated
from typing_extensions import TypedDict

# Load environment variables from .env file
load_dotenv()

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import our custom components
from src.schemas import ResearchState, ResearchReport
from src.middleware import get_dynamic_system_prompt, format_tool_error
from src.tools import (
    web_search,
    web_search_simple,
    calculate,
    percentage_change,
    compound_growth_rate,
    scrape_webpage,
    extract_links,
    read_pdf,
    read_text_file,
    list_directory,
    store_finding,
    retrieve_finding,
    list_all_findings,
    verify_fact,
    check_source_credibility,
    citation_formatter
)


class AgentConfig:
    """Configuration for the ResearchPro Agent."""
    
    def __init__(
        self,
        model_name: str = "gpt-oss:120b-cloud",
        base_url: str = "http://localhost:11434",
        api_key: str = None,
        temperature: float = 0.3,
        user_level: Literal["expert", "beginner", "general"] = "general"
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key or os.getenv("OLLAMA_API_KEY")
        self.temperature = temperature
        self.user_level = user_level


class ResearchProAgent:
    """
    Main ResearchPro Agent class.
    
    This agent uses a ReAct (Reasoning + Acting) pattern to conduct research.
    It can search the web, calculate numbers, scrape pages, read documents,
    store findings, and verify facts.
    """
    
    def __init__(self, config: AgentConfig = None):
        """Initialize the ResearchPro Agent."""
        self.config = config or AgentConfig()
        
        # Initialize the LLM - use OpenAI client for cloud, Ollama for local
        if self.config.api_key:
            # Ollama Cloud uses OpenAI-compatible API
            self.llm = ChatOpenAI(
                model=self.config.model_name,
                base_url=f"{self.config.base_url}/v1",
                api_key=self.config.api_key,
                temperature=self.config.temperature
            )
        else:
            # Local Ollama instance
            self.llm = ChatOllama(
                model=self.config.model_name,
                base_url=self.config.base_url,
                temperature=self.config.temperature
            )
        
        # Bind only essential tools to the LLM
        self.tools = [
            web_search,
            scrape_webpage,
        ]
        
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build the agent graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        
        # Define the agent node
        def agent_node(state: ResearchState) -> ResearchState:
            """
            Agent reasoning node.
            
            The agent decides whether to:
            1. Use a tool to gather more information (max 1 time)
            2. Provide a final answer
            """
            messages = state["messages"]
            iteration_count = state.get("progress", 0)
            
            # Add system prompt if not present
            if not messages or not isinstance(messages[0], SystemMessage):
                system_prompt = get_dynamic_system_prompt(self.config.user_level)
                messages = [SystemMessage(content=system_prompt)] + messages
            
            # After first tool call, force final answer
            if iteration_count >= 1:
                # Check if we have any tool messages
                has_tool_results = any(hasattr(m, '__class__') and m.__class__.__name__ == 'ToolMessage' for m in messages)
                
                if has_tool_results:
                    # Force final answer with very explicit instruction
                    force_msg = HumanMessage(content="STOP. You have all the information you need from the tools. Now write a comprehensive final answer. Write your answer as plain text. Do NOT call any more tools.")
                    messages = messages + [force_msg]
                    
                    # Use model WITHOUT tool binding
                    response = self.llm.invoke(messages)
                    
                    # If response is still empty, try to provide something useful
                    if not response.content:
                        response = AIMessage(content="I apologize, but I encountered an issue generating the final answer. Please try rephrasing your question or asking something different.")
                    
                    return {"messages": [response], "progress": iteration_count + 1}
            
            # First iteration - allow tool use
            response = self.llm_with_tools.invoke(messages)
            
            # Return only the NEW message to be added
            return {"messages": [response], "progress": iteration_count + 1}
        
        # Define the tools node
        tool_node = ToolNode(self.tools)
        
        # Define routing function
        def should_continue(state: ResearchState) -> Literal["continue", "end"]:
            """
            Determine whether to continue or end.
            
            Allow only ONE tool call, then force final answer.
            """
            messages = state["messages"]
            last_message = messages[-1]
            iteration_count = state.get("progress", 0)
            
            # Stop after 2 iterations (1 tool call + 1 final answer)
            if iteration_count >= 2:
                return "end"
            
            # Check if there are tool calls
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "continue"
            return "end"
        
        # Build the graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile the graph
        return workflow.compile()
    
    def research(self, query: str, max_iterations: int = 10) -> dict:
        """
        Conduct research on a given query.
        
        Args:
            query: The research question or topic
            max_iterations: Maximum number of agent-tool cycles
        
        Returns:
            Final state with messages and results
        """
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "citations": [],
            "progress": 0
        }
        
        # Run the graph
        try:
            final_state = self.graph.invoke(
                initial_state,
                config={"recursion_limit": max_iterations}
            )
            return final_state
        except Exception as e:
            error_msg = format_tool_error(e, "agent")
            return {
                "messages": initial_state["messages"] + [
                    AIMessage(content=f"An error occurred: {error_msg}")
                ],
                "citations": [],
                "progress": 0
            }
    
    def get_final_answer(self, state: dict) -> str:
        """Extract the final answer from the state."""
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, AIMessage):
                return last_message.content
        return "No answer generated."
    
    def stream_research(self, query: str):
        """
        Stream research results in real-time.
        
        Args:
            query: The research question or topic
        
        Yields:
            State updates as they occur
        """
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "citations": [],
            "progress": 0
        }
        
        for state in self.graph.stream(initial_state):
            yield state


# Convenience function for quick usage
def create_agent(
    model_name: str = "gpt-oss:120b-cloud",
    temperature: float = 0.3,
    user_level: str = "general"
) -> ResearchProAgent:
    """
    Create a ResearchPro Agent with custom configuration.
    
    Args:
        model_name: Ollama model to use (default: gemma2:2b)
        temperature: LLM temperature (0.0-1.0)
        user_level: User expertise level ("expert", "beginner", "general")
    
    Returns:
        Configured ResearchProAgent instance
    
    Example:
        >>> agent = create_agent(temperature=0.5, user_level="beginner")
        >>> result = agent.research("What is photosynthesis?")
        >>> print(agent.get_final_answer(result))
    """
    config = AgentConfig(
        model_name=model_name,
        temperature=temperature,
        user_level=user_level
    )
    return ResearchProAgent(config)


if __name__ == "__main__":
    # Quick test
    print("🔬 ResearchPro Agent initialized!")
    print("📚 Tools available:", len(ResearchProAgent(AgentConfig()).tools))
    print("\nTo use the agent:")
    print("  from agent import create_agent")
    print("  agent = create_agent()")
    print("  result = agent.research('Your question here')")
    print("  print(agent.get_final_answer(result))")
