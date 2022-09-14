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
        query = request.form['tweetIdeas']
        print(query)

        prompt = 'AI Suggestions for {} are:'.format(query)
        openAIAnswer = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

    return render_template('tweet-ideas.html', **locals())



@app.route('/cold-emails', methods=["GET", "POST"])
def coldEmails():

    if request.method == 'POST':
        query = request.form['coldEmails']
        print(query)

        prompt = 'AI Suggestions for {} are:'.format(query)
        openAIAnswer = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

    return render_template('cold-emails.html', **locals())



@app.route('/social-media', methods=["GET", "POST"])
def socialMedia():

    if request.method == 'POST':
        query = request.form['socialMedia']
        print(query)

        # prompt = 'AI Suggestions for {} are:'.format(query)
        response = openai.Completion.create(
                engine = GPT_Engine,
                prompt=f"Subject of the Advertisement:\n{query}\nWrite a long and clever Advertisement on the given subject:\nAd:\n",
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        openAIAnswer = response['choices'][0]['text']
        print(openAIAnswer)
        

    return render_template('social-media.html', **locals())


@app.route('/business-pitch', methods=["GET", "POST"])
def businessPitch():

    if request.method == 'POST':
        query = request.form['businessPitch']
        print(query)

        # prompt = 'AI Suggestions for {} are:'.format(query)
        response = openai.Completion.create(
                engine = GPT_Engine,
                prompt=f"Subject of the Advertisement:\n{query}\nWrite a clever Advertisement on the given subject:\nAd:\n",
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        openAIAnswer = response['choices'][0]['text']
    return render_template('business-pitch.html', **locals())


@app.route('/email-gen', methods=["GET", "POST"])
def videoIdeas():

    if request.method == 'POST':
        prev_email = request.form['videoIdeas']
        bullet_points = request.form['bullet_points']
        # print("here")
        print(prev_email)
        print(bullet_points)

        # prompt1 = query
        if prev_email == "":
            response = openai.Completion.create(
                engine = GPT_Engine,
                prompt=f"Bullet Points:\n{bullet_points}\nWrite a reply email based on the bullet point above:\nEmail:\n",
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        elif bullet_points =="":
            response = openai.Completion.create(
                engine=GPT_Engine,
                prompt=f"Previous Email:\n{prev_email}\nWrite a suitable reply to the above email:\nEmail:\n",
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
        print(openAIAnswer)
        # openAIAnswer = openAIAnswer.replace("\n","<br>.innerHTML")
        # openAIAnswer = openAIAnswer.replace(/\r\n/g, "<br />");
    return render_template('email-gen.html', **locals())


@app.route('/blog-article', methods=["GET", "POST"])
def videoDescription():

    if request.method == 'POST':
        title = request.form['title']
        keywords = request.form['keywords']

        # prompt = 'AI Suggestions for {} are:'.format(query)
        response = openai.Completion.create(
                            engine=GPT_Engine,
                            prompt=f"Title:\n{title}\nKeywords:\n{keywords}\nWrite a long blog article for the above title using the given keywords:\nArticle:\n",
                            temperature=0.5,
                            max_tokens=200,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0
                            )
        openAIAnswer = response['choices'][0]['text']
        print(openAIAnswer)
        openAIAnswer = openAIAnswer.replace("\n","<br>")
    return render_template('blog-article.html', **locals())










if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
