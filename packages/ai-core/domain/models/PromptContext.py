"""
Prompt Context Model - Context data for rendering prompts
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class PromptContext:
    """
    Context for rendering prompt templates.

    Contains variables and metadata needed to generate prompts.
    """

    variables: Dict[str, Any]
    site_id: Optional[str] = None
    user_id: Optional[str] = None
    feature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get variable value"""
        return self.variables.get(key, default)

    def has(self, key: str) -> bool:
        """Check if variable exists"""
        return key in self.variables

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "variables": self.variables,
            "site_id": self.site_id,
            "user_id": self.user_id,
            "feature": self.feature,
            "metadata": self.metadata
        }
