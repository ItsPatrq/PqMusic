## W tym pliku znajduje się metoda wywoływana przez GUI do prezentacji spektrogramu

import os
import wave
from  .general import convertAudioFileToWave, path_leaf, loadNormalizedSoundFile
import pylab
from .plots import plot_spectrogram
import math
import numpy as np
from scipy.fftpack import fft
from io import BytesIO

def plot_spectrogram_wrapped(filePath, result_path):
    frameWidth = 2048
    spacing = 2048
    sampleRate, data = loadNormalizedSoundFile(filePath)
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
