"""
Webcam Capture Component
Provides real-time camera capture for waste classification
"""

import logging
from typing import Callable

import streamlit as st
from PIL import Image

logger = logging.getLogger(__name__)


def render_webcam_capture(
    on_capture: Callable[[Image.Image], None] | None = None,
    key: str = "webcam_capture"
) -> Image.Image | None:
    """
    Render webcam capture component.
    
    Args:
        on_capture: Callback function when image is captured.
        key: Unique key for the component.
        
    Returns:
        Captured PIL Image or None.
    """
    st.markdown("### 📷 Camera Capture")
    
    # Check if camera is enabled
    enable_camera = st.checkbox("Enable Camera", key=f"{key}_enable")
    
    if not enable_camera:
        st.info("Enable camera to capture waste images directly.")
        return None
    
    # Camera input
    camera_image = st.camera_input(
        "Take a photo of the waste item",
        key=f"{key}_camera"
    )
    
    if camera_image is not None:
        image = Image.open(camera_image)
        
        if on_capture:
            on_capture(image)
        
        return image
    
    return None


def render_camera_tips() -> None:
    """Render tips for better camera captures."""
    with st.expander("📸 Camera Tips"):
        st.markdown("""
        **For best results:**
        
        1. **Good Lighting** - Ensure adequate lighting on the item
        2. **Clear Background** - Use a contrasting background
        3. **Single Item** - Focus on one item at a time
        4. **Show Labels** - Include any recycling symbols or labels
        5. **Steady Shot** - Keep the camera steady for clarity
        """)
