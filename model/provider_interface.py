"""Abstract interface for LLM providers."""
from abc import ABC, abstractmethod
from typing import Optional, Dict


class ModelProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate candidate source code from prompt.
        
        Args:
            prompt: Generation prompt
            context: Optional context dictionary
            
        Returns:
            Generated source code as string
            
        Raises:
            ConnectionError: If provider is unreachable
            ValueError: If prompt is invalid
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and reachable.
        
        Returns:
            True if provider can generate, False otherwise
        """
        pass

    def validate_prompt(self, prompt: str) -> bool:
        """Validate that prompt is well-formed.
        
        Args:
            prompt: Prompt to validate
            
        Returns:
            True if prompt is valid
        """
        return isinstance(prompt, str) and len(prompt) > 0 and len(prompt) < 10000
