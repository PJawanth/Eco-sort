"""
EcoSort-AI - Main Streamlit Application
AI-Powered Waste Classification for a Sustainable Future
"""

import sys
import pathlib
# Ensure repository root is on sys.path so top-level packages (utils, components)
# can be imported when running app/main.py directly (e.g., `python app/main.py` or
# `streamlit run app/main.py`). Insert at front to prefer local packages.
repo_root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

import logging
import os
import time
from pathlib import Path
from queue import Queue
from threading import Thread, Lock
from dataclasses import dataclass, field
from typing import List, Dict, Any

import cv2
import numpy as np
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av

# Shared detection state for thread-safe communication
@dataclass
class DetectionState:
    """Thread-safe detection state."""
    detections: List[Dict[str, Any]] = field(default_factory=list)
    last_update: float = 0.0
    status: str = "waiting"  # waiting, detecting, detected, no_objects, error
    error_message: str = ""
    _lock: Lock = field(default_factory=Lock)
    
    def update(self, detections: List[Dict], status: str, error: str = ""):
        with self._lock:
            self.detections = detections
            self.last_update = time.time()
            self.status = status
            self.error_message = error
    
    def get(self):
        with self._lock:
            return self.detections.copy(), self.status, self.error_message, self.last_update

# Global detection state instance
_detection_state = DetectionState()

from utils.ai_engine import GeminiEngine
from components.webcam import render_webcam_capture

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="EcoSort-AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-org/EcoSort-AI",
        "Report a bug": "https://github.com/your-org/EcoSort-AI/issues",
        "About": "# EcoSort-AI\nAI-Powered Waste Classification"
    }
)

# Global engine instance for WebRTC (can't use session_state in threads)
@st.cache_resource
def get_engine():
    """Get or create the GeminiEngine instance."""
    return GeminiEngine()


def init_session_state() -> None:
    """Initialize session state variables."""
    if "classification_history" not in st.session_state:
        st.session_state.classification_history = []
    if "engine" not in st.session_state:
        st.session_state.engine = get_engine()


def render_sidebar() -> None:
    """Render the sidebar with app info and settings."""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=EcoSort-AI", width=150)
        st.markdown("---")
        
        st.markdown("### 🌍 About")
        st.markdown(
            "EcoSort-AI helps you classify waste items "
            "using advanced AI for proper recycling and disposal."
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=50,
            max_value=100,
            value=70,
            help="Minimum confidence score for classification"
        )
        st.session_state.confidence_threshold = confidence_threshold
        
        st.markdown("---")
        st.markdown("### 📊 Statistics")
        st.metric("Items Classified", len(st.session_state.classification_history))


def render_classification_result(result: dict) -> None:
    """Render the classification result."""
    st.markdown("---")
    st.markdown("## 🔍 Classification Result")
    
    # Category display with color coding
    category_colors = {
        "recyclable": "🟢",
        "compostable": "🟤",
        "landfill": "⚫",
        "hazardous": "🔴",
        "special": "🟡"
    }
    
    category = result.get("category", "unknown").lower()
    icon = category_colors.get(category, "⚪")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Category",
            value=f"{icon} {category.title()}"
        )
    
    with col2:
        confidence = result.get("confidence", 0)
        st.metric(
            label="Confidence",
            value=f"{confidence}%"
        )
        st.progress(confidence / 100)
    
    with col3:
        material = result.get("material", "Unknown")
        st.metric(
            label="Material",
            value=material
        )
    
    # Disposal instructions
    st.markdown("### 📋 Disposal Instructions")
    st.info(result.get("disposal_instructions", "No specific instructions available."))
    
    # Environmental tip
    if "environmental_tip" in result:
        st.markdown("### 🌱 Environmental Tip")
        st.success(result["environmental_tip"])


def main() -> None:
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    
    # Header
    st.title("🌿 EcoSort-AI")
    st.markdown("*AI-Powered Waste Classification for a Sustainable Future*")
    st.markdown("---")
    
    # Tabs for different input modes
    tab1, tab2 = st.tabs(["📤 Upload Image", "📷 Live Camera Detection"])
    
    with tab1:
        render_upload_tab()
    
    with tab2:
        render_webcam_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Made with 💚 for a sustainable future | "
        "<a href='https://github.com/your-org/EcoSort-AI'>GitHub</a>"
        "</div>",
        unsafe_allow_html=True
    )


def render_upload_tab() -> None:
    """Render the image upload tab with auto-classification."""
    st.markdown("### 📸 Upload Waste Image")
    
    # Show mock mode warning
    if not st.session_state.engine.api_key:
        st.warning(
            "⚠️ **Demo Mode**: No Google API key configured. "
            "Classification results are simulated. Add `GOOGLE_API_KEY` to your `.env` file for real AI classification."
        )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload a clear image of the waste item",
            key="upload_tab_uploader"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Auto-classify on upload
            with st.spinner("🔍 Analyzing image with AI..."):
                try:
                    result = st.session_state.engine.classify_image(image)
                    
                    if result:
                        render_classification_result(result)
                        # Add to history only if not already added
                        if not st.session_state.classification_history or \
                           st.session_state.classification_history[-1] != result:
                            st.session_state.classification_history.append(result)
                    else:
                        st.error("Unable to classify the image. Please try again.")
                        
                except Exception as e:
                    logger.error(f"Classification error: {e}", exc_info=True)
                    st.error(f"An error occurred: {str(e)}")
    
    with col2:
        st.markdown("### 💡 Tips for Best Results")
        st.markdown("""
        - Use good lighting
        - Capture one item at a time
        - Show the entire item
        - Include any labels or markings
        """)


def render_webcam_tab() -> None:
    """Render the webcam tab with live object detection."""
    
    engine = get_engine()
    
    # Show warnings only if needed
    if not engine.api_key:
        st.warning("⚠️ Demo Mode: Add `GOOGLE_API_KEY` to `.env` for real detection.")
    
    if engine.is_quota_exceeded:
        st.error(f"🚫 Quota Exceeded: Wait {engine.quota_wait_time}s")
    
    # Two-column layout: Video on left, Info on right
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Detection interval slider
        detection_interval = st.slider(
            "Detection Interval (seconds)",
            min_value=1,
            max_value=10,
            value=3,
            help="How often to run AI detection on the video stream"
        )
        
        # WebRTC configuration
        RTC_CONFIGURATION = RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )
        
        cached_engine = get_engine()
        
        # Video processor class
        class WasteDetectionProcessor(VideoProcessorBase):
            def __init__(self):
                self.last_detection_time = 0
                self.current_detections = []
                self.detection_interval = detection_interval
                self.engine = cached_engine
                
            def recv(self, frame):
                global _detection_state
                img = frame.to_ndarray(format="bgr24")
                current_time = time.time()
                
                if current_time - self.last_detection_time > self.detection_interval:
                    try:
                        pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                        _, detections = self.engine.detect_objects(pil_image)
                        self.current_detections = detections
                        self.last_detection_time = current_time
                        
                        if detections:
                            _detection_state.update(detections, "detected", "")
                        else:
                            _detection_state.update([], "no_objects", "")
                    except Exception as e:
                        logger.error(f"Detection error: {e}")
                        _detection_state.update([], "error", str(e))
                
                # Draw detections
                img = self._draw_detections(img, self.current_detections)
                return av.VideoFrame.from_ndarray(img, format="bgr24")
            
            def _draw_detections(self, img, detections):
                height, width = img.shape[:2]
                colors = {
                    "recyclable": (100, 200, 0), "compostable": (43, 90, 139),
                    "landfill": (100, 100, 100), "hazardous": (50, 50, 220),
                    "special": (50, 180, 220), "unknown": (150, 150, 150)
                }
                
                for det in detections:
                    box = det.get("box", [])
                    if len(box) != 4:
                        continue
                    
                    ymin, xmin, ymax, xmax = box
                    x1, y1 = int((xmin / 1000) * width), int((ymin / 1000) * height)
                    x2, y2 = int((xmax / 1000) * width), int((ymax / 1000) * height)
                    
                    category = det.get("category", "unknown").lower()
                    color = colors.get(category, colors["unknown"])
                    color_bgr = (color[2], color[1], color[0])
                    label = f"{det.get('label', 'Object')} ({det.get('confidence', 0)}%)"
                    
                    cv2.rectangle(img, (x1, y1), (x2, y2), color_bgr, 3)
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(img, (x1, y1 - th - 10), (x1 + tw + 10, y1), color_bgr, -1)
                    cv2.putText(img, label, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                return img
        
        # WebRTC stream
        ctx = webrtc_streamer(
            key="waste-detection",
            video_processor_factory=WasteDetectionProcessor,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        # Detection results below video
        if ctx.video_processor:
            st.markdown("---")
            rcol1, rcol2 = st.columns([5, 1])
            with rcol2:
                if st.button("🔄", key="refresh"):
                    st.rerun()
            
            detections, status, error_msg, _ = _detection_state.get()
            
            if status == "detected" and detections:
                for det in detections:
                    cat = det.get("category", "unknown").lower()
                    label = det.get("label", "Unknown")
                    conf = det.get("confidence", 0)
                    icons = {"recyclable": "🟢", "compostable": "🟤", "landfill": "⚫", "hazardous": "🔴", "special": "🟡"}
                    instructions = {"recyclable": "Recycle bin", "compostable": "Compost", "landfill": "General waste", "hazardous": "Special collection", "special": "Check guidelines"}
                    st.success(f"{icons.get(cat, '⚪')} **{label}** — {cat.title()} ({conf}%) → {instructions.get(cat, 'Check guidelines')}")
            elif status == "no_objects":
                st.warning("⚠️ No objects detected. Point camera at waste items.")
            elif status == "error":
                st.error(f"❌ {error_msg}")
    
    with col2:
        st.markdown("### 🎯 Live Detection Features")
        st.markdown("""
        - **Real-time video** with AI detection
        - **Bounding boxes** drawn live
        - **Category labels** updated continuously
        - **Adjustable detection speed**
        """)
        
        st.markdown("### 🏷️ Category Colors")
        st.markdown("""
        - 🟢 **Green**: Recyclable
        - 🟤 **Brown**: Compostable  
        - ⚫ **Gray**: Landfill
        - 🔴 **Red**: Hazardous
        - 🟡 **Yellow**: Special disposal
        """)


if __name__ == "__main__":
    main()
