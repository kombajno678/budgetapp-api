import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    DEBUG = os.environ.get('ENV', 'development') != 'production'
    #CSRF_ENABLED = True
    CORS_HEADERS = 'Content-Type'


class Configdb(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'postgresql://postgres:super123@localhost/budgetapp')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
