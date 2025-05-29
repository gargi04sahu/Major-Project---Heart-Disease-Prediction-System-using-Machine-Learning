import pandas as pd
import numpy as np
import requests
import io
import os
from sklearn.preprocessing import StandardScaler

# Path to local dataset
DATASET_PATH = "data/heart.csv"

def load_data():
    """
    Load heart disease dataset from local file.
    If local file is not available, attempt to load from UCI repository as a fallback.
    """
    try:
        # Try to load the local dataset first
        if os.path.exists(DATASET_PATH):
            print(f"Loading data from local file: {DATASET_PATH}")
            data = pd.read_csv(DATASET_PATH)
            print("Data loaded successfully from local file.")
            return preprocess_raw_data(data)
        else:
            raise FileNotFoundError(f"Local dataset not found at {DATASET_PATH}")
    
    except Exception as e:
        print(f"Error loading local dataset: {e}")
        
        try:
            # Try to load from UCI repository as a fallback
            print("Attempting to fetch data from UCI repository...")
            
            response = requests.get("https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data")
            response.raise_for_status()
            
            # Define column names based on UCI heart disease dataset
            column_names = [
                'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
            ]
            
            # Read data from the response content
            data = pd.read_csv(
                io.StringIO(response.text), 
                names=column_names,
                na_values='?',
                delimiter=','
            )
            
            print("Data loaded successfully from UCI repository.")
            return preprocess_raw_data(data)
        
        except Exception as e:
            print(f"Error fetching data from UCI: {e}")
            raise Exception("Failed to load heart disease dataset")

def preprocess_raw_data(data):
    """
    Preprocess the raw dataset to handle missing values and convert features.
    """
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    # Handling the structured dataset format
    if 'Sex' in df.columns:  # New dataset format
        # Rename columns to match the expected format in the model
        column_mapping = {
            'Age': 'age',
            'Sex': 'sex',
            'ChestPainType': 'cp',
            'RestingBP': 'trestbps',
            'Cholesterol': 'chol',
            'FastingBS': 'fbs',
            'RestingECG': 'restecg',
            'MaxHR': 'thalach',
            'ExerciseAngina': 'exang',
            'Oldpeak': 'oldpeak',
            'ST_Slope': 'slope',
            'HeartDisease': 'target'
        }
        df = df.rename(columns=column_mapping)
        
        # Convert categorical variables to numeric
        # Sex: M -> 1, F -> 0
        df['sex'] = df['sex'].map({'M': 1, 'F': 0})
        
        # ChestPainType: convert to numeric (Typical Angina, Atypical Angina, Non-anginal Pain, Asymptomatic)
        cp_mapping = {
            'TA': 0,  # Typical Angina
            'ATA': 1,  # Atypical Angina
            'NAP': 2,  # Non-anginal Pain
            'ASY': 3   # Asymptomatic
        }
        df['cp'] = df['cp'].map(cp_mapping)
        
        # RestingECG: convert to numeric
        ecg_mapping = {
            'Normal': 0,
            'ST': 1,
            'LVH': 2
        }
        df['restecg'] = df['restecg'].map(ecg_mapping)
        
        # ExerciseAngina: Y -> 1, N -> 0
        df['exang'] = df['exang'].map({'Y': 1, 'N': 0})
        
        # ST_Slope: convert to numeric
        slope_mapping = {
            'Up': 0,
            'Flat': 1,
            'Down': 2
        }
        df['slope'] = df['slope'].map(slope_mapping)
    
    # Handle any missing values
    for col in df.columns:
        if df[col].dtype != 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fill any remaining missing values with median
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())
    
    # Map sex values back to string labels for display purposes
    if isinstance(df['sex'].iloc[0], (int, float)):
        df['sex'] = df['sex'].map({0: 'Female', 1: 'Male'})
    
    return df

def preprocess_data(data):
    """
    Prepare data for model training by extracting features and target.
    
    Args:
        data: Pandas DataFrame with heart disease data
    
    Returns:
        Tuple of (X, y) where X is the feature DataFrame and y is the target series
    """
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    # Convert sex back to binary for model training
    df['sex'] = df['sex'].map({'Female': 0, 'Male': 1})
    
    # Extract features and target
    y = df['target']
    
    # Select all columns except target for features
    X = df.drop(['target'], axis=1)
    
    # Drop any columns with missing values
    X = X.dropna(axis=1)
    
    return X, y

def get_real_time_data():
    """
    This function would connect to external APIs or databases to get real-time heart disease data.
    In a real application, this would pull from authorized medical data sources.
    """
    # This is a placeholder that would be replaced with actual API integration
    try:
        # Example of real-time data collection (not implemented)
        print("Fetching real-time heart disease data...")
        
        # For now, return None to indicate no real-time data is available
        return None
    
    except Exception as e:
        print(f"Error fetching real-time data: {e}")
        return None

if __name__ == "__main__":
    # Test data loading
    df = load_data()
    print(f"Loaded data shape: {df.shape}")
    print(df.head())
    
    # Test preprocessing
    X, y = preprocess_data(df)
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
