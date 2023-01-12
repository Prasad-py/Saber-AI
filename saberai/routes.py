from distutils.log import error
from urllib import response
from flask import render_template, request, redirect, url_for, session, flash, abort, jsonify,make_response
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
from saberai.controllers import signUpController, verifyEmailController, loginController, tweetIdeasController, coldEmailsController, socialMediaController, businessPitchController, emailGenController, blogArticleController
from saberai.middlewares import token_required

users = db.users
user_tokens = db.user_tokens

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost:8080/callback"
)

def page_not_found(e):
  return render_template('404.html'), 404

app.register_error_handler(404, page_not_found)

@app.route('/', methods=["GET", "POST"])
@token_required
def index(current_user):
    return render_template('index.html', **locals())

@app.route('/signup', methods = ["GET","POST"])
def signup():

    if "email" in session: 
        return redirect("/")

    if request.method == "POST":
        
        response = signUpController(request)
        
        if response == 'signup' :
            return render_template('signup.html')
        if response == 'verifyEmail' :
            return redirect(url_for('verifyEmail'))

    return render_template('signup.html')


@app.route("/verifyEmail",methods=["GET","POST"])
@token_required
def verifyEmail(current_user):

    if current_user['isVerified'] == True:
        return redirect("/")

    if request.method == "POST":
        
        response = verifyEmailController(request,current_user)

        if response == 'login' :
            return redirect('/login')
        elif response == 'home' :
            return redirect('/')
        elif response == 'verifyEmail':
            return redirect('/verifyEmail')


    return render_template("verifyEmail.html")

@app.route("/glogin")
def glogin():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

#login route
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        
        response = loginController(request)
        if response['error'] == True:
            return redirect('/' + response['data'])
        else :
            resp = make_response(redirect('/'))
            resp.set_cookie('user', response['data'])
            return resp
    
    return render_template("login.html")


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=1
    )

    email = id_info.get('email')
    name = id_info.get('name')

    user_found = users.find_one({"email" : email})
    if user_found == None:
        user_input = {"email": email, "isVerified": True,'otp': '','gauth': True,'name': name}
        users.insert_one(user_input)
        user = users.find_one({"email" : email})
        date_after_month = datetime.today()+ relativedelta(months=1)
        token_input = {"user_id": user["_id"],"tokens": 1000,"expiry":date_after_month.strftime('%d/%m/%Y'),"plan": "free"}
        user_tokens.insert_one(token_input)
        session["userId"] = str(user["_id"])
    else :
        session["userId"] = str(user_found["_id"])

    print("--------------------", id_info)
    session['email'] = id_info.get("email")
    session['isVerified'] = True
    session["google_id"] = id_info.get("sub")
    return redirect("/")


#logout route
@app.route("/logout")
def logout():
    #remove the token setting the user to None
    if request.cookies.get('user'):
       resp = make_response(redirect("/login"))
       resp.delete_cookie('user')
       return resp
    return redirect("/login")


@app.route("/payment", methods=["GET","POST"])
def payment():
    if "email" not in session: 
        return redirect("/login")
    
    if session["isVerified"] == False:
        return redirect("/verifyEmail")

    if request.method == "POST":
        amount = request.json['amount']
        data = { "amount": amount, "currency": "INR", "receipt": shortuuid.uuid() }
        payment = client.order.create(data)
        # payment = client.subscription.create({
        #     "plan_id": "plan_KxgXcWB7vPTvS4",
        #     "customer_notify": 1,
        #     "quantity": 1,
        #     "total_count": 12,
        #     "notes": {
        #         "key1": "value3",
        #         "key2": "value2"
        #     }
        # })
        
        return {
            "success": True,
            # "subscription_id": payment['id']
            "order_id": payment['id'],
            "currency": payment['currency'],
            "amount": payment['amount'],
        }

    subscriptions = get_subscriptions()
    email = session['email']
    user_found = users.find_one({"email" : email})

    return render_template("payment.html", subscriptions=subscriptions, email=email, name=user_found['name'])


@app.route('/payment/verify', methods=["POST"])
def verifyPayment():
    razorpay_order_id, razorpay_payment_id, razorpay_signature = request.json['razorpay_order_id'], request.json['razorpay_payment_id'], request.json['razorpay_signature']
    if razorpay_order_id is None or razorpay_payment_id is None or razorpay_signature is None:
        return{ 'success': False, 'msg': 'Please fill in all required fields'}
    
    verif_error_msg = 'Payment Verification failed.\nPlease email us your details in case you feel that there is any error.';
    generated_signature = hmac.new(
        bytes('QEgmCqVZVVAuGzL3saBEDvaH' , 'latin-1'),
        msg = bytes(f"{razorpay_order_id}|{razorpay_payment_id}" , 'latin-1'),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

    print(generated_signature,razorpay_signature.upper())

    if (generated_signature == razorpay_signature.upper()):
        return {"success":True}
    else:
        return { "success": False, "msg": "An error occured while processing your payment.\nPlease email us your details, and we will look into it." }  

# @app.route('/product-description', methods=["GET", "POST"])
# def productDescription():

#     if "email" not in session: 
#         return redirect("/login")
    
#     if session["isVerified"] == False:
#         return redirect("/verifyEmail")

#     if request.method == 'POST':
#         query = request.form['productDescription']
#         print(query)

#         prompt = 'AI Suggestions for {} are:'.format(query)
#         openAIAnswer = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

#     return render_template('product-description.html', **locals())



# @app.route('/job-description', methods=["GET", "POST"])
# def jobDescription():

#     if "email" not in session: 
#         return redirect("/login")
    
#     if session["isVerified"] == False:
#         return redirect("/verifyEmail")

#     if request.method == 'POST':
#         query = request.form['jobDescription']
#         print(query)

#         prompt = 'AI Suggestions for {} are:'.format(query)
#         openAIAnswer = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

#     return render_template('job-description.html', **locals())



@app.route('/tweet-ideas', methods=["GET", "POST"])
@token_required
def tweetIdeas(current_user):
   
    if request.method == 'POST':
        response = tweetIdeasController(request,current_user)
        if response['error'] == True : 
            return redirect('/tweet-ideas')
        else :
            openAIAnswer = response['data']
        

    return render_template('tweet-ideas.html', **locals())



@app.route('/cold-emails', methods=["GET", "POST"])
@token_required
def coldEmails(current_user):

    if request.method == 'POST':
        response = coldEmailsController(request,current_user)
        if response['error'] == True : 
            return redirect('/cold-emails')
        else :
            openAIAnswer = response['data']
        
    return render_template('cold-emails.html', **locals())



@app.route('/social-media', methods=["GET", "POST"])
@token_required
def socialMedia(current_user):

    if request.method == 'POST':
        response = socialMediaController(request,current_user)
        if response['error'] == True : 
            return redirect('/social-media')
        else :
            openAIAnswer = response['data']
        

    return render_template('social-media.html', **locals())


@app.route('/code-gen', methods=["GET", "POST"])
@token_required
def businessPitch(current_user):

    if request.method == 'POST':
        response = businessPitchController(request,current_user)
        if response['error'] == True : 
            return redirect('/code-gen')
        else :
            openAIAnswer = response['data']

    return render_template('code-gen.html', **locals())


@app.route('/email-gen', methods=["GET", "POST"])
@token_required
def emailGen(current_user):

    if request.method == 'POST':
        response = emailGenController(request,current_user)
        if response['error'] == True : 
            return redirect('/email-gen')
        else :
            openAIAnswer = response['data']

    return render_template('email-gen.html', **locals())

# TITLE = ""
# KEYWORDS = ""

@app.route('/blog-article', methods=["GET", "POST"])
@token_required
def blogArticle(current_user):

    if request.method == 'POST':
        response = blogArticleController(request,current_user)
        if response['error'] == True : 
            return redirect('/blog-article')
        else :
            openAIAnswer = response['data']

    return render_template('blog-article.html', **locals())


