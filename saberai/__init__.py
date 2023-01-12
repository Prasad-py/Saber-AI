from distutils.log import error
from flask import Flask
from flask_mail import Mail
import saberai.config as config
import openai
import pymongo
import razorpay
import os
import pathlib

openai.api_key = config.OPENAI_API_KEY
GPT_Engine = "text-davinci-003"

#Mongodb configuration
client = pymongo.MongoClient(config.MONGO_URL)
db = client.get_database('saberAI')

app = Flask(__name__)
app.config.from_object(config.config['development'])

app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'dummyaditya22@gmail.com'
app.config['MAIL_PASSWORD'] = 'xadafnzuxtlugpgq'
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = config.GOOGLE_CLIENT_ID
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "goauth.json")

client = razorpay.Client(auth=(config.RAZORPAY_CONFIG['razorpayKey'], config.RAZORPAY_CONFIG['razorpaySecret']))

from saberai import routes
from saberai import restapis