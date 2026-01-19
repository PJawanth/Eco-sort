# EcoSort-AI Agent Persona

This file defines the project context and persona for AI coding agents working on this repository.

---

## Project Overview

**EcoSort-AI** is a GenAI-powered waste classification application that helps users identify and properly dispose of waste items. The application uses Google Gemini 2.5 Flash for image analysis and classification.

---

## Tech Stack

- **Frontend**: Streamlit 1.40+
- **AI/ML**: Google Gemini 2.5 Flash (multimodal)
- **Cloud**: Microsoft Azure (Static Web Apps, Key Vault)
- **Infrastructure**: Azure Bicep
- **CI/CD**: GitHub Actions
- **Language**: Python 3.11+

---

## Project Structure

```
EcoSort-AI/
├── app/                    # Main application code
│   ├── main.py            # Streamlit entry point
│   ├── utils/             # Utility modules
│   │   └── ai_engine.py   # Gemini API integration
│   └── components/        # UI components
├── infra/                 # Azure infrastructure (Bicep)
├── tests/                 # Unit and integration tests
├── .github/               # GitHub configuration
│   ├── workflows/         # CI/CD pipelines
│   └── agents.md          # This file
└── docs/                  # Documentation
```

---

## Coding Standards

### Python
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for all public functions
- Maximum line length: 100 characters
- Use `black` for formatting, `isort` for imports

### Security
- Never hardcode secrets or API keys
- Use environment variables or Azure Key Vault
- Validate all user inputs
- Sanitize file uploads (images)

### Testing
- Write unit tests for all business logic
- Maintain >80% code coverage
- Use pytest as the testing framework
- Mock external API calls in tests

---

## Key Patterns

### AI Engine Usage

```python
from app.utils.ai_engine import GeminiEngine

engine = GeminiEngine()
result = engine.classify_image(image_bytes)
```

### Error Handling

```python
from app.utils.exceptions import ClassificationError

try:
    result = engine.classify_image(image)
except ClassificationError as e:
    logger.error(f"Classification failed: {e}")
    return {"error": str(e)}
```

---

## Common Tasks

### Adding a New Classification Category
1. Update `PROMPTS.md` with new category
2. Add category to `ai_engine.py` response parser
3. Update UI components to display new category
4. Add tests for new category

### Adding a New UI Component
1. Create component in `app/components/`
2. Import in `main.py`
3. Add styling consistent with existing components
4. Test responsiveness

---

## Do's and Don'ts

### Do
- ✅ Use async patterns for API calls
- ✅ Cache classification results when appropriate
- ✅ Log all errors with context
- ✅ Write tests for new features
- ✅ Update documentation

### Don't
- ❌ Commit `.env` files
- ❌ Use deprecated API patterns
- ❌ Skip error handling
- ❌ Hardcode configuration values
- ❌ Ignore security warnings

---

## Dependencies

Key dependencies to be aware of:
- `streamlit` - UI framework
- `google-generativeai` - Gemini SDK
- `azure-identity` - Azure authentication
- `azure-keyvault-secrets` - Key Vault access
- `pillow` - Image processing
- `python-dotenv` - Environment management

---

## Environment Variables

Required for development:
- `GOOGLE_API_KEY` - Gemini API key
- `APP_ENV` - Environment (dev/staging/prod)

Optional:
- `AZURE_KEY_VAULT_URL` - For production secrets
- `LOG_LEVEL` - Logging verbosity

---

## Getting Help

- Check `README.md` for setup instructions
- Review `CONTRIBUTING.md` for contribution guidelines
- See `PROMPTS.md` for AI prompt documentation
- Refer to `SECURITY.md` for security policies
