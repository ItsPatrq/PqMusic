"""
Ten moduł odpowiada za uruchomienie serwera HTTP odpowiadającego na zapytania z GUI
"""

import matplotlib
import base64
from flask import Flask, send_file, request, json, Response
import os
from flask_cors import CORS
import uuid
from utils.spectogram import plot_spectrogram_wrapped # pylint: disable=import-error
from utils.window_functions_presentation import hannWindow, hammingWindow, rectangleWindow # pylint: disable=import-error
from transcription.autocorrelation import autocorrelation_wrapped # pylint: disable=import-error
from transcription.cepstrum_f0_analysis import transcribe_by_cepstrum_wrapped # pylint: disable=import-error
from transcription.aclos import transcribe_by_aclos_wrapped # pylint: disable=import-error
from transcription.generative_method_by_pertus_and_inesta import transcribe_by_generative_method_wrapped # pylint: disable=import-error
app = Flask(__name__, static_url_path='',
            static_folder=os.path.abspath('../static/build'))
matplotlib.use('Agg')

CORS(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#region transcription initialization Onsets and Frames
onsets = None
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
    return send_file("../static/build/index.html")

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
def getRectangleWindow():
    _, responseFolderPath, _, _ = createRequestResponseFolders()
    responseFilePath = "/".join([responseFolderPath, 'RectangleWindow.png'])
    rectangleWindow(responseFilePath)
    return send_file(responseFilePath)


@app.route("/TranscribeByAutoCorrelation", methods=['POST'])
def transcribeByAutoCorrelation():
    requestFilePath, _, _, _, _ = handleRequestWithFile()

    pitches, correlogram = autocorrelation_wrapped(requestFilePath)

    pitchesEncoded = base64.b64encode(pitches.getbuffer()).decode("ascii")
    correlogramOpenedEncoded = base64.b64encode(
        correlogram.getbuffer()).decode("ascii")
    dict_data = {'pitches': pitchesEncoded,
                 'correlogram': correlogramOpenedEncoded}
    return Response(json.dumps(dict_data), mimetype='text/plain')


@app.route("/TranscribeByCepstrum", methods=['POST'])
def TranscribeByCepstrum():
    requestFilePath, _, _, _, _ = handleRequestWithFile()

    pitches, cepstrogram, curr_spectrogram, logSpectrogram = transcribe_by_cepstrum_wrapped(
        requestFilePath)

    pitchesEncoded = base64.b64encode(pitches.getbuffer()).decode("ascii")
    cepstrogramEncoded = base64.b64encode(
        cepstrogram.getbuffer()).decode("ascii")
    spectrogramEncoded = base64.b64encode(
        curr_spectrogram.getbuffer()).decode("ascii")
    logSpectrogramEncoded = base64.b64encode(
        logSpectrogram.getbuffer()).decode("ascii")

    dict_data = {'pitches': pitchesEncoded, 'cepstrogram': cepstrogramEncoded,
                 'spectrogram': spectrogramEncoded, 'logSpectrogram': logSpectrogramEncoded}
    return Response(json.dumps(dict_data), mimetype='text/plain')


@app.route("/TranscribeByAclos", methods=['POST'])
def TranscribeByAclos():
    requestFilePath, _, _, _, _ = handleRequestWithFile()

    pitchesFig, correlogramFig, spectrogramFig = transcribe_by_aclos_wrapped(
        requestFilePath)

    pitchesEncoded = base64.b64encode(pitchesFig.getbuffer()).decode("ascii")
    correlogramEncoded = base64.b64encode(
        correlogramFig.getbuffer()).decode("ascii")
    spectrogramEncoded = base64.b64encode(
        spectrogramFig.getbuffer()).decode("ascii")

    dict_data = {'pitches': pitchesEncoded,
                 'correlogram': correlogramEncoded, 'spectrogram': spectrogramEncoded}
    return Response(json.dumps(dict_data), mimetype='text/plain')


@app.route("/TranscribeByPertusa2008", methods=['POST'])
def TranscribeByPertusa2008():
    requestFilePath, responseFolderPath, _, _, _ = handleRequestWithFile()
    responseFilePath = "/".join([responseFolderPath, 'transkrypcja.mid'])
    transcribe_by_generative_method_wrapped(
        requestFilePath, False, responseFilePath)
    return send_file(responseFilePath)


@app.route("/TranscribeByPertusa2012", methods=['POST'])
def TranscribeByPertusa2012():
    requestFilePath, responseFolderPath, _, _, _ = handleRequestWithFile()
    responseFilePath = "/".join([responseFolderPath, 'transkrypcja.mid'])
    transcribe_by_generative_method_wrapped(
        requestFilePath, True, responseFilePath)
    return send_file(responseFilePath)


@app.route("/TranscribeByOnsetsAndFrames", methods=['POST'])
def transcribeByOnsetsAndFrames():
    requestFilePath, responseFolderPath, _, _, _ = handleRequestWithFile()
    responseFilePath = "/".join([responseFolderPath, 'transkrypcja.mid'])
    exampleFile = open(requestFilePath, 'rb')

    if onsets == None:
        return "Nie znaleziono bibliotek potrzebnych do wykonania transkrypcji przy użyciu metody Onsets and Frames"
    uploaded = {
        str(exampleFile.name): exampleFile.read()
    }
    onsets.initializeModel()
    onsets.transcribe(uploaded, responseFilePath)
    return send_file(responseFilePath)


if __name__ == "__main__":
    try:
        from transcription.onsets_and_frames import OnsetsAndFramesImpl
        onsets = OnsetsAndFramesImpl()
        onsets.initializeModel()
    except ImportError:
        print("Uruchomiona instancja serwera nie wspiera metody Onsets and Frames")
    app.run(port=5000)
