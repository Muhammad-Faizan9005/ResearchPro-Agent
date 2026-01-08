"""
Example 2: Comparative Research with Calculations
Demonstrates complex research with multiple tools (search + calculator).
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import create_agent


def main():
    print("=" * 70)
    print("ResearchPro Agent - Comparative Research with Calculations")
    print("=" * 70)
    print()
    
    # Create agent
    print("🔧 Initializing agent...")
    agent = create_agent(temperature=0.2, user_level="expert")
    print("✅ Agent ready!")
    print()
    
    # Complex research query requiring multiple tools
    query = """
    Compare the GDP growth rates of India and China over the last 5 years.
    Calculate the compound annual growth rate (CAGR) for each country.
    Which country had stronger economic growth?
    """
    
    print("📝 Research Query:")
    print(query.strip())
    print()
    print("🔍 This query will demonstrate:")
    print("  • Web search for economic data")
    print("  • Calculator tool for CAGR computation")
    print("  • Multi-step reasoning")
    print()
    print("-" * 70)
    print("🔄 Research in progress...")
    print("-" * 70)
    print()
    
    # Run research
    result = agent.research(query, max_iterations=20)
    
    # Display results
    print()
    print("=" * 70)
    print("📊 ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    answer = agent.get_final_answer(result)
    print(answer)
    
    # Show tool usage statistics
    messages = result.get("messages", [])
    tool_calls = 0
    tools_used = set()
    
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_calls += len(msg.tool_calls)
            for tool_call in msg.tool_calls:
                tools_used.add(tool_call.get("name", "unknown"))
    
    print()
    print("=" * 70)
    print("📈 STATISTICS")
    print("=" * 70)
    print(f"Total tool invocations: {tool_calls}")
    print(f"Tools used: {', '.join(tools_used)}")
    print(f"Total messages: {len(messages)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
