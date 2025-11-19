"""
Prompt Template Interface - For managing and rendering prompts
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models.PromptContext import PromptContext


class IPromptTemplate(ABC):
    """
    Abstract prompt template interface.
    Allows for different template engines (Jinja2, string.Template, etc.)
    """

    @abstractmethod
    def render(
        self,
        context: PromptContext
    ) -> str:
        """
        Render prompt with given context.

        Args:
            context: PromptContext with variables

        Returns:
            Rendered prompt string

        Raises:
            TemplateError: If rendering fails
        """
        pass

    @abstractmethod
    def validate_context(
        self,
        context: PromptContext
    ) -> bool:
        """
        Validate that context contains all required variables.

        Args:
            context: PromptContext to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get template metadata.

        Returns:
            Dict with template info (name, category, required_vars, etc.)
        """
        pass

    @abstractmethod
    def get_required_variables(self) -> list[str]:
        """
        Get list of required variables for this template.

        Returns:
            List of required variable names
        """
        pass
