from distutils.log import error
from urllib import response
from flask import render_template, request, redirect, url_for, flash, abort, jsonify,make_response
from flask_mail import Mail, Message
from saberai import app,db,mail, GPT_Engine, openai, client, client_secrets_file, GOOGLE_CLIENT_ID
from saberai.helperFunctions import get_gpt3_response, generate_code, returns_estimated_number_of_tokens_used, parse_json, get_subscriptions
import bcrypt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId
import shortuuid
import hashlib
import hmac
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import requests
import jwt
from datetime import datetime, timedelta
import saberai.config as config


users = db.users
user_tokens = db.user_tokens

def signUpController (request):
    email = request.form["email"]
    password = request.form["password"]
    name=request.form['name']
    confirmPassword = request.form["confirmPassword"]

    if email is None or password is None or len(password)<8:
        flash("Please fill all the details")
        return 'signup'

    if password != confirmPassword:
        flash("Passwords do not match!!")
        return 'signup'

    
    user_found = users.find_one({"email" : email})

    if user_found:
        flash("This email already exists!!")
        return 'signup'
    
    print('----',email)
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    otp = generate_code()
    user_input = {"email": email, "password": hashedPassword, "isVerified": False, "otp": otp,'name': name,'gauth': False}
    users.insert_one(user_input)
    user = users.find_one({"email" : email})
    date_after_month = datetime.today()+ relativedelta(months=1)
    token_input = {"user_id": user["_id"],"tokens": 1000,"expiry":date_after_month.strftime('%d/%m/%Y'),"plan": "free"}
    user_tokens.insert_one(token_input)

    msg = Message(
                    'OTP Verification for SaberAI',
                    sender ='dummyaditya22@gmail.com',
                    recipients = [email]
                )
                
    msg.body = f" Hello {email},\n This mail is for verifying your account with Saber Intelligence. Your account verification OTP is {otp}.\n If this was not you please get in touch with our contact at www.saber-ai.com.\n Thank You for signing up with Saber Intelligence.\n Saber Intelligence Pvt Ltd" 
    mail.send(msg)
    return 'verifyEmail'


def verifyEmailController (request,current_user) :
    email = current_user["email"]
    otp = request.form["otp"]
    user_found = users.find_one({"email": email})

    if user_found is None:
        flash("This email is not registered!!")
        return "login"

    if otp == '':
        flash("Enter OTP!!")
        return "verifyEmail"
    
    if int(user_found["otp"])== int(otp):
        user = users.update_one({"email": email}, { "$set": {"isVerified": True, "otp": ""}})
        current_user['isVerified']=True
        return "home"
    else:
        flash("Incorrect OTP!!")
        return "verifyEmail"

def loginController (request) :
    email = request.form["email"]
    password = request.form["password"]
    
    email_found = users.find_one({"email": email})
    if email_found:
        passwordcheck = email_found['password']
        isVerified = email_found['isVerified']
        
        if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
            if isVerified is False:
                return {'error': True,'msg': 'Please your email first!!', 'data': 'verifyEmail'}
            token = jwt.encode({
                'public_id': str(email_found['_id']),
                'exp' : datetime.utcnow() + timedelta(days = 30)
            },config.SECRET_KEY)
            print(token)
            return {'error': False,'msg': 'success','data':token} 
        else:
            flash("Enter correct credentials!!")
            return {'error': True,'msg': 'Enter correct credentials!!', 'data': 'login'}
    else:
        flash('Email not found!')
        return {'error': True,'msg': 'Enter correct credentials!!', 'data': 'login'}

def tweetIdeasController(request,current_user) : 
    title = request.form['tweetIdeas']
    tokens = user_tokens.find_one({"user_id": current_user['_id']})
    estimated_number_of_tokens = returns_estimated_number_of_tokens_used(title)
    if estimated_number_of_tokens > tokens["tokens"] : 
        flash("You don't have sufficient tokens!!")
        return {'error': True, 'msg': "You don't have sufficient tokens!!", 'data': ''}
    query_dict = {
        "service": "tweet-ideas",
        "title": title,
    } 
    response = get_gpt3_response(query_dict)
    openAIAnswer = response['choices'][0]['text']
    print(openAIAnswer)
    openAIAnswer = openAIAnswer.replace("\n","<br>")
    print(openAIAnswer[:4])
    tokens_used = response['usage']['total_tokens']
    user_available_tokens = tokens["tokens"]
    remaining_tokens = max(0,user_available_tokens-tokens_used)
    user_tokens.update_one({"_id":ObjectId(tokens["_id"])},{"$set": {"tokens" : remaining_tokens}})      
    if openAIAnswer[:4] == "<br>":
        openAIAnswer = openAIAnswer[4:]
        print("true")
    print(openAIAnswer)
    return {'error' : False, 'msg' : 'success', 'data': openAIAnswer}

def coldEmailsController(request,current_user) :
    company_name = request.form['companyName']
    title = request.form['coldEmails']
    tokens = user_tokens.find_one({"user_id": current_user["_id"]})
    estimated_number_of_tokens = returns_estimated_number_of_tokens_used(title+company_name)
    if estimated_number_of_tokens > tokens["tokens"] : 
        flash("You don't have sufficient tokens!!")
        return {'error': True, 'msg': "You don't have sufficient tokens!!", 'data': ''}
    query_dict = {
        "service": "cold-emails",
        "title": title,
        "company_name": company_name,
    }
    response = get_gpt3_response(query_dict)
    openAIAnswer = response['choices'][0]['text']
    print(openAIAnswer)
    openAIAnswer = openAIAnswer.replace("\n","<br>")
    print(openAIAnswer[:4])
    tokens_used = response['usage']['total_tokens']
    user_available_tokens = tokens["tokens"]
    remaining_tokens = max(0,user_available_tokens-tokens_used)
    user_tokens.update_one({"_id":ObjectId(tokens["_id"])},{"$set": {"tokens" : remaining_tokens}})      
    if openAIAnswer[:4] == "<br>":
        openAIAnswer = openAIAnswer[4:]
        print("true")
    print(openAIAnswer)
    return {'error' : False, 'msg' : 'success', 'data': openAIAnswer}

def socialMediaController(request,current_user) :
    query = request.form['socialMedia']
    print(query)
    tokens = user_tokens.find_one({"user_id": current_user["_id"]})
    estimated_number_of_tokens = returns_estimated_number_of_tokens_used(query)
    if estimated_number_of_tokens > tokens["tokens"] : 
        flash("You don't have sufficient tokens!!")
        return {'error': True, 'msg': "You don't have sufficient tokens!!", 'data': ''}
    # prompt = 'AI Suggestions for {} are:'.format(query)
    query_dict = {
        "service": "social-media",
        "query": query ,
    }
    response = get_gpt3_response(query_dict)
    openAIAnswer = response['choices'][0]['text']
    tokens_used = response['usage']['total_tokens']
    user_available_tokens = tokens["tokens"]
    remaining_tokens = max(0,user_available_tokens-tokens_used)
    user_tokens.update_one({"_id":ObjectId(tokens["_id"])},{"$set": {"tokens" : remaining_tokens}})      
    print(openAIAnswer)
    return {'error' : False, 'msg' : 'success', 'data': openAIAnswer}

def businessPitchController(request,current_user) :
    purpose = request.form['purpose']
    language = request.form['language']
    # print(query)
    tokens = user_tokens.find_one({"user_id": current_user["_id"]})
    estimated_number_of_tokens = returns_estimated_number_of_tokens_used(language+purpose)
    if estimated_number_of_tokens > tokens["tokens"] : 
        flash("You don't have sufficient tokens!!")
        return {'error': True, 'msg': "You don't have sufficient tokens!!", 'data': ''}
    # prompt = 'AI Suggestions for {} are:'.format(query)
    query_dict = {
        "service": "code-gen",
        "purpose": purpose,
        "language": language
    }
    response = get_gpt3_response(query_dict)
    openAIAnswer = response['choices'][0]['text']
    openAIAnswer = openAIAnswer.replace("\n","<br>")
    tokens_used = response['usage']['total_tokens']
    user_available_tokens = tokens["tokens"]
    remaining_tokens = max(0,user_available_tokens-tokens_used)
    user_tokens.update_one({"_id":ObjectId(tokens["_id"])},{"$set": {"tokens" : remaining_tokens}})      
    if openAIAnswer[:4] == "<br>":
        openAIAnswer = openAIAnswer[4:]
    return {'error' : False, 'msg' : 'success', 'data': openAIAnswer}
    
def emailGenController(request,current_user) :
    prev_email = request.form["prev_email"]
    bullet_points = request.form['bullet_points']
    print(prev_email)
    print(bullet_points)

    tokens = user_tokens.find_one({"user_id": current_user["_id"]})

    if prev_email == "":
        estimated_number_of_tokens = returns_estimated_number_of_tokens_used(prev_email+bullet_points)
        if estimated_number_of_tokens > tokens["tokens"] : 
            flash("You don't have sufficient tokens!!")
            return {'error': True, 'msg': "You don't have sufficient tokens!!", 'data': ''}
        response = openai.Completion.create(
            engine = GPT_Engine,
            prompt="Bullet Points:\n"+bullet_points+"\nWrite a reply email based on the bullet point above:\nEmail:\n",
            temperature=0.7,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    elif bullet_points =="":
        estimated_number_of_tokens = returns_estimated_number_of_tokens_used(prev_email)
        if estimated_number_of_tokens > tokens["tokens"] : 
            flash("You don't have sufficient tokens!!")
            return {'error': True, 'msg': "You don't have sufficient tokens!!", 'data': ''}
        response = openai.Completion.create(
            engine=GPT_Engine,
            prompt="Previous Email:\n{prev_email}\nWrite a suitable reply to the above email:\nEmail:\n",
            temperature=0.7,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    else:
        estimated_number_of_tokens = returns_estimated_number_of_tokens_used(prev_email+bullet_points)
        if estimated_number_of_tokens > tokens["tokens"] : 
            flash("You don't have sufficient tokens!!")
            return {'error': True, 'msg': "You don't have sufficient tokens!!", 'data': ''}
        response = openai.Completion.create(
            engine=GPT_Engine,
            prompt=f"Previous Email:\n{prev_email}\nBullet Points:\n{bullet_points}\nWrite a reply to the previous email based on the bullet points above:\nEmail:\n",
            temperature=0.7,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    # response =  openai.Completion.create(
    #                     engine=GPT_Engine,
    #                     prompt=f"Previous Email:\n{prompt1}\nWrite a suitable reply to the above email:\nEmail:\n",
    #                     temperature=0.5,
    #                     max_tokens=200,
    #                     top_p=1,
    #                     frequency_penalty=0,
    #                     presence_penalty=0
    #                     )
    openAIAnswer = response['choices'][0]['text']
    tokens_used = response['usage']['total_tokens']
    user_available_tokens = tokens["tokens"]
    remaining_tokens = max(0,user_available_tokens-tokens_used)
    user_tokens.update_one({"_id":ObjectId(tokens["_id"])},{"$set": {"tokens" : remaining_tokens}})        
    openAIAnswer = openAIAnswer.replace("\n","<br>")

    if openAIAnswer[:4] == "<br>":
        openAIAnswer = openAIAnswer[4:]
    return {'error' : False, 'msg' : 'success', 'data': openAIAnswer}
    
def blogArticleController(request,current_user) :
    # Title = TITLE
    # KeyWords = KEYWORDS
    title = request.form['title']
    keywords = request.form['keywords']
    # title = title1 if title1 else Title
    # keywords = keywords1 if keywords1 else KeyWords
    # TITLE = title
    # KEYWORDS = keywords
    # prompt = 'AI Suggestions for {} are:'.format(query)
    tokens = user_tokens.find_one({"user_id": current_user["_id"]})
    estimated_number_of_tokens = returns_estimated_number_of_tokens_used(title+keywords)
    if estimated_number_of_tokens > tokens["tokens"] : 
        flash("You don't have sufficient tokens!!")
        return {'error': True, 'msg': "You don't have sufficient tokens!!", 'data': ''}
    query_dict = {
        "service": "blog-article",
        "title": title,
        "keywords": keywords
    }
    response = get_gpt3_response(query_dict)
    openAIAnswer = response['choices'][0]['text']
    # print(openAIAnswer)
    openAIAnswer = openAIAnswer.replace("\n","<br>")
    tokens_used = response['usage']['total_tokens']
    user_available_tokens = tokens["tokens"]
    remaining_tokens = max(0,user_available_tokens-tokens_used)
    user_tokens.update_one({"_id":ObjectId(tokens["_id"])},{"$set": {"tokens" : remaining_tokens}})      
    # print(openAIAnswer[:4])
    if openAIAnswer[:4] == "<br>":
        openAIAnswer = openAIAnswer[4:]
        print("true")
    # print(openAIAnswer)
    return {'error' : False, 'msg' : 'success', 'data': openAIAnswer}

