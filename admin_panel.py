import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlite_database import get_all_users, get_all_predictions, get_prediction_details
from session_state import is_admin, get_current_user_id

def render_admin_panel():
    """Render the admin panel with user management and data insights"""
    if not is_admin():
        st.error("Access denied. You must be an administrator to view this page.")
        return
    
    st.title("🔐 Admin Panel")
    
    # Admin dashboard tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "👥 User Management", "📋 Prediction History"])
    
    with tab1:
        render_admin_dashboard()
    
    with tab2:
        render_user_management()
    
    with tab3:
        render_prediction_history()

def render_admin_dashboard():
    """Render the admin dashboard with key metrics and charts"""
    st.header("Dashboard")
    
    # Get all users and predictions for analytics
    users = get_all_users()
    predictions = get_all_predictions()
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", len(users))
    
    with col2:
        st.metric("Total Predictions", len(predictions))
    
    with col3:
        # Calculate high risk percentage
        high_risk_count = sum(1 for p in predictions if p['risk_level'] == 'High')
        high_risk_percentage = (high_risk_count / len(predictions)) * 100 if predictions else 0
        st.metric("High Risk Patients", f"{high_risk_percentage:.1f}%")
    
    # Create user signup trend chart
    if users:
        st.subheader("User Registration Trend")
        
        # Convert to DataFrame for charting
        df_users = pd.DataFrame(users)
        df_users['date'] = pd.to_datetime(df_users['created_at']).dt.date
        user_counts = df_users.groupby('date').size().reset_index(name='count')
        
        fig = px.line(
            user_counts, 
            x='date', 
            y='count',
            title='User Registrations Over Time',
            labels={'count': 'Number of Registrations', 'date': 'Date'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Create risk distribution chart
    if predictions:
        st.subheader("Risk Level Distribution")
        
        # Convert to DataFrame for charting
        df_predictions = pd.DataFrame(predictions)
        risk_counts = df_predictions.groupby('risk_level').size().reset_index(name='count')
        
        fig = px.pie(
            risk_counts,
            values='count',
            names='risk_level',
            title='Distribution of Risk Levels',
            color='risk_level',
            color_discrete_map={'High': '#e74c3c', 'Low': '#2ecc71'}
        )
        st.plotly_chart(fig, use_container_width=True)

def render_user_management():
    """Render the user management section"""
    st.header("User Management")
    
    # Get all users
    users = get_all_users()
    
    if not users:
        st.info("No users found.")
        return
    
    # Convert to DataFrame for display
    df_users = pd.DataFrame(users)
    
    # Format the created_at column
    df_users['created_at'] = pd.to_datetime(df_users['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Rename and reorder columns
    df_users = df_users.rename(columns={
        'id': 'ID',
        'username': 'Username',
        'email': 'Email',
        'is_admin': 'Admin',
        'created_at': 'Created At'
    })
    
    # Display users table
    st.dataframe(df_users[['ID', 'Username', 'Email', 'Admin', 'Created At']], use_container_width=True)

def render_prediction_history():
    """Render the prediction history section with enhanced analytics and visualization"""
    st.header("Prediction History Analytics")
    
    # Get all predictions
    predictions = get_all_predictions()
    
    if not predictions:
        st.info("No predictions found.")
        return
    
    # Convert to DataFrame for display
    df_predictions = pd.DataFrame(predictions)
    df_predictions['date'] = pd.to_datetime(df_predictions['prediction_date'])
    
    # Add quick stats at the top
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        st.markdown(f"""
        <div style="background-color: #f5f9fa; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #e0e0e0;">
            <h4 style="margin: 0; color: #0cb8b6;">Total Tests</h4>
            <h2 style="margin: 10px 0; color: #325C6A;">{len(predictions)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col2:
        high_risk_count = sum(1 for p in predictions if p['risk_level'] == 'High')
        high_risk_percent = (high_risk_count / len(predictions) * 100) if predictions else 0
        st.markdown(f"""
        <div style="background-color: #ffebee; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #e0e0e0;">
            <h4 style="margin: 0; color: #e74c3c;">High Risk</h4>
            <h2 style="margin: 10px 0; color: #325C6A;">{high_risk_count} ({high_risk_percent:.1f}%)</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col3:
        low_risk_count = sum(1 for p in predictions if p['risk_level'] == 'Low')
        low_risk_percent = (low_risk_count / len(predictions) * 100) if predictions else 0
        st.markdown(f"""
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #e0e0e0;">
            <h4 style="margin: 0; color: #2ecc71;">Low Risk</h4>
            <h2 style="margin: 10px 0; color: #325C6A;">{low_risk_count} ({low_risk_percent:.1f}%)</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col4:
        unique_users = len(set(p['user_id'] for p in predictions))
        st.markdown(f"""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #e0e0e0;">
            <h4 style="margin: 0; color: #2196f3;">Unique Users</h4>
            <h2 style="margin: 10px 0; color: #325C6A;">{unique_users}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Create data visualization tabs
    st.markdown("### Prediction Analytics")
    trend_tabs = st.tabs(["Timeline Analysis", "User Distribution", "Risk Factors"])
    
    with trend_tabs[0]:
        # Timeline analysis
        st.markdown("#### Prediction Trends Over Time")
        
        # Group predictions by date and risk level
        df_predictions['date_only'] = df_predictions['date'].dt.date
        daily_counts = df_predictions.groupby(['date_only', 'risk_level']).size().reset_index(name='count')
        
        # Create a line chart showing prediction trends over time by risk level
        fig = px.line(
            daily_counts,
            x='date_only',
            y='count',
            color='risk_level',
            title='Predictions Over Time by Risk Level',
            labels={'count': 'Number of Predictions', 'date_only': 'Date', 'risk_level': 'Risk Level'},
            color_discrete_map={'High': '#e74c3c', 'Low': '#2ecc71'}
        )
        
        # Improve the chart appearance
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Predictions",
            legend_title="Risk Level",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with trend_tabs[1]:
        # User distribution analysis
        st.markdown("#### Predictions by User")
        
        # Group predictions by user and risk level
        user_counts = df_predictions.groupby(['username', 'risk_level']).size().reset_index(name='count')
        
        # Create a bar chart showing predictions by user and risk level
        fig = px.bar(
            user_counts,
            x='username',
            y='count',
            color='risk_level',
            title='Predictions by User and Risk Level',
            labels={'count': 'Number of Predictions', 'username': 'Username', 'risk_level': 'Risk Level'},
            color_discrete_map={'High': '#e74c3c', 'Low': '#2ecc71'}
        )
        
        # Improve the chart appearance
        fig.update_layout(
            xaxis_title="Username",
            yaxis_title="Number of Predictions",
            legend_title="Risk Level",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with trend_tabs[2]:
        # Risk factors analysis (placeholder for future implementation)
        st.markdown("#### Common Risk Factors")
        
        # This would require examining the user_data in each prediction
        # to identify common factors among high risk predictions
        st.info("This analysis will be implemented in a future update.")
    
    # Add searchable prediction table
    st.markdown("### Prediction Records")
    
    # Add filter functionality
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        risk_filter = st.selectbox("Filter by Risk Level", options=["All", "High", "Low"])
    with filter_col2:
        user_list = ["All"] + sorted(df_predictions['username'].unique().tolist())
        user_filter = st.selectbox("Filter by User", options=user_list)
    
    # Format the date column
    df_predictions['formatted_date'] = df_predictions['date'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Format the probability column
    df_predictions['formatted_probability'] = df_predictions['probability'].apply(lambda x: f"{x:.2%}")
    
    # Apply filters
    filtered_df = df_predictions.copy()
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    if user_filter != "All":
        filtered_df = filtered_df[filtered_df['username'] == user_filter]
    
    # Rename columns for display
    display_df = filtered_df.rename(columns={
        'id': 'ID',
        'user_id': 'User ID',
        'username': 'Username',
        'formatted_date': 'Date',
        'risk_level': 'Risk Level',
        'formatted_probability': 'Probability'
    })
    
    # Display predictions table
    st.dataframe(
        display_df[['ID', 'Username', 'Date', 'Risk Level', 'Probability']], 
        use_container_width=True,
        height=300
    )
    
    # Detailed prediction view
    st.markdown("### Detailed Prediction View")
    
    # Only show selector if there are predictions
    if not filtered_df.empty:
        selected_prediction = st.selectbox(
            "Select a prediction to view details:",
            options=filtered_df['id'].tolist(),
            format_func=lambda x: f"ID: {x} - User: {filtered_df[filtered_df['id'] == x]['username'].values[0]} - Date: {filtered_df[filtered_df['id'] == x]['formatted_date'].values[0]}"
        )
        
        if st.button("View Complete Details", use_container_width=True):
            prediction_details = get_prediction_details(selected_prediction)
            
            if prediction_details:
                # Show prediction details in a styled card
                risk_color = "#e74c3c" if prediction_details['risk_level'] == "High" else "#2ecc71"
                
                st.markdown(f"""
                <div style="background-color: #f5f9fa; padding: 15px; border-radius: 10px; margin-top: 20px; border-left: 4px solid {risk_color};">
                    <h3 style="color: #325C6A; margin-top: 0;">Prediction #{prediction_details['id']} Details</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; height: 100%;">
                    """, unsafe_allow_html=True)
                    
                    st.markdown("#### User Information")
                    st.markdown(f"**Username:** {prediction_details.get('username', 'Unknown')}")
                    st.markdown(f"**Email:** {prediction_details.get('email', 'Unknown')}")
                    st.markdown(f"**Date:** {prediction_details['date'].strftime('%Y-%m-%d %H:%M') if isinstance(prediction_details['date'], datetime) else prediction_details['date']}")
                    
                    st.markdown(f"""
                    <div style="margin: 15px 0; padding: 10px; border-radius: 5px; background-color: {risk_color}20; border-left: 4px solid {risk_color};">
                        <h4 style="margin: 0; color: {risk_color};">Risk Assessment</h4>
                        <p style="margin: 5px 0;"><strong>Risk Level:</strong> {prediction_details['risk_level']}</p>
                        <p style="margin: 5px 0;"><strong>Probability:</strong> {prediction_details['probability']:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; height: 100%;">
                    """, unsafe_allow_html=True)
                    
                    st.markdown("#### Key Health Metrics")
                    user_data = prediction_details['user_data']
                    
                    metrics_data = [
                        {"name": "Age", "value": user_data.get('age', 'N/A'), "unit": "years"},
                        {"name": "Gender", "value": 'Male' if user_data.get('sex', 0) == 1 else 'Female', "unit": ""},
                        {"name": "Cholesterol", "value": user_data.get('chol', 'N/A'), "unit": "mg/dL"},
                        {"name": "Blood Pressure", "value": user_data.get('trestbps', 'N/A'), "unit": "mm Hg"},
                        {"name": "Fasting Blood Sugar > 120", "value": 'Yes' if user_data.get('fbs', 0) == 1 else 'No', "unit": ""},
                        {"name": "Max Heart Rate", "value": user_data.get('thalach', 'N/A'), "unit": "bpm"},
                        {"name": "Exercise Angina", "value": 'Yes' if user_data.get('exang', 0) == 1 else 'No', "unit": ""}
                    ]
                    
                    for metric in metrics_data:
                        unit_display = f" {metric['unit']}" if metric['unit'] else ""
                        st.markdown(f"**{metric['name']}:** {metric['value']}{unit_display}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Display complete health metrics
                st.markdown("#### Complete Health Metrics")
                
                if user_data:
                    # Map numeric codes to human-readable values
                    cp_map = {0: 'Typical Angina', 1: 'Atypical Angina', 2: 'Non-anginal Pain', 3: 'Asymptomatic'}
                    ecg_map = {0: 'Normal', 1: 'ST-T Wave Abnormality', 2: 'Left Ventricular Hypertrophy'}
                    slope_map = {1: 'Upsloping', 2: 'Flat', 3: 'Downsloping'}
                    thal_map = {1: 'Normal', 2: 'Fixed Defect', 3: 'Reversible Defect'}
                    
                    # Create a more readable format for display
                    user_inputs = pd.DataFrame({
                        'Metric': [
                            'Age',
                            'Gender',
                            'Chest Pain Type',
                            'Resting Blood Pressure',
                            'Cholesterol',
                            'Fasting Blood Sugar > 120 mg/dl',
                            'Resting ECG',
                            'Maximum Heart Rate',
                            'Exercise Angina',
                            'ST Depression',
                            'Slope of ST Segment',
                            'Number of Major Vessels',
                            'Thalassemia'
                        ],
                        'Value': [
                            user_data.get('age', 'N/A'),
                            'Male' if user_data.get('sex', 0) == 1 else 'Female',
                            cp_map.get(user_data.get('cp', 'N/A'), 'N/A'),
                            f"{user_data.get('trestbps', 'N/A')} mm Hg",
                            f"{user_data.get('chol', 'N/A')} mg/dl",
                            'Yes' if user_data.get('fbs', 0) == 1 else 'No',
                            ecg_map.get(user_data.get('restecg', 'N/A'), 'N/A'),
                            f"{user_data.get('thalach', 'N/A')} bpm",
                            'Yes' if user_data.get('exang', 0) == 1 else 'No',
                            user_data.get('oldpeak', 'N/A'),
                            slope_map.get(user_data.get('slope', 'N/A'), 'N/A'),
                            user_data.get('ca', 'N/A'),
                            thal_map.get(user_data.get('thal', 'N/A'), 'N/A')
                        ]
                    })
                    
                    # Display metrics in a clean table
                    st.dataframe(user_inputs, use_container_width=True, hide_index=True)
                
                # Display prescription if available
                if 'prescription' in prediction_details and prediction_details['prescription']:
                    st.markdown(f"""
                    <div style="background-color: #f5f9fa; padding: 15px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #0cb8b6;">
                        <h3 style="color: #325C6A; margin-top: 0;">Prescription & Recommendations</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        prescription = prediction_details['prescription']
                        
                        if isinstance(prescription, dict):
                            rec_col1, rec_col2 = st.columns(2)
                            
                            with rec_col1:
                                if 'lifestyle_changes' in prescription:
                                    st.markdown("#### Lifestyle Recommendations")
                                    for item in prescription['lifestyle_changes']:
                                        st.markdown(f"- {item}")
                            
                            with rec_col2:
                                if 'medical_advice' in prescription:
                                    st.markdown("#### Medical Advice")
                                    for item in prescription['medical_advice']:
                                        st.markdown(f"- {item}")
                            
                            if 'followup' in prescription:
                                st.markdown("#### Follow-up Recommendations")
                                st.markdown(prescription['followup'])
                        else:
                            st.json(prescription)
                    except:
                        st.json(prediction_details['prescription'])
                else:
                    st.info("No prescription data available for this prediction.")