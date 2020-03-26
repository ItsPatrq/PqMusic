# -*- coding: utf-8 -*-

# server.py
from flask import Flask, send_file, request, json, Response
import os
from flask_cors import CORS
from utils.spectogram import plot_spectrogram_wrapped
import uuid
from utils.windowFunctionsPresentation import *
from transcription.ac import autocorrelation_wrapped
from transcription.cepstrumF0Analysis import transcribe_by_cepstrum_wrapped
app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static/build'))
import base64
import matplotlib
from transcription.onsetsAndFrames import OnsetsAndFramesImpl
matplotlib.use('Agg')

CORS(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#region transcription initialization Onsets and Frames
onsets = OnsetsAndFramesImpl()
onsets.initializeModel()
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
    
def handleRequestWithFile():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFolders()
    file = request.files.getlist("file")[0]
    filename = file.filename
    requestFilePath = "/".join([requestFolderPath, filename])
    responseFilePath = "/".join([responseFolderPath])
    file.save(requestFilePath)

    return requestFilePath, responseFilePath, requestUuid, responseUuid, file.filename

@app.route('/', methods=['GET', 'POST'])
def index():
    return  send_file("../static/build/index.html")

@app.route("/Spectrogram", methods=['POST'])
def spectrogram():
    requestFilePath, responseFolderPath, _, _, fileName = handleRequestWithFile()
    
    responseFilePath = "/".join([responseFolderPath, fileName])
    responseFilePath = responseFilePath[:-3] + "png"

    plot_spectrogram_wrapped(requestFilePath, responseFilePath)

    return send_file(responseFilePath)

@app.route("/HannWindow", methods=['GET', 'POST'])
def getHannWindow():
    _, responseFolderPath, _, _ = createRequestResponseFolders()
    responseFilePath = "/".join([responseFolderPath, 'HannWindow.png'])
    hannWindow(responseFilePath)
    return send_file(responseFilePath)

@app.route("/HammingWindow", methods=['GET', 'POST'])
def getHammingWindow():
    _, responseFolderPath, _, _ = createRequestResponseFolders()
    responseFilePath = "/".join([responseFolderPath, 'HammingWindow.png'])
    hammingWindow(responseFilePath)
    return send_file(responseFilePath)

@app.route("/RectangleWindow", methods=['GET', 'POST'])
def getRectabgkeWubdiw():
    _, responseFolderPath, _, _ = createRequestResponseFolders()
    responseFilePath = "/".join([responseFolderPath, 'RectangleWindow.png'])
    rectangleWindow(responseFilePath)
    return send_file(responseFilePath)

@app.route("/TranscribeByAutoCorrelation", methods=['POST'])
def transcribeByAutoCorrelation():
    requestFilePath, _, _, _, _ = handleRequestWithFile()
        
    pitches, correlogram = autocorrelation_wrapped(requestFilePath)

    pitchesEncoded = base64.b64encode(pitches.getbuffer()).decode("ascii")
    correlogramOpenedEncoded = base64.b64encode(correlogram.getbuffer()).decode("ascii")
    dict_data = {'pitches': pitchesEncoded, 'correlogram': correlogramOpenedEncoded}
    return Response(json.dumps(dict_data), mimetype='text/plain')

@app.route("/TranscribeByCepstrum", methods=['POST'])
def TranscribeByCepstrum():
    requestFilePath, _, _, _, _ = handleRequestWithFile()
        
    pitches, cepstrogram, spectrogram, logSpectrogram = transcribe_by_cepstrum_wrapped(requestFilePath)

    pitchesEncoded = base64.b64encode(pitches.getbuffer()).decode("ascii")
    cepstrogramEncoded = base64.b64encode(cepstrogram.getbuffer()).decode("ascii")
    spectrogramEncoded = base64.b64encode(spectrogram.getbuffer()).decode("ascii")
    logSpectrogramEncoded = base64.b64encode(logSpectrogram.getbuffer()).decode("ascii")


    dict_data = {'pitches': pitchesEncoded, 'cepstrogram': cepstrogramEncoded, 'spectrogram': spectrogramEncoded, 'logSpectrogram': logSpectrogramEncoded}
    return Response(json.dumps(dict_data), mimetype='text/plain')

@app.route("/TranscribeByOnsetsAndFrames", methods=['POST'])
def transcribeByOnsetsAndFrames():
    requestFolderPath, responseFolderPath, requestUuid, responseUuid = createRequestResponseFolders()


if __name__ == "__main__":
    app.run(port=5000)