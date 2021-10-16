from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "Web page not found"

@app.route("/upload/<pubKeyID>", methods = ['POST', 'GET'])
def upload(pubKeyID):
    json = request.get_json(force=True)
    print(json)
    print(pubKeyID)


if __name__ == '__main__':
    app.run(debug = True)