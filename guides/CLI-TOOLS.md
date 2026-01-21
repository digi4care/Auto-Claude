# CLI Tools Guide

Auto Claude supports multiple CLI tools for AI-powered coding assistance. This guide explains how to choose and configure your preferred tool.

## Available CLI Tools

### Claude Code CLI (Default)

The official Claude Code CLI from Anthropic, powered by Claude AI.

**Best for:**
- General coding tasks
- Code generation and refactoring
- Testing and debugging
- Documentation writing

**Installation:**
```bash
# Using npm (recommended)
npm install -g @anthropic-ai/claude-code

# Using Homebrew (macOS)
brew install claude-code
```

**Requirements:**
- Claude Pro or Max subscription
- Node.js 18+ (for npm installation)

---

### Opencode CLI

Alternative CLI tool with different capabilities and approach.

**Best for:**
- Projects with specific Opencode requirements
- Teams using Opencode ecosystem
- Alternative AI coding workflows

**Installation:**
```bash
# Using npm
npm install -g @opencode/cli

# Using Homebrew (macOS)
brew install opencode
```

**Requirements:**
- Opencode account or subscription
- Project-specific configuration

---

## Tool Selection

### Method 1: Environment Variable (Recommended)

Set the `CLI_TOOL` environment variable before running Auto Claude:

```bash
# Use Claude Code (default)
export CLI_TOOL=claude

# Use Opencode
export CLI_TOOL=opencode

# Then run Auto Claude
python run.py --spec 001
```

**Permanently set in your shell profile:**
```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.config/fish/config.fish
echo 'export CLI_TOOL=claude' >> ~/.bashrc
source ~/.bashrc
```

---

### Method 2: Project Configuration

Add the `CLI_TOOL` setting to your project's `.auto-claude/.env` file:

```bash
# Create or edit .auto-claude/.env
echo "CLI_TOOL=opencode" >> .auto-claude/.env
```

**Example `.auto-claude/.env` file:**
```bash
# CLI Tool Selection
CLI_TOOL=claude

# Or use Opencode
# CLI_TOOL=opencode

# Other project settings...
USE_CLAUDE_MD=true
```

---

### Method 3: Command-Line Override

Override the project or environment setting for a single session:

```bash
# Override for this session only
CLI_TOOL=opencode python run.py --spec 001
```

---

## Priority Order

Auto Claude searches for CLI tool configuration in this order:

1. **Command-line environment variable** (e.g., `CLI_TOOL=opencode python ...`)
2. **Project `.auto-claude/.env` file** (project-specific setting)
3. **Shell environment variable** (e.g., `export CLI_TOOL=claude`)
4. **Default**: `claude` if not specified

---

## Switching Between Tools

### Temporary Switch

```bash
# Use Opencode for one session
CLI_TOOL=opencode python run.py --spec 001

# Use Claude for another session
CLI_TOOL=claude python run.py --spec 002
```

### Permanent Switch

```bash
# Update your shell profile
sed -i 's/CLI_TOOL=.*/CLI_TOOL=opencode/' ~/.bashrc
source ~/.bashrc
```

---

## Verifying Your Selection

Check which CLI tool Auto Claude is using:

```bash
# Check environment variable
echo $CLI_TOOL

# Check project configuration
cat .auto-claude/.env | grep CLI_TOOL
```

When running Auto Claude, you'll see log messages like:
```
[INFO] Selected CLI tool (from CLI_TOOL env): claude
[INFO] Created new CLI tool instance: claude
```

---

## Advanced Configuration

### Tool-Specific Settings

Each CLI tool may have additional configuration options:

**Claude Code:**
```bash
# Model selection (default: claude-sonnet-4.1-20250514)
export CLAUDE_MODEL=claude-opus-4.1-20250514
```

**Opencode:**
```bash
# Opencode-specific settings
export OPENCODE_CLI_PATH=/path/to/opencode
```

### Debug Mode

Enable debug logging to see tool selection details:

```bash
export DEBUG=true
python run.py --spec 001
```

Output:
```
[DEBUG] Selected CLI tool (from CLI_TOOL env): claude
[DEBUG] Creating new CLI tool instance: claude
[INFO] Created new CLI tool instance: claude
```

---

## Troubleshooting

### Tool Not Found

If you see "Unknown CLI tool" error:

```bash
# Check available tools
python -c "from core.cli_tools import list_available_cli_tools; print(list_available_cli_tools())"
# Output: ['claude', 'opencode']
```

### Installation Issues

**Claude Code not found:**
```bash
# Verify installation
claude --version

# Reinstall if needed
npm install -g @anthropic-ai/claude-code
```

**Opencode not found:**
```bash
# Verify installation
opencode --version

# Reinstall if needed
npm install -g @opencode/cli
```

### Permission Errors

If you encounter permission issues:

```bash
# Check tool path
which claude
which opencode

# Ensure executable permissions
chmod +x $(which claude)
chmod +x $(which opencode)
```

---

## Best Practices

1. **Use environment variables** for global preferences
2. **Use project configuration** for team projects
3. **Document your choice** in `.auto-claude/.env` for consistency
4. **Test before committing** - verify the tool works as expected
5. **Keep tools updated** - regularly update npm packages

---

## Additional Resources

- **Claude Code Documentation**: https://docs.anthropic.com/claude/docs/cli
- **Opencode Documentation**: Check your Opencode installation docs
- **Auto Claude CLI Usage**: See [guides/CLI-USAGE.md](guides/CLI-USAGE.md)
- **Project Structure**: See [README.md](README.md)

---

## Need Help?

- **Discord Community**: [Join our community](https://discord.gg/KCXaPBr4Dj)
- **GitHub Issues**: [Report problems](https://github.com/AndyMik90/Auto-Claude/issues)
- **Discussions**: [Ask questions](https://github.com/AndyMik90/Auto-Claude/discussions)
