from urllib import response
from flask import Flask, render_template, request
import config
import openai

openai.api_key = config.OPENAI_API_KEY
GPT_Engine = "text-davinci-002"

def page_not_found(e):
  return render_template('404.html'), 404


app = Flask(__name__)
app.config.from_object(config.config['development'])
app.register_error_handler(404, page_not_found)


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html', **locals())



@app.route('/product-description', methods=["GET", "POST"])
def productDescription():

    if request.method == 'POST':
        query = request.form['productDescription']
        print(query)

        prompt = 'AI Suggestions for {} are:'.format(query)
        openAIAnswer = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

    return render_template('product-description.html', **locals())



@app.route('/job-description', methods=["GET", "POST"])
def jobDescription():

    if request.method == 'POST':
        query = request.form['jobDescription']
        print(query)

        prompt = 'AI Suggestions for {} are:'.format(query)
        openAIAnswer = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

    return render_template('job-description.html', **locals())



@app.route('/tweet-ideas', methods=["GET", "POST"])
def tweetIdeas():

    if request.method == 'POST':
        title = request.form['tweetIdeas']

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
        if openAIAnswer[:4] == "<br>":
            openAIAnswer = openAIAnswer[4:]
            print("true")
        print(openAIAnswer)
    return render_template('tweet-ideas.html', **locals())



@app.route('/cold-emails', methods=["GET", "POST"])
def coldEmails():

    if request.method == 'POST':
        company_name = request.form['companyName']
        title = request.form['coldEmails']

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
        if openAIAnswer[:4] == "<br>":
            openAIAnswer = openAIAnswer[4:]
            print("true")
        print(openAIAnswer)
    return render_template('cold-emails.html', **locals())



@app.route('/social-media', methods=["GET", "POST"])
def socialMedia():

    if request.method == 'POST':
        query = request.form['socialMedia']
        print(query)

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
        print(openAIAnswer)
        

    return render_template('social-media.html', **locals())


@app.route('/code-gen', methods=["GET", "POST"])
def businessPitch():

    if request.method == 'POST':
        purpose = request.form['purpose']
        language = request.form['language']
        # print(query)

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

        if openAIAnswer[:4] == "<br>":
            openAIAnswer = openAIAnswer[4:]
    return render_template('code-gen.html', **locals())


@app.route('/email-gen', methods=["GET", "POST"])
def prevEmail():

    if request.method == 'POST':
        prev_email = request.form["prev_email"]
        bullet_points = request.form['bullet_points']
        print(prev_email)
        print(bullet_points)

        if prev_email == "":
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


        openAIAnswer = openAIAnswer.replace("\n","<br>")

        if openAIAnswer[:4] == "<br>":
            openAIAnswer = openAIAnswer[4:]


    return render_template('email-gen.html', **locals())

# TITLE = ""
# KEYWORDS = ""

@app.route('/blog-article', methods=["GET", "POST"])
def videoDescription():

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
        # print(openAIAnswer[:4])
        if openAIAnswer[:4] == "<br>":
            openAIAnswer = openAIAnswer[4:]
            print("true")
        # print(openAIAnswer)
    return render_template('blog-article.html', **locals())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
