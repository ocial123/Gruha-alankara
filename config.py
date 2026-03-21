import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-gruha-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///gruha_alankara.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings for Hugging Face iframe compatibility
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}