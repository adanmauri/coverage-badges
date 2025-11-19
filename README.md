# Coverage Badges

Collection of coverage SVG badges to import in README.md files of GitHub projects.

## Description

This repository contains static coverage SVG badges that can be directly imported into README.md files of other projects, especially useful for private repositories where external services like shields.io cannot be used.

## Usage

### Option 1: Use pre-generated badges

This repository includes pre-generated badges for different coverage levels (0%, 5%, 10%, ..., 100%).

To use a badge in your README.md, add:

```markdown
![Coverage](https://raw.githubusercontent.com/YOUR_USERNAME/coverage-badges/main/badges/coverage-85.svg)
```

Replace:
- `YOUR_USERNAME` with your GitHub username
- `coverage-badges` with the name of this repository (if you renamed it)
- `85` with the coverage percentage you need

### Option 2: Generate a custom badge

If you need a badge with a specific percentage that is not pre-generated:

```bash
python src/generate_badge.py 87.5 -o my-badge.svg
```

This will generate a badge with 87.5% coverage in the file `my-badge.svg`.

### Option 3: Customize the label

You can change the badge label:

```bash
python src/generate_badge.py 90 -l "tests" -o tests-coverage.svg
```

## Colors

Badges change color according to the coverage percentage:

- 🔴 **Red** (`#e05d44`): 0-39%
- 🟡 **Yellow** (`#dfb317`): 40-59%
- 🟢 **Yellow-green** (`#a3c51c`): 60-79%
- 🟢 **Green** (`#4c1`): 80-100%

## Examples

### Basic badge
```markdown
![Coverage](https://raw.githubusercontent.com/YOUR_USERNAME/coverage-badges/main/badges/coverage-85.svg)
```

### Badge with link
```markdown
[![Coverage](https://raw.githubusercontent.com/YOUR_USERNAME/coverage-badges/main/badges/coverage-85.svg)](https://github.com/YOUR_USERNAME/coverage-badges)
```

## Generate all badges

To generate all pre-made badges (0% to 100% in 5% increments):

```bash
python src/generate_all_badges.py
```

## Project structure

```
coverage-badges/
├── badges/              # Generated SVG badges
│   ├── coverage-0.svg
│   ├── coverage-5.svg
│   ├── ...
│   └── coverage-100.svg
├── src/                 # Python source code
│   ├── __init__.py
│   ├── generate_badge.py    # Script to generate individual badges
│   └── generate_all_badges.py  # Script to generate all badges
└── README.md
```

## Notes

- Badges are static SVG files, so you will need to update them manually when your project's coverage changes.
- To automate the update, you can integrate the `src/generate_badge.py` script into your CI/CD pipeline.
- This project does not perform coverage analysis, it only generates SVG badges based on a provided value.
