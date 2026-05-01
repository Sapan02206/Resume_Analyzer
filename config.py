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
    
    # PostgreSQL Database settings
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or '5432'
    DB_NAME = os.environ.get('DB_NAME') or 'resume_analyzer'
    DB_USER = os.environ.get('DB_USER') or 'postgres'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'sapan211'
    
    # SQLAlchemy Database URI
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
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
