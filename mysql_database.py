import os
import mysql.connector
from mysql.connector import Error
import bcrypt
import json
import streamlit as st
from datetime import datetime

# Database connection information - update these values with your MySQL credentials
DB_CONFIG = {
    'host': 'localhost',  # Change this to your MySQL host if needed
    'user': 'root',       # Change this to your MySQL username
    'password': '',       # Add your MySQL password here
    'database': 'cardiopredict'
}

# Global connection flag
db_connected = False
connection = None

# Try to establish connection
try:
    connection = mysql.connector.connect(**DB_CONFIG)
    if connection.is_connected():
        db_connected = True
        print("Connected to MySQL database")
except Error as e:
    print(f"Error connecting to MySQL database: {e}")

def create_tables():
    """Create tables if they don't exist"""
    if not db_connected or not connection:
        return False
    
    cursor = connection.cursor()
    
    # Create users table
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(128) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Create prediction history table
    predictions_table = """
    CREATE TABLE IF NOT EXISTS prediction_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        risk_level VARCHAR(10) NOT NULL,
        probability FLOAT NOT NULL,
        user_data TEXT NOT NULL,
        prescription TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
    
    try:
        cursor.execute(users_table)
        cursor.execute(predictions_table)
        connection.commit()
        
        # Create admin user if it doesn't exist
        create_admin_user()
        
        return True
    except Error as e:
        print(f"Error creating tables: {e}")
        return False
    finally:
        cursor.close()

def create_admin_user():
    """Create admin user if it doesn't exist"""
    if not db_connected or not connection:
        return False
    
    cursor = connection.cursor()
    
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
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(insert_admin, ('admin', 'admin@cardiopredict.com', hashed_password, True))
            connection.commit()
            print("Admin user created successfully")
        
        return True
    except Error as e:
        print(f"Error creating admin user: {e}")
        return False
    finally:
        cursor.close()

def get_connection():
    """Get database connection"""
    global connection, db_connected
    
    # If connection is lost, try to reconnect
    if not db_connected or not connection or not connection.is_connected():
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection.is_connected():
                db_connected = True
                return connection
        except Error as e:
            print(f"Error reconnecting to MySQL database: {e}")
            db_connected = False
            return None
    
    return connection

def create_user(username, email, password):
    """Create a new user account"""
    if not db_connected:
        return False, "Database connection is unavailable. Please try again later."
    
    conn = get_connection()
    if not conn:
        return False, "Database connection failed. Please try again later."
    
    cursor = conn.cursor()
    
    try:
        # Check if username or email already exists
        check_query = "SELECT * FROM users WHERE username = %s OR email = %s"
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
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (username, email, hashed_password, False))
        conn.commit()
        
        return True, "User created successfully"
    except Error as e:
        conn.rollback()
        return False, f"Error creating user: {str(e)}"
    finally:
        cursor.close()

def authenticate_user(username, password):
    """Authenticate a user by username and password"""
    if not db_connected:
        # Demo login for testing
        if username == "demo" and password == "demo":
            return True, 999, False
        
        # Admin login
        if username == "admin" and password == "admin123":
            return True, 1, True
            
        return False, None, False
    
    conn = get_connection()
    if not conn:
        return False, None, False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get user by username
        query = "SELECT id, password_hash, is_admin FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if user:
            password_bytes = password.encode('utf-8')
            hash_bytes = user['password_hash'].encode('utf-8')
            
            if bcrypt.checkpw(password_bytes, hash_bytes):
                return True, user['id'], user['is_admin']
        
        return False, None, False
    except Error as e:
        print(f"Authentication error: {e}")
        return False, None, False
    finally:
        cursor.close()

def save_prediction(user_id, risk_level, probability, user_data, prescription=None):
    """Save a prediction to the user's history with optional prescription data"""
    if not db_connected or user_id == 999:  # 999 is demo user ID
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
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (user_id, risk_level, float(probability), user_data_json, prescription_json))
        conn.commit()
        
        # Get the prediction ID
        prediction_id = cursor.lastrowid
        
        return True, prediction_id
    except Error as e:
        conn.rollback()
        return False, None
    finally:
        cursor.close()

def get_user_predictions(user_id, limit=10):
    """Get a user's prediction history including prescription data"""
    if not db_connected or user_id == 999:  # 999 is demo user ID
        return []
    
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get user predictions
        query = """
        SELECT * FROM prediction_history 
        WHERE user_id = %s 
        ORDER BY prediction_date DESC 
        LIMIT %s
        """
        
        cursor.execute(query, (user_id, limit))
        predictions = cursor.fetchall()
        
        # Process predictions
        result = []
        for p in predictions:
            # Convert JSON strings back to dictionaries
            user_data = json.loads(p['user_data']) if p['user_data'] else {}
            prescription = json.loads(p['prescription']) if p['prescription'] else None
            
            prediction_data = {
                'id': p['id'],
                'date': p['prediction_date'],
                'risk_level': p['risk_level'],
                'probability': p['probability'],
                'user_data': user_data,
                'prescription': prescription
            }
            result.append(prediction_data)
        
        return result
    except Error as e:
        print(f"Error getting user predictions: {e}")
        return []
    finally:
        cursor.close()

def get_user_by_id(user_id):
    """Get user by ID"""
    if not db_connected:
        # Demo user
        if user_id == 999:
            return {'id': 999, 'username': 'demo', 'email': 'demo@example.com', 'is_admin': False}
        # Admin user
        if user_id == 1:
            return {'id': 1, 'username': 'admin', 'email': 'admin@cardiopredict.com', 'is_admin': True}
        return None
    
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT id, username, email, is_admin FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        return user
    except Error as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        cursor.close()

def get_prediction_by_id(prediction_id):
    """Get a single prediction by ID"""
    if not db_connected:
        return None
    
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM prediction_history WHERE id = %s"
        cursor.execute(query, (prediction_id,))
        prediction = cursor.fetchone()
        
        if prediction:
            # Convert JSON strings back to dictionaries
            user_data = json.loads(prediction['user_data']) if prediction['user_data'] else {}
            prescription = json.loads(prediction['prescription']) if prediction['prescription'] else None
            
            prediction_data = {
                'id': prediction['id'],
                'date': prediction['prediction_date'],
                'risk_level': prediction['risk_level'],
                'probability': prediction['probability'],
                'user_data': user_data,
                'prescription': prescription
            }
            
            return prediction_data
        else:
            return None
    except Error as e:
        print(f"Error getting prediction: {e}")
        return None
    finally:
        cursor.close()

def get_all_users():
    """Get all users (for admin panel)"""
    if not db_connected:
        # Return demo data for testing
        return [
            {'id': 1, 'username': 'admin', 'email': 'admin@cardiopredict.com', 'is_admin': True, 'created_at': datetime.now()},
            {'id': 2, 'username': 'user1', 'email': 'user1@example.com', 'is_admin': False, 'created_at': datetime.now()},
            {'id': 3, 'username': 'user2', 'email': 'user2@example.com', 'is_admin': False, 'created_at': datetime.now()}
        ]
    
    conn = get_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT id, username, email, is_admin, created_at FROM users ORDER BY id"
        cursor.execute(query)
        users = cursor.fetchall()
        
        return users
    except Error as e:
        print(f"Error getting all users: {e}")
        return []
    finally:
        cursor.close()

def get_all_predictions():
    """Get all predictions (for admin panel)"""
    if not db_connected:
        # Return demo data for testing
        return [
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
        return []
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
        SELECT p.id, p.user_id, u.username, p.prediction_date, p.risk_level, p.probability
        FROM prediction_history p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.prediction_date DESC
        """
        
        cursor.execute(query)
        predictions = cursor.fetchall()
        
        return predictions
    except Error as e:
        print(f"Error getting all predictions: {e}")
        return []
    finally:
        cursor.close()

def get_prediction_details(prediction_id):
    """Get detailed prediction data for admin view"""
    prediction = get_prediction_by_id(prediction_id)
    
    if prediction:
        # Get the user who made this prediction
        conn = get_connection()
        if not conn:
            return prediction
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            query = "SELECT username, email FROM users WHERE id = (SELECT user_id FROM prediction_history WHERE id = %s)"
            cursor.execute(query, (prediction_id,))
            user = cursor.fetchone()
            
            if user:
                prediction['username'] = user['username']
                prediction['email'] = user['email']
            
            return prediction
        except Error as e:
            print(f"Error getting prediction details: {e}")
            return prediction
        finally:
            cursor.close()
    
    return None

# Create tables when module is imported
if db_connected:
    create_tables()