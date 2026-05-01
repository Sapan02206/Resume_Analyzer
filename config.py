import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    
    # Database settings - Use SQLite for PythonAnywhere compatibility
    # For local PostgreSQL, set DATABASE_URL environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Use PostgreSQL if DATABASE_URL is set (local development)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Use SQLite for PythonAnywhere and simple deployments
        SQLALCHEMY_DATABASE_URI = 'sqlite:///resume_analyzer.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI settings (optional)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    USE_OPENAI = bool(OPENAI_API_KEY)
    
    # Scoring weights
    REQUIRED_SKILL_WEIGHT = 1.0
    OPTIONAL_SKILL_WEIGHT = 0.5
    
    # Paths
    SKILLS_DATA_PATH = 'data/skills.json'
    JOB_ROLES_DATA_PATH = 'data/job_roles.json'
