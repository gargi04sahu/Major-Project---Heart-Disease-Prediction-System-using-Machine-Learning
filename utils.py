import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

def display_prediction_explanation(user_data, risk_level):
    """
    Display an explanation of the prediction results based on user input data.
    
    Args:
        user_data: DataFrame containing the user's health metrics
        risk_level: String indicating the predicted risk level ('High' or 'Low')
    """
    st.subheader("Understanding Your Results")
    
    # Extract key metrics from user data
    age = user_data['age'].values[0]
    gender = "Male" if user_data['sex'].values[0] == 1 else "Female"
    cholesterol = user_data['chol'].values[0]
    bp = user_data['trestbps'].values[0]
    max_hr = user_data['thalach'].values[0]
    
    # Define normal ranges
    cholesterol_normal = cholesterol < 200
    bp_normal = bp < 130
    max_hr_normal = (220 - age) * 0.85 > max_hr > (220 - age) * 0.5
    
    # Create explanation text
    st.markdown(f"Based on your health metrics, you have a **{risk_level} risk** of heart disease.")
    
    # List problematic and normal factors
    factors_of_concern = []
    healthy_factors = []
    
    # Age assessment
    if age > 45 and gender == "Male":
        factors_of_concern.append(f"Your age ({age}) puts you in a higher risk category for men over 45.")
    elif age > 55 and gender == "Female":
        factors_of_concern.append(f"Your age ({age}) puts you in a higher risk category for women over 55.")
    else:
        healthy_factors.append(f"Your age ({age}) is not a major risk factor based on your gender.")
    
    # Cholesterol assessment
    if not cholesterol_normal:
        severity = "moderately high" if cholesterol < 240 else "high"
        factors_of_concern.append(f"Your cholesterol level ({cholesterol} mg/dL) is {severity}. " 
                               f"Ideal levels are below 200 mg/dL.")
    else:
        healthy_factors.append(f"Your cholesterol level ({cholesterol} mg/dL) is within normal range.")
    
    # Blood pressure assessment
    if not bp_normal:
        severity = "elevated" if bp < 140 else "high"
        factors_of_concern.append(f"Your resting blood pressure ({bp} mm Hg) is {severity}. " 
                               f"Ideal levels are below 120 mm Hg.")
    else:
        healthy_factors.append(f"Your resting blood pressure ({bp} mm Hg) is within normal range.")
    
    # Heart rate assessment
    if not max_hr_normal:
        target_range = f"{int((220 - age) * 0.5)} - {int((220 - age) * 0.85)}"
        factors_of_concern.append(f"Your maximum heart rate ({max_hr} bpm) is outside the "
                               f"target range of {target_range} bpm for your age.")
    else:
        healthy_factors.append(f"Your maximum heart rate ({max_hr} bpm) is within normal range for your age.")
    
    # Display factors lists
    if factors_of_concern:
        st.markdown("### Factors of Concern:")
        for factor in factors_of_concern:
            st.markdown(f"- {factor}")
    
    if healthy_factors:
        st.markdown("### Positive Health Factors:")
        for factor in healthy_factors:
            st.markdown(f"- {factor}")
    
    # Show advice based on risk level
    st.markdown("### What This Means For You")
    if risk_level == "High":
        st.markdown(
            "Your results suggest a higher risk of heart disease. This doesn't mean you definitely "
            "have or will develop heart disease, but it indicates that you should consider consulting "
            "with a healthcare provider for a more thorough evaluation."
        )
    else:
        st.markdown(
            "Your results suggest a lower risk of heart disease. Continue maintaining a healthy "
            "lifestyle with regular exercise, a balanced diet, and routine health check-ups."
        )

def display_health_guidelines(user_data, risk_level):
    """
    Display health guidelines and recommendations based on user data and risk level.
    
    Args:
        user_data: DataFrame containing the user's health metrics
        risk_level: String indicating the predicted risk level ('High' or 'Low')
    """
    st.subheader("Health Recommendations")
    
    # Extract relevant data
    cholesterol = user_data['chol'].values[0]
    bp = user_data['trestbps'].values[0]
    has_diabetes = user_data['fbs'].values[0] == 1
    
    # General recommendations for everyone
    st.markdown("### General Heart Health Recommendations:")
    general_recommendations = [
        "**Regular Exercise**: Aim for at least 150 minutes of moderate aerobic activity or 75 minutes of vigorous aerobic activity weekly.",
        "**Healthy Diet**: Focus on fruits, vegetables, whole grains, lean proteins, and limit saturated fats, trans fats, and sodium.",
        "**Regular Check-ups**: Schedule routine medical check-ups to monitor your heart health.",
        "**Avoid Tobacco**: If you smoke, consider quitting. Avoid secondhand smoke when possible.",
        "**Limit Alcohol**: If you drink alcohol, do so in moderation (up to one drink per day for women and up to two for men)."
    ]
    
    for rec in general_recommendations:
        st.markdown(f"- {rec}")
    
    # Specific recommendations based on risk factors
    specific_recommendations = []
    
    if cholesterol >= 200:
        specific_recommendations.append(
            "**Cholesterol Management**: Consider dietary changes like reducing saturated fats and increasing fiber. "
            "Regular exercise can also help improve cholesterol levels."
        )
    
    if bp >= 130:
        specific_recommendations.append(
            "**Blood Pressure Control**: Consider the DASH diet (Dietary Approaches to Stop Hypertension), "
            "reducing sodium intake, regular physical activity, and stress management techniques."
        )
    
    if has_diabetes:
        specific_recommendations.append(
            "**Blood Sugar Management**: Monitor your blood sugar levels regularly, follow your diabetes treatment plan, "
            "and maintain a consistent eating and medication schedule."
        )
    
    if risk_level == "High":
        specific_recommendations.append(
            "**Consult a Specialist**: Consider seeing a cardiologist for a comprehensive heart health evaluation."
        )
        specific_recommendations.append(
            "**Stress Management**: Practice stress-reducing activities like meditation, yoga, or deep breathing exercises."
        )
    
    if specific_recommendations:
        st.markdown("### Specific Recommendations Based on Your Health Profile:")
        for rec in specific_recommendations:
            st.markdown(f"- {rec}")
    
    # Disclaimer
    st.info(
        "**Remember**: These are general recommendations and not a substitute for professional medical advice. "
        "Please consult with your healthcare provider for personalized guidance."
    )

def visualize_user_metrics(user_data):
    """
    Create visualizations of user health metrics compared to normal ranges.
    
    Args:
        user_data: DataFrame containing the user's health metrics
    """
    # Extract relevant metrics
    cholesterol = user_data['chol'].values[0]
    bp = user_data['trestbps'].values[0]
    
    # Create DataFrame for visualization
    metrics = pd.DataFrame({
        'Metric': ['Cholesterol', 'Blood Pressure'],
        'Value': [cholesterol, bp],
        'Lower Normal': [0, 90],  # Lower bounds of normal range
        'Upper Normal': [200, 120],  # Upper bounds of normal range
        'Status': [
            'High' if cholesterol > 200 else 'Normal',
            'High' if bp > 120 else 'Normal'
        ]
    })
    
    # Create visualization
    fig = px.bar(
        metrics,
        x='Metric',
        y='Value',
        color='Status',
        color_discrete_map={'Normal': 'green', 'High': 'red'},
        height=400
    )
    
    # Add reference ranges
    for i, row in metrics.iterrows():
        fig.add_shape(
            type='line',
            x0=i-0.4, x1=i+0.4,
            y0=row['Upper Normal'], y1=row['Upper Normal'],
            line=dict(color='black', width=2, dash='dash'),
            name='Upper Normal'
        )
    
    fig.update_layout(
        title='Your Key Health Metrics',
        yaxis_title='Value',
        showlegend=True
    )
    
    return fig

def create_comparison_chart(user_value, metric_name, normal_range, unit):
    """
    Create a gauge chart comparing user value to normal range.
    
    Args:
        user_value: The user's value for the metric
        metric_name: Name of the health metric
        normal_range: Tuple of (min, max) for normal range
        unit: Unit of measurement
    """
    min_val, max_val = normal_range
    
    # Determine status
    if user_value < min_val:
        status = "Low"
        color = "blue"
    elif user_value > max_val:
        status = "High"
        color = "red"
    else:
        status = "Normal"
        color = "green"
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=user_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{metric_name} ({unit})"},
        gauge={
            'axis': {'range': [min_val*0.8, max_val*1.5]},
            'bar': {'color': color},
            'steps': [
                {'range': [min_val*0.8, min_val], 'color': "lightblue"},
                {'range': [min_val, max_val], 'color': "lightgreen"},
                {'range': [max_val, max_val*1.5], 'color': "salmon"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': user_value
            }
        }
    ))
    
    return fig
