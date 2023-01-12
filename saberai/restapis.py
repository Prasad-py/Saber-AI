from saberai import app,db
from flask import request, make_response
from saberai.controllers import loginController, tweetIdeasController, coldEmailsController, socialMediaController, businessPitchController, emailGenController, blogArticleController
from saberai.middlewares import token_required_api

users = db.users
user_tokens = db.user_tokens

@app.route('/api/login', methods=["POST"])
def loginAPi():
    response = loginController(request)
    if response['error'] == True:
        return response
    else :
        resp = make_response(response)
        resp.set_cookie('user', response['data'])
        return resp

@app.route('/api/logout', methods=["POST"])
def logoutAPi():
    if request.cookies.get('user'):
       resp = make_response({'error': False,'msg': 'Success'})
       resp.delete_cookie('user')
       return resp

@app.route('/api/tweet-ideas', methods=["POST"])
@token_required_api
def tweetIdeasApi(current_user):
    return tweetIdeasController(request,current_user)

@app.route('/api/cold-emails', methods=["POST"])
@token_required_api
def coldEmailsApi(current_user):
    return coldEmailsController(request,current_user)

@app.route('/api/social-media', methods=["POST"])
@token_required_api
def socialMediaApi(current_user):
    return socialMediaController(request,current_user)

@app.route('/api/code-gen', methods=["POST"])
@token_required_api
def businessPitchApi(current_user):
    return businessPitchController(request,current_user)

@app.route('/api/email-gen', methods=["POST"])
@token_required_api
def emailGenApi(current_user):
    return emailGenController(request,current_user)

@app.route('/api/blog-article', methods=["POST"])
@token_required_api
def blogArticleApi(current_user):
    return blogArticleController(request,current_user)
