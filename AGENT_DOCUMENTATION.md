# ResearchPro Agent - Complete Documentation

##  Table of Contents
1. [Project Overview](#project-overview)
2. [Agent Architecture](#agent-architecture)
3. [Core Components](#core-components)
4. [Conversation Memory System](#conversation-memory-system)
5. [Technical Implementation](#technical-implementation)
6. [Usage Guide](#usage-guide)
7. [API Reference](#api-reference)
8. [Teaching Points](#teaching-points)

---

##  Project Overview

### Agent Name: **ResearchPro Agent**

### Problem Statement
Modern research and information gathering requires:
- **Real-time web information** for current events and data
- **Context-aware conversations** across multiple queries
- **Persistent conversation history** for continuity
- **Clean, readable output** for terminal interfaces
- **Session management** for organized research

### Solution
An intelligent conversational agent built with LangChain and Ollama that:
- Conducts web research with DuckDuckGo integration
- Maintains conversation context across sessions
- Automatically saves and organizes chat history
- Provides clean, terminal-friendly formatted responses
- Supports loading and continuing previous conversations

### Real-World Applications
1. **Comparative Research**: Product comparisons (cars, tech, services)
2. **Decision Support**: Gathering information for purchase decisions
3. **Learning Assistant**: Explaining complex topics with follow-up questions
4. **Current Events**: Research on recent news and developments
5. **Technical Research**: Understanding technologies, frameworks, tools

---

##  Agent Architecture

### High-Level Architecture

```

                     USER INPUT                               
         "Compare Honda Civic and Toyota Corolla"             

                   
                   

                  RESEARCHPRO AGENT                           
    
           AGENT STATE (Context Management)                
     Conversation messages (context)                      
     Active conversation ID                               
     Progress tracking                                    
     Citations accumulation                               
    
                                                              
    
           OLLAMA LLM (gpt-oss:120b-cloud)                
     Local inference (no API keys)                        
     Tool binding for structured calls                    
     Temperature control (0.3 default)                    
     Context window management                            
    
                                                              
    
                    TOOL SUITE (2 Tools)                   
                              
     web_search             scrape_                   
     (DuckDuck              webpage                   
       Go)                  (BeautifulS               
                 oup)                     
                                            
    
                                                              
    
             CONVERSATION MEMORY                           
     Automatic conversation saving                        
     Session-based file organization                      
     Context loading for continuity                       
     Meaningful naming from queries                       
    
                                                              
    
                    MIDDLEWARE                             
     Dynamic system prompts                               
     Error handling & formatting                          
     Terminal-friendly output formatting                  
    

                   
                   

                   OUTPUT                                     
   Clean, terminal-friendly text                             
   Structured comparisons and analysis                       
   Source citations when available                           
   Conversation saved to JSON                                

```

### ReAct Loop (Reasoning + Acting)

```
START
  
  

   USER QUERY         "Compare Honda and Toyota"

       
       

  AGENT REASONING     Should I search the web for current info?
  (LLM with tools)     YES, need recent pricing/specs

       
       

  TOOL EXECUTION      web_search("Honda Civic vs Toyota Corolla 2024")
  (web_search)         Returns: search results with links

       
       

  AGENT REASONING     "STOP. I have the info. Generate final answer."
  (LLM without tools)  Synthesizes comprehensive comparison

       
       

  FINAL ANSWER        Clean, formatted comparison
  (Save to memory)     Conversation saved to JSON

       
       
      END
```

**Key Features:**
- **One-shot tool use**: Agent calls tool once, then generates answer
- **Explicit stop instruction**: Forces final answer after tool results
- **Context preservation**: Full conversation stored for reload
- **Smart iteration control**: Max 2 iterations (1 tool call + 1 answer)

---

##  Core Components

### 1. **State Management** (src/schemas/state.py)

```python
class ResearchState(TypedDict):
    ""State schema for the agent with message accumulation.""
    messages: Annotated[List, add]      # Messages accumulate across nodes
    citations: Annotated[List[Dict], add]  # Citations accumulate
    progress: int                        # Iteration counter
```

**Key Concepts:**
- Annotated[List, add]: Messages append, not replace
- progress: Prevents infinite loops (max 2 iterations)
- TypedDict: Type-safe state definition

### 2. **Tools** (src/tools/)

#### Tool 1: Web Search (search.py)
```python
@tool
def web_search(query: str) -> str:
    ""Search the web using DuckDuckGo for current information.""
    # Fetches DuckDuckGo HTML results
    # Parses with BeautifulSoup
    # Returns JSON with title, link, snippet
```

**Use Cases:**
- Current events and news
- Product pricing and specs
- Recent developments
- Statistical data

#### Tool 2: Web Scraper (scraper.py)
```python
@tool
def scrape_webpage(url: str) -> str:
    ""Extract main content from a specific URL.""
    # Fetches webpage content
    # Extracts text with BeautifulSoup
    # Returns cleaned text content
```

**Use Cases:**
- Detailed article analysis
- Specific URL content extraction
- Documentation reading

### 3. **Middleware** (src/middleware/helpers.py)

#### Dynamic System Prompts
```python
def get_dynamic_system_prompt(user_level: str = "general") -> str:
    ""Generate context-aware system prompt.""
    # Instructs LLM to:
    # - Use built-in knowledge first
    # - Call web_search only when needed
    # - Provide terminal-friendly formatting
    # - Stop after one tool call
```

**Output Format Instructions:**
- NO markdown tables (|, --, etc.)
- NO asterisks for bold (**text**)
- Use UPPERCASE for emphasis
- Clear indentation and spacing
- Numbered sections with bullets

#### Error Handling
```python
def format_tool_error(error: Exception, tool_name: str) -> str:
    ""Format user-friendly error messages.""
    # Handles timeouts, not found, permissions
    # Returns helpful suggestions
```

### 4. **Conversation Memory** (src/utils/memory.py)

#### ConversationMemory Class
```python
class ConversationMemory:
    ""Manages conversation history storage.""
    
    def save_conversation(
        query: str,
        answer: str,
        messages: List,
        conversation_id: str = None,  # Append if provided
        conversation_name: str = None  # Auto-generate if None
    ) -> str:
        ""Save or append to conversation.""
```

**Storage Format (JSON):**
```json
{
  "id": "20260108_220710",
  "name": "compare honda and toyota reliability",
  "created_at": "2026-01-08T22:07:10.123456",
  "last_updated": "2026-01-08T22:07:29.456789",
  "exchanges": [
    {
      "query": "compare honda and toyota reliability",
      "answer": "COMPARISON: HONDA VS TOYOTA...",
      "timestamp": "2026-01-08T22:07:10.123456"
    },
    {
      "query": "which one is better for families",
      "answer": "FAMILY COMPARISON...",
      "timestamp": "2026-01-08T22:07:20.234567"
    }
  ],
  "messages": [
    {"type": "SystemMessage", "content": "You are ResearchPro..."},
    {"type": "HumanMessage", "content": "compare honda..."},
    {"type": "AIMessage", "content": "COMPARISON..."}
  ],
  "citations": [],
  "metadata": {
    "model": "gpt-oss:120b-cloud",
    "temperature": 0.3,
    "user_level": "general"
  }
}
```

**Features:**
- **Auto-naming**: Generates clean names from first query
- **Multi-turn storage**: All exchanges in one file
- **Context preservation**: Full message history saved
- **Metadata tracking**: Model, settings, timestamps

---

##  Conversation Memory System

### Architecture

```

                    USER WORKFLOW                         

                                                      
      New Query                                        Load Previous
                                                      
                                                      
                         
  Active Session                             Load Context   
  (memory buffer)                            from JSON      
                         
                                                  
      context_messages[]                           Deserialize
                                                   messages
                                                  

              AGENT PROCESSING                            
  - Prepends context_messages to new query                
  - Runs agent graph with full history                    
  - Generates contextually aware response                 

     
      After completion
     

          SAVE TO DISK (conversations/*.json)             
  IF active_conversation_id:                              
     Append exchange to existing file                    
  ELSE:                                                   
     Create new conversation file                        
  Update context_messages for next query                  

```

### Session Management

#### Starting a New Conversation
```python
agent = create_agent()
result1 = agent.research("What is Python?")
# Creates: 20260108_143000.json (new file)

result2 = agent.research("What about Java?")
# Appends to: 20260108_143000.json (same file)
```

#### Starting Fresh Session
```python
agent.new_chat()  # Clears active_conversation_id & context_messages
result3 = agent.research("What is JavaScript?")
# Creates: 20260108_143500.json (new file)
```

#### Loading Previous Conversation
```python
# List conversations
history = agent.get_conversation_history()
# [{'id': '20260108_143000', 'name': 'What is Python', 'total_exchanges': 2}, ...]

# Load by ID or number
agent.load_chat('20260108_143000')  # OR
agent.load_chat(history[0]['id'])

# Next query has full context!
result4 = agent.research("Compare them")
# Agent knows "them" = Python and Java
```

### Context Loading Mechanism

```python
def load_chat(conversation_id: str) -> bool:
    ""Load conversation and restore context.""
    conv = memory.load_conversation(conversation_id)
    
    # Deserialize saved messages into Message objects
    self.context_messages = self._deserialize_messages(conv['messages'])
    # [SystemMessage(...), HumanMessage(...), AIMessage(...), ...]
    
    # Set active ID for appending future queries
    self.active_conversation_id = conversation_id
    return True

def _deserialize_messages(serialized: list) -> list:
    ""Reconstruct Message objects from JSON.""
    messages = []
    for msg in serialized:
        if msg['type'] == 'SystemMessage':
            messages.append(SystemMessage(content=msg['content']))
        elif msg['type'] == 'HumanMessage':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['type'] == 'AIMessage':
            messages.append(AIMessage(content=msg['content']))
        # Skip ToolMessage (not needed for context)
    return messages
```

**Why This Works:**
- LangGraph nodes receive full message history
- LLM sees complete conversation context
- Follow-up questions make sense without repetition
- Agent "remembers" previous exchanges

---

##  Technical Implementation

### Agent Graph (LangGraph)

```python
workflow = StateGraph(ResearchState)

# Node 1: Agent Reasoning
def agent_node(state: ResearchState) -> dict:
    ""Main reasoning node.""
    messages = state["messages"]
    iteration_count = state.get("progress", 0)
    
    # Add system prompt if first message
    if not isinstance(messages[0], SystemMessage):
        system_prompt = get_dynamic_system_prompt()
        messages = [SystemMessage(content=system_prompt)] + messages
    
    # After first tool call, force final answer
    if iteration_count >= 1:
        has_tool_results = any(m.__class__.__name__ == 'ToolMessage' for m in messages)
        if has_tool_results:
            # Add explicit stop instruction
            force_msg = HumanMessage(content="STOP. Write final answer. NO more tools.")
            messages = messages + [force_msg]
            
            # Invoke WITHOUT tool binding
            response = self.llm.invoke(messages)
            return {"messages": [response], "progress": iteration_count + 1}
    
    # First iteration - allow tool use
    response = self.llm_with_tools.invoke(messages)
    return {"messages": [response], "progress": iteration_count + 1}

# Node 2: Tool Execution
tool_node = ToolNode([web_search, scrape_webpage])

# Routing Logic
def should_continue(state: ResearchState) -> Literal["continue", "end"]:
    ""Route to tools or end.""
    last_message = state["messages"][-1]
    iteration_count = state.get("progress", 0)
    
    if iteration_count >= 2:  # Max 2 iterations
        return "end"
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"

# Build graph
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {
    "continue": "tools",
    "end": END
})
workflow.add_edge("tools", "agent")
graph = workflow.compile()
```

### Execution Flow

**Example Query: "Compare Honda Civic and Toyota Corolla"**

```
ITERATION 1 (progress=0):
  agent_node:
    - Adds SystemMessage with instructions
    - Invokes llm_with_tools
    - LLM returns: AIMessage with tool_call(web_search, "Honda Civic vs Toyota...")
    - Returns: {"messages": [AIMessage(tool_calls=[...])], "progress": 1}
  
  should_continue: Sees tool_calls  returns "continue"
  
  tools:
    - Executes web_search
    - Returns: ToolMessage with search results
    - State now has: [SystemMessage, HumanMessage, AIMessage(tool_calls), ToolMessage]

ITERATION 2 (progress=1):
  agent_node:
    - Detects iteration_count >= 1
    - Sees ToolMessage in history
    - Adds HumanMessage("STOP. Write final answer...")
    - Invokes llm WITHOUT tools
    - LLM returns: AIMessage with comprehensive comparison
    - Returns: {"messages": [AIMessage(final_answer)], "progress": 2}
  
  should_continue: iteration_count >= 2  returns "end"

SAVE TO MEMORY:
  - Extract final answer from last AIMessage
  - Save to conversations/20260108_143000.json
  - Update context_messages for next query
```

---

##  Usage Guide

### Basic Usage

```python
from agent import create_agent

# Create agent
agent = create_agent()

# Simple query
result = agent.research("What is machine learning?")
answer = agent.get_final_answer(result)
print(answer)

# Conversation ID for reference
print(f"Saved as: {result['conversation_id']}")
```

### Multi-Turn Conversations

```python
agent = create_agent()

# First query
result1 = agent.research("Compare iPhone 15 and Samsung S24")
conv_id = result1['conversation_id']

# Follow-up in same conversation
result2 = agent.research("Which has better camera?")
# Same conversation ID, agent has context

result3 = agent.research("What about battery life?")
# Still same conversation, 3 exchanges total
```

### Session Management

```python
agent = create_agent()

# Session 1
agent.research("What is Python?")
agent.research("What is Java?")

# Start new session
agent.new_chat()
agent.research("What is JavaScript?")  # New conversation file

# List all conversations
for conv in agent.get_conversation_history():
    print(f"{conv['name']} - {conv['total_exchanges']} exchanges")
```

### Loading Previous Conversations

```python
agent = create_agent()

# List conversations
history = agent.get_conversation_history()
print("Saved conversations:")
for i, conv in enumerate(history, 1):
    print(f"{i}. {conv['name']} ({conv['total_exchanges']} exchanges)")

# Load by number or ID
agent.load_chat(history[0]['id'])

# Continue conversation
agent.research("Tell me more")  # Has full context!
```

### Interactive Mode

```bash
python examples/interactive_demo.py

# Commands:
# - Type questions naturally
# - "list"  View all saved conversations
# - "load 1"  Continue conversation #1
# - "new"  Start fresh conversation
# - "quit"  Exit
```

---

##  API Reference

### Agent Creation

```python
create_agent(
    model_name: str = "gpt-oss:120b-cloud",
    temperature: float = 0.3,
    user_level: str = "general"  # "expert", "beginner", "general"
) -> ResearchProAgent
```

### Research Methods

```python
# Blocking research
agent.research(
    query: str,
    max_iterations: int = 10
) -> dict  # Returns: {messages, citations, progress, conversation_id}

# Streaming research
agent.stream_research(query: str) -> Generator
# Yields: {node_name: state} for each step

# Extract answer
agent.get_final_answer(state: dict) -> str
```

### Conversation Management

```python
# Session control
agent.new_chat() -> None                    # Start new conversation
agent.load_chat(conversation_id: str) -> bool  # Load previous conversation
agent.get_active_conversation_id() -> str   # Get current conversation ID

# History access
agent.get_conversation_history(limit: int = 50) -> List[dict]
# Returns: [{'id', 'name', 'timestamp', 'last_updated', 'first_query', 'total_exchanges'}, ...]

agent.load_conversation(conversation_id: str) -> dict
# Returns: Full conversation data with exchanges, messages, metadata

agent.delete_conversation(conversation_id: str) -> bool
```

### Configuration

```python
from agent import AgentConfig, ResearchProAgent

config = AgentConfig(
    model_name="gpt-oss:120b-cloud",
    base_url="http://localhost:11434",
    temperature=0.3,
    user_level="general",
    save_conversations=True,
    storage_dir="conversations"
)

agent = ResearchProAgent(config)
```

---

##  Teaching Points

### 1. **LangChain Fundamentals**

#### StateGraph Pattern
```python
from langgraph.graph import StateGraph, END

# Define state schema
class ResearchState(TypedDict):
    messages: Annotated[List, add]
    progress: int

# Create graph
workflow = StateGraph(ResearchState)
workflow.add_node("agent", agent_function)
workflow.add_node("tools", tool_function)
workflow.set_entry_point("agent")
```

**Key Concepts:**
- **State accumulation**: Annotated[List, add] appends, doesn't replace
- **Nodes**: Functions that receive state, return updates
- **Edges**: Define flow between nodes
- **Compilation**: graph = workflow.compile()

#### Tool Calling
```python
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    ""Search the web for information.""
    # Implementation
    return results

# Bind tools to LLM
llm_with_tools = llm.bind_tools([web_search])

# LLM can now generate tool_calls
response = llm_with_tools.invoke(messages)
# response.tool_calls = [{'name': 'web_search', 'args': {'query': '...'}}]
```

### 2. **Message Management**

#### Message Types
- SystemMessage: Instructions for LLM behavior
- HumanMessage: User input
- AIMessage: LLM responses (may contain tool_calls)
- ToolMessage: Tool execution results

#### Accumulation Pattern
```python
# WRONG - Replaces all messages
return {"messages": [new_message]}  # State has only 1 message

# RIGHT - Appends to existing messages
return {"messages": [new_message]}  # With Annotated[List, add], appends!
```

### 3. **Conversation Persistence**

#### Why JSON?
- Human-readable
- Easy to edit/inspect
- Standard Python serialization
- Supports nested structures

#### Session vs File
- **Session**: Active conversation in memory
- **File**: Persistent storage on disk
- **Loading**: Deserializes file into session context

### 4. **Context Management**

#### Context Window
```python
# Too much context = slow + expensive
# Too little = no memory

# Solution: Smart context loading
self.context_messages = deserialize(saved_messages)
# Only include relevant history
```

#### Context Awareness
```python
# Without context:
User: "Compare Honda and Toyota"
Agent: [provides comparison]
User: "Which is better?"
Agent: "Better for what? Please specify what you're comparing."

# With context:
User: "Compare Honda and Toyota"
Agent: [provides comparison]
User: "Which is better?"
Agent: "Based on the comparison, Toyota has better reliability..."
```

### 5. **Error Handling**

```python
try:
    result = agent.research(query)
except Exception as e:
    error_msg = format_tool_error(e, "agent")
    return {"messages": [AIMessage(content=f"Error: {error_msg}")]}
```

**Best Practices:**
- Catch specific exceptions
- Provide user-friendly messages
- Log detailed errors for debugging
- Offer recovery suggestions

### 6. **Terminal Formatting**

**Problem**: Markdown doesn't render well in terminals
```
**Bold text** renders as **Bold text** (not bold!)
| Tables | Look | Messy |
```

**Solution**: Plain text with structure
```
COMPARISON: HONDA VS TOYOTA

1. Reliability
   Honda: 73/100 score
   Toyota: 84/100 score

2. Price
   Honda Civic: $24,000
   Toyota Corolla: $22,000
```

---

##  Advanced Topics

### Custom Tool Development

```python
from langchain_core.tools import tool
import requests

@tool
def custom_api_call(endpoint: str, params: dict) -> str:
    ""Call a custom API endpoint.""
    response = requests.get(endpoint, params=params)
    return response.json()

# Add to agent
agent.tools.append(custom_api_call)
agent.llm_with_tools = agent.llm.bind_tools(agent.tools)
```

### Streaming Implementation

```python
for state_update in agent.stream_research(query):
    node_name = list(state_update.keys())[0]
    state = state_update[node_name]
    
    if node_name == "agent":
        print(" Agent thinking...")
    elif node_name == "tools":
        print(" Executing tools...")
```

### Conversation Export

```python
def export_to_pdf(conversation_id: str):
    ""Export conversation to PDF.""
    conv = agent.load_conversation(conversation_id)
    
    # Use reportlab or fpdf
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, conv['name'], ln=True)
    
    for exchange in conv['exchanges']:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Q: {exchange['query']}", ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, exchange['answer'])
    
    pdf.output(f"{conversation_id}.pdf")
```

---

##  Troubleshooting

### Common Issues

#### 1. Empty Responses
**Symptom**: Agent returns empty or incomplete answers

**Causes:**
- Model not generating final answer
- Tool results not reaching agent
- Iteration limit hit too early

**Solution:**
```python
# Check iteration count
if iteration_count >= 1:
    # Force final answer explicitly
    force_msg = HumanMessage(content="STOP. Generate final answer NOW.")
```

#### 2. Lost Context
**Symptom**: Agent doesn't remember previous queries

**Causes:**
- Forgot to load conversation
- Context messages not restored
- New chat called accidentally

**Solution:**
```python
# Always check active conversation
print(f"Active: {agent.get_active_conversation_id()}")

# Ensure context loaded
if agent.load_chat(conv_id):
    print(f"Context messages: {len(agent.context_messages)}")
```

#### 3. Tool Not Called
**Symptom**: Agent answers from knowledge, doesn't search

**Causes:**
- System prompt too restrictive
- Temperature too low
- Query doesn't indicate need for search

**Solution:**
```python
# Explicit search request
result = agent.research("Search the web for: latest AI trends 2026")

# Or adjust temperature
agent = create_agent(temperature=0.5)  # More creative
```

---

##  Performance Considerations

### Model Selection
- **gpt-oss:120b-cloud**: Large, accurate, slower (120B parameters)
- **llama2**: Medium, fast, good for general use
- **mistral**: Fast, efficient, good for focused tasks

### Context Window
- Longer context = Better understanding
- Longer context = Slower inference
- Trade-off: Keep ~10-20 messages for balance

### Storage
- JSON files grow with exchanges
- Consider archiving old conversations
- Implement cleanup for very large histories

### Caching
```python
# Future enhancement: Cache common queries
cache = {}
if query in cache:
    return cache[query]
else:
    result = agent.research(query)
    cache[query] = result
```

---

##  Best Practices

### 1. System Prompt Design
```python
# BAD: Too vague
"You are a helpful assistant."

# GOOD: Specific instructions
"You are ResearchPro. Use built-in knowledge first.
Call web_search only for current info. Format output
with clean indentation. Stop after one tool call."
```

### 2. Conversation Naming
```python
# BAD: Generic
conversation_name = "Chat"

# GOOD: Descriptive
conversation_name = generate_name_from_query(first_query)
#  "compare honda civic and toyota corolla"
```

### 3. Error Messages
```python
# BAD: Technical
"ToolException: HTTP 500 at line 42"

# GOOD: User-friendly
"The web search tool encountered an issue. 
Please try again or rephrase your query."
```

### 4. Context Management
```python
# Clear context when appropriate
if user_says_new_topic:
    agent.new_chat()

# Load context when continuing
if user_says_continue:
    agent.load_chat(last_conversation_id)
```

---

##  Conclusion

The ResearchPro Agent demonstrates:

 **Modern agent architecture** with LangGraph
 **Conversation persistence** with JSON storage
 **Context awareness** across sessions
 **Clean formatting** for terminal interfaces
 **Local LLM integration** with Ollama
 **Production-ready** error handling
 **Educational value** for learning LangChain

### Next Steps

1. **Add more tools**: Custom APIs, databases, file operations
2. **Implement caching**: Speed up repeated queries
3. **Build UI**: Streamlit/Gradio web interface
4. **Export features**: PDF reports, summaries
5. **Analytics**: Track tool usage, response times
6. **Multi-modal**: Add image analysis, document understanding

---

**Happy Building! **

For questions or contributions, see the main README.md file.
