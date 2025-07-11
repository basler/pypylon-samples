# VS Code Configuration

Minimal VS Code configuration for the pypylon-samples project.

## Files

- **`settings.json`** - Automatically remove trailing whitespace and Ruff formatting
- **`extensions.json`** - Only Python and Ruff extensions
- **`launch.json`** - Start pytest and Jupyter Notebook

## Features

- **Trailing whitespace** is automatically removed on save
- **Final newline** is automatically inserted at end of file
- **Ruff formatting** on save for Python files

## Extensions

- **ms-python.python** - Python support
- **charliermarsh.ruff** - Code formatting

## Debug Configurations (F5)

- **Python: pytest** - Run all tests
- **Python: Jupyter Notebook** - Start Jupyter Notebook server
