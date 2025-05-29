import streamlit as st

# Set page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="CardioPredict",
    page_icon="❤️",
    layout="wide",
)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import requests
import json
import os
from model import load_model, predict_heart_disease
from data_processor import load_data, preprocess_data
from utils import display_prediction_explanation, display_health_guidelines
from sqlite_database import save_prediction, db_connected
from session_state import initialize_session_state, is_authenticated, is_admin, get_current_user_id, logout_user
from admin_panel import render_admin_panel
from auth_components import render_auth_page
from user_profile import render_user_profile
from doctor_advice import get_personalized_doctor_prescription, display_health_recommendations_detailed
from pages import render_home_page, render_about_page, render_contact_page
from layout import setup_page, render_card, render_custom_button, render_stat_card
from layout import render_footer, render_prediction_result, render_health_recommendation

# Initialize session state
initialize_session_state()

# Apply custom styling
setup_page()

# Navigation bar with modern styling
st.markdown("""
<style>
    .nav-link {
        color: #325C6A !important;
        border-radius: 5px !important;
        margin: 0 5px !important;
        transition: all 0.3s ease !important;
    }
    .nav-link:hover {
        background-color: rgba(12, 184, 182, 0.1) !important;
        color: #0cb8b6 !important;
    }
    .nav-link.active {
        background-color: #0cb8b6 !important;
        color: white !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 5px 5px 0 0;
    }
</style>
""", unsafe_allow_html=True)

if is_authenticated():
    # Different menu options for admin users
    if is_admin():
        selected = option_menu(
            menu_title=None,
            options=["Home", "Prediction", "Admin Panel", "About Us", "Contact Us", "Profile", "Logout"],
            icons=["house", "activity", "shield-lock", "info-circle", "envelope", "person", "box-arrow-right"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "10px", "background-color": "#f5f9fa", "border-radius": "10px", "margin": "10px 0px"},
                "icon": {"color": "#0cb8b6", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "rgba(12, 184, 182, 0.1)"},
                "nav-link-selected": {"background-color": "#0cb8b6"},
            }
        )
    else:
        selected = option_menu(
            menu_title=None,
            options=["Home", "Prediction", "About Us", "Contact Us", "Profile", "Logout"],
            icons=["house", "activity", "info-circle", "envelope", "person", "box-arrow-right"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "10px", "background-color": "#f5f9fa", "border-radius": "10px", "margin": "10px 0px"},
                "icon": {"color": "#0cb8b6", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "rgba(12, 184, 182, 0.1)"},
                "nav-link-selected": {"background-color": "#0cb8b6"},
            }
        )
else:
    selected = option_menu(
        menu_title=None,
        options=["Home", "Prediction", "About Us", "Contact Us", "Login/Register"],
        icons=["house", "activity", "info-circle", "envelope", "person"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "10px", "background-color": "#f5f9fa", "border-radius": "10px", "margin": "10px 0px"},
            "icon": {"color": "#0cb8b6", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "rgba(12, 184, 182, 0.1)"},
            "nav-link-selected": {"background-color": "#0cb8b6"},
        }
    )

# Sidebar with styled info cards
with st.sidebar:
    st.markdown(f"""
    <div class="card" style="margin-bottom: 20px;">
        <h3 class="card-title">About CardioPredict</h3>
        <p>This clinical-grade platform uses advanced machine learning to predict heart disease risk
        based on your health metrics and provide personalized recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Heart disease risk factors in a stylish format
    st.markdown(f"""
    <div class="card">
        <h3 class="card-title">
            <i class="fas fa-heart-pulse" style="color: #e74c3c;"></i> 
            Heart Disease Risk Factors
        </h3>
        <ul style="padding-left: 20px; color: #555;">
            <li><strong>Age</strong>: Risk increases with age</li>
            <li><strong>Gender</strong>: Men are generally at higher risk</li>
            <li><strong>Cholesterol</strong>: High levels increase risk</li>
            <li><strong>Blood Pressure</strong>: High BP is a major risk factor</li>
            <li><strong>Smoking</strong>: Significantly increases risk</li>
            <li><strong>Diabetes</strong>: Can double the risk of heart disease</li>
            <li><strong>Family History</strong>: Genetic factors play a role</li>
            <li><strong>Physical Activity</strong>: Regular exercise reduces risk</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Handle logout
if selected == "Logout":
    logout_user()
    st.rerun()

# Display content based on navigation selection
if selected == "Home":
    render_home_page()

elif selected == "About Us":
    render_about_page()

elif selected == "Contact Us":
    render_contact_page()

elif selected == "Login/Register":
    auth_col1, auth_col2 = st.columns([2, 3])
    
    with auth_col1:
        render_auth_page()
    
    with auth_col2:
        # Create a heart disease themed SVG illustration
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 20px 0;">
            <svg width="200" height="150" viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg">
                <!-- Background circle -->
                <circle cx="100" cy="75" r="65" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
                
                <!-- Large heart -->
                <path d="M100,120 C100,120 70,100 70,75 C70,60 80,50 95,50 C97,50 100,55 100,55 C100,55 103,50 105,50 C120,50 130,60 130,75 C130,100 100,120 100,120 Z" 
                      fill="#e74c3c" stroke="#c0392b" stroke-width="2"/>
                
                <!-- EKG heartbeat line -->
                <path d="M30,75 L50,75 L55,55 L60,95 L65,35 L70,115 L75,75 L125,75 L130,55 L135,95 L140,75 L170,75" 
                      fill="none" stroke="#2ecc71" stroke-width="3" stroke-linecap="round"/>
                
                <!-- Stethoscope -->
                <circle cx="60" cy="40" r="8" fill="none" stroke="white" stroke-width="3"/>
                <path d="M68,40 Q75,45 80,55" fill="none" stroke="white" stroke-width="3" stroke-linecap="round"/>
                
                <!-- Medical cross -->
                <rect x="130" y="35" width="15" height="4" fill="white" rx="2"/>
                <rect x="135.5" y="29.5" width="4" height="15" fill="white" rx="2"/>
                
                <!-- Data points/analytics -->
                <circle cx="45" cy="105" r="3" fill="#3498db"/>
                <circle cx="55" cy="100" r="3" fill="#3498db"/>
                <circle cx="65" cy="110" r="3" fill="#3498db"/>
                <circle cx="155" cy="105" r="3" fill="#f39c12"/>
                <circle cx="165" cy="100" r="3" fill="#f39c12"/>
                <circle cx="175" cy="108" r="3" fill="#f39c12"/>
                
                <!-- Connecting lines for data points -->
                <path d="M45,105 L55,100 L65,110" fill="none" stroke="#3498db" stroke-width="2"/>
                <path d="M155,105 L165,100 L175,108" fill="none" stroke="#f39c12" stroke-width="2"/>
            </svg>
            <h4 style="color: white; margin: 15px 0 5px 0;">Heart Health Monitoring</h4>
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 14px;">Advanced cardiac risk assessment technology</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### Benefits of Creating an Account:
        - Track your heart health over time
        - Save your prediction history
        - Monitor changes in your health metrics
        - Get personalized health recommendations
        """)

elif selected == "Profile" and is_authenticated():
    render_user_profile()
    
elif selected == "Admin Panel" and is_authenticated() and is_admin():
    render_admin_panel()

elif selected == "Prediction":
    # Check if user is authenticated, if not, show option to continue as guest or sign in
    if not is_authenticated():
        st.warning("⚠️ You are not logged in. Your prediction data will not be saved.")
        st.info("Create an account or log in to track your heart health over time.")
        
        auth_col1, auth_col2, auth_col3 = st.columns([2, 3, 2])
        with auth_col2:
            if st.button("Continue as Guest", use_container_width=True):
                pass  # Continue to prediction content
    
    # Prediction content
    st.title("Heart Disease Prediction Tool")
    st.markdown("### Enter your health information below for a personalized risk assessment")
    
    # Create two columns for input form
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=45)
        gender = st.selectbox("Gender", ["Male", "Female"])
        gender_encoded = 1 if gender == "Male" else 0
        
        chest_pain_type = st.selectbox(
            "Chest Pain Type",
            [
                "Typical Angina",
                "Atypical Angina",
                "Non-anginal Pain",
                "Asymptomatic"
            ]
        )
        # Encode chest pain type (0-3)
        cp_dict = {
            "Typical Angina": 0,
            "Atypical Angina": 1,
            "Non-anginal Pain": 2,
            "Asymptomatic": 3
        }
        cp_encoded = cp_dict[chest_pain_type]
        
        resting_bp = st.number_input("Resting Blood Pressure (mm Hg)", min_value=80, max_value=200, value=120)
        cholesterol = st.number_input("Serum Cholesterol (mg/dl)", min_value=100, max_value=600, value=200)
        
    with col2:
        fasting_bs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", ["No", "Yes"])
        fbs_encoded = 1 if fasting_bs == "Yes" else 0
        
        rest_ecg = st.selectbox(
            "Resting ECG Results",
            [
                "Normal",
                "ST-T Wave Abnormality",
                "Left Ventricular Hypertrophy"
            ]
        )
        # Encode resting ECG (0-2)
        ecg_dict = {
            "Normal": 0,
            "ST-T Wave Abnormality": 1,
            "Left Ventricular Hypertrophy": 2
        }
        rest_ecg_encoded = ecg_dict[rest_ecg]
        
        max_hr = st.number_input("Maximum Heart Rate Achieved", min_value=60, max_value=220, value=150)
        
        exercise_angina = st.selectbox("Exercise Induced Angina", ["No", "Yes"])
        exang_encoded = 1 if exercise_angina == "Yes" else 0
        
        st_depression = st.number_input("ST Depression Induced by Exercise", min_value=0.0, max_value=10.0, value=0.0)
        
        st_slope = st.selectbox(
            "Slope of Peak Exercise ST Segment",
            ["Upsloping", "Flat", "Downsloping"]
        )
        # Encode ST slope (0-2)
        slope_dict = {
            "Upsloping": 0,
            "Flat": 1,
            "Downsloping": 2
        }
        st_slope_encoded = slope_dict[st_slope]
    
    # Collect user input into a dictionary
    user_data = {
        'age': age,
        'sex': gender_encoded,
        'cp': cp_encoded,
        'trestbps': resting_bp,
        'chol': cholesterol,
        'fbs': fbs_encoded,
        'restecg': rest_ecg_encoded,
        'thalach': max_hr,
        'exang': exang_encoded,
        'oldpeak': st_depression,
        'slope': st_slope_encoded
    }
    
    # Convert dictionary to DataFrame for prediction
    user_df = pd.DataFrame([user_data])
    
    # Create custom styled prediction button
    st.markdown("""
    <style>
    div.stButton > button {
        background: linear-gradient(90deg, #0cb8b6 0%, #325C6A 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(12, 184, 182, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("Predict Heart Disease Risk", use_container_width=True):
        with st.spinner("Analyzing your data..."):
            # Load model and make prediction
            model = load_model()
            prediction, probability = predict_heart_disease(model, user_df)
            
            # Display styled prediction result
            st.subheader("Prediction Result")
            
            if prediction[0] == 1:
                risk_level = "High"
                risk_prob = probability[0][1]
                
                # Use custom styled result display
                st.markdown(render_prediction_result(risk_level, risk_prob), unsafe_allow_html=True)
                
                # Add styled risk explanation card
                st.markdown("""
                <div class="card" style="border-left: 4px solid #e74c3c; margin-top: 20px;">
                    <h3 class="card-title">Risk Explanation</h3>
                    <p>Your health metrics indicate an elevated risk of heart disease. This assessment is based on 
                    multiple factors including your age, gender, blood pressure, cholesterol levels, and other clinical indicators.</p>
                    <p>Please consider discussing these results with your healthcare provider for a comprehensive evaluation.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                risk_level = "Low"
                risk_prob = probability[0][0]
                
                # Use custom styled result display
                st.markdown(render_prediction_result(risk_level, risk_prob), unsafe_allow_html=True)
                
                # Add styled risk explanation card
                st.markdown("""
                <div class="card" style="border-left: 4px solid #2ecc71; margin-top: 20px;">
                    <h3 class="card-title">Risk Explanation</h3>
                    <p>Your health metrics indicate a lower risk of heart disease. This is a positive sign, but maintaining 
                    heart-healthy habits is still important for long-term cardiovascular health.</p>
                    <p>Regular check-ups and a healthy lifestyle will help maintain your heart health.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Create enhanced visualization of prediction probability
            st.markdown("<div class='custom-chart'>", unsafe_allow_html=True)
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=["Heart Disease Risk", "Normal Heart"],
                y=[probability[0][1], probability[0][0]],
                marker_color=["#e74c3c", "#2ecc71"],
                text=[f"{probability[0][1]:.2%}", f"{probability[0][0]:.2%}"],
                textposition="auto"
            ))
            
            fig.update_layout(
                title={
                    'text': "Prediction Probability",
                    'font': {'size': 22, 'color': '#325C6A'}
                },
                xaxis={'title': 'Outcome'},
                yaxis={'title': 'Probability', 'range': [0, 1]},
                plot_bgcolor='rgba(245, 249, 250, 0.8)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Generate prescription or recommendations based on risk level
            st.markdown("<h3 style='color: #325C6A; margin-top: 30px;'>Personalized Health Recommendations</h3>", unsafe_allow_html=True)
            
            if risk_level == "High":
                # Generate doctor's prescription for high risk
                prescription_data = get_personalized_doctor_prescription(user_df, risk_level)
                
                # Display in styled recommendation cards
                st.markdown("""
                <div class="card" style="border-left: 4px solid #e74c3c;">
                    <h3 class="card-title"><i class="fas fa-user-md"></i> Medical Consultation Advised</h3>
                    <p>Based on your risk factors, we recommend consulting with a healthcare provider for a more thorough evaluation.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Generate detailed health recommendations for low risk
                prescription_data = display_health_recommendations_detailed(user_df, risk_level)
                
                # Display in styled recommendation cards
                st.markdown("""
                <div class="card" style="border-left: 4px solid #2ecc71;">
                    <h3 class="card-title"><i class="fas fa-heart"></i> Continue Healthy Habits</h3>
                    <p>Your current metrics show good heart health. Continue maintaining healthy lifestyle choices to preserve your cardiovascular health.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Show specific health recommendations
            st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
            
            rec_col1, rec_col2 = st.columns(2)
            
            with rec_col1:
                st.markdown(render_health_recommendation(
                    "Diet Recommendations", 
                    "Focus on a heart-healthy diet rich in fruits, vegetables, whole grains, and lean proteins. Limit saturated fats, trans fats, sodium, and added sugars.",
                    "fa-utensils"
                ), unsafe_allow_html=True)
                
                st.markdown(render_health_recommendation(
                    "Exercise Guidance", 
                    "Aim for at least 150 minutes of moderate-intensity aerobic activity or 75 minutes of vigorous activity each week, plus muscle-strengthening activities twice a week.",
                    "fa-dumbbell"
                ), unsafe_allow_html=True)
            
            with rec_col2:
                st.markdown(render_health_recommendation(
                    "Stress Management", 
                    "Practice stress reduction techniques such as mindfulness, meditation, deep breathing, or yoga to help manage stress levels.",
                    "fa-brain"
                ), unsafe_allow_html=True)
                
                st.markdown(render_health_recommendation(
                    "Regular Check-ups", 
                    "Schedule regular check-ups with your healthcare provider to monitor your blood pressure, cholesterol, and overall heart health.",
                    "fa-calendar-check"
                ), unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add account creation prompt with custom styling
            if is_authenticated():
                user_id = get_current_user_id()
                success, prediction_id = save_prediction(user_id, risk_level, risk_prob, user_data, prescription_data)
                if success:
                    st.markdown("""
                    <div style="background-color: rgba(46, 204, 113, 0.1); padding: 15px; border-radius: 5px; border-left: 4px solid #2ecc71; margin-top: 20px;">
                        <p style="margin: 0;"><i class="fas fa-check-circle" style="color: #2ecc71;"></i> This prediction and prescription have been saved to your profile.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Could not save prediction to your profile.")
            else:
                st.markdown("""
                <div style="background-color: rgba(52, 152, 219, 0.1); padding: 20px; border-radius: 5px; border-left: 4px solid #3498db; margin-top: 20px;">
                    <h4 style="color: #3498db; margin-top: 0;"><i class="fas fa-user-plus"></i> Track Your Heart Health Journey</h4>
                    <p>Create an account to save your prediction history, track changes in your health metrics over time, and receive personalized recommendations.</p>
                    <p>Having a complete history helps you and your healthcare provider monitor your cardiovascular health progress.</p>
                </div>
                """, unsafe_allow_html=True)

# Add custom footer
st.markdown("<br><br>", unsafe_allow_html=True)
render_footer()
