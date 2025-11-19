# Coverage Badges

<p align="center">
    <em>Collection of coverage SVG badges to import in README.md files of GitHub projects.</em>
</p>

<p align="center">
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/code-quality.yaml"><img src="https://github.com/adanmauri/coverage-badges/actions/workflows/code-quality.yaml/badge.svg" alt="Code Quality"></a>
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/tests.yaml"><img src="https://github.com/adanmauri/coverage-badges/actions/workflows/tests.yaml/badge.svg" alt="Tests & Coverage"></a>
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/security.yaml"><img src="https://github.com/adanmauri/coverage-badges/actions/workflows/security.yaml/badge.svg" alt="Security"></a>
</p>
<p align="center">
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/tests.yaml"><img src="https://raw.githubusercontent.com/adanmauri/coverage-badges/refs/heads/main/coverage.svg" alt="Coverage"></a>
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/todo-to-issue.yaml"><img src="https://github.com/adanmauri/coverage-badges/actions/workflows/todo-to-issue.yaml/badge.svg" alt="Todo to Issue"></a>
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/dependabot/dependabot-updates"><img src="https://github.com/adanmauri/coverage-badges/actions/workflows/dependabot/dependabot-updates/badge.svg" alt="Dependabot Updates"></a>
</p>

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Colors](#colors)
- [Examples](#examples)
- [Architecture](#architecture)
- [Testing](#testing)
- [Quality Assurance](#quality-assurance)
- [Contributing](#contributing)
- [License](#license)
- [TODO](#todo)

## Overview

This repository provides static coverage SVG badges that can be directly imported into README.md files of other projects. Especially useful for private repositories where external services like shields.io cannot be used. The badges are generated with GitHub-style design, including rounded corners, gradients, and the Pytest icon.

### Why Use This?

- ✅ **Private Repositories** - Works with private GitHub repositories where shields.io cannot access coverage data
- ✅ **No External Dependencies** - Static SVG files that work without external services
- ✅ **GitHub-style Design** - Professional appearance matching GitHub's native badges
- ✅ **Easy Integration** - Simple URL-based import in any README.md
- ✅ **Customizable** - Generate badges with any coverage percentage or custom labels

## Quick Start

### Prerequisites

- Python 3.14
- Pipenv for dependency management

### Installation

```bash
# Install all dependencies (including dev dependencies)
pipenv install --dev

# Or install only production dependencies
pipenv install
```

## Usage

### Option 1: Use Pre-generated Badges

This repository includes pre-generated badges for different coverage levels (0%, 5%, 10%, ..., 100%).

To use a badge in your README.md, add:

```markdown
![Coverage](https://raw.githubusercontent.com/adanmauri/coverage-badges/main/badges/coverage-85.svg)
```

**Note:** If you fork this repository, replace `adanmauri` with your GitHub username and `coverage-badges` with your repository name (if you renamed it). Replace `85` with the coverage percentage you need.

### Option 2: Generate a Custom Badge

If you need a badge with a specific percentage that is not pre-generated:

```bash
python -m src.generate_badge 87.5 -o my-badge.svg
```

This will generate a badge with 87.5% coverage in the file `my-badge.svg`.

### Option 3: Customize the Label

You can change the badge label:

```bash
python -m src.generate_badge 90 -l "tests" -o tests-coverage.svg
```

## Project Structure

```text
coverage-badges/
├── badges/              # Generated SVG badges
│   ├── coverage-0.svg
│   ├── coverage-5.svg
│   ├── ...
│   └── coverage-100.svg
├── src/                 # Python source code
│   ├── __init__.py
│   ├── badge_generator.py    # BadgeGenerator class
│   ├── generate_badge.py     # Script to generate individual badges
│   └── generate_all_badges.py  # Script to generate all badges
├── tests/               # Test files
│   ├── __init__.py
│   └── test_badge_generator.py
├── .vscode/             # VS Code workspace configuration
│   ├── extensions.json  # Recommended extensions
│   ├── settings.json    # Workspace settings
│   └── launch.json      # Debug configurations
├── .github/              # GitHub workflows and templates
│   └── workflows/        # CI/CD workflows
├── CONTRIBUTING.md       # Contribution guidelines
├── LICENSE               # MIT License
├── Pipfile               # Python dependencies (pipenv)
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Colors

Badges change color according to the coverage percentage:

- 🔴 **Red** (`#e05d44`): 0-39%
- 🟡 **Yellow** (`#dfb317`): 40-59%
- 🟢 **Yellow-green** (`#a3c51c`): 60-79%
- 🟢 **Green** (`#4c1`): 80-100%

## Examples

### Basic Badge

```markdown
![Coverage](https://raw.githubusercontent.com/adanmauri/coverage-badges/main/badges/coverage-85.svg)
```

### Badge with Link

```markdown
[![Coverage](https://raw.githubusercontent.com/adanmauri/coverage-badges/main/badges/coverage-85.svg)](https://github.com/adanmauri/coverage-badges)
```

## Generate All Badges

To generate all pre-made badges (0% to 100% in 5% increments):

```bash
python -m src.generate_all_badges
```

## Architecture

### Core Components

1. **BadgeGenerator** - Main class for generating coverage SVG badges
2. **Color System** - Automatic color selection based on coverage percentage
3. **SVG Generation** - GitHub-style badges with gradients and rounded corners

### BadgeGenerator Class

The `BadgeGenerator` class provides methods to generate SVG badges:

```python
from src import BadgeGenerator

# Initialize generator
generator = BadgeGenerator()

# Generate SVG content
svg = generator.generate_svg(85.0, label="Coverage")

# Save badge to file
from pathlib import Path
generator.save_badge(85.0, Path("badge.svg"), label="Coverage")
```

### Key Features

- ✅ **GitHub-style Design** - Rounded corners, gradients, and professional appearance
- ✅ **Pytest Icon** - Includes Pytest icon on the left side of badges
- ✅ **Automatic Color Selection** - Colors change based on coverage percentage
- ✅ **Customizable Labels** - Support for custom badge labels
- ✅ **Type Safety** - Full type hints using Python 3.10+ syntax
- ✅ **Static SVG Files** - No external dependencies required for display

## Testing

The project uses pytest for testing. Run tests from the `tests/` directory:

```bash
# Install dependencies (including pytest)
pipenv install --dev

# Run all tests
pipenv run pytest tests/

# Run tests with verbose output
pipenv run pytest tests/ -v

# Run specific test file
pipenv run pytest tests/test_badge_generator.py -v

# Run tests with coverage report
pipenv run pytest tests/ --cov=src --cov-report=term-missing

# Run tests with HTML coverage report
pipenv run pytest tests/ --cov=src --cov-report=html
```

## Quality Assurance

### Code Quality

- **Python 3.14** - Modern Python syntax with built-in type hints (`dict`, `list`, `| None` instead of `typing` module)
- **Type Hints** - Full type annotations throughout the codebase using Python 3.10+ syntax
- **Linting** - Pylint, Flake8, and Ruff for code quality checks
- **Formatting** - Black for consistent code formatting (line length: 100)
- **Security** - Bandit and Trivy for security vulnerability scanning
- **Type Checking** - mypy, pyright, and ruff for static type analysis
- **Testing** - pytest for comprehensive test coverage
- **Documentation** - Clear, concise docstrings following project standards

### CI/CD

The project includes GitHub Actions workflows for:

- **Code Quality** - Automated linting and formatting checks via MegaLinter
- **Tests & Coverage** - Automated test execution with coverage reporting
- **Security** - Security vulnerability scanning with Trivy and Bandit
- **Todo Management** - Automatic issue creation from TODO comments

### Development Tools

- **Pipenv** - Dependency management
- **Pre-commit hooks** - Automated code quality checks (via MegaLinter)
- **VS Code integration** - Pre-configured settings, extensions, and debug configurations
- **Cursor Rules** - Project-specific coding standards defined in `.cursorrules`

#### VS Code Setup

The project includes pre-configured VS Code settings in `.vscode/`:

- **Recommended Extensions** (`.vscode/extensions.json`) - Automatically suggests essential extensions
- **Workspace Settings** (`.vscode/settings.json`) - Configured for Python development with Pipenv
- **Debug Configurations** (`.vscode/launch.json`) - Ready-to-use debug configurations for badge generation scripts

### Code Standards

The project follows strict coding standards defined in `.cursorrules`:

- All code, comments, and documentation in English
- Python 3.10+ syntax with modern type hints
- Simplified docstring format (brief descriptions)
- No emojis in logs or messages
- Consistent code style with Black and isort

## Notes

- Badges are static SVG files, so you will need to update them manually when your project's coverage changes.
- To automate the update, you can integrate the `python -m src.generate_badge` command into your CI/CD pipeline.
- This project does not perform coverage analysis, it only generates SVG badges based on a provided value.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## TODO

See [TODO.md](TODO.md) for planned features and improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
