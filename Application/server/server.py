# server.py
from flask import Flask, send_file, request, jsonify
import os
from flask_cors import CORS
from spectogram import graph_spectrogram
import uuid
import shutil

app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static/build'))
CORS(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET', 'POST'])
def index():
    return  send_file("../static/build/index.html")

@app.route("/hello")
def hello():
    return  "Hello world!"

@app.route("/Spectrogram", methods=['POST'])
def sayhello():
    target = os.path.join(APP_ROOT, 'utils/')

    if not os.path.isdir(target):
        os.mkdir(target)

    target = os.path.join(target, 'spectrogram/')

    if not os.path.isdir(target):
        os.mkdir(target)

    requestFolderPath = os.path.join(target, 'request' + str(uuid.uuid1()))

    if not os.path.isdir(requestFolderPath):
        os.mkdir(requestFolderPath)

    responseFolderPath = os.path.join(target, 'response' + str(uuid.uuid1()))

    if not os.path.isdir(responseFolderPath):
        os.mkdir(responseFolderPath)
    
    for file in request.files.getlist("file"):
        filename = file.filename
        requestFilePath = "/".join([requestFolderPath, filename])
        responseFilePath = "/".join([responseFolderPath, filename])
        responseFilePath = responseFilePath[:-3] + "png"

        file.save(requestFilePath)

        graph_spectrogram(requestFilePath, responseFilePath)
    
    shutil.rmtree(requestFolderPath)
    return send_file(responseFilePath)

if __name__ == "__main__":
    app.run()