"""Claude Code CLI Adapter"""

import logging
from pathlib import Path
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from claude_agent_sdk.types import HookMatcher

from core.auth import get_sdk_env_vars
from .base import CLIToolAdapter

logger = logging.getLogger(__name__)


class ClaudeCodeAdapter(CLIToolAdapter):
    """Adapter for Claude Code CLI."""

    def __init__(self) -> None:
        """Initialize Claude Code adapter."""
        self._client: ClaudeSDKClient | None = None
        self._settings_file: Path | None = None

    def send_message(self, message: str, **kwargs: Any) -> Any:
        """
        Send a message to Claude Code CLI.

        Args:
            message: The message to send
            **kwargs: Additional parameters
                - spec_dir: Path to spec directory (required)
                - model: Model to use (required)
                - agent_type: Agent type (default: "coder")
                - max_thinking_tokens: Max thinking tokens (optional)

        Returns:
            The SDK client response

        Raises:
            ValueError: If required parameters are missing
        """
        spec_dir = kwargs.get("spec_dir")
        model = kwargs.get("model")

        if not spec_dir or not model:
            raise ValueError("spec_dir and model are required parameters")

        agent_type = kwargs.get("agent_type", "coder")
        max_thinking_tokens = kwargs.get("max_thinking_tokens")

        # Import here to avoid circular dependency
        from core.client import create_client

        project_dir = kwargs.get("project_dir", spec_dir.parent)

        # Create client (this caches project index, MCP servers, etc.)
        self._client = create_client(
            project_dir=project_dir,
            spec_dir=spec_dir,
            model=model,
            agent_type=agent_type,
            max_thinking_tokens=max_thinking_tokens,
        )

        # Send message using SDK
        return self._client.run(message)

    def cleanup(self) -> None:
        """Clean up SDK client resources."""
        if self._settings_file and self._settings_file.exists():
            try:
                self._settings_file.unlink()
                logger.debug(f"Deleted settings file: {self._settings_file}")
            except Exception as e:
                logger.warning(f"Failed to delete settings file: {e}")

        self._client = None
