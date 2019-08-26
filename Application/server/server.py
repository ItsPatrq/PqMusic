# server.py
from flask import Flask, send_file, request, jsonify
import os
from flask_cors import CORS

app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static/build'))
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return send_file("../static/build/index.html")

@app.route("/hello")
def hello():
    return  "Hello world!"

@app.route("/SayHello", methods=['POST'])
def sayhello():
    print("SAY HELLO MADAFUCKA")
    return "ok"

if __name__ == "__main__":
    app.run()