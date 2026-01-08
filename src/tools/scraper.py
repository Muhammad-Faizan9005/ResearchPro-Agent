"""
Web scraping tool for extracting content from webpages.
"""

from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse


@tool
def scrape_webpage(url: str, max_length: int = 5000) -> str:
    """
    Extract main text content from a webpage.
    
    This tool fetches a webpage and extracts the main textual content,
    removing navigation, ads, and other non-essential elements. Useful
    for reading articles, blog posts, and documentation.
    
    Args:
        url (str): The URL of the webpage to scrape
        max_length (int): Maximum length of content to return (default: 5000 chars)
    
    Returns:
        str: Extracted text content from the webpage
    
    Examples:
        >>> scrape_webpage("https://example.com/article")
        >>> scrape_webpage("https://blog.example.com/post", max_length=3000)
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return json.dumps({
                "status": "error",
                "message": "Invalid URL format",
                "url": url
            })
        
        # Fetch webpage
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            element.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else "No title"
        
        # Extract main content
        # Try to find main content areas
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', class_=['content', 'main-content', 'post-content', 'article-content']) or
            soup.find('body')
        )
        
        # Get text content
        if main_content:
            # Get all paragraphs and headings
            text_elements = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])
            content_parts = []
            
            for elem in text_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 20:  # Filter out very short text
                    content_parts.append(text)
            
            content = "\n\n".join(content_parts)
        else:
            content = soup.get_text(strip=True)
        
        # Truncate if needed
        if len(content) > max_length:
            content = content[:max_length] + "... [Content truncated]"
        
        return json.dumps({
            "status": "success",
            "url": url,
            "title": title_text,
            "content_length": len(content),
            "content": content
        }, indent=2)
        
    except requests.Timeout:
        return json.dumps({
            "status": "error",
            "message": "Request timed out",
            "url": url
        })
    except requests.RequestException as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to fetch webpage: {str(e)}",
            "url": url
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Scraping failed: {str(e)}",
            "url": url
        })


@tool
def extract_links(url: str, link_type: str = "all") -> str:
    """
    Extract links from a webpage.
    
    Args:
        url (str): The URL to extract links from
        link_type (str): Type of links to extract: "all", "internal", or "external"
    
    Returns:
        str: JSON list of links found on the page
    
    Example:
        >>> extract_links("https://example.com", link_type="internal")
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        parsed_base = urlparse(url)
        base_domain = parsed_base.netloc
        
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip anchors and javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Make absolute URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                full_url = f"{parsed_base.scheme}://{base_domain}{href}"
            else:
                continue
            
            parsed_link = urlparse(full_url)
            is_internal = parsed_link.netloc == base_domain
            
            # Filter by type
            if link_type == "internal" and not is_internal:
                continue
            if link_type == "external" and is_internal:
                continue
            
            link_text = a_tag.get_text(strip=True) or "No text"
            links.append({
                "url": full_url,
                "text": link_text,
                "type": "internal" if is_internal else "external"
            })
        
        return json.dumps({
            "status": "success",
            "source_url": url,
            "count": len(links),
            "links": links[:50]  # Limit to 50 links
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Link extraction failed: {str(e)}",
            "url": url
        })
