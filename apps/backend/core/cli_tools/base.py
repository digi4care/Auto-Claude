"""Base CLI Tool Adapter"""

from abc import ABC, abstractmethod
from typing import Any


class CLIToolAdapter(ABC):
    """Base class for CLI tool adapters."""

    @abstractmethod
    def send_message(self, message: str, **kwargs: Any) -> Any:
        """
        Send a message to the CLI tool.

        Args:
            message: The message to send
            **kwargs: Additional tool-specific parameters

        Returns:
            The tool response
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources (stop servers, close connections, etc.)."""
        pass
