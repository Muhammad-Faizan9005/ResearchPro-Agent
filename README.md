# ResearchPro Agent 🔬

An intelligent research assistant powered by **LangChain** and **Ollama** that demonstrates advanced agent concepts including tool calling, structured output, state management, and local LLM integration.

## 🌟 Features

### **11 Powerful Tools**
- **Web Search**: DuckDuckGo integration for web research
- **Calculator**: Mathematical computations (basic math, percentage changes, CAGR)
- **Web Scraper**: Extract content and links from web pages
- **Document Reader**: Read PDF and text files, list directories
- **Storage**: Persistent storage for research findings
- **Verification**: Fact verification, source credibility checking, citation formatting

### **Advanced LangChain Concepts**
- ✅ **ReAct Pattern** (Reasoning + Acting loop)
- ✅ **Tool Calling** with dynamic tool selection
- ✅ **Structured Output** using Pydantic models
- ✅ **State Management** with TypedDict
- ✅ **Middleware** for message trimming and error handling
- ✅ **Streaming** for real-time results
- ✅ **Local LLM** (Ollama gemma2:2b - no API keys needed!)

## 📋 Prerequisites

1. **Ollama** installed on your system
   - Download from: https://ollama.ai
   - Pull the model: `ollama pull gemma2:2b`

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

### 4. Run Examples

**Basic Research:**
```bash
python examples/basic_research.py
```

**Comparative Research with Calculations:**
```bash
python examples/comparative_research.py
```

**Interactive Demo:**
```bash
python examples/interactive_demo.py
```

**Preset Demo:**
```bash
python examples/interactive_demo.py --preset
```

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
```

### Advanced Usage with Streaming

```python
from agent import create_agent

agent = create_agent()

# Stream results in real-time
for state_update in agent.stream_research("Explain quantum computing"):
    node = list(state_update.keys())[0]
    print(f"Step: {node}")
```

### Custom Configuration

```python
from agent import AgentConfig, ResearchProAgent

config = AgentConfig(
    model_name="gemma2:2b",
    base_url="http://localhost:11434",
    temperature=0.5,
    user_level="expert"  # Options: "expert", "beginner", "general"
)

agent = ResearchProAgent(config)
```

## 🏗️ Project Structure

```
langchain/
├── agent.py                      # Main agent implementation
├── agent1.py                     # Original documentation file
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment configuration template
├── AGENT_DOCUMENTATION.md        # Comprehensive documentation (15 pages)
│
├── src/
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── state.py             # Pydantic models for state & output
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py            # Web search tools
│   │   ├── calculator.py        # Math calculation tools
│   │   ├── scraper.py           # Web scraping tools
│   │   ├── document.py          # Document reading tools
│   │   ├── storage.py           # Persistent storage tools
│   │   └── verification.py      # Fact verification tools
│   │
│   └── middleware/
│       ├── __init__.py
│       └── helpers.py           # Message trimming, error handling
│
├── examples/
│   ├── basic_research.py        # Simple research example
│   ├── comparative_research.py  # Complex multi-tool example
│   └── interactive_demo.py      # Interactive CLI demo
│
├── data/                        # Storage for findings
└── logs/                        # Logs directory
```

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `web_search` | Search the web using DuckDuckGo |
| `web_search_simple` | Quick web search with summary |
| `calculate` | Basic mathematical calculations |
| `percentage_change` | Calculate percentage change |
| `compound_growth_rate` | Calculate CAGR |
| `scrape_webpage` | Extract content from web pages |
| `extract_links` | Extract links from web pages |
| `read_pdf` | Read PDF documents |
| `read_text_file` | Read text files |
| `list_directory` | List files in a directory |
| `store_finding` | Store research findings |
| `retrieve_finding` | Retrieve stored findings |
| `list_all_findings` | List all stored findings |
| `verify_fact` | Verify facts with confidence scoring |
| `check_source_credibility` | Check source reliability |
| `citation_formatter` | Format citations (APA/MLA/Chicago) |

## 📚 Teaching Use Cases

This project is designed for **teaching LangChain concepts** to students:

### **Module 1: Basic Agent Setup**
- Understanding LangGraph and StateGraph
- Creating custom tools with the `@tool` decorator
- Basic agent loop (agent → tools → agent)

### **Module 2: Tool Integration**
- Binding multiple tools to an LLM
- Tool calling and response handling
- Error handling in tools

### **Module 3: State Management**
- TypedDict for state definition
- Tracking conversation history
- Managing agent context

### **Module 4: Advanced Features**
- Structured output with Pydantic
- Middleware for message management
- Streaming results in real-time
- Dynamic system prompts

## 🎓 Learning Objectives

After studying this project, students will understand:

1. ✅ How to build a **multi-tool agent** using LangChain
2. ✅ **ReAct pattern** implementation (Reasoning + Acting)
3. ✅ **Tool calling** with dynamic tool selection
4. ✅ **State management** in conversational agents
5. ✅ **Structured output** using Pydantic models
6. ✅ **Local LLM integration** with Ollama
7. ✅ **Streaming** for real-time agent responses
8. ✅ **Error handling** and middleware patterns

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

**Problem**: `Model gemma2:2b not found`

**Solution**:
```bash
# Pull the model
ollama pull gemma2:2b

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

### Tool Execution Errors

**Problem**: Tools fail with timeout or connection errors

**Solution**:
- Check your internet connection (for web search/scraper)
- Increase timeout in tool configuration
- Check file permissions (for document reading)

## 📖 Additional Resources

- **Full Documentation**: See `AGENT_DOCUMENTATION.md` for 15-page comprehensive guide
- **LangChain Docs**: https://python.langchain.com/
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Ollama Docs**: https://ollama.ai/docs

## 🤝 Contributing

This is an educational project. Suggestions for improvement are welcome!

## 📄 License

This project is created for educational purposes.

## 🎯 Next Steps

1. **Experiment** with different models: `ollama pull llama2`, `ollama pull mistral`
2. **Add custom tools** for your specific use case
3. **Modify prompts** in `middleware/helpers.py` for different behaviors
4. **Extend state** in `schemas/state.py` for additional tracking
5. **Create new examples** showcasing different research scenarios

---

**Happy Learning! 🚀**

For questions or issues, refer to the comprehensive documentation in `AGENT_DOCUMENTATION.md`.
