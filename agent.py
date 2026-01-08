"""
ResearchPro Agent - An intelligent research assistant using LangChain and Ollama.

This agent demonstrates:
- Tool Calling with 2 essential tools (web_search, scrape_webpage)
- State Management with TypedDict
- Middleware for dynamic prompts
- Local Ollama (gpt-oss:120b-cloud)
"""

import os
from dotenv import load_dotenv
from typing import Literal, Annotated
from typing_extensions import TypedDict

# Load environment variables from .env file
load_dotenv()

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import our custom components
from src.schemas import ResearchState
from src.middleware import get_dynamic_system_prompt, format_tool_error
from src.tools import web_search, scrape_webpage
from src.utils import ConversationMemory


class AgentConfig:
    """Configuration for the ResearchPro Agent."""
    
    def __init__(
        self,
        model_name: str = "gpt-oss:120b-cloud",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.3,
        user_level: Literal["expert", "beginner", "general"] = "general",
        save_conversations: bool = True,
        storage_dir: str = "conversations"
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.user_level = user_level
        self.save_conversations = save_conversations
        self.storage_dir = storage_dir


class ResearchProAgent:
    """
    Main ResearchPro Agent class.
    
    This agent uses a ReAct (Reasoning + Acting) pattern to conduct research.
    It can search the web and scrape pages to gather information.
    """
    
    def __init__(self, config: AgentConfig = None):
        """Initialize the ResearchPro Agent."""
        self.config = config or AgentConfig()
        
        # Initialize conversation memory
        self.memory = ConversationMemory(self.config.storage_dir) if self.config.save_conversations else None
        self.active_conversation_id = None  # Track current conversation session
        self.context_messages = []  # Store loaded conversation context
        
        # Initialize local Ollama LLM
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
        # Initialize state with context messages if available
        initial_messages = self.context_messages.copy() if self.context_messages else []
        initial_messages.append(HumanMessage(content=query))
        
        initial_state = {
            "messages": initial_messages,
            "citations": [],
            "progress": 0
        }
        
        # Run the graph
        try:
            final_state = self.graph.invoke(
                initial_state,
                config={"recursion_limit": max_iterations}
            )
            
            # Save conversation to memory
            if self.memory:
                answer = self.get_final_answer(final_state)
                conversation_id = self.memory.save_conversation(
                    query=query,
                    answer=answer,
                    messages=final_state["messages"],
                    citations=final_state.get("citations", []),
                    metadata={
                        "model": self.config.model_name,
                        "temperature": self.config.temperature,
                        "user_level": self.config.user_level
                    },
                    conversation_id=self.active_conversation_id  # Append to active session
                )
                # Update active conversation ID
                self.active_conversation_id = conversation_id
                final_state["conversation_id"] = conversation_id
            
            # Update context messages for next query in conversation
            self.context_messages = final_state["messages"].copy()
            
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
        # Initialize state with context messages if available
        initial_messages = self.context_messages.copy() if self.context_messages else []
        initial_messages.append(HumanMessage(content=query))
        
        initial_state = {
            "messages": initial_messages,
            "citations": [],
            "progress": 0
        }
        
        final_state = None
        for state in self.graph.stream(initial_state):
            final_state = state
            yield state
        
        # Save conversation after streaming completes
        if self.memory and final_state:
            # Get the actual state from the last node update
            last_node_state = list(final_state.values())[0] if final_state else None
            if last_node_state:
                answer = self.get_final_answer(last_node_state)
                conversation_id = self.memory.save_conversation(
                    query=query,
                    answer=answer,
                    messages=last_node_state["messages"],
                    citations=last_node_state.get("citations", []),
                    metadata={
                        "model": self.config.model_name,
                        "temperature": self.config.temperature,
                        "user_level": self.config.user_level
                    },
                    conversation_id=self.active_conversation_id  # Append to active session
                )
                # Update active conversation ID and context
                self.active_conversation_id = conversation_id
                self.context_messages = last_node_state["messages"].copy()
    
    def get_conversation_history(self, limit: int = 50) -> list:
        """Get list of saved conversations."""
        if not self.memory:
            return []
        return self.memory.list_conversations(limit)
    
    def load_conversation(self, conversation_id: str) -> dict:
        """Load a specific conversation by ID."""
        if not self.memory:
            return None
        return self.memory.load_conversation(conversation_id)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation by ID."""
        if not self.memory:
            return False
        return self.memory.delete_conversation(conversation_id)
    
    def new_chat(self) -> None:
        """Start a new conversation session. Next queries will create a new conversation file."""
        self.active_conversation_id = None
        self.context_messages = []  # Clear conversation context
    
    def load_chat(self, conversation_id: str) -> bool:
        """Load a previous conversation and continue from it.
        
        Args:
            conversation_id: The conversation ID to load
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.memory:
            return False
        
        conv = self.memory.load_conversation(conversation_id)
        if conv:
            self.active_conversation_id = conversation_id
            # Load messages from saved conversation
            if "messages" in conv and conv["messages"]:
                # Reconstruct message objects from serialized data
                self.context_messages = self._deserialize_messages(conv["messages"])
            else:
                self.context_messages = []
            return True
        return False
    
    def _deserialize_messages(self, serialized_messages: list) -> list:
        """Reconstruct message objects from serialized data."""
        messages = []
        for msg in serialized_messages:
            if isinstance(msg, dict):
                msg_type = msg.get("type", "")
                content = msg.get("content", "")
                
                if msg_type == "SystemMessage":
                    messages.append(SystemMessage(content=content))
                elif msg_type == "HumanMessage":
                    messages.append(HumanMessage(content=content))
                elif msg_type == "AIMessage":
                    messages.append(AIMessage(content=content))
                # Skip ToolMessage as they are not needed for context
        return messages
    
    def get_active_conversation_id(self) -> str:
        """Get the current active conversation ID."""
        return self.active_conversation_id


# Convenience function for quick usage
def create_agent(
    model_name: str = "gpt-oss:120b-cloud",
    temperature: float = 0.3,
    user_level: str = "general"
) -> ResearchProAgent:
    """
    Create a ResearchPro Agent with custom configuration.
    
    Args:
        model_name: Ollama model to use (default: gpt-oss:120b-cloud)
        temperature: LLM temperature (0.0-1.0)
        user_level: User expertise level ("expert", "beginner", "general")
    
    Returns:
        Configured ResearchProAgent instance
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
