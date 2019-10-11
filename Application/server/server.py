# server.py
from flask import Flask, send_file, request, jsonify
import os
from flask_cors import CORS
from utils.spectogram import *
import uuid
import shutil
from utils.windowFunctionsPresentation import *
from transcription.onesets_frames.model_initialization import *
from transcription.onesets_frames.transcribe import *


app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static/build'))
CORS(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def createRequestResponseFiles():
    requestUuid = str(uuid.uuid1())
    responseUuid = str(uuid.uuid1())
    target = os.path.join(APP_ROOT, 'tmpFiles/')

    if not os.path.isdir(target):
        os.mkdir(target)

    requestFolderPath = os.path.join(target, 'request' + requestUuid)

    if not os.path.isdir(requestFolderPath):
        os.mkdir(requestFolderPath)

    responseFolderPath = os.path.join(target, 'response' + responseUuid)

    if not os.path.isdir(responseFolderPath):
        os.mkdir(responseFolderPath)

    return requestFolderPath, responseFolderPath, requestUuid, responseUuid
    

@app.route('/', methods=['GET', 'POST'])
def index():
    return  send_file("../static/build/index.html")

@app.route("/hello")
def hello():
    return  "Hello world!"

@app.route("/Spectrogram", methods=['POST'])
def spectrogram():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFiles()
    
    for file in request.files.getlist("file"):
        filename = file.filename
        requestFilePath = "/".join([requestFolderPath, filename])
        responseFilePath = "/".join([responseFolderPath, filename])
        responseFilePath = responseFilePath[:-3] + "png"

        file.save(requestFilePath)

        graph_spectrogram(requestFilePath, responseFilePath)

    #shutil.rmtree(requestFolderPath)
    #shutil.rmtree(responseFolderPath)
    return send_file(responseFilePath)

@app.route("/HannWindow", methods=['GET', 'POST'])
def getHannWindow():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFiles()
    responseFilePath = "/".join([responseFolderPath, 'HannWindow.png'])
    hannWindow(responseFilePath)
    return send_file(responseFilePath)

@app.route("/HammingWindow", methods=['GET', 'POST'])
def getHammingWindow():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFiles()
    responseFilePath = "/".join([responseFolderPath, 'HammingWindow.png'])
    hammingWindow(responseFilePath)
    return send_file(responseFilePath)

@app.route("/RectangleWindow", methods=['GET', 'POST'])
def getRectabgkeWubdiw():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFiles()
    responseFilePath = "/".join([responseFolderPath, 'RectangleWindow.png'])
    rectangleWindow(responseFilePath)
    return send_file(responseFilePath)

@app.route("/Transcribe", methods=['GET', 'POST'])
def transcribe():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFiles()
    for file in request.files.getlist("file"):
        filename = file.filename
        requestFilePath = "/".join([requestFolderPath, filename])
        responseFilePath = "/".join([responseFolderPath, filename])
        responseFilePath = responseFilePath[:-3] + "mid"

        file.save(requestFilePath)

        transcribe(requestFilePath, responseFilePath)

    return send_file(responseFilePath)

if __name__ == "__main__":
    app.run()