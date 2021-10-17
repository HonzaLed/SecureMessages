from logging import error
from flask import Flask
from flask import request
import json
import uuid
import sys
import os
app = Flask(__name__)

try:
    with open("users.json", "r"):
        pass
except FileNotFoundError:
    with open("users.json", "w"):
        file.write('{"users":[]}')
class NullValueError(Exception):
    def __init__(self):
        print("NullValueError: used value is Null")

def get_user_file(pubKeyID):
    usersF = open("users.json", "r")
    userFJson = json.loads(usersF.read())
    users = userFJson["users"]
    if pubKeyID == None:
        return users
    for user in users:
        if user["pubKeyID"] == pubKeyID:
            return user["uuid"]
    newUuid = str(uuid.uuid4())
    users.append({"pubKeyID":pubKeyID, "uuid":newUuid})
    userFJson["users"] = users
    usersF = open("users.json", "w")
    usersF.write(json.dumps(userFJson))
    return newUuid

@app.route("/")
def index():
    return "Use /<pubKeyID> or /users instead"

@app.route("/users")
def users():
    fList = {"users":[]}
    fList["users"] = get_user_file(None)
    return json.dumps(fList)
"""
def users():
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    fList = {"users":[]}
    for f in files:
        if f[-4:] == ".msg":
            fList["users"].append(f.replace(".msg",""))
    return json.dumps(fList)
"""

@app.route("/register", methods = ["POST", "GET"])
def addUser():
    if request.method == "POST":
        try:
            data = request.get_json(force=True)
            pubKeyID = str(data["pubKeyID"])
            nickname = str(data["nickname"])
            try:
                with open(get_user_file(pubKeyID)+".msg", "r") as file:
                    return '{"status":"ERR", "error":"UserExist"}'
            except FileNotFoundError:
                with open(get_user_file(pubKeyID)+".msg", "w") as file:
                    file.write('{"status":"OK", "pubKeyID":"'+pubKeyID+'", "nickname":"'+nickname+'", "messages": [] }')
                return '{"status":"OK", "pubKeyID":"'+pubKeyID+'", "nickname":"'+nickname+'", "messages": [] }'
        except KeyError:
            return '{"status":"ERR", "error":"RequestKeyNotFound"}'
        except BaseException as err:
            return '{"status":"ERR", "error":"'+err+'"}'
    else:
        return '{"status":"ERR", "error":"ExpectedPostRequest"}'

@app.route("/upload/<pubKeyID>", methods = ['POST', 'GET'])
def upload(pubKeyID):
    if request.method == "POST":
        data = request.get_json(force=True)
        try:
            msg = str(data["msg"])
            sign = str(data["sign"])
            try:
                nickname = str(data["nickname"])
            except KeyError:
                nickname = None
            frmPubKeyID = str(data["frmPubKeyID"]) # rfm stands for from, so frmPubKeyID is sender public key ID
            msgTemplate = json.loads('{"msg":"", "sign":"", "frmPubKeyID":""}')
            print("[DEBUG]",msg, file=sys.stderr)
            print("[DEBUG]",pubKeyID, file=sys.stderr)
            try:
                with open(get_user_file(pubKeyID)+".msg", "r") as file:
                    fileContent = file.read()
            except FileNotFoundError:
                if nickname == None:
                    raise KeyError
                fileContent = '{"status":"OK", "pubKeyID":"'+pubKeyID+'", "nickname":"'+nickname+'", "messages": [] }'
            fileJson = json.loads(fileContent)
            msgObj = msgTemplate
            msgObj["msg"] = msg
            msgObj["sign"] = sign
            msgObj["frmPubKeyID"] = frmPubKeyID
            fileJson["messages"].append(msgObj)
            with open(get_user_file(pubKeyID)+".msg", "w") as file:
                file.write(json.dumps(fileJson))
            return '{"status":"OK", "msg":"'+msg+'", "sign":"'+sign+'", "pubKeyID":"'+pubKeyID+'", "frmPubKeyID":"'+frmPubKeyID+'"}'
        except KeyError:
            return '{"status":"ERR", "error":"RequestKeyNotFound"}'
        except BaseException as err:
            return '{"status":"ERR", "error":"'+err+'"}'
    if request.method == "GET":
        #return '{"pubKeyID":"'+pubKeyID+'", "all":"test"}'
        try:
            with open(get_user_file(pubKeyID)+".msg", "r") as file:
                return file.read()
        except FileNotFoundError:
            return '{"status":"ERR", "error":"NotFoundError"}'
        except BaseException as err:
            return '{"status":"ERR", "error":"'+err+'"}'


if __name__ == '__main__':
    app.run(debug = True)