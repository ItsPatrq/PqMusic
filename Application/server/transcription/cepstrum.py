import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
from tqdm import tqdm
import pyaudio
import math
from utils.general import loadNormalizedSoundFIle, create_sine, fft_to_hz
from utils.plots import plot_spectrum_line_component, plot_spectrogram, plot_correlation, plot_pitches, plot_correlogram, plot_interpolated_correlation
from utils.profile import profile, print_prof_data
from scipy.interpolate import interp1d
from utils.cepstrumUtils import real_cepst_from_signal

def cepstrum(data, sampleRate = 1024, frameWidth = 512, sizeOfZeroPadding = 512, spacing = 512):
    hamming = np.hamming(frameWidth)
    spectrogram = []
    cepstra = []
    bestFq = []
    zeroPadding = np.zeros(sizeOfZeroPadding)

    for i in tqdm(range(0, int(math.ceil((len(data) - frameWidth) / spacing)))):
        frame = data[i*spacing:i*spacing+frameWidth]
        frame = frame*hamming
        frame = np.concatenate((frame, zeroPadding))
        cepst, powerSp, spectr = real_cepst_from_signal(frame)
        fftLen = int(np.floor(len(spectr)/2))

        spectrogram.append(powerSp[:fftLen])
        cepst = cepst[:fftLen//2]
        cepst[0:9] = np.zeros(9)
        cepstra.append(cepst)
        
        maxperiod = np.argmax(cepst)
        bestFq.append(sampleRate/maxperiod)
    
    return cepstra, spectrogram, bestFq


if __name__ == "__main__":
    frameWidth = 2048
    spacing = 2048
    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, '../test_sounds/piano-c3-d3-c3-b2.wav')
    #file_path = '../test_sounds/Sine_sequence.wav'
    #filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')

    sampleRate, data = loadNormalizedSoundFIle(filePath)
    sine_data = create_sine(220, sampleRate, 5)
    sine_data += (create_sine(440, sampleRate, 5) * 0.2)
    sine_data += (create_sine(110, sampleRate, 5) * 0.3)

    cepstra, spectra, bestFq = cepstrum(data, sampleRate, frameWidth, frameWidth, spacing)

    plot_pitches(bestFq, spacing, sampleRate)
    plot_spectrogram(spectra, spacing, sampleRate)
    plot_correlogram(cepstra, spacing, sampleRate)


    print("ok")


