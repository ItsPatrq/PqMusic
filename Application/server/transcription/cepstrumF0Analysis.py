import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft
from tqdm import tqdm
import pyaudio
import math
from utils.general import loadNormalizedSoundFIle, create_sine
from utils.plots import plot_spectrum_line_component, plot_spectrogram, plot_cepstrogram, plot_pitches, plot_correlogram, plot_interpolated_correlation
from utils.profile import profile, print_prof_data
from scipy.interpolate import interp1d
from utils.cepstrumUtils import real_cepst_from_signal
from pycuda import cumath
import pycuda.driver
import pycuda.tools
import pycuda.gpuarray as gpuarray
import pycuda.cumath
from reikna.fft import FFT as gpu_fft
from reikna.cluda import dtypes, cuda_api
from utils.profile import profile, print_prof_data, print_normalize_profile_data

@profile
def cepstrumF0Analysis (data, sampleRate = 1024, frameWidth = 512, sizeOfZeroPadding = 512, spacing = 512):
    hanning = np.hanning(frameWidth)
    spectrogram = []
    cepstra = []
    bestFq = []
    zeroPadding = np.zeros(sizeOfZeroPadding)

    for i in tqdm(range(0, int(math.ceil((len(data) - frameWidth) / spacing)))):
        frame = data[i*spacing:i*spacing+frameWidth]
        frame = frame*hanning
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

@profile
def ceostrumF0AnalysisGpu (api, thr, data, sampleRate = 1024, frameWidth = 512, sizeOfZeroPadding = 512, spacing = 512):
    zeroPadding = np.zeros(sizeOfZeroPadding)
    hamming = np.hamming(frameWidth)
    hamming = np.concatenate((hamming, zeroPadding))

    hamming_dev = thr.to_device(hamming)
    powerSp_dev = thr.array((frameWidth + sizeOfZeroPadding,), np.complex128)
    res_dev = thr.array((frameWidth + sizeOfZeroPadding,), np.complex128)

    fft = gpu_fft.FFT(res_dev)
    fft_compiled = fft.compile(thr)

    cepstra = []
    bestFq = []
    #TODO: Czy nie lepiej wrzucic całego data do GPU na start? Jedyny problem jaki z tym mam jest taki, ze nie wiem jak potem dodać zero padding do tego
    #najlepiej by było kazde i w iteracji wrzucić do innego wąku, tylko nie wiem jak
    for i in tqdm(range(0, int(math.ceil((len(data) - frameWidth) / spacing)))):
        data_dev = thr.to_device(np.concatenate((data[i * spacing:i*spacing+frameWidth], zeroPadding)) + 0j) * hamming_dev
    
        fft_compiled(powerSp_dev, data_dev, inverse=0)
        powerSpDev = cumath.log(powerSp_dev.__abs__()).astype(np.complex128)

        fft_compiled(res_dev, powerSpDev, inverse=1)
        cepst = res_dev.get().real
        cepst = cepst[:int(np.floor(len(cepst)/4))]

        cepst[0:9] = np.zeros(9)
        cepstra.append(cepst)
        
        maxperiod = np.argmax(cepst)
        bestFq.append(sampleRate/maxperiod)

    return cepstra, bestFq

if __name__ == "__main__":
    frameWidth = 2048
    spacing = 1024
    filePath = path.dirname(path.abspath(__file__))
    filePath = path.join(filePath, '../test_sounds/piano-c3-d3-c3-b2.wav')
    #file_path = '../test_sounds/Sine_sequence.wav'
    #filePath = path.join(filePath, '../test_sounds/chopin-nocturne.wav')

    sampleRate, data = loadNormalizedSoundFIle(filePath)
    sine_data = create_sine(220, sampleRate, 5)
    sine_data += (create_sine(440, sampleRate, 5) * 0.2)
    sine_data += (create_sine(110, sampleRate, 5) * 0.3)

    cepstra, spectra, bestFq = cepstrumF0Analysis(data, sampleRate, frameWidth, frameWidth, spacing)

    #plot_pitches(bestFq, spacing, sampleRate)
    #plot_spectrogram(spectra, spacing, sampleRate)
    plot_cepstrogram(cepstra, spacing, sampleRate)

    #GPU
    # pycuda.driver.init() # pylint: disable=no-member
    # # replace 0 with your device number. In this case, 0 is appropriate
    # dev = pycuda.driver.Device(0) # pylint: disable=no-member
    # ctx = dev.make_context()
    # api = cuda_api()
    # thr = api.Thread.create()
    # for i in range(100):
    #     cepstra, bestFq = ceostrumF0AnalysisGpu(api, thr, np.array(data), sampleRate, frameWidth, frameWidth, spacing)

    # plot_pitches(bestFq, spacing, sampleRate)
    # plot_cepstrogram(cepstra, spacing, sampleRate)

    # ctx.pop()
    # pycuda.tools.clear_context_caches()
    # print_prof_data()
    # print_normalize_profile_data(10)

