# ResearchPro Agent 🔬

An intelligent research assistant powered by **LangChain** and **Ollama** with advanced conversation memory, context-aware responses, and terminal-friendly formatting. Perfect for research, comparisons, and interactive AI conversations.

## 🌟 Features

### **Core Capabilities**
- **Web Search**: Real-time web research using DuckDuckGo
- **Web Scraper**: Extract and analyze webpage content
- **Conversation Memory**: Automatic saving and loading of chat history
- **Context Awareness**: Maintains conversation context across sessions
- **Smart Formatting**: Clean, terminal-friendly output (no messy markdown)
- **Session Management**: Continue previous conversations seamlessly

### **Advanced LangChain Concepts**
- ✅ **ReAct Pattern** (Reasoning + Acting loop)
- ✅ **Tool Calling** with intelligent tool selection
- ✅ **State Management** with TypedDict and message accumulation
- ✅ **Conversation Persistence** with JSON-based storage
- ✅ **Context Loading** for conversation continuity
- ✅ **Streaming** for real-time results
- ✅ **Local LLM** (Ollama gpt-oss:120b-cloud - no API keys needed!)

## 📋 Prerequisites

1. **Ollama** installed on your system
   - Download from: https://ollama.ai
   - Pull the model: `ollama pull gpt-oss:120b-cloud`

2. **Python 3.10+**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env` and customize if needed:

```bash
cp .env.example .env
```

Default configuration works with standard Ollama installation.

### 3. Start Ollama

Make sure Ollama is running:

```bash
# On most systems, Ollama runs automatically after installation
# You can verify by running:
ollama list
```

### 4. Run Interactive Demo

```bash
python examples/interactive_demo.py
```

**Interactive Commands:**
- Type your questions naturally
- `new` - Start a new conversation
- `list` - View all saved conversations
- `load <number>` - Continue a previous conversation (e.g., `load 1`)
- `quit` - Exit the application

## 💻 Usage

### Simple Usage

```python
from agent import create_agent

# Create agent
agent = create_agent(temperature=0.3, user_level="general")

# Ask a question
result = agent.research("What are the benefits of renewable energy?")

# Get answer
answer = agent.get_final_answer(result)
print(answer)

# Conversation is automatically saved!
conv_id = result.get('conversation_id')
print(f"Saved to: {conv_id}")
```

### Continue Previous Conversations

```python
from agent import create_agent

agent = create_agent()

# List all saved conversations
history = agent.get_conversation_history()
for conv in history:
    print(f"{conv['id']}: {conv['name']} ({conv['total_exchanges']} exchanges)")

# Load and continue a conversation
agent.load_chat(history[0]['id'])
result = agent.research("Tell me more about that")  # Has context!
```

### Advanced Usage with Streaming

```python
from agent import create_agent

agent = create_agent()

# Stream results in real-time
for state_update in agent.stream_research("Compare Honda and Toyota"):
    node = list(state_update.keys())[0]
    print(f"Step: {node}")
```

### Session Management

```python
from agent import create_agent

agent = create_agent()

# First conversation
agent.research("What is Python?")
agent.research("What about Java?")  # Same conversation file

# Start new conversation
agent.new_chat()
agent.research("What is machine learning?")  # New conversation file

# Load previous conversation
agent.load_chat(conv_id)
agent.research("Compare them")  # Has context of first conversation!
```

### Custom Configuration

```python
from agent import AgentConfig, ResearchProAgent

config = AgentConfig(
    model_name="gpt-oss:120b-cloud",
    base_url="http://localhost:11434",
    temperature=0.5,
    user_level="expert",  # Options: "expert", "beginner", "general"
    save_conversations=True,
    storage_dir="conversations"
)

agent = ResearchProAgent(config)
```

## 🏗️ Project Structure

```
langchain/
├── agent.py                      # Main agent implementation
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
│
├── src/
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── state.py             # State management with TypedDict
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py            # Web search (DuckDuckGo)
│   │   └── scraper.py           # Web scraping (BeautifulSoup)
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── helpers.py           # System prompts, error handling
│   │
│   └── utils/
│       ├── __init__.py
│       └── memory.py            # Conversation memory management
│
├── examples/
│   └── interactive_demo.py      # Interactive CLI demo
│
└── conversations/               # Auto-saved conversation history (JSON)
```

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `web_search` | Search the web using DuckDuckGo for current information |
| `scrape_webpage` | Extract and analyze content from specific URLs |

## 💾 Conversation Memory

All conversations are automatically saved to `conversations/` directory:

```json
{
  "id": "20260108_220710",
  "name": "compare honda and toyota reliability",
  "created_at": "2026-01-08T22:07:10",
  "last_updated": "2026-01-08T22:07:29",
  "exchanges": [
    {"query": "compare honda and toyota reliability", "answer": "...", "timestamp": "..."},
    {"query": "which one is better for families", "answer": "...", "timestamp": "..."},
    {"query": "what about fuel efficiency", "answer": "...", "timestamp": "..."}
  ],
  "messages": [...],
  "citations": [],
  "metadata": {"model": "gpt-oss:120b-cloud", "temperature": 0.3}
}
```

### Conversation Features:
- ✅ **Automatic naming** from first query
- ✅ **Multi-turn conversations** in single file
- ✅ **Context preservation** across sessions
- ✅ **Easy loading** by number or ID
- ✅ **Full message history** for analysis

## 📚 Key Features Explained

### 1. **Conversation Memory System**
- Every research session is automatically saved
- Conversations grouped by chat session (not individual queries)
- Meaningful names auto-generated from first query
- Load previous conversations to continue where you left off

### 2. **Context-Aware Responses**
- Agent remembers previous exchanges in loaded conversations
- Can answer follow-up questions without repeating information
- Maintains full conversation history across multiple queries
- Smart context management (clears on `new_chat()`)

### 3. **Terminal-Friendly Formatting**
- Clean, readable output optimized for terminal display
- No messy markdown tables or symbols
- Proper indentation and spacing
- UPPERCASE for emphasis instead of bold markers

### 4. **Smart Session Management**
- Continue conversations: All queries in same session → one file
- Start fresh: `new_chat()` creates new conversation file
- Easy navigation: List and load conversations by number

## 🎓 Learning Objectives

After studying this project, students will understand:

1. ✅ How to build a **multi-tool agent** using LangChain
2. ✅ **ReAct pattern** implementation (Reasoning + Acting)
3. ✅ **Tool calling** with intelligent tool selection
4. ✅ **State management** in conversational agents
5. ✅ **Conversation persistence** and context loading
6. ✅ **Local LLM integration** with Ollama
7. ✅ **Streaming** for real-time agent responses
8. ✅ **Error handling** and middleware patterns
9. ✅ **Session management** for multi-turn conversations
10. ✅ **JSON-based storage** for conversation history

## 🔧 Troubleshooting

### Ollama Connection Issues

**Problem**: `Could not connect to Ollama`

**Solution**:
```bash
# Check if Ollama is running
ollama list

# If not running, start it (varies by OS)
# On macOS/Linux:
ollama serve

# On Windows: Ollama Desktop app should be running
```

### Model Not Found

**Problem**: `Model gpt-oss:120b-cloud not found`

**Solution**:
```bash
# Pull the model
ollama pull gpt-oss:120b-cloud

# Verify it's installed
ollama list
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'langchain'`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Conversation Loading Issues

**Problem**: Cannot load previous conversations

**Solution**:
- Use `list` command to see available conversations with numbers
- Use `load <number>` (e.g., `load 1`) to load by list number
- Or use `load <conversation_id>` to load by full ID
- Ensure `conversations/` directory exists and has read permissions

### Empty Responses

**Problem**: Agent returns empty or incomplete answers

**Solution**:
- Check Ollama model is running: `ollama list`
- Increase temperature for more creative responses
- Verify internet connection for web search tool
- Check model has enough resources (RAM/VRAM)

## 🎯 API Reference

### Agent Methods

```python
# Create agent
agent = create_agent(model_name="gpt-oss:120b-cloud", temperature=0.3, user_level="general")

# Research
result = agent.research("query")              # Blocking research
agent.stream_research("query")                # Streaming research

# Conversation management
agent.new_chat()                              # Start new conversation
agent.load_chat(conversation_id)              # Load previous conversation
agent.get_active_conversation_id()            # Get current conversation ID

# History
agent.get_conversation_history(limit=50)      # List saved conversations
agent.load_conversation(conversation_id)      # Load full conversation data
agent.delete_conversation(conversation_id)    # Delete conversation

# Results
agent.get_final_answer(state)                 # Extract answer from state
```

## 📖 Additional Resources

- **LangChain Docs**: https://python.langchain.com/
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Ollama Docs**: https://ollama.ai/docs
- **Ollama Models**: https://ollama.ai/library

## 🤝 Contributing

This is an educational project. Suggestions for improvement are welcome!

## 📄 License

This project is created for educational purposes.

## 🎯 Next Steps

1. **Experiment** with different models: `ollama pull llama2`, `ollama pull mistral`
2. **Add custom tools** for your specific use case
3. **Modify prompts** in `src/middleware/helpers.py` for different output styles
4. **Extend conversation features** - add export to PDF, search conversations, etc.
5. **Build a UI** - Create a web interface using Streamlit or Gradio

## 💡 Example Interactions

### Research Comparison
```
🔍 Your question: compare honda civic and toyota corolla

[Agent searches web, analyzes data]

📄 ANSWER:
COMPARISON: HONDA CIVIC VS TOYOTA COROLLA
1. Overview
   Honda Civic: Sporty, 180hp turbocharged, $24k-$30k
   Toyota Corolla: Reliable, 169hp hybrid available, $22k-$28k
...
```

### Follow-up Questions
```
🔍 Your question: which one has better fuel efficiency?

[Agent remembers context, provides specific comparison]

📄 ANSWER:
FUEL EFFICIENCY COMPARISON
- Corolla Hybrid: 52 mpg combined
- Civic: 36 mpg combined
...
```

### Load Previous Conversations
```
🔍 Your question: list

📚 Saved Conversations:
1. [20260108_220710] compare honda civic and toyota corolla (3 exchanges)
2. [20260108_221831] What is Python (1 exchange)

🔍 Your question: load 1

✅ Loaded conversation: compare honda civic and toyota corolla
   You can now continue this conversation.

🔍 Your question: what about their prices?

[Agent uses context from loaded conversation]
```

---

**Happy Learning! 🚀**

For detailed implementation questions, check the source code in `agent.py` and `src/` directory.
