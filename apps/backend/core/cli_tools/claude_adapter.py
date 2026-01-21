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
    """Adapter for Claude Code CLI - wraps Claude SDK client."""

    def __init__(self) -> None:
        """Initialize Claude Code adapter."""
        self._client: ClaudeSDKClient | None = None
        self._settings_file: Path | None = None

    async def __aenter__(self) -> "ClaudeCodeAdapter":
        """
        Enter async context manager.

        Returns:
            Self for use in `async with` blocks
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit async context manager.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        # Cleanup resources on exit
        self.cleanup()

    def run(self, message: str) -> Any:
        """
        Run a message (placeholder for compatibility).

        Actual execution happens via async context manager.
        This provides interface compatibility with agents expecting .run().

        Args:
            message: The message to send

        Returns:
            None (actual execution via __aenter__/__aexit__)

        Raises:
            ValueError: If client is not configured
        """
        if self._client is None:
            raise ValueError(
                "Client not configured. Call send_message() with parameters first."
            )
        # Note: SDK execution happens in async context
        # This .run() method is for interface compatibility only
        logger.warning(
            "ClaudeCodeAdapter.run() called - execution should use async with client"
        )
        return None

    def send_message(self, message: str, **kwargs: Any) -> None:
        """
        Configure the adapter for a session.

        Args:
            message: Ignored (kept for interface compatibility)
            **kwargs: Configuration parameters
                - spec_dir: Path to spec directory (required)
                - model: Model to use (required)
                - agent_type: Agent type (default: "coder")
                - max_thinking_tokens: Max thinking tokens (optional)
                - project_dir: Root project directory (optional, defaults to spec_dir.parent)

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
        from core.client import _create_claude_sdk_client

        # Create client (this caches project index, MCP servers, etc.)
        self._client = _create_claude_sdk_client(
            project_dir=kwargs.get("project_dir", spec_dir.parent),
            spec_dir=spec_dir,
            model=model,
            agent_type=agent_type,
            max_thinking_tokens=max_thinking_tokens,
        )

    def cleanup(self) -> None:
        """Clean up SDK client resources."""
        if self._settings_file and self._settings_file.exists():
            try:
                self._settings_file.unlink()
                logger.debug(f"Deleted settings file: {self._settings_file}")
            except Exception as e:
                logger.warning(f"Failed to delete settings file: {e}")

        self._client = None
