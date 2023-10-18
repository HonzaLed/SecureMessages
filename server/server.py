from Crypto.PublicKey import RSA
from hashlib import sha512
from flask import request
from flask import Flask
import argparse
import json
import uuid
import sys

app = Flask(__name__)

def verify(msg, signature, pubKey):
        try:
            msg = msg.encode()
        except:
            pass
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        hashFromSignature = pow(signature, pubKey.e, pubKey.n)
        return hash==hashFromSignature

try:
    with open("users.json", "r") as file:
        pass
except FileNotFoundError:
    with open("users.json", "w") as file:
        file.write('{"users":[]}')
class NullValueError(Exception):
    def __init__(self):
        print("NullValueError: used value is Null")

def get_user_file(pubKeyID, new=True):
    usersF = open("users.json", "r")
    userFJson = json.load(usersF)
    users = userFJson["users"]
    if pubKeyID is None:
        return users
    for user in users:
        if user["pubKeyID"] == pubKeyID:
            return user["uuid"]
    if new:
        newUuid = str(uuid.uuid4())
        foundSame = False
        ifContinue = False
        while ifContinue is not True:
            for user in users:
                if user["uuid"] == newUuid:
                    foundSame = True
            if foundSame:
                newUuid = str(uuid.uuid4())
            else:
                ifContinue = True
        users.append({"pubKeyID":pubKeyID, "uuid":newUuid})
        userFJson["users"] = users
        usersF = open("users.json", "w")
        json.dump(userFJson, usersF)
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
            return '{"status":"ERR", "error":"RequestKeyNotFound"}', 404
        except BaseException as err:
            return '{"status":"ERR", "error":"'+err+'"}'
    else:
        return '{"status":"ERR", "error":"ExpectedPostRequest"}'

@app.route("/delete/<pubKeyID>/<msgID>/<pubKeyIDSign>", methods=["GET","DELETE"])
def delete(pubKeyID, msgID, pubKeyIDSign):
    if request.method == "GET":
        return '{"status":"ERR", "error":"ExpectedDELETERequest"}', 405
    if request.method == "DELETE":
        try:
            pubKey = RSA.import_key(bytes.fromhex(pubKeyID))
            signed = verify(pubKeyID+msgID, int(pubKeyIDSign), pubKey)
            if not signed:
                return '{"status":"ERR", "error":"SignatureNotValid"}', 403
            if signed:
                with open(get_user_file(pubKeyID)+".msg", "r") as file:
                    data = json.load(file)
                print("Deleting message",msgID, file=sys.stderr)
                data["messages"].pop(int(msgID))
                with open(get_user_file(pubKeyID)+".msg", "w") as file:
                    json.dump(data, file)
                return '{"status":"OK", "pubKeyID":"'+pubKeyID+'", "msgID":"'+msgID+'", "pubKeyIDSign":"'+pubKeyIDSign+'"}', 200
        except BaseException as err:
            return '{"status":"ERR", "error":"'+str(err)+'"}', 501

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
                print("File",get_user_file(pubKeyID)+".msg","not found", file=sys.stderr)
                if nickname is None:
                    raise KeyError
                fileContent = '{"status":"OK", "pubKeyID":"'+pubKeyID+'", "nickname":"'+nickname+'", "messages": [] }'
            fileJson = json.loads(fileContent)
            msgObj = msgTemplate
            msgObj["msg"] = msg
            msgObj["sign"] = sign
            msgObj["frmPubKeyID"] = frmPubKeyID
            fileJson["messages"].append(msgObj)
            with open(get_user_file(pubKeyID)+".msg", "w") as file:
                json.dump(fileJson, file)
            return '{"status":"OK", "msg":"'+msg+'", "sign":"'+sign+'", "pubKeyID":"'+pubKeyID+'", "frmPubKeyID":"'+frmPubKeyID+'"}'
        except KeyError:
            return '{"status":"ERR", "error":"RequestKeyNotFound"}'
        except BaseException as err:
            return '{"status":"ERR", "error":"'+err+'"}'
    if request.method == "GET":
        try:
            with open(get_user_file(pubKeyID)+".msg", "r") as file:
                return file.read()
        except FileNotFoundError:
            return '{"status":"ERR", "error":"NotFoundError"}'
        except BaseException as err:
            return '{"status":"ERR", "error":"'+err+'"}'

@app.route("/vrf/<randomBytes>")
def vrf(randomBytes):
    try:
        hash = int.from_bytes(sha512(randomBytes.encode()).digest(), byteorder='big')
        return '{"status":"OK", "hash":'+str(hash)+'}', 200
    except BaseException as err:
        return json.dumps({"status":"ERR", "error":str(err)}), 400

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server of secure communication service')
    parser.add_argument("-p", "--port", action="store", dest="port", default="5000", type=int, help="Port to server run on")
    arguments = parser.parse_args()
    app.run(debug = True, host="0.0.0.0", port=arguments.port)
