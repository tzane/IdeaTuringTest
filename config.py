
# default config
class BaseConfig(object):
    DEBUG = False
    # shortened for readability
    SECRET_KEY = 'my precious'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///arguments.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///arguments.db'


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False