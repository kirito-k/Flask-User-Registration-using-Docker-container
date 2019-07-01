"""
    File name: app.py
    Authod: Devavrat Kalam
    Language: Python 3.x
    Description: Flask server implementation for registration-login of users and stores the phrases provided by users
"""

from flask import Flask
from flask import jsonify
from flask import request
from flask_restful import Api
from flask_restful import Resource
from pymongo import MongoClient
import bcrypt as bcrypt

# Creating app
app = Flask(__name__)
# Creating API
api = Api(app)
# Creating MongoDB client and database
mongoclient = MongoClient('mongodb://db:27017')
db = mongoclient.mydb


class Register(Resource):
    # Registers users on the server
    # User must provide a unique username and password
    def post(self):
        data = request.get_json()
        username = data['Username']
        password = data['Password']
        # Encrypting password
        encrypted_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # Inserting the entry in col1 collection
        db.col1.insert_one({'Username': username,
                        'Password': encrypted_pw,
                        'Sentence': '',
                        'Tokens': 6})
        response = {
            "status": 200,
            'msg': "Sign Up successful!"
        }
        return jsonify(response)



class Store(Resource):
    def post(self):
        data = request.get_json()
        username = data['Username']
        password = data['Password']
        sentence = data["Sentence"]

        # Check if the password is correct
        correct_pw = verifyPassord(username, password)
        if not correct_pw:
            response = {
                "status": 301,
                'msg': 'Password is incorrect'
            }
            return jsonify(response)

        # Check if the user has enough coins
        token_count = countTokens(username)
        if token_count <= 0:
            response = {
                "status": 302,
                'msg': 'Not enough tokens left'
            }
            return jsonify(response)

        # Store the sentence
        db.col1.update({"Username": username},
                       {"$set": {"Sentence": sentence,
                                 "Tokens": token_count - 1}})
        response = {
            "status": 200,
            "msg": "Sentence stored successfully"
        }
        return jsonify(response)


class Get(Resource):
    def post(self):
        data = request.get_json()
        Username = data['Username']
        Password = data['Password']

        # Checking if password is correct
        correct_pw = verifyPassord(Username, Password)
        if not correct_pw:
            response = {
                'status': 301
            }
            return jsonify(response)

        # Checking if user has enough tokens left
        tokens = countTokens(Username)
        if tokens <= 0:
            response = {
                'status': 302,
                'msg': 'Not enough tokens left'
            }
            return jsonify(response)

        # Reducing token count by one
        db.col1.update({'Username': Username}, {'$set': {"Tokens": tokens - 1}})
        # Retrieving sentence
        sentence = db.col1.find({'Username': Username})[0]['Sentence']
        
        response = {
            'status': 200,
            'msg': sentence
        }
        return jsonify(response)


def verifyPassord(username, password):
    # Check whether the password is correct or not
    hashedP = db.col1.find({"Username": username})[0]['Password']
    if bcrypt.hashpw(password.encode('utf8'), hashedP) == hashedP:
        return True
    return False


def countTokens(username):
    # Returns the number of Tokens left for user
    tokens = db.col1.find({"Username": username})[0]['Tokens']
    return tokens

# Adding resources to API
api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')


# Home page response
@app.route('/')
def hello():
    return 'Hello to HOME!!'


def main():
    # Defining the server to host on localhost for docker
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
