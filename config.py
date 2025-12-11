import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    # Update this with your actual MySQL credentials
    # Format: mysql+pymysql://username:password@host/db_name
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "mysql+pymysql://root:root@localhost/csr"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
