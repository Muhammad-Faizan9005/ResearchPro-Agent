"""
Example 1: Basic Research Query
Demonstrates simple agent usage with a straightforward question.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import create_agent


def main():
    print("=" * 60)
    print("ResearchPro Agent - Basic Research Example")
    print("=" * 60)
    print()
    
    # Create the agent
    print("🔧 Initializing agent...")
    agent = create_agent(temperature=0.3, user_level="general")
    print("✅ Agent ready!")
    print()
    
    # Research query
    query = "What are the main health benefits of regular exercise?"
    print(f"📝 Research Query: {query}")
    print()
    print("🔍 Conducting research...")
    print("-" * 60)
    print()
    
    # Run research
    result = agent.research(query, max_iterations=15)
    
    # Display results
    print()
    print("=" * 60)
    print("📊 RESEARCH RESULTS")
    print("=" * 60)
    print()
    
    answer = agent.get_final_answer(result)
    print(answer)
    print()
    
    # Display citations if available
    citations = result.get("citations", [])
    if citations:
        print()
        print("=" * 60)
        print("📚 CITATIONS")
        print("=" * 60)
        for i, citation in enumerate(citations, 1):
            print(f"{i}. {citation}")
    
    # Display message count
    messages = result.get("messages", [])
    print()
    print("=" * 60)
    print(f"💬 Total messages exchanged: {len(messages)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
