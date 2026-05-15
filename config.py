import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dewill-secret-key-change-in-production')
    
    # Use DATABASE_URL for Render (Postgres), fallback to local SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or ('sqlite:///' + os.path.join(basedir, 'instance', 'dewill.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'mp4', 'webm'}

    # Mail settings (configure with real SMTP for production)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'alemherb@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'eczgozohtkbrjqvp')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'alemherb@gmail.com')
    MAIL_NOTIFY_TO = os.environ.get('MAIL_NOTIFY_TO', 'alemherb@gmail.com')
