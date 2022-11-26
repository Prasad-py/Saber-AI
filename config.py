
class Config(object):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    SECRET_KEY = "this-is-a-super-secret-key"

config = {
    'development': DevelopmentConfig,
    'testing': DevelopmentConfig,
    'production': DevelopmentConfig
}

## Enter your Open API Key here
OPENAI_API_KEY = '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'


FIREBASE_CONFIG = {
    'apiKey': "AIzaSyAxIW3tbaUEnmvqV93rqyQxA2xEnpH8Z2k",
    'authDomain': "saberdemo-6e885.firebaseapp.com",
    'projectId': "saberdemo-6e885",
    'storageBucket': "saberdemo-6e885.appspot.com",
    'messagingSenderId': "221117736160",
    'appId': "1:221117736160:web:67edce645aab1f37559c85",
    'measurementId': "G-N6C3RD35G1",
    'databaseURL' : 'https://saberdemo-6e885.firebaseio.com/'
}

MONGO_URL = 'mongodb://localhost:27017'