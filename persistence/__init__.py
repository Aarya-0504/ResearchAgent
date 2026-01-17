"""
Persistence Module

Handles all data storage and retrieval for the research system.
"""

from .memory_manager import MemoryManager, get_memory_manager

__all__ = ["MemoryManager", "get_memory_manager"]
