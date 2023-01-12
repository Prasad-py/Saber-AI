from flask import request, jsonify, redirect
import jwt
from functools import wraps
from saberai import db
import saberai.config as config
from bson.objectid import ObjectId

users = db.users

def token_required_api(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        token = request.cookies.get('user')
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(str(token), config.SECRET_KEY,algorithms=["HS256"])
            current_user = users.find_one({"_id": ObjectId(data['public_id'])})
            print(current_user)
            if current_user['isVerified'] == False:
                return redirect('/verifyEmail')
            
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        token = request.cookies.get('user')
        # return 401 if token is not passed
        if not token:
            return redirect("/login")
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(str(token), config.SECRET_KEY,algorithms=["HS256"])
            current_user = users.find_one({"_id": ObjectId(data['public_id'])})
            print(current_user)
            
        except:
            return redirect("/login")
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated