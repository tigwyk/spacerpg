import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'sklof90sfd09fj3o90sd0v0svikxcv90902k0094950289208490248902489sjkcivoxjc90vux9cv903949124oi24sdfsdfiosd903958090-41-0940-1o4aa0993459035'

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
