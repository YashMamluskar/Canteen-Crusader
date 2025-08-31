# config.py

import os

class Config:
    # A secret key is needed for session management and form security (CSRF)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-super-secret-key-you-should-change'
    
    # Configure the database URI. We'll use SQLite for simplicity.
    # 'site.db' will be created in the root directory.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    
    # Disable a feature of SQLAlchemy that we don't need, which saves resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Add this line for the image upload folder
    UPLOAD_FOLDER = 'app/static/uploads'