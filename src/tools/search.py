"""
Web search tool for the ResearchPro Agent.
Provides web search capabilities using DuckDuckGo (free, no API key required).
"""

from langchain.tools import tool
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import json


@tool
def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web for information on a given topic using DuckDuckGo.
    
    This tool performs a web search and returns the top results with titles,
    URLs, and snippets. It's useful for finding recent information, articles,
    and resources on any topic.
    
    Args:
        query (str): The search query to look up
        num_results (int): Number of results to return (default: 5, max: 10)
    
    Returns:
        str: JSON string containing search results with titles, URLs, and snippets
    
    Examples:
        >>> web_search("AI in healthcare 2024")
        >>> web_search("quantum computing applications", num_results=3)
    """
    try:
        # Use DuckDuckGo HTML search (no API key required)
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.post(url, data=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Parse search results
        result_divs = soup.find_all('div', class_='result', limit=num_results)
        
        for idx, div in enumerate(result_divs, 1):
            title_elem = div.find('a', class_='result__a')
            snippet_elem = div.find('a', class_='result__snippet')
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No description available"
                
                results.append({
                    "id": idx,
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
        
        if not results:
            return json.dumps({
                "status": "no_results",
                "message": f"No results found for query: {query}",
                "results": []
            })
        
        return json.dumps({
            "status": "success",
            "query": query,
            "count": len(results),
            "results": results
        }, indent=2)
        
    except requests.Timeout:
        return json.dumps({
            "status": "error",
            "message": "Search request timed out. Please try again.",
            "results": []
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Search failed: {str(e)}",
            "results": []
        })


@tool
def web_search_simple(query: str) -> str:
    """
    Simplified web search that returns a brief summary of top results.
    Use this when you need quick information without detailed results.
    
    Args:
        query (str): The search query
    
    Returns:
        str: Brief summary of search results
    """
    result = web_search(query, num_results=3)
    data = json.loads(result)
    
    if data["status"] != "success":
        return f"Search failed: {data.get('message', 'Unknown error')}"
    
    summary = f"Found {data['count']} results for '{query}':\n\n"
    for r in data["results"]:
        summary += f"{r['id']}. {r['title']}\n   {r['snippet'][:100]}...\n\n"
    
    return summary
