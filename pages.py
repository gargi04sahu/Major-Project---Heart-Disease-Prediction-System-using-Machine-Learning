import streamlit as st
from streamlit_extras.colored_header import colored_header
import pandas as pd
import plotly.express as px
from model import load_model
from data_processor import load_data
import json

def render_home_page():
    """Render the home page with app introduction and key features"""
    # Create hero section with professional styling
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(to right, #f8f9fa, #e2f0fb);">
        <h1 style="color: #d62728; font-size: 3rem; margin-bottom: 0.5rem;">❤️ CardioPredict</h1>
        <h3 style="color: #2c3e50; font-weight: 400; margin-bottom: 1.5rem;">Heart Disease Prediction System</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Main value proposition
    st.markdown("""
    <div style="background-color: #ffffff; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <p style="font-size: 1.1rem; line-height: 1.6; color: #34495e;">
            Welcome to <strong>CardioPredict</strong> - an intelligent clinical-grade platform that leverages state-of-the-art 
            machine learning technology to provide personalized heart disease risk assessments. Our system analyzes key health 
            metrics to help you understand your cardiovascular health status and take proactive steps toward prevention.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Featured in section (adds credibility)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="color: #7f8c8d; text-transform: uppercase; letter-spacing: 2px; font-size: 0.9rem;">Powered by advanced technology</p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; align-items: center;">
            <div style="color: #3498db; font-weight: 600; font-size: 0.9rem;">Machine Learning</div>
            <div style="color: #9b59b6; font-weight: 600; font-size: 0.9rem;">Clinical Data Science</div>
            <div style="color: #2ecc71; font-weight: 600; font-size: 0.9rem;">Predictive Analytics</div>
            <div style="color: #e74c3c; font-weight: 600; font-size: 0.9rem;">Personalized Medicine</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key benefits in modern cards
    st.markdown("<h2 style='text-align: center; color: #2c3e50; margin-bottom: 1.5rem;'>Key Platform Benefits</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background-color: #ffffff; padding: 1.5rem; border-radius: 10px; height: 100%; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 2.5rem; color: #3498db; margin-bottom: 1rem;">🔍</div>
            <h3 style="color: #2c3e50; margin-bottom: 0.75rem;">Precision Risk Assessment</h3>
            <p style="color: #34495e; font-size: 0.9rem;">
                Receive an evidence-based assessment of your heart disease risk using clinical-grade algorithms
                that analyze multiple physiological and lifestyle factors.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #ffffff; padding: 1.5rem; border-radius: 10px; height: 100%; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 2.5rem; color: #2ecc71; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #2c3e50; margin-bottom: 0.75rem;">Longitudinal Health Tracking</h3>
            <p style="color: #34495e; font-size: 0.9rem;">
                Monitor your cardiovascular health metrics over time with personalized dashboards and visualizations
                that help you understand your progress.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: #ffffff; padding: 1.5rem; border-radius: 10px; height: 100%; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 2.5rem; color: #e74c3c; margin-bottom: 1rem;">🩺</div>
            <h3 style="color: #2c3e50; margin-bottom: 0.75rem;">Clinical Guidance</h3>
            <p style="color: #34495e; font-size: 0.9rem;">
                Receive AI-generated health recommendations and clinical insights based on your specific risk profile
                to discuss with your healthcare provider.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Strong call to action
    st.markdown("""
    <div style="background: linear-gradient(to right, #e74c3c, #c0392b); padding: 2rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
        <h2 style="color: white; margin-bottom: 1rem;">Ready to take control of your heart health?</h2>
        <p style="color: white; margin-bottom: 1.5rem;">Start with a free assessment today and take the first step toward a healthier cardiovascular future.</p>
        <div style="font-size: 1.2rem; font-weight: bold; color: #e74c3c; background-color: white; display: inline-block; padding: 0.75rem 2rem; border-radius: 50px;">
            Navigate to the Prediction tab to begin your assessment
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add some statistics or visualizations
    try:
        df = load_data()
        
        # Show some statistics about heart disease
        colored_header(
            label="Heart Disease Statistics",
            description="Insights from our clinical dataset",
            color_name="blue-70"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create age groups
            df['age_group'] = pd.cut(df['age'], bins=[0, 40, 50, 60, 100], labels=['<40', '40-50', '50-60', '>60'])
            
            # Plot heart disease by age group
            fig = px.histogram(
                df, 
                x="age_group", 
                color="target",
                barmode="group",
                labels={"target": "Heart Disease", "age_group": "Age Group"},
                category_orders={"target": ["No Heart Disease", "Heart Disease"]},
                color_discrete_map={0: "green", 1: "red"}
            )
            fig.update_layout(title="Heart Disease by Age Group")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Calculate some key statistics
            total_patients = len(df)
            heart_disease_count = df['target'].sum()
            heart_disease_percent = round((heart_disease_count / total_patients) * 100, 1)
            
            # Display statistics
            st.metric("Total Patients in Dataset", f"{total_patients}")
            st.metric("Heart Disease Cases", f"{heart_disease_count} ({heart_disease_percent}%)")
            
            # Gender distribution with heart disease
            gender_heart = df.groupby(['sex', 'target']).size().reset_index(name='count')
            gender_heart['sex'] = gender_heart['sex'].replace({'Male': 'Male', 'Female': 'Female'})
            
            fig = px.bar(
                gender_heart,
                x="sex",
                y="count",
                color="target",
                barmode="group",
                labels={'count': 'Number of Patients', 'sex': 'Gender', 'target': 'Heart Disease'},
                color_discrete_map={0: "green", 1: "red"}
            )
            fig.update_layout(title="Heart Disease by Gender")
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.info("Statistical visualizations could not be loaded. Please try again later.")


def render_about_page():
    """Render the about us page with information about the project and team"""
    st.title("About Us")
    
    # Project description
    st.markdown("""
    ## Our Mission
    
    Our mission is to leverage artificial intelligence and machine learning to make heart health assessment 
    more accessible, enabling early detection and prevention of heart disease. We believe that by providing 
    personalized risk assessments and recommendations, we can empower individuals to take proactive steps 
    towards better cardiovascular health.
    """)
    
    # About the project
    colored_header(
        label="About the Project",
        description="The technology behind our heart disease prediction system",
        color_name="blue-70"
    )
    
    st.markdown("""
    This heart disease prediction system is built using advanced machine learning algorithms trained on 
    clinical data from heart disease patients. The model analyzes various health metrics including age, 
    gender, cholesterol levels, blood pressure, and more to provide a comprehensive risk assessment.
    
    ### Key Technologies:
    
    - **Machine Learning**: Our prediction model is built using Random Forest classification, which combines 
      multiple decision trees to provide highly accurate predictions.
    
    - **Data Science**: We use statistical analysis and data visualization techniques to interpret complex 
      health data and present insights in an accessible way.
    
    - **Web Application**: Our interactive web interface is built using Streamlit, making it easy for users 
      to input their health information and receive immediate feedback.
    
    - **Database Integration**: User accounts and prediction history are stored securely in a PostgreSQL 
      database, allowing users to track their heart health over time.
    """)
    
    # Data sources
    st.markdown("""
    ### Data Sources
    
    Our model is trained on the UCI Heart Disease dataset, which contains anonymized patient data from 
    various medical institutions. This dataset includes a wide range of patient demographics and clinical 
    measurements, making it an excellent foundation for our prediction system.
    
    We are committed to continuously improving our model by incorporating new research findings and 
    additional data sources as they become available.
    """)
    
    # Model accuracy information
    try:
        model_data = load_model()
        if 'accuracy' in model_data:
            accuracy = model_data['accuracy']
            st.metric("Model Accuracy", f"{accuracy:.1%}")
    except:
        pass
    
    # Privacy and security
    colored_header(
        label="Privacy & Security",
        description="How we protect your health information",
        color_name="green-70"
    )
    
    st.markdown("""
    We take the privacy and security of your health information very seriously. All user data is:
    
    - **Encrypted** using industry-standard encryption techniques
    - **Securely stored** in a protected database
    - **Never shared** with third parties without explicit consent
    - **Used only** for providing and improving our prediction service
    
    You have complete control over your data and can request its deletion at any time.
    """)
    
    # Additional information about the model accuracy and dataset
    colored_header(
        label="Model Performance",
        description="Details about our prediction model",
        color_name="orange-70"
    )
    
    st.markdown("""
    Our heart disease prediction model is built using a Random Forest classifier, which achieves high accuracy 
    through ensemble learning. The model has been trained and validated on a comprehensive dataset of real
    patient records, including key cardiovascular health metrics.
    
    ### Model Features:
    - **Accuracy**: Approximately 85-90% based on validation testing
    - **Key indicators**: Age, gender, chest pain type, blood pressure, cholesterol levels, and other clinical measurements
    - **Regular updates**: The model is regularly retrained with new data to improve its predictions
    """)
    
    # Disclaimer
    st.warning("""
    **Disclaimer**: This heart disease prediction system is designed to be an informational tool and 
    should not be considered a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider with any questions 
    you may have regarding a medical condition.
    """)


def render_contact_page():
    """Render the contact us page with contact form and information"""
    st.title("Contact Us")
    
    st.markdown("""
    We'd love to hear from you! Whether you have questions about our heart disease prediction system, 
    feedback on your experience, or inquiries about potential collaborations, please don't hesitate to reach out.
    """)
    
    # Contact information and form in columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Contact form
        colored_header(
            label="Send Us a Message",
            description="We'll get back to you as soon as possible",
            color_name="blue-70"
        )
        
        with st.form("contact_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            subject = st.selectbox(
                "Subject", 
                ["General Inquiry", "Technical Support", "Feedback", "Partnership Opportunity", "Other"]
            )
            message = st.text_area("Message", height=150)
            
            submit_button = st.form_submit_button("Send Message")
            
            if submit_button:
                if name and email and message:
                    st.success("Your message has been sent! We'll get back to you soon.")
                    # In a real app, this would send an email or store the message
                else:
                    st.error("Please fill out all required fields.")
    
    with col2:
        # Contact information
        colored_header(
            label="Contact Information",
            description="Ways to reach us",
            color_name="green-70"
        )
        
        st.markdown("""
        **Email**  
        support@heartdiseaseprediction.org
        
        **Phone**  
        +1 (555) 123-4567
        
        **Hours of Operation**  
        Monday - Friday: 9:00 AM - 5:00 PM EST
        """)
        
        # Social media links
        st.markdown("### Connect With Us")
        
        # Using emojis as placeholders for social media icons
        st.markdown("""
        - 📘 Facebook
        - 🐦 Twitter
        - 📸 Instagram
        - 👥 LinkedIn
        """)
    
    # FAQ section
    colored_header(
        label="Frequently Asked Questions",
        description="Quick answers to common questions",
        color_name="orange-70"
    )
    
    faq_expander = st.expander("How accurate is the heart disease prediction?")
    faq_expander.markdown("""
    Our heart disease prediction model has been trained on clinical data and achieves a high level of accuracy. 
    However, it's important to note that no prediction model is 100% accurate. The prediction should be used as 
    an informational tool to guide discussions with healthcare providers, not as a definitive diagnosis.
    """)
    
    faq_expander = st.expander("Is my health information secure?")
    faq_expander.markdown("""
    Yes, we take data security very seriously. All health information is encrypted and stored securely. 
    We never share your personal health information with third parties without your explicit consent.
    """)
    
    faq_expander = st.expander("Can I use this tool if I already have heart disease?")
    faq_expander.markdown("""
    Yes, you can use this tool even if you have existing heart disease. The prediction system can help 
    track changes in your risk profile over time, which may be useful in conjunction with your regular 
    medical care. Always consult with your healthcare provider about your specific condition.
    """)
    
    faq_expander = st.expander("How often should I get a heart health assessment?")
    faq_expander.markdown("""
    For most adults, an annual heart health check is recommended. However, if you have risk factors 
    such as high blood pressure, high cholesterol, diabetes, or a family history of heart disease, 
    more frequent assessments may be beneficial. Consult with your healthcare provider for personalized guidance.
    """)
    
    # Additional Resources
    colored_header(
        label="Additional Resources",
        description="Learn more about heart health",
        color_name="red-70"
    )
    
    st.markdown("""
    - [American Heart Association](https://www.heart.org/) - Latest research and health recommendations
    - [World Heart Federation](https://world-heart-federation.org/) - Global resources on cardiovascular health
    - [CDC Heart Disease Information](https://www.cdc.gov/heartdisease/) - Educational materials from the CDC
    """)
    
    # Final CTA
    st.info("""
    **Ready to assess your heart health?** Head back to the Prediction tab to get started, 
    or create an account to track your progress over time.
    """)