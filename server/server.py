from logging import error
from flask import Flask
from flask import request
import json
import sys
import os
app = Flask(__name__)

@app.route("/")
def index():
    return "Use /<pubKeyID> instead"

@app.route("/users")
def users():
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    fList = {"users":[]}
    for f in files:
        if f[-4:] == ".msg":
            fList["users"].append(f.replace(".msg",""))
    return json.dumps(fList)

@app.route("/<pubKeyID>", methods = ['POST', 'GET'])
def upload(pubKeyID):
    if request.method == "POST":
        data = request.get_json(force=True)
        try:
            msg = str(data["msg"])
            sign = str(data["sign"])
            frmPubKeyID = str(data["frmPubKeyID"]) # rfm stands for from, so frmPubKeyID is sender public key ID
            msgTemplate = json.loads('{"msg":"", "sign":""}')
            print("[DEBUG]",msg, file=sys.stderr)
            print("[DEBUG]",pubKeyID, file=sys.stderr)
            try:
                with open(pubKeyID+".msg", "r") as file:
                    fileContent = file.read()
            except FileNotFoundError:
                fileContent = '{"status":"OK", "pubKeyID":"'+pubKeyID+'", "messages": [] }'
            fileJson = json.loads(fileContent)
            msgObj = msgTemplate
            msgObj["msg"] = msg
            msgObj["sign"] = sign
            fileJson["messages"].append(msgObj)
            with open(pubKeyID+".msg", "w") as file:
                file.write(json.dumps(fileJson))
            return '{"status":"OK", "msg":"'+msg+'", "sign":"'+sign+'", "pubKeyID":"'+pubKeyID+'"}'
        except KeyError:
            return '{"status":"ERR", "error":"RequestKeyNotFound"}'
        #except error as err:
        #    return '{"status":"ERR", "error":"'+str(err)+'"}'
    if request.method == "GET":
        #return '{"pubKeyID":"'+pubKeyID+'", "all":"test"}'
        try:
            with open(pubKeyID+".msg", "r") as file:
                return file.read()
        except FileNotFoundError:
            return '{"status":"ERR", "error":"NotFoundError"}'


if __name__ == '__main__':
    app.run(debug = True)