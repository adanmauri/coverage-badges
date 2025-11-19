# Contributing to Coverage Badges

Thank you for your interest in contributing to Coverage Badges! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/adanmauri/coverage-badges.git`
3. Set up the development environment:

   ```bash
   pipenv install --dev
   pipenv shell
   ```

## Reporting Issues

- Before opening a new issue, search for existing issues to avoid duplicates
- Include minimal examples when reporting bugs
- If reporting a bug, try to reproduce it on the latest development version
- Include relevant information:
  - Python version
  - Operating system
  - Steps to reproduce
  - Expected vs actual behavior

## Contributing Code

### For New Contributors

If you're new to the project and would like guidance on where to start, feel free to:
- Open an issue asking for suggestions
- Comment on existing issues to express interest
- Start with small improvements like documentation or bug fixes

### Development Workflow

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   or for bug fixes:
   ```bash
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes following the style guidelines below

3. Format and lint your code:
   ```bash
   black src/
   isort src/
   pylint src/
   flake8 src/
   mypy src/
   ruff check src/
   pyright src/
   bandit -r src/
   ```

4. Write or update tests if needed (see Testing section)

5. Commit your changes with descriptive messages:
   ```bash
   git commit -m "Add feature: description of what you did"
   ```

6. Push to your fork and open a Pull Request

### Pull Request Guidelines

- **All PRs should be opened against the `main` branch**
- Use descriptive PR titles and descriptions
- Aim for atomic commits (one logical change per commit)
- If your PR introduces breaking changes, prefix the title with `[BREAKING]`
- Keep PRs focused - avoid mixing unrelated changes
- If a PR is not ready for review, mark it as a Draft
- Update documentation if you add or change functionality

### Git Best Practices

- Avoid working directly on the `main` branch of your fork
- Use descriptive commit messages:
  - Good: `Add validation for coverage percentage in BadgeGenerator`
  - Bad: `fix stuff`
- Use `git add -p` or `git add -i` to stage changes selectively
- If conflicts arise, prefer `git rebase` over `git merge` to keep history clean
- When linking to code in discussions, use GitHub's permalink feature (press `y` while viewing code)

## Style Guidelines

This project follows strict style guidelines to ensure consistency. Please read the `.cursorrules` file for complete details.

### Python Version

- **Python 3.10+ syntax is required**
- The project uses Python 3.14 (as specified in `Pipfile`)

### Type Hints

- **All function and method signatures must include type hints**
- Use built-in types instead of `typing` module when possible:
  - Use `dict[str, int]` instead of `Dict[str, int]`
  - Use `list[str]` instead of `List[str]`
  - Use `tuple[int, str]` instead of `Tuple[int, str]`
  - Use `set[int]` instead of `Set[int]`
- Use union syntax: `type | None` instead of `Optional[type]`
- Use `type1 | type2` instead of `Union[type1, type2]`
- Only import from `typing` when necessary (e.g., `Any`, `IO`, `BinaryIO`, `TextIO`, `cast`)

**Example:**
```python
# ✅ Correct
def process_data(data: dict[str, int]) -> list[str] | None:
    ...

# ❌ Incorrect
from typing import Dict, List, Optional
def process_data(data: Dict[str, int]) -> Optional[List[str]]:
    ...
```

### Code Formatting

- **Follow PEP 8 guidelines**
- **Use Black for formatting** (line length: 100 characters)
- **Use isort for import sorting** (Black profile)
- Run formatters before committing:
  ```bash
  black src/
  isort src/
  ```

### Docstrings

All docstrings must follow this format:

**Module-level docstrings:**
```python
"""Brief description of the module.

More detailed description that explains what the module does,
its purpose, and key concepts. Can span multiple lines to
provide comprehensive context about the module's functionality.

Additional paragraphs can be added to explain more complex
aspects or usage patterns.
"""
```

**Class docstrings:**
```python
class MyClass:
    """Brief description of the class.

    More detailed description explaining the class purpose,
    its main responsibilities, and how it fits into the
    larger system architecture.

    Additional context about usage patterns or important
    design decisions.
    """
```

**Method/Function docstrings:**
```python
def my_method(self, param1: str, param2: int | None = None) -> dict[str, Any]:
    """Brief description of what the method does."""
```

**Key guidelines:**
- Start with a brief one-line summary
- Follow with a blank line
- Add detailed description in paragraphs (for modules and classes)
- Be descriptive and clear
- Use proper capitalization and punctuation
- Document all public methods, classes, and modules

### Imports

- Group imports in this order:
  1. Standard library imports
  2. Third-party imports
  3. Local imports (from `src.`)
- Use absolute imports from `src.` prefix
- Sort imports with isort (Black profile)

**Example:**
```python
import argparse
from pathlib import Path

from src import BadgeGenerator
```

### Error Handling

- Use specific exception types when possible
- Include descriptive error messages in English
- Use `ValueError` for invalid input
- Use `FileNotFoundError` for missing files
- Use `NotImplementedError` for abstract methods

### Logging

- Use standard `logging` module if logging is needed
- **Do not use emojis in log messages**
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Include context in log messages

### Code Style

- Use descriptive variable and function names
- Prefer explicit over implicit code
- Don't leave trailing whitespace
- Maximum line length: 100 characters (enforced by Black)
- Use 4 spaces for indentation (no tabs)

### Language Requirements

- **All comments and messages must be in English**
- **Logs must not use emojis** - Use plain text messages only
- **Error messages and user-facing text must be in English**

## Testing

- Write tests for all public functions and classes
- Use pytest for testing
- Test files should be in `tests/` directory
- Test file names should start with `test_`
- Use descriptive test function names starting with `test_`

**Example:**
```python
def test_badge_generator_get_color_high_coverage():
    """Test that high coverage returns green color."""
    generator = BadgeGenerator()
    assert generator.get_color(85.0) == "#4c1"
```

Run tests with:
```bash
pytest
```

## Dependency Management

- **Use Pipenv for dependency management**
- **Production dependencies (`[packages]`)**: Always use fixed versions (e.g., `pandas = "==2.3.3"`)
- **Development dependencies (`[dev-packages]`)**: Use `*` for flexible versions (e.g., `pytest = "*"`)
- This ensures reproducible production builds while allowing flexibility for development tools

When adding new dependencies:
1. Add to `Pipfile` with appropriate version constraints
2. Run `pipenv install` or `pipenv install --dev` as needed
3. Commit both `Pipfile` and `Pipfile.lock`

## Code Review Process

1. All PRs require at least one approval before merging
2. Maintainers will review code for:
   - Adherence to style guidelines
   - Code quality and correctness
   - Test coverage
   - Documentation updates
3. Address review comments promptly
4. Keep discussions focused and constructive

## Questions?

If you have questions or need help, feel free to:
- Open an issue with the `question` label
- Comment on existing issues or PRs
- Reach out to maintainers

Thank you for contributing to Coverage Badges!
