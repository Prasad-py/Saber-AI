from distutils.log import error
from urllib import response
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import config
import openai
import random
import pymongo
import bcrypt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bson import json_util
import json
from bson.objectid import ObjectId


openai.api_key = config.OPENAI_API_KEY
GPT_Engine = "text-davinci-003"

#Mongodb configuration
client = pymongo.MongoClient(config.MONGO_URL)
db = client.get_database('saberAI')
users = db.users
user_tokens = db.user_tokens

    
def get_prompt(query_dict):
    service = query_dict["service"] if "service" in query_dict else None
    title = query_dict["title"] if "title" in query_dict else None
    keywords = query_dict["keywords"] if "keywords" in query_dict else None
    # prev_email = query_dict["prev_email"] if "prev_email" in query_dict else None
    # bullet_points = query_dict["bullet_points"] if "bullet_points" in query_dict else None
    query = query_dict["query"] if "query" in query_dict else None
    purpose = query_dict["purpose"] if "purpose" in query_dict else None
    language = query_dict["language"] if "language" in query_dict else None
    company_name = query_dict["company_name"] if "company_name" in query_dict else None

    prompts_dict = {
        "blog-article": f"Title:\n"+title+"\nKeywords:\n+"+keywords+"\nWrite a long blog article for the above title using the given keywords:\nArticle:\n",
        "social-media": f"Subject of the Advertisement:\n"+query+"\nWrite a long and clever Advertisement on the given subject:\nAd:\n",
        "cold-emails": f"Services:\n"+title+"\nA company named "+company_name+" provides the above services.\nWrite a cold email to advertise its services:\nEmail:\n",
        "tweet-ideas": f"Description:\n"+title+"\nWrite a long and clever tweet for the above decription:\nTweet:\n",
        #     "email-gen": 
        "code-gen": f"Usecase of the Code:\n"+purpose+"\nWrite a "+language+" function for the above usecase:\nCode:\n",
    }
    return prompts_dict[service]

def get_gpt3_response(query_dict):
    raw_response = openai.Completion.create(
                engine=GPT_Engine,
                prompt= get_prompt(query_dict)
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
    return raw_response


def page_not_found(e):
  return render_template('404.html'), 404


app = Flask(__name__)
app.config.from_object(config.config['development'])
app.register_error_handler(404, page_not_found)


app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'dummyaditya22@gmail.com'
app.config['MAIL_PASSWORD'] = 'xadafnzuxtlugpgq'
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def generate_code():
    code = random.choice(range(100000, 999999))  # generating 6 digit random code
    return code

def returns_estimated_number_of_tokens_used(text_input):
    number_of_words_in_input = len(text_input.split())
    total_words_processed_by_gpt = 4 * number_of_words_in_input
    tokens_used_up = total_words_processed_by_gpt/2.5
    return tokens_used_up

def parse_json(data):
    return json.loads(json_util.dumps(data))


@app.route('/', methods=["GET", "POST"])
def index():
    if "email" not in session: 
        return redirect("/login")

    if "isVerified" in session and session["isVerified"] == False:
        return redirect("/verifyEmail")

    return render_template('index.html', **locals())


@app.route('/signup', methods = ["GET","POST"])
def signup():

    if "email" in session: 
        return redirect("/")

    if request.method == "POST":
        
        email = request.form["email"]
        password = request.form["password"]
        confirmPassword = request.form["confirmPassword"]

        if email is None or password is None or len(password)<8:
            flash("Please fill all the details")
            return redirect("/signup")

        if password != confirmPassword:
            flash("Passwords do not match!!")
            return render_template('signup.html')
        
        user_found = users.find_one({"email" : email})

        if user_found:
            flash("This email already exists!!")
            return redirect("/signup")
        
        hashedPassword = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        otp = generate_code()
        user_input = {"email": email, "password": hashedPassword, "isVerified": False, "otp": otp}
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
        return redirect(url_for('verifyEmail'))
        # except :
        #     flash("email taken")
        #     return render_template("signup.html")  

    return render_template('signup.html')


@app.route("/verifyEmail",methods=["GET","POST"])
def verifyEmail():

    if "email" not in session: 
        return redirect("/login")

    if session["isVerified"] == True:
        return redirect("/")

    if request.method == "POST":
        email = request.form["email"]
        otp = request.form["otp"]
        user_found = users.find_one({"email": email})

        if user_found is None:
            flash("This email is not registered!!")
            return redirect('/login')
        
        if int(user_found["otp"])== int(otp):
            user = users.update_one({"email": email}, { "$set": {"isVerified": True, "otp": ""}})
            session["isVerified"] = True
            return redirect('/')
        else:
            flash("Incorrect OTP!!")
            return redirect("/verifyEmail")

    return render_template("verifyEmail.html")

#login route
@app.route("/login", methods=["GET", "POST"])
def login():

    if "email" in session: 
        return redirect("/")

    if request.method == "POST":
        #get the request data
        email = request.form["email"]
        password = request.form["password"]
        
        email_found = users.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            isVerified = email_found['isVerified']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                session['isVerified'] = isVerified
                session["userId"] = str(email_found["_id"])
                if isVerified is False:
                    return redirect('/verifyEmail')
                return redirect('/')
            else:
                flash("Enter correct credentials!!")
                return redirect("/login")
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)

    if session.get('email') is not None:
        return redirect("/")

    return render_template("login.html")

#logout route
@app.route("/logout")
def logout():
    #remove the token setting the user to None
    if "email" in session:
        session.pop("email", None)
    return redirect("/login")


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
def tweetIdeas():

    if "email" not in session: 
        return redirect("/login")
    
    if session["isVerified"] == False:
        return redirect("/verifyEmail")
   
    if request.method == 'POST':
        title = request.form['tweetIdeas']
        tokens = user_tokens.find_one({"user_id": ObjectId(session["userId"])})
        estimated_number_of_tokens = returns_estimated_number_of_tokens_used(title)
        if estimated_number_of_tokens > tokens["tokens"] : 
            flash("You don't have sufficient tokens!!")
            return redirect("/tweet-ideas")
        response = openai.Completion.create(
                            engine=GPT_Engine,
                            prompt="Description:\n"+title+"\nWrite a long and clever tweet for the above decription:\nTweet:\n",
                            temperature=0.5,
                            max_tokens=300,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0
                            )
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
    return render_template('tweet-ideas.html', **locals())



@app.route('/cold-emails', methods=["GET", "POST"])
def coldEmails():

    if "email" not in session: 
        return redirect("/login")
    
    if session["isVerified"] == False:
        return redirect("/verifyEmail")

    if request.method == 'POST':
        company_name = request.form['companyName']
        title = request.form['coldEmails']
        tokens = user_tokens.find_one({"user_id": ObjectId(session["userId"])})
        estimated_number_of_tokens = returns_estimated_number_of_tokens_used(title+company_name)
        if estimated_number_of_tokens > tokens["tokens"] : 
            flash("You don't have sufficient tokens!!")
            return redirect("/cold-emails")
        response = openai.Completion.create(
                            engine=GPT_Engine,
                            prompt="Services:\n"+title+"\nA company named "+company_name+" provides the above services.\nWrite a cold email to advertise its services:\nEmail:\n",
                            temperature=0.5,
                            max_tokens=300,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0
                            )
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
    return render_template('cold-emails.html', **locals())



@app.route('/social-media', methods=["GET", "POST"])
def socialMedia():

    if "email" not in session: 
        return redirect("/login")
    
    if session["isVerified"] == False:
        return redirect("/verifyEmail")

    if request.method == 'POST':
        query = request.form['socialMedia']
        print(query)
        tokens = user_tokens.find_one({"user_id": ObjectId(session["userId"])})
        estimated_number_of_tokens = returns_estimated_number_of_tokens_used(query)
        if estimated_number_of_tokens > tokens["tokens"] : 
            flash("You don't have sufficient tokens!!")
            return redirect("/social-media")
        # prompt = 'AI Suggestions for {} are:'.format(query)
        response = openai.Completion.create(
                engine = GPT_Engine,
                prompt="Subject of the Advertisement:\n"+query+"\nWrite a long and clever Advertisement on the given subject:\nAd:\n",
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        openAIAnswer = response['choices'][0]['text']
        tokens_used = response['usage']['total_tokens']
        user_available_tokens = tokens["tokens"]
        remaining_tokens = max(0,user_available_tokens-tokens_used)
        user_tokens.update_one({"_id":ObjectId(tokens["_id"])},{"$set": {"tokens" : remaining_tokens}})      
        print(openAIAnswer)
        

    return render_template('social-media.html', **locals())


@app.route('/code-gen', methods=["GET", "POST"])
def businessPitch():

    if "email" not in session: 
        return redirect("/login")
    
    if session["isVerified"] == False:
        return redirect("/verifyEmail")

    if request.method == 'POST':
        purpose = request.form['purpose']
        language = request.form['language']
        # print(query)
        tokens = user_tokens.find_one({"user_id": ObjectId(session["userId"])})
        estimated_number_of_tokens = returns_estimated_number_of_tokens_used(language+purpose)
        if estimated_number_of_tokens > tokens["tokens"] : 
            flash("You don't have sufficient tokens!!")
            return redirect("/code-gen")
        # prompt = 'AI Suggestions for {} are:'.format(query)
        response = openai.Completion.create(
                engine = GPT_Engine,
                prompt="Usecase of the Code:\n"+purpose+"\nWrite a "+language+" function for the above usecase:\nCode:\n",
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        openAIAnswer = response['choices'][0]['text']
        openAIAnswer = openAIAnswer.replace("\n","<br>")
        tokens_used = response['usage']['total_tokens']
        user_available_tokens = tokens["tokens"]
        remaining_tokens = max(0,user_available_tokens-tokens_used)
        user_tokens.update_one({"_id":ObjectId(tokens["_id"])},{"$set": {"tokens" : remaining_tokens}})      
        if openAIAnswer[:4] == "<br>":
            openAIAnswer = openAIAnswer[4:]
    return render_template('code-gen.html', **locals())


@app.route('/email-gen', methods=["GET", "POST"])
def prevEmail():

    if "email" not in session: 
        return redirect("/login")
    
    if session["isVerified"] == False:
        return redirect("/verifyEmail")

    if request.method == 'POST':
        prev_email = request.form["prev_email"]
        bullet_points = request.form['bullet_points']
        print(prev_email)
        print(bullet_points)

        tokens = user_tokens.find_one({"user_id": ObjectId(session["userId"])})

        if prev_email == "":
            estimated_number_of_tokens = returns_estimated_number_of_tokens_used(prev_email+bullet_points)
            if estimated_number_of_tokens > tokens["tokens"] : 
                flash("You don't have sufficient tokens!!")
                return redirect("/email-gen")

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
                return redirect("/email-gen")
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
                return redirect("/email-gen")
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


    return render_template('email-gen.html', **locals())

# TITLE = ""
# KEYWORDS = ""

@app.route('/blog-article', methods=["GET", "POST"])
def videoDescription():

    if "email" not in session: 
        return redirect("/login")
    
    if session["isVerified"] == False:
        return redirect("/verifyEmail")

    if request.method == 'POST':
        # Title = TITLE
        # KeyWords = KEYWORDS
        title = request.form['title']
        keywords = request.form['keywords']
        # title = title1 if title1 else Title
        # keywords = keywords1 if keywords1 else KeyWords
        # TITLE = title
        # KEYWORDS = keywords
        # prompt = 'AI Suggestions for {} are:'.format(query)
        tokens = user_tokens.find_one({"user_id": ObjectId(session["userId"])})
        estimated_number_of_tokens = returns_estimated_number_of_tokens_used(title+keywords)
        if estimated_number_of_tokens > tokens["tokens"] : 
            flash("You don't have sufficient tokens!!")
            return redirect("/blog-article")
        response = openai.Completion.create(
                            engine=GPT_Engine,
                            prompt=f"Title:\n{title}\nKeywords:\n{keywords}\nWrite a long blog article for the above title using the given keywords:\nArticle:\n",
                            temperature=0.5,
                            max_tokens=700,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0
                            )
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
    return render_template('blog-article.html', **locals())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
