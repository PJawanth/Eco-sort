"""
Pytest Configuration and Fixtures
Shared fixtures for EcoSort-AI test suite
"""

import os
import sys
from pathlib import Path

import pytest
from PIL import Image

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))


@pytest.fixture(scope="session")
def test_images_dir(tmp_path_factory) -> Path:
    """Create temporary directory for test images."""
    return tmp_path_factory.mktemp("images")


@pytest.fixture
def sample_rgb_image() -> Image.Image:
    """Create a sample RGB test image."""
    return Image.new("RGB", (200, 200), color="blue")


@pytest.fixture
def sample_rgba_image() -> Image.Image:
    """Create a sample RGBA test image."""
    return Image.new("RGBA", (200, 200), color=(255, 0, 0, 128))


@pytest.fixture
def sample_grayscale_image() -> Image.Image:
    """Create a sample grayscale test image."""
    return Image.new("L", (200, 200), color=128)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    # Tests should not rely on a real API key; use a dummy value
    monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def classification_result() -> dict:
    """Standard classification result for testing."""
    return {
        "category": "recyclable",
        "confidence": 90,
        "material": "Aluminum",
        "disposal_instructions": "Rinse and place in recycling bin",
        "environmental_tip": "Recycling one can saves enough energy for 3 hours of TV"
    }


@pytest.fixture
def hazardous_result() -> dict:
    """Hazardous classification result for testing."""
    return {
        "category": "hazardous",
        "confidence": 95,
        "material": "Lithium Battery",
        "disposal_instructions": "Take to designated battery recycling center",
        "environmental_tip": "Never put batteries in regular trash - they can cause fires"
    }
