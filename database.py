import os
import sqlalchemy as db
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import bcrypt
import json
import streamlit as st

# Create base class for models
Base = declarative_base()

# Database connection flag to track connection status
db_connected = False
engine = None
Session = None

# Try to create database connection
try:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL:
        engine = db.create_engine(DATABASE_URL)
        # Test connection
        with engine.connect() as conn:
            db_connected = True
        Session = sessionmaker(bind=engine)
except Exception as e:
    st.warning(f"Running in offline mode - database features are disabled. Please activate your Neon database endpoint.")
    # For debugging: st.error(f"Database connection error: {str(e)}")

# Define User model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    predictions = relationship("PredictionHistory", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash password before storing"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against stored hash"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)

# Define Prediction History model
class PredictionHistory(Base):
    __tablename__ = 'prediction_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    prediction_date = Column(DateTime, default=datetime.utcnow)
    risk_level = Column(String(10), nullable=False)  # "High" or "Low"
    probability = Column(Float, nullable=False)  # Probability of prediction
    user_data = Column(Text, nullable=False)  # Store user input as JSON
    prescription = Column(Text, nullable=True)  # Store doctor's prescription or recommendations
    
    user = relationship("User", back_populates="predictions")
    
    def set_user_data(self, user_data_dict):
        """Convert user data dictionary to JSON string for storage"""
        self.user_data = json.dumps(user_data_dict)
    
    def get_user_data(self):
        """Convert stored JSON string back to dictionary"""
        return json.loads(self.user_data)
    
    def set_prescription(self, prescription_dict):
        """Convert prescription dictionary to JSON string for storage"""
        self.prescription = json.dumps(prescription_dict)
    
    def get_prescription(self):
        """Convert stored JSON string back to dictionary"""
        if self.prescription:
            return json.loads(self.prescription)
        return None

# Create tables if database is connected
if engine:
    try:
        Base.metadata.create_all(engine)
        # Create session factory if connection successful
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        st.warning("Could not create database tables. Some features will be limited.")
        db_connected = False
else:
    # Fallback for when database is not available
    SessionLocal = None
    db_connected = False

def get_db_session():
    """Return a database session"""
    if not db_connected or SessionLocal is None:
        return None
        
    try:
        session = SessionLocal()
        return session
    except Exception as e:
        # If we can't create a session, database connection may be down
        return None

# User management functions
def create_user(username, email, password):
    """Create a new user account"""
    session = get_db_session()
    try:
        # Check if username or email already exists
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            session.close()
            return False, "Username or email already exists"
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        session.add(user)
        session.commit()
        session.close()
        
        return True, "User created successfully"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error creating user: {str(e)}"

def authenticate_user(username, password):
    """Authenticate a user by username and password"""
    session = get_db_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        
        if user and user.check_password(password):
            result = True, user.id
        else:
            result = False, None
        
        session.close()
        return result
    except Exception as e:
        session.close()
        return False, None

def save_prediction(user_id, risk_level, probability, user_data, prescription=None):
    """Save a prediction to the user's history with optional prescription data"""
    session = get_db_session()
    try:
        prediction = PredictionHistory(
            user_id=user_id,
            risk_level=risk_level,
            probability=probability
        )
        prediction.set_user_data(user_data)
        
        # Add prescription if provided
        if prescription:
            prediction.set_prescription(prescription)
        
        session.add(prediction)
        session.commit()
        session.close()
        
        return True, prediction.id
    except Exception as e:
        session.rollback()
        session.close()
        return False, None

def get_user_predictions(user_id, limit=10):
    """Get a user's prediction history including prescription data"""
    session = get_db_session()
    try:
        predictions = session.query(PredictionHistory).filter(
            PredictionHistory.user_id == user_id
        ).order_by(PredictionHistory.prediction_date.desc()).limit(limit).all()
        
        result = []
        for pred in predictions:
            prediction_data = {
                'id': pred.id,
                'date': pred.prediction_date,
                'risk_level': pred.risk_level,
                'probability': pred.probability,
                'user_data': pred.get_user_data()
            }
            
            # Add prescription data if it exists
            if pred.prescription:
                prediction_data['prescription'] = pred.get_prescription()
            
            result.append(prediction_data)
        
        session.close()
        return result
    except Exception as e:
        session.close()
        return []

def get_user_by_id(user_id):
    """Get user by ID"""
    session = get_db_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        return user
    except Exception as e:
        session.close()
        return None
        
def get_prediction_by_id(prediction_id):
    """Get a single prediction by ID"""
    session = get_db_session()
    try:
        pred = session.query(PredictionHistory).filter(PredictionHistory.id == prediction_id).first()
        
        if not pred:
            session.close()
            return None
            
        prediction_data = {
            'id': pred.id,
            'date': pred.prediction_date,
            'risk_level': pred.risk_level,
            'probability': pred.probability,
            'user_data': pred.get_user_data()
        }
        
        # Add prescription data if it exists
        if pred.prescription:
            prediction_data['prescription'] = pred.get_prescription()
        
        session.close()
        return prediction_data
    except Exception as e:
        session.close()
        return None