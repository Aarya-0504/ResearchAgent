"""
Web Search Tool Module

Provides web search functionality for the research agent.
Supports multiple search backends (Tavily, SerpAPI, Google).
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv


load_dotenv()


def web_search(query: str, num_results: int = 5) -> str:
    """
    Perform web search and return results.
    
    Supports multiple search backends in order of preference:
    1. Tavily AI (recommended)
    2. SerpAPI
    3. Google Custom Search
    4. Fallback mock results
    
    Args:
        query (str): Search query string
        num_results (int): Number of results to return. Defaults to 5.
    
    Returns:
        str: Formatted search results as a string
    """
    
    # Try Tavily first
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        return _tavily_search(query, num_results, tavily_key)
    
    # Try SerpAPI
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    if serpapi_key:
        return _serpapi_search(query, num_results, serpapi_key)
    
    # Try Google Custom Search
    google_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    if google_key and google_cse_id:
        return _google_search(query, num_results, google_key, google_cse_id)
    
    # Fallback
    return _fallback_search(query)


def _tavily_search(query: str, num_results: int, api_key: str) -> str:
    """Search using Tavily AI API."""
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": query,
            "max_results": num_results,
            "include_answer": True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results_text = f"Tavily Search Results for '{query}':\n\n"
        
        if "answer" in data:
            results_text += f"Answer: {data['answer']}\n\n"
        
        if "results" in data:
            for i, result in enumerate(data["results"][:num_results], 1):
                results_text += f"{i}. {result.get('title', 'No title')}\n"
                results_text += f"   URL: {result.get('url', 'No URL')}\n"
                results_text += f"   {result.get('content', 'No content')}\n\n"
        
        return results_text
    except Exception as e:
        print(f"Tavily search error: {str(e)}")
        return _fallback_search(query)


def _serpapi_search(query: str, num_results: int, api_key: str) -> str:
    """Search using SerpAPI."""
    try:
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": api_key,
            "num": num_results,
            "engine": "google"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results_text = f"SerpAPI Search Results for '{query}':\n\n"
        
        if "organic_results" in data:
            for i, result in enumerate(data["organic_results"][:num_results], 1):
                results_text += f"{i}. {result.get('title', 'No title')}\n"
                results_text += f"   URL: {result.get('link', 'No URL')}\n"
                results_text += f"   {result.get('snippet', 'No snippet')}\n\n"
        
        return results_text
    except Exception as e:
        print(f"SerpAPI search error: {str(e)}")
        return _fallback_search(query)


def _google_search(query: str, num_results: int, api_key: str, cse_id: str) -> str:
    """Search using Google Custom Search API."""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": min(num_results, 10)
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results_text = f"Google Search Results for '{query}':\n\n"
        
        if "items" in data:
            for i, item in enumerate(data["items"][:num_results], 1):
                results_text += f"{i}. {item.get('title', 'No title')}\n"
                results_text += f"   URL: {item.get('link', 'No URL')}\n"
                results_text += f"   {item.get('snippet', 'No snippet')}\n\n"
        
        return results_text
    except Exception as e:
        print(f"Google search error: {str(e)}")
        return _fallback_search(query)


def _fallback_search(query: str) -> str:
    """Fallback search when no API keys are configured."""
    return f"""
Web Search Results for '{query}':

Note: No search API configured. Please set one of:
- TAVILY_API_KEY (recommended)
- SERPAPI_API_KEY
- GOOGLE_API_KEY + GOOGLE_CSE_ID

For now, the system will proceed with web search simulation.
In production, configure at least one search API in your .env file.

Search Query: {query}
Status: Using mock results for demonstration
"""

