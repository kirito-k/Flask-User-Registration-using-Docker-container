import bcrypt as bcrypt
from flask import Flask
from flask import jsonify
from flask import request
from flask_restful import Api
from flask_restful import Resource
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)
mongoclient = MongoClient('mongodb://db:27017')
db = mongoclient.mydb


class Register(Resource):
    def post(self):
        data = request.get_json()
        username = data['Username']
        password = data['Password']
        encrypted_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        db.col1.insert({'Username': username,
                        'Password': encrypted_pw,
                        'Sentense': '',
                        'Tokens': 10})
        response = {
            "status": 200,
            'msg': "Sign Up successful!"
        }
        return jsonify(response)


def verifyPassord(username, password):
    hashedP = db.col1.find({"Username": username})[0]['Password']
    if bcrypt.hashpw(password.encode('utf8'), hashedP) == hashedP:
        return True
    return False


def countTokens(username):
    tokens = db.col1.find({"Username": username})[0]['Tokens']
    return tokens


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
            }
            return jsonify(response)

        # Check if the user has enough coins
        token_count = countTokens(username)
        if token_count <= 0:
            response = {
                "status": 302
            }
            return jsonify(response)

        # Store the sentence
        db.col1.update({"Username": username},
                       {"$set": {"Sentense": sentence,
                                 "Tokens": token_count - 1}})
        response = {
            "status": 200,
            "msg": "Sentence stored successfully"
        }
        return jsonify(response)


api.add_resource(Register, '/register')
api.add_resource(Store, '/store')


@app.route('/')
def home():
    return 'Hello to HOME!!'


def main():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
