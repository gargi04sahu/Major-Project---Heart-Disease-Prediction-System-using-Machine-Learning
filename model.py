import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from data_processor import load_data, preprocess_data

# Path to save trained model
MODEL_PATH = "heart_disease_model.pkl"

def train_model():
    """
    Train a heart disease prediction model and save it to disk.
    Returns the trained model.
    """
    # Load and preprocess data
    df = load_data()
    X, y = preprocess_data(df)
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train a Random Forest classifier
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=2,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model and scaler
    model_data = {
        'model': model,
        'scaler': scaler,
        'features': X.columns.tolist()
    }
    joblib.dump(model_data, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    
    return model_data

def load_model():
    """
    Load the trained model from disk. If model doesn't exist, train a new one.
    """
    if os.path.exists(MODEL_PATH):
        try:
            model_data = joblib.load(MODEL_PATH)
            return model_data
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Training new model...")
            return train_model()
    else:
        print("Model not found. Training new model...")
        return train_model()

def predict_heart_disease(model_data, user_data):
    """
    Make heart disease prediction for user input data.
    
    Args:
        model_data: Dictionary containing model, scaler, and features
        user_data: DataFrame containing user input health metrics
    
    Returns:
        Tuple containing prediction (0 or 1) and probability
    """
    model = model_data['model']
    scaler = model_data['scaler']
    features = model_data['features']
    
    # Ensure user_data has the required features in the correct order
    user_data = user_data[features]
    
    # Preprocess the user data
    user_data_scaled = scaler.transform(user_data)
    
    # Make prediction
    prediction = model.predict(user_data_scaled)
    probability = model.predict_proba(user_data_scaled)
    
    return prediction, probability

if __name__ == "__main__":
    # Train and test the model
    train_model()
