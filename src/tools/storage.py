"""
Storage tool for persisting research findings and citations.
"""

from langchain.tools import tool
import json
import os
from datetime import datetime
from typing import Dict, Any


# In-memory storage (can be replaced with database)
STORAGE_FILE = "./data/storage.json"
_storage: Dict[str, Any] = {}


def _load_storage():
    """Load storage from file."""
    global _storage
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                _storage = json.load(f)
        except:
            _storage = {}
    else:
        _storage = {}


def _save_storage():
    """Save storage to file."""
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(_storage, f, indent=2)


@tool
def store_finding(key: str, value: str, citation: str = "") -> str:
    """
    Store a research finding with optional citation.
    
    Use this tool to save important findings, data points, or facts
    discovered during research. Each finding is stored with a unique key
    and can be retrieved later.
    
    Args:
        key (str): Category or identifier for the finding (e.g., "market_size", "key_stat_1")
        value (str): The actual finding or data
        citation (str): Source citation (optional but recommended)
    
    Returns:
        str: Confirmation message
    
    Examples:
        >>> store_finding("ai_market_2024", "Market valued at $11B", "Source: TechReport 2024")
        >>> store_finding("growth_rate", "32% CAGR projected", "McKinsey Report")
    """
    try:
        _load_storage()
        
        finding = {
            "key": key,
            "value": value,
            "citation": citation,
            "timestamp": datetime.now().isoformat(),
            "id": len(_storage.get("findings", [])) + 1
        }
        
        if "findings" not in _storage:
            _storage["findings"] = []
        
        _storage["findings"].append(finding)
        _save_storage()
        
        return json.dumps({
            "status": "success",
            "message": f"Stored finding '{key}'",
            "finding": finding
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to store finding: {str(e)}"
        })


@tool
def retrieve_finding(key: str) -> str:
    """
    Retrieve a stored research finding by key.
    
    Args:
        key (str): The key of the finding to retrieve
    
    Returns:
        str: The stored finding or error message
    
    Example:
        >>> retrieve_finding("ai_market_2024")
    """
    try:
        _load_storage()
        
        if "findings" not in _storage:
            return json.dumps({
                "status": "error",
                "message": "No findings stored yet"
            })
        
        for finding in _storage["findings"]:
            if finding["key"] == key:
                return json.dumps({
                    "status": "success",
                    "finding": finding
                }, indent=2)
        
        return json.dumps({
            "status": "error",
            "message": f"Finding with key '{key}' not found"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to retrieve finding: {str(e)}"
        })


@tool
def list_all_findings() -> str:
    """
    List all stored research findings.
    
    Returns:
        str: JSON list of all stored findings
    
    Example:
        >>> list_all_findings()
    """
    try:
        _load_storage()
        
        findings = _storage.get("findings", [])
        
        return json.dumps({
            "status": "success",
            "count": len(findings),
            "findings": findings
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to list findings: {str(e)}"
        })


@tool
def clear_storage() -> str:
    """
    Clear all stored findings (use with caution).
    
    Returns:
        str: Confirmation message
    """
    try:
        global _storage
        _storage = {}
        _save_storage()
        
        return json.dumps({
            "status": "success",
            "message": "All findings cleared"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to clear storage: {str(e)}"
        })
