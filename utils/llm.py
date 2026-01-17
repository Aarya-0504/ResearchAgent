"""
LLM Utility Module with LangChain Integration

Provides flexible interfaces to multiple language model providers.
Supports: Google Gemini, Claude (Anthropic), OpenAI GPT, and more.

Easy switching between providers via LLM_PROVIDER environment variable:
    - gemini (default) - Google Gemini
    - claude - Anthropic Claude
    - openai - OpenAI GPT
"""

import os
from typing import Optional
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class LLMConfig:
    """Configuration for LLM settings."""
    
    def __init__(self):
        # Provider selection
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        
        # API Keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Model names
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        
        # Generation parameters
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    
    def validate(self) -> bool:
        """Validate configuration based on selected provider."""
        if self.provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set in environment")
        elif self.provider == "claude":
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
        elif self.provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        return True


class LangChainLLM:
    """Unified LLM interface using LangChain."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LangChain LLM wrapper.
        
        Args:
            config (LLMConfig, optional): Configuration object.
        """
        self.config = config or LLMConfig()
        self.config.validate()
        self.model = self._initialize_model()
        
        logger.info(f"✅ LLM initialized: {self.config.provider} ({self._get_model_name()})")
    
    def _initialize_model(self):
        """Initialize the appropriate LLM based on provider."""
        try:
            if self.config.provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model=self.config.gemini_model,
                    api_key=self.config.gemini_api_key,
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                )
            
            elif self.config.provider == "claude":
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=self.config.claude_model,
                    api_key=self.config.anthropic_api_key,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
            
            elif self.config.provider == "openai":
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=self.config.openai_model,
                    api_key=self.config.openai_api_key,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
        
        except ImportError as e:
            raise ImportError(f"LangChain provider library not installed: {str(e)}")
    
    def _get_model_name(self) -> str:
        """Get current model name."""
        if self.config.provider == "gemini":
            return self.config.gemini_model
        elif self.config.provider == "claude":
            return self.config.claude_model
        elif self.config.provider == "openai":
            return self.config.openai_model
        return "unknown"
    
    def generate(self, prompt: str) -> str:
        """
        Generate text using the configured LLM.
        
        Args:
            prompt (str): Input prompt
        
        Returns:
            str: Generated text response
        
        Raises:
            ValueError: If API call fails
        """
        try:
            from langchain_core.messages import HumanMessage
            
            message = HumanMessage(content=prompt)
            response = self.model.invoke([message])
            
            if not response.content:
                raise ValueError("Empty response from LLM")
            
            return response.content
        
        except Exception as e:
            raise ValueError(f"LLM API error: {str(e)}")


# Global LLM instance
_llm_instance: Optional[LangChainLLM] = None


def get_llm() -> LangChainLLM:
    """Get or create global LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LangChainLLM()
    return _llm_instance


def call_gemini(prompt: str) -> str:
    """
    Call the configured LLM with a prompt.
    
    This is a convenience function that uses a global LLM instance.
    Supports any provider configured via LLM_PROVIDER environment variable.
    
    Args:
        prompt (str): Input prompt
    
    Returns:
        str: Generated text
    
    Example:
        >>> response = call_gemini("What is quantum computing?")
        >>> print(response)
        
    Note:
        Function name "call_gemini" is kept for backward compatibility.
        It actually uses the LLM provider specified in .env (LLM_PROVIDER).
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
    Call LLM with custom configuration (temporary override).
    
    Args:
        prompt (str): Input prompt
        model (str, optional): Model name override
        temperature (float): Sampling temperature
        max_tokens (int): Max output tokens
    
    Returns:
        str: Generated text
        
    Note:
        This creates a temporary LLM instance with custom settings.
        For consistent settings, configure via environment variables.
    """
    config = LLMConfig()
    if model:
        # Try to detect provider from model name or use current provider
        config.gemini_model = model if config.provider == "gemini" else config.gemini_model
        config.claude_model = model if config.provider == "claude" else config.claude_model
        config.openai_model = model if config.provider == "openai" else config.openai_model
    
    config.temperature = temperature
    config.max_tokens = max_tokens
    
    llm = LangChainLLM(config)
    return llm.generate(prompt)
