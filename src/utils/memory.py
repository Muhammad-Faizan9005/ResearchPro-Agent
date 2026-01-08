"""
Conversation memory storage for the ResearchPro Agent.
Saves and retrieves conversation history for PDF generation and analysis.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ConversationMemory:
    """Manages conversation history storage."""
    
    def __init__(self, storage_dir: str = "conversations"):
        """
        Initialize conversation memory.
        
        Args:
            storage_dir: Directory to store conversation files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def save_conversation(
        self,
        query: str,
        answer: str,
        messages: List[Dict],
        citations: List[Dict] = None,
        metadata: Dict = None,
        conversation_id: str = None,
        conversation_name: str = None
    ) -> str:
        """
        Save a conversation to disk.
        
        Args:
            query: The research query
            answer: The final answer
            messages: List of all messages in the conversation
            citations: Optional list of citations
            metadata: Optional metadata (model, temperature, etc.)
            conversation_id: If provided, append to existing conversation; otherwise create new
            conversation_name: Optional custom name for the conversation
        
        Returns:
            Conversation ID (timestamp-based filename)
        """
        # If conversation_id provided, load and append
        if conversation_id:
            existing = self.load_conversation(conversation_id)
            if existing:
                # Append new query-answer pair
                existing["exchanges"].append({
                    "query": query,
                    "answer": answer,
                    "timestamp": datetime.now().isoformat()
                })
                existing["last_updated"] = datetime.now().isoformat()
                existing["messages"] = self._serialize_messages(messages)
                existing["citations"] = citations or existing.get("citations", [])
                
                filepath = self.storage_dir / f"{conversation_id}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(existing, f, indent=2, ensure_ascii=False)
                
                return conversation_id
        
        # Create new conversation
        timestamp = datetime.now()
        conversation_id = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Generate meaningful name from query if not provided
        if not conversation_name:
            conversation_name = self._generate_conversation_name(query)
        
        conversation_data = {
            "id": conversation_id,
            "name": conversation_name,
            "created_at": timestamp.isoformat(),
            "last_updated": timestamp.isoformat(),
            "exchanges": [
                {
                    "query": query,
                    "answer": answer,
                    "timestamp": timestamp.isoformat()
                }
            ],
            "messages": self._serialize_messages(messages),
            "citations": citations or [],
            "metadata": metadata or {}
        }
        
        filepath = self.storage_dir / f"{conversation_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        return conversation_id
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Load a conversation from disk.
        
        Args:
            conversation_id: The conversation ID to load
        
        Returns:
            Conversation data or None if not found
        """
        filepath = self.storage_dir / f"{conversation_id}.json"
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_conversations(self, limit: int = 50) -> List[Dict]:
        """
        List all saved conversations.
        
        Args:
            limit: Maximum number of conversations to return
        
        Returns:
            List of conversation summaries (id, timestamp, query)
        """
        conversations = []
        
        for filepath in sorted(self.storage_dir.glob("*.json"), reverse=True)[:limit]:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Support both old and new format
                    if "exchanges" in data:
                        first_query = data["exchanges"][0]["query"][:100] if data["exchanges"] else "N/A"
                        total_exchanges = len(data["exchanges"])
                    else:
                        # Old format
                        first_query = data.get("query", "N/A")[:100]
                        total_exchanges = 1
                    
                    conversations.append({
                        "id": data["id"],
                        "name": data.get("name", first_query[:50]),
                        "timestamp": data.get("created_at", data.get("timestamp", "N/A")),
                        "last_updated": data.get("last_updated", data.get("timestamp", "N/A")),
                        "first_query": first_query,
                        "total_exchanges": total_exchanges
                    })
            except (json.JSONDecodeError, KeyError):
                continue
        
        return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: The conversation ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        filepath = self.storage_dir / f"{conversation_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def _generate_conversation_name(self, query: str, max_length: int = 50) -> str:
        """
        Generate a meaningful conversation name from the query.
        
        Args:
            query: The first query in the conversation
            max_length: Maximum length for the name
        
        Returns:
            Clean conversation name
        """
        import re
        
        # Remove special characters and clean up
        clean_query = re.sub(r'[^a-zA-Z0-9\s-]', '', query)
        clean_query = re.sub(r'\s+', ' ', clean_query).strip()
        
        # Truncate and capitalize first letter of each word
        words = clean_query.split()[:8]  # Take first 8 words
        name = ' '.join(words)
        
        if len(name) > max_length:
            name = name[:max_length].rsplit(' ', 1)[0]  # Cut at word boundary
        
        return name or "Untitled Conversation"
    
    def _serialize_messages(self, messages: List) -> List[Dict]:
        """
        Serialize message objects to dict format.
        
        Args:
            messages: List of message objects
        
        Returns:
            List of serialized messages
        """
        serialized = []
        for msg in messages:
            if hasattr(msg, 'content'):
                msg_dict = {
                    "type": msg.__class__.__name__,
                    "content": msg.content
                }
                
                # Include tool calls if present
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "name": tc.get("name"),
                            "args": tc.get("args")
                        } for tc in msg.tool_calls
                    ]
                
                # Include tool call ID if present
                if hasattr(msg, 'tool_call_id'):
                    msg_dict["tool_call_id"] = msg.tool_call_id
                
                serialized.append(msg_dict)
            elif isinstance(msg, dict):
                serialized.append(msg)
        
        return serialized


# Convenience functions for global usage
_default_memory = ConversationMemory()


def save_conversation(
    query: str,
    answer: str,
    messages: List,
    citations: List[Dict] = None,
    metadata: Dict = None,
    conversation_id: str = None,
    conversation_name: str = None,
    storage_dir: str = "conversations"
) -> str:
    """
    Save a conversation using the default memory instance.
    
    Args:
        query: The research query
        answer: The final answer
        messages: List of all messages
        citations: Optional citations
        metadata: Optional metadata
        conversation_id: Optional existing conversation ID to append to
        conversation_name: Optional custom name for the conversation
        storage_dir: Storage directory
    
    Returns:
        Conversation ID
    """
    memory = ConversationMemory(storage_dir)
    return memory.save_conversation(query, answer, messages, citations, metadata, conversation_id, conversation_name)


def load_conversation(conversation_id: str, storage_dir: str = "conversations") -> Optional[Dict]:
    """Load a conversation by ID."""
    memory = ConversationMemory(storage_dir)
    return memory.load_conversation(conversation_id)


def list_conversations(limit: int = 50, storage_dir: str = "conversations") -> List[Dict]:
    """List all saved conversations."""
    memory = ConversationMemory(storage_dir)
    return memory.list_conversations(limit)
