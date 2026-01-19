"""
Results Display Component
Renders classification results with styling and details
"""

import logging

import streamlit as st

logger = logging.getLogger(__name__)

# Category styling configuration
CATEGORY_CONFIG = {
    "recyclable": {
        "icon": "♻️",
        "color": "#28a745",
        "description": "This item can be recycled!"
    },
    "compostable": {
        "icon": "🌱",
        "color": "#8b4513",
        "description": "This item can be composted!"
    },
    "landfill": {
        "icon": "🗑️",
        "color": "#6c757d",
        "description": "This item goes in the trash."
    },
    "hazardous": {
        "icon": "⚠️",
        "color": "#dc3545",
        "description": "This item requires special handling!"
    },
    "special": {
        "icon": "📦",
        "color": "#ffc107",
        "description": "This item requires special disposal."
    }
}


def render_result_card(result: dict, show_details: bool = True) -> None:
    """
    Render a styled classification result card.
    
    Args:
        result: Classification result dictionary.
        show_details: Whether to show detailed information.
    """
    category = result.get("category", "unknown").lower()
    config = CATEGORY_CONFIG.get(category, {
        "icon": "❓",
        "color": "#6c757d",
        "description": "Unknown classification"
    })
    
    # Main result container
    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {config['color']};
            padding: 1rem;
            background-color: rgba(0,0,0,0.05);
            border-radius: 0.5rem;
            margin: 1rem 0;
        ">
            <h2 style="margin: 0;">
                {config['icon']} {category.title()}
            </h2>
            <p style="color: gray; margin: 0.5rem 0;">
                {config['description']}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if show_details:
        render_result_details(result)


def render_result_details(result: dict) -> None:
    """
    Render detailed classification information.
    
    Args:
        result: Classification result dictionary.
    """
    col1, col2 = st.columns(2)
    
    with col1:
        # Confidence meter
        confidence = result.get("confidence", 0)
        st.markdown("**Confidence Score**")
        st.progress(confidence / 100)
        st.caption(f"{confidence}% confident")
        
        # Material info
        material = result.get("material", "Unknown")
        st.markdown("**Material Detected**")
        st.code(material)
    
    with col2:
        # Disposal instructions
        st.markdown("**Disposal Instructions**")
        instructions = result.get(
            "disposal_instructions",
            "No specific instructions available."
        )
        st.info(instructions)
    
    # Environmental tip (full width)
    if "environmental_tip" in result:
        st.markdown("---")
        st.markdown("### 🌍 Environmental Tip")
        st.success(result["environmental_tip"])


def render_history(history: list[dict], max_items: int = 5) -> None:
    """
    Render classification history.
    
    Args:
        history: List of previous classification results.
        max_items: Maximum number of items to display.
    """
    if not history:
        st.info("No classification history yet.")
        return
    
    st.markdown("### 📜 Recent Classifications")
    
    for i, result in enumerate(reversed(history[-max_items:])):
        category = result.get("category", "unknown")
        config = CATEGORY_CONFIG.get(category.lower(), {"icon": "❓"})
        
        with st.expander(
            f"{config['icon']} {category.title()} - "
            f"{result.get('material', 'Unknown')}"
        ):
            render_result_details(result)
