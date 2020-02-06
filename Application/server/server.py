# -*- coding: utf-8 -*-

# server.py
from flask import Flask, send_file, request, json, Response
import os
from flask_cors import CORS
from utils.spectogram import *
import uuid
import shutil
from utils.windowFunctionsPresentation import *
from transcription.ac import autocorrelationWrap
app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static/build'))
import base64
import matplotlib
matplotlib.use('Agg')

CORS(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#region transcription initialization

#endregion
#region generate
#endregion

def createRequestResponseFolders():
    requestUuid = str(uuid.uuid1())
    responseUuid = str(uuid.uuid1())
    target = os.path.join(APP_ROOT, 'tmpFiles/')

    if not os.path.isdir(target):
        os.mkdir(target)

    requestFolderPath = os.path.join(target, 'request-' + requestUuid)

    if not os.path.isdir(requestFolderPath):
        os.mkdir(requestFolderPath)

    responseFolderPath = os.path.join(target, 'response-' + responseUuid)

    if not os.path.isdir(responseFolderPath):
        os.mkdir(responseFolderPath)

    return requestFolderPath, responseFolderPath, requestUuid, responseUuid
    

@app.route('/', methods=['GET', 'POST'])
def index():
    return  send_file("../static/build/index.html")

@app.route("/Spectrogram", methods=['POST'])
def spectrogram():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFolders()
    
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
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFolders()
    responseFilePath = "/".join([responseFolderPath, 'HannWindow.png'])
    hannWindow(responseFilePath)
    return send_file(responseFilePath)

@app.route("/HammingWindow", methods=['GET', 'POST'])
def getHammingWindow():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFolders()
    responseFilePath = "/".join([responseFolderPath, 'HammingWindow.png'])
    hammingWindow(responseFilePath)
    return send_file(responseFilePath)

@app.route("/RectangleWindow", methods=['GET', 'POST'])
def getRectabgkeWubdiw():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFolders()
    responseFilePath = "/".join([responseFolderPath, 'RectangleWindow.png'])
    rectangleWindow(responseFilePath)
    return send_file(responseFilePath)

@app.route("/TranscribeByAutoCorrelation", methods=['POST'])
def transcribeByAutoCorrelation():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFolders()
    
    
    for file in request.files.getlist("file"):
        filename = file.filename
        requestFilePath = "/".join([requestFolderPath, filename])
        responseFilePath = "/".join([responseFolderPath])
        print(responseFilePath)
        file.save(requestFilePath)
        
        pitches, correlogram = autocorrelationWrap(requestFilePath, responseFilePath)

    pitchesEncoded = base64.b64encode(pitches.getbuffer()).decode("ascii")
    correlogramOpenedEncoded = base64.b64encode(correlogram.getbuffer()).decode("ascii")
    dict_data = {'pitches': pitchesEncoded, 'correlogram': correlogramOpenedEncoded}
    return Response(json.dumps(dict_data), mimetype='text/plain')

@app.route("/GenerateTransformUnconditioned", methods=['GET', 'POST'])
def GenerateTransformUnconditioned():
    requestFolderPath, responseFolderPath, _, _ = createRequestResponseFolders()

    for file in request.files.getlist("file"):
       filename = file.filename
       requestFilePath = "/".join([requestFolderPath, filename])

       file.save(requestFilePath)

    res = musicTransformer.generateUnconditionalTransform(requestFilePath, responseFolderPath)
    return send_file(res)

@app.route("/GenerateTransformMelodyConditioned", methods=['GET', 'POST'])
def generateTransformMelodyConditioned():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFolders()

    res = musicTransformer.generateMelodyConditionedTransform(responseFolderPath)
    return send_file(res)

if __name__ == "__main__":
    app.run(port=5000)