import os
import wave
from  .general import convertAudioFileToWave, path_leaf, loadNormalizedSoundFIle
import pylab
from .plots import plot_spectrogram
import math
import numpy as np
from scipy.fftpack import fft
from io import BytesIO

def graph_spectrogram(file_name, result_path):
    sound_info, frame_rate = get_file_info(file_name)
    pylab.figure(num=None, figsize=(19, 12))
    pylab.subplot(111)
    pylab.title('Spektogram of %r' % path_leaf(file_name))
    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig(result_path)

def get_file_info(file_name):
    waveFilePath = convertAudioFileToWave(file_name)
    wav = wave.open(waveFilePath, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'Int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate

if __name__ == '__main__':
    file_name = './spectogram/Violas.mp3'
    graph_spectrogram(file_name, '.')

def plot_spectrogram_wrapped(filePath, result_path):
    frameWidth = 2048
    spacing = 2048
    sampleRate, data = loadNormalizedSoundFIle(filePath)
    spectra = []
    hann = np.hanning(frameWidth)
    zeroPadding = np.zeros(frameWidth)
    for i in range(0, int(math.ceil((len(data) - frameWidth) / spacing))):
        frame = data[i*spacing:i*spacing+frameWidth] * hann
        frame = np.concatenate((frame, zeroPadding))
        frameComplex = fft(frame)
        fftLen = int(np.floor(len(frameComplex)/2))
        powerSpec = abs(frameComplex)

        powerSpec = powerSpec[:fftLen]
        spectra.append(powerSpec)
    
    fig, _ = plot_spectrogram(spectra, spacing, sampleRate, showColorbar=True, language="pl", show=False)
    fig.savefig(result_path, format="png")
