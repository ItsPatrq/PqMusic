# server.py
from flask import Flask, send_file, request, jsonify
import os
from flask_cors import CORS

app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static/build'))
CORS(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET', 'POST'])
def index():
    return  send_file("../static/build/index.html")

@app.route("/hello")
def hello():
    return  "Hello world!"

@app.route("/SayHello", methods=['POST'])
def sayhello():
    target = os.path.join(APP_ROOT, 'images/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)
    
    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)
    
    return "ok"

if __name__ == "__main__":
    app.run()