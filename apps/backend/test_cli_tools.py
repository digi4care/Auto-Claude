"""Unit tests for core.cli_tools module"""

import os
from unittest.mock import patch

import pytest

from core.cli_tools import (
    get_cli_tool_instance,
    get_default_cli_tool,
    list_available_cli_tools,
    cleanup_all_instances,
    ClaudeCodeAdapter,
    OpencodeAdapter,
)


class TestGetCliToolInstance:
    """Tests for get_cli_tool_instance function."""

    def test_get_claude_tool_instance(self):
        """Test getting Claude tool instance."""
        instance = get_cli_tool_instance("claude")

        assert isinstance(instance, ClaudeCodeAdapter)
        assert instance is not None

    def test_get_opencode_tool_instance(self):
        """Test getting Opencode tool instance."""
        instance = get_cli_tool_instance("opencode")

        assert isinstance(instance, OpencodeAdapter)
        assert instance is not None

    def test_singleton_cache_same_tool(self):
        """Test that calling get_cli_tool_instance twice returns same instance."""
        inst1 = get_cli_tool_instance("claude")
        inst2 = get_cli_tool_instance("claude")

        assert inst1 is inst2
        assert id(inst1) == id(inst2)

    def test_singleton_cache_different_tools(self):
        """Test that different tools return different instances."""
        inst1 = get_cli_tool_instance("claude")
        inst2 = get_cli_tool_instance("opencode")

        assert inst1 is not inst2
        assert id(inst1) != id(inst2)
        assert isinstance(inst1, ClaudeCodeAdapter)
        assert isinstance(inst2, OpencodeAdapter)

    def test_cache_clear(self):
        """Test clearing cache."""
        from core.cli_tools import _cli_tool_instances

        inst1 = get_cli_tool_instance("claude")

        # Clear both cache and instances
        get_cli_tool_instance.cache_clear()
        _cli_tool_instances.clear()

        inst2 = get_cli_tool_instance("claude")

        # After cache clear, should be different instances
        assert inst1 is not inst2
        assert id(inst1) != id(inst2)

    def test_invalid_tool_name(self):
        """Test that invalid tool name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown CLI tool"):
            get_cli_tool_instance("invalid_tool")


class TestGetDefaultCliTool:
    """Tests for get_default_cli_tool function."""

    @patch.dict(os.environ, {"CLI_TOOL": "claude"}, clear=False)
    def test_default_from_env_claude(self):
        """Test getting default tool from environment (claude)."""
        instance = get_default_cli_tool()

        assert isinstance(instance, ClaudeCodeAdapter)

    @patch.dict(os.environ, {"CLI_TOOL": "opencode"}, clear=False)
    def test_default_from_env_opencode(self):
        """Test getting default tool from environment (opencode)."""
        instance = get_default_cli_tool()

        assert isinstance(instance, OpencodeAdapter)

    @patch.dict(os.environ, {}, clear=True)
    def test_default_no_env(self):
        """Test getting default tool when no env var set."""
        instance = get_default_cli_tool()

        # Should default to claude
        assert isinstance(instance, ClaudeCodeAdapter)

    @patch.dict(os.environ, {"CLI_TOOL": "CLAUDE"}, clear=False)
    def test_default_case_insensitive(self):
        """Test that tool name is case-insensitive."""
        instance = get_default_cli_tool()

        assert isinstance(instance, ClaudeCodeAdapter)


class TestListAvailableCliTools:
    """Tests for list_available_cli_tools function."""

    def test_list_available_tools(self):
        """Test listing all available CLI tools."""
        tools = list_available_cli_tools()

        assert isinstance(tools, list)
        assert "claude" in tools
        assert "opencode" in tools
        assert len(tools) >= 2


class TestCleanupAllInstances:
    """Tests for cleanup_all_instances function."""

    def test_cleanup_clears_instances(self):
        """Test that cleanup clears all instances."""
        # Create instances
        get_cli_tool_instance("claude")
        get_cli_tool_instance("opencode")

        # Import and check internal state
        from core.cli_tools import _cli_tool_instances

        initial_count = len(_cli_tool_instances)
        assert initial_count >= 2

        # Cleanup
        cleanup_all_instances()

        # Verify instances are cleared
        assert len(_cli_tool_instances) == 0

    def test_cleanup_clears_cache(self):
        """Test that cleanup also clears lru_cache."""
        # Create instances
        inst1 = get_cli_tool_instance("claude")

        # Cleanup
        cleanup_all_instances()

        # After cleanup, new call should create fresh instance
        inst2 = get_cli_tool_instance("claude")

        # Should be different instances
        assert inst1 is not inst2


class TestClaudeCodeAdapter:
    """Tests for ClaudeCodeAdapter class."""

    def test_adapter_instantiation(self):
        """Test that ClaudeCodeAdapter can be instantiated."""
        adapter = ClaudeCodeAdapter()

        assert adapter is not None
        assert hasattr(adapter, "_client")
        assert hasattr(adapter, "_settings_file")

    def test_adapter_cleanup(self):
        """Test that ClaudeCodeAdapter cleanup works."""
        adapter = ClaudeCodeAdapter()
        adapter._settings_file = None

        # Should not raise
        adapter.cleanup()


class TestOpencodeAdapter:
    """Tests for OpencodeAdapter class."""

    def test_adapter_instantiation(self):
        """Test that OpencodeAdapter can be instantiated."""
        adapter = OpencodeAdapter()

        assert adapter is not None
        assert hasattr(adapter, "_command")

    @patch.dict(os.environ, {"OPENCODE_CLI_PATH": "/custom/opencode"}, clear=False)
    def test_adapter_custom_path(self):
        """Test that OpencodeAdapter respects custom path."""
        adapter = OpencodeAdapter()

        assert adapter._command == "/custom/opencode"

    def test_adapter_default_command(self):
        """Test that OpencodeAdapter uses default command when not configured."""
        with patch.dict(os.environ, {}, clear=True):
            adapter = OpencodeAdapter()

            # Should fallback to "opencode"
            assert "opencode" in adapter._command


class TestIntegrationWithClient:
    """Integration tests for cli_tools with client.py."""

    def test_client_imports_cli_tools(self):
        """Test that client.py can import from cli_tools."""
        from core.client import get_default_cli_tool, get_cli_tool_instance

        assert callable(get_default_cli_tool)
        assert callable(get_cli_tool_instance)

    def test_cli_tools_imported_in_client(self):
        """Test that client.py imports required functions."""
        import core.client as client_module

        # Check that imports are present
        assert hasattr(client_module, "get_default_cli_tool")
        assert hasattr(client_module, "get_cli_tool_instance")


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset cache before each test."""
    get_cli_tool_instance.cache_clear()
    from core.cli_tools import _cli_tool_instances

    _cli_tool_instances.clear()
    yield
    get_cli_tool_instance.cache_clear()
    _cli_tool_instances.clear()
