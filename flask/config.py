class Configuration(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://eruph:1234@localhost/test1'

    ### FLASK SECURITY ###
    SECURITY_PASSWORD_SALT = 'salt'
    SECURITY_PASSWORD_HASH = 'sha512_crypt'

class TestingConfig(object):
    TESTING = True
    SECRET_KEY = 'secret key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SERVER_NAME = 'localhost'  # Обязательно
    APPLICATION_ROOT = '/'
    WTF_CSRF_ENABLED = False
    PREFERRED_URL_SCHEME = 'http'
    SECURITY_PASSWORD_SALT = 'test_salt'
    SECURITY_PASSWORD_HASH = 'plaintext'  # Для простоты тестирования
    
    
