import os
import sqlite3
import bcrypt
import json
import streamlit as st
from datetime import datetime

# Database file
DB_FILE = 'cardiopredict.db'

# Global connection flag
db_connected = False

# Make the database connection thread-safe for Streamlit
def get_connection():
    """Get a new database connection for the current thread"""
    try:
        # Use check_same_thread=False to allow access from multiple threads
        # This is safe for read operations and limited concurrent writes
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        return conn
    except Exception as e:
        print(f"Error connecting to SQLite database: {e}")
        return None

def create_tables():
    """Create tables if they don't exist"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Create users table
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Create prediction history table
    predictions_table = """
    CREATE TABLE IF NOT EXISTS prediction_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        risk_level TEXT NOT NULL,
        probability REAL NOT NULL,
        user_data TEXT NOT NULL,
        prescription TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
    
    try:
        cursor.execute(users_table)
        cursor.execute(predictions_table)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_admin_user():
    """Create admin user if it doesn't exist"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Check if admin user exists
    check_admin = "SELECT * FROM users WHERE username = 'admin'"
    
    try:
        cursor.execute(check_admin)
        admin = cursor.fetchone()
        
        if not admin:
            # Create admin user with fixed credentials
            admin_password = "admin123"  # Fixed admin password
            password_bytes = admin_password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            
            insert_admin = """
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (?, ?, ?, ?)
            """
            
            cursor.execute(insert_admin, ('admin', 'admin@cardiopredict.com', hashed_password, 1))
            conn.commit()
            print("Admin user created successfully")
        
        return True
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_user(username, email, password):
    """Create a new user account"""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed. Please try again later."
    
    cursor = conn.cursor()
    
    try:
        # Check if username or email already exists
        check_query = "SELECT * FROM users WHERE username = ? OR email = ?"
        cursor.execute(check_query, (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return False, "Username or email already exists"
        
        # Hash password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        # Create new user
        insert_query = """
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)
        """
        
        cursor.execute(insert_query, (username, email, hashed_password, 0))
        conn.commit()
        
        return True, "User created successfully"
    except Exception as e:
        conn.rollback()
        return False, f"Error creating user: {str(e)}"
    finally:
        cursor.close()
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user by username and password"""
    # Demo login for testing
    if username == "demo" and password == "demo":
        return True, 999, False
    
    # Admin login for offline testing
    if username == "admin" and password == "admin123":
        return True, 1, True
    
    conn = get_connection()
    if not conn:
        return False, None, False
    
    cursor = conn.cursor()
    
    try:
        # Get user by username
        query = "SELECT id, password_hash, is_admin FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if user:
            user_id, stored_hash, is_admin = user
            password_bytes = password.encode('utf-8')
            hash_bytes = stored_hash.encode('utf-8')
            
            if bcrypt.checkpw(password_bytes, hash_bytes):
                return True, user_id, bool(is_admin)
        
        return False, None, False
    except Exception as e:
        print(f"Authentication error: {e}")
        return False, None, False
    finally:
        cursor.close()
        conn.close()

def save_prediction(user_id, risk_level, probability, user_data, prescription=None):
    """Save a prediction to the user's history with optional prescription data"""
    if user_id == 999:  # 999 is demo user ID
        st.info("Prediction cannot be saved while in demo mode.")
        return True, None
    
    conn = get_connection()
    if not conn:
        return False, None
    
    cursor = conn.cursor()
    
    try:
        # Convert dictionaries to JSON strings
        user_data_json = json.dumps(user_data)
        prescription_json = json.dumps(prescription) if prescription else None
        
        # Insert prediction
        insert_query = """
        INSERT INTO prediction_history (user_id, risk_level, probability, user_data, prescription)
        VALUES (?, ?, ?, ?, ?)
        """
        
        cursor.execute(insert_query, (user_id, risk_level, float(probability), user_data_json, prescription_json))
        conn.commit()
        
        # Get the prediction ID
        prediction_id = cursor.lastrowid
        
        return True, prediction_id
    except Exception as e:
        conn.rollback()
        return False, None
    finally:
        cursor.close()
        conn.close()

def get_user_predictions(user_id, limit=10):
    """Get a user's prediction history including prescription data"""
    if user_id == 999:  # 999 is demo user ID
        return []
    
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    try:
        # Get user predictions
        query = """
        SELECT * FROM prediction_history 
        WHERE user_id = ? 
        ORDER BY prediction_date DESC 
        LIMIT ?
        """
        
        cursor.execute(query, (user_id, limit))
        predictions = cursor.fetchall()
        
        # Process predictions
        result = []
        for p in predictions:
            p_id, p_user_id, p_date, p_risk, p_prob, p_data, p_prescription = p
            
            # Convert JSON strings back to dictionaries
            user_data = json.loads(p_data) if p_data else {}
            prescription = json.loads(p_prescription) if p_prescription else None
            
            prediction_data = {
                'id': p_id,
                'date': p_date,
                'risk_level': p_risk,
                'probability': p_prob,
                'user_data': user_data,
                'prescription': prescription
            }
            result.append(prediction_data)
        
        return result
    except Exception as e:
        print(f"Error getting user predictions: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    """Get user by ID"""
    # Demo user
    if user_id == 999:
        return {'id': 999, 'username': 'demo', 'email': 'demo@example.com', 'is_admin': False}
    
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        query = "SELECT id, username, email, is_admin FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'is_admin': bool(user[3])
            }
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_prediction_by_id(prediction_id):
    """Get a single prediction by ID"""
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        query = "SELECT * FROM prediction_history WHERE id = ?"
        cursor.execute(query, (prediction_id,))
        prediction = cursor.fetchone()
        
        if prediction:
            p_id, p_user_id, p_date, p_risk, p_prob, p_data, p_prescription = prediction
            
            # Convert JSON strings back to dictionaries
            user_data = json.loads(p_data) if p_data else {}
            prescription = json.loads(p_prescription) if p_prescription else None
            
            prediction_data = {
                'id': p_id,
                'user_id': p_user_id,
                'date': p_date,
                'risk_level': p_risk,
                'probability': p_prob,
                'user_data': user_data,
                'prescription': prescription
            }
            
            return prediction_data
        else:
            return None
    except Exception as e:
        print(f"Error getting prediction: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_users():
    """Get all users (for admin panel)"""
    # Return demo data if database connection fails
    fallback_data = [
        {'id': 1, 'username': 'admin', 'email': 'admin@cardiopredict.com', 'is_admin': True, 'created_at': datetime.now()},
        {'id': 2, 'username': 'user1', 'email': 'user1@example.com', 'is_admin': False, 'created_at': datetime.now()},
        {'id': 3, 'username': 'user2', 'email': 'user2@example.com', 'is_admin': False, 'created_at': datetime.now()}
    ]
    
    conn = get_connection()
    if not conn:
        return fallback_data
    
    cursor = conn.cursor()
    
    try:
        query = "SELECT id, username, email, is_admin, created_at FROM users ORDER BY id"
        cursor.execute(query)
        users = cursor.fetchall()
        
        result = []
        for user in users:
            user_dict = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'is_admin': bool(user[3]),
                'created_at': user[4]
            }
            result.append(user_dict)
            
        return result if result else fallback_data
    except Exception as e:
        print(f"Error getting all users: {e}")
        return fallback_data
    finally:
        cursor.close()
        conn.close()

def get_all_predictions():
    """Get all predictions (for admin panel)"""
    # Return demo data if database connection fails
    fallback_data = [
        {
            'id': 1, 
            'user_id': 2, 
            'username': 'user1',
            'prediction_date': datetime.now(), 
            'risk_level': 'High', 
            'probability': 0.85
        },
        {
            'id': 2, 
            'user_id': 3, 
            'username': 'user2',
            'prediction_date': datetime.now(), 
            'risk_level': 'Low', 
            'probability': 0.25
        }
    ]
    
    conn = get_connection()
    if not conn:
        return fallback_data
    
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT p.id, p.user_id, u.username, p.prediction_date, p.risk_level, p.probability
        FROM prediction_history p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.prediction_date DESC
        """
        
        cursor.execute(query)
        predictions = cursor.fetchall()
        
        result = []
        for p in predictions:
            pred_dict = {
                'id': p[0],
                'user_id': p[1],
                'username': p[2],
                'prediction_date': p[3],
                'risk_level': p[4],
                'probability': p[5]
            }
            result.append(pred_dict)
            
        return result if result else fallback_data
    except Exception as e:
        print(f"Error getting all predictions: {e}")
        return fallback_data
    finally:
        cursor.close()
        conn.close()

def get_prediction_details(prediction_id):
    """Get detailed prediction data for admin view"""
    prediction = get_prediction_by_id(prediction_id)
    
    if prediction:
        # Get the user who made this prediction
        user = get_user_by_id(prediction['user_id'])
        
        if user:
            prediction['username'] = user['username']
            prediction['email'] = user['email']
        
        return prediction
    
    return None

# Initialize database
try:
    conn = get_connection()
    if conn:
        db_connected = True
        print("Connected to SQLite database")
        create_tables()
        create_admin_user()
        conn.close()
except Exception as e:
    print(f"Error initializing database: {e}")