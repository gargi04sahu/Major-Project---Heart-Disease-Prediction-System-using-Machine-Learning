import streamlit as st
import os
import base64

def inject_custom_css():
    """Inject custom CSS into the Streamlit app."""
    custom_css_path = os.path.join(".streamlit", "static", "css", "custom.css")
    bootstrap_css_path = os.path.join(".streamlit", "static", "css", "bootstrap.min.css")
    fa_css_path = os.path.join(".streamlit", "static", "css", "font-awesome.min.css")
    
    with open(custom_css_path, "r") as f:
        custom_css = f.read()
        
    try:
        with open(bootstrap_css_path, "r") as f:
            bootstrap_css = f.read()
    except:
        bootstrap_css = ""
        
    try:
        with open(fa_css_path, "r") as f:
            fa_css = f.read()
    except:
        fa_css = ""

    # Combine the CSS files
    all_css = f"""
    <style>
        {custom_css}
    </style>
    """
    
    st.markdown(all_css, unsafe_allow_html=True)

def add_font_awesome():
    """Add Font Awesome Icons CSS"""
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)

def add_logo():
    """Add the CardioPredict logo."""
    # Use a heart disease prediction themed SVG logo instead of external image
    logo_html = '''
    <div style="display: flex; align-items: center; justify-content: center;">
        <svg width="60" height="60" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <!-- Heart shape -->
            <path d="M50,85 C50,85 20,65 20,40 C20,25 30,15 45,15 C47,15 50,20 50,20 C50,20 53,15 55,15 C70,15 80,25 80,40 C80,65 50,85 50,85 Z" 
                  fill="#e74c3c" stroke="#c0392b" stroke-width="2"/>
            <!-- EKG line -->
            <path d="M15,50 L25,50 L30,30 L35,70 L40,20 L45,80 L50,50 L55,50 L60,30 L65,70 L70,50 L85,50" 
                  fill="none" stroke="#2ecc71" stroke-width="3" stroke-linecap="round"/>
            <!-- Small medical cross -->
            <rect x="45" y="35" width="10" height="3" fill="white"/>
            <rect x="48.5" y="31.5" width="3" height="10" fill="white"/>
        </svg>
    </div>
    '''
    
    return logo_html

def render_header():
    """Render the custom header for the app."""
    st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; align-items: center; justify-content: center;">
            {add_logo()}
            <div style="margin-left: 20px;">
                <h1 class="header-title">CardioPredict</h1>
                <p class="header-subtitle">Advanced Heart Disease Risk Assessment Platform</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_card(icon, title, content):
    """Render a styled card with icon, title and content."""
    return f"""
    <div class="card">
        <div class="card-icon" style="color: #0cb8b6;">
            <i class="fas {icon}"></i>
        </div>
        <h3 class="card-title">{title}</h3>
        <p>{content}</p>
    </div>
    """

def render_custom_button(label, icon=None, url=None):
    """Render a styled button with optional icon and URL."""
    icon_html = f'<i class="fas {icon} mr-2"></i> ' if icon else ''
    
    if url:
        return f"""
        <a href="{url}" class="custom-button">
            {icon_html}{label}
        </a>
        """
    else:
        return f"""
        <div class="custom-button">
            {icon_html}{label}
        </div>
        """

def render_stat_card(number, label):
    """Render a statistic card."""
    return f"""
    <div class="stat-card">
        <div class="stat-number">{number}</div>
        <div class="stat-label">{label}</div>
    </div>
    """

def render_footer():
    """Render the custom footer for the app."""
    st.markdown(f"""
    <div class="footer">
        <p>© 2025 CardioPredict - Advanced Heart Disease Risk Assessment Platform</p>
        <p>Disclaimer: This tool provides an estimate based on machine learning and should not replace professional medical advice.</p>
    </div>
    """, unsafe_allow_html=True)

def render_prediction_result(risk_level, probability):
    """Render a styled prediction result."""
    if risk_level == "High":
        color = "#e74c3c"
        bg_color = "rgba(231, 76, 60, 0.1)"
        icon = "fa-triangle-exclamation"
        message = "High Risk Detected"
    else:
        color = "#2ecc71"
        bg_color = "rgba(46, 204, 113, 0.1)"
        icon = "fa-circle-check"
        message = "Low Risk Detected"
    
    return f"""
    <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; border-left: 5px solid {color}; margin: 20px 0;">
        <div style="display: flex; align-items: center;">
            <i class="fas {icon}" style="font-size: 40px; color: {color}; margin-right: 20px;"></i>
            <div>
                <h3 style="color: {color}; margin: 0 0 5px 0;">{message}</h3>
                <p style="margin: 0; font-size: 16px;">Confidence: <span style="font-weight: bold;">{probability:.2%}</span></p>
            </div>
        </div>
    </div>
    """

def render_health_recommendation(title, content, icon="fa-heart-pulse"):
    """Render a styled health recommendation."""
    return f"""
    <div class="health-recommendation">
        <h4><i class="fas {icon}"></i> {title}</h4>
        <p>{content}</p>
    </div>
    """

def setup_page():
    """Set up the page with custom styling."""
    inject_custom_css()
    add_font_awesome()