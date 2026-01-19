# GitHub Copilot Instructions for EcoSort-AI

## Project Context

This is a GenAI waste classification application using:
- **Streamlit** for the frontend
- **Google Gemini 2.5 Flash** for AI classification
- **Azure** for cloud infrastructure
- **Python 3.11+** as the primary language

---

## Code Generation Rules

### Python Style
- Use Python 3.11+ features
- Always include type hints
- Follow PEP 8 conventions
- Use `async/await` for I/O operations
- Prefer f-strings over `.format()` or `%`

### Example Function Signature
```python
async def classify_waste(
    image: bytes,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.1
) -> ClassificationResult:
    """Classify waste from image using Gemini AI."""
    ...
```

---

## Import Preferences

```python
# Standard library
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any

# Third-party
import streamlit as st
from PIL import Image
import google.generativeai as genai

# Local
from app.utils.ai_engine import GeminiEngine
from app.utils.config import settings
```

---

## Error Handling Pattern

```python
from app.utils.exceptions import EcoSortError

try:
    result = await engine.classify(image)
except EcoSortError as e:
    logger.error(f"Classification error: {e}", exc_info=True)
    st.error(f"Unable to classify: {e.user_message}")
    return None
```

---

## Streamlit Patterns

### Page Configuration
```python
st.set_page_config(
    page_title="EcoSort-AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### Component Structure
```python
def render_classification_result(result: ClassificationResult) -> None:
    """Render classification result card."""
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(result.image, caption="Analyzed Item")
        with col2:
            st.metric("Category", result.category)
            st.progress(result.confidence / 100)
```

---

## Testing Patterns

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_gemini_response():
    return {
        "category": "recyclable",
        "confidence": 95,
        "material": "plastic"
    }

@patch("app.utils.ai_engine.genai")
async def test_classify_waste(mock_genai, mock_gemini_response):
    mock_genai.GenerativeModel.return_value.generate_content.return_value = (
        Mock(text=json.dumps(mock_gemini_response))
    )
    
    engine = GeminiEngine()
    result = await engine.classify(sample_image)
    
    assert result.category == "recyclable"
    assert result.confidence == 95
```

---

## Security Rules

- **NEVER** generate code that hardcodes API keys or secrets
- **ALWAYS** use environment variables via `os.getenv()` or settings
- **ALWAYS** validate and sanitize user inputs
- **PREFER** Azure Key Vault for production secrets

---

## Documentation Style

```python
def process_image(
    image_data: bytes,
    max_size: tuple[int, int] = (1024, 1024)
) -> Image.Image:
    """
    Process and resize image for classification.
    
    Args:
        image_data: Raw image bytes from upload
        max_size: Maximum dimensions (width, height)
        
    Returns:
        Processed PIL Image ready for classification
        
    Raises:
        ImageProcessingError: If image cannot be decoded
        
    Example:
        >>> img = process_image(uploaded_file.read())
        >>> result = await engine.classify(img)
    """
```

---

## Common Snippets

### Environment Loading
```python
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not configured")
```

### Logging Setup
```python
import logging

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
```

### Gemini Client Initialization
```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
```

---

## File Naming Conventions

- Python modules: `snake_case.py`
- Test files: `test_<module_name>.py`
- Components: `<component_name>.py`
- Constants: `UPPER_SNAKE_CASE`

---

## Avoid These Patterns

❌ `from typing import *`
❌ Bare `except:` clauses
❌ Magic numbers without constants
❌ `print()` statements (use `logger`)
❌ Synchronous API calls in async contexts
❌ Mutable default arguments
