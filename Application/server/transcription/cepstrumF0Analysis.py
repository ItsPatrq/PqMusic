import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
import math
from utils.general import loadNormalizedSoundFile, create_sine
from utils.plots import plot_spectrum_line_component_only, plot_spectrum_line_components, plot_spectrogram, plot_cepstrogram, plot_pitches, plot_correlogram, plot_interpolated_correlation
from scipy.interpolate import interp1d
from utils.cepstrumUtils import real_cepst_from_signal
from io import BytesIO

def cepstrumF0Analysis (data, sampleRate = 1024, frameWidth = 512, spacing = 512, sizeOfZeroPadding = 512):
    hanning = np.hanning(frameWidth)
    spectrogram = []
    logSpectrogram = []
    cepstra = []
    bestFq = []
    zeroPadding = np.zeros(sizeOfZeroPadding)

    for i in range(0, int(math.ceil((len(data) - frameWidth) / spacing))):
        frame = data[i*spacing:i*spacing+frameWidth]
        frame = frame*hanning
        frame = np.concatenate((frame, zeroPadding))
        cepst, logSp, spectr = real_cepst_from_signal(frame)
        fftLen = int(np.floor(len(spectr)/2))
        spectrogram.append(np.abs(spectr[:fftLen]))
        logSpectrogram.append(logSp[:fftLen])
        cepst = cepst[:fftLen//2]
        cepst[0:14] = np.zeros(14)
        cepstra.append(cepst)
        
        maxperiod = np.argmax(cepst)
        bestFq.append(sampleRate/maxperiod)
    
    return bestFq, cepstra, spectrogram, logSpectrogram
## Funkcja do użytku serwera
def transcribe_by_cepstrum_wrapped(filePath):
    frameWidth = 2048
    spacing = 512
    sampleRate, data = loadNormalizedSoundFile(filePath)
    bestFq, cepstra, spectra, logSpectrogram  = cepstrumF0Analysis(data, sampleRate, frameWidth, spacing, frameWidth)

    fig, _ = plot_pitches(bestFq, spacing, sampleRate, show=False, language="pl")
    fig2, _ = plot_cepstrogram(cepstra, spacing, sampleRate, show=False, language="pl")
    fig3, _ = plot_spectrogram(spectra, spacing, sampleRate, show=False, language="pl")
    fig4, _ = plot_spectrogram(logSpectrogram, spacing, sampleRate, show=False, language="pl", title="logPowSpectrogram")


    pitches, cepstrogram, spectrogram, logSpectrogram = BytesIO(), BytesIO(), BytesIO(), BytesIO()
    fig.savefig(pitches, format="png")
    fig2.savefig(cepstrogram, format="png")
    fig3.savefig(spectrogram, format="png")
    fig4.savefig(logSpectrogram, format="png")

    return pitches, cepstrogram, spectrogram, logSpectrogram


if __name__ == "__main__":
    frameWidth = 2048
    spacing = 512
    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, '../test_sounds/piano-c3-d3-c3-b2.wav')

    sampleRate, data = loadNormalizedSoundFile(filePath)
    
    for i in range(0, 1000):
        bestFq, cepstra, spectra, logSpectrogram = cepstrumF0Analysis(data, sampleRate, 4096, 1024, 8192)
    #---------------------------#
    plot_spectrum_line_component_only(spectra[5], sampleRate, language="pl")


