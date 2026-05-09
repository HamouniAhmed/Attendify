# app/config.py
import os
import sys
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to determine the base directory correctly
def get_base_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller one-file bundle or one-dir bundle where sys.executable is the exe
        return os.path.dirname(sys.executable)
    else:
        # Normal execution (from script like run.py or serve.py)
        # __file__ is app/config.py. We want the project root, which is one level up from 'app'.
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_database_path():
    """Get the correct database path for both development and portable versions"""
    base_dir = get_base_dir()
    
    # Check if we're in a portable version (data folder exists)
    portable_db_path = os.path.join(base_dir, 'data', 'instance', 'attendance.db')
    dev_db_path = os.path.join(base_dir, 'instance', 'attendance.db')
    
    # If portable structure exists, use it
    if os.path.exists(os.path.join(base_dir, 'data')):
        return portable_db_path
    else:
        return dev_db_path

def get_instance_dir():
    """Get the correct instance directory for both versions"""
    base_dir = get_base_dir()
    
    # Check if we're in a portable version
    if os.path.exists(os.path.join(base_dir, 'data')):
        return os.path.join(base_dir, 'data', 'instance')
    else:
        return os.path.join(base_dir, 'instance')

def get_uploads_dir():
    """Get the correct uploads directory for both versions"""
    base_dir = get_base_dir()
    
    # Check if we're in a portable version
    if os.path.exists(os.path.join(base_dir, 'data')):
        return os.path.join(base_dir, 'data', 'uploads')
    else:
        return os.path.join(base_dir, 'user_uploads')

APP_ROOT_DIR = get_base_dir()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Use dynamic paths that work for both dev and portable versions
    INSTANCE_DIR = get_instance_dir()
    USER_UPLOADS_DIR = get_uploads_dir()

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + get_database_path()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = USER_UPLOADS_DIR 
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    WTF_CSRF_ENABLED = True
    
    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(Config.INSTANCE_DIR, exist_ok=True)
        os.makedirs(Config.USER_UPLOADS_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    SERVER_NAME = 'localhost.localdomain'

class ProductionConfig(Config):
    DEBUG = False  # Should be False for production
    
    # For packaged app, ensure directories exist
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Additional production setup if needed
        # Ensure upload folder exists with proper permissions
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}