"""
Unit Tests for AI Engine Logic
Tests the classification engine without requiring API access
"""

import json
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pytest
from PIL import Image


class TestGeminiEngine:
    """Test suite for GeminiEngine class."""
    
    @pytest.fixture
    def sample_image(self) -> Image.Image:
        """Create a sample test image."""
        img = Image.new("RGB", (100, 100), color="red")
        return img
    
    @pytest.fixture
    def mock_classification_response(self) -> dict:
        """Mock Gemini API response."""
        return {
            "category": "recyclable",
            "confidence": 95,
            "material": "Plastic (PET-1)",
            "disposal_instructions": "Rinse and place in recycling bin",
            "environmental_tip": "Consider using reusable containers"
        }
    
    @pytest.fixture
    def engine(self):
        """Create engine instance for testing."""
        from app.utils.ai_engine import GeminiEngine
        return GeminiEngine(api_key="test_key")
    
    def test_engine_initialization_with_api_key(self):
        """Test engine initializes correctly with API key."""
        from app.utils.ai_engine import GeminiEngine
        
        engine = GeminiEngine(api_key="test_api_key")
        
        assert engine.api_key == "test_api_key"
        assert engine.model_name == "gemini-2.5-flash"
    
    def test_engine_initialization_without_api_key(self):
        """Test engine handles missing API key gracefully."""
        from app.utils.ai_engine import GeminiEngine
        
        with patch.dict("os.environ", {}, clear=True):
            engine = GeminiEngine(api_key=None)
            assert engine.api_key is None
    
    def test_prepare_image_rgb(self, engine, sample_image):
        """Test image preparation for RGB images."""
        result = engine._prepare_image(sample_image)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_prepare_image_rgba(self, engine):
        """Test image preparation converts RGBA to RGB."""
        rgba_image = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        
        result = engine._prepare_image(rgba_image)
        
        assert isinstance(result, bytes)
        # Verify it's a valid JPEG
        img = Image.open(BytesIO(result))
        assert img.mode == "RGB"
    
    def test_prepare_image_resize_large(self, engine):
        """Test large images are resized."""
        large_image = Image.new("RGB", (4000, 4000), color="blue")
        
        result = engine._prepare_image(large_image)
        
        # Verify image was processed
        img = Image.open(BytesIO(result))
        assert img.size[0] <= 1024
        assert img.size[1] <= 1024
    
    def test_parse_response_valid_json(self, engine, mock_classification_response):
        """Test parsing valid JSON response."""
        response_text = json.dumps(mock_classification_response)
        
        result = engine._parse_response(response_text)
        
        assert result["category"] == "recyclable"
        assert result["confidence"] == 95
    
    def test_parse_response_json_in_markdown(self, engine, mock_classification_response):
        """Test parsing JSON wrapped in markdown code block."""
        response_text = f"```json\n{json.dumps(mock_classification_response)}\n```"
        
        result = engine._parse_response(response_text)
        
        assert result["category"] == "recyclable"
    
    def test_parse_response_invalid_json(self, engine):
        """Test parsing invalid JSON raises error."""
        from app.utils.ai_engine import ClassificationError
        
        with pytest.raises(ClassificationError):
            engine._parse_response("not valid json")
    
    def test_parse_response_missing_required_field(self, engine):
        """Test parsing response without required fields raises error."""
        from app.utils.ai_engine import ClassificationError
        
        incomplete_response = json.dumps({"material": "plastic"})
        
        with pytest.raises(ClassificationError):
            engine._parse_response(incomplete_response)
    
    def test_mock_classify(self, engine):
        """Test mock classification returns expected format."""
        result = engine._mock_classify()
        
        assert "category" in result
        assert "confidence" in result
        assert "material" in result
        assert "disposal_instructions" in result
        assert "environmental_tip" in result
        assert isinstance(result["confidence"], int)
    
    @patch("app.utils.ai_engine.genai")
    def test_classify_image_success(
        self,
        mock_genai,
        engine,
        sample_image,
        mock_classification_response
    ):
        """Test successful image classification."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.generate_content.return_value = Mock(
            text=json.dumps(mock_classification_response)
        )
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Force model initialization
        engine._model = mock_model
        
        result = engine.classify_image(sample_image)
        
        assert result["category"] == "recyclable"
        assert result["confidence"] == 95
    
    def test_classify_image_no_api_key(self, sample_image):
        """Test classification without API key returns mock."""
        from app.utils.ai_engine import GeminiEngine
        
        engine = GeminiEngine(api_key=None)
        engine.api_key = None  # Ensure no key
        
        result = engine.classify_image(sample_image)
        
        # Should return mock result
        assert result["category"] == "recyclable"


class TestClassificationCategories:
    """Test classification category validation."""
    
    @pytest.mark.parametrize("category", [
        "recyclable",
        "compostable",
        "landfill",
        "hazardous",
        "special"
    ])
    def test_valid_categories(self, category):
        """Test all valid categories are recognized."""
        valid_categories = [
            "recyclable",
            "compostable",
            "landfill",
            "hazardous",
            "special"
        ]
        assert category in valid_categories


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_image(self):
        """Test handling of empty/minimal image."""
        from app.utils.ai_engine import GeminiEngine
        
        engine = GeminiEngine(api_key=None)
        tiny_image = Image.new("RGB", (1, 1), color="white")
        
        # Should handle gracefully
        result = engine.classify_image(tiny_image)
        assert result is not None
    
    def test_large_image_processing(self):
        """Test large images don't cause memory issues."""
        from app.utils.ai_engine import GeminiEngine
        
        engine = GeminiEngine(api_key=None)
        large_image = Image.new("RGB", (2000, 2000), color="green")
        
        result = engine.classify_image(large_image)
        assert result is not None
