import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
from tqdm import tqdm
from utils.profile import profile, print_prof_data
import pyaudio
import math
import utils.plots
import utils.general
import transcription.aclos
file_path = './test_sounds/piano-c3-d3-c3-b2.wav'
#file_path = './test_sounds/Sine_sequence.wav'
#file_path = './test_sounds/chopin-nocturne.wav'

@profile
def count_fft(data, frameWidth, spacing):
    hamming = np.hamming(frameWidth)
    spectra = []
    for i in tqdm(range(0, int((len(data) - frameWidth) / spacing))):
        frame_complex = fft((data[i*spacing:i*spacing+frameWidth]) * hamming)
        frame_len = int(np.floor(len(frame_complex)/2))
        frame_amplitude = np.log(abs(frame_complex))
        spectra.append(frame_amplitude[:(frame_len - 1)])
    return spectra


@profile
def cepstrogram(data, frameWidth, spacing, sampleRate):
    spectra = []
    cepstrum = []
    bestFq = []
    hamming = np.hamming(frameWidth)

    for i in tqdm(range(0, int((len(data)-frameWidth)/spacing))):
        frame = data[i*spacing:i*spacing+frameWidth]
        frame = frame*hamming
        complex_fourier = fft(frame)
        fft_len = int(np.floor(len(complex_fourier)/2))
        power_sp = np.log(abs(complex_fourier))

        spectra.append(power_sp[:(fft_len-1)])

        cepst = abs(fft(power_sp).real)[:fft_len//2]/frameWidth
        cepstrum.append(cepst)
        cepst[0:8] = np.zeros(8)
        maxPeriod = np.argmax(cepst[30:]) + 30
        bestFq.append(sampleRate/maxPeriod)
    
    return spectra, cepstrum, bestFq

# # http://www.ii.uib.no/~espenr/hovedfag/thesis.pdf p 31
# def crossCorelation():
#     autocorr_func_gpu = ...
#     samples = [...]
#     for i in range((0, int((len(data) - frame_width) / spacing))):
#         frame = cpu_fft

def create_sine(hz, sample_rate, durotian):
    samples = np.arange(sample_rate * durotian) / sample_rate
    return  np.sin(2 * np.pi * hz * samples)

    
if __name__ == "__main__":
    frameWidth = 512
    spacing = 512


    sampleRate, data = loadNormalizedSoundFIle(file_path)

    sine_data = create_sine(777, sampleRate, 5)
    sine_data += (create_sine(440, sampleRate, 5) * 0.2)
    sine_data += (create_sine(220, sampleRate, 5) * 0.5)


    # fft1 = count_fft(sine_data)

    # print("FFT CPU:", len(fft1), fft1[0].shape, fft1[0].dtype, fft1[1] )

    # pqutils.plotSpectrogram(fft1, frame_width, spacing, 44100)
    # pqutils.plotSpectrogram(fft2, frame_width, spacing, 44100)

    # pqutils.plotSpectrogram(spectra, frame_width, spacing, 44100)
    # pqutils.plot_correlogram(cepstrum, frame_width, spacing, sample_rate)
    # pqutils.plot_pitches(bestFq, spacing, sample_rate)
   

    # spectra, cepstrum, bestFq = cepstrogram(data, frame_width, spacing, sample_rate)

    # plotSpectrogram(spectra, frame_width, spacing, 44100)
    #plot_correlogram(cepstrum, frame_width, spacing, sample_rate)
    #pqutils.plot_pitches(bestFq, spacing, sample_rate)
    print("ok")