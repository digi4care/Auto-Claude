# AGENTS.md

This file provides build/lint/test commands and code style guidelines for agentic coding.

## Quick Reference

**Backend (Python)** - Uses Ruff for linting/formatting
**Frontend (TypeScript)** - Uses Biome for linting/formatting
**Golden Rule**: If you can't easily test it, refactor it

---

## Issue Tracking

This project uses **bd (beads)** for issue tracking.
Run `bd prime` for workflow context, or install hooks (`bd hooks install`) for auto-injection.

**Quick reference:**
- `bd ready` - Find unblocked work
- `bd create "Title" --type task --priority 2` - Create issue
- `bd close <id>` - Complete work
- `bd sync` - Sync with git (run at session end)

For full workflow details: `bd prime`

---

## Build/Lint/Test Commands

### Backend (Python)

```bash
# Run all tests
npm run test:backend

# Run specific test file
npm run test:backend -- tests/test_security.py -v

# Run specific test
npm run test:backend -- tests/test_security.py::test_bash_command_validation -v

# Skip slow tests
npm run test:backend -- -m "not slow"

# Run with coverage
apps/backend/.venv/bin/pytest tests/ --cov=apps/backend --cov-report=html

# Lint (ruff)
ruff check apps/backend/

# Format (ruff-format)
ruff format apps/backend/

# Run pre-commit checks
pre-commit run --all-files
```

**Note**: Use `apps/backend/.venv/bin/pytest` on Unix, `apps/backend/.venv/Scripts/pytest.exe` on Windows.

### Frontend (TypeScript/React)

```bash
cd apps/frontend

# Lint (Biome)
npm run lint

# Auto-fix lint issues
npm run lint:fix

# Format (Biome)
npm run format

# Type checking
npm run typecheck

# Run unit tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Build for production
npm run build

# Package for distribution
npm run package
```

### Root Commands

```bash
# Install all dependencies
npm run install:all

# Run backend tests
npm run test:backend

# Start frontend dev
npm run dev
```

---

## Code Style Guidelines

### Python

**Imports**:
- Standard library → Third-party → Local (with blank lines between groups)
- Use `from typing import X` for type hints
- Sort automatically via Ruff (I rule set)

**Formatting**:
- PEP 8 style
- 4 spaces indentation
- Double quotes for strings
- Line length: handled by formatter (Ruff ignores E501)
- No trailing whitespace
- End files with newline

**Types**:
- **Required**: Type hints for all function signatures
- Use modern union syntax: `str | int` not `Union[str, int]`
- Use collections.abc types for generics: `Iterator[X]`, `Mapping[K, V]`

**Naming**:
- snake_case for variables/functions: `get_user_data`
- PascalCase for classes: `UserDataManager`
- UPPER_SNAKE_CASE for constants: `MAX_RETRIES`
- _prefix for private: `_internal_function`

**Error Handling**:
- **ALWAYS** specify `encoding="utf-8"` for text file operations (Windows compatibility)
  ```python
  # Good
  with open(path, encoding="utf-8") as f:
      content = f.read()

  # Wrong - platform-dependent encoding
  with open(path) as f:
      content = f.read()
  ```
- Validate at boundaries with explicit error messages
- Return result objects or raise with context, not silent failures

**Docstrings**:
- Required for public functions and classes
- Use triple quotes, Google style preferred
- Describe Args and Returns

**Example**:
```python
def get_next_chunk(spec_dir: Path) -> dict | None:
    """
    Find the next pending chunk in the implementation plan.

    Args:
        spec_dir: Path to the spec directory

    Returns:
        The next chunk dict or None if all chunks are complete
    """
    ...
```

**Patterns**:
- Keep functions < 50 lines when possible
- Pure functions: same input = same output, no side effects
- Prefer pathlib.Path over os.path
- Use context managers for resources

### TypeScript/React

**Imports**:
- Explicit imports over wildcards
- Group: External → Internal (with blank line)
- No namespace imports unless necessary

**Formatting**:
- 2 spaces indentation
- Double quotes for strings
- No trailing whitespace
- Enforced by Biome

**Types**:
- Strict mode required
- Interfaces for object shapes
- Type aliases for unions: `type Status = "pending" | "complete"`
- Explicit any禁止 - use proper types or unknown

**Naming**:
- camelCase for variables/functions: `getUserData`
- PascalCase for components: `UserDataManager`
- UPPER_SNAKE_CASE for constants: `MAX_RETRIES`
- Prefix boolean predicates: `isValid`, `hasPermission`, `canAccess`

**Components**:
- Functional components with hooks
- **Named exports preferred**: `export function Component()`
- Props interface explicitly defined
- Use shadcn-svelte components from `src/renderer/components/ui/`

**Internationalization (i18n)**:
- **CRITICAL**: All user-facing text MUST use translation keys
  ```tsx
  // Good
  const { t } = useTranslation(['navigation', 'common']);
  <span>{t('navigation:items.githubPRs')}</span>

  // Wrong
  <span>GitHub PRs</span>
  ```

**Error Handling**:
- Validate inputs at component boundaries
- Use error boundaries for component errors
- Return proper error states for user feedback

**Example**:
```typescript
interface TaskCardProps {
  task: Task;
  onEdit: (id: string) => void;
}

export function TaskCard({ task, onEdit }: TaskCardProps) {
  const { t } = useTranslation(['tasks', 'common']);

  return (
    <div className="task-card">
      <h3>{task.title}</h3>
      <button onClick={() => onEdit(task.id)}>
        {t('tasks:buttons.edit')}
      </button>
    </div>
  );
}
```

---

## Architecture Patterns

**Backend Structure**:
```
apps/backend/
├── core/          # Core infrastructure (client, security, auth)
├── agents/        # Agent implementations (planner, coder, qa)
├── spec_agents/   # Spec creation agents
├── integrations/  # Graphiti memory, Linear, GitHub
├── prompts/       # Agent system prompts
└── cli/           # CLI utilities
```

**Frontend Structure**:
```
apps/frontend/src/
├── main/         # Electron main process (IPC handlers)
├── renderer/     # React UI (features, components)
├── preload/      # Context bridge
└── shared/       # Types, utilities, i18n
```

---

## Critical Rules

### Python
1. **ALWAYS** use `encoding="utf-8"` for text I/O (Windows compatibility)
2. Type hints required for function signatures
3. Docstrings for public APIs
4. Use pathlib.Path over os.path

### TypeScript
1. **ALWAYS** use i18n translation keys for user-facing text
2. Named exports preferred over default exports
3. Strict mode enforced - no `any` types
4. Functional components with hooks

### General
1. No trailing whitespace
2. End files with newline
3. Keep functions/components < 50 lines when possible
4. Test-driven development - if you can't test it, refactor it

---

## Anti-Patterns

❌ **Mutation**: Modifying data in place (use immutable updates)
❌ **Side effects in pure functions**: API calls, logging in pure functions
❌ **God modules**: Split into focused modules
❌ **Deep nesting**: Use early returns instead
❌ **Missing encoding**: Text I/O without `encoding="utf-8"` (Windows breakage)
❌ **Hardcoded UI strings**: User-facing text without i18n keys
❌ **Default exports**: Prefer named exports
❌ **Any types**: Use proper types or unknown

---

## Testing Requirements

Before submitting changes:
1. All existing tests must pass
2. New features should include tests
3. Bug fixes should include regression tests
4. Test coverage should not decrease significantly
5. Run pre-commit hooks locally first

---

## Platform Compatibility

**Critical**: This project supports Windows, macOS, and Linux.

- **Windows**: Text encoding MUST be `utf-8` (not cp1252 default)
- **Paths**: Use `pathlib.Path` (not `os.path`)
- **Line endings**: Auto-handled by git (LF in repo, CRLF on Windows)
- **Permissions**: Use platform abstractions from `core/platform/`

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
