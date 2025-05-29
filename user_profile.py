import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.colored_header import colored_header
from sqlite_database import get_user_predictions, get_prediction_by_id, db_connected
from session_state import get_current_user_id, get_current_username, logout_user
from doctor_advice import display_saved_prescription

def render_user_profile():
    """Render the user profile page with prediction history"""
    user_id = get_current_user_id()
    username = get_current_username()
    
    st.title(f"👤 {username}'s Profile")
    
    # Improved header layout
    col1, col2, col3 = st.columns([6, 2, 2])
    with col3:
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Get user prediction history
    predictions = get_user_predictions(user_id, limit=20)
    
    # Add a health dashboard at the top
    if predictions:
        total_predictions = len(predictions)
        high_risk_count = sum(1 for p in predictions if p['risk_level'] == 'High')
        low_risk_count = total_predictions - high_risk_count
        
        st.markdown("""
        <div style="margin-bottom: 20px; margin-top: 10px;">
            <h3 style="color: #325C6A;">Your Health Dashboard</h3>
        </div>
        """, unsafe_allow_html=True)
        
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        with stats_col1:
            st.markdown(f"""
            <div style="background-color: #f5f9fa; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #e0e0e0;">
                <h4 style="margin: 0; color: #0cb8b6;">Total Tests</h4>
                <h2 style="margin: 10px 0; color: #325C6A;">{total_predictions}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with stats_col2:
            st.markdown(f"""
            <div style="background-color: #ffebee; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #e0e0e0;">
                <h4 style="margin: 0; color: #e74c3c;">High Risk</h4>
                <h2 style="margin: 10px 0; color: #325C6A;">{high_risk_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with stats_col3:
            st.markdown(f"""
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #e0e0e0;">
                <h4 style="margin: 0; color: #2ecc71;">Low Risk</h4>
                <h2 style="margin: 10px 0; color: #325C6A;">{low_risk_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Add a quick action button
        st.markdown("""
        <div style="margin: 20px 0;">
            <h4 style="color: #325C6A;">Quick Actions</h4>
        </div>
        """, unsafe_allow_html=True)
        
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            st.markdown("""
            <a href="/?selected=Prediction" target="_self" style="text-decoration: none;">
                <div style="background-color: #0cb8b6; color: white; padding: 15px; border-radius: 10px; text-align: center;">
                    <h4 style="margin: 0; color: white;">Take New Test</h4>
                </div>
            </a>
            """, unsafe_allow_html=True)
    
    if not predictions:
        st.info("You haven't made any predictions yet. Try making a prediction first!")
        return
    
    colored_header(
        label="Your Prediction History",
        description="View your previous heart disease risk assessments",
        color_name="blue-70"
    )
    
    # Create a DataFrame from the prediction history
    history_data = []
    for pred in predictions:
        # Extract key metrics from user data
        user_data = pred['user_data']
        risk_probability = pred['probability'] if pred['risk_level'] == "High" else 1 - pred['probability']
        
        history_data.append({
            'Date': pred['date'].strftime("%Y-%m-%d %H:%M"),
            'Risk Level': pred['risk_level'],
            'Probability': f"{risk_probability:.2%}",
            'Age': user_data.get('age', 'N/A'),
            'Gender': "Male" if user_data.get('sex', 0) == 1 else "Female",
            'Cholesterol': user_data.get('chol', 'N/A'),
            'Blood Pressure': user_data.get('trestbps', 'N/A'),
            'Max Heart Rate': user_data.get('thalach', 'N/A'),
        })
    
    history_df = pd.DataFrame(history_data)
    
    # Add buttons to view prescription details
    for i, pred in enumerate(predictions):
        has_prescription = 'prescription' in pred
        prescription_indicator = "📋" if has_prescription else ""
        
        if st.button(f"View Details {prescription_indicator} - {pred['date'].strftime('%Y-%m-%d %H:%M')} - {pred['risk_level']} Risk", key=f"view_{pred['id']}"):
            st.session_state.selected_prediction_id = pred['id']
            
    # Display the prediction history
    st.dataframe(history_df, use_container_width=True)
    
    # Display detailed prediction view if one is selected
    if 'selected_prediction_id' in st.session_state and st.session_state.selected_prediction_id:
        render_single_prediction_view(st.session_state.selected_prediction_id)
        if st.button("Back to History"):
            st.session_state.selected_prediction_id = None
            st.rerun()
    
    # Create a visualization of risk level history
    if len(predictions) > 1:
        st.subheader("Risk Level History")
        
        # Create chart data
        chart_data = []
        for i, pred in enumerate(reversed(predictions)):  # Reverse to show chronological order
            risk_probability = pred['probability'] if pred['risk_level'] == "High" else 1 - pred['probability']
            chart_data.append({
                'Prediction #': i + 1,
                'Date': pred['date'].strftime("%Y-%m-%d"),
                'Risk Probability': risk_probability,
                'Risk Level': pred['risk_level']
            })
        
        chart_df = pd.DataFrame(chart_data)
        
        # Create line chart
        fig = px.line(
            chart_df, 
            x='Prediction #', 
            y='Risk Probability',
            color='Risk Level',
            markers=True,
            labels={'Risk Probability': 'Risk Probability', 'Prediction #': 'Prediction Number'},
            color_discrete_map={"High": "red", "Low": "green"}
        )
        fig.update_layout(yaxis_tickformat='.0%')
        st.plotly_chart(fig, use_container_width=True)
        
        # Show data comparison
        if len(predictions) >= 2:
            st.subheader("Compare Your First and Latest Prediction")
            
            col1, col2 = st.columns(2)
            
            first_pred = predictions[-1]  # First prediction (oldest)
            latest_pred = predictions[0]  # Latest prediction
            
            with col1:
                st.markdown(f"**First Assessment ({first_pred['date'].strftime('%Y-%m-%d')})**")
                st.markdown(f"Risk Level: **{first_pred['risk_level']}**")
                first_data = first_pred['user_data']
                st.markdown(f"Age: {first_data.get('age', 'N/A')}")
                st.markdown(f"Cholesterol: {first_data.get('chol', 'N/A')} mg/dL")
                st.markdown(f"Blood Pressure: {first_data.get('trestbps', 'N/A')} mm Hg")
                st.markdown(f"Max Heart Rate: {first_data.get('thalach', 'N/A')} bpm")
            
            with col2:
                st.markdown(f"**Latest Assessment ({latest_pred['date'].strftime('%Y-%m-%d')})**")
                st.markdown(f"Risk Level: **{latest_pred['risk_level']}**")
                latest_data = latest_pred['user_data']
                st.markdown(f"Age: {latest_data.get('age', 'N/A')}")
                st.markdown(f"Cholesterol: {latest_data.get('chol', 'N/A')} mg/dL")
                st.markdown(f"Blood Pressure: {latest_data.get('trestbps', 'N/A')} mm Hg")
                st.markdown(f"Max Heart Rate: {latest_data.get('thalach', 'N/A')} bpm")
            
            # Track changes in risk
            if first_pred['risk_level'] != latest_pred['risk_level']:
                if latest_pred['risk_level'] == "Low":
                    st.success("👏 Your risk level has improved since your first assessment!")
                else:
                    st.warning("⚠️ Your risk level has increased since your first assessment.")
                
                # Provide simple recommendations based on changes
                st.markdown("### Recommendations Based on Changes")
                if latest_data.get('chol', 0) > first_data.get('chol', 0):
                    st.markdown("- Your cholesterol levels have increased. Consider consulting with a healthcare provider and reviewing your diet.")
                if latest_data.get('trestbps', 0) > first_data.get('trestbps', 0):
                    st.markdown("- Your blood pressure has increased. Regular exercise and reducing sodium intake may help.")

def render_single_prediction_view(prediction_id):
    """Render a detailed view of a single prediction with prescription information"""
    # Get the prediction data
    prediction = get_prediction_by_id(prediction_id)
    
    if not prediction:
        st.error("Prediction not found.")
        return
    
    # Display prediction details
    st.markdown("---")
    colored_header(
        label=f"Detailed View: {prediction['date'].strftime('%Y-%m-%d %H:%M')}",
        description=f"Risk Level: {prediction['risk_level']}",
        color_name="blue-70"
    )
    
    # Display basic prediction information
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Assessment Details")
        st.markdown(f"**Date:** {prediction['date'].strftime('%Y-%m-%d %H:%M')}")
        st.markdown(f"**Risk Level:** {prediction['risk_level']}")
        risk_probability = prediction['probability'] if prediction['risk_level'] == "High" else 1 - prediction['probability']
        st.markdown(f"**Probability:** {risk_probability:.2%}")
    
    with col2:
        st.markdown("### Health Metrics")
        user_data = prediction['user_data']
        st.markdown(f"**Age:** {user_data.get('age', 'N/A')}")
        st.markdown(f"**Gender:** {'Male' if user_data.get('sex', 0) == 1 else 'Female'}")
        st.markdown(f"**Cholesterol:** {user_data.get('chol', 'N/A')} mg/dL")
        st.markdown(f"**Blood Pressure:** {user_data.get('trestbps', 'N/A')} mm Hg")
        st.markdown(f"**Fasting Blood Sugar > 120 mg/dl:** {'Yes' if user_data.get('fbs', 0) == 1 else 'No'}")
        st.markdown(f"**Max Heart Rate:** {user_data.get('thalach', 'N/A')} bpm")
        st.markdown(f"**Exercise Angina:** {'Yes' if user_data.get('exang', 0) == 1 else 'No'}")
    
    # Display prescription or recommendation data if available
    if 'prescription' in prediction:
        st.markdown("### Medical Advice")
        st.markdown("The following prescription or recommendation was generated based on your health assessment:")
        
        # Use the doctor_advice module to display the saved prescription
        display_saved_prescription(prediction['prescription'])
    else:
        st.info("No prescription or recommendation data is available for this prediction.")
        
    st.markdown("---")