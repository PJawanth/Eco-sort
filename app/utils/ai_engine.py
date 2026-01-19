"""
AI Engine Module - Google Gemini Integration
Handles waste classification using Gemini 2.5 Flash
"""

import json
import logging
import os
import random
from io import BytesIO
from typing import Any

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Module-level placeholder for google.generativeai so tests can patch it
genai = None


class ClassificationError(Exception):
    """Custom exception for classification errors."""
    
    def __init__(self, message: str, user_message: str | None = None):
        super().__init__(message)
        self.user_message = user_message or message


class GeminiEngine:
    """
    Gemini AI Engine for waste classification.
    
    This class handles all interactions with the Google Gemini API
    for classifying waste items from images.
    """
    
    # Classification system prompt
    SYSTEM_PROMPT = """
    You are EcoSort-AI, an expert waste classification assistant.
    Analyze the provided image and classify the waste item.
    
    Categories:
    - recyclable: Paper, cardboard, glass, metal, plastics (1, 2, 5)
    - compostable: Food waste, yard waste, compostable packaging
    - landfill: Non-recyclable plastics, mixed materials
    - hazardous: Batteries, electronics, chemicals
    - special: Large items, textiles, construction materials
    
    Respond ONLY with valid JSON in this exact format:
    {
        "category": "category_name",
        "confidence": 85,
        "material": "primary material",
        "disposal_instructions": "specific disposal instructions",
        "environmental_tip": "helpful sustainability tip"
    }
    """
    
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash"):
        """
        Initialize the Gemini Engine.
        
        Args:
            api_key: Google API key. If not provided, reads from environment.
            model: Gemini model name to use. Default is gemini-2.0-flash.
            
        Raises:
            ValueError: If API key is not available.
        """
        # Prefer injected api_key (from CI/CD secrets). Fall back to env for local dev.
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model
        self._model = None
        self._last_request_time = 0
        self._min_request_interval = 2.0  # Minimum seconds between requests
        self._quota_exceeded = False
        self._quota_reset_time = 0
        
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not configured - using mock mode")

    @property
    def is_quota_exceeded(self) -> bool:
        """Check if quota is currently exceeded."""
        import time
        if self._quota_exceeded and time.time() >= self._quota_reset_time:
            self._quota_exceeded = False
        return self._quota_exceeded

    @property
    def quota_wait_time(self) -> int:
        """Get remaining wait time in seconds if quota is exceeded."""
        import time
        if self._quota_exceeded:
            return max(0, int(self._quota_reset_time - time.time()))
        return 0
    
    def _get_model(self) -> Any:
        """
        Lazy initialization of the Gemini model.
        
        Returns:
            Configured Gemini GenerativeModel instance.
        """
        global genai
        if self._model is None:
            # Use module-level `genai` if tests or CI injected a mock.
            if genai is None:
                try:
                    import google.generativeai as _genai

                    genai = _genai
                except ImportError:
                    logger.error("google-generativeai package not installed and genai not provided")
                    raise ClassificationError(
                        "Gemini SDK not installed",
                        "AI service is not configured properly"
                    )

            # Configure and create model instance
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
            )
            logger.info(f"Initialized Gemini model: {self.model_name}")
        
        return self._model
    
    def _prepare_image(self, image: Image.Image) -> bytes:
        """
        Prepare image for API submission.
        
        Args:
            image: PIL Image to process.
            
        Returns:
            Image bytes in JPEG format.
        """
        # Convert to RGB if necessary
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Resize if too large
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to bytes
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def _parse_response(self, response_text: str) -> dict:
        """
        Parse the Gemini response into structured data.
        
        Args:
            response_text: Raw response from Gemini.
            
        Returns:
            Parsed classification result.
            
        Raises:
            ClassificationError: If response cannot be parsed.
        """
        try:
            # Try to extract JSON from response
            text = response_text.strip()
            
            # Handle markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            result = json.loads(text)
            
            # Validate required fields
            required_fields = ["category", "confidence"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse response: {e}")
            logger.debug(f"Raw response: {response_text}")
            raise ClassificationError(
                f"Failed to parse AI response: {e}",
                "Unable to understand AI response. Please try again."
            )
    
    def classify_image(self, image: Image.Image) -> dict:
        """
        Classify a waste item from an image.
        
        Args:
            image: PIL Image of the waste item.
            
        Returns:
            Classification result dictionary containing:
                - category: Classification category
                - confidence: Confidence score (0-100)
                - material: Detected material type
                - disposal_instructions: How to dispose of the item
                - environmental_tip: Sustainability tip
                
        Raises:
            ClassificationError: If classification fails.
        """
        logger.info("Starting image classification")
        
        # Mock mode for development without API key
        if not self.api_key:
            logger.warning("Using mock classification (no API key)")
            return self._mock_classify(image)
        
        try:
            model = self._get_model()
            image_bytes = self._prepare_image(image)
            
            # Create image part for multimodal input
            import google.generativeai as genai
            
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            
            # Generate classification
            response = model.generate_content([
                self.SYSTEM_PROMPT,
                image_part
            ])
            
            if not response.text:
                raise ClassificationError(
                    "Empty response from Gemini",
                    "AI returned no classification. Please try again."
                )
            
            result = self._parse_response(response.text)
            logger.info(f"Classification complete: {result.get('category')}")
            
            return result
            
        except ClassificationError:
            raise
        except Exception as e:
            logger.error(f"Classification failed: {e}", exc_info=True)
            raise ClassificationError(
                f"Classification failed: {e}",
                "Unable to classify image. Please try again later."
            )
    
    def _mock_classify(self, image: Image.Image | None = None) -> dict:
        """
        Return mock classification for development.
        Uses image characteristics to vary the response.
        
        Args:
            image: Optional PIL Image to base mock response on.
            
        Returns:
            Mock classification result.
        """
        import random
        
        # Use image size as a seed for varied responses
        if image:
            seed = (image.size[0] * image.size[1]) % 5
        else:
            seed = random.randint(0, 4)
        
        mock_responses = [
            {
                "category": "recyclable",
                "confidence": 92,
                "material": "Plastic (PET-1)",
                "disposal_instructions": "Rinse the container and remove the cap. Place in your recycling bin.",
                "environmental_tip": "Consider using a reusable water bottle to reduce plastic waste!"
            },
            {
                "category": "compostable",
                "confidence": 88,
                "material": "Organic Food Waste",
                "disposal_instructions": "Place in your compost bin or green waste container. Avoid adding meat or dairy to home compost.",
                "environmental_tip": "Composting reduces methane emissions from landfills and creates nutrient-rich soil!"
            },
            {
                "category": "landfill",
                "confidence": 75,
                "material": "Mixed Materials",
                "disposal_instructions": "This item contains mixed materials that cannot be easily separated. Place in general waste.",
                "environmental_tip": "Try to avoid products with mixed, non-separable materials when possible."
            },
            {
                "category": "hazardous",
                "confidence": 95,
                "material": "Electronic Waste",
                "disposal_instructions": "Do NOT place in regular trash. Take to an e-waste collection center or retailer take-back program.",
                "environmental_tip": "E-waste contains valuable materials that can be recovered and reused!"
            },
            {
                "category": "recyclable",
                "confidence": 90,
                "material": "Glass Bottle",
                "disposal_instructions": "Rinse and remove any caps or lids. Place in glass recycling bin.",
                "environmental_tip": "Glass can be recycled endlessly without losing quality!"
            }
        ]
        
        return mock_responses[seed]

    # Object Detection Prompt
    DETECTION_PROMPT = """
    You are an expert waste detection system. Analyze this image and detect ALL objects visible that could be classified as waste, recyclable items, or everyday objects that would eventually become waste.
    
    IMPORTANT: Be inclusive - detect common household items like:
    - Plastic bottles, containers, bags
    - Paper, cardboard, newspapers
    - Food items, fruit peels, food scraps
    - Glass bottles and jars
    - Metal cans, aluminum foil
    - Electronics, batteries, cables
    - Cups, plates, utensils (paper or plastic)
    - Any other objects in view
    
    For EACH object detected, provide:
    - A bounding box as [ymin, xmin, ymax, xmax] normalized to 0-1000 scale (where 0 is top/left and 1000 is bottom/right)
    - The object label/name
    - The waste category (recyclable, compostable, landfill, hazardous, special)
    - A confidence score (0-100)
    
    Respond ONLY with valid JSON in this exact format:
    {
        "detections": [
            {
                "box": [ymin, xmin, ymax, xmax],
                "label": "object name",
                "category": "waste category",
                "confidence": 85
            }
        ]
    }
    
    If no waste items are detected, return: {"detections": []}
    """

    def _check_rate_limit(self) -> bool:
        """
        Check if we should wait before making another request.
        
        Returns:
            True if OK to proceed, False if should wait.
        """
        import time
        current_time = time.time()
        
        # Check if quota is exceeded
        if self._quota_exceeded:
            if current_time < self._quota_reset_time:
                wait_time = int(self._quota_reset_time - current_time)
                logger.warning(f"Quota exceeded. Wait {wait_time}s before retrying.")
                return False
            else:
                self._quota_exceeded = False
        
        # Rate limiting between requests
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            return False
        
        self._last_request_time = current_time
        return True

    def detect_objects(self, image: Image.Image) -> tuple[Image.Image, list[dict]]:
        """
        Detect and annotate waste objects in an image.
        
        Args:
            image: PIL Image to analyze.
            
        Returns:
            Tuple of (annotated image, list of detections).
        """
        logger.info("Starting object detection")
        
        # Mock mode for development
        if not self.api_key:
            logger.warning("Using mock detection (no API key)")
            return self._mock_detect(image)
        
        # Check rate limiting
        if not self._check_rate_limit():
            logger.warning("Rate limited - returning cached or empty result")
            return image, []
        
        try:
            model = self._get_model()
            image_bytes = self._prepare_image(image)
            
            import google.generativeai as genai
            
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            
            response = model.generate_content([
                self.DETECTION_PROMPT,
                image_part
            ])
            
            if not response.text:
                logger.warning("Empty response from API")
                return image, []
            
            logger.info(f"API response received: {response.text[:200]}...")
            
            # Parse detection-specific response
            detections = self._parse_detection_response(response.text)
            logger.info(f"Parsed {len(detections)} detections")
            
            annotated_image = self._draw_detections(image.copy(), detections)
            
            return annotated_image, detections
            
        except Exception as e:
            error_str = str(e)
            # Check for quota exceeded error
            if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
                import time
                self._quota_exceeded = True
                # Set reset time to 60 seconds from now
                self._quota_reset_time = time.time() + 60
                logger.error(f"API quota exceeded. Will retry after 60 seconds.")
            else:
                logger.error(f"Detection failed: {e}", exc_info=True)
            return image, []

    def _parse_detection_response(self, response_text: str) -> list[dict]:
        """
        Parse the detection response from Gemini.
        
        Args:
            response_text: Raw response from Gemini.
            
        Returns:
            List of detection dictionaries.
        """
        try:
            text = response_text.strip()
            
            # Handle markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            result = json.loads(text.strip())
            
            # Handle both formats
            if isinstance(result, dict):
                return result.get("detections", [])
            elif isinstance(result, list):
                return result
            else:
                return []
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse detection response: {e}")
            logger.debug(f"Raw response: {response_text}")
            return []

    def _draw_detections(
        self, 
        image: Image.Image, 
        detections: list[dict]
    ) -> Image.Image:
        """
        Draw bounding boxes and labels on image.
        
        Args:
            image: PIL Image to annotate.
            detections: List of detection dictionaries.
            
        Returns:
            Annotated PIL Image.
        """
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Category colors (RGB)
        category_colors = {
            "recyclable": (0, 200, 100),
            "compostable": (139, 90, 43),
            "landfill": (100, 100, 100),
            "hazardous": (220, 50, 50),
            "special": (220, 180, 50),
            "unknown": (150, 150, 150)
        }
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        for det in detections:
            box = det.get("box", [])
            if len(box) != 4:
                continue
                
            # Convert normalized coordinates (0-1000) to pixel coordinates
            ymin, xmin, ymax, xmax = box
            x1 = int((xmin / 1000) * width)
            y1 = int((ymin / 1000) * height)
            x2 = int((xmax / 1000) * width)
            y2 = int((ymax / 1000) * height)
            
            category = det.get("category", "unknown").lower()
            color = category_colors.get(category, category_colors["unknown"])
            label = det.get("label", "Object")
            
            # Draw box
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            # Draw label background
            label_text = f"{label}"
            bbox = draw.textbbox((x1, y1 - 20), label_text, font=font)
            draw.rectangle(bbox, fill=color)
            draw.text((x1, y1 - 20), label_text, fill="white", font=font)
        
        return image

    def _mock_detect(self, image: Image.Image) -> tuple[Image.Image, list[dict]]:
        """
        Return mock detection for development.
        
        Args:
            image: PIL Image to annotate.
            
        Returns:
            Tuple of (annotated image, list of detections).
        """
        width, height = image.size
        
        # Create varied mock detections based on image
        seed = (width * height) % 3
        
        mock_detections_sets = [
            [
                {"box": [200, 100, 600, 400], "label": "Plastic Bottle", "category": "recyclable", "confidence": 92},
                {"box": [300, 500, 700, 850], "label": "Food Container", "category": "compostable", "confidence": 85}
            ],
            [
                {"box": [150, 200, 500, 600], "label": "Glass Jar", "category": "recyclable", "confidence": 88},
                {"box": [400, 100, 800, 400], "label": "Cardboard Box", "category": "recyclable", "confidence": 90}
            ],
            [
                {"box": [100, 150, 450, 500], "label": "Banana Peel", "category": "compostable", "confidence": 95},
                {"box": [300, 400, 650, 750], "label": "Vegetable Scraps", "category": "compostable", "confidence": 91},
                {"box": [500, 200, 850, 550], "label": "Paper Bag", "category": "recyclable", "confidence": 87}
            ]
        ]
        
        detections = mock_detections_sets[seed]
        annotated_image = self._draw_detections(image.copy(), detections)
        
        return annotated_image, detections
