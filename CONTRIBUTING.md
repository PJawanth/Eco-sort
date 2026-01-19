# Contributing to EcoSort-AI

First off, thank you for considering contributing to EcoSort-AI! 🌿

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)

---

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## Getting Started

### Issues

- Look for issues labeled `good first issue` or `help wanted`
- Comment on an issue before starting work to avoid duplicated effort
- Create a new issue if you find a bug or have a feature request

### Fork & Clone

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/EcoSort-AI.git
   cd EcoSort-AI
   ```

---

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- VS Code (recommended) with Python extension

### Environment Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env
```

---

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-camera-support`
- `fix/classification-accuracy`
- `docs/update-readme`

### Commit Messages

Follow conventional commits:
```
feat: add webcam capture support
fix: resolve image processing timeout
docs: update API documentation
test: add unit tests for ai_engine
```

---

## Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** for new features
3. **Run linters** before submitting:
   ```bash
   bandit -r app/
   safety check
   ```
4. **Update the README.md** if needed
5. **Request review** from maintainers

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with `main`

---

## Style Guidelines

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for all public functions

### Example

```python
def classify_waste(image: bytes, model: str = "gemini-2.5-flash") -> dict:
    """
    Classify waste from an image using the Gemini model.
    
    Args:
        image: Raw image bytes
        model: The Gemini model to use for classification
        
    Returns:
        Dictionary containing classification results and confidence scores
    """
    # Implementation
    pass
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_ai_logic.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names

---

## Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

Thank you for contributing! 🌍♻️
