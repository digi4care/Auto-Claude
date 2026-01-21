"""CLI Tools Package"""

import logging
import functools

from .base import CLIToolAdapter
from .claude_adapter import ClaudeCodeAdapter
from .opencode_adapter import OpencodeAdapter

logger = logging.getLogger(__name__)

__all__ = ["CLIToolAdapter", "ClaudeCodeAdapter", "OpencodeAdapter"]

# Registry of available CLI tools
CLI_TOOLS: dict[str, type] = {
    "claude": ClaudeCodeAdapter,
    "opencode": OpencodeAdapter,
}

# Singleton instances cache
_cli_tool_instances: dict[str, CLIToolAdapter] = {}


@functools.lru_cache(maxsize=None)
def get_cli_tool_instance(tool_name: str) -> CLIToolAdapter:
    """
    Get CLI tool instance by name (cached).

    This function uses functools.lru_cache for efficient caching.
    The cache persists for the Python process lifetime.

    Args:
        tool_name: Name of CLI tool ('claude', 'opencode', etc.)

    Returns:
        CLIToolAdapter instance

    Raises:
        ValueError: If tool_name is not registered
    """
    if tool_name not in CLI_TOOLS:
        raise ValueError(
            f"Unknown CLI tool: '{tool_name}'. "
            f"Available tools: {sorted(CLI_TOOLS.keys())}"
        )

    # Return cached instance if exists
    if tool_name in _cli_tool_instances:
        logger.debug(f"Using cached CLI tool instance: {tool_name}")
        return _cli_tool_instances[tool_name]

    # Create new instance
    instance = CLI_TOOLS[tool_name]()
    _cli_tool_instances[tool_name] = instance
    logger.info(f"Created new CLI tool instance: {tool_name}")
    return instance


def get_default_cli_tool() -> CLIToolAdapter:
    """
    Get default CLI tool (from env or default to claude).

    Returns:
        CLIToolAdapter instance
    """
    import os

    tool_name = os.environ.get("CLI_TOOL", "claude").lower()
    logger.info(f"Selected CLI tool (from CLI_TOOL env): {tool_name}")
    return get_cli_tool_instance(tool_name)


def list_available_cli_tools() -> list[str]:
    """
    Return list of available CLI tool names.

    Returns:
        List of tool names
    """
    return sorted(CLI_TOOLS.keys())


def cleanup_all_instances():
    """
    Clean up all CLI tool instances (stop servers, etc.).

    This should be called when Auto-Claude exits.
    """
    global _cli_tool_instances
    for tool_name, instance in _cli_tool_instances.items():
        try:
            logger.info(f"Cleaning up CLI tool: {tool_name}")
            instance.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up {tool_name}: {e}")
    _cli_tool_instances.clear()
    get_cli_tool_instance.cache_clear()
