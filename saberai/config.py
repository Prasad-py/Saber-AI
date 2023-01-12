
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

SECRET_KEY='this-is-a-super-secret-key'

## Enter your Open API Key here
OPENAI_API_KEY = "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"


FIREBASE_CONFIG = {
    'apiKey': "AIzaSyAxIW3tbaUEnmvqV93rqyQxA2xEnpH8Z2k",
    'authDomain': "saberdemo-6e885.firebaseapp.com",
    'databaseURL': "https://saberdemo-6e885-default-rtdb.firebaseio.com",
    'projectId': "saberdemo-6e885",
    'storageBucket': "saberdemo-6e885.appspot.com",
    'messagingSenderId': "221117736160",
    'appId': "1:221117736160:web:67edce645aab1f37559c85",
    'measurementId': "G-N6C3RD35G1",
    'databaseURL' : 'https://saberdemo-6e885.firebaseio.com/',
}

# RAZORPAY_CONFIG = {
#     'razorpayKey': 'rzp_live_tIV0KgA5JaQyMd',
#     'razorpaySecret': '8BVl6hcEO7LdxqLESl3b4hvw'
# }

RAZORPAY_CONFIG = {
    'razorpayKey': 'rzp_test_UJJjpGLL14Eki4',
    'razorpaySecret': 'QEgmCqVZVVAuGzL3saBEDvaH'
}

MONGO_URL = 'mongodb://localhost:27017'

GOOGLE_CLIENT_ID = '964331532997-d9leuglhn22abhbm1sjggp29hoiglg5g.apps.googleusercontent.com'
