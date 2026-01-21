"""Opencode CLI Adapter"""

import logging
import os
import subprocess
from typing import Any

from .base import CLIToolAdapter

logger = logging.getLogger(__name__)


class OpencodeAdapter(CLIToolAdapter):
    """Adapter for Opencode CLI."""

    def __init__(self) -> None:
        """Initialize Opencode adapter."""
        self._command = self._find_opencode_command()

    def _find_opencode_command(self) -> str:
        """
        Find the Opencode CLI command.

        Returns:
            The command to use ('opencode' or full path)
        """
        # Check environment variable first
        opencode_path = os.environ.get("OPENCODE_CLI_PATH")
        if opencode_path:
            return opencode_path

        # Try system PATH
        try:
            subprocess.run(
                ["opencode", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
            return "opencode"
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            logger.warning("Opencode CLI not found")
            return "opencode"

    def send_message(self, message: str, **kwargs: Any) -> Any:
        """
        Send a command to Opencode CLI.

        Args:
            message: The command to send
            **kwargs: Additional parameters

        Returns:
            The command output
        """
        cmd = [self._command] + message.split()

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Opencode command failed: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            logger.error("Opencode command timed out")
            raise

    def cleanup(self) -> None:
        """Clean up resources (no-op for Opencode)."""
        pass
