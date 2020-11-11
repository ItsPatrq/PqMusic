"""
W tym module znajduje się funkcja wywoływana przez GUI do prezentacji spektrogramu
"""

import math
import numpy as np
from scipy.fftpack import fft
from .general import loadNormalizedSoundFile
from .plots import plot_spectrogram


def plot_spectrogram_wrapped(filePath, result_path):
    """
    Funkcja wywoływana przez GUI do prezentacji spektrogramu
    """
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

    fig, _ = plot_spectrogram(
        spectra, spacing, sampleRate, showColorbar=True, language="eng", show=False)
    fig.savefig(result_path, format="png")
