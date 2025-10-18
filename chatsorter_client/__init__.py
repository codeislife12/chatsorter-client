# chatsorter_client/__init__.py
"""
ChatSorter Client - Official Python SDK
Simple memory API for chatbots
"""

from .client import ChatSorter, ChatSorter as ChatSorterClient

__version__ = "1.0.0"
__all__ = ['ChatSorter', 'ChatSorterClient']