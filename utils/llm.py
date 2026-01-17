"""
LLM Utility Module

Provides interfaces to various language models.
Currently supports Google Gemini API.
"""

import os
from typing import Optional, List
from dotenv import load_dotenv


load_dotenv()


class LLMConfig:
    """Configuration for LLM settings."""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "2048"))
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        return True


class GeminiLLM:
    """Google Gemini API wrapper."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize Gemini LLM.
        
        Args:
            config (LLMConfig, optional): Configuration object.
        """
        self.config = config or LLMConfig()
        self.config.validate()
        
        try:
            import google.generativeai as genai
            self.genai = genai
            self.genai.configure(api_key=self.config.gemini_api_key)
        except ImportError:
            raise ImportError("google-generativeai package not installed")
    
    def generate(self, prompt: str) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt (str): Input prompt
        
        Returns:
            str: Generated text response
        
        Raises:
            ValueError: If API call fails
        """
        try:
            model = self.genai.GenerativeModel(self.config.model_name)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": self.config.max_tokens,
                }
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini API")
            
            return response.text
        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")


# Global LLM instance
_llm_instance: Optional[GeminiLLM] = None


def get_llm() -> GeminiLLM:
    """Get or create global LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = GeminiLLM()
    return _llm_instance


def call_gemini(prompt: str) -> str:
    """
    Call Gemini API with a prompt.
    
    This is a convenience function that uses a global LLM instance.
    For advanced usage, use GeminiLLM class directly.
    
    Args:
        prompt (str): Input prompt
    
    Returns:
        str: Generated text
    
    Example:
        >>> response = call_gemini("What is quantum computing?")
        >>> print(response)
    """
    llm = get_llm()
    return llm.generate(prompt)


def call_gemini_with_config(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> str:
    """
    Call Gemini with custom configuration.
    
    Args:
        prompt (str): Input prompt
        model (str, optional): Model name override
        temperature (float): Sampling temperature
        max_tokens (int): Max output tokens
    
    Returns:
        str: Generated text
    """
    config = LLMConfig()
    if model:
        config.model_name = model
    config.temperature = temperature
    config.max_tokens = max_tokens
    
    llm = GeminiLLM(config)
    return llm.generate(prompt)
