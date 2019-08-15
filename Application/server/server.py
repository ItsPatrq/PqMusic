# server.py
from flask import Flask, send_file
import os

app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static/build'))

@app.route('/', methods=['GET', 'POST'])
def index():
    return send_file("../static/build/index.html")

@app.route("/hello")
def hello():
    return  "Hello world!"

if __name__ == "__main__":
    app.run()