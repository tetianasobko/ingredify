import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:1234@localhost:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

