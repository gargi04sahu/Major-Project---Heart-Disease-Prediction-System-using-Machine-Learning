import streamlit as st
import pandas as pd
from streamlit_extras.colored_header import colored_header

def get_personalized_doctor_prescription(user_data, risk_level):
    """
    Generate a personalized doctor's prescription based on the user's data and risk level.
    This would be shown only to users with high risk of heart disease.
    
    Args:
        user_data: DataFrame containing the user's health metrics
        risk_level: String indicating the predicted risk level ('High' or 'Low')
        
    Returns:
        Dictionary containing prescription details for database storage
    """
    # Extract key metrics from user data
    age = user_data['age'].values[0]
    gender = "Male" if user_data['sex'].values[0] == 1 else "Female"
    cholesterol = user_data['chol'].values[0]
    bp = user_data['trestbps'].values[0]
    fbs = "Yes" if user_data['fbs'].values[0] == 1 else "No"
    max_hr = user_data['thalach'].values[0]
    angina = "Yes" if user_data['exang'].values[0] == 1 else "No"
    
    # Create the prescription
    colored_header(
        label="Doctor's Prescription",
        description="Important medical advice based on your risk assessment",
        color_name="red-70"
    )
    
    st.markdown("### Medical Consultation Required")
    st.markdown("""
    Based on your risk assessment, it is strongly recommended that you consult with a healthcare 
    professional promptly. This prescription provides guidance for your discussion with your doctor.
    """)
    
    # Patient details section
    st.markdown("### Patient Details")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Age:** {age}")
        st.markdown(f"**Gender:** {gender}")
        st.markdown(f"**High Fasting Blood Sugar:** {fbs}")
    with col2:
        st.markdown(f"**Cholesterol Level:** {cholesterol} mg/dL")
        st.markdown(f"**Blood Pressure:** {bp} mm Hg")
        st.markdown(f"**Exercise-Induced Angina:** {angina}")
    
    # Recommended tests
    st.markdown("### Recommended Medical Tests")
    tests = [
        "**Complete Lipid Profile**: To assess cholesterol levels in detail, including LDL, HDL, and triglycerides.",
        "**Cardiac Stress Test**: To evaluate heart function during physical activity.",
        "**Echocardiogram**: To assess heart structure and function.",
        "**Electrocardiogram (ECG/EKG)**: To detect abnormalities in heart rhythm.",
        "**Blood Glucose Test**: To check for diabetes or pre-diabetes.",
    ]
    
    # Add coronary angiography for very high risk
    if cholesterol > 240 and bp > 140:
        tests.append("**Coronary Angiography**: To examine the condition of coronary arteries (based on elevated cholesterol and blood pressure).")
    
    for test in tests:
        st.markdown(f"- {test}")
    
    # Medication considerations
    st.markdown("### Medication Considerations")
    st.markdown("""
    The following medications might be prescribed by your doctor after proper evaluation:
    """)
    
    medications = []
    
    # Add medications based on specific conditions
    if cholesterol > 200:
        medications.append("**Statins**: To help lower cholesterol levels.")
    
    if bp > 130:
        medications.append("**Antihypertensives**: Such as ACE inhibitors, ARBs, or calcium channel blockers to manage blood pressure.")
    
    if angina == "Yes":
        medications.append("**Nitroglycerin**: To relieve chest pain.")
        medications.append("**Beta-blockers**: To reduce heart workload and improve blood flow.")
    
    medications.append("**Aspirin (low-dose)**: As a blood thinner to prevent clots, if deemed appropriate by your doctor.")
    
    for med in medications:
        st.markdown(f"- {med}")
    
    # Lifestyle modifications
    st.markdown("### Prescribed Lifestyle Modifications")
    
    lifestyle = [
        "**Diet**: Mediterranean diet rich in fruits, vegetables, whole grains, fish, and olive oil. Limit saturated fats, trans fats, and sodium.",
        "**Exercise**: Start with 10-15 minutes of light activity daily, gradually increasing to 30 minutes of moderate activity 5 days per week, as tolerated.",
        "**Stress Management**: Daily practice of stress reduction techniques such as deep breathing, meditation, or yoga.",
        "**Sleep**: Aim for 7-8 hours of quality sleep per night."
    ]
    
    # Add smoking cessation if applicable
    if user_data['exang'].values[0] == 1:  # Using exang as a proxy for smoking since we don't have direct smoking data
        lifestyle.append("**Smoking Cessation**: Immediate discontinuation of tobacco products. Ask your doctor about smoking cessation programs.")
    
    for item in lifestyle:
        st.markdown(f"- {item}")
    
    # Follow-up plan
    follow_up = [
        "Initial consultation with cardiologist within 1-2 weeks",
        "Complete recommended tests before follow-up appointment",
        "Schedule follow-up appointment in 4-6 weeks to review test results and adjust treatment plan",
        "Regular monitoring of blood pressure and heart rate at home",
        "Monthly check-ins for the first 3 months, then quarterly if condition stabilizes"
    ]
    
    st.markdown("### Follow-up Plan")
    for item in follow_up:
        st.markdown(f"- {item}")
    
    # Important disclaimer
    st.warning("""
    **Important Disclaimer**: This is a computer-generated prescription based on your risk assessment 
    and should not replace professional medical advice. Please consult with a qualified healthcare 
    provider for proper diagnosis and treatment. Seek immediate medical attention if you experience 
    chest pain, shortness of breath, or other concerning symptoms.
    """)
    
    # Prepare prescription data for database storage
    prescription_data = {
        "risk_level": "High",
        "patient_details": {
            "age": age,
            "gender": gender,
            "cholesterol": cholesterol,
            "blood_pressure": bp,
            "fasting_blood_sugar": fbs,
            "max_heart_rate": max_hr,
            "exercise_angina": angina
        },
        "recommended_tests": tests,
        "medications": medications,
        "lifestyle_modifications": lifestyle,
        "follow_up_plan": follow_up
    }
    
    return prescription_data


def display_health_recommendations_detailed(user_data, risk_level):
    """
    Display detailed health recommendations for users with low risk level.
    
    Args:
        user_data: DataFrame containing the user's health metrics
        risk_level: String indicating the predicted risk level ('High' or 'Low')
        
    Returns:
        Dictionary containing prescription details for database storage
    """
    # Extract key metrics from user data
    age = user_data['age'].values[0]
    gender = "Male" if user_data['sex'].values[0] == 1 else "Female"
    cholesterol = user_data['chol'].values[0]
    bp = user_data['trestbps'].values[0]
    fbs = user_data['fbs'].values[0] == 1
    
    colored_header(
        label="Health Recommendations",
        description="Personalized guidance to maintain your heart health",
        color_name="green-70"
    )
    
    st.markdown("### Good News!")
    st.markdown("""
    Your risk assessment indicates a lower risk of heart disease. However, heart health
    requires ongoing maintenance. Here are recommendations to help you maintain and 
    improve your heart health.
    """)
    
    # Preventive measures
    st.markdown("### Preventive Health Measures")
    
    preventive = [
        "**Annual Physical Examination**: Including blood pressure check, cholesterol screening, and blood glucose test.",
        "**Heart Health Screening**: Consider a baseline ECG after age 40.",
        "**Regular Blood Pressure Monitoring**: At home or at pharmacy kiosks.",
    ]
    
    for measure in preventive:
        st.markdown(f"- {measure}")
    
    # Diet recommendations
    st.markdown("### Diet Recommendations")
    
    diet_recs = [
        "**Mediterranean Diet**: Focus on fruits, vegetables, whole grains, fish, and olive oil.",
        "**Portion Control**: Be mindful of portion sizes to maintain healthy weight.",
        "**Hydration**: Drink plenty of water throughout the day.",
        "**Limit Processed Foods**: Reduce intake of processed foods high in sodium and unhealthy fats.",
    ]
    
    # Add specific recommendations based on metrics
    if cholesterol > 180:
        diet_recs.append("**Cholesterol Management**: Increase soluble fiber intake (oats, beans, fruits) and reduce saturated fats.")
    
    if bp > 120:
        diet_recs.append("**DASH Diet**: Consider following the DASH diet approach to help maintain healthy blood pressure.")
    
    if fbs:
        diet_recs.append("**Blood Sugar Management**: Limit refined carbohydrates and sugars; choose complex carbohydrates with lower glycemic index.")
    
    for rec in diet_recs:
        st.markdown(f"- {rec}")
    
    # Exercise recommendations
    st.markdown("### Exercise Recommendations")
    
    # Tailor exercise recommendations by age
    if age < 40:
        exercise_level = "at least 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity weekly"
    elif age < 65:
        exercise_level = "at least 150 minutes of moderate aerobic activity weekly, incorporating balance and flexibility exercises"
    else:
        exercise_level = "start with 10-15 minute sessions of light to moderate activity daily, gradually increasing as tolerated"
    
    exercise_recs = [
        f"**Regular Physical Activity**: Aim for {exercise_level}.",
        "**Strength Training**: Include muscle-strengthening activities at least twice per week.",
        "**Daily Movement**: Incorporate more movement throughout your day, such as taking stairs or walking short distances."
    ]
    
    for rec in exercise_recs:
        st.markdown(f"- {rec}")
    
    # Lifestyle recommendations
    st.markdown("### Lifestyle Recommendations")
    
    lifestyle_recs = [
        "**Stress Management**: Practice stress-reduction techniques such as meditation, deep breathing, or yoga.",
        "**Quality Sleep**: Aim for 7-8 hours of quality sleep each night.",
        "**Alcohol Moderation**: If you drink alcohol, do so in moderation (up to one drink per day for women and up to two for men).",
        "**Avoid Tobacco**: If you smoke, consider quitting. Avoid secondhand smoke when possible."
    ]
    
    for rec in lifestyle_recs:
        st.markdown(f"- {rec}")
    
    # Additional resources
    resources = [
        "American Heart Association (www.heart.org)",
        "CDC Heart Disease Resources (www.cdc.gov/heartdisease)",
        "Heart-Healthy Recipes (www.heartfoundation.org/recipes)",
        "Fitness Programs for Heart Health (www.cardiosmart.org)"
    ]
    
    st.markdown("### Additional Resources")
    for resource in resources:
        st.markdown(f"- {resource}")
    
    # Reminder
    st.info("""
    **Remember**: These are general recommendations to maintain heart health. Even with a low risk 
    assessment, regular check-ups with a healthcare provider are important for preventive care.
    """)
    
    # Prepare recommendation data for database storage
    prescription_data = {
        "risk_level": "Low",
        "patient_details": {
            "age": age,
            "gender": gender,
            "cholesterol": cholesterol,
            "blood_pressure": bp,
            "fasting_blood_sugar": "Elevated" if fbs else "Normal"
        },
        "preventive_measures": preventive,
        "diet_recommendations": diet_recs,
        "exercise_recommendations": exercise_recs,
        "lifestyle_recommendations": lifestyle_recs,
        "additional_resources": resources
    }
    
    return prescription_data


def display_saved_prescription(prescription_data):
    """
    Display a previously saved prescription or health recommendation.
    
    Args:
        prescription_data: Dictionary containing the saved prescription data
    """
    if not prescription_data:
        st.info("No prescription or recommendation data available for this prediction.")
        return
    
    risk_level = prescription_data.get("risk_level", "Unknown")
    
    if risk_level == "High":
        # Display high risk prescription
        colored_header(
            label="Doctor's Prescription",
            description="Important medical advice based on your risk assessment",
            color_name="red-70"
        )
        
        # Patient details if available
        if "patient_details" in prescription_data:
            st.markdown("### Patient Details")
            details = prescription_data["patient_details"]
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Age:** {details.get('age', 'N/A')}")
                st.markdown(f"**Gender:** {details.get('gender', 'N/A')}")
                st.markdown(f"**High Fasting Blood Sugar:** {details.get('fasting_blood_sugar', 'N/A')}")
            with col2:
                st.markdown(f"**Cholesterol Level:** {details.get('cholesterol', 'N/A')} mg/dL")
                st.markdown(f"**Blood Pressure:** {details.get('blood_pressure', 'N/A')} mm Hg")
                st.markdown(f"**Exercise-Induced Angina:** {details.get('exercise_angina', 'N/A')}")
        
        # Recommended tests
        if "recommended_tests" in prescription_data:
            st.markdown("### Recommended Medical Tests")
            for test in prescription_data["recommended_tests"]:
                st.markdown(f"- {test}")
        
        # Medication considerations
        if "medications" in prescription_data:
            st.markdown("### Medication Considerations")
            st.markdown("The following medications might be prescribed by your doctor after proper evaluation:")
            for med in prescription_data["medications"]:
                st.markdown(f"- {med}")
        
        # Lifestyle modifications
        if "lifestyle_modifications" in prescription_data:
            st.markdown("### Prescribed Lifestyle Modifications")
            for item in prescription_data["lifestyle_modifications"]:
                st.markdown(f"- {item}")
        
        # Follow-up plan
        if "follow_up_plan" in prescription_data:
            st.markdown("### Follow-up Plan")
            for item in prescription_data["follow_up_plan"]:
                st.markdown(f"- {item}")
        
        # Important disclaimer
        st.warning("""
        **Important Disclaimer**: This is a computer-generated prescription based on your risk assessment 
        and should not replace professional medical advice. Please consult with a qualified healthcare 
        provider for proper diagnosis and treatment. Seek immediate medical attention if you experience 
        chest pain, shortness of breath, or other concerning symptoms.
        """)
    
    elif risk_level == "Low":
        # Display low risk recommendations
        colored_header(
            label="Health Recommendations",
            description="Personalized guidance to maintain your heart health",
            color_name="green-70"
        )
        
        st.markdown("### Good News!")
        st.markdown("""
        Your risk assessment indicates a lower risk of heart disease. Here are recommendations 
        to help you maintain and improve your heart health.
        """)
        
        # Preventive measures
        if "preventive_measures" in prescription_data:
            st.markdown("### Preventive Health Measures")
            for measure in prescription_data["preventive_measures"]:
                st.markdown(f"- {measure}")
        
        # Diet recommendations
        if "diet_recommendations" in prescription_data:
            st.markdown("### Diet Recommendations")
            for rec in prescription_data["diet_recommendations"]:
                st.markdown(f"- {rec}")
        
        # Exercise recommendations
        if "exercise_recommendations" in prescription_data:
            st.markdown("### Exercise Recommendations")
            for rec in prescription_data["exercise_recommendations"]:
                st.markdown(f"- {rec}")
        
        # Lifestyle recommendations
        if "lifestyle_recommendations" in prescription_data:
            st.markdown("### Lifestyle Recommendations")
            for rec in prescription_data["lifestyle_recommendations"]:
                st.markdown(f"- {rec}")
        
        # Additional resources
        if "additional_resources" in prescription_data:
            st.markdown("### Additional Resources")
            for resource in prescription_data["additional_resources"]:
                st.markdown(f"- {resource}")
        
        # Reminder
        st.info("""
        **Remember**: These are general recommendations to maintain heart health. Even with a low risk 
        assessment, regular check-ups with a healthcare provider are important for preventive care.
        """)
    
    else:
        st.info("No detailed prescription or recommendation information available.")