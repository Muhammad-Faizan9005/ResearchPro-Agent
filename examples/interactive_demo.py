"""
Example 3: Interactive Demo with Streaming
Demonstrates real-time streaming of agent reasoning.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import create_agent


def print_header(text: str):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(text.center(70))
    print("=" * 70)
    print()


def main():
    print_header("🔬 ResearchPro Agent - Interactive Demo")
    
    # Create agent
    print("🔧 Initializing agent with streaming enabled...")
    agent = create_agent(temperature=0.4, user_level="general")
    print("✅ Agent ready!")
    print()
    
    # Interactive loop
    print("Type your research questions (or 'quit' to exit)")
    print("Type 'new' to start a new conversation")
    print("Type 'list' to see previous conversations")
    print("Type 'load <number>' to continue a conversation (e.g., 'load 1')")
    print("-" * 70)
    print()
    
    while True:
        # Get user input
        try:
            query = input("🔍 Your question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break
        
        if not query:
            continue
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if query.lower() in ['new', 'new chat', 'newchat']:
            agent.new_chat()
            print("\n✨ Started new conversation!\n")
            continue
        
        if query.lower() == 'list':
            history = agent.get_conversation_history()
            if not history:
                print("\n📭 No saved conversations yet.\n")
            else:
                print("\n📚 Saved Conversations:")
                print("=" * 70)
                for i, conv in enumerate(history, 1):
                    print(f"{i}. [{conv['id']}]")
                    print(f"   Name: {conv['name']}")
                    print(f"   Exchanges: {conv['total_exchanges']}")
                    print(f"   Last updated: {conv['last_updated'][:19]}")
                    print("-" * 70)
                print()
            continue
        
        if query.lower().startswith('load '):
            conv_identifier = query[5:].strip()
            
            # Check if it's a number (list index) or conversation ID
            conv_id = None
            if conv_identifier.isdigit():
                # User entered a number from the list
                idx = int(conv_identifier) - 1
                history = agent.get_conversation_history()
                if 0 <= idx < len(history):
                    conv_id = history[idx]['id']
                else:
                    print(f"\n❌ Invalid conversation number: {conv_identifier}\n")
                    print(f"   Please use a number between 1 and {len(history)}\n")
                    continue
            else:
                # User entered a conversation ID
                conv_id = conv_identifier
            
            if conv_id and agent.load_chat(conv_id):
                conv = agent.load_conversation(conv_id)
                print(f"\n✅ Loaded conversation: {conv.get('name', conv_id)}")
                print(f"   Total exchanges: {len(conv.get('exchanges', []))}")
                print("   You can now continue this conversation.\n")
            else:
                print(f"\n❌ Could not load conversation: {conv_identifier}\n")
            continue
        
        print()
        print("-" * 70)
        print("🤖 Agent is thinking...")
        print("-" * 70)
        print()
        
        # Stream the research process
        step_count = 0
        final_state = None
        for state_update in agent.stream_research(query):
            step_count += 1
            
            # Extract the node that was just executed
            node_name = list(state_update.keys())[0]
            state = state_update[node_name]
            final_state = state  # Keep track of final state
            
            if node_name == "agent":
                last_msg = state["messages"][-1] if state.get("messages") else None
                if last_msg and hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    print(f"  🔧 Step {step_count}: Calling {len(last_msg.tool_calls)} tool(s)...")
                    for tool_call in last_msg.tool_calls:
                        tool_name = tool_call.get("name", "unknown")
                        print(f"     └─ {tool_name}")
                else:
                    print(f"  💭 Step {step_count}: Generating final answer...")
            
            elif node_name == "tools":
                print(f"  ✅ Step {step_count}: Tools executed")
        
        # Get final answer from the streamed state
        print()
        print("=" * 70)
        print("📄 ANSWER")
        print("=" * 70)
        print()
        
        # Extract answer from final state
        if final_state:
            answer = agent.get_final_answer(final_state)
            print(answer)
        else:
            print("No answer generated.")
        
        print()
        print("=" * 70)
        print()


def run_preset_demo():
    """Run a preset demo with predefined questions."""
    print_header("🎬 ResearchPro Agent - Preset Demo")
    
    agent = create_agent(temperature=0.3, user_level="general")
    
    questions = [
        "What is machine learning?",
        "Calculate the compound growth rate if a company grew from $100M to $250M in 5 years",
        "What are the top 3 benefits of meditation according to research?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}/{len(questions)}: {question}")
        print("-" * 70)
        
        result = agent.research(question, max_iterations=10)
        answer = agent.get_final_answer(result)
        
        print()
        print(answer)
        print()
        print("=" * 70)
        
        if i < len(questions):
            input("\nPress Enter to continue to next question...")


if __name__ == "__main__":
    import sys
    
    # Check if preset mode
    if len(sys.argv) > 1 and sys.argv[1] == "--preset":
        run_preset_demo()
    else:
        main()
