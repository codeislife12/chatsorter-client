# chatsorter_client/client.py
"""
ChatSorter Python Client
Official SDK for ChatSorter Memory API
"""

import requests
from typing import Dict, List, Optional, Any
import json


class ChatSorter:
    """
    ChatSorter Memory API Client
    
    Usage:
        client = ChatSorter(api_key="sk_test_demo123")
        
        # TRUE PLUG AND PLAY (1 line):
        prompt = client.build_prompt(chat_id="user123", message=user_message)
        
        # Or use individual methods:
        client.add_message(chat_id="user123", message="I love pizza")
        results = client.search(chat_id="user123", query="food")
    """
    
    def __init__(self, api_key: str, base_url: str = "https://chatsorter-api.onrender.com"):
        """
        Initialize ChatSorter client
        
        Args:
            api_key: Your ChatSorter API key (get from dashboard)
            base_url: API endpoint (default: https://chatsorter-api.onrender.com)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def build_prompt(self, chat_id: str, message: str, 
                    prompt_template: str = "{context}{message}",
                    max_memories: int = 3) -> str:
        """
        🚀 PLUG AND PLAY: Automatic memory storage, search, and prompt building
        
        This is the easiest way to add memory to your chatbot.
        Just replace your prompt line with this method.
        
        Args:
            chat_id: Unique user/conversation ID
            message: Current user message
            prompt_template: Your prompt format (use {context} and {message} placeholders)
            max_memories: Max relevant memories to include (default: 3)
            
        Returns:
            Complete prompt with memory context automatically injected
            
        Example:
            # Instead of:
            prompt = f"User: {user_message}"
            
            # Do this:
            prompt = chatsorter.build_prompt("user123", user_message, "User: {message}")
            
            # For chat models (OpenAI, Claude):
            prompt = chatsorter.build_prompt("user123", user_message, 
                prompt_template="System: {context}\nUser: {message}")
        """
        # 1. Store message in memory
        try:
            self.process(chat_id=chat_id, message=message)
        except Exception as e:
            print(f"[ChatSorter] Warning: Failed to store message: {e}")
        
        # 2. Search for relevant memories
        context = ""
        try:
            search_result = self.search(chat_id=chat_id, query=message)
            if search_result.get('result', {}).get('found'):
                memories = search_result['result']['results'][:max_memories]
                if memories:
                    context_items = []
                    for mem in memories:
                        content = mem.get('content', '')
                        importance = mem.get('decayed_importance', 0)
                        context_items.append(f"- {content} (importance: {importance:.1f})")
                    context = "Previous context:\n" + "\n".join(context_items) + "\n\n"
        except Exception as e:
            print(f"[ChatSorter] Warning: Failed to search memory: {e}")
        
        # 3. Build final prompt
        final_prompt = prompt_template.replace("{context}", context).replace("{message}", message)
        return final_prompt
    
    def add_message(self, chat_id: str, message: str, 
                   tool_result: Optional[Dict] = None) -> Dict:
        """
        Add a message to memory
        
        Args:
            chat_id: Unique identifier for this conversation
            message: The message text to store
            tool_result: Optional metadata about tools used
            
        Returns:
            Dict with processing results including importance score
            
        Example:
            result = client.add_message(
                chat_id="user123",
                message="My favorite food is pizza"
            )
            print(f"Importance: {result['result']['importance_score']}")
        """
        response = self.session.post(
            f"{self.base_url}/process",
            json={
                "chat_id": chat_id,
                "message": message,
                "tool_result": tool_result
            }
        )
        response.raise_for_status()
        return response.json()
    
    def process(self, chat_id: str, message: str, 
               tool_result: Optional[Dict] = None) -> Dict:
        """
        Alias for add_message() - matches API endpoint name
        
        Args:
            chat_id: Unique identifier for this conversation
            message: The message text to store
            tool_result: Optional metadata about tools used
            
        Returns:
            Dict with processing results including importance score
        """
        return self.add_message(chat_id, message, tool_result)
    
    def search(self, chat_id: str, query: str, 
              use_vector_db: bool = True, limit: int = 5) -> Dict:
        """
        Search memory semantically
        
        Args:
            chat_id: Conversation ID to search
            query: Search query (semantic, not keyword)
            use_vector_db: Use vector DB if available (default: True)
            limit: Maximum results to return
            
        Returns:
            Dict with search results ranked by relevance
            
        Example:
            results = client.search(
                chat_id="user123",
                query="food preferences"
            )
            
            if results['result']['found']:
                for item in results['result']['results']:
                    print(f"- {item['content']} (score: {item['retrieval_score']})")
        """
        response = self.session.post(
            f"{self.base_url}/search",
            json={
                "chat_id": chat_id,
                "query": query,
                "use_vector_db": use_vector_db
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_context(self, chat_id: str, message: str, 
                   max_results: int = 3) -> str:
        """
        Get relevant context for LLM prompt
        Convenience method that searches and formats results
        
        Args:
            chat_id: Conversation ID
            message: Current user message (used for search)
            max_results: Maximum context items to include
            
        Returns:
            Formatted string ready to inject into LLM prompt
            
        Example:
            # Get context
            context = client.get_context(
                chat_id="user123",
                message="What should I eat for dinner?"
            )
            
            # Use in OpenAI call
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"Context:\n{context}"},
                    {"role": "user", "content": message}
                ]
            )
        """
        search_result = self.search(chat_id, message)
        
        if not search_result.get('result', {}).get('found'):
            return ""
        
        results = search_result['result']['results'][:max_results]
        
        context_items = []
        for i, item in enumerate(results, 1):
            content = item.get('content', '')
            importance = item.get('decayed_importance', 0)
            context_items.append(f"{i}. {content} (importance: {importance:.1f})")
        
        return "\n".join(context_items)
    
    def get_stats(self, chat_id: str) -> Dict:
        """
        Get statistics for a conversation
        
        Args:
            chat_id: Conversation ID
            
        Returns:
            Dict with message count, summary count, and performance metrics
        """
        response = self.session.get(
            f"{self.base_url}/stats",
            params={"chat_id": chat_id}
        )
        response.raise_for_status()
        return response.json()
    
    def get_memory_analysis(self, chat_id: str) -> Dict:
        """
        Get detailed memory analysis
        
        Args:
            chat_id: Conversation ID
            
        Returns:
            Dict with memory items, decay stats, and metadata
        """
        response = self.session.get(
            f"{self.base_url}/memory/{chat_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """
        Check API health status
        
        Returns:
            Dict with server status, version, features
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


class ChatSorterError(Exception):
    """Base exception for ChatSorter client errors"""
    pass


class AuthenticationError(ChatSorterError):
    """Raised when API key is invalid"""
    pass


class RateLimitError(ChatSorterError):
    """Raised when usage limits are exceeded"""
    pass